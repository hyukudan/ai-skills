"""Skill manager - main orchestrator for all skill operations."""

from __future__ import annotations

import shutil
from pathlib import Path
from typing import Literal

from ..config import AppConfig, get_config
from ..models.skill import Skill, SkillIndex
from ..storage.cache import CacheManager, get_cache_manager
from ..storage.lockfile import LockFileManager
from ..storage.paths import PathResolver, get_path_resolver
from .loader import LoadError, SkillLoader, get_loader
from .renderer import SkillRenderer, get_renderer
from ..models.variable import VariableContext


class SkillManager:
    """Main orchestrator for skill operations.

    Coordinates:
    - Loading and parsing skills
    - Installing from various sources
    - Removing and updating skills
    - Lock file management
    - Cache management
    """

    def __init__(
        self,
        config: AppConfig | None = None,
        paths: PathResolver | None = None,
        loader: SkillLoader | None = None,
        cache: CacheManager | None = None,
        renderer: SkillRenderer | None = None,
    ):
        self.config = config or get_config()
        self.paths = paths or get_path_resolver()
        self.loader = loader or get_loader()
        self.cache = cache or get_cache_manager()
        self.renderer = renderer or get_renderer()
        self._lock_managers: dict[str, LockFileManager] = {}
        self._resolver = None  # Lazy loaded to avoid circular import

    def _get_lock_manager(self, global_install: bool = False) -> LockFileManager:
        """Get or create lock manager for scope."""
        key = "global" if global_install else "project"
        if key not in self._lock_managers:
            manager = LockFileManager(self.paths)
            manager.load(global_install=global_install)
            self._lock_managers[key] = manager
        return self._lock_managers[key]

    # ─────────────────────────────────────────────────────────────────
    # Reading Skills
    # ─────────────────────────────────────────────────────────────────

    def get(self, name: str) -> Skill | None:
        """Get a skill by name.

        Searches in priority order: project > global.

        Args:
            name: Skill name

        Returns:
            Skill if found, None otherwise
        """
        result = self.paths.find_skill(name)
        if result is None:
            return None

        path, source, location_type = result
        return self.loader.load(path, source=source, location_type=location_type)

    def list_installed(
        self,
        global_only: bool = False,
        project_only: bool = False,
    ) -> list[Skill]:
        """List all installed skills.

        Args:
            global_only: Only return global skills
            project_only: Only return project skills

        Returns:
            List of installed skills
        """
        skills: list[Skill] = []
        seen_names: set[str] = set()

        for skills_dir, location_type in self.paths.get_search_dirs():
            is_global = str(skills_dir).startswith(str(self.paths.global_base))

            if global_only and not is_global:
                continue
            if project_only and is_global:
                continue

            for skill_dir in self.loader.list_skill_dirs(skills_dir):
                try:
                    skill = self.loader.load(
                        skill_dir,
                        source="global" if is_global else "project",
                        location_type=location_type,
                    )

                    # Skip duplicates (first one wins due to priority order)
                    if skill.manifest.name in seen_names:
                        continue
                    seen_names.add(skill.manifest.name)
                    skills.append(skill)

                except Exception:
                    continue

        return skills

    def read(
        self,
        name: str,
        variables: dict | None = None,
        resolve_composition: bool = True,
        raw: bool = False,
    ) -> str:
        """Read skill content for agent consumption.

        Args:
            name: Skill name
            variables: Optional variables to render
            resolve_composition: If True, resolve extends/includes
            raw: If True, return raw content without rendering templates

        Returns:
            Formatted skill content

        Raises:
            LoadError: If skill not found
        """
        skill = self.get(name)
        if skill is None:
            raise LoadError(f"Skill not found: {name}")

        content = skill.content

        # If raw, return unprocessed content
        if raw:
            return content

        # Resolve composition (extends/includes)
        if resolve_composition and skill.manifest.has_composition:
            resolver = self._get_resolver()
            content = resolver.resolve_composition(skill)

        # Render variables if provided or skill has variables
        if variables or skill.manifest.has_variables:
            context = VariableContext(variables=variables or {})
            # Create a temporary skill with resolved content for rendering
            temp_skill = skill.model_copy(update={"content": content})
            content = self.renderer.render(temp_skill, context)

        return self._format_for_agent(skill, content)

    def _get_resolver(self):
        """Get resolver instance (lazy loaded)."""
        if self._resolver is None:
            from .resolver import SkillResolver
            self._resolver = SkillResolver(self)
        return self._resolver

    def _format_for_agent(self, skill: Skill, content: str | None = None) -> str:
        """Format skill content for agent consumption."""
        content = content or skill.content
        lines = [
            f"# Skill: {skill.manifest.name} v{skill.manifest.version}",
            f"Base directory: {skill.path}",
            "",
            content,
        ]
        return "\n".join(lines)

    def get_skill_variables(self, name: str) -> dict:
        """Get variable definitions for a skill.

        Args:
            name: Skill name

        Returns:
            Dict of variable name -> metadata
        """
        skill = self.get(name)
        if skill is None:
            return {}
        return self.renderer.preview_variables(skill)

    # ─────────────────────────────────────────────────────────────────
    # Listing Skills
    # ─────────────────────────────────────────────────────────────────

    def list_all(
        self,
        include_global: bool = True,
        include_project: bool = True,
    ) -> list[SkillIndex]:
        """List all installed skills.

        Args:
            include_global: Include globally installed skills
            include_project: Include project-level skills

        Returns:
            List of skill indices
        """
        skills: list[SkillIndex] = []
        seen_names: set[str] = set()

        for skills_dir, location_type in self.paths.get_search_dirs():
            is_global = str(skills_dir).startswith(str(self.paths.global_base))

            if is_global and not include_global:
                continue
            if not is_global and not include_project:
                continue

            for skill_dir in self.loader.list_skill_dirs(skills_dir):
                try:
                    skill = self.loader.load(
                        skill_dir,
                        source="global" if is_global else "project",
                        location_type=location_type,
                    )

                    if skill.manifest.name not in seen_names:
                        seen_names.add(skill.manifest.name)
                        skills.append(skill.to_index())

                except Exception:
                    continue

        return sorted(skills, key=lambda s: s.name)

    # ─────────────────────────────────────────────────────────────────
    # Installing Skills
    # ─────────────────────────────────────────────────────────────────

    def install_from_path(
        self,
        source_path: Path,
        global_install: bool = False,
        force: bool = False,
    ) -> tuple[Skill, Literal["installed", "updated", "unchanged"]]:
        """Install a skill from a local path.

        Args:
            source_path: Path to skill directory
            global_install: Install globally if True
            force: Overwrite without hash check

        Returns:
            Tuple of (installed skill, status)
        """
        # Load the skill first to validate
        skill = self.loader.load(source_path, source="cache")

        # Check for existing skill
        existing = self.get(skill.manifest.name)
        status: Literal["installed", "updated", "unchanged"]

        if existing:
            if not force and existing.content_hash == skill.content_hash:
                return existing, "unchanged"
            status = "updated"
        else:
            status = "installed"

        # Determine target path
        target_path = self.paths.get_install_path(
            skill.manifest.name,
            global_install=global_install,
        )

        # Ensure parent directory exists
        self.paths.ensure_dirs(global_install=global_install)

        # Remove existing if present
        if target_path.exists():
            shutil.rmtree(target_path)

        # Copy skill directory
        shutil.copytree(source_path, target_path, dirs_exist_ok=True)

        # Reload from installed location
        installed_skill = self.loader.load(
            target_path,
            source="global" if global_install else "project",
            location_type=".aiskills",
        )

        # Update lock file
        lock = self._get_lock_manager(global_install)
        source_str = f"local:{source_path}"
        lock.add_skill(installed_skill, source_str)
        lock.save()

        return installed_skill, status

    def install_skills(
        self,
        skills: list[tuple[Path, str]],  # (path, source_string)
        global_install: bool = False,
        force: bool = False,
    ) -> list[tuple[Skill, Literal["installed", "updated", "unchanged", "error"], str]]:
        """Install multiple skills.

        Args:
            skills: List of (source_path, source_string) tuples
            global_install: Install globally if True
            force: Overwrite without hash check

        Returns:
            List of (skill, status, message) tuples
        """
        results: list[tuple[Skill, Literal["installed", "updated", "unchanged", "error"], str]] = []

        for source_path, source_str in skills:
            try:
                skill, status = self.install_from_path(
                    source_path,
                    global_install=global_install,
                    force=force,
                )
                results.append((skill, status, ""))
            except Exception as e:
                # Create a dummy skill for error reporting
                dummy = Skill(
                    manifest={"name": source_path.name, "description": "Error"},  # type: ignore
                    content="",
                    raw_content="",
                    path=str(source_path),
                )
                results.append((dummy, "error", str(e)))

        return results

    # ─────────────────────────────────────────────────────────────────
    # Removing Skills
    # ─────────────────────────────────────────────────────────────────

    def remove(
        self,
        name: str,
        global_only: bool = False,
    ) -> bool:
        """Remove an installed skill.

        Args:
            name: Skill name to remove
            global_only: Only remove from global location

        Returns:
            True if removed, False if not found
        """
        result = self.paths.find_skill(name)
        if result is None:
            return False

        path, source, _ = result

        # Check scope
        if global_only and source != "global":
            return False

        # Remove directory
        shutil.rmtree(path)

        # Update lock file
        is_global = source == "global"
        lock = self._get_lock_manager(is_global)
        lock.remove_skill(name)
        lock.save()

        return True

    # ─────────────────────────────────────────────────────────────────
    # Validation
    # ─────────────────────────────────────────────────────────────────

    def validate(self, path: Path) -> list[str]:
        """Validate a skill at path.

        Args:
            path: Path to skill directory

        Returns:
            List of validation errors
        """
        return self.loader.validate_structure(path)

    # ─────────────────────────────────────────────────────────────────
    # Cache Management
    # ─────────────────────────────────────────────────────────────────

    def clear_cache(self) -> int:
        """Clear the skill cache.

        Returns:
            Number of entries cleared
        """
        return self.cache.clear()

    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        return self.cache.get_stats()


# Singleton instance
_manager: SkillManager | None = None


def get_manager() -> SkillManager:
    """Get the singleton manager instance."""
    global _manager
    if _manager is None:
        _manager = SkillManager()
    return _manager

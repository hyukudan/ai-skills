"""Skill loader - loads and parses SKILL.md files."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from ..constants import (
    ASSETS_DIR,
    MAX_SKILL_SIZE_KB,
    REFERENCES_DIR,
    SCRIPTS_DIR,
    SKILL_FILE,
)
from ..models.skill import Skill, SkillManifest, SkillPrecedence
from .parser import ParseError, YAMLParser, get_parser


# Local override file name
SKILL_LOCAL_FILE = "SKILL.local.md"


class LoadError(Exception):
    """Error loading a skill."""

    def __init__(self, message: str, path: str | None = None):
        self.path = path
        if path:
            message = f"{path}: {message}"
        super().__init__(message)


class ValidationError(Exception):
    """Error validating a skill."""

    def __init__(self, message: str, errors: list[str] | None = None):
        self.errors = errors or [message]
        super().__init__(message)


class SkillLoader:
    """Loads and parses SKILL.md files from directories.

    Responsible for:
    - Finding SKILL.md in a directory
    - Parsing frontmatter and content
    - Creating Skill instances
    - Validating skill structure
    """

    def __init__(self, parser: YAMLParser | None = None):
        self.parser = parser or get_parser()

    def load(
        self,
        path: Path | str,
        source: Literal["project", "global", "cache"] = "project",
        location_type: Literal[".aiskills", ".claude", ".agent"] = ".aiskills",
        apply_local_overrides: bool = True,
    ) -> Skill:
        """Load a skill from a directory path.

        Args:
            path: Path to skill directory (must contain SKILL.md)
            source: Where the skill came from
            location_type: Which directory structure it's in
            apply_local_overrides: If True, merge SKILL.local.md if it exists

        Returns:
            Loaded Skill instance

        Raises:
            LoadError: If skill cannot be loaded
            ParseError: If SKILL.md cannot be parsed
        """
        path = Path(path)

        if not path.exists():
            raise LoadError("Directory does not exist", str(path))

        if not path.is_dir():
            raise LoadError("Path is not a directory", str(path))

        skill_file = path / SKILL_FILE
        if not skill_file.exists():
            raise LoadError(f"No {SKILL_FILE} found in directory", str(path))

        # Check file size
        size_kb = skill_file.stat().st_size / 1024
        if size_kb > MAX_SKILL_SIZE_KB:
            raise LoadError(
                f"{SKILL_FILE} is too large ({size_kb:.1f}KB > {MAX_SKILL_SIZE_KB}KB)",
                str(path),
            )

        # Read and parse base skill
        raw_content = skill_file.read_text(encoding="utf-8")

        try:
            result = self.parser.parse(raw_content)
        except ParseError as e:
            raise LoadError(str(e), str(skill_file)) from e

        manifest = result.manifest
        content = result.content

        # Check for local overrides
        local_file = path / SKILL_LOCAL_FILE
        if apply_local_overrides and local_file.exists():
            try:
                local_content = local_file.read_text(encoding="utf-8")
                local_result = self.parser.parse(local_content)

                # Merge local overrides into manifest
                manifest = self._merge_manifest(manifest, local_result.manifest)

                # Append or replace content based on local settings
                if local_result.content.strip():
                    # If local has content, it extends the base
                    content = f"{content}\n\n<!-- Local overrides from {SKILL_LOCAL_FILE} -->\n{local_result.content}"

                # Update raw content to reflect merging
                raw_content = f"{raw_content}\n\n# --- Local overrides ---\n{local_content}"

            except ParseError:
                # If local file is invalid, just skip it
                pass

        return Skill(
            manifest=manifest,
            content=content,
            raw_content=raw_content,
            path=str(path.absolute()),
            source=source,
            location_type=location_type,
        )

    def _merge_manifest(
        self,
        base: SkillManifest,
        override: SkillManifest,
    ) -> SkillManifest:
        """Merge local override manifest into base manifest.

        Local overrides can:
        - Override scalar values (priority, precedence, etc.)
        - Extend lists (tags, includes, dependencies)
        - Override nested objects (scope, security, variables)

        Args:
            base: Base skill manifest
            override: Local override manifest

        Returns:
            Merged manifest
        """
        # Start with base as dict
        base_dict = base.model_dump()

        # Get override as dict, excluding defaults
        override_dict = override.model_dump(exclude_unset=True, exclude_defaults=True)

        # Merge logic
        for key, value in override_dict.items():
            if key in base_dict:
                base_value = base_dict[key]

                # List fields: extend instead of replace
                if isinstance(base_value, list) and isinstance(value, list):
                    # Extend with unique values
                    combined = base_value + [v for v in value if v not in base_value]
                    base_dict[key] = combined

                # Dict fields: deep merge
                elif isinstance(base_value, dict) and isinstance(value, dict):
                    base_dict[key] = {**base_value, **value}

                # Scalar: override
                else:
                    base_dict[key] = value
            else:
                base_dict[key] = value

        # Mark as local precedence since it has local overrides
        base_dict["precedence"] = SkillPrecedence.LOCAL.value

        return SkillManifest(**base_dict)

    def load_from_content(
        self,
        content: str,
        path: str = "<memory>",
        source: Literal["project", "global", "cache"] = "cache",
        location_type: Literal[".aiskills", ".claude", ".agent"] = ".aiskills",
    ) -> Skill:
        """Load a skill from string content.

        Useful for loading skills from remote sources before saving.

        Args:
            content: Full SKILL.md content
            path: Virtual path for the skill
            source: Where the skill came from
            location_type: Which directory structure

        Returns:
            Loaded Skill instance
        """
        result = self.parser.parse(content)

        return Skill(
            manifest=result.manifest,
            content=result.content,
            raw_content=result.raw_content,
            path=path,
            source=source,
            location_type=location_type,
        )

    def validate_structure(self, path: Path | str) -> list[str]:
        """Validate skill directory structure.

        Checks:
        - SKILL.md exists and is valid
        - Referenced directories exist
        - No suspicious files

        Args:
            path: Path to skill directory

        Returns:
            List of validation errors (empty if valid)
        """
        path = Path(path)
        errors: list[str] = []

        # Check directory exists
        if not path.exists():
            return ["Directory does not exist"]

        if not path.is_dir():
            return ["Path is not a directory"]

        # Check SKILL.md
        skill_file = path / SKILL_FILE
        if not skill_file.exists():
            errors.append(f"Missing {SKILL_FILE}")
        else:
            # Try to parse it
            try:
                content = skill_file.read_text(encoding="utf-8")
                self.parser.parse(content)
            except (ParseError, UnicodeDecodeError) as e:
                errors.append(f"Invalid {SKILL_FILE}: {e}")

        # Check optional directories
        for dirname in [REFERENCES_DIR, SCRIPTS_DIR, ASSETS_DIR]:
            dirpath = path / dirname
            if dirpath.exists() and not dirpath.is_dir():
                errors.append(f"'{dirname}' exists but is not a directory")

        # Check for suspicious files
        suspicious = [".env", "credentials", "secrets", "password"]
        for item in path.iterdir():
            name_lower = item.name.lower()
            for sus in suspicious:
                if sus in name_lower:
                    errors.append(f"Potentially sensitive file: {item.name}")
                    break

        return errors

    def list_skill_dirs(self, base_path: Path | str) -> list[Path]:
        """List all skill directories under a base path.

        Finds directories containing SKILL.md files.

        Args:
            base_path: Directory to search in

        Returns:
            List of paths to skill directories
        """
        base_path = Path(base_path)
        skill_dirs = []

        if not base_path.exists() or not base_path.is_dir():
            return skill_dirs

        # Check if base_path itself is a skill
        if (base_path / SKILL_FILE).exists():
            skill_dirs.append(base_path)
            return skill_dirs

        # Search subdirectories (non-recursive for now)
        for item in base_path.iterdir():
            if item.is_dir() and (item / SKILL_FILE).exists():
                skill_dirs.append(item)

        return sorted(skill_dirs)


# Singleton instance
_loader: SkillLoader | None = None


def get_loader() -> SkillLoader:
    """Get the singleton loader instance."""
    global _loader
    if _loader is None:
        _loader = SkillLoader()
    return _loader

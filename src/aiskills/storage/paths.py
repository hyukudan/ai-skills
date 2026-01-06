"""Path resolution for skill directories."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from ..config import AppConfig, get_config
from ..constants import GLOBAL_BASE, PROJECT_DIRS, SKILLS_DIR


class PathResolver:
    """Resolves paths for skill storage and lookup.

    Implements priority-based path resolution:
    1. Project .aiskills/skills/ (highest priority)
    2. Project .claude/skills/ (Claude compatibility)
    3. Project .agent/skills/ (universal compatibility)
    4. Global ~/.aiskills/skills/
    """

    def __init__(self, config: AppConfig | None = None, cwd: Path | None = None):
        self.config = config or get_config()
        self.cwd = cwd or Path.cwd()

    @property
    def global_base(self) -> Path:
        """Get global aiskills directory."""
        return self.config.storage.global_dir

    @property
    def global_skills_dir(self) -> Path:
        """Get global skills directory."""
        return self.global_base / SKILLS_DIR

    def get_project_base(self, location: str = ".aiskills") -> Path:
        """Get project-level aiskills directory."""
        return self.cwd / location

    def get_project_skills_dir(self, location: str = ".aiskills") -> Path:
        """Get project-level skills directory."""
        return self.get_project_base(location) / SKILLS_DIR

    def get_search_dirs(self) -> list[tuple[Path, Literal[".aiskills", ".claude", ".agent"]]]:
        """Get all directories to search for skills, in priority order.

        Returns:
            List of (path, location_type) tuples, highest priority first
        """
        dirs: list[tuple[Path, Literal[".aiskills", ".claude", ".agent"]]] = []

        # Project directories (highest priority)
        for location in PROJECT_DIRS:
            project_path = self.cwd / location / SKILLS_DIR
            if project_path.exists():
                location_type: Literal[".aiskills", ".claude", ".agent"]
                if location == ".aiskills":
                    location_type = ".aiskills"
                elif location == ".claude":
                    location_type = ".claude"
                else:
                    location_type = ".agent"
                dirs.append((project_path, location_type))

        # Global directory (lowest priority)
        global_path = self.global_skills_dir
        if global_path.exists():
            dirs.append((global_path, ".aiskills"))

        return dirs

    def get_all_search_paths(self) -> list[Path]:
        """Get all search paths without location type info."""
        return [path for path, _ in self.get_search_dirs()]

    def find_skill(
        self, name: str
    ) -> tuple[Path, Literal["project", "global"], Literal[".aiskills", ".claude", ".agent"]] | None:
        """Find a skill by name in search paths.

        Args:
            name: Skill name to find

        Returns:
            Tuple of (path, source, location_type) or None if not found
        """
        for skills_dir, location_type in self.get_search_dirs():
            skill_path = skills_dir / name
            if skill_path.exists() and (skill_path / "SKILL.md").exists():
                # Determine source based on path
                source: Literal["project", "global"]
                if str(skills_dir).startswith(str(self.cwd)):
                    source = "project"
                else:
                    source = "global"
                return skill_path, source, location_type

        return None

    def get_install_path(
        self,
        name: str,
        global_install: bool = False,
        location: str = ".aiskills",
    ) -> Path:
        """Get the path where a skill should be installed.

        Args:
            name: Skill name
            global_install: If True, install globally
            location: Project directory to use (default .aiskills)

        Returns:
            Path where skill should be installed
        """
        if global_install:
            return self.global_skills_dir / name
        else:
            return self.get_project_skills_dir(location) / name

    def ensure_dirs(self, global_install: bool = False, location: str = ".aiskills") -> Path:
        """Ensure skill directories exist and return skills dir.

        Args:
            global_install: If True, create global dirs
            location: Project directory to use

        Returns:
            Path to skills directory (created if needed)
        """
        if global_install:
            skills_dir = self.global_skills_dir
        else:
            skills_dir = self.get_project_skills_dir(location)

        skills_dir.mkdir(parents=True, exist_ok=True)
        return skills_dir

    def get_lock_file_path(self, global_install: bool = False) -> Path:
        """Get path to lock file.

        Args:
            global_install: If True, get global lock file

        Returns:
            Path to aiskills.lock
        """
        from ..constants import LOCK_FILE

        if global_install:
            return self.global_base / LOCK_FILE
        return self.cwd / ".aiskills" / LOCK_FILE

    def get_cache_dir(self) -> Path:
        """Get cache directory for remote skills."""
        from ..constants import CACHE_DIR

        cache_dir = self.global_base / CACHE_DIR
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir

    def get_registry_dir(self) -> Path:
        """Get registry directory for index and vectors."""
        from ..constants import REGISTRY_DIR

        registry_dir = self.global_base / REGISTRY_DIR
        registry_dir.mkdir(parents=True, exist_ok=True)
        return registry_dir

    def expand_path(self, path: str) -> Path:
        """Expand a path string, handling ~ and relative paths.

        Args:
            path: Path string (can be ~, relative, or absolute)

        Returns:
            Expanded absolute Path
        """
        p = Path(path).expanduser()
        if not p.is_absolute():
            p = self.cwd / p
        return p.resolve()

    def is_local_path(self, source: str) -> bool:
        """Check if a source string is a local path.

        Returns True for:
        - Absolute paths: /path/to/skill
        - Relative paths: ./skill, ../skill
        - Home paths: ~/skills/my-skill

        Returns False for:
        - GitHub shorthand: owner/repo
        - Git URLs: git@github.com:..., https://github.com/...
        """
        # Git URLs
        if source.startswith(("git@", "https://", "http://", "ssh://")):
            return False

        # Explicit local paths
        if source.startswith(("/", "./", "../", "~")):
            return True

        # Check if it looks like a GitHub shorthand (owner/repo with no slashes after)
        # vs a local path with subdirectories
        parts = source.split("/")
        if len(parts) == 2 and not Path(source).exists():
            # Likely GitHub shorthand if path doesn't exist
            return False

        # If path exists locally, it's local
        return Path(source).expanduser().exists()


# Singleton instance
_resolver: PathResolver | None = None


def get_path_resolver() -> PathResolver:
    """Get the singleton path resolver instance."""
    global _resolver
    if _resolver is None:
        _resolver = PathResolver()
    return _resolver

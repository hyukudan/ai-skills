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
from ..models.skill import Skill
from .parser import ParseError, YAMLParser, get_parser


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
    ) -> Skill:
        """Load a skill from a directory path.

        Args:
            path: Path to skill directory (must contain SKILL.md)
            source: Where the skill came from
            location_type: Which directory structure it's in

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

        # Read and parse
        raw_content = skill_file.read_text(encoding="utf-8")

        try:
            result = self.parser.parse(raw_content)
        except ParseError as e:
            raise LoadError(str(e), str(skill_file)) from e

        return Skill(
            manifest=result.manifest,
            content=result.content,
            raw_content=result.raw_content,
            path=str(path.absolute()),
            source=source,
            location_type=location_type,
        )

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

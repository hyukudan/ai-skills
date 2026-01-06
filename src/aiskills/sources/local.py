"""Local filesystem source for skills."""

from __future__ import annotations

from pathlib import Path

from ..constants import SKILL_FILE
from ..core.loader import SkillLoader, get_loader
from .base import FetchedSkill, FetchError, SkillSource


class LocalSource(SkillSource):
    """Handles skills from local filesystem paths.

    Matches:
    - Absolute paths: /path/to/skill
    - Relative paths: ./skill, ../skill
    - Home paths: ~/skills/my-skill
    """

    def __init__(self, loader: SkillLoader | None = None):
        self.loader = loader or get_loader()

    def matches(self, source: str) -> bool:
        """Check if source is a local path."""
        # Explicit local path indicators
        if source.startswith(("/", "./", "../", "~")):
            return True

        # Check if path exists locally
        path = Path(source).expanduser()
        return path.exists()

    def fetch(self, source: str) -> list[FetchedSkill]:
        """Fetch skills from local path.

        If path is a skill directory (has SKILL.md), returns that skill.
        If path is a directory of skills, returns all skills found.
        """
        path = Path(source).expanduser().resolve()

        if not path.exists():
            raise FetchError(f"Path does not exist: {path}", source)

        if not path.is_dir():
            raise FetchError(f"Path is not a directory: {path}", source)

        skills: list[FetchedSkill] = []

        # Check if this is a skill directory
        if (path / SKILL_FILE).exists():
            skill_name = path.name
            skills.append(
                FetchedSkill(
                    name=skill_name,
                    path=path,
                    source_string=f"local:{path}",
                )
            )
        else:
            # Search for skills in subdirectories
            for skill_dir in self.loader.list_skill_dirs(path):
                skills.append(
                    FetchedSkill(
                        name=skill_dir.name,
                        path=skill_dir,
                        source_string=f"local:{skill_dir}",
                    )
                )

        if not skills:
            raise FetchError(
                f"No skills found at {path}. Expected SKILL.md file.", source
            )

        return skills

    def cleanup(self) -> None:
        """No cleanup needed for local sources."""
        pass

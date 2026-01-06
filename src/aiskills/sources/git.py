"""Git repository source for skills."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from ..constants import SKILL_FILE
from ..core.loader import SkillLoader, get_loader
from ..storage.cache import CacheManager, get_cache_manager
from .base import FetchedSkill, FetchError, SkillSource


class GitSource(SkillSource):
    """Handles skills from Git repositories.

    Matches:
    - SSH URLs: git@github.com:owner/repo.git
    - HTTPS URLs: https://github.com/owner/repo.git
    - Git protocol: git://github.com/owner/repo.git
    """

    def __init__(
        self,
        loader: SkillLoader | None = None,
        cache: CacheManager | None = None,
    ):
        self.loader = loader or get_loader()
        self.cache = cache or get_cache_manager()
        self._temp_dirs: list[Path] = []

    def matches(self, source: str) -> bool:
        """Check if source is a Git URL."""
        git_prefixes = (
            "git@",
            "https://",
            "http://",
            "git://",
            "ssh://",
        )
        return source.startswith(git_prefixes) and (
            ".git" in source or "github.com" in source or "gitlab.com" in source
        )

    def fetch(self, source: str) -> list[FetchedSkill]:
        """Clone repo and fetch skills."""
        import subprocess

        # Check cache first
        cached_path = self.cache.get("git", source)
        if cached_path:
            return self._find_skills_in_dir(cached_path, source)

        # Create cache directory
        clone_path = self.cache.set("git", source)

        try:
            # Clone with depth 1 for speed
            result = subprocess.run(
                ["git", "clone", "--depth", "1", source, str(clone_path / "repo")],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode != 0:
                raise FetchError(
                    f"Git clone failed: {result.stderr.strip()}", source
                )

            repo_path = clone_path / "repo"
            return self._find_skills_in_dir(repo_path, source)

        except subprocess.TimeoutExpired:
            raise FetchError("Git clone timed out", source)
        except FileNotFoundError:
            raise FetchError(
                "Git is not installed. Please install git.", source
            )

    def _find_skills_in_dir(self, path: Path, source: str) -> list[FetchedSkill]:
        """Find all skills in a directory."""
        skills: list[FetchedSkill] = []

        # Check if root is a skill
        if (path / SKILL_FILE).exists():
            skills.append(
                FetchedSkill(
                    name=path.name,
                    path=path,
                    source_string=f"git:{source}",
                )
            )
            return skills

        # Search subdirectories
        for skill_dir in self.loader.list_skill_dirs(path):
            skills.append(
                FetchedSkill(
                    name=skill_dir.name,
                    path=skill_dir,
                    source_string=f"git:{source}/{skill_dir.name}",
                )
            )

        # Also check nested directories (skills/*)
        skills_subdir = path / "skills"
        if skills_subdir.exists():
            for skill_dir in self.loader.list_skill_dirs(skills_subdir):
                if skill_dir.name not in [s.name for s in skills]:
                    skills.append(
                        FetchedSkill(
                            name=skill_dir.name,
                            path=skill_dir,
                            source_string=f"git:{source}/skills/{skill_dir.name}",
                        )
                    )

        if not skills:
            raise FetchError(
                f"No skills found in repository. Expected SKILL.md files.", source
            )

        return skills

    def cleanup(self) -> None:
        """Clean up temporary directories."""
        for temp_dir in self._temp_dirs:
            if temp_dir.exists():
                shutil.rmtree(temp_dir, ignore_errors=True)
        self._temp_dirs.clear()

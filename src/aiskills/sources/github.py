"""GitHub shorthand source for skills."""

from __future__ import annotations

import re
from pathlib import Path

from ..constants import SKILL_FILE
from ..core.loader import SkillLoader, get_loader
from ..storage.cache import CacheManager, get_cache_manager
from .base import FetchedSkill, FetchError, SkillSource


class GitHubSource(SkillSource):
    """Handles GitHub shorthand notation.

    Matches:
    - owner/repo - All skills in repo
    - owner/repo/path/to/skill - Specific skill
    - owner/repo@branch - Specific branch
    - owner/repo/path@branch - Specific skill on branch
    """

    # Pattern: owner/repo[/path][@branch]
    PATTERN = re.compile(
        r"^(?P<owner>[a-zA-Z0-9_-]+)/(?P<repo>[a-zA-Z0-9_.-]+)"
        r"(?:/(?P<path>[^@]+))?"
        r"(?:@(?P<branch>.+))?$"
    )

    def __init__(
        self,
        loader: SkillLoader | None = None,
        cache: CacheManager | None = None,
    ):
        self.loader = loader or get_loader()
        self.cache = cache or get_cache_manager()

    def matches(self, source: str) -> bool:
        """Check if source is GitHub shorthand."""
        # Must not be a URL or local path
        if source.startswith(("/", "./", "../", "~", "http", "git@", "ssh://")):
            return False

        # Must match pattern
        return bool(self.PATTERN.match(source))

    def _parse_source(self, source: str) -> tuple[str, str, str | None, str]:
        """Parse GitHub shorthand into components.

        Returns:
            Tuple of (owner, repo, subpath, branch)
        """
        match = self.PATTERN.match(source)
        if not match:
            raise FetchError(f"Invalid GitHub shorthand: {source}", source)

        owner = match.group("owner")
        repo = match.group("repo")
        subpath = match.group("path")
        branch = match.group("branch") or "main"

        return owner, repo, subpath, branch

    def fetch(self, source: str) -> list[FetchedSkill]:
        """Fetch skills from GitHub."""
        import subprocess

        owner, repo, subpath, branch = self._parse_source(source)

        # Build clone URL
        clone_url = f"https://github.com/{owner}/{repo}.git"
        cache_key = f"{owner}/{repo}@{branch}"

        # Check cache
        cached_path = self.cache.get("github", cache_key)
        if cached_path:
            repo_path = cached_path / "repo"
            if repo_path.exists():
                return self._find_skills(repo_path, subpath, source)

        # Clone to cache
        clone_path = self.cache.set("github", cache_key)
        repo_path = clone_path / "repo"

        try:
            # Clone specific branch with depth 1
            result = subprocess.run(
                [
                    "git", "clone",
                    "--depth", "1",
                    "--branch", branch,
                    clone_url,
                    str(repo_path),
                ],
                capture_output=True,
                text=True,
                timeout=120,
            )

            if result.returncode != 0:
                # Try without branch (might be main vs master)
                result = subprocess.run(
                    [
                        "git", "clone",
                        "--depth", "1",
                        clone_url,
                        str(repo_path),
                    ],
                    capture_output=True,
                    text=True,
                    timeout=120,
                )

                if result.returncode != 0:
                    raise FetchError(
                        f"Failed to clone: {result.stderr.strip()}", source
                    )

            return self._find_skills(repo_path, subpath, source)

        except subprocess.TimeoutExpired:
            raise FetchError("Clone timed out", source)
        except FileNotFoundError:
            raise FetchError("Git is not installed", source)

    def _find_skills(
        self,
        repo_path: Path,
        subpath: str | None,
        source: str,
    ) -> list[FetchedSkill]:
        """Find skills in cloned repo."""
        skills: list[FetchedSkill] = []

        # If subpath specified, look only there
        if subpath:
            target_path = repo_path / subpath
            if not target_path.exists():
                raise FetchError(
                    f"Path '{subpath}' not found in repository", source
                )

            if (target_path / SKILL_FILE).exists():
                # Direct skill path
                skills.append(
                    FetchedSkill(
                        name=target_path.name,
                        path=target_path,
                        source_string=f"github:{source}",
                    )
                )
            else:
                # Directory of skills
                for skill_dir in self.loader.list_skill_dirs(target_path):
                    skills.append(
                        FetchedSkill(
                            name=skill_dir.name,
                            path=skill_dir,
                            source_string=f"github:{source}/{skill_dir.name}",
                        )
                    )
        else:
            # Search entire repo
            # Check root
            if (repo_path / SKILL_FILE).exists():
                skills.append(
                    FetchedSkill(
                        name=repo_path.name,
                        path=repo_path,
                        source_string=f"github:{source}",
                    )
                )
            else:
                # Check immediate subdirectories
                for skill_dir in self.loader.list_skill_dirs(repo_path):
                    skills.append(
                        FetchedSkill(
                            name=skill_dir.name,
                            path=skill_dir,
                            source_string=f"github:{source}/{skill_dir.name}",
                        )
                    )

                # Also check skills/ subdirectory
                skills_subdir = repo_path / "skills"
                if skills_subdir.exists():
                    for skill_dir in self.loader.list_skill_dirs(skills_subdir):
                        if skill_dir.name not in [s.name for s in skills]:
                            skills.append(
                                FetchedSkill(
                                    name=skill_dir.name,
                                    path=skill_dir,
                                    source_string=f"github:{source}/skills/{skill_dir.name}",
                                )
                            )

        if not skills:
            raise FetchError(
                "No skills found. Expected directories with SKILL.md files.", source
            )

        return skills

    def cleanup(self) -> None:
        """Cleanup is handled by cache manager."""
        pass

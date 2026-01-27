"""Source resolver - detects and uses appropriate source handler."""

from __future__ import annotations

from .base import FetchedSkill, FetchError, SkillSource
from .git import GitSource
from .github import GitHubSource
from .local import LocalSource
from .registry import RegistrySource


class SourceResolver:
    """Resolves source strings to appropriate handlers.

    Tries handlers in order until one matches.
    Supports:
    - Local paths: ./skill, /path/to/skill, ~/skills/name
    - Git URLs: https://github.com/owner/repo.git, git@github.com:owner/repo
    - GitHub shorthand: owner/repo, owner/repo/skill-name
    - Registry: registry:skill-name, registry:skill@1.2.3, skill-slug
    """

    def __init__(self):
        # Order matters - more specific first
        self.handlers: list[SkillSource] = [
            LocalSource(),
            GitSource(),
            GitHubSource(),
            RegistrySource(),  # Last: matches bare slugs as fallback
        ]

    def resolve(self, source: str) -> SkillSource:
        """Find the handler that matches the source.

        Args:
            source: Source string

        Returns:
            Matching source handler

        Raises:
            FetchError: If no handler matches
        """
        for handler in self.handlers:
            if handler.matches(source):
                return handler

        raise FetchError(
            f"Unknown source format: {source}. "
            "Expected: local path, git URL, or owner/repo",
            source,
        )

    def fetch(self, source: str) -> list[FetchedSkill]:
        """Fetch skills from source using appropriate handler.

        Args:
            source: Source string

        Returns:
            List of fetched skills
        """
        handler = self.resolve(source)
        return handler.fetch(source)

    def cleanup_all(self) -> None:
        """Clean up all handlers."""
        for handler in self.handlers:
            handler.cleanup()


# Singleton instance
_resolver: SourceResolver | None = None


def get_source_resolver() -> SourceResolver:
    """Get the singleton source resolver."""
    global _resolver
    if _resolver is None:
        _resolver = SourceResolver()
    return _resolver

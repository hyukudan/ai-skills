"""Base class for skill sources."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path


@dataclass
class FetchedSkill:
    """A skill fetched from a source."""

    name: str
    path: Path  # Path to skill directory
    source_string: str  # e.g., "github:owner/repo/skill-name"


class SkillSource(ABC):
    """Abstract base class for skill sources.

    Skill sources handle fetching skills from different locations:
    - Local filesystem
    - Git repositories
    - GitHub (shorthand)
    - Future: npm, marketplace, etc.
    """

    @abstractmethod
    def matches(self, source: str) -> bool:
        """Check if this source handler matches the given source string.

        Args:
            source: Source string (path, URL, shorthand, etc.)

        Returns:
            True if this handler can process the source
        """
        ...

    @abstractmethod
    def fetch(self, source: str) -> list[FetchedSkill]:
        """Fetch skills from the source.

        Args:
            source: Source string

        Returns:
            List of fetched skills with paths and metadata

        Raises:
            FetchError: If fetching fails
        """
        ...

    @abstractmethod
    def cleanup(self) -> None:
        """Clean up any temporary resources."""
        ...


class FetchError(Exception):
    """Error fetching skills from a source."""

    def __init__(self, message: str, source: str | None = None):
        self.source = source
        if source:
            message = f"{source}: {message}"
        super().__init__(message)

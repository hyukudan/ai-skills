"""Lock file models for reproducible installations."""

from __future__ import annotations

import hashlib
import time

from pydantic import BaseModel, Field, computed_field

from .. import __version__


class LockedSkill(BaseModel):
    """A skill as recorded in the lock file."""

    name: str
    version: str
    content_hash: str
    source: str  # e.g., "github:owner/repo", "local:/path", "git:https://..."
    resolved_dependencies: list[str] = Field(default_factory=list)  # ["name@version", ...]
    installed_at: float = Field(default_factory=time.time)


class LockFile(BaseModel):
    """The aiskills.lock file structure.

    Ensures reproducible installations across machines and time.
    """

    version: str = "1"  # Lock file format version
    generated_at: float = Field(default_factory=time.time)
    aiskills_version: str = Field(default_factory=lambda: __version__)

    skills: dict[str, LockedSkill] = Field(default_factory=dict)

    @computed_field
    @property
    def checksum(self) -> str:
        """Compute integrity checksum of all skills."""
        hashes = sorted(f"{name}:{s.content_hash}" for name, s in self.skills.items())
        combined = "\n".join(hashes)
        return hashlib.sha256(combined.encode()).hexdigest()[:16]

    def add_skill(self, skill: LockedSkill) -> None:
        """Add or update a skill in the lock file."""
        self.skills[skill.name] = skill

    def remove_skill(self, name: str) -> bool:
        """Remove a skill from the lock file."""
        if name in self.skills:
            del self.skills[name]
            return True
        return False

    def get_skill(self, name: str) -> LockedSkill | None:
        """Get a locked skill by name."""
        return self.skills.get(name)

    def has_skill(self, name: str, version: str | None = None) -> bool:
        """Check if a skill is locked, optionally at a specific version."""
        if name not in self.skills:
            return False
        if version is None:
            return True
        return self.skills[name].version == version

    def list_skills(self) -> list[tuple[str, str]]:
        """List all locked skills as (name, version) tuples."""
        return [(name, s.version) for name, s in sorted(self.skills.items())]

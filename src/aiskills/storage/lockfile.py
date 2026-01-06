"""Lock file management for reproducible installations."""

from __future__ import annotations

from pathlib import Path

import yaml

from ..models.lock import LockedSkill, LockFile
from ..models.skill import Skill
from .paths import PathResolver, get_path_resolver


class LockFileManager:
    """Manages aiskills.lock files.

    The lock file ensures reproducible installations by recording:
    - Exact versions installed
    - Content hashes for integrity
    - Source information
    - Resolved dependencies
    """

    def __init__(self, paths: PathResolver | None = None):
        self.paths = paths or get_path_resolver()
        self._lock: LockFile | None = None
        self._lock_path: Path | None = None

    def load(self, global_install: bool = False, create: bool = True) -> LockFile:
        """Load lock file from disk.

        Args:
            global_install: Load global lock file if True
            create: Create new lock file if doesn't exist

        Returns:
            Loaded or new LockFile
        """
        lock_path = self.paths.get_lock_file_path(global_install)
        self._lock_path = lock_path

        if lock_path.exists():
            with open(lock_path) as f:
                data = yaml.safe_load(f) or {}

            # Parse skills
            skills_data = data.get("skills", {})
            skills = {}
            for name, skill_data in skills_data.items():
                skills[name] = LockedSkill(**skill_data)

            self._lock = LockFile(
                version=data.get("version", "1"),
                generated_at=data.get("generated_at", 0),
                aiskills_version=data.get("aiskills_version", "unknown"),
                skills=skills,
            )
        elif create:
            self._lock = LockFile()
        else:
            raise FileNotFoundError(f"Lock file not found: {lock_path}")

        return self._lock

    def save(self) -> None:
        """Save lock file to disk."""
        if self._lock is None:
            raise RuntimeError("No lock file loaded")
        if self._lock_path is None:
            raise RuntimeError("No lock path set")

        # Ensure directory exists
        self._lock_path.parent.mkdir(parents=True, exist_ok=True)

        # Convert to serializable dict
        data = {
            "version": self._lock.version,
            "generated_at": self._lock.generated_at,
            "aiskills_version": self._lock.aiskills_version,
            "skills": {
                name: {
                    "name": s.name,
                    "version": s.version,
                    "content_hash": s.content_hash,
                    "source": s.source,
                    "resolved_dependencies": s.resolved_dependencies,
                    "installed_at": s.installed_at,
                }
                for name, s in self._lock.skills.items()
            },
            "checksum": self._lock.checksum,
        }

        with open(self._lock_path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

    def add_skill(self, skill: Skill, source: str) -> None:
        """Add a skill to the lock file.

        Args:
            skill: Skill to add
            source: Source string (e.g., "github:owner/repo")
        """
        if self._lock is None:
            self.load()

        assert self._lock is not None

        # Build resolved dependencies list
        deps = [f"{d.name}@{d.version}" for d in skill.manifest.dependencies]

        locked = LockedSkill(
            name=skill.manifest.name,
            version=skill.manifest.version,
            content_hash=skill.content_hash,
            source=source,
            resolved_dependencies=deps,
        )

        self._lock.add_skill(locked)

    def remove_skill(self, name: str) -> bool:
        """Remove a skill from the lock file.

        Args:
            name: Skill name to remove

        Returns:
            True if skill was removed, False if not found
        """
        if self._lock is None:
            self.load()

        assert self._lock is not None
        return self._lock.remove_skill(name)

    def has_skill(self, name: str, version: str | None = None) -> bool:
        """Check if a skill is in the lock file.

        Args:
            name: Skill name
            version: Optional specific version

        Returns:
            True if skill is locked (at version if specified)
        """
        if self._lock is None:
            try:
                self.load(create=False)
            except FileNotFoundError:
                return False

        assert self._lock is not None
        return self._lock.has_skill(name, version)

    def get_locked_skill(self, name: str) -> LockedSkill | None:
        """Get locked skill info.

        Args:
            name: Skill name

        Returns:
            LockedSkill or None if not found
        """
        if self._lock is None:
            try:
                self.load(create=False)
            except FileNotFoundError:
                return None

        assert self._lock is not None
        return self._lock.get_skill(name)

    def verify_integrity(self, skill: Skill) -> bool:
        """Verify a skill matches its locked hash.

        Args:
            skill: Skill to verify

        Returns:
            True if hash matches, False otherwise
        """
        locked = self.get_locked_skill(skill.manifest.name)
        if locked is None:
            return False
        return locked.content_hash == skill.content_hash

    def list_locked(self) -> list[tuple[str, str]]:
        """List all locked skills.

        Returns:
            List of (name, version) tuples
        """
        if self._lock is None:
            try:
                self.load(create=False)
            except FileNotFoundError:
                return []

        assert self._lock is not None
        return self._lock.list_skills()

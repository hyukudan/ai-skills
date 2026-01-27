"""Semantic versioning utilities for skill version management."""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum
from functools import total_ordering
from typing import Literal


class VersionBump(str, Enum):
    """Type of version increment."""

    MAJOR = "major"
    MINOR = "minor"
    PATCH = "patch"
    PRERELEASE = "prerelease"


@total_ordering
@dataclass
class SemanticVersion:
    """Semantic version representation (semver 2.0.0).

    Supports versions like:
    - 1.0.0
    - 1.2.3-alpha.1
    - 2.0.0-beta+build.123
    """

    major: int
    minor: int
    patch: int
    prerelease: str | None = None
    build: str | None = None

    # Regex for parsing semver
    PATTERN = re.compile(
        r"^(?P<major>0|[1-9]\d*)"
        r"\.(?P<minor>0|[1-9]\d*)"
        r"\.(?P<patch>0|[1-9]\d*)"
        r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
        r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
        r"(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
    )

    @classmethod
    def parse(cls, version_str: str) -> "SemanticVersion":
        """Parse a version string into SemanticVersion.

        Args:
            version_str: Version string (e.g., "1.2.3-alpha")

        Returns:
            SemanticVersion instance

        Raises:
            ValueError: If version string is invalid
        """
        # Strip leading 'v' if present
        if version_str.startswith("v"):
            version_str = version_str[1:]

        match = cls.PATTERN.match(version_str)
        if not match:
            raise ValueError(f"Invalid semantic version: {version_str}")

        return cls(
            major=int(match.group("major")),
            minor=int(match.group("minor")),
            patch=int(match.group("patch")),
            prerelease=match.group("prerelease"),
            build=match.group("build"),
        )

    @classmethod
    def try_parse(cls, version_str: str) -> "SemanticVersion | None":
        """Try to parse a version string, returning None on failure."""
        try:
            return cls.parse(version_str)
        except ValueError:
            return None

    def __str__(self) -> str:
        """Convert to string representation."""
        version = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version += f"-{self.prerelease}"
        if self.build:
            version += f"+{self.build}"
        return version

    def __eq__(self, other: object) -> bool:
        """Check equality (build metadata ignored per semver spec)."""
        if not isinstance(other, SemanticVersion):
            return NotImplemented
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.prerelease == other.prerelease
        )

    def __lt__(self, other: "SemanticVersion") -> bool:
        """Compare versions (build metadata ignored per semver spec)."""
        if not isinstance(other, SemanticVersion):
            return NotImplemented

        # Compare major.minor.patch
        self_tuple = (self.major, self.minor, self.patch)
        other_tuple = (other.major, other.minor, other.patch)

        if self_tuple != other_tuple:
            return self_tuple < other_tuple

        # Prerelease has lower precedence than release
        if self.prerelease is None and other.prerelease is None:
            return False
        if self.prerelease is None:
            return False  # Release > prerelease
        if other.prerelease is None:
            return True  # Prerelease < release

        # Compare prerelease identifiers
        return self._compare_prerelease(self.prerelease, other.prerelease) < 0

    @staticmethod
    def _compare_prerelease(a: str, b: str) -> int:
        """Compare prerelease strings per semver spec."""
        a_parts = a.split(".")
        b_parts = b.split(".")

        for i in range(max(len(a_parts), len(b_parts))):
            if i >= len(a_parts):
                return -1  # Fewer parts = lower precedence
            if i >= len(b_parts):
                return 1

            a_part = a_parts[i]
            b_part = b_parts[i]

            # Numeric identifiers compare as integers
            a_num = a_part.isdigit()
            b_num = b_part.isdigit()

            if a_num and b_num:
                diff = int(a_part) - int(b_part)
                if diff != 0:
                    return diff
            elif a_num:
                return -1  # Numeric < alphanumeric
            elif b_num:
                return 1
            else:
                # Compare as strings
                if a_part < b_part:
                    return -1
                if a_part > b_part:
                    return 1

        return 0

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash((self.major, self.minor, self.patch, self.prerelease))

    def bump(self, bump_type: VersionBump) -> "SemanticVersion":
        """Create a new version with the specified bump.

        Args:
            bump_type: Type of version increment

        Returns:
            New SemanticVersion with incremented version
        """
        if bump_type == VersionBump.MAJOR:
            return SemanticVersion(self.major + 1, 0, 0)
        elif bump_type == VersionBump.MINOR:
            return SemanticVersion(self.major, self.minor + 1, 0)
        elif bump_type == VersionBump.PATCH:
            return SemanticVersion(self.major, self.minor, self.patch + 1)
        elif bump_type == VersionBump.PRERELEASE:
            # Increment prerelease or add .1
            if self.prerelease:
                parts = self.prerelease.split(".")
                # Try to increment last numeric part
                for i in range(len(parts) - 1, -1, -1):
                    if parts[i].isdigit():
                        parts[i] = str(int(parts[i]) + 1)
                        return SemanticVersion(
                            self.major, self.minor, self.patch,
                            prerelease=".".join(parts)
                        )
                # No numeric part, append .1
                return SemanticVersion(
                    self.major, self.minor, self.patch,
                    prerelease=f"{self.prerelease}.1"
                )
            else:
                return SemanticVersion(
                    self.major, self.minor, self.patch + 1,
                    prerelease="alpha.1"
                )
        raise ValueError(f"Unknown bump type: {bump_type}")

    @property
    def is_prerelease(self) -> bool:
        """Check if this is a prerelease version."""
        return self.prerelease is not None

    @property
    def is_stable(self) -> bool:
        """Check if this is a stable release (>= 1.0.0, no prerelease)."""
        return self.major >= 1 and not self.is_prerelease


@dataclass
class VersionConstraint:
    """Version constraint for dependency resolution.

    Supports:
    - Exact: =1.2.3 or 1.2.3
    - Range: >=1.0.0 <2.0.0
    - Caret: ^1.2.3 (>=1.2.3 <2.0.0)
    - Tilde: ~1.2.3 (>=1.2.3 <1.3.0)
    - Wildcard: 1.2.* (>=1.2.0 <1.3.0)
    - Latest: * or latest
    """

    operator: Literal["=", ">=", "<=", ">", "<", "^", "~", "*"]
    version: SemanticVersion | None
    upper_bound: SemanticVersion | None = None  # For ranges

    @classmethod
    def parse(cls, constraint_str: str) -> "VersionConstraint":
        """Parse a constraint string.

        Args:
            constraint_str: Constraint (e.g., "^1.2.3", ">=1.0.0")

        Returns:
            VersionConstraint instance
        """
        constraint_str = constraint_str.strip()

        # Latest/any
        if constraint_str in ("*", "latest", ""):
            return cls(operator="*", version=None)

        # Caret (compatible with)
        if constraint_str.startswith("^"):
            version = SemanticVersion.parse(constraint_str[1:])
            return cls(operator="^", version=version)

        # Tilde (patch-level changes)
        if constraint_str.startswith("~"):
            version = SemanticVersion.parse(constraint_str[1:])
            return cls(operator="~", version=version)

        # Comparison operators
        for op in (">=", "<=", ">", "<", "="):
            if constraint_str.startswith(op):
                version = SemanticVersion.parse(constraint_str[len(op):])
                return cls(operator=op, version=version)

        # Wildcard (1.2.*)
        if "*" in constraint_str:
            parts = constraint_str.replace("*", "0").split(".")
            while len(parts) < 3:
                parts.append("0")
            version = SemanticVersion(
                int(parts[0]), int(parts[1]), int(parts[2])
            )
            return cls(operator="~", version=version)

        # Exact (no operator)
        version = SemanticVersion.parse(constraint_str)
        return cls(operator="=", version=version)

    def satisfies(self, version: SemanticVersion) -> bool:
        """Check if a version satisfies this constraint.

        Args:
            version: Version to check

        Returns:
            True if version satisfies the constraint
        """
        if self.operator == "*":
            return True

        if self.version is None:
            return True

        if self.operator == "=":
            return version == self.version

        if self.operator == ">=":
            return version >= self.version

        if self.operator == "<=":
            return version <= self.version

        if self.operator == ">":
            return version > self.version

        if self.operator == "<":
            return version < self.version

        if self.operator == "^":
            # ^1.2.3 means >=1.2.3 <2.0.0 (for major > 0)
            # ^0.2.3 means >=0.2.3 <0.3.0 (for major = 0)
            if version < self.version:
                return False
            if self.version.major == 0:
                return version.major == 0 and version.minor == self.version.minor
            return version.major == self.version.major

        if self.operator == "~":
            # ~1.2.3 means >=1.2.3 <1.3.0
            if version < self.version:
                return False
            return (
                version.major == self.version.major
                and version.minor == self.version.minor
            )

        return False

    def __str__(self) -> str:
        """String representation."""
        if self.operator == "*":
            return "*"
        return f"{self.operator}{self.version}"


def compare_versions(v1: str, v2: str) -> int:
    """Compare two version strings.

    Args:
        v1: First version
        v2: Second version

    Returns:
        -1 if v1 < v2, 0 if equal, 1 if v1 > v2
    """
    ver1 = SemanticVersion.parse(v1)
    ver2 = SemanticVersion.parse(v2)

    if ver1 < ver2:
        return -1
    if ver1 > ver2:
        return 1
    return 0


def is_newer(current: str, candidate: str) -> bool:
    """Check if candidate version is newer than current.

    Args:
        current: Current version string
        candidate: Candidate version string

    Returns:
        True if candidate is newer
    """
    return compare_versions(candidate, current) > 0


def find_latest(versions: list[str], include_prerelease: bool = False) -> str | None:
    """Find the latest version from a list.

    Args:
        versions: List of version strings
        include_prerelease: Include prerelease versions

    Returns:
        Latest version string or None if list is empty
    """
    if not versions:
        return None

    parsed = []
    for v in versions:
        try:
            sv = SemanticVersion.parse(v)
            if include_prerelease or not sv.is_prerelease:
                parsed.append((sv, v))
        except ValueError:
            continue

    if not parsed:
        return None

    parsed.sort(key=lambda x: x[0], reverse=True)
    return parsed[0][1]


def satisfies_constraint(version: str, constraint: str) -> bool:
    """Check if a version satisfies a constraint.

    Args:
        version: Version string
        constraint: Constraint string (e.g., "^1.2.3")

    Returns:
        True if version satisfies constraint
    """
    ver = SemanticVersion.parse(version)
    con = VersionConstraint.parse(constraint)
    return con.satisfies(ver)

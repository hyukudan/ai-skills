"""Dependency models for skill versioning and resolution."""

from __future__ import annotations

import re
from enum import Enum
from typing import Literal

from packaging.specifiers import SpecifierSet
from packaging.version import Version
from pydantic import BaseModel, Field, model_validator


class VersionOperator(str, Enum):
    """Version constraint operators."""

    EXACT = "="
    GTE = ">="
    LTE = "<="
    GT = ">"
    LT = "<"
    CARET = "^"  # Compatible with (same major)
    TILDE = "~"  # Approximately (same minor)
    ANY = "*"


class SkillDependency(BaseModel):
    """A dependency on another skill with version constraints."""

    name: str
    version: str = "*"  # Version constraint string
    optional: bool = False

    @model_validator(mode="after")
    def validate_version_constraint(self) -> SkillDependency:
        """Validate that version constraint is parseable."""
        if self.version != "*":
            try:
                self.to_specifier()
            except Exception as e:
                raise ValueError(f"Invalid version constraint '{self.version}': {e}") from e
        return self

    def to_specifier(self) -> SpecifierSet:
        """Convert version constraint to packaging SpecifierSet.

        Supports npm-like syntax:
        - "*" -> any version
        - "1.0.0" -> ==1.0.0
        - ">=1.0.0" -> >=1.0.0
        - "^1.2.3" -> >=1.2.3,<2.0.0 (caret = compatible)
        - "~1.2.3" -> >=1.2.3,<1.3.0 (tilde = approximately)
        """
        v = self.version.strip()

        if v == "*":
            return SpecifierSet()  # Matches any version

        # Caret: ^1.2.3 means >=1.2.3,<2.0.0
        if v.startswith("^"):
            ver = v[1:]
            parts = ver.split(".")
            major = int(parts[0])
            return SpecifierSet(f">={ver},<{major + 1}.0.0")

        # Tilde: ~1.2.3 means >=1.2.3,<1.3.0
        if v.startswith("~"):
            ver = v[1:]
            parts = ver.split(".")
            major, minor = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0
            return SpecifierSet(f">={ver},<{major}.{minor + 1}.0")

        # Standard specifiers (>=, <=, >, <, ==, !=)
        if re.match(r"^[><=!]", v):
            return SpecifierSet(v)

        # Plain version means exact match
        return SpecifierSet(f"=={v}")

    def matches(self, version: str) -> bool:
        """Check if a version satisfies this dependency."""
        try:
            spec = self.to_specifier()
            return Version(version) in spec
        except Exception:
            return False


class SkillConflict(BaseModel):
    """Declaration that this skill conflicts with another."""

    name: str
    version: str | None = None  # If None, conflicts with all versions
    reason: str | None = None


class ResolvedDependency(BaseModel):
    """A dependency that has been resolved to a specific version and path."""

    name: str
    requested_version: str
    resolved_version: str
    path: str
    is_optional: bool = False


class DependencyGraph(BaseModel):
    """Result of dependency resolution."""

    root: str  # Name of the skill being resolved
    resolved: dict[str, ResolvedDependency] = Field(default_factory=dict)
    resolution_order: list[str] = Field(default_factory=list)  # Topological order
    conflicts: list[str] = Field(default_factory=list)
    missing: list[str] = Field(default_factory=list)
    circular: list[str] = Field(default_factory=list)

    @property
    def is_complete(self) -> bool:
        """Check if all dependencies were resolved without issues."""
        return not self.conflicts and not self.missing and not self.circular

    def get_install_order(self) -> list[str]:
        """Get skills in the order they should be installed (dependencies first)."""
        return self.resolution_order


class DependencyResolutionError(Exception):
    """Error during dependency resolution."""

    def __init__(
        self,
        message: str,
        missing: list[str] | None = None,
        conflicts: list[str] | None = None,
        circular: list[str] | None = None,
    ):
        super().__init__(message)
        self.missing = missing or []
        self.conflicts = conflicts or []
        self.circular = circular or []

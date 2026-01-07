"""Core skill models."""

from __future__ import annotations

import hashlib
import time
import uuid
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field, computed_field

from .dependency import SkillConflict, SkillDependency
from .variable import SkillVariable


class SkillStability(str, Enum):
    """Stability level of a skill."""

    EXPERIMENTAL = "experimental"
    BETA = "beta"
    STABLE = "stable"
    DEPRECATED = "deprecated"


class SkillAuthor(BaseModel):
    """Author information for a skill."""

    name: str
    email: str | None = None
    url: str | None = None


class SkillTrigger(BaseModel):
    """Automatic trigger conditions for a skill."""

    pattern: str | None = None  # Regex pattern to match in user prompt
    file_pattern: str | None = None  # Glob pattern for file paths
    condition: str | None = None  # Additional condition (e.g., "error|exception")


class SkillRequirements(BaseModel):
    """Runtime requirements for a skill."""

    tools: list[str] = Field(default_factory=list)  # External tools needed
    packages: list[str] = Field(default_factory=list)  # Python/npm packages
    min_python_version: str | None = None


class SkillMetadata(BaseModel):
    """Additional metadata for a skill."""

    created_at: str | None = None
    updated_at: str | None = None
    stability: SkillStability = SkillStability.STABLE
    min_aiskills_version: str | None = None


class SkillManifest(BaseModel):
    """YAML frontmatter parsed from SKILL.md.

    This contains all the structured metadata about a skill.
    """

    # Required fields
    name: str
    description: str

    # Versioning
    version: str = "1.0.0"
    authors: list[SkillAuthor] = Field(default_factory=list)
    license: str | None = None

    # Taxonomy and discovery
    tags: list[str] = Field(default_factory=list)
    category: str | None = None

    # Dependencies
    dependencies: list[SkillDependency] = Field(default_factory=list)
    conflicts: list[SkillConflict] = Field(default_factory=list)

    # Composition
    extends: str | None = None  # Name of skill to extend
    includes: list[str] = Field(default_factory=list)  # Skills to include

    # Variables (templates)
    variables: dict[str, SkillVariable] = Field(default_factory=dict)

    # Context for semantic search and triggers
    context: str | None = None  # Additional context for semantic search
    triggers: list[SkillTrigger] = Field(default_factory=list)

    # Simple trigger phrases for easier semantic matching
    # These are phrases that should strongly match this skill
    trigger_phrases: list[str] = Field(
        default_factory=list,
        description="Phrases that should strongly match this skill (e.g., 'memory leak', 'debug python')",
    )

    # Requirements
    requirements: SkillRequirements | None = None

    # Metadata
    metadata: SkillMetadata = Field(default_factory=SkillMetadata)

    @computed_field
    @property
    def has_dependencies(self) -> bool:
        """Check if skill has any dependencies."""
        return len(self.dependencies) > 0

    @computed_field
    @property
    def has_composition(self) -> bool:
        """Check if skill uses extends or includes."""
        return self.extends is not None or len(self.includes) > 0

    @computed_field
    @property
    def has_variables(self) -> bool:
        """Check if skill defines any variables."""
        return len(self.variables) > 0


class Skill(BaseModel):
    """Complete skill representation.

    Contains both the manifest (metadata) and the content (markdown body).
    """

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    manifest: SkillManifest
    content: str  # Markdown content after frontmatter
    raw_content: str  # Full SKILL.md content including frontmatter

    # Location info
    path: str  # Full path to skill directory
    source: Literal["project", "global", "cache"] = "project"
    location_type: Literal[".aiskills", ".claude", ".agent"] = ".aiskills"

    # Computed on load
    content_hash: str = ""
    loaded_at: float = Field(default_factory=time.time)

    # After rendering (with variables resolved)
    rendered_content: str | None = None

    def model_post_init(self, _context: object) -> None:
        """Compute content hash after initialization."""
        if not self.content_hash:
            self.content_hash = self._compute_hash()

    def _compute_hash(self) -> str:
        """Compute SHA-256 hash of raw content."""
        return hashlib.sha256(self.raw_content.encode()).hexdigest()[:16]

    @computed_field
    @property
    def name(self) -> str:
        """Convenience accessor for skill name."""
        return self.manifest.name

    @computed_field
    @property
    def version(self) -> str:
        """Convenience accessor for skill version."""
        return self.manifest.version

    @computed_field
    @property
    def description(self) -> str:
        """Convenience accessor for skill description."""
        return self.manifest.description

    def to_index(self) -> SkillIndex:
        """Convert to lightweight index representation."""
        return SkillIndex(
            id=self.id,
            name=self.manifest.name,
            description=self.manifest.description,
            version=self.manifest.version,
            tags=self.manifest.tags,
            category=self.manifest.category,
            source=self.source,
            path=self.path,
            content_hash=self.content_hash,
        )


class SkillIndex(BaseModel):
    """Lightweight representation for search and listing.

    Used in registries and search results to avoid loading full skill content.
    """

    id: str
    name: str
    description: str
    version: str
    tags: list[str] = Field(default_factory=list)
    category: str | None = None
    source: str  # "project", "global", "cache"
    path: str
    content_hash: str
    embedding_id: str | None = None  # ID in vector store

    @computed_field
    @property
    def display_name(self) -> str:
        """Name with version for display."""
        return f"{self.name}@{self.version}"

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


class SkillScope(BaseModel):
    """Scoping rules for when a skill applies.

    Enables declarative matching beyond semantic search,
    reducing false positives by constraining skill eligibility.
    """

    paths: list[str] = Field(
        default_factory=list,
        description="Glob patterns for file paths where skill applies (e.g., ['src/api/**', 'infra/**'])",
    )
    languages: list[str] = Field(
        default_factory=list,
        description="Programming languages/filetypes (e.g., ['python', 'typescript'])",
    )
    triggers: list[str] = Field(
        default_factory=list,
        description="Hard trigger keywords that strongly match this skill (e.g., ['migrate', 'alembic'])",
    )


class SkillSecurity(BaseModel):
    """Security policy for skill resources.

    Controls what resources a skill can access and execute.
    """

    allowed_resources: list[str] = Field(
        default_factory=lambda: ["references", "templates"],
        description="Resource types this skill can access (references, templates, scripts, assets)",
    )
    allow_execution: bool = Field(
        default=False,
        description="Whether scripts in this skill can be executed",
    )
    sandbox_level: Literal["strict", "standard", "permissive"] = Field(
        default="standard",
        description="Sandbox strictness level",
    )
    allowlist: list[str] = Field(
        default_factory=list,
        description="Specific commands/scripts allowed to execute",
    )


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


class SkillPrecedence(str, Enum):
    """Precedence tier for skill priority resolution."""

    ORGANIZATION = "organization"  # Highest: org-level skills
    REPOSITORY = "repository"  # Repo/team-level skills
    PROJECT = "project"  # Project-specific skills
    USER = "user"  # User-level defaults
    LOCAL = "local"  # Lowest: local overrides


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

    # AgentSkills spec: allowed tools (e.g., "Read Edit Bash")
    allowed_tools: list[str] = Field(
        default_factory=list,
        description="Tools this skill is allowed to use (e.g., ['Read', 'Edit', 'Bash'])",
    )

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

    # Scoping - declarative matching beyond semantic search (NEW)
    scope: SkillScope = Field(
        default_factory=SkillScope,
        description="Scoping rules for when this skill applies",
    )

    # Priority for precedence resolution (NEW)
    priority: int = Field(
        default=50,
        ge=0,
        le=100,
        description="Priority score (0-100). Higher = more preferred. Default 50.",
    )
    precedence: SkillPrecedence = Field(
        default=SkillPrecedence.PROJECT,
        description="Precedence tier for override resolution",
    )

    # Security policy (NEW)
    security: SkillSecurity = Field(
        default_factory=SkillSecurity,
        description="Security policy for this skill's resources",
    )

    # Requirements
    requirements: SkillRequirements | None = None

    # Metadata
    metadata: SkillMetadata = Field(default_factory=SkillMetadata)

    # Token estimation for progressive disclosure (NEW)
    tokens_est: int | None = Field(
        default=None,
        description="Estimated token count for content (auto-calculated if not set)",
    )

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

    @computed_field
    @property
    def has_scope(self) -> bool:
        """Check if skill has any scoping rules defined."""
        return bool(
            self.scope.paths or self.scope.languages or self.scope.triggers
        )


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
            # Progressive disclosure fields
            tokens_est=self.manifest.tokens_est or self.estimate_tokens(),
            priority=self.manifest.priority,
            precedence=self.manifest.precedence.value,
            # Scope fields
            scope_paths=self.manifest.scope.paths,
            scope_languages=self.manifest.scope.languages,
            scope_triggers=self.manifest.scope.triggers,
            # AgentSkills spec fields
            license=self.manifest.license,
            allowed_tools=self.manifest.allowed_tools,
        )

    def to_browse_info(self) -> "SkillBrowseInfo":
        """Convert to browse-phase metadata (Phase 1 of progressive disclosure)."""
        return SkillBrowseInfo.from_skill(self)

    def estimate_tokens(self) -> int:
        """Estimate token count for the skill content.

        Uses a simple heuristic: ~4 characters per token.
        This is a rough estimate for English text.
        """
        content_length = len(self.content)
        # Add some overhead for frontmatter
        overhead = 100
        return (content_length // 4) + overhead

    def list_resources(self) -> list["SkillResourceInfo"]:
        """List available resources for this skill (Phase 3).

        Scans the skill directory for references, templates,
        scripts, and assets subdirectories.
        """
        from pathlib import Path

        resources: list[SkillResourceInfo] = []
        skill_path = Path(self.path)

        resource_dirs = {
            "references": "reference",
            "templates": "template",
            "scripts": "script",
            "assets": "asset",
        }

        for dir_name, resource_type in resource_dirs.items():
            resource_dir = skill_path / dir_name
            if resource_dir.exists() and resource_dir.is_dir():
                for file_path in resource_dir.iterdir():
                    if file_path.is_file():
                        # Check if allowed by security policy
                        allowed = dir_name in self.manifest.security.allowed_resources
                        requires_exec = resource_type == "script"

                        if requires_exec and not self.manifest.security.allow_execution:
                            allowed = False

                        resources.append(
                            SkillResourceInfo(
                                resource_type=resource_type,
                                path=str(file_path),
                                name=file_path.name,
                                size_bytes=file_path.stat().st_size,
                                tokens_est=file_path.stat().st_size // 4,
                                requires_execution=requires_exec,
                                allowed=allowed,
                            )
                        )

        return resources


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

    # Progressive disclosure metadata (NEW)
    tokens_est: int | None = None
    priority: int = 50
    precedence: str = "project"

    # Scope summary for filtering (NEW)
    scope_paths: list[str] = Field(default_factory=list)
    scope_languages: list[str] = Field(default_factory=list)
    scope_triggers: list[str] = Field(default_factory=list)

    # AgentSkills spec fields
    license: str | None = None
    allowed_tools: list[str] = Field(default_factory=list)

    @computed_field
    @property
    def display_name(self) -> str:
        """Name with version for display."""
        return f"{self.name}@{self.version}"


class SkillBrowseInfo(BaseModel):
    """Minimal metadata for browse phase (Progressive Disclosure Phase 1).

    Contains only what's needed to decide IF to load a skill,
    without loading the full content. This is the "browse" contract.
    """

    name: str
    description: str
    version: str
    tags: list[str] = Field(default_factory=list)
    category: str | None = None
    tokens_est: int | None = None  # Estimated token cost
    priority: int = 50
    precedence: str = "project"

    # Scope for filtering eligibility
    scope_paths: list[str] = Field(default_factory=list)
    scope_languages: list[str] = Field(default_factory=list)
    scope_triggers: list[str] = Field(default_factory=list)

    # Source info
    source: str = "project"
    has_variables: bool = False
    has_dependencies: bool = False

    # AgentSkills spec fields
    license: str | None = None
    allowed_tools: list[str] = Field(default_factory=list)

    @classmethod
    def from_skill(cls, skill: "Skill") -> "SkillBrowseInfo":
        """Create browse info from a full skill."""
        return cls(
            name=skill.manifest.name,
            description=skill.manifest.description,
            version=skill.manifest.version,
            tags=skill.manifest.tags,
            category=skill.manifest.category,
            tokens_est=skill.manifest.tokens_est or skill.estimate_tokens(),
            priority=skill.manifest.priority,
            precedence=skill.manifest.precedence.value,
            scope_paths=skill.manifest.scope.paths,
            scope_languages=skill.manifest.scope.languages,
            scope_triggers=skill.manifest.scope.triggers,
            source=skill.source,
            has_variables=skill.manifest.has_variables,
            has_dependencies=skill.manifest.has_dependencies,
            # AgentSkills spec fields
            license=skill.manifest.license,
            allowed_tools=skill.manifest.allowed_tools,
        )


class SkillResourceInfo(BaseModel):
    """Resource information for use phase (Progressive Disclosure Phase 3).

    Describes extra resources (scripts, templates, assets) that can be
    loaded on-demand after the main skill content.
    """

    resource_type: Literal["reference", "template", "script", "asset"]
    path: str
    name: str
    size_bytes: int = 0
    tokens_est: int | None = None
    description: str | None = None

    # Security - what's needed to use this resource
    requires_execution: bool = False
    allowed: bool = True  # Based on skill's security policy

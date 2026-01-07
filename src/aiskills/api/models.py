"""API request/response models."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────────
# Request Models
# ─────────────────────────────────────────────────────────────────


class SearchRequest(BaseModel):
    """Request for skill search."""

    query: str = Field(description="Search query")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum results")
    tags: list[str] | None = Field(default=None, description="Filter by tags")
    category: str | None = Field(default=None, description="Filter by category")
    text_only: bool = Field(default=False, description="Use text search only")
    min_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Minimum similarity score")


class ReadRequest(BaseModel):
    """Request for reading a skill."""

    name: str = Field(description="Skill name")
    variables: dict[str, Any] | None = Field(default=None, description="Template variables")
    raw: bool = Field(default=False, description="Return raw content without rendering")


class SuggestRequest(BaseModel):
    """Request for skill suggestions."""

    context: str = Field(description="Current context or task description")
    limit: int = Field(default=3, ge=1, le=10, description="Maximum suggestions")


class UseRequest(BaseModel):
    """Request for using a skill via natural language."""

    context: str = Field(
        description=(
            "Natural language description of what you need. "
            "Example: 'debug python memory leak', 'write unit tests'"
        )
    )
    variables: dict[str, Any] | None = Field(
        default=None, description="Optional variables to customize the skill"
    )
    # Scoping context for better matching
    active_paths: list[str] | None = Field(
        default=None, description="File paths currently being worked on"
    )
    languages: list[str] | None = Field(
        default=None, description="Programming languages in current context"
    )


class BrowseRequest(BaseModel):
    """Request for browsing skills (Progressive Disclosure Phase 1)."""

    context: str | None = Field(
        default=None, description="Optional query for semantic filtering"
    )
    active_paths: list[str] | None = Field(
        default=None, description="File paths for scope matching"
    )
    languages: list[str] | None = Field(
        default=None, description="Languages in current context"
    )
    limit: int = Field(default=20, ge=1, le=100, description="Maximum results")
    min_score: float = Field(default=0.1, ge=0.0, le=1.0, description="Minimum score")


class ResourceRequest(BaseModel):
    """Request for loading a skill resource (Progressive Disclosure Phase 3)."""

    skill_name: str = Field(description="Name of the skill")
    resource_name: str = Field(description="Name of the resource file to load")


# ─────────────────────────────────────────────────────────────────
# Response Models
# ─────────────────────────────────────────────────────────────────


class SkillInfo(BaseModel):
    """Basic skill information."""

    name: str
    version: str
    description: str
    tags: list[str] = []
    category: str | None = None
    source: str = ""


class SkillBrowseInfo(BaseModel):
    """Lightweight skill metadata for browse phase (Progressive Disclosure Phase 1).

    Contains only what's needed to decide IF to load a skill.
    """

    name: str
    description: str
    version: str
    tags: list[str] = []
    category: str | None = None
    tokens_est: int | None = None
    priority: int = 50
    precedence: str = "project"
    scope_paths: list[str] = []
    scope_languages: list[str] = []
    scope_triggers: list[str] = []
    source: str = "project"
    has_variables: bool = False
    has_dependencies: bool = False


class SkillResourceInfo(BaseModel):
    """Resource information for Phase 3 of progressive disclosure."""

    resource_type: str  # "reference", "template", "script", "asset"
    path: str
    name: str
    size_bytes: int = 0
    tokens_est: int | None = None
    requires_execution: bool = False
    allowed: bool = True


class SearchResult(BaseModel):
    """A single search result."""

    skill: SkillInfo
    score: float | None = None  # None for text search


class SearchResponse(BaseModel):
    """Response for skill search."""

    query: str
    type: str  # "semantic" or "text"
    results: list[SearchResult]
    total: int


class ReadResponse(BaseModel):
    """Response for reading a skill."""

    name: str
    content: str
    metadata: SkillInfo


class ListResponse(BaseModel):
    """Response for listing skills."""

    skills: list[SkillInfo]
    total: int
    project_count: int
    global_count: int


class SuggestResponse(BaseModel):
    """Response for skill suggestions."""

    context: str
    suggestions: list[SearchResult]


class UseResponse(BaseModel):
    """Response for using a skill (Phase 2: Load)."""

    skill_name: str
    content: str
    score: float | None = None
    matched_query: str
    # Progressive disclosure Phase 3 info
    available_resources: list[str] = []
    tokens_used: int | None = None


class BrowseResponse(BaseModel):
    """Response for browsing skills (Progressive Disclosure Phase 1)."""

    skills: list[SkillBrowseInfo]
    total: int
    query: str | None = None


class ResourceResponse(BaseModel):
    """Response for loading a resource (Progressive Disclosure Phase 3)."""

    skill_name: str
    resource_name: str
    content: str
    resource_type: str
    tokens_est: int | None = None


class ResourceListResponse(BaseModel):
    """Response for listing available resources."""

    skill_name: str
    resources: list[SkillResourceInfo]
    total: int


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    detail: str | None = None
    suggestion: str | None = None


# ─────────────────────────────────────────────────────────────────
# OpenAI Compatible Models
# ─────────────────────────────────────────────────────────────────


class OpenAIFunctionParameter(BaseModel):
    """OpenAI function parameter schema."""

    type: str
    description: str | None = None
    enum: list[str] | None = None
    default: Any | None = None


class OpenAIFunctionParameters(BaseModel):
    """OpenAI function parameters schema."""

    type: str = "object"
    properties: dict[str, OpenAIFunctionParameter]
    required: list[str] = []


class OpenAIFunction(BaseModel):
    """OpenAI function definition."""

    name: str
    description: str
    parameters: OpenAIFunctionParameters


class OpenAITool(BaseModel):
    """OpenAI tool definition."""

    type: str = "function"
    function: OpenAIFunction


class OpenAIToolsResponse(BaseModel):
    """Response with OpenAI-compatible tool definitions."""

    tools: list[OpenAITool]


class OpenAIFunctionCall(BaseModel):
    """OpenAI function call request."""

    name: str
    arguments: dict[str, Any]


class OpenAIFunctionResponse(BaseModel):
    """OpenAI function call response."""

    name: str
    content: str  # JSON string of result


# ─────────────────────────────────────────────────────────────────
# Auto-Discovery Models
# ─────────────────────────────────────────────────────────────────


class ShouldInvokeRequest(BaseModel):
    """Request for skill auto-discovery."""

    user_message: str = Field(description="The user's message or query")
    active_paths: list[str] | None = Field(
        default=None, description="File paths being worked on"
    )
    languages: list[str] | None = Field(
        default=None, description="Programming languages in context"
    )
    recent_context: str | None = Field(
        default=None, description="Recent conversation context"
    )


class ShouldInvokeResponse(BaseModel):
    """Response for skill auto-discovery."""

    should_invoke: bool = Field(description="Whether a skill should be invoked")
    suggested_skill: str | None = Field(
        default=None, description="Name of the suggested skill"
    )
    confidence: float = Field(
        default=0.0, ge=0.0, le=1.0, description="Confidence score (0-1)"
    )
    reason: str | None = Field(
        default=None, description="Explanation for the suggestion"
    )
    matched_triggers: list[str] = Field(
        default_factory=list, description="Keywords that triggered the suggestion"
    )
    alternatives: list[str] = Field(
        default_factory=list, description="Alternative skills that could help"
    )

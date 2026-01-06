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
    """Response for using a skill."""

    skill_name: str
    content: str
    score: float | None = None
    matched_query: str


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

"""MCP tool definitions for aiskills."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class SkillSearchInput(BaseModel):
    """Input for skill_search tool."""

    query: str = Field(description="Search query for finding skills")
    limit: int = Field(default=5, description="Maximum number of results", ge=1, le=20)
    tags: list[str] | None = Field(
        default=None, description="Filter by tags (returns skills matching any tag)"
    )
    category: str | None = Field(default=None, description="Filter by category")
    text_only: bool = Field(
        default=False,
        description="Use text search instead of semantic search (faster, no ML)",
    )
    hybrid: bool = Field(
        default=False,
        description="Use hybrid search combining semantic + BM25 for best accuracy",
    )


class SkillReadInput(BaseModel):
    """Input for skill_read tool."""

    name: str = Field(description="Name of the skill to read")
    variables: dict[str, Any] | None = Field(
        default=None, description="Variables to render in the skill template"
    )
    raw: bool = Field(
        default=False,
        description="Return raw content without rendering templates",
    )


class SkillListInput(BaseModel):
    """Input for skill_list tool."""

    global_only: bool = Field(
        default=False, description="Only list globally installed skills"
    )
    category: str | None = Field(default=None, description="Filter by category")


class SkillSuggestInput(BaseModel):
    """Input for skill_suggest tool."""

    context: str = Field(
        description="Current context or task description to suggest relevant skills"
    )
    limit: int = Field(default=3, description="Maximum suggestions", ge=1, le=10)


class UseSkillInput(BaseModel):
    """Input for use_skill tool - the primary skill invocation interface."""

    context: str = Field(
        description=(
            "Natural language description of what you need help with. "
            "Examples: 'debug python memory leak', 'write unit tests', 'optimize SQL query'"
        )
    )
    variables: dict[str, Any] | None = Field(
        default=None,
        description="Optional variables to customize the skill output",
    )


class SkillCategoriesInput(BaseModel):
    """Input for skill_categories tool."""

    include_skills: bool = Field(
        default=True,
        description="Include list of skills in each category",
    )


class SkillVarsInput(BaseModel):
    """Input for skill_vars tool."""

    name: str = Field(description="Name of the skill to get variables for")


# Tool schemas for MCP
# NOTE: Descriptions are intentionally specific to avoid unnecessary tool calls.
# Claude should only use these tools when the user explicitly needs architectural
# guidance, best practices, or design patterns - NOT for simple code questions.
TOOL_DEFINITIONS = [
    {
        "name": "use_skill",
        "description": (
            "Get expert guidance from AI Skills knowledge base. "
            "ONLY use when the user explicitly asks for: best practices, design patterns, "
            "architectural guidance, or debugging strategies. "
            "DO NOT use for: simple code questions, syntax help, or quick fixes. "
            "Examples of when to use: 'what are best practices for API design', "
            "'how should I structure authentication', 'guide me on database optimization'."
        ),
        "inputSchema": UseSkillInput.model_json_schema(),
    },
    {
        "name": "skill_search",
        "description": (
            "Search the AI Skills knowledge base. Only use when the user explicitly "
            "asks to search or find skills, or asks 'what skills are available for X'. "
            "Do not use proactively."
        ),
        "inputSchema": SkillSearchInput.model_json_schema(),
    },
    {
        "name": "skill_read",
        "description": (
            "Read a specific skill by name. Only use when the user explicitly asks "
            "to 'show skill X' or 'read skill X'. Requires knowing the skill name first."
        ),
        "inputSchema": SkillReadInput.model_json_schema(),
    },
    {
        "name": "skill_list",
        "description": (
            "List all installed AI skills. Only use when the user explicitly asks "
            "'what skills are available', 'list skills', or 'show all skills'."
        ),
        "inputSchema": SkillListInput.model_json_schema(),
    },
    {
        "name": "skill_suggest",
        "description": (
            "Suggest relevant skills for a task. Only use when the user explicitly "
            "asks for skill suggestions or recommendations."
        ),
        "inputSchema": SkillSuggestInput.model_json_schema(),
    },
    {
        "name": "skill_categories",
        "description": (
            "List skill categories. Only use when the user asks about skill categories "
            "or wants to browse skills by domain."
        ),
        "inputSchema": SkillCategoriesInput.model_json_schema(),
    },
    {
        "name": "skill_vars",
        "description": (
            "Get variables for a specific skill. Only use when the user asks about "
            "customization options for a specific skill."
        ),
        "inputSchema": SkillVarsInput.model_json_schema(),
    },
]


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
TOOL_DEFINITIONS = [
    {
        "name": "use_skill",
        "description": (
            "Find and use the best matching AI skill for your current task. "
            "Describe what you need in natural language and this tool will find "
            "the most relevant skill and return its content. This is the primary "
            "way to leverage AI skills - just describe your problem."
        ),
        "inputSchema": UseSkillInput.model_json_schema(),
    },
    {
        "name": "skill_search",
        "description": (
            "Search for AI skills by semantic similarity or text matching. "
            "Use this to find relevant skills for a given task or topic. "
            "Semantic search understands meaning, while text search matches exact keywords."
        ),
        "inputSchema": SkillSearchInput.model_json_schema(),
    },
    {
        "name": "skill_read",
        "description": (
            "Read the content of a skill by name. Returns the skill's markdown content "
            "with optional template variables rendered. Use this after finding a skill "
            "with skill_search to get its full content."
        ),
        "inputSchema": SkillReadInput.model_json_schema(),
    },
    {
        "name": "skill_list",
        "description": (
            "List all installed skills. Returns skill names, versions, and descriptions. "
            "Use this to see what skills are available in the system."
        ),
        "inputSchema": SkillListInput.model_json_schema(),
    },
    {
        "name": "skill_suggest",
        "description": (
            "Suggest relevant skills based on the current context or task. "
            "Provide a description of what you're working on, and this tool will "
            "return the most relevant skills that might help."
        ),
        "inputSchema": SkillSuggestInput.model_json_schema(),
    },
    {
        "name": "skill_categories",
        "description": (
            "List all skill categories with their skills. Use this to explore "
            "available skills organized by domain (e.g., development/debugging, "
            "devops/automation). Helps discover what skills are available."
        ),
        "inputSchema": SkillCategoriesInput.model_json_schema(),
    },
    {
        "name": "skill_vars",
        "description": (
            "Get the available variables for a skill. Returns variable names, types, "
            "allowed values, and descriptions. Use this before calling skill_read "
            "to understand what customization options are available."
        ),
        "inputSchema": SkillVarsInput.model_json_schema(),
    },
]


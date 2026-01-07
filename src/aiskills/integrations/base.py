"""Base interface for LLM provider integrations.

This module defines the abstract interface that all LLM integrations implement,
ensuring consistent behavior across providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass
class ToolDefinition:
    """Universal tool definition that can be converted to any provider format."""

    name: str
    description: str
    parameters: dict[str, Any]
    required: list[str] = field(default_factory=list)
    handler: Callable[..., Any] | None = None


@dataclass
class SkillInvocationResult:
    """Result from invoking a skill through any provider."""

    skill_name: str | None
    content: str | None
    score: float | None = None
    tokens_used: int | None = None
    error: str | None = None
    raw_response: dict[str, Any] | None = None

    @property
    def success(self) -> bool:
        """Whether the invocation was successful."""
        return self.error is None and self.content is not None


@dataclass
class SearchResult:
    """Result from searching skills."""

    results: list[dict[str, Any]]
    total: int
    query: str
    search_type: str = "hybrid"


class BaseLLMIntegration(ABC):
    """Abstract base class for LLM provider integrations.

    All provider-specific integrations (OpenAI, Gemini, Ollama) inherit from
    this class to ensure consistent behavior and API surface.

    Example:
        >>> class MyProvider(BaseLLMIntegration):
        ...     def get_tools(self): ...
        ...     def execute_tool(self, name, args): ...
    """

    def __init__(self):
        from ..core.router import get_router

        self._router = get_router()

    @property
    def router(self):
        """Access to the skill router."""
        return self._router

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider identifier (e.g., 'openai', 'gemini', 'ollama')."""
        ...

    @abstractmethod
    def get_tools(self) -> list[dict[str, Any]]:
        """Return tool definitions in the provider's native format.

        Returns:
            List of tool definitions compatible with the provider's API.
        """
        ...

    @abstractmethod
    def execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool call and return the result.

        Args:
            name: Name of the tool to execute
            arguments: Arguments for the tool

        Returns:
            Tool execution result (format depends on provider)
        """
        ...

    def use_skill(
        self,
        context: str,
        variables: dict[str, Any] | None = None,
        active_paths: list[str] | None = None,
        languages: list[str] | None = None,
    ) -> SkillInvocationResult:
        """Use a skill via natural language query.

        Args:
            context: Natural language description of what's needed
            variables: Optional template variables
            active_paths: File paths for scope matching
            languages: Programming languages for scope matching

        Returns:
            SkillInvocationResult with the skill content
        """
        try:
            result = self._router.use(
                context=context,
                variables=variables or {},
                active_paths=active_paths,
                languages=languages,
            )
            return SkillInvocationResult(
                skill_name=result.skill_name,
                content=result.content,
                score=result.score,
                tokens_used=result.tokens_used,
                raw_response={
                    "matched_query": result.matched_query,
                    "available_resources": result.available_resources,
                },
            )
        except Exception as e:
            return SkillInvocationResult(
                skill_name=None,
                content=None,
                error=str(e),
            )

    def search_skills(
        self,
        query: str,
        limit: int = 10,
        text_only: bool = False,
    ) -> SearchResult:
        """Search for skills.

        Args:
            query: Search query
            limit: Maximum results
            text_only: Use text search only (faster, no embeddings)

        Returns:
            SearchResult with matching skills
        """
        if text_only:
            results = self._router.registry.search_text(query, limit=limit)
            return SearchResult(
                results=[
                    {
                        "name": r.name,
                        "description": r.description,
                        "tags": r.tags,
                        "category": r.category,
                    }
                    for r in results
                ],
                total=len(results),
                query=query,
                search_type="text",
            )
        else:
            try:
                results = self._router.registry.search(query, limit=limit)
                return SearchResult(
                    results=[
                        {
                            "name": r.name,
                            "description": r.description,
                            "tags": r.tags,
                            "category": r.category,
                            "score": score,
                        }
                        for r, score in results
                    ],
                    total=len(results),
                    query=query,
                    search_type="semantic",
                )
            except Exception:
                # Fallback to text search
                return self.search_skills(query, limit, text_only=True)

    def read_skill(
        self,
        name: str,
        variables: dict[str, Any] | None = None,
    ) -> SkillInvocationResult:
        """Read a specific skill by name.

        Args:
            name: Exact skill name
            variables: Optional template variables

        Returns:
            SkillInvocationResult with the skill content
        """
        try:
            result = self._router.use_by_name(name, variables=variables)
            return SkillInvocationResult(
                skill_name=result.skill_name,
                content=result.content,
                score=1.0,
            )
        except Exception as e:
            return SkillInvocationResult(
                skill_name=name,
                content=None,
                error=str(e),
            )

    def list_skills(self) -> list[dict[str, Any]]:
        """List all available skills.

        Returns:
            List of skill metadata dictionaries
        """
        skills = self._router.manager.list_installed()
        return [
            {
                "name": s.manifest.name,
                "version": s.manifest.version,
                "description": s.manifest.description,
                "tags": s.manifest.tags,
                "category": s.manifest.category,
                "source": s.source,
            }
            for s in skills
        ]

    def browse_skills(
        self,
        context: str | None = None,
        active_paths: list[str] | None = None,
        languages: list[str] | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Browse skills with lightweight metadata (Phase 1 of Progressive Disclosure).

        Args:
            context: Optional query for filtering
            active_paths: File paths for scope matching
            languages: Programming languages for scope matching
            limit: Maximum results

        Returns:
            List of skill browse info (metadata only, no content)
        """
        results = self._router.browse(
            context=context,
            active_paths=active_paths,
            languages=languages,
            limit=limit,
        )
        return [
            {
                "name": r.name,
                "description": r.description,
                "version": r.version,
                "tags": r.tags,
                "category": r.category,
                "tokens_est": r.tokens_est,
                "priority": r.priority,
                "has_variables": r.has_variables,
            }
            for r in results
        ]


# Standard tool definitions used by all providers
STANDARD_TOOLS: list[ToolDefinition] = [
    ToolDefinition(
        name="use_skill",
        description=(
            "Find and use the best matching AI skill for your current task. "
            "Describe what you need in natural language and this tool will find "
            "the most relevant skill and return its content."
        ),
        parameters={
            "context": {
                "type": "string",
                "description": (
                    "Natural language description of what you need. "
                    "Examples: 'debug python memory leak', 'write unit tests'"
                ),
            },
            "variables": {
                "type": "object",
                "description": "Optional variables to customize the skill output",
            },
        },
        required=["context"],
    ),
    ToolDefinition(
        name="skill_search",
        description=(
            "Search for AI skills by semantic similarity or text matching. "
            "Use this to find relevant skills for a given task or topic."
        ),
        parameters={
            "query": {
                "type": "string",
                "description": "Search query for finding skills",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results (default: 10)",
                "default": 10,
            },
            "text_only": {
                "type": "boolean",
                "description": "Use text search only (faster, no ML)",
                "default": False,
            },
        },
        required=["query"],
    ),
    ToolDefinition(
        name="skill_read",
        description=(
            "Read the full content of a skill by its exact name. "
            "Use this after finding a skill with skill_search."
        ),
        parameters={
            "name": {
                "type": "string",
                "description": "Name of the skill to read",
            },
            "variables": {
                "type": "object",
                "description": "Variables to render in the skill template",
            },
        },
        required=["name"],
    ),
    ToolDefinition(
        name="skill_list",
        description="List all available skills with their metadata.",
        parameters={
            "category": {
                "type": "string",
                "description": "Filter by category (optional)",
            },
        },
        required=[],
    ),
    ToolDefinition(
        name="skill_browse",
        description=(
            "Browse skills with lightweight metadata (no full content). "
            "Use this to discover skills before loading them fully. "
            "Supports context-aware filtering by file paths and languages."
        ),
        parameters={
            "context": {
                "type": "string",
                "description": "Optional query for semantic filtering",
            },
            "active_paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "File paths being worked on (for scope matching)",
            },
            "languages": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Programming languages in current context",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum results (default: 20)",
                "default": 20,
            },
        },
        required=[],
    ),
]

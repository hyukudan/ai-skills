"""Skill router - intelligent skill discovery and retrieval."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field


class UseResult(BaseModel):
    """Result from using a skill."""

    skill_name: str
    content: str
    score: float | None = None
    matched_query: str = ""
    variables_applied: dict[str, Any] = Field(default_factory=dict)


class SkillRouter:
    """Intelligent skill router using semantic search.

    Provides a single `use()` method that finds the best matching skill
    for a given context and returns its rendered content.

    This is the primary interface for all integrations (MCP, REST, CLI).
    """

    def __init__(self):
        self._manager = None
        self._registry = None

    @property
    def manager(self):
        """Lazy load manager to avoid circular imports."""
        if self._manager is None:
            from .manager import get_manager

            self._manager = get_manager()
        return self._manager

    @property
    def registry(self):
        """Lazy load registry to avoid circular imports."""
        if self._registry is None:
            from .registry import get_registry

            self._registry = get_registry()
        return self._registry

    def use(
        self,
        context: str,
        variables: dict[str, Any] | None = None,
        limit: int = 1,
        min_score: float = 0.2,
    ) -> UseResult | list[UseResult]:
        """Find and return the best matching skill(s) for a context.

        This is the main entry point for natural skill invocation.
        It performs semantic search to find relevant skills and returns
        the rendered content.

        Args:
            context: Natural language description of what's needed
                     (e.g., "debug python memory leak", "write unit tests")
            variables: Optional variables to render in the skill template
            limit: Number of skills to return (default 1 for single best match)
            min_score: Minimum similarity score threshold

        Returns:
            Single UseResult if limit=1, otherwise list of UseResult

        Example:
            >>> router = SkillRouter()
            >>> result = router.use("help me debug python")
            >>> print(result.content)  # Rendered skill content
        """
        variables = variables or {}

        # Try semantic search first
        try:
            results = self.registry.search(
                query=context,
                limit=limit,
                min_score=min_score,
            )
        except Exception as e:
            # Fallback to text search if semantic fails
            if "not installed" in str(e).lower():
                results = [
                    (idx, None)
                    for idx in self.registry.search_text(context, limit=limit)
                ]
            else:
                raise

        if not results:
            # Return empty result if no matches
            return UseResult(
                skill_name="",
                content="No matching skill found for the given context.",
                score=0.0,
                matched_query=context,
            )

        use_results: list[UseResult] = []

        for skill_idx, score in results:
            try:
                # Read and render the skill
                content = self.manager.read(
                    name=skill_idx.name,
                    variables=variables,
                )

                use_results.append(
                    UseResult(
                        skill_name=skill_idx.name,
                        content=content,
                        score=round(score, 3) if score is not None else None,
                        matched_query=context,
                        variables_applied=variables,
                    )
                )
            except Exception:
                # Skip skills that fail to load
                continue

        if not use_results:
            return UseResult(
                skill_name="",
                content="Failed to load matching skills.",
                score=0.0,
                matched_query=context,
            )

        # Return single result or list based on limit
        if limit == 1:
            return use_results[0]
        return use_results

    def use_by_name(
        self,
        name: str,
        variables: dict[str, Any] | None = None,
    ) -> UseResult:
        """Use a skill by exact name (for direct invocation).

        Args:
            name: Exact skill name
            variables: Optional variables to render

        Returns:
            UseResult with rendered content
        """
        variables = variables or {}

        try:
            content = self.manager.read(name=name, variables=variables)
            skill = self.manager.get(name)

            return UseResult(
                skill_name=name,
                content=content,
                score=1.0,  # Exact match
                matched_query=name,
                variables_applied=variables,
            )
        except Exception as e:
            return UseResult(
                skill_name=name,
                content=f"Error loading skill '{name}': {e}",
                score=0.0,
                matched_query=name,
            )


# Singleton instance
_router: SkillRouter | None = None


def get_router() -> SkillRouter:
    """Get the singleton router instance."""
    global _router
    if _router is None:
        _router = SkillRouter()
    return _router

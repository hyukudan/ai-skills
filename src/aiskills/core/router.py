"""Skill router - intelligent skill discovery and retrieval.

Implements a 3-phase progressive disclosure system:
1. Browse: List skills with metadata only (SkillBrowseInfo)
2. Load: Get full skill content (UseResult)
3. Use: Load additional resources on-demand (SkillResourceInfo)

Also integrates declarative scoping for more accurate matching.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel, Field

from .scoping import ScopeContext, ScopeMatcher, get_scope_matcher


class SkillCandidate(BaseModel):
    """A candidate skill when multiple skills match similarly."""

    name: str
    description: str
    score: float
    category: str | None = None
    tags: list[str] = Field(default_factory=list)


class UseResult(BaseModel):
    """Result from using a skill (Phase 2: Load)."""

    skill_name: str
    content: str
    score: float | None = None
    matched_query: str = ""
    variables_applied: dict[str, Any] = Field(default_factory=dict)
    # Progressive disclosure Phase 3 info
    available_resources: list[str] = Field(default_factory=list)
    tokens_used: int | None = None
    # Ambiguous match info
    ambiguous: bool = False
    candidates: list[SkillCandidate] = Field(default_factory=list)


class SkillRouter:
    """Intelligent skill router using semantic search and declarative scoping.

    Implements Progressive Disclosure in 3 phases:
    1. browse() - Returns lightweight metadata only (SkillBrowseInfo)
    2. use() - Loads full content for selected skill
    3. resource() - Loads additional resources on-demand

    Also integrates scoping rules for more accurate skill matching.

    This is the primary interface for all integrations (MCP, REST, CLI).
    """

    def __init__(self):
        self._manager = None
        self._registry = None
        self._scope_matcher = None

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

    @property
    def scope_matcher(self) -> ScopeMatcher:
        """Lazy load scope matcher."""
        if self._scope_matcher is None:
            self._scope_matcher = get_scope_matcher()
        return self._scope_matcher

    def browse(
        self,
        context: str | None = None,
        active_paths: list[str] | None = None,
        languages: list[str] | None = None,
        limit: int = 20,
        min_score: float = 0.1,
    ) -> list["SkillBrowseInfo"]:
        """Phase 1: Browse available skills with metadata only.

        Returns lightweight SkillBrowseInfo without loading full content.
        Use this to discover skills and decide which to load.

        Args:
            context: Optional query for semantic filtering
            active_paths: File paths being worked on (for scope matching)
            languages: Languages in current context
            limit: Maximum number of results
            min_score: Minimum semantic score (if context provided)

        Returns:
            List of SkillBrowseInfo sorted by relevance/priority
        """
        from ..models.skill import SkillBrowseInfo

        # Create scope context for filtering
        scope_ctx = ScopeContext(
            active_paths=active_paths or [],
            languages=languages or [],
            query=context or "",
        )

        # Get all skills from registry
        all_skills = self.registry.list_all()

        # If context provided, do semantic search first
        semantic_scores: dict[str, float] = {}
        if context:
            try:
                results = self.registry.search(
                    query=context,
                    limit=limit * 2,  # Get more for filtering
                    min_score=min_score,
                )
                semantic_scores = {idx.name: score for idx, score in results}
                # Filter to only semantically relevant skills
                all_skills = [s for s in all_skills if s.name in semantic_scores]
            except Exception:
                # Fall back to all skills if semantic search fails
                pass

        # Apply scope filtering
        scope_filtered = self.scope_matcher.filter_by_scope(all_skills, scope_ctx)

        # Sort by priority (combines priority, precedence, scope bonus, semantic)
        sorted_skills = self.scope_matcher.sort_by_priority(
            scope_filtered, semantic_scores
        )

        # Convert to browse info
        browse_results: list[SkillBrowseInfo] = []
        for skill_idx, combined_score in sorted_skills[:limit]:
            skill = self.manager.get(skill_idx.name)
            if skill:
                browse_results.append(skill.to_browse_info())

        return browse_results

    def use(
        self,
        context: str,
        variables: dict[str, Any] | None = None,
        limit: int = 1,
        min_score: float = 0.2,
        active_paths: list[str] | None = None,
        languages: list[str] | None = None,
        ambiguity_threshold: float = 0.1,
        auto_select: bool = False,
    ) -> UseResult | list[UseResult]:
        """Phase 2: Load and return skill content.

        Finds the best matching skill(s) using semantic search + scoping,
        then loads and renders the full content.

        Args:
            context: Natural language description of what's needed
                     (e.g., "debug python memory leak", "write unit tests")
            variables: Optional variables to render in the skill template
            limit: Number of skills to return (default 1 for single best match)
            min_score: Minimum similarity score threshold
            active_paths: File paths being worked on (for scope matching)
            languages: Languages in current context
            ambiguity_threshold: Score difference threshold to consider matches
                                 ambiguous (default 0.1). Set to 0 to disable.
            auto_select: If True, always select best match even if ambiguous.
                        If False (default), return candidates when ambiguous.

        Returns:
            Single UseResult if limit=1, otherwise list of UseResult.
            If ambiguous=True in result, content is empty and candidates
            contains the similar skills to choose from.

        Example:
            >>> router = SkillRouter()
            >>> result = router.use("help me debug python")
            >>> if result.ambiguous:
            ...     print("Multiple matches:", result.candidates)
            ... else:
            ...     print(result.content)  # Rendered skill content
        """
        variables = variables or {}

        # Create scope context
        scope_ctx = ScopeContext(
            active_paths=active_paths or [],
            languages=languages or [],
            query=context,
        )

        # Try semantic search first
        semantic_scores: dict[str, float] = {}
        try:
            results = self.registry.search(
                query=context,
                limit=limit * 3,  # Get extra for scope filtering
                min_score=min_score,
            )
            semantic_scores = {idx.name: score for idx, score in results}
            skill_indices = [idx for idx, _ in results]
        except Exception as e:
            # Fallback to text search if semantic fails
            if "not installed" in str(e).lower():
                skill_indices = self.registry.search_text(context, limit=limit * 3)
            else:
                raise

        if not skill_indices:
            return UseResult(
                skill_name="",
                content="No matching skill found for the given context.",
                score=0.0,
                matched_query=context,
            )

        # Apply scope filtering
        scope_filtered = self.scope_matcher.filter_by_scope(skill_indices, scope_ctx)

        # If scope filtering removed everything, fall back to unfiltered
        if not scope_filtered and skill_indices:
            # Create dummy match results for unfiltered skills
            from .scoping import ScopeMatchResult
            scope_filtered = [
                (idx, ScopeMatchResult(matches=True, reason="No scope filter"))
                for idx in skill_indices
            ]

        # Sort by combined priority
        sorted_skills = self.scope_matcher.sort_by_priority(
            scope_filtered, semantic_scores
        )

        # Check for ambiguous matches (multiple skills with similar combined scores)
        # Note: we use combined scores for ambiguity detection (internal ranking),
        # but return semantic scores to the user (interpretable similarity)
        if (
            limit == 1
            and not auto_select
            and ambiguity_threshold > 0
            and len(sorted_skills) >= 2
        ):
            top_combined = sorted_skills[0][1]
            # Find all skills within threshold of top combined score
            similar_skills = [
                (idx, combined)
                for idx, combined in sorted_skills
                if top_combined - combined <= ambiguity_threshold
            ]

            if len(similar_skills) >= 2:
                # Return ambiguous result with candidates (using semantic scores)
                candidates = []
                for skill_idx, _combined in similar_skills[:5]:  # Max 5 candidates
                    skill = self.manager.get(skill_idx.name)
                    if skill:
                        semantic = semantic_scores.get(skill_idx.name, 0.0)
                        candidates.append(
                            SkillCandidate(
                                name=skill_idx.name,
                                description=skill.manifest.description[:200],
                                score=round(semantic, 3),
                                category=skill.manifest.category,
                                tags=skill.manifest.tags[:5],
                            )
                        )

                if len(candidates) >= 2:
                    top_semantic = semantic_scores.get(sorted_skills[0][0].name, 0.0)
                    return UseResult(
                        skill_name="",
                        content="",
                        score=round(top_semantic, 3),
                        matched_query=context,
                        ambiguous=True,
                        candidates=candidates,
                    )

        use_results: list[UseResult] = []

        for skill_idx, _combined_score in sorted_skills[:limit]:
            try:
                skill = self.manager.get(skill_idx.name)
                if not skill:
                    continue

                # Read and render the skill (no header, skill_name is in result)
                content = self.manager.read(
                    name=skill_idx.name,
                    variables=variables,
                    include_header=False,
                )

                # Get available resources for Phase 3
                resources = skill.list_resources()
                resource_names = [r.name for r in resources if r.allowed]

                # Return semantic score (not combined) - combined is only for internal sorting
                raw_semantic_score = semantic_scores.get(skill_idx.name, 0.0)

                use_results.append(
                    UseResult(
                        skill_name=skill_idx.name,
                        content=content,
                        score=round(raw_semantic_score, 3),
                        matched_query=context,
                        variables_applied=variables,
                        available_resources=resource_names,
                        tokens_used=skill.estimate_tokens(),
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

    def resource(
        self,
        skill_name: str,
        resource_name: str,
    ) -> str | None:
        """Phase 3: Load additional resource from a skill.

        After using a skill, load extra resources (templates, references,
        scripts, assets) on-demand.

        Args:
            skill_name: Name of the skill
            resource_name: Name of the resource file to load

        Returns:
            Resource content as string, or None if not found/not allowed
        """
        skill = self.manager.get(skill_name)
        if not skill:
            return None

        resources = skill.list_resources()
        for resource in resources:
            if resource.name == resource_name:
                if not resource.allowed:
                    return None
                # Read the resource file
                from pathlib import Path
                try:
                    return Path(resource.path).read_text()
                except Exception:
                    return None

        return None

    def list_resources(self, skill_name: str) -> list["SkillResourceInfo"]:
        """List available resources for a skill (Phase 3 preparation).

        Args:
            skill_name: Name of the skill

        Returns:
            List of SkillResourceInfo for available resources
        """
        from ..models.skill import SkillResourceInfo

        skill = self.manager.get(skill_name)
        if not skill:
            return []

        return skill.list_resources()

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

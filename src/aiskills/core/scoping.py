"""Skill scoping - declarative matching beyond semantic search.

This module implements the scoping system that constrains skill eligibility
based on:
- File paths (glob patterns)
- Languages/filetypes
- Hard trigger keywords
- Priority and precedence levels

This reduces false positives from purely semantic matching by providing
explicit constraints on when a skill should compete for selection.
"""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..models.skill import Skill, SkillIndex, SkillBrowseInfo, SkillScope


@dataclass
class ScopeContext:
    """Context for scope matching.

    Provides information about the current environment
    to match against skill scopes.
    """

    # Current working files/paths being touched
    active_paths: list[str] = None  # type: ignore
    # Detected languages in current context
    languages: list[str] = None  # type: ignore
    # User query/prompt text (for trigger matching)
    query: str = ""
    # Current working directory
    cwd: str = ""

    def __post_init__(self):
        if self.active_paths is None:
            self.active_paths = []
        if self.languages is None:
            self.languages = []


@dataclass
class ScopeMatchResult:
    """Result of scope matching."""

    matches: bool  # Overall match
    path_match: bool = False
    language_match: bool = False
    trigger_match: bool = False
    # Bonus score for strong matches
    bonus_score: float = 0.0
    # Reason for match/no-match
    reason: str = ""


class ScopeMatcher:
    """Matches skills against scope constraints.

    Used by the router to filter skills before/after semantic search.
    """

    # Language extensions mapping
    LANGUAGE_EXTENSIONS: dict[str, list[str]] = {
        "python": [".py", ".pyw", ".pyi"],
        "javascript": [".js", ".mjs", ".cjs"],
        "typescript": [".ts", ".mts", ".cts", ".tsx"],
        "rust": [".rs"],
        "go": [".go"],
        "java": [".java"],
        "kotlin": [".kt", ".kts"],
        "swift": [".swift"],
        "c": [".c", ".h"],
        "cpp": [".cpp", ".cc", ".cxx", ".hpp", ".hh"],
        "csharp": [".cs"],
        "ruby": [".rb"],
        "php": [".php"],
        "scala": [".scala"],
        "haskell": [".hs"],
        "elixir": [".ex", ".exs"],
        "clojure": [".clj", ".cljs", ".cljc"],
        "sql": [".sql"],
        "shell": [".sh", ".bash", ".zsh"],
        "yaml": [".yaml", ".yml"],
        "json": [".json"],
        "toml": [".toml"],
        "markdown": [".md", ".markdown"],
        "html": [".html", ".htm"],
        "css": [".css", ".scss", ".sass", ".less"],
    }

    def match_scope(
        self,
        scope: "SkillScope",
        context: ScopeContext,
    ) -> ScopeMatchResult:
        """Check if a skill's scope matches the current context.

        Args:
            scope: Skill's scope definition
            context: Current context to match against

        Returns:
            ScopeMatchResult with match details
        """
        # If scope has no constraints, it matches everything
        if not scope.paths and not scope.languages and not scope.triggers:
            return ScopeMatchResult(
                matches=True,
                reason="No scope constraints (universal match)",
            )

        path_match = self._match_paths(scope.paths, context.active_paths)
        lang_match = self._match_languages(scope.languages, context)
        trigger_match = self._match_triggers(scope.triggers, context.query)

        # Calculate if overall matches
        # Logic: If a constraint is defined, it must match
        constraints_defined = []
        if scope.paths:
            constraints_defined.append(("path", path_match))
        if scope.languages:
            constraints_defined.append(("language", lang_match))
        if scope.triggers:
            constraints_defined.append(("trigger", trigger_match))

        if not constraints_defined:
            matches = True
            reason = "No constraints"
        else:
            # All defined constraints must match
            matches = all(m for _, m in constraints_defined)
            if matches:
                reason = f"Matched: {', '.join(n for n, _ in constraints_defined)}"
            else:
                failed = [n for n, m in constraints_defined if not m]
                reason = f"Failed: {', '.join(failed)}"

        # Calculate bonus score for trigger matches (strong signal)
        bonus = 0.0
        if trigger_match:
            bonus += 0.3  # Significant boost for trigger match
        if path_match:
            bonus += 0.1
        if lang_match:
            bonus += 0.1

        return ScopeMatchResult(
            matches=matches,
            path_match=path_match,
            language_match=lang_match,
            trigger_match=trigger_match,
            bonus_score=bonus,
            reason=reason,
        )

    def _match_paths(self, patterns: list[str], active_paths: list[str]) -> bool:
        """Check if any active path matches any pattern."""
        if not patterns or not active_paths:
            return not patterns  # True if no patterns defined

        for path in active_paths:
            for pattern in patterns:
                if fnmatch.fnmatch(path, pattern):
                    return True
                # Also try matching against just the relative part
                if "/" in path:
                    rel_path = path.split("/", 1)[-1]
                    if fnmatch.fnmatch(rel_path, pattern):
                        return True
        return False

    def _match_languages(
        self,
        languages: list[str],
        context: ScopeContext,
    ) -> bool:
        """Check if context languages match skill's language constraints."""
        if not languages:
            return True  # No constraint

        # Direct match with context languages
        lang_set = set(lang.lower() for lang in languages)
        context_langs = set(lang.lower() for lang in context.languages)

        if lang_set & context_langs:
            return True

        # Infer from file extensions in active_paths
        for path in context.active_paths:
            ext = Path(path).suffix.lower()
            for lang, extensions in self.LANGUAGE_EXTENSIONS.items():
                if ext in extensions and lang in lang_set:
                    return True

        return False

    def _match_triggers(self, triggers: list[str], query: str) -> bool:
        """Check if query contains any trigger keywords."""
        if not triggers or not query:
            return not triggers  # True if no triggers defined

        query_lower = query.lower()

        for trigger in triggers:
            trigger_lower = trigger.lower()
            # Word boundary match to avoid partial matches
            pattern = r"\b" + re.escape(trigger_lower) + r"\b"
            if re.search(pattern, query_lower):
                return True

        return False

    def filter_by_scope(
        self,
        skills: list["SkillIndex"],
        context: ScopeContext,
    ) -> list[tuple["SkillIndex", ScopeMatchResult]]:
        """Filter skills by scope matching.

        Args:
            skills: List of skill indices to filter
            context: Current context

        Returns:
            List of (skill, match_result) tuples for matching skills
        """
        results: list[tuple[SkillIndex, ScopeMatchResult]] = []

        for skill in skills:
            # Create scope from skill index fields
            from ..models.skill import SkillScope

            scope = SkillScope(
                paths=skill.scope_paths,
                languages=skill.scope_languages,
                triggers=skill.scope_triggers,
            )

            match_result = self.match_scope(scope, context)
            if match_result.matches:
                results.append((skill, match_result))

        return results

    def sort_by_priority(
        self,
        skills: list[tuple["SkillIndex", ScopeMatchResult]],
        semantic_scores: dict[str, float] | None = None,
    ) -> list[tuple["SkillIndex", float]]:
        """Sort skills by combined priority, precedence, and semantic score.

        Combines:
        - Skill priority (0-100)
        - Precedence tier
        - Scope match bonus
        - Semantic search score (if available)

        Args:
            skills: List of (skill, match_result) tuples
            semantic_scores: Optional dict of skill_name -> semantic score

        Returns:
            Sorted list of (skill, combined_score) tuples
        """
        semantic_scores = semantic_scores or {}

        # Precedence weights (higher = more priority)
        precedence_weights = {
            "organization": 100,
            "repository": 80,
            "project": 60,
            "user": 40,
            "local": 20,
        }

        scored: list[tuple[SkillIndex, float]] = []

        for skill, match_result in skills:
            # Base score from priority (0-100 -> 0-1)
            priority_score = skill.priority / 100

            # Precedence contribution (0-1)
            precedence_score = precedence_weights.get(skill.precedence, 60) / 100

            # Scope match bonus (0-0.5)
            scope_bonus = match_result.bonus_score

            # Semantic score (0-1)
            semantic = semantic_scores.get(skill.name, 0.5)

            # Combined score with weights
            combined = (
                priority_score * 0.25
                + precedence_score * 0.15
                + scope_bonus * 0.20
                + semantic * 0.40
            )

            scored.append((skill, combined))

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored


# Singleton instance
_matcher: ScopeMatcher | None = None


def get_scope_matcher() -> ScopeMatcher:
    """Get the singleton scope matcher instance."""
    global _matcher
    if _matcher is None:
        _matcher = ScopeMatcher()
    return _matcher


def detect_languages_from_paths(paths: list[str]) -> list[str]:
    """Detect languages from file paths.

    Args:
        paths: List of file paths

    Returns:
        List of detected language names
    """
    languages: set[str] = set()
    matcher = get_scope_matcher()

    for path in paths:
        ext = Path(path).suffix.lower()
        for lang, extensions in matcher.LANGUAGE_EXTENSIONS.items():
            if ext in extensions:
                languages.add(lang)

    return list(languages)

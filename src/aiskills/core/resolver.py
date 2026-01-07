"""Skill resolver - handles dependencies and composition."""

from __future__ import annotations

from typing import TYPE_CHECKING

from ..models.dependency import (
    DependencyGraph,
    DependencyResolutionError,
    ResolvedDependency,
    SkillDependency,
)
from ..models.skill import Skill

if TYPE_CHECKING:
    from .manager import SkillManager


class SkillResolver:
    """Resolves skill dependencies and composition.

    Handles:
    - Dependency resolution with version constraints
    - Cycle detection
    - Conflict detection
    - Composition (extends/includes)
    """

    def __init__(self, manager: SkillManager):
        self.manager = manager

    def resolve_dependencies(self, skill: Skill) -> DependencyGraph:
        """Build dependency graph for a skill.

        Args:
            skill: Skill to resolve dependencies for

        Returns:
            DependencyGraph with resolution results
        """
        graph = DependencyGraph(root=skill.manifest.name)
        visited: set[str] = set()
        path: list[str] = []  # Current resolution path for cycle detection

        self._resolve_recursive(skill, graph, visited, path)

        # Build topological order
        graph.resolution_order = self._topological_sort(graph)

        return graph

    def _resolve_recursive(
        self,
        skill: Skill,
        graph: DependencyGraph,
        visited: set[str],
        path: list[str],
    ) -> None:
        """Recursively resolve dependencies."""
        name = skill.manifest.name

        # Cycle detection
        if name in path:
            cycle = " -> ".join(path + [name])
            graph.circular.append(cycle)
            return

        if name in visited:
            return

        visited.add(name)
        path.append(name)

        for dep in skill.manifest.dependencies:
            resolved = self._resolve_single(dep, graph)

            if resolved:
                # Load the dependency skill and recurse
                dep_skill = self.manager.get(dep.name)
                if dep_skill:
                    self._resolve_recursive(dep_skill, graph, visited, path)

        path.pop()

    def _resolve_single(
        self,
        dep: SkillDependency,
        graph: DependencyGraph,
    ) -> ResolvedDependency | None:
        """Resolve a single dependency."""
        # Check if already resolved
        if dep.name in graph.resolved:
            existing = graph.resolved[dep.name]
            # Check version compatibility
            if not dep.matches(existing.resolved_version):
                graph.conflicts.append(
                    f"{dep.name}: {dep.version} conflicts with {existing.resolved_version}"
                )
            return existing

        # Try to find the skill
        skill = self.manager.get(dep.name)

        if skill is None:
            if not dep.optional:
                graph.missing.append(f"{dep.name}@{dep.version}")
            return None

        # Check version constraint
        if not dep.matches(skill.manifest.version):
            graph.conflicts.append(
                f"{dep.name}: installed {skill.manifest.version} doesn't match {dep.version}"
            )
            return None

        resolved = ResolvedDependency(
            name=dep.name,
            requested_version=dep.version,
            resolved_version=skill.manifest.version,
            path=skill.path,
            is_optional=dep.optional,
        )

        graph.resolved[dep.name] = resolved
        return resolved

    def _topological_sort(self, graph: DependencyGraph) -> list[str]:
        """Sort resolved dependencies in topological order."""
        # Simple implementation - dependencies before dependents
        order: list[str] = []
        visited: set[str] = set()

        def visit(name: str) -> None:
            if name in visited:
                return
            visited.add(name)

            skill = self.manager.get(name)
            if skill:
                for dep in skill.manifest.dependencies:
                    if dep.name in graph.resolved:
                        visit(dep.name)

            order.append(name)

        for name in graph.resolved:
            visit(name)

        return order

    def check_conflicts(self, skills: list[Skill]) -> list[str]:
        """Check for conflicts between a set of skills.

        Args:
            skills: Skills to check

        Returns:
            List of conflict descriptions
        """
        conflicts: list[str] = []
        skill_map = {s.manifest.name: s for s in skills}

        for skill in skills:
            for conflict in skill.manifest.conflicts:
                if conflict.name in skill_map:
                    target = skill_map[conflict.name]
                    # Check version if specified
                    if conflict.version is None or self._version_matches(
                        target.manifest.version, conflict.version
                    ):
                        reason = conflict.reason or "declared conflict"
                        conflicts.append(
                            f"{skill.manifest.name} conflicts with {conflict.name}: {reason}"
                        )

        return conflicts

    def _version_matches(self, version: str, constraint: str) -> bool:
        """Check if version matches constraint."""
        dep = SkillDependency(name="check", version=constraint)
        return dep.matches(version)

    # Maximum include depth to prevent infinite loops
    MAX_INCLUDE_DEPTH = 5

    def resolve_composition(
        self,
        skill: Skill,
        depth: int = 0,
        visited: set[str] | None = None,
    ) -> str:
        """Resolve extends/includes into final content.

        Supports both frontmatter includes and @include directives.
        Includes depth limit to prevent infinite recursion.

        Args:
            skill: Skill with potential composition
            depth: Current recursion depth
            visited: Set of already-visited skill names (cycle detection)

        Returns:
            Resolved content with includes expanded
        """
        visited = visited or set()

        # Cycle detection
        if skill.manifest.name in visited:
            return f"<!-- ERROR: Circular include detected for {skill.manifest.name} -->\n"

        visited.add(skill.manifest.name)

        # Depth limit
        if depth >= self.MAX_INCLUDE_DEPTH:
            return f"<!-- WARNING: Max include depth ({self.MAX_INCLUDE_DEPTH}) reached -->\n{skill.content}"

        content = skill.content

        # Handle extends (inheritance)
        if skill.manifest.extends:
            base_skill = self.manager.get(skill.manifest.extends)
            if base_skill:
                # Recursively resolve base skill
                base_content = self.resolve_composition(
                    base_skill, depth + 1, visited.copy()
                )
                content = self._merge_with_base(base_content, skill)

        # Handle frontmatter includes
        for include_name in skill.manifest.includes:
            included_skill = self.manager.get(include_name)
            if included_skill:
                # Recursively resolve included skill
                included_content = self.resolve_composition(
                    included_skill, depth + 1, visited.copy()
                )
                content = self._expand_include(content, included_skill, included_content)

        # Handle @include directives in content
        content = self._expand_include_directives(content, depth, visited)

        return content

    def _merge_with_base(self, base_content: str, child: Skill) -> str:
        """Merge child skill with base skill content.

        Child content is appended after base content with a separator.
        """
        return f"{base_content}\n\n---\n\n## Extended by {child.manifest.name}\n\n{child.content}"

    def _expand_include(
        self,
        content: str,
        included: Skill,
        included_content: str,
    ) -> str:
        """Expand include markers in content.

        Looks for {{> skill:name }} or {{> include:name }} patterns.
        """
        import re

        # Pattern: {{> skill:name }} or {{> include:name }}
        pattern = rf"\{{\{{\s*>\s*(?:skill|include):{re.escape(included.manifest.name)}\s*\}}\}}"

        # Replace with included content
        replacement = f"\n<!-- Included from {included.manifest.name} -->\n{included_content}\n<!-- End include -->\n"

        return re.sub(pattern, replacement, content)

    def _expand_include_directives(
        self,
        content: str,
        depth: int,
        visited: set[str],
    ) -> str:
        """Expand @include directives in content.

        Supports:
        - @include skill:name
        - @include path/to/snippet.md

        Args:
            content: Content with potential @include directives
            depth: Current recursion depth
            visited: Set of visited skills for cycle detection

        Returns:
            Content with @include directives expanded
        """
        import re
        from pathlib import Path

        if depth >= self.MAX_INCLUDE_DEPTH:
            return content

        # Pattern: @include skill:name or @include path/to/file.md
        include_pattern = re.compile(
            r"@include\s+(?:skill:)?([^\s\n]+)",
            re.MULTILINE,
        )

        def replace_include(match: re.Match) -> str:
            include_ref = match.group(1).strip()

            # Check if it's a skill reference
            if not include_ref.endswith(".md"):
                # It's a skill name
                included_skill = self.manager.get(include_ref)
                if included_skill:
                    if include_ref in visited:
                        return f"<!-- ERROR: Circular include: {include_ref} -->"
                    included_content = self.resolve_composition(
                        included_skill, depth + 1, visited.copy()
                    )
                    return f"\n<!-- @include {include_ref} -->\n{included_content}\n<!-- End @include -->\n"
                else:
                    return f"<!-- WARNING: Skill not found: {include_ref} -->"
            else:
                # It's a file path - resolve relative to current skill
                # For security, only allow .md files
                if not include_ref.endswith(".md"):
                    return f"<!-- ERROR: Only .md files can be included: {include_ref} -->"

                # Try to find the file in common locations
                possible_paths = [
                    Path(include_ref),
                    Path(".aiskills/snippets") / include_ref,
                    Path(".claude/snippets") / include_ref,
                ]

                for path in possible_paths:
                    if path.exists() and path.is_file():
                        try:
                            snippet_content = path.read_text()
                            # Recursively expand any includes in the snippet
                            snippet_content = self._expand_include_directives(
                                snippet_content, depth + 1, visited
                            )
                            return f"\n<!-- @include {include_ref} -->\n{snippet_content}\n<!-- End @include -->\n"
                        except Exception as e:
                            return f"<!-- ERROR reading {include_ref}: {e} -->"

                return f"<!-- WARNING: File not found: {include_ref} -->"

        return include_pattern.sub(replace_include, content)


def get_resolver(manager: SkillManager) -> SkillResolver:
    """Create a resolver for a manager."""
    return SkillResolver(manager)

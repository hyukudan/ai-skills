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

    def resolve_composition(self, skill: Skill) -> str:
        """Resolve extends/includes into final content.

        Args:
            skill: Skill with potential composition

        Returns:
            Resolved content with includes expanded
        """
        content = skill.content

        # Handle extends (inheritance)
        if skill.manifest.extends:
            base_skill = self.manager.get(skill.manifest.extends)
            if base_skill:
                content = self._merge_with_base(base_skill, skill)

        # Handle includes (composition)
        for include_name in skill.manifest.includes:
            included_skill = self.manager.get(include_name)
            if included_skill:
                content = self._expand_include(content, included_skill)

        return content

    def _merge_with_base(self, base: Skill, child: Skill) -> str:
        """Merge child skill with base skill.

        Child content is appended after base content with a separator.
        """
        return f"{base.content}\n\n---\n\n## Extended by {child.manifest.name}\n\n{child.content}"

    def _expand_include(self, content: str, included: Skill) -> str:
        """Expand include markers in content.

        Looks for {{> skill:name }} or {{> include:name }} patterns.
        """
        import re

        # Pattern: {{> skill:name }} or {{> include:name }}
        pattern = rf"\{{\{{\s*>\s*(?:skill|include):{re.escape(included.manifest.name)}\s*\}}\}}"

        # Replace with included content
        replacement = f"\n<!-- Included from {included.manifest.name} -->\n{included.content}\n<!-- End include -->\n"

        return re.sub(pattern, replacement, content)


def get_resolver(manager: SkillManager) -> SkillResolver:
    """Create a resolver for a manager."""
    return SkillResolver(manager)

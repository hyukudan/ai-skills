"""Tests for dependency models and version constraints."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from aiskills.models.dependency import (
    DependencyGraph,
    DependencyResolutionError,
    ResolvedDependency,
    SkillConflict,
    SkillDependency,
    VersionOperator,
)


class TestVersionOperator:
    """Tests for VersionOperator enum."""

    def test_operator_values(self):
        assert VersionOperator.EXACT.value == "="
        assert VersionOperator.GTE.value == ">="
        assert VersionOperator.LTE.value == "<="
        assert VersionOperator.GT.value == ">"
        assert VersionOperator.LT.value == "<"
        assert VersionOperator.CARET.value == "^"
        assert VersionOperator.TILDE.value == "~"
        assert VersionOperator.ANY.value == "*"


class TestSkillDependency:
    """Tests for SkillDependency model."""

    def test_dependency_with_name_only(self):
        dep = SkillDependency(name="base-skill")
        assert dep.name == "base-skill"
        assert dep.version == "*"  # Default
        assert dep.optional is False

    def test_dependency_with_version(self):
        dep = SkillDependency(name="skill", version=">=1.0.0")
        assert dep.version == ">=1.0.0"

    def test_dependency_optional(self):
        dep = SkillDependency(name="skill", optional=True)
        assert dep.optional is True

    # Version constraint tests
    def test_any_version_matches_all(self):
        dep = SkillDependency(name="skill", version="*")
        assert dep.matches("0.1.0")
        assert dep.matches("1.0.0")
        assert dep.matches("99.99.99")

    def test_exact_version(self):
        dep = SkillDependency(name="skill", version="1.0.0")
        assert dep.matches("1.0.0")
        assert not dep.matches("1.0.1")
        assert not dep.matches("0.9.9")

    def test_gte_constraint(self):
        dep = SkillDependency(name="skill", version=">=1.0.0")
        assert dep.matches("1.0.0")
        assert dep.matches("1.0.1")
        assert dep.matches("2.0.0")
        assert not dep.matches("0.9.9")

    def test_gt_constraint(self):
        dep = SkillDependency(name="skill", version=">1.0.0")
        assert not dep.matches("1.0.0")
        assert dep.matches("1.0.1")
        assert dep.matches("2.0.0")

    def test_lte_constraint(self):
        dep = SkillDependency(name="skill", version="<=2.0.0")
        assert dep.matches("1.0.0")
        assert dep.matches("2.0.0")
        assert not dep.matches("2.0.1")

    def test_lt_constraint(self):
        dep = SkillDependency(name="skill", version="<2.0.0")
        assert dep.matches("1.9.9")
        assert not dep.matches("2.0.0")

    def test_caret_constraint(self):
        """Caret (^) allows changes that do not modify the major version."""
        dep = SkillDependency(name="skill", version="^1.2.3")
        # Should match: >=1.2.3,<2.0.0
        assert dep.matches("1.2.3")
        assert dep.matches("1.2.4")
        assert dep.matches("1.3.0")
        assert dep.matches("1.9.9")
        assert not dep.matches("1.2.2")  # Below min
        assert not dep.matches("2.0.0")  # Major changed

    def test_caret_constraint_major_zero(self):
        dep = SkillDependency(name="skill", version="^0.2.3")
        # Should match: >=0.2.3,<1.0.0
        assert dep.matches("0.2.3")
        assert dep.matches("0.9.9")
        assert not dep.matches("1.0.0")

    def test_tilde_constraint(self):
        """Tilde (~) allows patch-level changes."""
        dep = SkillDependency(name="skill", version="~1.2.3")
        # Should match: >=1.2.3,<1.3.0
        assert dep.matches("1.2.3")
        assert dep.matches("1.2.4")
        assert dep.matches("1.2.99")
        assert not dep.matches("1.3.0")  # Minor changed
        assert not dep.matches("1.2.2")  # Below min

    def test_tilde_constraint_no_patch(self):
        dep = SkillDependency(name="skill", version="~1.2")
        # Should match: >=1.2,<1.3.0
        assert dep.matches("1.2.0")
        assert dep.matches("1.2.5")
        assert not dep.matches("1.3.0")

    def test_complex_specifier(self):
        dep = SkillDependency(name="skill", version=">=1.0.0,<2.0.0")
        assert dep.matches("1.0.0")
        assert dep.matches("1.5.0")
        assert not dep.matches("2.0.0")
        assert not dep.matches("0.9.0")

    def test_invalid_version_constraint(self):
        with pytest.raises(ValidationError):
            SkillDependency(name="skill", version="invalid")

    def test_invalid_caret_version(self):
        with pytest.raises(ValidationError):
            SkillDependency(name="skill", version="^invalid")

    def test_matches_handles_invalid_version_gracefully(self):
        dep = SkillDependency(name="skill", version=">=1.0.0")
        # Invalid version string should return False, not raise
        assert not dep.matches("not-a-version")

    def test_to_specifier_caching(self):
        """Verify specifier conversion works multiple times."""
        dep = SkillDependency(name="skill", version="^1.0.0")
        spec1 = dep.to_specifier()
        spec2 = dep.to_specifier()
        # Both should work identically
        assert "1.5.0" in spec1
        assert "1.5.0" in spec2


class TestSkillConflict:
    """Tests for SkillConflict model."""

    def test_conflict_with_name_only(self):
        conflict = SkillConflict(name="conflicting-skill")
        assert conflict.name == "conflicting-skill"
        assert conflict.version is None  # Conflicts with all versions
        assert conflict.reason is None

    def test_conflict_with_version(self):
        conflict = SkillConflict(name="skill", version="<2.0.0")
        assert conflict.version == "<2.0.0"

    def test_conflict_with_reason(self):
        conflict = SkillConflict(
            name="old-skill",
            version="<1.0.0",
            reason="Deprecated API incompatibility",
        )
        assert conflict.reason == "Deprecated API incompatibility"


class TestResolvedDependency:
    """Tests for ResolvedDependency model."""

    def test_resolved_dependency_creation(self):
        resolved = ResolvedDependency(
            name="my-skill",
            requested_version=">=1.0.0",
            resolved_version="1.2.3",
            path="/path/to/skill",
        )
        assert resolved.name == "my-skill"
        assert resolved.requested_version == ">=1.0.0"
        assert resolved.resolved_version == "1.2.3"
        assert resolved.path == "/path/to/skill"
        assert resolved.is_optional is False

    def test_resolved_dependency_optional(self):
        resolved = ResolvedDependency(
            name="opt-skill",
            requested_version="*",
            resolved_version="2.0.0",
            path="/path",
            is_optional=True,
        )
        assert resolved.is_optional is True


class TestDependencyGraph:
    """Tests for DependencyGraph model."""

    def test_empty_graph(self):
        graph = DependencyGraph(root="my-skill")
        assert graph.root == "my-skill"
        assert graph.resolved == {}
        assert graph.resolution_order == []
        assert graph.conflicts == []
        assert graph.missing == []
        assert graph.circular == []

    def test_is_complete_true(self):
        graph = DependencyGraph(
            root="skill",
            resolved={"dep1": ResolvedDependency(
                name="dep1",
                requested_version="*",
                resolved_version="1.0.0",
                path="/path",
            )},
            resolution_order=["dep1"],
        )
        assert graph.is_complete is True

    def test_is_complete_false_with_conflicts(self):
        graph = DependencyGraph(
            root="skill",
            conflicts=["conflicting-skill"],
        )
        assert graph.is_complete is False

    def test_is_complete_false_with_missing(self):
        graph = DependencyGraph(
            root="skill",
            missing=["missing-skill"],
        )
        assert graph.is_complete is False

    def test_is_complete_false_with_circular(self):
        graph = DependencyGraph(
            root="skill",
            circular=["skill-a", "skill-b"],
        )
        assert graph.is_complete is False

    def test_get_install_order(self):
        graph = DependencyGraph(
            root="main",
            resolution_order=["base", "helper", "main"],
        )
        order = graph.get_install_order()
        assert order == ["base", "helper", "main"]
        assert order[0] == "base"  # Dependencies first


class TestDependencyResolutionError:
    """Tests for DependencyResolutionError exception."""

    def test_error_with_message(self):
        error = DependencyResolutionError("Resolution failed")
        assert str(error) == "Resolution failed"
        assert error.missing == []
        assert error.conflicts == []
        assert error.circular == []

    def test_error_with_missing(self):
        error = DependencyResolutionError(
            "Missing dependencies",
            missing=["skill-a", "skill-b"],
        )
        assert error.missing == ["skill-a", "skill-b"]

    def test_error_with_conflicts(self):
        error = DependencyResolutionError(
            "Conflicts detected",
            conflicts=["v1 vs v2"],
        )
        assert error.conflicts == ["v1 vs v2"]

    def test_error_with_circular(self):
        error = DependencyResolutionError(
            "Circular dependency",
            circular=["a -> b -> a"],
        )
        assert error.circular == ["a -> b -> a"]

    def test_error_with_all_details(self):
        error = DependencyResolutionError(
            "Complex failure",
            missing=["x"],
            conflicts=["y"],
            circular=["z"],
        )
        assert error.missing == ["x"]
        assert error.conflicts == ["y"]
        assert error.circular == ["z"]

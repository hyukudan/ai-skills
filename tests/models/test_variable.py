"""Tests for variable models."""

from __future__ import annotations

import pytest

from aiskills.models.variable import SkillVariable, VariableContext


class TestSkillVariable:
    """Tests for SkillVariable model."""

    # Type validation tests
    def test_string_variable(self):
        var = SkillVariable(type="string", default="hello")
        assert var.type == "string"
        assert var.default == "hello"

    def test_integer_variable(self):
        var = SkillVariable(type="integer", default=42)
        assert var.type == "integer"
        assert var.default == 42

    def test_float_variable(self):
        var = SkillVariable(type="float", default=3.14)
        assert var.type == "float"
        assert var.default == 3.14

    def test_boolean_variable(self):
        var = SkillVariable(type="boolean", default=True)
        assert var.type == "boolean"
        assert var.default is True

    def test_array_variable(self):
        var = SkillVariable(type="array", default=["a", "b"])
        assert var.type == "array"
        assert var.default == ["a", "b"]

    def test_object_variable(self):
        var = SkillVariable(type="object", default={"key": "value"})
        assert var.type == "object"
        assert var.default == {"key": "value"}

    # Validation tests
    def test_validate_string_valid(self):
        var = SkillVariable(type="string")
        is_valid, error = var.validate_value("test")
        assert is_valid is True
        assert error is None

    def test_validate_string_invalid(self):
        var = SkillVariable(type="string")
        is_valid, error = var.validate_value(123)
        assert is_valid is False
        assert "Expected string" in error

    def test_validate_integer_valid(self):
        var = SkillVariable(type="integer")
        is_valid, error = var.validate_value(42)
        assert is_valid is True

    def test_validate_integer_rejects_float(self):
        var = SkillVariable(type="integer")
        is_valid, error = var.validate_value(3.14)
        assert is_valid is False
        assert "Expected integer" in error

    def test_validate_integer_rejects_bool(self):
        var = SkillVariable(type="integer")
        is_valid, error = var.validate_value(True)
        assert is_valid is False

    def test_validate_float_accepts_int(self):
        var = SkillVariable(type="float")
        is_valid, _ = var.validate_value(42)
        assert is_valid is True

    def test_validate_float_valid(self):
        var = SkillVariable(type="float")
        is_valid, _ = var.validate_value(3.14)
        assert is_valid is True

    def test_validate_boolean_valid(self):
        var = SkillVariable(type="boolean")
        is_valid_true, _ = var.validate_value(True)
        is_valid_false, _ = var.validate_value(False)
        assert is_valid_true is True
        assert is_valid_false is True

    def test_validate_boolean_rejects_int(self):
        var = SkillVariable(type="boolean")
        is_valid, error = var.validate_value(1)
        assert is_valid is False

    def test_validate_array_valid(self):
        var = SkillVariable(type="array")
        is_valid, _ = var.validate_value([1, 2, 3])
        assert is_valid is True

    def test_validate_array_invalid(self):
        var = SkillVariable(type="array")
        is_valid, error = var.validate_value("not an array")
        assert is_valid is False

    def test_validate_object_valid(self):
        var = SkillVariable(type="object")
        is_valid, _ = var.validate_value({"key": "value"})
        assert is_valid is True

    def test_validate_object_invalid(self):
        var = SkillVariable(type="object")
        is_valid, error = var.validate_value([1, 2])
        assert is_valid is False

    # None/required tests
    def test_validate_none_not_required(self):
        var = SkillVariable(type="string", required=False)
        is_valid, _ = var.validate_value(None)
        assert is_valid is True

    def test_validate_none_required_with_default(self):
        var = SkillVariable(type="string", required=True, default="fallback")
        is_valid, _ = var.validate_value(None)
        assert is_valid is True

    def test_validate_none_required_no_default(self):
        var = SkillVariable(type="string", required=True)
        is_valid, error = var.validate_value(None)
        assert is_valid is False
        assert "Required variable" in error

    # Enum validation
    def test_validate_enum_valid(self):
        var = SkillVariable(type="string", enum=["python", "rust", "go"])
        is_valid, _ = var.validate_value("python")
        assert is_valid is True

    def test_validate_enum_invalid(self):
        var = SkillVariable(type="string", enum=["python", "rust", "go"])
        is_valid, error = var.validate_value("javascript")
        assert is_valid is False
        assert "must be one of" in error

    def test_validate_integer_enum(self):
        var = SkillVariable(type="integer", enum=[1, 2, 3])
        assert var.validate_value(2)[0] is True
        assert var.validate_value(5)[0] is False

    # Range validation
    def test_validate_integer_min(self):
        var = SkillVariable(type="integer", min=0)
        assert var.validate_value(0)[0] is True
        assert var.validate_value(10)[0] is True
        is_valid, error = var.validate_value(-1)
        assert is_valid is False
        assert ">= 0" in error

    def test_validate_integer_max(self):
        var = SkillVariable(type="integer", max=100)
        assert var.validate_value(100)[0] is True
        is_valid, error = var.validate_value(101)
        assert is_valid is False
        assert "<= 100" in error

    def test_validate_integer_range(self):
        var = SkillVariable(type="integer", min=1, max=10)
        assert var.validate_value(1)[0] is True
        assert var.validate_value(5)[0] is True
        assert var.validate_value(10)[0] is True
        assert var.validate_value(0)[0] is False
        assert var.validate_value(11)[0] is False

    def test_validate_float_range(self):
        var = SkillVariable(type="float", min=0.0, max=1.0)
        assert var.validate_value(0.5)[0] is True
        assert var.validate_value(1.5)[0] is False

    # Array length validation
    def test_validate_array_min_items(self):
        var = SkillVariable(type="array", min_items=2)
        assert var.validate_value([1, 2])[0] is True
        assert var.validate_value([1, 2, 3])[0] is True
        is_valid, error = var.validate_value([1])
        assert is_valid is False
        assert "at least 2" in error

    def test_validate_array_max_items(self):
        var = SkillVariable(type="array", max_items=3)
        assert var.validate_value([1, 2, 3])[0] is True
        is_valid, error = var.validate_value([1, 2, 3, 4])
        assert is_valid is False
        assert "at most 3" in error

    def test_validate_array_item_range(self):
        var = SkillVariable(type="array", min_items=1, max_items=5)
        assert var.validate_value([1])[0] is True
        assert var.validate_value([1, 2, 3, 4, 5])[0] is True
        assert var.validate_value([])[0] is False
        assert var.validate_value([1, 2, 3, 4, 5, 6])[0] is False

    # get_value tests
    def test_get_value_provided(self):
        var = SkillVariable(type="string", default="default")
        assert var.get_value("provided") == "provided"

    def test_get_value_default(self):
        var = SkillVariable(type="string", default="default")
        assert var.get_value(None) == "default"
        assert var.get_value() == "default"

    def test_get_value_no_default(self):
        var = SkillVariable(type="string")
        assert var.get_value(None) is None


class TestVariableContext:
    """Tests for VariableContext model."""

    def test_empty_context(self):
        ctx = VariableContext()
        assert ctx.variables == {}
        assert ctx.environment == {}
        assert ctx.project_info == {}

    def test_context_with_variables(self):
        ctx = VariableContext(variables={"lang": "python", "debug": True})
        assert ctx.variables["lang"] == "python"
        assert ctx.variables["debug"] is True

    # resolve tests
    def test_resolve_from_variables(self):
        ctx = VariableContext(variables={"name": "test"})
        assert ctx.resolve("name") == "test"

    def test_resolve_from_environment(self):
        ctx = VariableContext(environment={"AISKILLS_LANG": "rust"})
        assert ctx.resolve("lang") == "rust"

    def test_resolve_from_project_info(self):
        ctx = VariableContext(project_info={"project_name": "my-project"})
        assert ctx.resolve("project_name") == "my-project"

    def test_resolve_priority_variables_first(self):
        ctx = VariableContext(
            variables={"name": "from_variables"},
            environment={"AISKILLS_NAME": "from_env"},
            project_info={"name": "from_project"},
        )
        assert ctx.resolve("name") == "from_variables"

    def test_resolve_priority_env_second(self):
        ctx = VariableContext(
            environment={"AISKILLS_NAME": "from_env"},
            project_info={"name": "from_project"},
        )
        assert ctx.resolve("name") == "from_env"

    def test_resolve_priority_project_third(self):
        ctx = VariableContext(project_info={"name": "from_project"})
        assert ctx.resolve("name") == "from_project"

    def test_resolve_default_fallback(self):
        ctx = VariableContext()
        assert ctx.resolve("missing") is None
        assert ctx.resolve("missing", "default_value") == "default_value"

    # merge tests
    def test_merge_empty_contexts(self):
        ctx1 = VariableContext()
        ctx2 = VariableContext()
        merged = ctx1.merge(ctx2)
        assert merged.variables == {}
        assert merged.environment == {}
        assert merged.project_info == {}

    def test_merge_combines_variables(self):
        ctx1 = VariableContext(variables={"a": 1, "b": 2})
        ctx2 = VariableContext(variables={"c": 3})
        merged = ctx1.merge(ctx2)
        assert merged.variables == {"a": 1, "b": 2, "c": 3}

    def test_merge_other_takes_priority(self):
        ctx1 = VariableContext(variables={"key": "old"})
        ctx2 = VariableContext(variables={"key": "new"})
        merged = ctx1.merge(ctx2)
        assert merged.variables["key"] == "new"

    def test_merge_preserves_original(self):
        ctx1 = VariableContext(variables={"a": 1})
        ctx2 = VariableContext(variables={"b": 2})
        merged = ctx1.merge(ctx2)
        # Original contexts should be unchanged
        assert ctx1.variables == {"a": 1}
        assert ctx2.variables == {"b": 2}
        assert merged.variables == {"a": 1, "b": 2}

    def test_merge_all_fields(self):
        ctx1 = VariableContext(
            variables={"v1": 1},
            environment={"E1": "e1"},
            project_info={"p1": "p1"},
        )
        ctx2 = VariableContext(
            variables={"v2": 2},
            environment={"E2": "e2"},
            project_info={"p2": "p2"},
        )
        merged = ctx1.merge(ctx2)
        assert "v1" in merged.variables and "v2" in merged.variables
        assert "E1" in merged.environment and "E2" in merged.environment
        assert "p1" in merged.project_info and "p2" in merged.project_info

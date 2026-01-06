"""Tests for skill renderer."""

from __future__ import annotations

import pytest

from aiskills.core.renderer import RenderError, SkillRenderer, get_renderer
from aiskills.models.skill import Skill, SkillManifest
from aiskills.models.variable import SkillVariable, VariableContext


class TestSkillRenderer:
    """Tests for SkillRenderer class."""

    @pytest.fixture
    def renderer(self):
        return SkillRenderer()

    @pytest.fixture
    def skill_with_vars(self, tmp_path):
        """Create a skill with variables for testing."""
        manifest = SkillManifest(
            name="templated-skill",
            description="A skill with variables",
            variables={
                "language": SkillVariable(
                    type="string",
                    default="python",
                    enum=["python", "javascript", "rust"],
                ),
                "include_examples": SkillVariable(
                    type="boolean",
                    default=True,
                ),
                "max_depth": SkillVariable(
                    type="integer",
                    default=5,
                    min=1,
                    max=10,
                ),
                "required_var": SkillVariable(
                    type="string",
                    required=True,
                ),
            },
        )

        content = """\
# Guide for {{ language }}

{% if include_examples %}
## Examples

Here are {{ language }} examples:
{% endif %}

Max depth: {{ max_depth }}
"""
        return Skill(
            manifest=manifest,
            content=content,
            raw_content="---\nname: test\n---\n" + content,
            path=str(tmp_path),
        )

    # Basic rendering tests
    def test_render_without_variables(self, renderer, sample_skill):
        result = renderer.render(sample_skill)
        assert "Test Skill" in result

    def test_render_with_default_variables(self, renderer, skill_with_vars):
        result = renderer.render(skill_with_vars)
        assert "python" in result
        assert "Examples" in result  # include_examples is True by default
        assert "Max depth: 5" in result

    def test_render_with_provided_variables(self, renderer, skill_with_vars):
        context = VariableContext(variables={"language": "rust"})
        result = renderer.render(skill_with_vars, context)
        assert "rust" in result

    def test_render_override_default(self, renderer, skill_with_vars):
        context = VariableContext(variables={
            "language": "javascript",
            "max_depth": 10,
        })
        result = renderer.render(skill_with_vars, context)
        assert "javascript" in result
        assert "Max depth: 10" in result

    def test_render_boolean_false_hides_section(self, renderer, skill_with_vars):
        context = VariableContext(variables={"include_examples": False})
        result = renderer.render(skill_with_vars, context)
        assert "Examples" not in result

    # Context priority tests
    def test_render_context_variables_priority(self, renderer, skill_with_vars):
        context = VariableContext(
            variables={"language": "from_vars"},
            environment={"language": "from_env"},
        )
        result = renderer.render(skill_with_vars, context)
        assert "from_vars" in result

    def test_render_extra_context_variables(self, renderer, tmp_path):
        """Variables not defined in skill but provided in context."""
        manifest = SkillManifest(name="test", description="test")
        skill = Skill(
            manifest=manifest,
            content="Hello {{ name }}!",
            raw_content="test",
            path=str(tmp_path),
        )
        context = VariableContext(variables={"name": "World"})
        result = renderer.render(skill, context)
        assert "Hello World!" in result

    # Undefined variable behavior
    def test_render_undefined_variable_silent(self, renderer, tmp_path):
        """Undefined variables should render as empty string by default."""
        manifest = SkillManifest(name="test", description="test")
        skill = Skill(
            manifest=manifest,
            content="Value: {{ undefined_var }}",
            raw_content="test",
            path=str(tmp_path),
        )
        result = renderer.render(skill)
        assert "Value:" in result
        assert "{{ undefined_var }}" not in result

    # Strict mode tests
    def test_render_strict_required_missing(self, renderer, skill_with_vars):
        """Strict mode should error on missing required variables."""
        with pytest.raises(RenderError) as exc:
            renderer.render(skill_with_vars, strict=True)
        assert "required_var" in str(exc.value).lower()

    def test_render_strict_required_provided(self, renderer, skill_with_vars):
        context = VariableContext(variables={"required_var": "value"})
        result = renderer.render(skill_with_vars, context, strict=True)
        assert result is not None

    def test_render_strict_invalid_type(self, renderer, skill_with_vars):
        context = VariableContext(variables={
            "required_var": "value",
            "max_depth": "not an integer",  # Should be integer
        })
        with pytest.raises(RenderError):
            renderer.render(skill_with_vars, context, strict=True)

    def test_render_strict_invalid_enum(self, renderer, skill_with_vars):
        context = VariableContext(variables={
            "required_var": "value",
            "language": "invalid_lang",  # Not in enum
        })
        with pytest.raises(RenderError):
            renderer.render(skill_with_vars, context, strict=True)

    # Template syntax tests
    def test_render_jinja2_if(self, renderer, tmp_path):
        manifest = SkillManifest(name="test", description="test")
        skill = Skill(
            manifest=manifest,
            content="{% if show %}Visible{% endif %}",
            raw_content="test",
            path=str(tmp_path),
        )
        # True
        result = renderer.render(skill, VariableContext(variables={"show": True}))
        assert "Visible" in result
        # False
        result = renderer.render(skill, VariableContext(variables={"show": False}))
        assert "Visible" not in result

    def test_render_jinja2_if_else(self, renderer, tmp_path):
        manifest = SkillManifest(name="test", description="test")
        skill = Skill(
            manifest=manifest,
            content="{% if active %}Active{% else %}Inactive{% endif %}",
            raw_content="test",
            path=str(tmp_path),
        )
        result = renderer.render(skill, VariableContext(variables={"active": True}))
        assert "Active" in result
        result = renderer.render(skill, VariableContext(variables={"active": False}))
        assert "Inactive" in result

    def test_render_jinja2_for_loop(self, renderer, tmp_path):
        manifest = SkillManifest(name="test", description="test")
        skill = Skill(
            manifest=manifest,
            content="{% for item in items %}- {{ item }}\n{% endfor %}",
            raw_content="test",
            path=str(tmp_path),
        )
        context = VariableContext(variables={"items": ["a", "b", "c"]})
        result = renderer.render(skill, context)
        assert "- a" in result
        assert "- b" in result
        assert "- c" in result

    def test_render_template_syntax_error(self, renderer, tmp_path):
        manifest = SkillManifest(name="test", description="test")
        skill = Skill(
            manifest=manifest,
            content="{% if unclosed",
            raw_content="test",
            path=str(tmp_path),
        )
        with pytest.raises(RenderError) as exc:
            renderer.render(skill)
        assert "syntax error" in str(exc.value).lower()

    # validate_variables() tests
    def test_validate_variables_all_valid(self, renderer, skill_with_vars):
        provided = {
            "required_var": "value",
            "language": "python",
            "max_depth": 5,
        }
        errors = renderer.validate_variables(skill_with_vars, provided)
        assert errors == []

    def test_validate_variables_missing_required(self, renderer, skill_with_vars):
        errors = renderer.validate_variables(skill_with_vars, {})
        assert any("required_var" in e for e in errors)

    def test_validate_variables_invalid_type(self, renderer, skill_with_vars):
        errors = renderer.validate_variables(
            skill_with_vars,
            {"max_depth": "string", "required_var": "x"},
        )
        assert any("max_depth" in e for e in errors)

    def test_validate_variables_out_of_range(self, renderer, skill_with_vars):
        errors = renderer.validate_variables(
            skill_with_vars,
            {"max_depth": 100, "required_var": "x"},  # max is 10
        )
        assert any("max_depth" in e for e in errors)

    def test_validate_variables_invalid_enum(self, renderer, skill_with_vars):
        errors = renderer.validate_variables(
            skill_with_vars,
            {"language": "cobol", "required_var": "x"},
        )
        assert any("language" in e for e in errors)

    # extract_variables() tests
    def test_extract_variables_simple(self, renderer):
        content = "Hello {{ name }}, welcome to {{ place }}!"
        vars = renderer.extract_variables(content)
        assert "name" in vars
        assert "place" in vars

    def test_extract_variables_with_filter(self, renderer):
        content = "{{ value | upper }}"
        vars = renderer.extract_variables(content)
        assert "value" in vars

    def test_extract_variables_from_conditionals(self, renderer):
        content = "{% if show_section %}Content{% endif %}"
        vars = renderer.extract_variables(content)
        assert "show_section" in vars

    def test_extract_variables_from_loops(self, renderer):
        content = "{% for item in items %}{{ item }}{% endfor %}"
        vars = renderer.extract_variables(content)
        assert "items" in vars

    def test_extract_variables_empty(self, renderer):
        content = "No variables here."
        vars = renderer.extract_variables(content)
        assert vars == []

    def test_extract_variables_deduplicates(self, renderer):
        content = "{{ x }} and {{ x }} again"
        vars = renderer.extract_variables(content)
        assert vars.count("x") == 1

    def test_extract_variables_sorted(self, renderer):
        content = "{{ zebra }} {{ alpha }} {{ mango }}"
        vars = renderer.extract_variables(content)
        assert vars == ["alpha", "mango", "zebra"]

    # preview_variables() tests
    def test_preview_variables(self, renderer, skill_with_vars):
        preview = renderer.preview_variables(skill_with_vars)

        assert "language" in preview
        assert preview["language"]["type"] == "string"
        assert preview["language"]["default"] == "python"
        assert preview["language"]["enum"] == ["python", "javascript", "rust"]

        assert "max_depth" in preview
        assert preview["max_depth"]["type"] == "integer"
        assert preview["max_depth"]["default"] == 5

    def test_preview_variables_empty(self, renderer, sample_skill):
        preview = renderer.preview_variables(sample_skill)
        assert preview == {}


class TestSilentUndefined:
    """Tests for SilentUndefined behavior."""

    def test_undefined_str_is_empty(self):
        from aiskills.core.renderer import SilentUndefined

        undef = SilentUndefined()
        assert str(undef) == ""

    def test_undefined_repr_is_empty(self):
        from aiskills.core.renderer import SilentUndefined

        undef = SilentUndefined()
        assert repr(undef) == ""

    def test_undefined_bool_is_false(self):
        from aiskills.core.renderer import SilentUndefined

        undef = SilentUndefined()
        assert bool(undef) is False

    def test_undefined_iter_is_empty(self):
        from aiskills.core.renderer import SilentUndefined

        undef = SilentUndefined()
        assert list(undef) == []

    def test_undefined_len_is_zero(self):
        from aiskills.core.renderer import SilentUndefined

        undef = SilentUndefined()
        assert len(undef) == 0


class TestGetRenderer:
    """Tests for get_renderer singleton."""

    def test_returns_renderer_instance(self):
        renderer = get_renderer()
        assert isinstance(renderer, SkillRenderer)

    def test_returns_same_instance(self):
        r1 = get_renderer()
        r2 = get_renderer()
        assert r1 is r2


class TestRenderError:
    """Tests for RenderError exception."""

    def test_error_message(self):
        error = RenderError("Failed to render")
        assert str(error) == "Failed to render"
        assert error.variable is None

    def test_error_with_variable(self):
        error = RenderError("Invalid value", variable="my_var")
        assert error.variable == "my_var"

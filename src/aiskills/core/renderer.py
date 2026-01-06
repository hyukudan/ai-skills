"""Skill renderer - applies variables and templates using Jinja2."""

from __future__ import annotations

from typing import Any

from jinja2 import Environment, BaseLoader, TemplateSyntaxError, UndefinedError, Undefined

from ..models.skill import Skill
from ..models.variable import SkillVariable, VariableContext


class SilentUndefined(Undefined):
    """Jinja2 undefined that returns empty string instead of raising."""

    def _fail_with_undefined_error(self, *args, **kwargs):
        return ""

    def __str__(self) -> str:
        return ""

    def __repr__(self) -> str:
        return ""

    def __bool__(self) -> bool:
        return False

    def __iter__(self):
        return iter([])

    def __len__(self):
        return 0


class RenderError(Exception):
    """Error rendering skill content."""

    def __init__(self, message: str, variable: str | None = None):
        self.variable = variable
        super().__init__(message)


class SkillRenderer:
    """Renders skill content with variables using Jinja2.

    Supports:
    - Simple variables: {{ variable_name }}
    - Conditionals: {% if condition %}...{% endif %}
    - Loops: {% for item in items %}...{% endfor %}
    - Filters: {{ value | upper }}, {{ value | default('fallback') }}
    """

    def __init__(self):
        self.env = Environment(
            loader=BaseLoader(),
            # Keep default Jinja2 delimiters for better compatibility
            variable_start_string="{{",
            variable_end_string="}}",
            block_start_string="{%",
            block_end_string="%}",
            comment_start_string="{#",
            comment_end_string="#}",
            # Don't auto-escape (we're dealing with markdown, not HTML)
            autoescape=False,
            # Keep undefined variables as-is instead of erroring
            undefined=SilentUndefined,
        )

        # Add custom filters
        self.env.filters["default"] = lambda v, d: d if v is None else v

    def render(
        self,
        skill: Skill,
        context: VariableContext | None = None,
        strict: bool = False,
    ) -> str:
        """Render skill content with variables.

        Args:
            skill: Skill to render
            context: Variable context with provided values
            strict: If True, raise error on undefined variables

        Returns:
            Rendered content

        Raises:
            RenderError: If rendering fails
        """
        context = context or VariableContext()

        # Build variable dict: defaults + provided
        variables = self._build_variables(skill.manifest.variables, context)

        # Validate required variables in strict mode
        if strict:
            errors = self.validate_variables(skill, context.variables)
            if errors:
                raise RenderError(f"Variable validation failed: {'; '.join(errors)}")

        # Render content
        content = skill.rendered_content or skill.content

        try:
            template = self.env.from_string(content)
            rendered = template.render(**variables)
            return rendered

        except TemplateSyntaxError as e:
            raise RenderError(f"Template syntax error at line {e.lineno}: {e.message}") from e
        except UndefinedError as e:
            raise RenderError(f"Undefined variable: {e}") from e
        except Exception as e:
            raise RenderError(f"Render error: {e}") from e

    def _build_variables(
        self,
        definitions: dict[str, SkillVariable],
        context: VariableContext,
    ) -> dict[str, Any]:
        """Build final variable dict from definitions and context."""
        variables: dict[str, Any] = {}

        # Start with defaults from definitions
        for name, var_def in definitions.items():
            variables[name] = var_def.get_value(context.variables.get(name))

        # Add any extra variables from context not in definitions
        for name, value in context.variables.items():
            if name not in variables:
                variables[name] = value

        # Add environment variables
        for name, value in context.environment.items():
            if name not in variables:
                variables[name] = value

        # Add project info
        for name, value in context.project_info.items():
            if name not in variables:
                variables[name] = value

        return variables

    def validate_variables(
        self,
        skill: Skill,
        provided: dict[str, Any],
    ) -> list[str]:
        """Validate provided variables against skill's variable definitions.

        Args:
            skill: Skill with variable definitions
            provided: Provided variable values

        Returns:
            List of validation error messages
        """
        errors: list[str] = []

        for name, var_def in skill.manifest.variables.items():
            value = provided.get(name)

            # Check if required
            if var_def.required and value is None and var_def.default is None:
                errors.append(f"Required variable '{name}' not provided")
                continue

            # Validate value if provided
            if value is not None:
                is_valid, error = var_def.validate_value(value)
                if not is_valid:
                    errors.append(f"Variable '{name}': {error}")

        return errors

    def extract_variables(self, content: str) -> list[str]:
        """Extract variable names used in content.

        Args:
            content: Template content

        Returns:
            List of variable names found
        """
        import re

        # Find {{ variable }} patterns
        simple_vars = re.findall(r"\{\{\s*(\w+)(?:\s*\||\s*\}\})", content)

        # Find {% if variable %} patterns
        condition_vars = re.findall(r"\{%\s*if\s+(\w+)", content)

        # Find {% for item in variable %} patterns
        loop_vars = re.findall(r"\{%\s*for\s+\w+\s+in\s+(\w+)", content)

        all_vars = set(simple_vars + condition_vars + loop_vars)
        return sorted(all_vars)

    def preview_variables(self, skill: Skill) -> dict[str, dict[str, Any]]:
        """Get preview of skill's variables with their metadata.

        Args:
            skill: Skill to preview

        Returns:
            Dict of variable name -> metadata
        """
        result: dict[str, dict[str, Any]] = {}

        for name, var_def in skill.manifest.variables.items():
            result[name] = {
                "type": var_def.type,
                "default": var_def.default,
                "required": var_def.required,
                "description": var_def.description,
                "enum": var_def.enum,
            }

        return result


# Singleton instance
_renderer: SkillRenderer | None = None


def get_renderer() -> SkillRenderer:
    """Get the singleton renderer instance."""
    global _renderer
    if _renderer is None:
        _renderer = SkillRenderer()
    return _renderer

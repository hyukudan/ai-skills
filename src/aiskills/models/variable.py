"""Variable models for skill templates."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

VariableType = Literal["string", "integer", "float", "boolean", "array", "object"]


class SkillVariable(BaseModel):
    """Definition of a skill variable with validation rules."""

    type: VariableType = "string"
    default: Any = None
    description: str | None = None
    required: bool = False

    # Validation constraints
    enum: list[Any] | None = None
    min: int | float | None = None
    max: int | float | None = None
    pattern: str | None = None  # Regex for strings

    # Array-specific
    items: str | None = None  # Type of array items
    min_items: int | None = None
    max_items: int | None = None

    def validate_value(self, value: Any) -> tuple[bool, str | None]:
        """Validate a value against this variable's constraints.

        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            if self.required and self.default is None:
                return False, "Required variable not provided"
            return True, None

        # Type validation
        type_checks = {
            "string": lambda v: isinstance(v, str),
            "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
            "float": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
            "boolean": lambda v: isinstance(v, bool),
            "array": lambda v: isinstance(v, list),
            "object": lambda v: isinstance(v, dict),
        }

        if not type_checks.get(self.type, lambda _: True)(value):
            return False, f"Expected {self.type}, got {type(value).__name__}"

        # Enum validation
        if self.enum is not None and value not in self.enum:
            return False, f"Value must be one of: {self.enum}"

        # Range validation for numbers
        if self.type in ("integer", "float"):
            if self.min is not None and value < self.min:
                return False, f"Value must be >= {self.min}"
            if self.max is not None and value > self.max:
                return False, f"Value must be <= {self.max}"

        # Array length validation
        if self.type == "array":
            if self.min_items is not None and len(value) < self.min_items:
                return False, f"Array must have at least {self.min_items} items"
            if self.max_items is not None and len(value) > self.max_items:
                return False, f"Array must have at most {self.max_items} items"

        return True, None

    def get_value(self, provided: Any = None) -> Any:
        """Get the effective value, using default if not provided."""
        if provided is not None:
            return provided
        return self.default


class VariableContext(BaseModel):
    """Runtime context for variable resolution."""

    variables: dict[str, Any] = Field(default_factory=dict)
    environment: dict[str, str] = Field(default_factory=dict)
    project_info: dict[str, Any] = Field(default_factory=dict)

    def resolve(self, name: str, default: Any = None) -> Any:
        """Resolve a variable with fallback chain.

        Priority: variables > environment > project_info > default
        """
        if name in self.variables:
            return self.variables[name]

        # Check environment (prefixed with AISKILLS_)
        env_key = f"AISKILLS_{name.upper()}"
        if env_key in self.environment:
            return self.environment[env_key]

        if name in self.project_info:
            return self.project_info[name]

        return default

    def merge(self, other: VariableContext) -> VariableContext:
        """Merge another context into this one (other takes priority)."""
        return VariableContext(
            variables={**self.variables, **other.variables},
            environment={**self.environment, **other.environment},
            project_info={**self.project_info, **other.project_info},
        )

"""Base interface for LLM provider integrations.

This module defines the abstract interface that all LLM integrations implement,
ensuring consistent behavior across providers.
"""

from __future__ import annotations

import functools
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

# Type variable for generic retry decorator
T = TypeVar("T")


# =============================================================================
# Custom Exceptions
# =============================================================================


class AISkillsError(Exception):
    """Base exception for all AI Skills errors."""

    pass


class ProviderError(AISkillsError):
    """Error from the LLM provider (API errors, rate limits, etc.)."""

    def __init__(
        self,
        message: str,
        provider: str,
        status_code: int | None = None,
        retryable: bool = False,
    ):
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code
        self.retryable = retryable


class RateLimitError(ProviderError):
    """Rate limit exceeded - should retry with backoff."""

    def __init__(self, message: str, provider: str, retry_after: float | None = None):
        super().__init__(message, provider, status_code=429, retryable=True)
        self.retry_after = retry_after


class ToolExecutionError(AISkillsError):
    """Error executing a tool call."""

    def __init__(self, tool_name: str, message: str, arguments: dict | None = None):
        super().__init__(f"Tool '{tool_name}' failed: {message}")
        self.tool_name = tool_name
        self.arguments = arguments


class ToolValidationError(AISkillsError):
    """Tool arguments failed validation."""

    def __init__(self, tool_name: str, message: str, invalid_args: list[str] | None = None):
        super().__init__(f"Invalid arguments for '{tool_name}': {message}")
        self.tool_name = tool_name
        self.invalid_args = invalid_args or []


class SkillNotFoundError(AISkillsError):
    """Requested skill was not found."""

    def __init__(self, skill_name: str, query: str | None = None):
        msg = f"Skill '{skill_name}' not found"
        if query:
            msg += f" (query: '{query}')"
        super().__init__(msg)
        self.skill_name = skill_name
        self.query = query


# =============================================================================
# Retry Logic with Exponential Backoff
# =============================================================================


def retry_with_backoff(
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    exponential_base: float = 2.0,
    retryable_exceptions: tuple = (RateLimitError,),
    retryable_status_codes: tuple[int, ...] = (429, 500, 502, 503, 504),
):
    """Decorator for retrying functions with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        base_delay: Initial delay in seconds (default: 1.0)
        max_delay: Maximum delay between retries (default: 30.0)
        exponential_base: Multiplier for exponential backoff (default: 2.0)
        retryable_exceptions: Exception types that should trigger retry
        retryable_status_codes: HTTP status codes that should trigger retry

    Example:
        >>> @retry_with_backoff(max_retries=3)
        ... def call_api():
        ...     return api.chat(message)
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.warning(
                            f"Max retries ({max_retries}) exceeded for {func.__name__}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(
                        base_delay * (exponential_base ** attempt),
                        max_delay,
                    )

                    # Use retry_after if provided (for rate limits)
                    if isinstance(e, RateLimitError) and e.retry_after:
                        delay = min(e.retry_after, max_delay)

                    logger.info(
                        f"Retry {attempt + 1}/{max_retries} for {func.__name__} "
                        f"after {delay:.1f}s (error: {e})"
                    )
                    time.sleep(delay)

                except ProviderError as e:
                    # Check if status code is retryable
                    if e.status_code in retryable_status_codes and e.retryable:
                        last_exception = e

                        if attempt == max_retries:
                            raise

                        delay = min(
                            base_delay * (exponential_base ** attempt),
                            max_delay,
                        )
                        logger.info(
                            f"Retry {attempt + 1}/{max_retries} for {func.__name__} "
                            f"after {delay:.1f}s (status: {e.status_code})"
                        )
                        time.sleep(delay)
                    else:
                        # Non-retryable error
                        raise

            # Should not reach here, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError("Retry logic failed unexpectedly")

        return wrapper

    return decorator


# =============================================================================
# Input Validation
# =============================================================================


def validate_tool_arguments(
    tool_name: str,
    arguments: dict[str, Any],
    required: list[str],
    parameters: dict[str, dict],
) -> dict[str, Any]:
    """Validate tool arguments against schema.

    Args:
        tool_name: Name of the tool being called
        arguments: Arguments provided to the tool
        required: List of required parameter names
        parameters: Parameter definitions with types

    Returns:
        Validated and cleaned arguments

    Raises:
        ToolValidationError: If validation fails
    """
    if not isinstance(arguments, dict):
        raise ToolValidationError(
            tool_name,
            f"Arguments must be a dictionary, got {type(arguments).__name__}",
        )

    # Check required parameters
    missing = [r for r in required if r not in arguments or arguments[r] is None]
    if missing:
        raise ToolValidationError(
            tool_name,
            f"Missing required parameters: {', '.join(missing)}",
            invalid_args=missing,
        )

    # Type validation for provided arguments
    validated = {}
    for key, value in arguments.items():
        if key not in parameters:
            # Unknown parameter - skip but warn
            logger.debug(f"Unknown parameter '{key}' for tool '{tool_name}'")
            continue

        param_def = parameters[key]
        expected_type = param_def.get("type")

        if value is None:
            if key in required:
                raise ToolValidationError(
                    tool_name,
                    f"Required parameter '{key}' cannot be null",
                    invalid_args=[key],
                )
            # Optional parameter with null value - use default if available
            validated[key] = param_def.get("default")
            continue

        # Basic type validation
        if expected_type == "string" and not isinstance(value, str):
            raise ToolValidationError(
                tool_name,
                f"Parameter '{key}' must be a string, got {type(value).__name__}",
                invalid_args=[key],
            )
        elif expected_type == "integer" and not isinstance(value, int):
            # Allow conversion from string
            if isinstance(value, str) and value.isdigit():
                value = int(value)
            else:
                raise ToolValidationError(
                    tool_name,
                    f"Parameter '{key}' must be an integer, got {type(value).__name__}",
                    invalid_args=[key],
                )
        elif expected_type == "boolean" and not isinstance(value, bool):
            raise ToolValidationError(
                tool_name,
                f"Parameter '{key}' must be a boolean, got {type(value).__name__}",
                invalid_args=[key],
            )
        elif expected_type == "array" and not isinstance(value, list):
            raise ToolValidationError(
                tool_name,
                f"Parameter '{key}' must be an array, got {type(value).__name__}",
                invalid_args=[key],
            )
        elif expected_type == "object" and not isinstance(value, dict):
            raise ToolValidationError(
                tool_name,
                f"Parameter '{key}' must be an object, got {type(value).__name__}",
                invalid_args=[key],
            )

        validated[key] = value

    return validated


# =============================================================================
# Token Counting and Cost Estimation
# =============================================================================


# Pricing per 1K tokens (input/output) - Updated January 2025
MODEL_PRICING: dict[str, dict[str, float]] = {
    # OpenAI
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    "gpt-3.5-turbo": {"input": 0.0005, "output": 0.0015},
    "o1": {"input": 0.015, "output": 0.06},
    "o1-mini": {"input": 0.003, "output": 0.012},
    # Anthropic
    "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
    "claude-sonnet-4-20250514": {"input": 0.003, "output": 0.015},
    "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
    "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
    # Gemini (free tier available, these are paid tier)
    "gemini-1.5-pro": {"input": 0.00025, "output": 0.0005},
    "gemini-1.5-flash": {"input": 0.000075, "output": 0.0003},
    "gemini-2.0-flash": {"input": 0.0001, "output": 0.0004},
    # Ollama (free - local)
    "llama3.1": {"input": 0.0, "output": 0.0},
    "llama3.2": {"input": 0.0, "output": 0.0},
    "mistral": {"input": 0.0, "output": 0.0},
    "mixtral": {"input": 0.0, "output": 0.0},
    "codellama": {"input": 0.0, "output": 0.0},
}


def count_tokens_estimate(text: str, model: str = "gpt-4") -> int:
    """Estimate token count for text.

    Uses tiktoken for OpenAI models when available, otherwise uses a
    character-based estimate (roughly 4 chars per token).

    Args:
        text: Text to count tokens for
        model: Model name (affects tokenization)

    Returns:
        Estimated token count
    """
    if not text:
        return 0

    # Try tiktoken for OpenAI models
    if "gpt" in model.lower() or model.startswith("o1"):
        try:
            import tiktoken

            try:
                encoding = tiktoken.encoding_for_model(model)
            except KeyError:
                # Fall back to cl100k_base for newer models
                encoding = tiktoken.get_encoding("cl100k_base")

            return len(encoding.encode(text))
        except ImportError:
            pass  # Fall through to estimate

    # Claude uses a similar tokenization to GPT-4
    # Gemini and others: use character-based estimate
    # Average: ~4 characters per token for English text
    return max(1, len(text) // 4)


def estimate_cost(
    input_tokens: int,
    output_tokens: int,
    model: str,
) -> float:
    """Estimate cost for a request.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name

    Returns:
        Estimated cost in USD
    """
    pricing = MODEL_PRICING.get(model, {"input": 0.01, "output": 0.03})

    input_cost = (input_tokens / 1000) * pricing["input"]
    output_cost = (output_tokens / 1000) * pricing["output"]

    return round(input_cost + output_cost, 6)


@dataclass
class UsageStats:
    """Token usage and cost statistics for a session or request."""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost: float = 0.0
    requests: int = 0
    model: str = ""

    def add(self, input_tokens: int, output_tokens: int, model: str = "") -> None:
        """Add usage from a request.

        Args:
            input_tokens: Input tokens used
            output_tokens: Output tokens used
            model: Model used (for cost calculation)
        """
        self.input_tokens += input_tokens
        self.output_tokens += output_tokens
        self.total_tokens = self.input_tokens + self.output_tokens
        self.requests += 1
        self.model = model or self.model

        if self.model:
            self.estimated_cost = estimate_cost(
                self.input_tokens,
                self.output_tokens,
                self.model,
            )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "input_tokens": self.input_tokens,
            "output_tokens": self.output_tokens,
            "total_tokens": self.total_tokens,
            "estimated_cost": self.estimated_cost,
            "requests": self.requests,
            "model": self.model,
        }


class UsageTracker:
    """Track token usage and costs across multiple requests.

    Example:
        >>> tracker = UsageTracker()
        >>> tracker.add_usage(150, 300, "gpt-4")
        >>> print(f"Total cost: ${tracker.total_cost:.4f}")
    """

    def __init__(self):
        self._stats = UsageStats()
        self._history: list[dict[str, Any]] = []

    def add_usage(
        self,
        input_tokens: int,
        output_tokens: int,
        model: str = "",
    ) -> None:
        """Record usage from a request.

        Args:
            input_tokens: Input tokens used
            output_tokens: Output tokens used
            model: Model used
        """
        self._stats.add(input_tokens, output_tokens, model)
        self._history.append({
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "model": model,
            "cost": estimate_cost(input_tokens, output_tokens, model) if model else 0,
        })

    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self._stats.total_tokens

    @property
    def total_cost(self) -> float:
        """Total estimated cost in USD."""
        return self._stats.estimated_cost

    @property
    def stats(self) -> UsageStats:
        """Get current usage statistics."""
        return self._stats

    @property
    def history(self) -> list[dict[str, Any]]:
        """Get request history."""
        return self._history.copy()

    def reset(self) -> None:
        """Reset all tracking."""
        self._stats = UsageStats()
        self._history.clear()


@dataclass
class ToolDefinition:
    """Universal tool definition that can be converted to any provider format."""

    name: str
    description: str
    parameters: dict[str, Any]
    required: list[str] = field(default_factory=list)
    handler: Callable[..., Any] | None = None


@dataclass
class SkillInvocationResult:
    """Result from invoking a skill through any provider."""

    skill_name: str | None
    content: str | None
    score: float | None = None
    tokens_used: int | None = None
    error: str | None = None
    raw_response: dict[str, Any] | None = None

    @property
    def success(self) -> bool:
        """Whether the invocation was successful."""
        return self.error is None and self.content is not None


@dataclass
class SearchResult:
    """Result from searching skills."""

    results: list[dict[str, Any]]
    total: int
    query: str
    search_type: str = "hybrid"


class BaseLLMIntegration(ABC):
    """Abstract base class for LLM provider integrations.

    All provider-specific integrations (OpenAI, Gemini, Ollama) inherit from
    this class to ensure consistent behavior and API surface.

    Example:
        >>> class MyProvider(BaseLLMIntegration):
        ...     def get_tools(self): ...
        ...     def execute_tool(self, name, args): ...
    """

    def __init__(self):
        from ..core.router import get_router

        self._router = get_router()

    @property
    def router(self):
        """Access to the skill router."""
        return self._router

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider identifier (e.g., 'openai', 'gemini', 'ollama')."""
        ...

    @abstractmethod
    def get_tools(self) -> list[dict[str, Any]]:
        """Return tool definitions in the provider's native format.

        Returns:
            List of tool definitions compatible with the provider's API.
        """
        ...

    @abstractmethod
    def execute_tool(self, name: str, arguments: dict[str, Any]) -> Any:
        """Execute a tool call and return the result.

        Args:
            name: Name of the tool to execute
            arguments: Arguments for the tool

        Returns:
            Tool execution result (format depends on provider)
        """
        ...

    def use_skill(
        self,
        context: str,
        variables: dict[str, Any] | None = None,
        active_paths: list[str] | None = None,
        languages: list[str] | None = None,
    ) -> SkillInvocationResult:
        """Use a skill via natural language query.

        Args:
            context: Natural language description of what's needed
            variables: Optional template variables
            active_paths: File paths for scope matching
            languages: Programming languages for scope matching

        Returns:
            SkillInvocationResult with the skill content
        """
        try:
            result = self._router.use(
                context=context,
                variables=variables or {},
                active_paths=active_paths,
                languages=languages,
            )
            return SkillInvocationResult(
                skill_name=result.skill_name,
                content=result.content,
                score=result.score,
                tokens_used=result.tokens_used,
                raw_response={
                    "matched_query": result.matched_query,
                    "available_resources": result.available_resources,
                },
            )
        except Exception as e:
            return SkillInvocationResult(
                skill_name=None,
                content=None,
                error=str(e),
            )

    def search_skills(
        self,
        query: str,
        limit: int = 10,
        text_only: bool = False,
    ) -> SearchResult:
        """Search for skills.

        Args:
            query: Search query
            limit: Maximum results
            text_only: Use text search only (faster, no embeddings)

        Returns:
            SearchResult with matching skills
        """
        if text_only:
            results = self._router.registry.search_text(query, limit=limit)
            return SearchResult(
                results=[
                    {
                        "name": r.name,
                        "description": r.description,
                        "tags": r.tags,
                        "category": r.category,
                    }
                    for r in results
                ],
                total=len(results),
                query=query,
                search_type="text",
            )
        else:
            try:
                results = self._router.registry.search(query, limit=limit)
                return SearchResult(
                    results=[
                        {
                            "name": r.name,
                            "description": r.description,
                            "tags": r.tags,
                            "category": r.category,
                            "score": score,
                        }
                        for r, score in results
                    ],
                    total=len(results),
                    query=query,
                    search_type="semantic",
                )
            except Exception:
                # Fallback to text search
                return self.search_skills(query, limit, text_only=True)

    def read_skill(
        self,
        name: str,
        variables: dict[str, Any] | None = None,
    ) -> SkillInvocationResult:
        """Read a specific skill by name.

        Args:
            name: Exact skill name
            variables: Optional template variables

        Returns:
            SkillInvocationResult with the skill content
        """
        try:
            result = self._router.use_by_name(name, variables=variables)
            return SkillInvocationResult(
                skill_name=result.skill_name,
                content=result.content,
                score=1.0,
            )
        except Exception as e:
            return SkillInvocationResult(
                skill_name=name,
                content=None,
                error=str(e),
            )

    def list_skills(self) -> list[dict[str, Any]]:
        """List all available skills.

        Returns:
            List of skill metadata dictionaries
        """
        skills = self._router.manager.list_installed()
        return [
            {
                "name": s.manifest.name,
                "version": s.manifest.version,
                "description": s.manifest.description,
                "tags": s.manifest.tags,
                "category": s.manifest.category,
                "source": s.source,
            }
            for s in skills
        ]

    def browse_skills(
        self,
        context: str | None = None,
        active_paths: list[str] | None = None,
        languages: list[str] | None = None,
        limit: int = 20,
    ) -> list[dict[str, Any]]:
        """Browse skills with lightweight metadata (Phase 1 of Progressive Disclosure).

        Args:
            context: Optional query for filtering
            active_paths: File paths for scope matching
            languages: Programming languages for scope matching
            limit: Maximum results

        Returns:
            List of skill browse info (metadata only, no content)
        """
        results = self._router.browse(
            context=context,
            active_paths=active_paths,
            languages=languages,
            limit=limit,
        )
        return [
            {
                "name": r.name,
                "description": r.description,
                "version": r.version,
                "tags": r.tags,
                "category": r.category,
                "tokens_est": r.tokens_est,
                "priority": r.priority,
                "has_variables": r.has_variables,
            }
            for r in results
        ]


# Standard tool definitions used by all providers
STANDARD_TOOLS: list[ToolDefinition] = [
    ToolDefinition(
        name="use_skill",
        description=(
            "Find and use the best matching AI skill for your current task. "
            "Describe what you need in natural language and this tool will find "
            "the most relevant skill and return its content."
        ),
        parameters={
            "context": {
                "type": "string",
                "description": (
                    "Natural language description of what you need. "
                    "Examples: 'debug python memory leak', 'write unit tests'"
                ),
            },
            "variables": {
                "type": "object",
                "description": "Optional variables to customize the skill output",
            },
        },
        required=["context"],
    ),
    ToolDefinition(
        name="skill_search",
        description=(
            "Search for AI skills by semantic similarity or text matching. "
            "Use this to find relevant skills for a given task or topic."
        ),
        parameters={
            "query": {
                "type": "string",
                "description": "Search query for finding skills",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum number of results (default: 10)",
                "default": 10,
            },
            "text_only": {
                "type": "boolean",
                "description": "Use text search only (faster, no ML)",
                "default": False,
            },
        },
        required=["query"],
    ),
    ToolDefinition(
        name="skill_read",
        description=(
            "Read the full content of a skill by its exact name. "
            "Use this after finding a skill with skill_search."
        ),
        parameters={
            "name": {
                "type": "string",
                "description": "Name of the skill to read",
            },
            "variables": {
                "type": "object",
                "description": "Variables to render in the skill template",
            },
        },
        required=["name"],
    ),
    ToolDefinition(
        name="skill_list",
        description="List all available skills with their metadata.",
        parameters={
            "category": {
                "type": "string",
                "description": "Filter by category (optional)",
            },
        },
        required=[],
    ),
    ToolDefinition(
        name="skill_browse",
        description=(
            "Browse skills with lightweight metadata (no full content). "
            "Use this to discover skills before loading them fully. "
            "Supports context-aware filtering by file paths and languages."
        ),
        parameters={
            "context": {
                "type": "string",
                "description": "Optional query for semantic filtering",
            },
            "active_paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "File paths being worked on (for scope matching)",
            },
            "languages": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Programming languages in current context",
            },
            "limit": {
                "type": "integer",
                "description": "Maximum results (default: 20)",
                "default": 20,
            },
        },
        required=[],
    ),
]


def get_tool_schema(tool_name: str) -> tuple[list[str], dict[str, dict]] | None:
    """Get the required parameters and schema for a standard tool.

    Args:
        tool_name: Name of the tool

    Returns:
        Tuple of (required_params, parameters_schema) or None if not found
    """
    for tool in STANDARD_TOOLS:
        if tool.name == tool_name:
            return tool.required, tool.parameters
    return None

"""OpenAI/Codex integration for aiskills.

Provides a seamless integration with OpenAI's function calling API,
including automatic tool execution loop for hands-free skill invocation.

Example:
    >>> from aiskills.integrations.openai import OpenAISkills
    >>>
    >>> # Simple usage
    >>> client = OpenAISkills()
    >>> response = client.chat("Help me debug this memory leak in Python")
    >>>
    >>> # With custom OpenAI client
    >>> from openai import OpenAI
    >>> client = OpenAISkills(openai_client=OpenAI(api_key="..."))
"""

from __future__ import annotations

import json
from typing import Any, TYPE_CHECKING

from .base import BaseLLMIntegration, STANDARD_TOOLS, SkillInvocationResult

if TYPE_CHECKING:
    from openai import OpenAI
    from openai.types.chat import ChatCompletionMessageToolCall


class OpenAISkills(BaseLLMIntegration):
    """OpenAI integration with automatic skill tool execution.

    This class wraps the OpenAI API and automatically handles skill-related
    tool calls, creating a seamless experience where the model can access
    your skills without manual intervention.

    Features:
        - Automatic tool execution loop
        - Compatible with GPT-4, GPT-3.5, and Codex models
        - Supports all standard skill operations
        - Configurable auto-execution behavior

    Example:
        >>> client = OpenAISkills()
        >>> # Single turn with auto tool execution
        >>> response = client.chat("What skills do I have for Python debugging?")
        >>> print(response)

        >>> # Multi-turn conversation
        >>> messages = [{"role": "user", "content": "Help me with testing"}]
        >>> response = client.chat_with_messages(messages)
    """

    def __init__(
        self,
        openai_client: "OpenAI | None" = None,
        model: str = "gpt-4",
        auto_execute: bool = True,
        max_tool_rounds: int = 5,
    ):
        """Initialize OpenAI integration.

        Args:
            openai_client: Optional pre-configured OpenAI client.
                          If None, creates one using OPENAI_API_KEY env var.
            model: Model to use for chat completions (default: gpt-4)
            auto_execute: Automatically execute tool calls (default: True)
            max_tool_rounds: Maximum tool execution rounds to prevent infinite loops
        """
        super().__init__()
        self._client = openai_client
        self.model = model
        self.auto_execute = auto_execute
        self.max_tool_rounds = max_tool_rounds

    @property
    def client(self) -> "OpenAI":
        """Lazy-load OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI

                self._client = OpenAI()
            except ImportError:
                raise ImportError(
                    "OpenAI package not installed. Install with: pip install openai"
                )
        return self._client

    @property
    def provider_name(self) -> str:
        return "openai"

    def get_tools(self) -> list[dict[str, Any]]:
        """Return tool definitions in OpenAI function calling format.

        Returns:
            List of tools compatible with OpenAI's chat completions API.

        Example format:
            [{
                "type": "function",
                "function": {
                    "name": "use_skill",
                    "description": "...",
                    "parameters": {
                        "type": "object",
                        "properties": {...},
                        "required": [...]
                    }
                }
            }]
        """
        tools = []
        for tool_def in STANDARD_TOOLS:
            tools.append({
                "type": "function",
                "function": {
                    "name": tool_def.name,
                    "description": tool_def.description,
                    "parameters": {
                        "type": "object",
                        "properties": tool_def.parameters,
                        "required": tool_def.required,
                    },
                },
            })
        return tools

    def execute_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute a tool call and return the result.

        Args:
            name: Tool name (use_skill, skill_search, skill_read, skill_list)
            arguments: Tool arguments

        Returns:
            Dictionary with tool execution result
        """
        if name == "use_skill":
            result = self.use_skill(
                context=arguments.get("context", ""),
                variables=arguments.get("variables"),
            )
            return {
                "skill_name": result.skill_name,
                "content": result.content,
                "score": result.score,
                "error": result.error,
            }

        elif name == "skill_search":
            result = self.search_skills(
                query=arguments.get("query", ""),
                limit=arguments.get("limit", 10),
                text_only=arguments.get("text_only", False),
            )
            return {
                "results": result.results,
                "total": result.total,
                "search_type": result.search_type,
            }

        elif name == "skill_read":
            result = self.read_skill(
                name=arguments.get("name", ""),
                variables=arguments.get("variables"),
            )
            return {
                "name": result.skill_name,
                "content": result.content,
                "error": result.error,
            }

        elif name == "skill_list":
            skills = self.list_skills()
            category = arguments.get("category")
            if category:
                skills = [s for s in skills if s.get("category") == category]
            return {"skills": skills, "total": len(skills)}

        elif name == "skill_browse":
            results = self.browse_skills(
                context=arguments.get("context"),
                active_paths=arguments.get("active_paths"),
                languages=arguments.get("languages"),
                limit=arguments.get("limit", 20),
            )
            return {"skills": results, "total": len(results)}

        else:
            return {"error": f"Unknown tool: {name}"}

    def _process_tool_calls(
        self,
        tool_calls: list["ChatCompletionMessageToolCall"],
    ) -> list[dict[str, Any]]:
        """Process tool calls and return results for each.

        Args:
            tool_calls: List of tool calls from OpenAI response

        Returns:
            List of tool result messages ready for the API
        """
        results = []
        for call in tool_calls:
            try:
                arguments = json.loads(call.function.arguments)
            except json.JSONDecodeError:
                arguments = {}

            result = self.execute_tool(call.function.name, arguments)

            results.append({
                "tool_call_id": call.id,
                "role": "tool",
                "content": json.dumps(result),
            })

        return results

    def chat(
        self,
        message: str,
        system_prompt: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Send a message and get a response with automatic tool execution.

        This is the simplest way to use skills with OpenAI. The method
        automatically handles tool calls, executing skills as needed.

        Args:
            message: User message
            system_prompt: Optional system prompt (has a default)
            **kwargs: Additional arguments for chat completions

        Returns:
            Final assistant response after all tool executions

        Example:
            >>> client = OpenAISkills()
            >>> response = client.chat("How do I debug memory leaks in Python?")
            >>> print(response)
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({
                "role": "system",
                "content": (
                    "You are a helpful assistant with access to AI skills. "
                    "Use the available tools to find and apply relevant skills "
                    "when the user asks for help with technical tasks."
                ),
            })

        messages.append({"role": "user", "content": message})

        return self.chat_with_messages(messages, **kwargs)

    def chat_with_messages(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Send messages and get response with automatic tool execution loop.

        Args:
            messages: List of message dictionaries
            model: Override default model
            **kwargs: Additional arguments for chat completions

        Returns:
            Final assistant response content

        Example:
            >>> messages = [
            ...     {"role": "system", "content": "You are helpful."},
            ...     {"role": "user", "content": "Help me with Python testing"},
            ... ]
            >>> response = client.chat_with_messages(messages)
        """
        model = model or self.model
        tools = self.get_tools() if self.auto_execute else None

        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            **kwargs,
        )

        rounds = 0
        while (
            self.auto_execute
            and response.choices[0].message.tool_calls
            and rounds < self.max_tool_rounds
        ):
            rounds += 1

            # Add assistant message with tool calls
            messages.append(response.choices[0].message.model_dump())

            # Execute tools and add results
            tool_results = self._process_tool_calls(
                response.choices[0].message.tool_calls
            )
            messages.extend(tool_results)

            # Get next response
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                **kwargs,
            )

        return response.choices[0].message.content or ""

    def get_completion_with_skills(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        **kwargs: Any,
    ) -> Any:
        """Get raw completion response (for manual tool handling).

        Use this if you want to handle tool calls yourself instead of
        using the automatic execution loop.

        Args:
            messages: List of message dictionaries
            model: Override default model
            **kwargs: Additional arguments for chat completions

        Returns:
            Raw ChatCompletion response from OpenAI
        """
        return self.client.chat.completions.create(
            model=model or self.model,
            messages=messages,
            tools=self.get_tools(),
            **kwargs,
        )


def get_openai_tools() -> list[dict[str, Any]]:
    """Get skill tools in OpenAI format (convenience function).

    Returns:
        List of tool definitions for OpenAI's function calling API.

    Example:
        >>> from openai import OpenAI
        >>> from aiskills.integrations.openai import get_openai_tools
        >>>
        >>> client = OpenAI()
        >>> response = client.chat.completions.create(
        ...     model="gpt-4",
        ...     messages=[{"role": "user", "content": "Help me debug"}],
        ...     tools=get_openai_tools(),
        ... )
    """
    integration = OpenAISkills.__new__(OpenAISkills)
    # Skip __init__ to avoid loading router for just tool definitions
    return [
        {
            "type": "function",
            "function": {
                "name": tool_def.name,
                "description": tool_def.description,
                "parameters": {
                    "type": "object",
                    "properties": tool_def.parameters,
                    "required": tool_def.required,
                },
            },
        }
        for tool_def in STANDARD_TOOLS
    ]


def create_openai_client(
    api_key: str | None = None,
    model: str = "gpt-4",
    auto_execute: bool = True,
) -> OpenAISkills:
    """Create an OpenAI client with skill tools pre-configured.

    This is the recommended way to get started with OpenAI + skills.

    Args:
        api_key: OpenAI API key (uses OPENAI_API_KEY env var if not provided)
        model: Model to use (default: gpt-4)
        auto_execute: Automatically execute tool calls (default: True)

    Returns:
        Configured OpenAISkills client

    Example:
        >>> client = create_openai_client()
        >>> response = client.chat("Help me with Python debugging")
    """
    openai_client = None
    if api_key:
        from openai import OpenAI

        openai_client = OpenAI(api_key=api_key)

    return OpenAISkills(
        openai_client=openai_client,
        model=model,
        auto_execute=auto_execute,
    )

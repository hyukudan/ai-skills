"""Anthropic Claude integration for aiskills.

Provides a seamless integration with Anthropic's Claude API using tool use,
including automatic tool execution loop for hands-free skill invocation.

Example:
    >>> from aiskills.integrations.anthropic import create_anthropic_client
    >>>
    >>> # Simple usage
    >>> client = create_anthropic_client()
    >>> response = client.chat("Help me debug this memory leak in Python")
    >>>
    >>> # With custom Anthropic client
    >>> from anthropic import Anthropic
    >>> client = create_anthropic_client(api_key="...")
"""

from __future__ import annotations

import json
from typing import Any, TYPE_CHECKING

from .base import BaseLLMIntegration, STANDARD_TOOLS, SkillInvocationResult

if TYPE_CHECKING:
    from anthropic import Anthropic
    from anthropic.types import Message, ToolUseBlock


class AnthropicSkills(BaseLLMIntegration):
    """Anthropic Claude integration with automatic skill tool execution.

    This class wraps the Anthropic API and automatically handles skill-related
    tool calls, creating a seamless experience where Claude can access
    your skills without manual intervention.

    Features:
        - Automatic tool execution loop
        - Compatible with Claude 3.5, Claude 3, and future models
        - Supports all standard skill operations
        - Configurable auto-execution behavior

    Example:
        >>> client = AnthropicSkills()
        >>> # Single turn with auto tool execution
        >>> response = client.chat("What skills do I have for Python debugging?")
        >>> print(response)

        >>> # Multi-turn conversation
        >>> messages = [{"role": "user", "content": "Help me with testing"}]
        >>> response = client.chat_with_messages(messages)
    """

    def __init__(
        self,
        anthropic_client: "Anthropic | None" = None,
        model: str = "claude-sonnet-4-20250514",
        auto_execute: bool = True,
        max_tool_rounds: int = 5,
        max_tokens: int = 4096,
    ):
        """Initialize Anthropic integration.

        Args:
            anthropic_client: Optional pre-configured Anthropic client.
                             If None, creates one using ANTHROPIC_API_KEY env var.
            model: Model to use (default: claude-sonnet-4-20250514)
            auto_execute: Automatically execute tool calls (default: True)
            max_tool_rounds: Maximum tool execution rounds to prevent infinite loops
            max_tokens: Maximum tokens in response (default: 4096)
        """
        super().__init__()
        self._client = anthropic_client
        self.model = model
        self.auto_execute = auto_execute
        self.max_tool_rounds = max_tool_rounds
        self.max_tokens = max_tokens

    @property
    def client(self) -> "Anthropic":
        """Lazy-load Anthropic client."""
        if self._client is None:
            try:
                from anthropic import Anthropic

                self._client = Anthropic()
            except ImportError:
                raise ImportError(
                    "Anthropic package not installed. Install with: pip install anthropic"
                )
        return self._client

    @property
    def provider_name(self) -> str:
        return "anthropic"

    def get_tools(self) -> list[dict[str, Any]]:
        """Return tool definitions in Anthropic tool use format.

        Returns:
            List of tools compatible with Anthropic's messages API.

        Example format:
            [{
                "name": "use_skill",
                "description": "...",
                "input_schema": {
                    "type": "object",
                    "properties": {...},
                    "required": [...]
                }
            }]
        """
        tools = []
        for tool_def in STANDARD_TOOLS:
            tools.append({
                "name": tool_def.name,
                "description": tool_def.description,
                "input_schema": {
                    "type": "object",
                    "properties": tool_def.parameters,
                    "required": tool_def.required,
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

    def _extract_tool_uses(self, message: "Message") -> list["ToolUseBlock"]:
        """Extract tool use blocks from a message.

        Args:
            message: Anthropic Message response

        Returns:
            List of ToolUseBlock objects
        """
        tool_uses = []
        for block in message.content:
            if block.type == "tool_use":
                tool_uses.append(block)
        return tool_uses

    def _process_tool_calls(
        self,
        tool_uses: list["ToolUseBlock"],
    ) -> list[dict[str, Any]]:
        """Process tool calls and return results for each.

        Args:
            tool_uses: List of tool use blocks from Anthropic response

        Returns:
            List of tool result content blocks for the API
        """
        results = []
        for tool_use in tool_uses:
            arguments = tool_use.input if isinstance(tool_use.input, dict) else {}
            result = self.execute_tool(tool_use.name, arguments)

            results.append({
                "type": "tool_result",
                "tool_use_id": tool_use.id,
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

        This is the simplest way to use skills with Claude. The method
        automatically handles tool calls, executing skills as needed.

        Args:
            message: User message
            system_prompt: Optional system prompt (has a default)
            **kwargs: Additional arguments for messages API

        Returns:
            Final assistant response after all tool executions

        Example:
            >>> client = AnthropicSkills()
            >>> response = client.chat("How do I debug memory leaks in Python?")
            >>> print(response)
        """
        messages = [{"role": "user", "content": message}]

        system = system_prompt or (
            "You are a helpful assistant with access to AI skills. "
            "Use the available tools to find and apply relevant skills "
            "when the user asks for help with technical tasks."
        )

        return self.chat_with_messages(messages, system=system, **kwargs)

    def chat_with_messages(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        system: str | None = None,
        **kwargs: Any,
    ) -> str:
        """Send messages and get response with automatic tool execution loop.

        Args:
            messages: List of message dictionaries
            model: Override default model
            system: System prompt
            **kwargs: Additional arguments for messages API

        Returns:
            Final assistant response content

        Example:
            >>> messages = [
            ...     {"role": "user", "content": "Help me with Python testing"},
            ... ]
            >>> response = client.chat_with_messages(messages, system="Be helpful")
        """
        model = model or self.model
        tools = self.get_tools() if self.auto_execute else None

        api_kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": kwargs.pop("max_tokens", self.max_tokens),
        }

        if system:
            api_kwargs["system"] = system

        if tools:
            api_kwargs["tools"] = tools

        api_kwargs.update(kwargs)

        response = self.client.messages.create(**api_kwargs)

        rounds = 0
        while (
            self.auto_execute
            and response.stop_reason == "tool_use"
            and rounds < self.max_tool_rounds
        ):
            rounds += 1

            # Extract tool uses
            tool_uses = self._extract_tool_uses(response)

            # Add assistant message with tool use
            messages.append({
                "role": "assistant",
                "content": [block.model_dump() for block in response.content],
            })

            # Execute tools and add results
            tool_results = self._process_tool_calls(tool_uses)
            messages.append({
                "role": "user",
                "content": tool_results,
            })

            # Update kwargs for next call
            api_kwargs["messages"] = messages

            # Get next response
            response = self.client.messages.create(**api_kwargs)

        # Extract text from final response
        text_parts = []
        for block in response.content:
            if hasattr(block, "text"):
                text_parts.append(block.text)

        return "\n".join(text_parts)

    def get_completion_with_skills(
        self,
        messages: list[dict[str, Any]],
        model: str | None = None,
        system: str | None = None,
        **kwargs: Any,
    ) -> "Message":
        """Get raw completion response (for manual tool handling).

        Use this if you want to handle tool calls yourself instead of
        using the automatic execution loop.

        Args:
            messages: List of message dictionaries
            model: Override default model
            system: System prompt
            **kwargs: Additional arguments for messages API

        Returns:
            Raw Message response from Anthropic
        """
        api_kwargs: dict[str, Any] = {
            "model": model or self.model,
            "messages": messages,
            "max_tokens": kwargs.pop("max_tokens", self.max_tokens),
            "tools": self.get_tools(),
        }

        if system:
            api_kwargs["system"] = system

        api_kwargs.update(kwargs)

        return self.client.messages.create(**api_kwargs)


def get_anthropic_tools() -> list[dict[str, Any]]:
    """Get skill tools in Anthropic format (convenience function).

    Returns:
        List of tool definitions for Anthropic's tool use API.

    Example:
        >>> from anthropic import Anthropic
        >>> from aiskills.integrations.anthropic import get_anthropic_tools
        >>>
        >>> client = Anthropic()
        >>> response = client.messages.create(
        ...     model="claude-sonnet-4-20250514",
        ...     max_tokens=4096,
        ...     messages=[{"role": "user", "content": "Help me debug"}],
        ...     tools=get_anthropic_tools(),
        ... )
    """
    return [
        {
            "name": tool_def.name,
            "description": tool_def.description,
            "input_schema": {
                "type": "object",
                "properties": tool_def.parameters,
                "required": tool_def.required,
            },
        }
        for tool_def in STANDARD_TOOLS
    ]


def create_anthropic_client(
    api_key: str | None = None,
    model: str = "claude-sonnet-4-20250514",
    auto_execute: bool = True,
    max_tokens: int = 4096,
) -> AnthropicSkills:
    """Create an Anthropic client with skill tools pre-configured.

    This is the recommended way to get started with Claude + skills.

    Args:
        api_key: Anthropic API key (uses ANTHROPIC_API_KEY env var if not provided)
        model: Model to use (default: claude-sonnet-4-20250514)
        auto_execute: Automatically execute tool calls (default: True)
        max_tokens: Maximum tokens in response (default: 4096)

    Returns:
        Configured AnthropicSkills client

    Example:
        >>> client = create_anthropic_client()
        >>> response = client.chat("Help me with Python debugging")
    """
    anthropic_client = None
    if api_key:
        from anthropic import Anthropic

        anthropic_client = Anthropic(api_key=api_key)

    return AnthropicSkills(
        anthropic_client=anthropic_client,
        model=model,
        auto_execute=auto_execute,
        max_tokens=max_tokens,
    )

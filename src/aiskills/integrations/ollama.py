"""Ollama integration for aiskills.

Provides seamless integration with locally-running Ollama models,
supporting both tool calling (for compatible models) and prompt injection.

Example:
    >>> from aiskills.integrations.ollama import OllamaSkills
    >>>
    >>> # With tool calling (llama3.1, mistral-nemo, etc.)
    >>> client = OllamaSkills(model="llama3.1")
    >>> response = client.chat("Help me debug this Python memory leak")
    >>>
    >>> # Simple prompt injection (any model)
    >>> client = OllamaSkills(model="llama3", use_tools=False)
    >>> response = client.chat_with_skill("debug python", "Here's my code...")
"""

from __future__ import annotations

import json
from typing import Any, TYPE_CHECKING

from .base import BaseLLMIntegration, STANDARD_TOOLS, SkillInvocationResult

if TYPE_CHECKING:
    import ollama


class OllamaSkills(BaseLLMIntegration):
    """Ollama integration with skill tools.

    This class provides skill access through locally-running Ollama models.
    It supports two modes:

    1. Tool calling (for models that support it like llama3.1, mistral-nemo)
    2. Prompt injection (for any model, skills injected into context)

    Features:
        - Works with any Ollama model
        - Automatic tool execution loop
        - Prompt injection fallback for non-tool models
        - Local-only, no API keys needed

    Example:
        >>> # Tool calling mode
        >>> client = OllamaSkills(model="llama3.1")
        >>> response = client.chat("Help me with testing")

        >>> # Prompt injection mode
        >>> client = OllamaSkills(model="codellama", use_tools=False)
        >>> response = client.chat_with_skill("python debugging", "Fix this code")
    """

    # Models known to support tool calling
    TOOL_CAPABLE_MODELS = [
        "llama3.1",
        "llama3.2",
        "mistral-nemo",
        "mistral",
        "mixtral",
        "command-r",
        "command-r-plus",
        "qwen2",
        "qwen2.5",
        "firefunction",
    ]

    def __init__(
        self,
        model: str = "llama3.1",
        host: str | None = None,
        use_tools: bool | None = None,
        max_tool_rounds: int = 5,
    ):
        """Initialize Ollama integration.

        Args:
            model: Ollama model name (default: llama3.1)
            host: Ollama server host (default: http://localhost:11434)
            use_tools: Use tool calling if model supports it.
                      If None, auto-detects based on model name.
            max_tool_rounds: Maximum tool execution rounds
        """
        super().__init__()
        self.model = model
        self.host = host
        self.max_tool_rounds = max_tool_rounds
        self._client = None

        # Auto-detect tool capability
        if use_tools is None:
            self.use_tools = any(
                cap in model.lower() for cap in self.TOOL_CAPABLE_MODELS
            )
        else:
            self.use_tools = use_tools

    @property
    def client(self):
        """Lazy-load Ollama client."""
        if self._client is None:
            try:
                import ollama

                if self.host:
                    self._client = ollama.Client(host=self.host)
                else:
                    self._client = ollama
            except ImportError:
                raise ImportError(
                    "ollama package not installed. Install with: pip install ollama"
                )
        return self._client

    @property
    def async_client(self):
        """Lazy-load async Ollama client."""
        if not hasattr(self, "_async_client") or self._async_client is None:
            try:
                import ollama

                if self.host:
                    self._async_client = ollama.AsyncClient(host=self.host)
                else:
                    self._async_client = ollama.AsyncClient()
            except ImportError:
                raise ImportError(
                    "ollama package not installed. Install with: pip install ollama"
                )
        return self._async_client

    @property
    def provider_name(self) -> str:
        return "ollama"

    def get_tools(self) -> list[dict[str, Any]]:
        """Return tool definitions in Ollama format.

        Ollama uses a format similar to OpenAI's function calling.

        Returns:
            List of tool definitions for Ollama's chat API.
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
            name: Tool name
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
                "tokens_used": result.tokens_used,
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
        tool_calls: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:
        """Process tool calls from Ollama response.

        Args:
            tool_calls: List of tool calls from Ollama

        Returns:
            List of tool result messages
        """
        results = []
        for call in tool_calls:
            func = call.get("function", {})
            name = func.get("name", "")
            arguments = func.get("arguments", {})

            if isinstance(arguments, str):
                try:
                    arguments = json.loads(arguments)
                except json.JSONDecodeError:
                    arguments = {}

            result = self.execute_tool(name, arguments)
            results.append({
                "role": "tool",
                "content": json.dumps(result),
            })

        return results

    def chat(
        self,
        message: str,
        system_prompt: str | None = None,
        **options: Any,
    ) -> str:
        """Send a message and get a response.

        If use_tools is True and model supports it, uses tool calling.
        Otherwise, provides a basic chat without skill access.

        Args:
            message: User message
            system_prompt: Optional system prompt
            **options: Additional Ollama options (temperature, etc.)

        Returns:
            Model response

        Example:
            >>> response = client.chat("How do I debug memory leaks?")
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        elif self.use_tools:
            messages.append({
                "role": "system",
                "content": (
                    "You are a helpful assistant with access to AI skills. "
                    "Use the available tools to find and apply relevant skills "
                    "when the user asks for help with technical tasks."
                ),
            })

        messages.append({"role": "user", "content": message})

        return self.chat_with_messages(messages, **options)

    def chat_with_messages(
        self,
        messages: list[dict[str, Any]],
        **options: Any,
    ) -> str:
        """Send messages and get response with tool execution loop.

        Args:
            messages: List of message dictionaries
            **options: Additional Ollama options

        Returns:
            Final response content
        """
        tools = self.get_tools() if self.use_tools else None

        response = self.client.chat(
            model=self.model,
            messages=messages,
            tools=tools,
            options=options if options else None,
        )

        rounds = 0
        while (
            self.use_tools
            and response.get("message", {}).get("tool_calls")
            and rounds < self.max_tool_rounds
        ):
            rounds += 1

            # Add assistant message with tool calls
            messages.append(response["message"])

            # Execute tools and add results
            tool_results = self._process_tool_calls(
                response["message"]["tool_calls"]
            )
            messages.extend(tool_results)

            # Get next response
            response = self.client.chat(
                model=self.model,
                messages=messages,
                tools=tools,
                options=options if options else None,
            )

        return response.get("message", {}).get("content", "")

    def chat_stream(
        self,
        message: str,
        system_prompt: str | None = None,
        **options: Any,
    ):
        """Stream a response with automatic tool execution.

        Tool calls are executed first (non-streaming), then the final
        response is streamed back.

        Args:
            message: User message
            system_prompt: Optional system prompt
            **options: Additional Ollama options

        Yields:
            String chunks of the response

        Example:
            >>> for chunk in client.chat_stream("Help me debug Python"):
            ...     print(chunk, end="", flush=True)
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        elif self.use_tools:
            messages.append({
                "role": "system",
                "content": (
                    "You are a helpful assistant with access to AI skills. "
                    "Use the available tools to find and apply relevant skills "
                    "when the user asks for help with technical tasks."
                ),
            })

        messages.append({"role": "user", "content": message})

        yield from self.chat_stream_with_messages(messages, **options)

    def chat_stream_with_messages(
        self,
        messages: list[dict[str, Any]],
        **options: Any,
    ):
        """Stream messages with automatic tool execution loop.

        Tool calls are handled non-streaming, then final response streams.

        Args:
            messages: List of message dictionaries
            **options: Additional Ollama options

        Yields:
            String chunks of the response
        """
        tools = self.get_tools() if self.use_tools else None

        # First, handle any tool calls (non-streaming)
        response = self.client.chat(
            model=self.model,
            messages=messages,
            tools=tools,
            options=options if options else None,
        )

        rounds = 0
        while (
            self.use_tools
            and response.get("message", {}).get("tool_calls")
            and rounds < self.max_tool_rounds
        ):
            rounds += 1

            messages.append(response["message"])
            tool_results = self._process_tool_calls(
                response["message"]["tool_calls"]
            )
            messages.extend(tool_results)

            response = self.client.chat(
                model=self.model,
                messages=messages,
                tools=tools,
                options=options if options else None,
            )

        # Stream the final response
        if not response.get("message", {}).get("tool_calls"):
            stream = self.client.chat(
                model=self.model,
                messages=messages,
                tools=tools,
                options=options if options else None,
                stream=True,
            )

            for chunk in stream:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content
        else:
            # Fallback if still has tool calls
            yield response.get("message", {}).get("content", "")

    # ===== ASYNC METHODS =====

    async def chat_async(
        self,
        message: str,
        system_prompt: str | None = None,
        **options: Any,
    ) -> str:
        """Async version of chat().

        Args:
            message: User message
            system_prompt: Optional system prompt
            **options: Additional Ollama options

        Returns:
            Model response

        Example:
            >>> response = await client.chat_async("Help me debug Python")
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        elif self.use_tools:
            messages.append({
                "role": "system",
                "content": (
                    "You are a helpful assistant with access to AI skills. "
                    "Use the available tools to find and apply relevant skills "
                    "when the user asks for help with technical tasks."
                ),
            })

        messages.append({"role": "user", "content": message})

        return await self.chat_with_messages_async(messages, **options)

    async def chat_with_messages_async(
        self,
        messages: list[dict[str, Any]],
        **options: Any,
    ) -> str:
        """Async version of chat_with_messages().

        Args:
            messages: List of message dictionaries
            **options: Additional Ollama options

        Returns:
            Final response content

        Example:
            >>> messages = [{"role": "user", "content": "Help me with testing"}]
            >>> response = await client.chat_with_messages_async(messages)
        """
        tools = self.get_tools() if self.use_tools else None

        response = await self.async_client.chat(
            model=self.model,
            messages=messages,
            tools=tools,
            options=options if options else None,
        )

        rounds = 0
        while (
            self.use_tools
            and response.get("message", {}).get("tool_calls")
            and rounds < self.max_tool_rounds
        ):
            rounds += 1

            # Add assistant message with tool calls
            messages.append(response["message"])

            # Execute tools and add results (sync - tool execution is local)
            tool_results = self._process_tool_calls(
                response["message"]["tool_calls"]
            )
            messages.extend(tool_results)

            # Get next response
            response = await self.async_client.chat(
                model=self.model,
                messages=messages,
                tools=tools,
                options=options if options else None,
            )

        return response.get("message", {}).get("content", "")

    async def chat_stream_async(
        self,
        message: str,
        system_prompt: str | None = None,
        **options: Any,
    ):
        """Async streaming version of chat().

        Tool calls are executed first (non-streaming), then the final
        response is streamed back.

        Args:
            message: User message
            system_prompt: Optional system prompt
            **options: Additional Ollama options

        Yields:
            String chunks of the response

        Example:
            >>> async for chunk in client.chat_stream_async("Help me debug"):
            ...     print(chunk, end="", flush=True)
        """
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        elif self.use_tools:
            messages.append({
                "role": "system",
                "content": (
                    "You are a helpful assistant with access to AI skills. "
                    "Use the available tools to find and apply relevant skills "
                    "when the user asks for help with technical tasks."
                ),
            })

        messages.append({"role": "user", "content": message})

        async for chunk in self.chat_stream_with_messages_async(messages, **options):
            yield chunk

    async def chat_stream_with_messages_async(
        self,
        messages: list[dict[str, Any]],
        **options: Any,
    ):
        """Async streaming version of chat_with_messages().

        Args:
            messages: List of message dictionaries
            **options: Additional Ollama options

        Yields:
            String chunks of the response
        """
        tools = self.get_tools() if self.use_tools else None

        # First, handle any tool calls (non-streaming)
        response = await self.async_client.chat(
            model=self.model,
            messages=messages,
            tools=tools,
            options=options if options else None,
        )

        rounds = 0
        while (
            self.use_tools
            and response.get("message", {}).get("tool_calls")
            and rounds < self.max_tool_rounds
        ):
            rounds += 1

            messages.append(response["message"])
            tool_results = self._process_tool_calls(
                response["message"]["tool_calls"]
            )
            messages.extend(tool_results)

            response = await self.async_client.chat(
                model=self.model,
                messages=messages,
                tools=tools,
                options=options if options else None,
            )

        # Stream the final response
        if not response.get("message", {}).get("tool_calls"):
            stream = await self.async_client.chat(
                model=self.model,
                messages=messages,
                tools=tools,
                options=options if options else None,
                stream=True,
            )

            async for chunk in stream:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content
        else:
            # Fallback if still has tool calls
            yield response.get("message", {}).get("content", "")

    def chat_with_skill(
        self,
        skill_query: str,
        user_message: str,
        variables: dict[str, Any] | None = None,
        **options: Any,
    ) -> str:
        """Chat with a skill pre-loaded into context (prompt injection mode).

        This method works with ANY Ollama model by injecting the skill
        content directly into the prompt. Use this for models that
        don't support tool calling.

        Args:
            skill_query: Query to find the relevant skill
            user_message: User's actual question/request
            variables: Optional skill variables
            **options: Additional Ollama options

        Returns:
            Model response with skill context applied

        Example:
            >>> response = client.chat_with_skill(
            ...     "python debugging",
            ...     "Fix this memory leak in my code: ...",
            ... )
        """
        # Load the skill
        result = self.use_skill(context=skill_query, variables=variables)

        if result.error or not result.content:
            # Fall back to regular chat if no skill found
            return self.chat(user_message, **options)

        # Create prompt with skill context
        system_prompt = f"""You are a helpful assistant. Use the following guide to help the user:

---
{result.content}
---

Apply this knowledge to answer the user's question."""

        return self.chat(user_message, system_prompt=system_prompt, **options)

    def generate_with_skill(
        self,
        skill_query: str,
        prompt: str,
        variables: dict[str, Any] | None = None,
        **options: Any,
    ) -> str:
        """Generate completion with skill context (non-chat mode).

        Use this for simple completions rather than chat conversations.

        Args:
            skill_query: Query to find the relevant skill
            prompt: Generation prompt
            variables: Optional skill variables
            **options: Additional Ollama options

        Returns:
            Generated text

        Example:
            >>> code = client.generate_with_skill(
            ...     "python unit testing",
            ...     "Write tests for this function: def add(a, b): return a + b",
            ... )
        """
        # Load the skill
        result = self.use_skill(context=skill_query, variables=variables)

        if result.error or not result.content:
            full_prompt = prompt
        else:
            full_prompt = f"""Using this guide:

{result.content}

---

{prompt}"""

        response = self.client.generate(
            model=self.model,
            prompt=full_prompt,
            options=options if options else None,
        )

        return response.get("response", "")

    def list_local_models(self) -> list[dict[str, Any]]:
        """List locally available Ollama models.

        Returns:
            List of model information dictionaries
        """
        response = self.client.list()
        return response.get("models", [])

    def is_model_available(self) -> bool:
        """Check if the configured model is available locally.

        Returns:
            True if model is available, False otherwise
        """
        models = self.list_local_models()
        model_names = [m.get("name", "").split(":")[0] for m in models]
        return self.model.split(":")[0] in model_names


def get_ollama_tools() -> list[dict[str, Any]]:
    """Get skill tools in Ollama format (convenience function).

    Returns:
        List of tool definitions for Ollama's chat API.

    Example:
        >>> import ollama
        >>> from aiskills.integrations.ollama import get_ollama_tools
        >>>
        >>> response = ollama.chat(
        ...     model='llama3.1',
        ...     messages=[{'role': 'user', 'content': 'Help me debug'}],
        ...     tools=get_ollama_tools(),
        ... )
    """
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


def create_ollama_client(
    model: str = "llama3.1",
    host: str | None = None,
    use_tools: bool | None = None,
) -> OllamaSkills:
    """Create an Ollama client with skill tools.

    Args:
        model: Ollama model name (default: llama3.1)
        host: Ollama server host (default: localhost:11434)
        use_tools: Use tool calling if supported (auto-detected if None)

    Returns:
        Configured OllamaSkills client

    Example:
        >>> client = create_ollama_client(model="llama3.1")
        >>> response = client.chat("Help me with Python debugging")
    """
    return OllamaSkills(model=model, host=host, use_tools=use_tools)


def pipe_to_ollama(
    skill_query: str,
    model: str = "llama3.1",
    variables: dict[str, Any] | None = None,
) -> str:
    """Get skill content formatted for piping to Ollama CLI.

    This is useful for shell-based workflows:
        aiskills use "debug python" | ollama run llama3 "Apply this to..."

    Args:
        skill_query: Query to find the skill
        model: Model name (for reference in output)
        variables: Optional skill variables

    Returns:
        Formatted skill content ready for piping

    Example:
        >>> content = pipe_to_ollama("python debugging")
        >>> # Then in shell: echo "$content" | ollama run llama3
    """
    client = OllamaSkills(model=model, use_tools=False)
    result = client.use_skill(context=skill_query, variables=variables)

    if result.error:
        return f"Error: {result.error}"

    return result.content or "No skill found"

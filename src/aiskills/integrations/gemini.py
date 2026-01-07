"""Google Gemini integration for aiskills.

Provides seamless integration with Google's Gemini models via function calling.
Supports both automatic function calling and manual control.

Example:
    >>> from aiskills.integrations.gemini import GeminiSkills
    >>>
    >>> # Simple usage with auto function calling
    >>> client = GeminiSkills()
    >>> response = client.chat("Help me debug this Python memory leak")
    >>>
    >>> # Or get a pre-configured model
    >>> from aiskills.integrations.gemini import create_gemini_model
    >>> model = create_gemini_model()
    >>> chat = model.start_chat(enable_automatic_function_calling=True)
"""

from __future__ import annotations

from typing import Any, Callable, TYPE_CHECKING

from .base import BaseLLMIntegration, STANDARD_TOOLS, SkillInvocationResult

if TYPE_CHECKING:
    import google.generativeai as genai
    from google.generativeai import GenerativeModel
    from google.generativeai.types import FunctionDeclaration


class GeminiSkills(BaseLLMIntegration):
    """Gemini integration with skill tools.

    This class provides skill access through Google's Gemini models.
    It can work in two modes:

    1. Automatic function calling (recommended for most use cases)
    2. Manual function handling (for custom control flow)

    Features:
        - Compatible with Gemini 1.5 Pro, Gemini 1.5 Flash
        - Supports automatic function calling
        - Native Python function format
        - Full skill operations support

    Example:
        >>> client = GeminiSkills()
        >>> response = client.chat("What tools do you have for testing?")

        >>> # Or with manual control
        >>> model = client.get_model()
        >>> chat = model.start_chat()
        >>> response = chat.send_message("Help me debug")
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-1.5-pro",
        auto_function_calling: bool = True,
    ):
        """Initialize Gemini integration.

        Args:
            api_key: Gemini API key (uses GEMINI_API_KEY or
                    GOOGLE_API_KEY env var if not provided)
            model_name: Model to use (default: gemini-1.5-pro)
            auto_function_calling: Enable automatic function calling
        """
        super().__init__()
        self._api_key = api_key
        self.model_name = model_name
        self.auto_function_calling = auto_function_calling
        self._model = None
        self._genai = None

    @property
    def genai(self):
        """Lazy-load google.generativeai module."""
        if self._genai is None:
            try:
                import google.generativeai as genai

                self._genai = genai

                # Configure API key
                import os

                api_key = self._api_key or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
                if api_key:
                    genai.configure(api_key=api_key)

            except ImportError:
                raise ImportError(
                    "google-generativeai package not installed. "
                    "Install with: pip install google-generativeai"
                )
        return self._genai

    @property
    def provider_name(self) -> str:
        return "gemini"

    def _create_skill_functions(self) -> list[Callable]:
        """Create Python functions that Gemini can call.

        Gemini's function calling works best with actual Python functions
        rather than JSON schemas. This method creates wrapper functions
        that call the underlying skill operations.

        Returns:
            List of callable functions for Gemini
        """

        def use_skill(context: str, variables: dict | None = None) -> str:
            """Find and use the best AI skill for your current task.

            Args:
                context: Natural language description of what you need.
                        Examples: 'debug python memory leak', 'write unit tests'
                variables: Optional variables to customize the skill output.

            Returns:
                The skill content or an error message.
            """
            result = self.use_skill(context=context, variables=variables)
            if result.error:
                return f"Error: {result.error}"
            return result.content or "No content found"

        def skill_search(query: str, limit: int = 10) -> str:
            """Search for AI skills by semantic similarity.

            Args:
                query: Search query for finding skills.
                limit: Maximum number of results (default: 10).

            Returns:
                Formatted list of matching skills.
            """
            result = self.search_skills(query=query, limit=limit)
            if not result.results:
                return "No skills found matching your query."

            lines = [f"Found {result.total} skills:"]
            for skill in result.results:
                score = skill.get("score", "N/A")
                lines.append(f"- {skill['name']}: {skill['description']} (score: {score})")
            return "\n".join(lines)

        def skill_read(name: str, variables: dict | None = None) -> str:
            """Read the full content of a skill by name.

            Args:
                name: Name of the skill to read.
                variables: Variables to render in the skill template.

            Returns:
                The skill content or an error message.
            """
            result = self.read_skill(name=name, variables=variables)
            if result.error:
                return f"Error: {result.error}"
            return result.content or "No content found"

        def skill_list(category: str | None = None) -> str:
            """List all available AI skills.

            Args:
                category: Filter by category (optional).

            Returns:
                Formatted list of available skills.
            """
            skills = self.list_skills()
            if category:
                skills = [s for s in skills if s.get("category") == category]

            if not skills:
                return "No skills found."

            lines = [f"Available skills ({len(skills)}):"]
            for skill in skills:
                cat = skill.get("category", "uncategorized")
                lines.append(f"- {skill['name']} [{cat}]: {skill['description']}")
            return "\n".join(lines)

        def skill_browse(
            context: str | None = None,
            languages: list[str] | None = None,
            limit: int = 20,
        ) -> str:
            """Browse skills with lightweight metadata.

            Args:
                context: Optional query for filtering.
                languages: Programming languages for filtering.
                limit: Maximum results (default: 20).

            Returns:
                Formatted list of skills with metadata.
            """
            results = self.browse_skills(
                context=context,
                languages=languages,
                limit=limit,
            )

            if not results:
                return "No skills found."

            lines = [f"Found {len(results)} skills:"]
            for skill in results:
                tokens = skill.get("tokens_est", "?")
                lines.append(
                    f"- {skill['name']} (~{tokens} tokens): {skill['description']}"
                )
            return "\n".join(lines)

        return [use_skill, skill_search, skill_read, skill_list, skill_browse]

    def get_tools(self) -> list[Callable]:
        """Return tool functions for Gemini.

        Unlike OpenAI which uses JSON schemas, Gemini works best with
        actual Python functions. This returns a list of callables.

        Returns:
            List of Python functions Gemini can call.
        """
        return self._create_skill_functions()

    def execute_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute a tool by name and return structured result.

        This method provides consistent return format with other providers
        (OpenAI, Anthropic, Ollama) for manual tool handling scenarios.

        Args:
            name: Tool name (use_skill, skill_search, skill_read, skill_list, skill_browse)
            arguments: Tool arguments

        Returns:
            Dictionary with tool execution result (consistent with other providers)
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

    def get_model(self) -> "GenerativeModel":
        """Get a Gemini model pre-configured with skill tools.

        Returns:
            GenerativeModel instance with skill tools attached.

        Example:
            >>> model = client.get_model()
            >>> chat = model.start_chat(enable_automatic_function_calling=True)
            >>> response = chat.send_message("Help with debugging")
        """
        if self._model is None:
            self._model = self.genai.GenerativeModel(
                model_name=self.model_name,
                tools=self.get_tools(),
            )
        return self._model

    def chat(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        """Send a message and get a response with automatic function calling.

        Args:
            message: User message
            history: Optional conversation history

        Returns:
            Model response after any function executions

        Example:
            >>> response = client.chat("What skills do you have for Python?")
        """
        model = self.get_model()

        # Start chat with or without history
        chat = model.start_chat(
            enable_automatic_function_calling=self.auto_function_calling,
            history=history or [],
        )

        response = chat.send_message(message)
        return response.text

    def chat_with_messages(
        self,
        messages: list[dict[str, Any]],
        **kwargs: Any,
    ) -> str:
        """Send messages and get response with automatic function calling.

        This method provides a consistent interface with other providers
        (OpenAI, Anthropic, Ollama) for multi-turn conversations.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            **kwargs: Additional arguments (ignored for compatibility)

        Returns:
            Final response content

        Example:
            >>> messages = [
            ...     {"role": "user", "content": "Help me with Python testing"},
            ... ]
            >>> response = client.chat_with_messages(messages)
        """
        model = self.get_model()

        # Convert messages to Gemini history format
        # Gemini uses 'user' and 'model' roles
        history = []
        for msg in messages[:-1]:  # All but last message go to history
            role = msg.get("role", "user")
            content = msg.get("content", "")
            # Map assistant/system to model
            if role in ("assistant", "system"):
                role = "model"
            history.append({"role": role, "parts": [content]})

        # Start chat with history
        chat = model.start_chat(
            enable_automatic_function_calling=self.auto_function_calling,
            history=history,
        )

        # Send the last message
        last_message = messages[-1].get("content", "") if messages else ""
        response = chat.send_message(last_message)
        return response.text

    def start_chat(
        self,
        history: list[dict[str, str]] | None = None,
    ) -> Any:
        """Start a chat session with skill tools enabled.

        Args:
            history: Optional conversation history

        Returns:
            ChatSession object for multi-turn conversations

        Example:
            >>> chat = client.start_chat()
            >>> response1 = chat.send_message("What skills do I have?")
            >>> response2 = chat.send_message("Tell me more about debugging")
        """
        model = self.get_model()
        return model.start_chat(
            enable_automatic_function_calling=self.auto_function_calling,
            history=history or [],
        )

    def chat_stream(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ):
        """Stream a response with automatic function calling.

        Function calls are handled automatically, then the final
        response is streamed back.

        Args:
            message: User message
            history: Optional conversation history

        Yields:
            String chunks of the response

        Example:
            >>> for chunk in client.chat_stream("Help me debug Python"):
            ...     print(chunk, end="", flush=True)
        """
        model = self.get_model()

        # Start chat with function calling enabled
        chat = model.start_chat(
            enable_automatic_function_calling=self.auto_function_calling,
            history=history or [],
        )

        # Stream the response
        response = chat.send_message(message, stream=True)

        for chunk in response:
            if chunk.text:
                yield chunk.text

    # ===== ASYNC METHODS =====

    async def chat_async(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ) -> str:
        """Async version of chat().

        Args:
            message: User message
            history: Optional conversation history

        Returns:
            Model response after any function executions

        Example:
            >>> response = await client.chat_async("Help me debug Python")
        """
        model = self.get_model()

        # Start chat with or without history
        chat = model.start_chat(
            enable_automatic_function_calling=self.auto_function_calling,
            history=history or [],
        )

        response = await chat.send_message_async(message)
        return response.text

    async def chat_with_messages_async(
        self,
        messages: list[dict[str, Any]],
        **kwargs: Any,
    ) -> str:
        """Async version of chat_with_messages().

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
            **kwargs: Additional arguments (ignored for compatibility)

        Returns:
            Final response content

        Example:
            >>> messages = [{"role": "user", "content": "Help me with testing"}]
            >>> response = await client.chat_with_messages_async(messages)
        """
        model = self.get_model()

        # Convert messages to Gemini history format
        history = []
        for msg in messages[:-1]:  # All but last message go to history
            role = msg.get("role", "user")
            content = msg.get("content", "")
            if role in ("assistant", "system"):
                role = "model"
            history.append({"role": role, "parts": [content]})

        # Start chat with history
        chat = model.start_chat(
            enable_automatic_function_calling=self.auto_function_calling,
            history=history,
        )

        # Send the last message
        last_message = messages[-1].get("content", "") if messages else ""
        response = await chat.send_message_async(last_message)
        return response.text

    async def chat_stream_async(
        self,
        message: str,
        history: list[dict[str, str]] | None = None,
    ):
        """Async streaming version of chat().

        Function calls are handled automatically, then the final
        response is streamed back.

        Args:
            message: User message
            history: Optional conversation history

        Yields:
            String chunks of the response

        Example:
            >>> async for chunk in client.chat_stream_async("Help me debug"):
            ...     print(chunk, end="", flush=True)
        """
        model = self.get_model()

        # Start chat with function calling enabled
        chat = model.start_chat(
            enable_automatic_function_calling=self.auto_function_calling,
            history=history or [],
        )

        # Stream the response (async)
        response = await chat.send_message_async(message, stream=True)

        async for chunk in response:
            if chunk.text:
                yield chunk.text


def get_gemini_tools() -> list[Callable]:
    """Get skill tools as Python functions for Gemini.

    This is a convenience function to get just the tool functions
    without creating a full client.

    Returns:
        List of Python functions for Gemini's function calling.

    Example:
        >>> import google.generativeai as genai
        >>> from aiskills.integrations.gemini import get_gemini_tools
        >>>
        >>> model = genai.GenerativeModel(
        ...     model_name='gemini-1.5-pro',
        ...     tools=get_gemini_tools(),
        ... )
    """
    client = GeminiSkills.__new__(GeminiSkills)
    BaseLLMIntegration.__init__(client)
    return client._create_skill_functions()


def create_gemini_model(
    api_key: str | None = None,
    model_name: str = "gemini-1.5-pro",
) -> "GenerativeModel":
    """Create a Gemini model pre-configured with skill tools.

    This is the simplest way to get a Gemini model with skills.

    Args:
        api_key: Gemini API key (uses env var if not provided)
        model_name: Model to use (default: gemini-1.5-pro)

    Returns:
        Configured GenerativeModel with skill tools

    Example:
        >>> model = create_gemini_model()
        >>> chat = model.start_chat(enable_automatic_function_calling=True)
        >>> response = chat.send_message("Help me with Python debugging")
    """
    client = GeminiSkills(api_key=api_key, model_name=model_name)
    return client.get_model()


def create_gemini_client(
    api_key: str | None = None,
    model_name: str = "gemini-1.5-pro",
    auto_function_calling: bool = True,
) -> GeminiSkills:
    """Create a GeminiSkills client.

    Args:
        api_key: Gemini API key (uses env var if not provided)
        model_name: Model to use (default: gemini-1.5-pro)
        auto_function_calling: Enable automatic function calling

    Returns:
        Configured GeminiSkills client

    Example:
        >>> client = create_gemini_client()
        >>> response = client.chat("Help me debug memory leaks")
    """
    return GeminiSkills(
        api_key=api_key,
        model_name=model_name,
        auto_function_calling=auto_function_calling,
    )

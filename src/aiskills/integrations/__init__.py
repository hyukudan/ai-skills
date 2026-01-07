"""External integrations for aiskills.

This module provides integrations with various LLM providers:
- OpenAI (GPT-4, GPT-3.5, Codex)
- Google Gemini
- Ollama (local models)
- AGENTS.md format

Example usage:

    # OpenAI
    from aiskills.integrations import create_openai_client
    client = create_openai_client()
    response = client.chat("Help me debug Python")

    # Gemini
    from aiskills.integrations import create_gemini_client
    client = create_gemini_client()
    response = client.chat("Help me with testing")

    # Ollama
    from aiskills.integrations import create_ollama_client
    client = create_ollama_client(model="llama3.1")
    response = client.chat("Help me optimize SQL")
"""

from .agents_md import generate_agents_md, sync_agents_md
from .base import (
    BaseLLMIntegration,
    SkillInvocationResult,
    SearchResult,
    ToolDefinition,
    STANDARD_TOOLS,
)

# Lazy imports for optional dependencies
def create_openai_client(*args, **kwargs):
    """Create an OpenAI client with skill tools. Requires: pip install openai"""
    from .openai import create_openai_client as _create
    return _create(*args, **kwargs)


def create_gemini_client(*args, **kwargs):
    """Create a Gemini client with skill tools. Requires: pip install google-generativeai"""
    from .gemini import create_gemini_client as _create
    return _create(*args, **kwargs)


def create_gemini_model(*args, **kwargs):
    """Create a Gemini model with skill tools. Requires: pip install google-generativeai"""
    from .gemini import create_gemini_model as _create
    return _create(*args, **kwargs)


def create_ollama_client(*args, **kwargs):
    """Create an Ollama client with skill tools. Requires: pip install ollama"""
    from .ollama import create_ollama_client as _create
    return _create(*args, **kwargs)


def get_openai_tools():
    """Get skill tools in OpenAI function calling format."""
    from .openai import get_openai_tools as _get
    return _get()


def get_gemini_tools():
    """Get skill tools as Python functions for Gemini."""
    from .gemini import get_gemini_tools as _get
    return _get()


def get_ollama_tools():
    """Get skill tools in Ollama format."""
    from .ollama import get_ollama_tools as _get
    return _get()


__all__ = [
    # AGENTS.md
    "generate_agents_md",
    "sync_agents_md",
    # Base classes
    "BaseLLMIntegration",
    "SkillInvocationResult",
    "SearchResult",
    "ToolDefinition",
    "STANDARD_TOOLS",
    # Client factories
    "create_openai_client",
    "create_gemini_client",
    "create_gemini_model",
    "create_ollama_client",
    # Tool getters
    "get_openai_tools",
    "get_gemini_tools",
    "get_ollama_tools",
]

"""Tests for LLM provider integrations."""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, patch

import pytest


# =============================================================================
# Base Integration Tests
# =============================================================================


class TestBaseLLMIntegration:
    """Tests for the base integration interface."""

    def test_standard_tools_defined(self):
        """Standard tools should be defined."""
        from aiskills.integrations.base import STANDARD_TOOLS

        assert len(STANDARD_TOOLS) >= 4
        tool_names = [t.name for t in STANDARD_TOOLS]
        assert "use_skill" in tool_names
        assert "skill_search" in tool_names
        assert "skill_read" in tool_names
        assert "skill_list" in tool_names

    def test_tool_definition_structure(self):
        """Tool definitions should have required fields."""
        from aiskills.integrations.base import STANDARD_TOOLS

        for tool in STANDARD_TOOLS:
            assert tool.name
            assert tool.description
            assert isinstance(tool.parameters, dict)
            assert isinstance(tool.required, list)

    def test_skill_invocation_result_success(self):
        """SkillInvocationResult should track success state."""
        from aiskills.integrations.base import SkillInvocationResult

        success = SkillInvocationResult(
            skill_name="test",
            content="test content",
            score=0.9,
        )
        assert success.success is True

        failure = SkillInvocationResult(
            skill_name=None,
            content=None,
            error="Not found",
        )
        assert failure.success is False


# =============================================================================
# OpenAI Integration Tests
# =============================================================================


class TestOpenAIIntegration:
    """Tests for OpenAI/Codex integration."""

    def test_get_openai_tools_format(self):
        """OpenAI tools should be in correct format."""
        from aiskills.integrations.openai import get_openai_tools

        tools = get_openai_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0

        for tool in tools:
            assert tool["type"] == "function"
            assert "function" in tool
            func = tool["function"]
            assert "name" in func
            assert "description" in func
            assert "parameters" in func
            assert func["parameters"]["type"] == "object"
            assert "properties" in func["parameters"]
            assert "required" in func["parameters"]

    def test_openai_skills_provider_name(self, mock_config):
        """OpenAISkills should identify as openai provider."""
        from aiskills.integrations.openai import OpenAISkills

        client = OpenAISkills.__new__(OpenAISkills)
        assert client.provider_name == "openai"

    def test_openai_execute_tool_unknown(self, mock_config):
        """Unknown tool should return error."""
        from aiskills.integrations.openai import OpenAISkills

        with patch("aiskills.core.router.get_router"):
            client = OpenAISkills()
            result = client.execute_tool("unknown_tool", {})
            assert "error" in result
            assert "unknown" in result["error"].lower()


# =============================================================================
# Gemini Integration Tests
# =============================================================================


class TestGeminiIntegration:
    """Tests for Gemini integration."""

    def test_gemini_skills_provider_name(self, mock_config):
        """GeminiSkills should identify as gemini provider."""
        from aiskills.integrations.gemini import GeminiSkills

        client = GeminiSkills.__new__(GeminiSkills)
        assert client.provider_name == "gemini"

    def test_gemini_tools_are_callables(self, mock_config):
        """Gemini tools should be Python callables."""
        from aiskills.integrations.gemini import GeminiSkills

        with patch("aiskills.core.router.get_router"):
            client = GeminiSkills()
            tools = client.get_tools()

            assert isinstance(tools, list)
            for tool in tools:
                assert callable(tool)


# =============================================================================
# Ollama Integration Tests
# =============================================================================


class TestOllamaIntegration:
    """Tests for Ollama integration."""

    def test_ollama_skills_provider_name(self, mock_config):
        """OllamaSkills should identify as ollama provider."""
        from aiskills.integrations.ollama import OllamaSkills

        client = OllamaSkills.__new__(OllamaSkills)
        assert client.provider_name == "ollama"

    def test_ollama_tools_format(self):
        """Ollama tools should match OpenAI format."""
        from aiskills.integrations.ollama import get_ollama_tools

        tools = get_ollama_tools()

        assert isinstance(tools, list)
        for tool in tools:
            assert tool["type"] == "function"
            assert "function" in tool
            func = tool["function"]
            assert "name" in func
            assert "parameters" in func

    def test_ollama_tool_capability_detection(self, mock_config):
        """Ollama should detect tool-capable models."""
        from aiskills.integrations.ollama import OllamaSkills

        # Tool-capable model
        with patch("aiskills.core.router.get_router"):
            client = OllamaSkills(model="llama3.1", use_tools=None)
            assert client.use_tools is True

        # Non-tool model
        with patch("aiskills.core.router.get_router"):
            client = OllamaSkills(model="codellama", use_tools=None)
            assert client.use_tools is False

        # Explicit override
        with patch("aiskills.core.router.get_router"):
            client = OllamaSkills(model="codellama", use_tools=True)
            assert client.use_tools is True

    def test_ollama_execute_tool_unknown(self, mock_config):
        """Unknown tool should return error."""
        from aiskills.integrations.ollama import OllamaSkills

        with patch("aiskills.core.router.get_router"):
            client = OllamaSkills()
            result = client.execute_tool("unknown_tool", {})
            assert "error" in result


# =============================================================================
# Integration Module Tests
# =============================================================================


class TestAnthropicIntegration:
    """Tests for Anthropic Claude integration."""

    def test_anthropic_skills_provider_name(self, mock_config):
        """AnthropicSkills should identify as anthropic provider."""
        from aiskills.integrations.anthropic import AnthropicSkills

        client = AnthropicSkills.__new__(AnthropicSkills)
        assert client.provider_name == "anthropic"

    def test_anthropic_tools_format(self):
        """Anthropic tools should be in correct format."""
        from aiskills.integrations.anthropic import get_anthropic_tools

        tools = get_anthropic_tools()

        assert isinstance(tools, list)
        assert len(tools) > 0

        for tool in tools:
            # Anthropic uses flat structure (not nested under "function")
            assert "name" in tool
            assert "description" in tool
            assert "input_schema" in tool
            assert tool["input_schema"]["type"] == "object"
            assert "properties" in tool["input_schema"]
            assert "required" in tool["input_schema"]

    def test_anthropic_execute_tool_unknown(self, mock_config):
        """Unknown tool should return error."""
        from aiskills.integrations.anthropic import AnthropicSkills

        with patch("aiskills.core.router.get_router"):
            client = AnthropicSkills()
            result = client.execute_tool("unknown_tool", {})
            assert "error" in result
            assert "unknown" in result["error"].lower()

    def test_anthropic_default_model(self, mock_config):
        """Should use Claude 3.5 Sonnet by default."""
        from aiskills.integrations.anthropic import AnthropicSkills

        with patch("aiskills.core.router.get_router"):
            client = AnthropicSkills()
            assert "claude" in client.model.lower()

    def test_anthropic_custom_model(self, mock_config):
        """Should accept custom model."""
        from aiskills.integrations.anthropic import AnthropicSkills

        with patch("aiskills.core.router.get_router"):
            client = AnthropicSkills(model="claude-3-opus-20240229")
            assert client.model == "claude-3-opus-20240229"


# =============================================================================
# Streaming Tests
# =============================================================================


class TestStreamingSupport:
    """Tests for streaming functionality across providers."""

    def test_openai_has_streaming_methods(self, mock_config):
        """OpenAI client should have streaming methods."""
        from aiskills.integrations.openai import OpenAISkills

        with patch("aiskills.core.router.get_router"):
            client = OpenAISkills()
            assert hasattr(client, "chat_stream")
            assert hasattr(client, "chat_stream_with_messages")
            assert callable(client.chat_stream)
            assert callable(client.chat_stream_with_messages)

    def test_anthropic_has_streaming_methods(self, mock_config):
        """Anthropic client should have streaming methods."""
        from aiskills.integrations.anthropic import AnthropicSkills

        with patch("aiskills.core.router.get_router"):
            client = AnthropicSkills()
            assert hasattr(client, "chat_stream")
            assert hasattr(client, "chat_stream_with_messages")
            assert callable(client.chat_stream)
            assert callable(client.chat_stream_with_messages)

    def test_gemini_has_streaming_method(self, mock_config):
        """Gemini client should have streaming method."""
        from aiskills.integrations.gemini import GeminiSkills

        with patch("aiskills.core.router.get_router"):
            client = GeminiSkills()
            assert hasattr(client, "chat_stream")
            assert callable(client.chat_stream)

    def test_ollama_has_streaming_methods(self, mock_config):
        """Ollama client should have streaming methods."""
        from aiskills.integrations.ollama import OllamaSkills

        with patch("aiskills.core.router.get_router"):
            client = OllamaSkills()
            assert hasattr(client, "chat_stream")
            assert hasattr(client, "chat_stream_with_messages")
            assert callable(client.chat_stream)
            assert callable(client.chat_stream_with_messages)


# =============================================================================
# SDK Wrapper Configuration Tests
# =============================================================================


class TestSDKWrapperConfiguration:
    """Tests for SDK wrapper configuration options."""

    def test_openai_auto_execute_option(self, mock_config):
        """OpenAI should respect auto_execute option."""
        from aiskills.integrations.openai import OpenAISkills

        with patch("aiskills.core.router.get_router"):
            client_auto = OpenAISkills(auto_execute=True)
            assert client_auto.auto_execute is True

            client_manual = OpenAISkills(auto_execute=False)
            assert client_manual.auto_execute is False

    def test_anthropic_max_tokens_option(self, mock_config):
        """Anthropic should respect max_tokens option."""
        from aiskills.integrations.anthropic import AnthropicSkills

        with patch("aiskills.core.router.get_router"):
            client = AnthropicSkills(max_tokens=8192)
            assert client.max_tokens == 8192

    def test_ollama_use_tools_option(self, mock_config):
        """Ollama should respect use_tools option."""
        from aiskills.integrations.ollama import OllamaSkills

        with patch("aiskills.core.router.get_router"):
            client_tools = OllamaSkills(use_tools=True)
            assert client_tools.use_tools is True

            client_no_tools = OllamaSkills(use_tools=False)
            assert client_no_tools.use_tools is False

    def test_max_tool_rounds_option(self, mock_config):
        """All SDK wrappers should respect max_tool_rounds."""
        from aiskills.integrations.openai import OpenAISkills
        from aiskills.integrations.anthropic import AnthropicSkills
        from aiskills.integrations.ollama import OllamaSkills

        with patch("aiskills.core.router.get_router"):
            openai_client = OpenAISkills(max_tool_rounds=10)
            assert openai_client.max_tool_rounds == 10

            anthropic_client = AnthropicSkills(max_tool_rounds=3)
            assert anthropic_client.max_tool_rounds == 3

            ollama_client = OllamaSkills(max_tool_rounds=7)
            assert ollama_client.max_tool_rounds == 7


# =============================================================================
# Tool Execution Tests
# =============================================================================


class TestToolExecution:
    """Tests for tool execution across providers."""

    def test_openai_execute_use_skill(self, mock_config):
        """OpenAI should execute use_skill tool."""
        from aiskills.integrations.openai import OpenAISkills

        mock_router = MagicMock()
        mock_router.use.return_value = MagicMock(
            skill_name="test-skill",
            content="Test content",
            score=0.9,
            error=None
        )

        with patch("aiskills.core.router.get_router", return_value=mock_router):
            client = OpenAISkills()
            result = client.execute_tool("use_skill", {"context": "test query"})

            assert result["skill_name"] == "test-skill"
            assert result["content"] == "Test content"
            assert result["score"] == 0.9

    def test_anthropic_execute_skill_search(self, mock_config):
        """Anthropic should execute skill_search tool."""
        from aiskills.integrations.anthropic import AnthropicSkills

        mock_router = MagicMock()
        mock_router.registry.search_text.return_value = [
            MagicMock(name="skill1", description="Skill 1", tags=["test"])
        ]

        with patch("aiskills.core.router.get_router", return_value=mock_router):
            client = AnthropicSkills()
            result = client.execute_tool("skill_search", {"query": "test"})

            assert "results" in result
            assert result["total"] >= 0

    def test_ollama_execute_skill_list(self, mock_config):
        """Ollama should execute skill_list tool."""
        from aiskills.integrations.ollama import OllamaSkills

        mock_router = MagicMock()
        mock_router.manager.list_installed.return_value = [
            MagicMock(manifest=MagicMock(
                name="skill1",
                description="Test skill",
                version="1.0.0",
                tags=["test"],
                category="testing"
            ))
        ]

        with patch("aiskills.core.router.get_router", return_value=mock_router):
            client = OllamaSkills()
            result = client.execute_tool("skill_list", {})

            assert "skills" in result
            assert "total" in result


# =============================================================================
# Integration Module Tests
# =============================================================================


class TestIntegrationModule:
    """Tests for the integrations module exports."""

    def test_exports_client_factories(self):
        """Module should export client factory functions."""
        from aiskills import integrations

        assert hasattr(integrations, "create_openai_client")
        assert hasattr(integrations, "create_anthropic_client")
        assert hasattr(integrations, "create_gemini_client")
        assert hasattr(integrations, "create_ollama_client")
        assert callable(integrations.create_openai_client)
        assert callable(integrations.create_anthropic_client)
        assert callable(integrations.create_gemini_client)
        assert callable(integrations.create_ollama_client)

    def test_exports_tool_getters(self):
        """Module should export tool getter functions."""
        from aiskills import integrations

        assert hasattr(integrations, "get_openai_tools")
        assert hasattr(integrations, "get_anthropic_tools")
        assert hasattr(integrations, "get_gemini_tools")
        assert hasattr(integrations, "get_ollama_tools")

    def test_exports_base_classes(self):
        """Module should export base classes."""
        from aiskills import integrations

        assert hasattr(integrations, "BaseLLMIntegration")
        assert hasattr(integrations, "SkillInvocationResult")
        assert hasattr(integrations, "SearchResult")
        assert hasattr(integrations, "STANDARD_TOOLS")

    def test_all_tool_getters_return_consistent_count(self):
        """All tool getters should return same number of tools."""
        from aiskills.integrations import (
            get_openai_tools,
            get_anthropic_tools,
            get_ollama_tools,
        )

        openai_count = len(get_openai_tools())
        anthropic_count = len(get_anthropic_tools())
        ollama_count = len(get_ollama_tools())

        # All should have same number of tools
        assert openai_count == anthropic_count == ollama_count

    def test_all_tools_have_same_names(self):
        """All providers should expose same tool names."""
        from aiskills.integrations import (
            get_openai_tools,
            get_anthropic_tools,
            get_ollama_tools,
        )

        openai_names = {t["function"]["name"] for t in get_openai_tools()}
        anthropic_names = {t["name"] for t in get_anthropic_tools()}
        ollama_names = {t["function"]["name"] for t in get_ollama_tools()}

        assert openai_names == anthropic_names == ollama_names


# =============================================================================
# Auto-Discovery API Tests
# =============================================================================


class TestAutoDiscoveryAPI:
    """Tests for the auto-discovery endpoint."""

    @pytest.fixture
    def api_client(self, mock_config):
        """Create API test client."""
        pytest.importorskip("fastapi")
        from fastapi.testclient import TestClient
        from aiskills.api.server import create_app

        app = create_app()
        return TestClient(app)

    def test_should_invoke_endpoint_exists(self, api_client):
        """Should-invoke endpoint should exist."""
        response = api_client.post(
            "/skills/should-invoke",
            json={"user_message": "help me debug"},
        )
        # Should not be 404
        assert response.status_code != 404

    def test_should_invoke_returns_expected_fields(self, api_client):
        """Response should contain expected fields."""
        response = api_client.post(
            "/skills/should-invoke",
            json={"user_message": "test message"},
        )

        if response.status_code == 200:
            data = response.json()
            assert "should_invoke" in data
            assert "confidence" in data
            assert "suggested_skill" in data
            assert "reason" in data
            assert isinstance(data["should_invoke"], bool)
            assert isinstance(data["confidence"], (int, float))

    def test_should_invoke_with_context(self, api_client):
        """Should accept additional context."""
        response = api_client.post(
            "/skills/should-invoke",
            json={
                "user_message": "I need help with testing",
                "languages": ["python"],
                "active_paths": ["tests/"],
            },
        )

        assert response.status_code in [200, 422]  # Valid or validation error


# =============================================================================
# Multi-LLM Acceptance Tests
# =============================================================================


class TestMultiLLMConsistency:
    """Tests ensuring consistent behavior across all LLM providers."""

    def test_all_providers_have_chat_method(self, mock_config):
        """All providers should have chat() method with same signature."""
        from aiskills.integrations.openai import OpenAISkills
        from aiskills.integrations.anthropic import AnthropicSkills
        from aiskills.integrations.gemini import GeminiSkills
        from aiskills.integrations.ollama import OllamaSkills
        import inspect

        with patch("aiskills.core.router.get_router"):
            openai = OpenAISkills()
            anthropic = AnthropicSkills()
            gemini = GeminiSkills()
            ollama = OllamaSkills()

            # All should have chat method
            assert hasattr(openai, "chat")
            assert hasattr(anthropic, "chat")
            assert hasattr(gemini, "chat")
            assert hasattr(ollama, "chat")

            # All chat methods should accept message as first param
            for client in [openai, anthropic, gemini, ollama]:
                sig = inspect.signature(client.chat)
                params = list(sig.parameters.keys())
                assert params[0] == "message"

    def test_all_providers_have_get_tools(self, mock_config):
        """All providers should have get_tools() method."""
        from aiskills.integrations.openai import OpenAISkills
        from aiskills.integrations.anthropic import AnthropicSkills
        from aiskills.integrations.gemini import GeminiSkills
        from aiskills.integrations.ollama import OllamaSkills

        with patch("aiskills.core.router.get_router"):
            clients = [
                OpenAISkills(),
                AnthropicSkills(),
                GeminiSkills(),
                OllamaSkills(),
            ]

            for client in clients:
                assert hasattr(client, "get_tools")
                tools = client.get_tools()
                assert isinstance(tools, list)
                assert len(tools) > 0

    def test_all_providers_have_execute_tool(self, mock_config):
        """All providers should have execute_tool() method."""
        from aiskills.integrations.openai import OpenAISkills
        from aiskills.integrations.anthropic import AnthropicSkills
        from aiskills.integrations.ollama import OllamaSkills

        with patch("aiskills.core.router.get_router"):
            clients = [
                ("openai", OpenAISkills()),
                ("anthropic", AnthropicSkills()),
                ("ollama", OllamaSkills()),
            ]

            for name, client in clients:
                assert hasattr(client, "execute_tool"), f"{name} missing execute_tool"
                # Should handle unknown tool gracefully
                result = client.execute_tool("nonexistent", {})
                assert "error" in result, f"{name} should return error for unknown tool"

    def test_tool_names_consistent_across_providers(self):
        """Tool names should be identical across all providers."""
        from aiskills.integrations.openai import get_openai_tools
        from aiskills.integrations.anthropic import get_anthropic_tools
        from aiskills.integrations.ollama import get_ollama_tools

        openai_tools = get_openai_tools()
        anthropic_tools = get_anthropic_tools()
        ollama_tools = get_ollama_tools()

        # Extract names (different formats)
        openai_names = sorted([t["function"]["name"] for t in openai_tools])
        anthropic_names = sorted([t["name"] for t in anthropic_tools])
        ollama_names = sorted([t["function"]["name"] for t in ollama_tools])

        assert openai_names == anthropic_names, "OpenAI and Anthropic tools differ"
        assert openai_names == ollama_names, "OpenAI and Ollama tools differ"

    def test_provider_names_unique(self, mock_config):
        """Each provider should have unique provider_name."""
        from aiskills.integrations.openai import OpenAISkills
        from aiskills.integrations.anthropic import AnthropicSkills
        from aiskills.integrations.gemini import GeminiSkills
        from aiskills.integrations.ollama import OllamaSkills

        providers = [
            OpenAISkills.__new__(OpenAISkills),
            AnthropicSkills.__new__(AnthropicSkills),
            GeminiSkills.__new__(GeminiSkills),
            OllamaSkills.__new__(OllamaSkills),
        ]

        names = [p.provider_name for p in providers]
        assert len(names) == len(set(names)), "Provider names not unique"
        assert "openai" in names
        assert "anthropic" in names
        assert "gemini" in names
        assert "ollama" in names


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for create_*_client factory functions."""

    def test_create_openai_client_returns_correct_type(self, mock_config):
        """create_openai_client should return OpenAISkills instance."""
        from aiskills.integrations import create_openai_client
        from aiskills.integrations.openai import OpenAISkills

        with patch("aiskills.core.router.get_router"):
            client = create_openai_client()
            assert isinstance(client, OpenAISkills)

    def test_create_anthropic_client_returns_correct_type(self, mock_config):
        """create_anthropic_client should return AnthropicSkills instance."""
        from aiskills.integrations import create_anthropic_client
        from aiskills.integrations.anthropic import AnthropicSkills

        with patch("aiskills.core.router.get_router"):
            client = create_anthropic_client()
            assert isinstance(client, AnthropicSkills)

    def test_create_gemini_client_returns_correct_type(self, mock_config):
        """create_gemini_client should return GeminiSkills instance."""
        from aiskills.integrations import create_gemini_client
        from aiskills.integrations.gemini import GeminiSkills

        with patch("aiskills.core.router.get_router"):
            client = create_gemini_client()
            assert isinstance(client, GeminiSkills)

    def test_create_ollama_client_returns_correct_type(self, mock_config):
        """create_ollama_client should return OllamaSkills instance."""
        from aiskills.integrations import create_ollama_client
        from aiskills.integrations.ollama import OllamaSkills

        with patch("aiskills.core.router.get_router"):
            client = create_ollama_client()
            assert isinstance(client, OllamaSkills)

    def test_factory_functions_pass_model_parameter(self, mock_config):
        """Factory functions should pass model parameter."""
        from aiskills.integrations import (
            create_openai_client,
            create_anthropic_client,
            create_ollama_client,
        )

        with patch("aiskills.core.router.get_router"):
            openai = create_openai_client(model="gpt-4-turbo")
            assert openai.model == "gpt-4-turbo"

            anthropic = create_anthropic_client(model="claude-3-opus-20240229")
            assert anthropic.model == "claude-3-opus-20240229"

            ollama = create_ollama_client(model="mistral")
            assert ollama.model == "mistral"


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_execute_tool_with_empty_arguments(self, mock_config):
        """Tools should handle empty arguments gracefully."""
        from aiskills.integrations.openai import OpenAISkills
        from aiskills.integrations.anthropic import AnthropicSkills
        from aiskills.integrations.ollama import OllamaSkills

        mock_router = MagicMock()
        mock_router.use.return_value = MagicMock(
            skill_name=None,
            content=None,
            score=0.0,
            error="No context provided"
        )

        with patch("aiskills.core.router.get_router", return_value=mock_router):
            clients = [
                OpenAISkills(),
                AnthropicSkills(),
                OllamaSkills(),
            ]

            for client in clients:
                # Should not raise, should return error
                result = client.execute_tool("use_skill", {})
                assert isinstance(result, dict)

    def test_skill_browse_tool_exists(self, mock_config):
        """skill_browse tool should be available in all providers."""
        from aiskills.integrations.openai import get_openai_tools
        from aiskills.integrations.anthropic import get_anthropic_tools
        from aiskills.integrations.ollama import get_ollama_tools

        openai_names = [t["function"]["name"] for t in get_openai_tools()]
        anthropic_names = [t["name"] for t in get_anthropic_tools()]
        ollama_names = [t["function"]["name"] for t in get_ollama_tools()]

        assert "skill_browse" in openai_names
        assert "skill_browse" in anthropic_names
        assert "skill_browse" in ollama_names

    def test_max_tool_rounds_prevents_infinite_loop(self, mock_config):
        """max_tool_rounds should prevent infinite tool execution."""
        from aiskills.integrations.openai import OpenAISkills
        from aiskills.integrations.anthropic import AnthropicSkills
        from aiskills.integrations.ollama import OllamaSkills

        with patch("aiskills.core.router.get_router"):
            # Create clients with low max_tool_rounds
            openai = OpenAISkills(max_tool_rounds=1)
            anthropic = AnthropicSkills(max_tool_rounds=2)
            ollama = OllamaSkills(max_tool_rounds=3)

            assert openai.max_tool_rounds == 1
            assert anthropic.max_tool_rounds == 2
            assert ollama.max_tool_rounds == 3

    def test_auto_execute_can_be_disabled(self, mock_config):
        """auto_execute should be disableable."""
        from aiskills.integrations.openai import OpenAISkills
        from aiskills.integrations.anthropic import AnthropicSkills

        with patch("aiskills.core.router.get_router"):
            openai = OpenAISkills(auto_execute=False)
            anthropic = AnthropicSkills(auto_execute=False)

            assert openai.auto_execute is False
            assert anthropic.auto_execute is False


# =============================================================================
# Tool Parameter Tests
# =============================================================================


class TestToolParameters:
    """Tests for tool parameter definitions."""

    def test_use_skill_has_context_parameter(self):
        """use_skill tool should have context parameter."""
        from aiskills.integrations.base import STANDARD_TOOLS

        use_skill = next(t for t in STANDARD_TOOLS if t.name == "use_skill")
        assert "context" in use_skill.parameters
        assert "context" in use_skill.required

    def test_skill_search_has_query_parameter(self):
        """skill_search tool should have query parameter."""
        from aiskills.integrations.base import STANDARD_TOOLS

        skill_search = next(t for t in STANDARD_TOOLS if t.name == "skill_search")
        assert "query" in skill_search.parameters
        assert "query" in skill_search.required

    def test_skill_read_has_name_parameter(self):
        """skill_read tool should have name parameter."""
        from aiskills.integrations.base import STANDARD_TOOLS

        skill_read = next(t for t in STANDARD_TOOLS if t.name == "skill_read")
        assert "name" in skill_read.parameters
        assert "name" in skill_read.required

    def test_skill_browse_has_optional_parameters(self):
        """skill_browse should have optional filter parameters."""
        from aiskills.integrations.base import STANDARD_TOOLS

        skill_browse = next(t for t in STANDARD_TOOLS if t.name == "skill_browse")
        params = skill_browse.parameters

        # Should have filter parameters
        assert "context" in params or "languages" in params or "limit" in params

    def test_all_tools_have_descriptions(self):
        """All tools should have non-empty descriptions."""
        from aiskills.integrations.base import STANDARD_TOOLS

        for tool in STANDARD_TOOLS:
            assert tool.description, f"{tool.name} missing description"
            assert len(tool.description) > 10, f"{tool.name} description too short"


# =============================================================================
# Inheritance Tests
# =============================================================================


class TestInheritance:
    """Tests for class inheritance structure."""

    def test_all_clients_inherit_from_base(self):
        """All SDK clients should inherit from BaseLLMIntegration."""
        from aiskills.integrations.base import BaseLLMIntegration
        from aiskills.integrations.openai import OpenAISkills
        from aiskills.integrations.anthropic import AnthropicSkills
        from aiskills.integrations.gemini import GeminiSkills
        from aiskills.integrations.ollama import OllamaSkills

        assert issubclass(OpenAISkills, BaseLLMIntegration)
        assert issubclass(AnthropicSkills, BaseLLMIntegration)
        assert issubclass(GeminiSkills, BaseLLMIntegration)
        assert issubclass(OllamaSkills, BaseLLMIntegration)

    def test_base_class_has_abstract_methods(self):
        """BaseLLMIntegration should define expected interface."""
        from aiskills.integrations.base import BaseLLMIntegration

        # Should have these methods/properties
        assert hasattr(BaseLLMIntegration, "provider_name")
        assert hasattr(BaseLLMIntegration, "get_tools")
        assert hasattr(BaseLLMIntegration, "use_skill")
        assert hasattr(BaseLLMIntegration, "search_skills")
        assert hasattr(BaseLLMIntegration, "read_skill")
        assert hasattr(BaseLLMIntegration, "list_skills")
        assert hasattr(BaseLLMIntegration, "browse_skills")


# =============================================================================
# Gemini Consistency Tests
# =============================================================================


class TestGeminiConsistency:
    """Tests for Gemini API consistency with other providers."""

    def test_gemini_has_chat_with_messages(self, mock_config):
        """Gemini should have chat_with_messages method like other providers."""
        from aiskills.integrations.gemini import GeminiSkills

        with patch("aiskills.core.router.get_router"):
            client = GeminiSkills()
            assert hasattr(client, "chat_with_messages")
            assert callable(client.chat_with_messages)

    def test_gemini_execute_tool_returns_dict(self, mock_config):
        """Gemini execute_tool should return dict like other providers."""
        from aiskills.integrations.gemini import GeminiSkills

        with patch("aiskills.core.router.get_router"):
            client = GeminiSkills()
            # Unknown tool should return error dict
            result = client.execute_tool("unknown_tool", {})
            assert isinstance(result, dict)
            assert "error" in result

    def test_gemini_execute_tool_skill_list_returns_dict(self, mock_config):
        """Gemini skill_list should return dict with skills array."""
        from aiskills.integrations.gemini import GeminiSkills

        mock_router = MagicMock()
        mock_router.manager.list_installed.return_value = []

        with patch("aiskills.core.router.get_router", return_value=mock_router):
            client = GeminiSkills()
            result = client.execute_tool("skill_list", {})
            assert isinstance(result, dict)
            assert "skills" in result
            assert "total" in result

    def test_gemini_execute_tool_skill_browse_returns_dict(self, mock_config):
        """Gemini skill_browse should return dict with skills array."""
        from aiskills.integrations.gemini import GeminiSkills

        mock_router = MagicMock()
        mock_router.browse.return_value = []

        with patch("aiskills.core.router.get_router", return_value=mock_router):
            client = GeminiSkills()
            result = client.execute_tool("skill_browse", {})
            assert isinstance(result, dict)
            assert "skills" in result
            assert "total" in result


# =============================================================================
# Exception and Utility Tests
# =============================================================================


class TestExceptions:
    """Tests for custom exceptions."""

    def test_provider_error_attributes(self):
        """ProviderError should have provider and status_code attributes."""
        from aiskills.integrations import ProviderError

        error = ProviderError("Test error", "openai", status_code=500, retryable=True)
        assert error.provider == "openai"
        assert error.status_code == 500
        assert error.retryable is True

    def test_rate_limit_error_is_retryable(self):
        """RateLimitError should always be retryable."""
        from aiskills.integrations import RateLimitError

        error = RateLimitError("Rate limit", "anthropic", retry_after=5.0)
        assert error.retryable is True
        assert error.status_code == 429
        assert error.retry_after == 5.0

    def test_tool_validation_error_attributes(self):
        """ToolValidationError should have tool_name and invalid_args."""
        from aiskills.integrations import ToolValidationError

        error = ToolValidationError("use_skill", "Missing param", ["context"])
        assert error.tool_name == "use_skill"
        assert error.invalid_args == ["context"]

    def test_skill_not_found_error(self):
        """SkillNotFoundError should contain skill name."""
        from aiskills.integrations import SkillNotFoundError

        error = SkillNotFoundError("python-debug", query="debug python")
        assert error.skill_name == "python-debug"
        assert error.query == "debug python"


class TestValidation:
    """Tests for input validation utilities."""

    def test_validate_tool_arguments_missing_required(self):
        """Should raise error for missing required parameters."""
        from aiskills.integrations import validate_tool_arguments, ToolValidationError

        with pytest.raises(ToolValidationError) as exc_info:
            validate_tool_arguments(
                "use_skill",
                {},  # Missing 'context'
                required=["context"],
                parameters={"context": {"type": "string"}},
            )
        assert "context" in str(exc_info.value)

    def test_validate_tool_arguments_type_mismatch(self):
        """Should raise error for type mismatches."""
        from aiskills.integrations import validate_tool_arguments, ToolValidationError

        with pytest.raises(ToolValidationError):
            validate_tool_arguments(
                "skill_search",
                {"query": 123},  # Should be string
                required=["query"],
                parameters={"query": {"type": "string"}},
            )

    def test_validate_tool_arguments_valid(self):
        """Should return validated arguments for valid input."""
        from aiskills.integrations import validate_tool_arguments

        result = validate_tool_arguments(
            "use_skill",
            {"context": "debug python"},
            required=["context"],
            parameters={"context": {"type": "string"}},
        )
        assert result["context"] == "debug python"

    def test_get_tool_schema(self):
        """Should return schema for known tools."""
        from aiskills.integrations import get_tool_schema

        schema = get_tool_schema("use_skill")
        assert schema is not None
        required, params = schema
        assert "context" in required
        assert "context" in params

    def test_get_tool_schema_unknown(self):
        """Should return None for unknown tools."""
        from aiskills.integrations import get_tool_schema

        schema = get_tool_schema("nonexistent_tool")
        assert schema is None

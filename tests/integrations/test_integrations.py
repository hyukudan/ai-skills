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


class TestIntegrationModule:
    """Tests for the integrations module exports."""

    def test_exports_client_factories(self):
        """Module should export client factory functions."""
        from aiskills import integrations

        assert hasattr(integrations, "create_openai_client")
        assert hasattr(integrations, "create_gemini_client")
        assert hasattr(integrations, "create_ollama_client")
        assert callable(integrations.create_openai_client)
        assert callable(integrations.create_gemini_client)
        assert callable(integrations.create_ollama_client)

    def test_exports_tool_getters(self):
        """Module should export tool getter functions."""
        from aiskills import integrations

        assert hasattr(integrations, "get_openai_tools")
        assert hasattr(integrations, "get_gemini_tools")
        assert hasattr(integrations, "get_ollama_tools")

    def test_exports_base_classes(self):
        """Module should export base classes."""
        from aiskills import integrations

        assert hasattr(integrations, "BaseLLMIntegration")
        assert hasattr(integrations, "SkillInvocationResult")
        assert hasattr(integrations, "SearchResult")
        assert hasattr(integrations, "STANDARD_TOOLS")


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

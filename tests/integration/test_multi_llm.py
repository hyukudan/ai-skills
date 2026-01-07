"""Multi-LLM Acceptance Tests for aiskills.

These tests validate that skills produce consistent behavior across different
LLM providers and integration interfaces:
- Claude MCP (Model Context Protocol)
- OpenAI Function Calling (via REST API)
- Gemini Function Calling (simulated format)
- Ollama Local Server (Python SDK)

The goal is to ensure no provider-specific bias and consistent skill behavior.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pytest


# =============================================================================
# Abstract LLM Client Interface
# =============================================================================


@dataclass
class SkillResult:
    """Unified result from skill operations across providers."""

    skill_name: str | None
    content: str | None
    score: float | None
    error: str | None = None
    raw_response: dict[str, Any] | None = None


@dataclass
class SearchResult:
    """Unified search result across providers."""

    results: list[dict[str, Any]]
    total: int
    query: str
    search_type: str


class BaseLLMClient(ABC):
    """Abstract base class for LLM provider clients."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Return the provider name."""
        ...

    @abstractmethod
    def use_skill(self, context: str, variables: dict[str, Any] | None = None) -> SkillResult:
        """Use a skill with the given context."""
        ...

    @abstractmethod
    def search_skills(self, query: str, limit: int = 10) -> SearchResult:
        """Search for skills."""
        ...

    @abstractmethod
    def read_skill(self, name: str, variables: dict[str, Any] | None = None) -> SkillResult:
        """Read a specific skill by name."""
        ...

    @abstractmethod
    def list_skills(self) -> list[dict[str, Any]]:
        """List all available skills."""
        ...


# =============================================================================
# Claude MCP Client
# =============================================================================


class ClaudeMCPClient(BaseLLMClient):
    """Client that simulates Claude MCP tool calls."""

    def __init__(self, manager, router, registry):
        self.manager = manager
        self.router = router
        self.registry = registry

    @property
    def provider_name(self) -> str:
        return "claude_mcp"

    def use_skill(self, context: str, variables: dict[str, Any] | None = None) -> SkillResult:
        """Simulate MCP use_skill tool call."""
        try:
            result = self.router.use(context=context, variables=variables or {})
            return SkillResult(
                skill_name=result.skill_name,
                content=result.content,
                score=result.score,
                raw_response={"matched_query": result.matched_query},
            )
        except Exception as e:
            return SkillResult(
                skill_name=None,
                content=None,
                score=None,
                error=str(e),
            )

    def search_skills(self, query: str, limit: int = 10) -> SearchResult:
        """Simulate MCP skill_search tool call."""
        results = self.registry.search_text(query, limit=limit)
        return SearchResult(
            results=[
                {
                    "name": idx.name,
                    "version": idx.version,
                    "description": idx.description,
                    "tags": idx.tags,
                    "category": idx.category,
                }
                for idx in results
            ],
            total=len(results),
            query=query,
            search_type="text",
        )

    def read_skill(self, name: str, variables: dict[str, Any] | None = None) -> SkillResult:
        """Simulate MCP skill_read tool call."""
        try:
            content = self.manager.read(name, variables=variables)
            skill = self.manager.get(name)
            return SkillResult(
                skill_name=name,
                content=content,
                score=1.0,
                raw_response={
                    "version": skill.manifest.version if skill else None,
                    "tags": skill.manifest.tags if skill else [],
                },
            )
        except Exception as e:
            return SkillResult(
                skill_name=name,
                content=None,
                score=None,
                error=str(e),
            )

    def list_skills(self) -> list[dict[str, Any]]:
        """Simulate MCP skill_list tool call."""
        skills = self.manager.list_installed()
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


# =============================================================================
# OpenAI Function Calling Client
# =============================================================================


class OpenAIFunctionClient(BaseLLMClient):
    """Client that uses OpenAI-compatible function calling format."""

    def __init__(self, test_client):
        """Initialize with FastAPI test client."""
        self.client = test_client

    @property
    def provider_name(self) -> str:
        return "openai_functions"

    def _call_function(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Make an OpenAI-style function call via REST API."""
        response = self.client.post(
            "/openai/call",
            json={"name": name, "arguments": arguments},
        )
        data = response.json()

        # OpenAI format returns content as JSON string
        if "content" in data:
            try:
                return json.loads(data["content"])
            except (json.JSONDecodeError, TypeError):
                return {"error": data["content"]}
        return data

    def use_skill(self, context: str, variables: dict[str, Any] | None = None) -> SkillResult:
        """Use skill via OpenAI function calling."""
        args = {"context": context}
        if variables:
            args["variables"] = variables

        result = self._call_function("use_skill", args)

        if "error" in result:
            return SkillResult(
                skill_name=None,
                content=None,
                score=None,
                error=result["error"],
            )

        return SkillResult(
            skill_name=result.get("skill_name"),
            content=result.get("content"),
            score=result.get("score"),
            raw_response=result,
        )

    def search_skills(self, query: str, limit: int = 10) -> SearchResult:
        """Search skills via OpenAI function calling."""
        result = self._call_function(
            "skill_search",
            {"query": query, "limit": limit, "text_only": True},
        )

        return SearchResult(
            results=result.get("results", []),
            total=result.get("total", 0),
            query=query,
            search_type=result.get("type", "text"),
        )

    def read_skill(self, name: str, variables: dict[str, Any] | None = None) -> SkillResult:
        """Read skill via OpenAI function calling."""
        args = {"name": name}
        if variables:
            args["variables"] = variables

        result = self._call_function("skill_read", args)

        if "error" in result:
            return SkillResult(
                skill_name=name,
                content=None,
                score=None,
                error=result["error"],
            )

        return SkillResult(
            skill_name=name,
            content=result.get("content"),
            score=1.0,
            raw_response=result,
        )

    def list_skills(self) -> list[dict[str, Any]]:
        """List skills via OpenAI function calling."""
        result = self._call_function("skill_list", {})
        return result.get("skills", [])


# =============================================================================
# Gemini Function Calling Client (Simulated)
# =============================================================================


class GeminiFunctionClient(BaseLLMClient):
    """Client that simulates Gemini function calling format.

    Gemini uses a similar function calling format to OpenAI but with
    different request/response structures. This client validates that
    our skill system can be adapted to Gemini's format.
    """

    def __init__(self, manager, router, registry):
        self.manager = manager
        self.router = router
        self.registry = registry

    @property
    def provider_name(self) -> str:
        return "gemini_functions"

    def _simulate_gemini_call(self, name: str, args: dict[str, Any]) -> dict[str, Any]:
        """Simulate Gemini function call format.

        Gemini format:
        Request: {"functionCall": {"name": "...", "args": {...}}}
        Response: {"functionResponse": {"name": "...", "response": {...}}}
        """
        # Convert to internal call
        if name == "use_skill":
            result = self.router.use(
                context=args.get("context", ""),
                variables=args.get("variables", {}),
            )
            return {
                "functionResponse": {
                    "name": name,
                    "response": {
                        "skill_name": result.skill_name,
                        "content": result.content,
                        "score": result.score,
                    },
                }
            }
        elif name == "search_skills":
            results = self.registry.search_text(
                args.get("query", ""),
                limit=args.get("limit", 10),
            )
            return {
                "functionResponse": {
                    "name": name,
                    "response": {
                        "results": [
                            {"name": idx.name, "description": idx.description}
                            for idx in results
                        ],
                        "total": len(results),
                    },
                }
            }
        elif name == "read_skill":
            content = self.manager.read(
                args.get("name", ""),
                variables=args.get("variables"),
            )
            return {
                "functionResponse": {
                    "name": name,
                    "response": {"name": args.get("name"), "content": content},
                }
            }
        elif name == "list_skills":
            skills = self.manager.list_installed()
            return {
                "functionResponse": {
                    "name": name,
                    "response": {
                        "skills": [
                            {"name": s.manifest.name, "description": s.manifest.description}
                            for s in skills
                        ],
                    },
                }
            }
        return {"error": f"Unknown function: {name}"}

    def use_skill(self, context: str, variables: dict[str, Any] | None = None) -> SkillResult:
        """Use skill via Gemini function calling simulation."""
        response = self._simulate_gemini_call(
            "use_skill",
            {"context": context, "variables": variables or {}},
        )

        if "error" in response:
            return SkillResult(
                skill_name=None,
                content=None,
                score=None,
                error=response["error"],
            )

        data = response["functionResponse"]["response"]
        return SkillResult(
            skill_name=data.get("skill_name"),
            content=data.get("content"),
            score=data.get("score"),
            raw_response=response,
        )

    def search_skills(self, query: str, limit: int = 10) -> SearchResult:
        """Search skills via Gemini function calling simulation."""
        response = self._simulate_gemini_call(
            "search_skills",
            {"query": query, "limit": limit},
        )

        data = response["functionResponse"]["response"]
        return SearchResult(
            results=data.get("results", []),
            total=data.get("total", 0),
            query=query,
            search_type="text",
        )

    def read_skill(self, name: str, variables: dict[str, Any] | None = None) -> SkillResult:
        """Read skill via Gemini function calling simulation."""
        try:
            response = self._simulate_gemini_call(
                "read_skill",
                {"name": name, "variables": variables},
            )

            data = response["functionResponse"]["response"]
            return SkillResult(
                skill_name=name,
                content=data.get("content"),
                score=1.0,
                raw_response=response,
            )
        except Exception as e:
            return SkillResult(
                skill_name=name,
                content=None,
                score=None,
                error=str(e),
            )

    def list_skills(self) -> list[dict[str, Any]]:
        """List skills via Gemini function calling simulation."""
        response = self._simulate_gemini_call("list_skills", {})
        return response["functionResponse"]["response"].get("skills", [])


# =============================================================================
# Ollama Local Client (Python SDK simulation)
# =============================================================================


class OllamaLocalClient(BaseLLMClient):
    """Client that simulates Ollama local server usage via Python SDK.

    Ollama typically exposes skills through direct Python SDK calls,
    without going through HTTP APIs. This tests the direct integration path.
    """

    def __init__(self, manager, router, registry):
        self.manager = manager
        self.router = router
        self.registry = registry

    @property
    def provider_name(self) -> str:
        return "ollama_local"

    def use_skill(self, context: str, variables: dict[str, Any] | None = None) -> SkillResult:
        """Direct Python SDK skill usage."""
        try:
            # Direct router call - simulating how Ollama would integrate
            result = self.router.use(
                context=context,
                variables=variables or {},
            )
            return SkillResult(
                skill_name=result.skill_name,
                content=result.content,
                score=result.score,
                raw_response={"tokens_used": result.tokens_used},
            )
        except Exception as e:
            return SkillResult(
                skill_name=None,
                content=None,
                score=None,
                error=str(e),
            )

    def search_skills(self, query: str, limit: int = 10) -> SearchResult:
        """Direct Python SDK search."""
        results = self.registry.search_text(query, limit=limit)
        return SearchResult(
            results=[
                {
                    "name": idx.name,
                    "description": idx.description,
                    "tags": idx.tags,
                }
                for idx in results
            ],
            total=len(results),
            query=query,
            search_type="text",
        )

    def read_skill(self, name: str, variables: dict[str, Any] | None = None) -> SkillResult:
        """Direct Python SDK read."""
        try:
            content = self.manager.read(name, variables=variables)
            return SkillResult(
                skill_name=name,
                content=content,
                score=1.0,
            )
        except Exception as e:
            return SkillResult(
                skill_name=name,
                content=None,
                score=None,
                error=str(e),
            )

    def list_skills(self) -> list[dict[str, Any]]:
        """Direct Python SDK list."""
        skills = self.manager.list_installed()
        return [
            {
                "name": s.manifest.name,
                "description": s.manifest.description,
            }
            for s in skills
        ]


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def multi_llm_skill_content() -> str:
    """Skill specifically designed for multi-LLM testing."""
    return """\
---
name: multi-llm-test-skill
description: A skill for testing cross-LLM compatibility.
version: 1.0.0
tags: [test, multi-llm, compatibility]
category: testing
variables:
  greeting:
    type: string
    default: Hello
  target:
    type: string
    default: World
---

# {{ greeting }}, {{ target }}!

This skill tests cross-LLM compatibility.

## Instructions

When invoked, return the greeting followed by the target.

## Expected Behavior

All LLM providers should:
1. Load this skill successfully
2. Apply variables correctly
3. Return consistent content
"""


@pytest.fixture
def multi_llm_setup(tmp_path, multi_llm_skill_content, simple_skill_content, skill_with_variables_content, monkeypatch):
    """Set up environment for multi-LLM testing."""
    from aiskills.config import AppConfig, StorageConfig, EmbeddingConfig, VectorStoreConfig, set_config
    from aiskills.core import manager as manager_module
    from aiskills.core import registry as registry_module
    from aiskills.storage import paths as paths_module

    # Set up directories
    global_dir = tmp_path / "global"
    global_skills = global_dir / "skills"
    global_skills.mkdir(parents=True)

    project_dir = tmp_path / "project"
    project_skills = project_dir / ".aiskills" / "skills"
    project_skills.mkdir(parents=True)

    # Create test skills
    skills_data = [
        ("multi-llm-test-skill", multi_llm_skill_content),
        ("simple-skill", simple_skill_content),
        ("skill-with-variables", skill_with_variables_content),
    ]

    for name, content in skills_data:
        skill_dir = project_skills / name
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(content)

    # Configure
    config = AppConfig(
        storage=StorageConfig(global_dir=global_dir),
        embedding=EmbeddingConfig(provider="none"),
        vector_store=VectorStoreConfig(provider="none"),
    )
    set_config(config)

    # Reset singletons
    manager_module._manager = None
    paths_module._resolver = None
    if hasattr(registry_module, '_registry'):
        registry_module._registry = None

    monkeypatch.chdir(project_dir)

    # Import after setup
    from aiskills.core.manager import get_manager
    from aiskills.core.router import get_router
    from aiskills.core.registry import get_registry

    return {
        "manager": get_manager(),
        "router": get_router(),
        "registry": get_registry(),
        "project_dir": project_dir,
    }


@pytest.fixture
def claude_mcp_client(multi_llm_setup) -> ClaudeMCPClient:
    """Create Claude MCP client."""
    return ClaudeMCPClient(
        manager=multi_llm_setup["manager"],
        router=multi_llm_setup["router"],
        registry=multi_llm_setup["registry"],
    )


@pytest.fixture
def openai_client(multi_llm_setup):
    """Create OpenAI function calling client."""
    pytest.importorskip("fastapi")
    from fastapi.testclient import TestClient
    from aiskills.api.server import create_app

    app = create_app()
    test_client = TestClient(app)
    return OpenAIFunctionClient(test_client)


@pytest.fixture
def gemini_client(multi_llm_setup) -> GeminiFunctionClient:
    """Create Gemini function calling client."""
    return GeminiFunctionClient(
        manager=multi_llm_setup["manager"],
        router=multi_llm_setup["router"],
        registry=multi_llm_setup["registry"],
    )


@pytest.fixture
def ollama_client(multi_llm_setup) -> OllamaLocalClient:
    """Create Ollama local client."""
    return OllamaLocalClient(
        manager=multi_llm_setup["manager"],
        router=multi_llm_setup["router"],
        registry=multi_llm_setup["registry"],
    )


@pytest.fixture
def all_clients(claude_mcp_client, openai_client, gemini_client, ollama_client) -> list[BaseLLMClient]:
    """Return all LLM clients for cross-provider testing."""
    return [claude_mcp_client, openai_client, gemini_client, ollama_client]


# =============================================================================
# Cross-Provider Acceptance Tests
# =============================================================================


class TestCrossProviderConsistency:
    """Tests that verify consistent behavior across all LLM providers."""

    def test_all_providers_can_list_skills(self, all_clients):
        """All providers should list the same skills."""
        results = {}

        for client in all_clients:
            skills = client.list_skills()
            results[client.provider_name] = {s["name"] for s in skills}

        # All providers should have the same skills
        first_provider = list(results.keys())[0]
        expected_skills = results[first_provider]

        for provider, skills in results.items():
            assert skills == expected_skills, (
                f"Provider {provider} has different skills than {first_provider}. "
                f"Missing: {expected_skills - skills}, Extra: {skills - expected_skills}"
            )

    def test_all_providers_can_read_same_skill(self, all_clients):
        """All providers should read the same skill content."""
        skill_name = "simple-skill"
        contents = {}

        for client in all_clients:
            result = client.read_skill(skill_name)
            assert result.error is None, f"{client.provider_name} failed: {result.error}"
            assert result.content is not None, f"{client.provider_name} returned no content"
            contents[client.provider_name] = result.content

        # All providers should return equivalent content
        first_provider = list(contents.keys())[0]
        expected_content = contents[first_provider]

        for provider, content in contents.items():
            # Normalize whitespace for comparison
            normalized_expected = " ".join(expected_content.split())
            normalized_actual = " ".join(content.split())
            assert normalized_actual == normalized_expected, (
                f"Provider {provider} returned different content than {first_provider}"
            )

    def test_all_providers_apply_variables_consistently(self, all_clients):
        """All providers should apply template variables the same way."""
        skill_name = "multi-llm-test-skill"
        variables = {"greeting": "Hola", "target": "Mundo"}

        for client in all_clients:
            result = client.read_skill(skill_name, variables=variables)
            assert result.error is None, f"{client.provider_name} failed: {result.error}"
            assert result.content is not None, f"{client.provider_name} returned no content"

            # All should contain the rendered variables
            assert "Hola" in result.content, (
                f"{client.provider_name} did not apply 'greeting' variable"
            )
            assert "Mundo" in result.content, (
                f"{client.provider_name} did not apply 'target' variable"
            )

    def test_all_providers_search_returns_results(self, all_clients):
        """All providers should return search results for the same query."""
        query = "test"

        for client in all_clients:
            result = client.search_skills(query, limit=10)
            assert result.total > 0, (
                f"{client.provider_name} returned no results for '{query}'"
            )
            assert len(result.results) > 0, (
                f"{client.provider_name} has total but empty results"
            )

    def test_all_providers_handle_missing_skill_gracefully(self, all_clients):
        """All providers should handle missing skills without crashing."""
        for client in all_clients:
            result = client.read_skill("nonexistent-skill-xyz")
            # Should either return error or empty content, not crash
            assert result.error is not None or result.content is None, (
                f"{client.provider_name} should handle missing skill gracefully"
            )


class TestClaudeMCPIntegration:
    """Tests specific to Claude MCP integration."""

    def test_mcp_use_skill(self, claude_mcp_client):
        """MCP should successfully use skills via context."""
        result = claude_mcp_client.use_skill("I need help with testing")
        assert result.skill_name is not None
        assert result.content is not None

    def test_mcp_skill_with_variables(self, claude_mcp_client):
        """MCP should apply variables when using skills."""
        result = claude_mcp_client.read_skill(
            "skill-with-variables",
            variables={"language": "rust"},
        )
        assert result.content is not None
        assert "rust" in result.content.lower()

    def test_mcp_returns_metadata(self, claude_mcp_client):
        """MCP should include skill metadata in responses."""
        result = claude_mcp_client.read_skill("simple-skill")
        assert result.raw_response is not None
        assert "version" in result.raw_response


class TestOpenAIFunctionCalling:
    """Tests specific to OpenAI function calling integration."""

    def test_openai_tool_definitions(self, multi_llm_setup):
        """OpenAI tools endpoint should return valid tool definitions."""
        pytest.importorskip("fastapi")
        from fastapi.testclient import TestClient
        from aiskills.api.server import create_app

        app = create_app()
        client = TestClient(app)

        response = client.get("/openai/tools")
        assert response.status_code == 200

        data = response.json()
        assert "tools" in data

        # Validate tool structure matches OpenAI format
        for tool in data["tools"]:
            assert tool["type"] == "function"
            assert "function" in tool
            func = tool["function"]
            assert "name" in func
            assert "description" in func
            assert "parameters" in func
            assert func["parameters"]["type"] == "object"

    def test_openai_use_skill(self, openai_client):
        """OpenAI function calling should use skills correctly."""
        result = openai_client.use_skill("help with simple tasks")
        assert result.skill_name is not None or result.error is None

    def test_openai_handles_all_functions(self, openai_client):
        """All OpenAI-compatible functions should work."""
        # skill_list
        skills = openai_client.list_skills()
        assert isinstance(skills, list)

        # skill_search
        search = openai_client.search_skills("test")
        assert isinstance(search.results, list)

        # skill_read
        result = openai_client.read_skill("simple-skill")
        assert result.content is not None


class TestGeminiFunctionCalling:
    """Tests specific to Gemini function calling format."""

    def test_gemini_response_format(self, gemini_client):
        """Gemini should use correct functionResponse format."""
        result = gemini_client.read_skill("simple-skill")

        # Check that raw response follows Gemini format
        assert result.raw_response is not None
        assert "functionResponse" in result.raw_response
        assert "name" in result.raw_response["functionResponse"]
        assert "response" in result.raw_response["functionResponse"]

    def test_gemini_use_skill(self, gemini_client):
        """Gemini function calling should use skills correctly."""
        result = gemini_client.use_skill("I need testing help")
        assert result.skill_name is not None
        assert result.content is not None

    def test_gemini_variables(self, gemini_client):
        """Gemini should handle template variables."""
        result = gemini_client.read_skill(
            "multi-llm-test-skill",
            variables={"greeting": "Bonjour", "target": "Monde"},
        )
        assert "Bonjour" in result.content
        assert "Monde" in result.content


class TestOllamaLocalIntegration:
    """Tests specific to Ollama local server integration."""

    def test_ollama_direct_sdk_access(self, ollama_client):
        """Ollama should access skills directly via Python SDK."""
        # This simulates how Ollama would integrate - direct Python calls
        result = ollama_client.use_skill("testing assistance")
        assert result.skill_name is not None
        assert result.content is not None

    def test_ollama_returns_token_count(self, ollama_client):
        """Ollama integration should return token usage info."""
        result = ollama_client.use_skill("help with tests")
        # Tokens should be available for local context management
        assert result.raw_response is not None
        assert "tokens_used" in result.raw_response

    def test_ollama_local_search(self, ollama_client):
        """Ollama should search skills locally."""
        result = ollama_client.search_skills("variable")
        assert result.total > 0


class TestProviderAgnosticBehavior:
    """Tests that verify no provider-specific bias in skill behavior."""

    def test_no_provider_specific_content(self, all_clients):
        """Skills should not contain provider-specific instructions."""
        for client in all_clients:
            result = client.read_skill("multi-llm-test-skill")
            content = result.content.lower()

            # Should not contain provider-specific instructions
            assert "claude" not in content or "mcp" in content, (
                "Skill should not contain Claude-specific instructions"
            )
            assert "chatgpt" not in content, (
                "Skill should not contain ChatGPT-specific instructions"
            )
            assert "gemini" not in content, (
                "Skill should not contain Gemini-specific instructions"
            )

    def test_consistent_error_handling(self, all_clients):
        """All providers should handle errors consistently."""
        for client in all_clients:
            # Try to read non-existent skill
            result = client.read_skill("this-skill-does-not-exist-12345")

            # All should indicate error somehow
            has_error = (
                result.error is not None or
                result.content is None or
                (result.content and "not found" in result.content.lower())
            )
            assert has_error, (
                f"{client.provider_name} did not handle missing skill error"
            )

    def test_consistent_variable_defaults(self, all_clients):
        """All providers should use the same default values."""
        for client in all_clients:
            result = client.read_skill("multi-llm-test-skill")

            # Should use default values: "Hello" and "World"
            assert "Hello" in result.content, (
                f"{client.provider_name} did not use default greeting"
            )
            assert "World" in result.content, (
                f"{client.provider_name} did not use default target"
            )


# =============================================================================
# Integration Smoke Tests
# =============================================================================


class TestIntegrationSmoke:
    """Smoke tests for quick validation of multi-LLM support."""

    def test_basic_workflow_all_providers(self, all_clients):
        """Basic workflow should work for all providers."""
        for client in all_clients:
            # 1. List skills
            skills = client.list_skills()
            assert len(skills) > 0, f"{client.provider_name}: No skills found"

            # 2. Search for a skill
            search = client.search_skills("test")
            assert search.total > 0, f"{client.provider_name}: Search failed"

            # 3. Read a specific skill
            result = client.read_skill(skills[0]["name"])
            assert result.content is not None, f"{client.provider_name}: Read failed"

    def test_provider_info(self, all_clients):
        """All providers should identify themselves correctly."""
        provider_names = {client.provider_name for client in all_clients}

        expected = {"claude_mcp", "openai_functions", "gemini_functions", "ollama_local"}
        assert provider_names == expected, f"Missing providers: {expected - provider_names}"

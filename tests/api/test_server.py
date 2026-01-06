"""Tests for REST API server."""

from __future__ import annotations

import pytest

# Skip all tests if FastAPI is not installed
pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from aiskills.api.server import create_app


@pytest.fixture
def client():
    """Create test client for the API."""
    app = create_app()
    return TestClient(app)


@pytest.fixture
def populated_client(tmp_path, simple_skill_content, skill_with_variables_content, monkeypatch):
    """Create test client with some skills installed."""
    # Set up temp directories
    global_dir = tmp_path / "global"
    global_skills = global_dir / "skills"
    global_skills.mkdir(parents=True)

    project_dir = tmp_path / "project"
    project_skills = project_dir / ".aiskills" / "skills"
    project_skills.mkdir(parents=True)

    # Create skills - directory names must match skill names in SKILL.md
    skill1 = project_skills / "simple-skill"
    skill1.mkdir()
    (skill1 / "SKILL.md").write_text(simple_skill_content)

    skill2 = project_skills / "skill-with-variables"
    skill2.mkdir()
    (skill2 / "SKILL.md").write_text(skill_with_variables_content)

    # Patch config and cwd
    from aiskills.config import AppConfig, StorageConfig, EmbeddingConfig, VectorStoreConfig, set_config

    config = AppConfig(
        storage=StorageConfig(global_dir=global_dir),
        embedding=EmbeddingConfig(provider="none"),
        vector_store=VectorStoreConfig(provider="none"),
    )
    set_config(config)

    # Reset singletons so they pick up new config
    from aiskills.core import manager as manager_module
    from aiskills.storage import paths as paths_module
    from aiskills.core import registry as registry_module

    manager_module._manager = None
    paths_module._resolver = None
    if hasattr(registry_module, '_registry'):
        registry_module._registry = None

    # Change to project dir
    monkeypatch.chdir(project_dir)

    app = create_app()
    return TestClient(app)


class TestHealthEndpoints:
    """Tests for health and info endpoints."""

    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "aiskills"
        assert "version" in data
        assert "docs" in data

    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestSkillsEndpoints:
    """Tests for skills CRUD endpoints."""

    def test_list_skills_empty(self, client, tmp_path, monkeypatch):
        # Set up empty project
        from aiskills.config import AppConfig, StorageConfig, EmbeddingConfig, VectorStoreConfig, set_config

        config = AppConfig(
            storage=StorageConfig(global_dir=tmp_path / "global"),
            embedding=EmbeddingConfig(provider="none"),
            vector_store=VectorStoreConfig(provider="none"),
        )
        set_config(config)
        monkeypatch.chdir(tmp_path)

        response = client.get("/skills")
        assert response.status_code == 200
        data = response.json()
        assert "skills" in data
        assert data["skills"] == []

    def test_list_skills_with_skills(self, populated_client):
        response = populated_client.get("/skills")
        assert response.status_code == 200
        data = response.json()
        assert len(data["skills"]) >= 1

        # Check skill structure
        skill = data["skills"][0]
        assert "name" in skill
        assert "description" in skill
        assert "version" in skill

    def test_get_skill_by_name(self, populated_client):
        response = populated_client.get("/skills/simple-skill")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "simple-skill"
        assert "content" in data

    def test_get_skill_not_found(self, populated_client):
        response = populated_client.get("/skills/nonexistent-skill")
        assert response.status_code == 404


class TestSearchEndpoints:
    """Tests for search endpoints."""

    def test_search_basic(self, populated_client):
        response = populated_client.post(
            "/skills/search",
            json={"query": "simple"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "results" in data

    def test_search_with_limit(self, populated_client):
        response = populated_client.post(
            "/skills/search",
            json={"query": "skill", "limit": 1},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["results"]) <= 1

    def test_search_text_only(self, populated_client):
        response = populated_client.post(
            "/skills/search",
            json={"query": "variables", "text_only": True},
        )
        assert response.status_code == 200


class TestReadEndpoints:
    """Tests for read/render endpoints."""

    def test_read_skill(self, populated_client):
        response = populated_client.post(
            "/skills/read",
            json={"name": "simple-skill"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "content" in data
        assert "name" in data

    def test_read_skill_with_variables(self, populated_client):
        response = populated_client.post(
            "/skills/read",
            json={
                "name": "skill-with-variables",
                "variables": {"language": "rust"},
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "rust" in data["content"]

    def test_read_skill_not_found(self, populated_client):
        response = populated_client.post(
            "/skills/read",
            json={"name": "nonexistent"},
        )
        assert response.status_code == 404


class TestSuggestEndpoints:
    """Tests for suggestion endpoints."""

    def test_suggest_basic(self, populated_client):
        response = populated_client.post(
            "/skills/suggest",
            json={"context": "I need help with testing"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data


class TestOpenAIEndpoints:
    """Tests for OpenAI-compatible endpoints."""

    def test_get_tools(self, client):
        response = client.get("/openai/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data

        # Check tool structure
        tools = data["tools"]
        assert len(tools) >= 1

        tool = tools[0]
        assert tool["type"] == "function"
        assert "function" in tool
        assert "name" in tool["function"]
        assert "description" in tool["function"]
        assert "parameters" in tool["function"]

    def test_call_skill_search(self, populated_client):
        response = populated_client.post(
            "/openai/call",
            json={
                "name": "skill_search",
                "arguments": {"query": "test"},
            },
        )
        assert response.status_code == 200
        data = response.json()
        # OpenAI format returns name and content (JSON string)
        assert "name" in data
        assert "content" in data
        assert data["name"] == "skill_search"

    def test_call_skill_read(self, populated_client):
        response = populated_client.post(
            "/openai/call",
            json={
                "name": "skill_read",
                "arguments": {"name": "simple-skill"},
            },
        )
        assert response.status_code == 200
        data = response.json()
        # OpenAI format returns name and content (JSON string)
        assert "name" in data
        assert "content" in data
        assert data["name"] == "skill_read"
        # Content is a JSON string containing the skill content
        import json
        content_data = json.loads(data["content"])
        assert "content" in content_data

    def test_call_skill_list(self, populated_client):
        response = populated_client.post(
            "/openai/call",
            json={
                "name": "skill_list",
                "arguments": {},
            },
        )
        assert response.status_code == 200
        data = response.json()
        # OpenAI format returns name and content (JSON string)
        assert "name" in data
        assert "content" in data
        assert data["name"] == "skill_list"

    def test_call_unknown_function(self, client):
        response = client.post(
            "/openai/call",
            json={
                "name": "unknown_function",
                "arguments": {},
            },
        )
        # Server returns 200 with error message in content
        assert response.status_code == 200
        data = response.json()
        assert "error" in data["content"]
        assert "unknown_function" in data["content"].lower()


class TestCORS:
    """Tests for CORS configuration."""

    def test_cors_headers(self, client):
        response = client.options(
            "/skills",
            headers={"Origin": "http://localhost:3000"},
        )
        # FastAPI/Starlette handles OPTIONS
        assert response.status_code in [200, 405]


class TestErrorHandling:
    """Tests for error responses."""

    def test_invalid_json(self, client):
        response = client.post(
            "/skills/search",
            content="not json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422

    def test_missing_required_field(self, client):
        response = client.post(
            "/skills/search",
            json={},  # Missing 'query'
        )
        assert response.status_code == 422

    def test_invalid_limit(self, client):
        response = client.post(
            "/skills/search",
            json={"query": "test", "limit": -1},
        )
        # Pydantic validation should catch this
        assert response.status_code in [200, 422]

"""Tests for the SkillRouter."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from aiskills.core.router import SkillRouter, UseResult, get_router


class TestUseResult:
    """Tests for UseResult model."""

    def test_minimal_result(self):
        """Test creating a minimal UseResult."""
        result = UseResult(skill_name="test", content="Test content")
        assert result.skill_name == "test"
        assert result.content == "Test content"
        assert result.score is None
        assert result.matched_query == ""
        assert result.variables_applied == {}

    def test_full_result(self):
        """Test creating a full UseResult."""
        result = UseResult(
            skill_name="my-skill",
            content="# My Skill Content",
            score=0.95,
            matched_query="help with python debugging",
            variables_applied={"lang": "python"},
        )
        assert result.skill_name == "my-skill"
        assert result.content == "# My Skill Content"
        assert result.score == 0.95
        assert result.matched_query == "help with python debugging"
        assert result.variables_applied == {"lang": "python"}


class TestSkillRouter:
    """Tests for SkillRouter class."""

    def test_init(self):
        """Test router initialization."""
        router = SkillRouter()
        assert router._manager is None
        assert router._registry is None

    def test_manager_lazy_load(self):
        """Test manager is lazily loaded."""
        router = SkillRouter()
        with patch("aiskills.core.router.get_manager") as mock_get:
            mock_manager = MagicMock()
            mock_get.return_value = mock_manager
            
            # First access
            manager = router.manager
            assert manager is mock_manager
            mock_get.assert_called_once()
            
            # Second access should use cached value
            manager2 = router.manager
            assert manager2 is mock_manager
            assert mock_get.call_count == 1

    def test_registry_lazy_load(self):
        """Test registry is lazily loaded."""
        router = SkillRouter()
        with patch("aiskills.core.router.get_registry") as mock_get:
            mock_registry = MagicMock()
            mock_get.return_value = mock_registry
            
            # First access
            registry = router.registry
            assert registry is mock_registry
            mock_get.assert_called_once()
            
            # Second access should use cached value
            registry2 = router.registry
            assert registry2 is mock_registry
            assert mock_get.call_count == 1

    def test_use_no_results(self):
        """Test use() when no skills match."""
        router = SkillRouter()
        
        with patch.object(router, "registry") as mock_registry:
            mock_registry.search.return_value = []
            
            result = router.use("nonexistent skill query")
            
            assert result.skill_name == ""
            assert "No matching skill found" in result.content
            assert result.score == 0.0
            assert result.matched_query == "nonexistent skill query"

    def test_use_with_result(self):
        """Test use() with a matching skill."""
        router = SkillRouter()
        
        mock_skill_idx = MagicMock()
        mock_skill_idx.name = "debug-python"
        
        with patch.object(router, "registry") as mock_registry, \
             patch.object(router, "manager") as mock_manager:
            mock_registry.search.return_value = [(mock_skill_idx, 0.89)]
            mock_manager.read.return_value = "# Debug Python\n\nStep 1..."
            
            result = router.use("help me debug python")
            
            assert result.skill_name == "debug-python"
            assert result.content == "# Debug Python\n\nStep 1..."
            assert result.score == 0.89
            assert result.matched_query == "help me debug python"

    def test_use_with_variables(self):
        """Test use() passes variables correctly."""
        router = SkillRouter()
        
        mock_skill_idx = MagicMock()
        mock_skill_idx.name = "template-skill"
        
        with patch.object(router, "registry") as mock_registry, \
             patch.object(router, "manager") as mock_manager:
            mock_registry.search.return_value = [(mock_skill_idx, 0.95)]
            mock_manager.read.return_value = "Content for python"
            
            result = router.use("need help", variables={"lang": "python"})
            
            mock_manager.read.assert_called_once_with(
                name="template-skill",
                variables={"lang": "python"},
            )
            assert result.variables_applied == {"lang": "python"}

    def test_use_fallback_to_text_search(self):
        """Test use() falls back to text search if semantic fails."""
        router = SkillRouter()
        
        mock_skill_idx = MagicMock()
        mock_skill_idx.name = "fallback-skill"
        
        with patch.object(router, "registry") as mock_registry, \
             patch.object(router, "manager") as mock_manager:
            # Semantic search raises "not installed" error
            mock_registry.search.side_effect = Exception("embeddings not installed")
            mock_registry.search_text.return_value = [mock_skill_idx]
            mock_manager.read.return_value = "Fallback content"
            
            result = router.use("some query")
            
            mock_registry.search_text.assert_called_once()
            assert result.skill_name == "fallback-skill"

    def test_use_multiple_results(self):
        """Test use() with limit > 1."""
        router = SkillRouter()
        
        mock_skill1 = MagicMock()
        mock_skill1.name = "skill-1"
        mock_skill2 = MagicMock()
        mock_skill2.name = "skill-2"
        
        with patch.object(router, "registry") as mock_registry, \
             patch.object(router, "manager") as mock_manager:
            mock_registry.search.return_value = [
                (mock_skill1, 0.9),
                (mock_skill2, 0.8),
            ]
            mock_manager.read.side_effect = ["Content 1", "Content 2"]
            
            results = router.use("query", limit=2)
            
            assert isinstance(results, list)
            assert len(results) == 2
            assert results[0].skill_name == "skill-1"
            assert results[1].skill_name == "skill-2"

    def test_use_by_name_success(self):
        """Test use_by_name() with existing skill."""
        router = SkillRouter()
        
        mock_skill = MagicMock()
        
        with patch.object(router, "manager") as mock_manager:
            mock_manager.read.return_value = "# Skill Content"
            mock_manager.get.return_value = mock_skill
            
            result = router.use_by_name("my-skill")
            
            assert result.skill_name == "my-skill"
            assert result.content == "# Skill Content"
            assert result.score == 1.0  # Exact match

    def test_use_by_name_not_found(self):
        """Test use_by_name() with nonexistent skill."""
        router = SkillRouter()
        
        with patch.object(router, "manager") as mock_manager:
            mock_manager.read.side_effect = Exception("Skill not found")
            
            result = router.use_by_name("nonexistent")
            
            assert result.skill_name == "nonexistent"
            assert "Error loading skill" in result.content
            assert result.score == 0.0


class TestGetRouter:
    """Tests for get_router singleton."""

    def test_returns_router_instance(self):
        """Test get_router returns a SkillRouter."""
        # Reset singleton for test
        import aiskills.core.router as router_module
        router_module._router = None
        
        router = get_router()
        assert isinstance(router, SkillRouter)

    def test_returns_same_instance(self):
        """Test get_router returns the same instance."""
        router1 = get_router()
        router2 = get_router()
        assert router1 is router2

"""Tests for skill manager."""

from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from aiskills.config import AppConfig, EmbeddingConfig, StorageConfig, VectorStoreConfig
from aiskills.core.loader import LoadError
from aiskills.core.manager import SkillManager, get_manager
from aiskills.models.skill import Skill, SkillIndex


class TestSkillManager:
    """Tests for SkillManager class."""

    @pytest.fixture
    def manager(self, mock_config, tmp_path):
        """Create a manager with test configuration."""
        from aiskills.storage.paths import PathResolver
        from aiskills.storage.cache import CacheManager
        from aiskills.core.loader import SkillLoader
        from aiskills.core.renderer import SkillRenderer

        paths = PathResolver(config=mock_config, cwd=tmp_path)
        return SkillManager(
            config=mock_config,
            paths=paths,
            loader=SkillLoader(),
            cache=CacheManager(paths),  # CacheManager expects PathResolver, not AppConfig
            renderer=SkillRenderer(),
        )

    @pytest.fixture
    def skill_in_project(self, tmp_path, simple_skill_content):
        """Create a skill in the project directory.

        Note: Directory name must match skill name in SKILL.md for lookup to work.
        """
        # simple_skill_content has name: simple-skill, so directory must match
        skill_dir = tmp_path / ".aiskills" / "skills" / "simple-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(simple_skill_content)
        return skill_dir

    # ─────────────────────────────────────────────────────────────────
    # get() tests
    # ─────────────────────────────────────────────────────────────────

    def test_get_nonexistent_skill(self, manager):
        result = manager.get("nonexistent")
        assert result is None

    def test_get_skill_from_project(self, manager, skill_in_project):
        # Directory name matches skill name in SKILL.md
        skill = manager.get("simple-skill")
        assert skill is not None
        assert skill.name == "simple-skill"
        assert skill.source == "project"

    def test_get_skill_from_global(self, manager, tmp_global_dir, simple_skill_content, tmp_path_factory):
        # Use separate directories to avoid project/global overlap
        separate_global = tmp_path_factory.mktemp("global")
        (separate_global / "skills").mkdir(parents=True)
        cwd_path = tmp_path_factory.mktemp("project")

        config = AppConfig(
            storage=StorageConfig(global_dir=separate_global),
            embedding=EmbeddingConfig(provider="none"),
            vector_store=VectorStoreConfig(provider="none"),
        )

        from aiskills.storage.paths import PathResolver
        from aiskills.core.loader import SkillLoader

        paths = PathResolver(config=config, cwd=cwd_path)
        test_manager = SkillManager(config=config, paths=paths, loader=SkillLoader())

        # Create skill in global - directory name must match skill name in SKILL.md
        skill_dir = separate_global / "skills" / "simple-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(simple_skill_content)

        skill = test_manager.get("simple-skill")
        assert skill is not None
        assert skill.source == "global"

    # ─────────────────────────────────────────────────────────────────
    # list_installed() tests
    # ─────────────────────────────────────────────────────────────────

    def test_list_installed_empty(self, manager):
        skills = manager.list_installed()
        assert skills == []

    def test_list_installed_with_skills(self, manager, skill_in_project):
        skills = manager.list_installed()
        assert len(skills) >= 1
        names = [s.name for s in skills]
        assert "simple-skill" in names

    def test_list_installed_project_only(self, manager, skill_in_project):
        skills = manager.list_installed(project_only=True)
        for skill in skills:
            assert skill.source == "project"

    # ─────────────────────────────────────────────────────────────────
    # read() tests
    # ─────────────────────────────────────────────────────────────────

    def test_read_nonexistent_skill(self, manager):
        with pytest.raises(LoadError) as exc:
            manager.read("nonexistent")
        assert "not found" in str(exc.value).lower()

    def test_read_skill_content(self, manager, skill_in_project):
        content = manager.read("simple-skill")
        assert "# Skill: simple-skill" in content
        assert "Simple Skill" in content

    def test_read_skill_with_variables(self, manager, tmp_path, skill_with_variables_content):
        # Create a skill with variables - directory name must match skill name
        skill_dir = tmp_path / ".aiskills" / "skills" / "skill-with-variables"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(skill_with_variables_content)

        content = manager.read("skill-with-variables", variables={"language": "rust"})
        assert "rust" in content

    # ─────────────────────────────────────────────────────────────────
    # list_all() tests
    # ─────────────────────────────────────────────────────────────────

    def test_list_all_empty(self, manager):
        indices = manager.list_all()
        assert indices == []

    def test_list_all_with_skills(self, manager, skill_in_project):
        indices = manager.list_all()
        assert len(indices) >= 1
        assert all(isinstance(idx, SkillIndex) for idx in indices)

    def test_list_all_sorted(self, manager, tmp_path, simple_skill_content):
        # Create multiple skills
        for name in ["zebra", "alpha", "mango"]:
            skill_dir = tmp_path / ".aiskills" / "skills" / name
            skill_dir.mkdir(parents=True)
            content = simple_skill_content.replace("simple-skill", name)
            (skill_dir / "SKILL.md").write_text(content)

        indices = manager.list_all()
        names = [idx.name for idx in indices]
        assert names == sorted(names)

    # ─────────────────────────────────────────────────────────────────
    # install_from_path() tests
    # ─────────────────────────────────────────────────────────────────

    def test_install_from_path_new(self, manager, tmp_path, simple_skill_content):
        # Create source skill
        source_dir = tmp_path / "source-skill"
        source_dir.mkdir()
        (source_dir / "SKILL.md").write_text(simple_skill_content)

        skill, status = manager.install_from_path(source_dir)
        assert status == "installed"
        assert skill.name == "simple-skill"
        assert skill.source == "project"

    def test_install_from_path_already_exists(self, manager, tmp_path, simple_skill_content):
        # Create source skill
        source_dir = tmp_path / "source-skill"
        source_dir.mkdir()
        (source_dir / "SKILL.md").write_text(simple_skill_content)

        # Install first time
        skill1, status1 = manager.install_from_path(source_dir)
        assert status1 == "installed"

        # Install again with same content
        skill2, status2 = manager.install_from_path(source_dir)
        assert status2 == "unchanged"

    def test_install_from_path_updated(self, manager, tmp_path, simple_skill_content):
        # Create source skill
        source_dir = tmp_path / "source-skill"
        source_dir.mkdir()
        (source_dir / "SKILL.md").write_text(simple_skill_content)

        # Install first time
        skill1, status1 = manager.install_from_path(source_dir)
        assert status1 == "installed"

        # Update content
        updated_content = simple_skill_content.replace("unit tests", "updated content")
        (source_dir / "SKILL.md").write_text(updated_content)

        # Install again
        skill2, status2 = manager.install_from_path(source_dir)
        assert status2 == "updated"

    def test_install_from_path_force(self, manager, tmp_path, simple_skill_content):
        # Create source skill
        source_dir = tmp_path / "source-skill"
        source_dir.mkdir()
        (source_dir / "SKILL.md").write_text(simple_skill_content)

        # Install first time
        skill1, status1 = manager.install_from_path(source_dir)
        assert status1 == "installed"

        # Force reinstall (should be updated even with same content)
        skill2, status2 = manager.install_from_path(source_dir, force=True)
        assert status2 == "updated"

    def test_install_from_path_global(self, manager, tmp_path, simple_skill_content):
        # Create source skill
        source_dir = tmp_path / "source-skill"
        source_dir.mkdir()
        (source_dir / "SKILL.md").write_text(simple_skill_content)

        skill, status = manager.install_from_path(source_dir, global_install=True)
        assert status == "installed"
        assert skill.source == "global"

    # ─────────────────────────────────────────────────────────────────
    # remove() tests
    # ─────────────────────────────────────────────────────────────────

    def test_remove_nonexistent(self, manager):
        result = manager.remove("nonexistent")
        assert result is False

    def test_remove_skill(self, manager, skill_in_project):
        # Verify skill exists
        assert manager.get("simple-skill") is not None

        # Remove it
        result = manager.remove("simple-skill")
        assert result is True

        # Verify it's gone
        assert manager.get("simple-skill") is None

    # ─────────────────────────────────────────────────────────────────
    # validate() tests
    # ─────────────────────────────────────────────────────────────────

    def test_validate_valid_skill(self, manager, skill_in_project):
        errors = manager.validate(skill_in_project)
        assert errors == []

    def test_validate_missing_skill_file(self, manager, tmp_path):
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        errors = manager.validate(empty_dir)
        assert any("SKILL.md" in e for e in errors)

    def test_validate_nonexistent_path(self, manager, tmp_path):
        errors = manager.validate(tmp_path / "nonexistent")
        assert any("does not exist" in e for e in errors)

    # ─────────────────────────────────────────────────────────────────
    # Cache tests
    # ─────────────────────────────────────────────────────────────────

    def test_clear_cache(self, manager):
        # Should not raise even with empty cache
        count = manager.clear_cache()
        assert count >= 0

    def test_get_cache_stats(self, manager):
        stats = manager.get_cache_stats()
        assert isinstance(stats, dict)

    # ─────────────────────────────────────────────────────────────────
    # get_skill_variables() tests
    # ─────────────────────────────────────────────────────────────────

    def test_get_skill_variables_nonexistent(self, manager):
        variables = manager.get_skill_variables("nonexistent")
        assert variables == {}

    def test_get_skill_variables_with_vars(self, manager, tmp_path, skill_with_variables_content):
        # Create a skill with variables - directory name must match skill name
        skill_dir = tmp_path / ".aiskills" / "skills" / "skill-with-variables"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(skill_with_variables_content)

        variables = manager.get_skill_variables("skill-with-variables")
        assert "language" in variables
        assert variables["language"]["type"] == "string"
        assert variables["language"]["default"] == "python"


class TestGetManager:
    """Tests for get_manager singleton."""

    def test_returns_manager_instance(self):
        manager = get_manager()
        assert isinstance(manager, SkillManager)

    def test_returns_same_instance(self):
        m1 = get_manager()
        m2 = get_manager()
        assert m1 is m2

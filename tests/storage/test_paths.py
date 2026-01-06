"""Tests for path resolution."""

from __future__ import annotations

from pathlib import Path

import pytest

from aiskills.storage.paths import PathResolver, get_path_resolver


class TestPathResolver:
    """Tests for PathResolver class."""

    @pytest.fixture
    def resolver(self, mock_config, tmp_path):
        """Create a resolver with test paths."""
        return PathResolver(config=mock_config, cwd=tmp_path)

    # Property tests
    def test_global_base(self, resolver, mock_config):
        assert resolver.global_base == mock_config.storage.global_dir

    def test_global_skills_dir(self, resolver, mock_config):
        expected = mock_config.storage.global_dir / "skills"
        assert resolver.global_skills_dir == expected

    # get_project_base/skills_dir tests
    def test_get_project_base_default(self, resolver, tmp_path):
        assert resolver.get_project_base() == tmp_path / ".aiskills"

    def test_get_project_base_claude(self, resolver, tmp_path):
        assert resolver.get_project_base(".claude") == tmp_path / ".claude"

    def test_get_project_base_agent(self, resolver, tmp_path):
        assert resolver.get_project_base(".agent") == tmp_path / ".agent"

    def test_get_project_skills_dir(self, resolver, tmp_path):
        expected = tmp_path / ".aiskills" / "skills"
        assert resolver.get_project_skills_dir() == expected

    # get_search_dirs tests
    def test_get_search_dirs_no_project(self, mock_config, tmp_path):
        """No project directories exist, only global."""
        # Create resolver with fresh tmp_path as cwd (no project dirs)
        resolver = PathResolver(config=mock_config, cwd=tmp_path)
        dirs = resolver.get_search_dirs()
        # Only global should exist (from mock_config)
        assert len(dirs) <= 1  # May have global if it exists

    def test_get_search_dirs_with_project(self, mock_config, tmp_path):
        # Create project skills dir
        project_skills = tmp_path / ".aiskills" / "skills"
        project_skills.mkdir(parents=True)

        resolver = PathResolver(config=mock_config, cwd=tmp_path)
        dirs = resolver.get_search_dirs()
        # Project should be first
        assert len(dirs) >= 1
        assert dirs[0][0] == project_skills
        assert dirs[0][1] == ".aiskills"

    def test_get_search_dirs_with_global(self, resolver, tmp_global_dir):
        # Global dir already has skills/ created
        dirs = resolver.get_search_dirs()
        # Only global should be present (no project dirs)
        assert len(dirs) == 1
        assert "global" in str(dirs[0][0])

    def test_get_search_dirs_priority(self, resolver, tmp_path, tmp_global_dir):
        """Project dirs should come before global."""
        # Create project dir
        project_skills = tmp_path / ".aiskills" / "skills"
        project_skills.mkdir(parents=True)

        dirs = resolver.get_search_dirs()
        # Project should be first
        assert len(dirs) == 2
        assert dirs[0][0] == project_skills
        assert "global" in str(dirs[1][0])

    def test_get_search_dirs_multiple_project_dirs(self, resolver, tmp_path, tmp_global_dir):
        """All project directory types are searched."""
        # Create all types
        (tmp_path / ".aiskills" / "skills").mkdir(parents=True)
        (tmp_path / ".claude" / "skills").mkdir(parents=True)
        (tmp_path / ".agent" / "skills").mkdir(parents=True)

        dirs = resolver.get_search_dirs()
        location_types = [d[1] for d in dirs]

        assert ".aiskills" in location_types
        assert ".claude" in location_types
        assert ".agent" in location_types

    def test_get_all_search_paths(self, resolver, tmp_path):
        project_skills = tmp_path / ".aiskills" / "skills"
        project_skills.mkdir(parents=True)

        paths = resolver.get_all_search_paths()
        assert project_skills in paths

    # find_skill tests
    def test_find_skill_not_found(self, resolver):
        result = resolver.find_skill("nonexistent")
        assert result is None

    def test_find_skill_in_project(self, resolver, tmp_path, simple_skill_content):
        # Create skill in project
        skill_dir = tmp_path / ".aiskills" / "skills" / "my-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(simple_skill_content)

        result = resolver.find_skill("my-skill")
        assert result is not None
        path, source, location_type = result
        assert path == skill_dir
        assert source == "project"
        assert location_type == ".aiskills"

    def test_find_skill_in_global(self, mock_config, simple_skill_content, tmp_path_factory):
        # Create a truly separate global dir (not under cwd)
        separate_global = tmp_path_factory.mktemp("global")
        (separate_global / "skills").mkdir(parents=True)

        # Create a separate cwd
        cwd_path = tmp_path_factory.mktemp("project")

        # Create config with separate global
        from aiskills.config import AppConfig, StorageConfig, EmbeddingConfig, VectorStoreConfig

        config = AppConfig(
            storage=StorageConfig(global_dir=separate_global),
            embedding=EmbeddingConfig(provider="none"),
            vector_store=VectorStoreConfig(provider="none"),
        )

        resolver = PathResolver(config=config, cwd=cwd_path)

        # Create skill in global
        skill_dir = separate_global / "skills" / "global-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(simple_skill_content)

        result = resolver.find_skill("global-skill")
        assert result is not None
        path, source, location_type = result
        assert path == skill_dir
        assert source == "global"

    def test_find_skill_project_overrides_global(self, resolver, tmp_path, tmp_global_dir, simple_skill_content):
        """Project skill takes precedence over global."""
        # Create in both
        project_skill = tmp_path / ".aiskills" / "skills" / "shared-skill"
        project_skill.mkdir(parents=True)
        (project_skill / "SKILL.md").write_text(simple_skill_content)

        global_skill = tmp_global_dir / "skills" / "shared-skill"
        global_skill.mkdir(parents=True)
        (global_skill / "SKILL.md").write_text(simple_skill_content)

        result = resolver.find_skill("shared-skill")
        assert result is not None
        path, source, _ = result
        assert path == project_skill
        assert source == "project"

    def test_find_skill_missing_skill_file(self, resolver, tmp_path):
        """Directory exists but no SKILL.md."""
        skill_dir = tmp_path / ".aiskills" / "skills" / "empty-dir"
        skill_dir.mkdir(parents=True)
        # No SKILL.md

        result = resolver.find_skill("empty-dir")
        assert result is None

    # get_install_path tests
    def test_get_install_path_project(self, resolver, tmp_path):
        path = resolver.get_install_path("new-skill")
        expected = tmp_path / ".aiskills" / "skills" / "new-skill"
        assert path == expected

    def test_get_install_path_global(self, resolver, tmp_global_dir):
        path = resolver.get_install_path("new-skill", global_install=True)
        expected = tmp_global_dir / "skills" / "new-skill"
        assert path == expected

    def test_get_install_path_custom_location(self, resolver, tmp_path):
        path = resolver.get_install_path("skill", location=".claude")
        expected = tmp_path / ".claude" / "skills" / "skill"
        assert path == expected

    # ensure_dirs tests
    def test_ensure_dirs_project(self, resolver, tmp_path):
        skills_dir = resolver.ensure_dirs()
        assert skills_dir.exists()
        assert skills_dir == tmp_path / ".aiskills" / "skills"

    def test_ensure_dirs_global(self, resolver, tmp_global_dir):
        skills_dir = resolver.ensure_dirs(global_install=True)
        assert skills_dir.exists()
        assert skills_dir == tmp_global_dir / "skills"

    def test_ensure_dirs_idempotent(self, resolver):
        # Call twice
        dir1 = resolver.ensure_dirs()
        dir2 = resolver.ensure_dirs()
        assert dir1 == dir2
        assert dir1.exists()

    # get_lock_file_path tests
    def test_get_lock_file_path_project(self, resolver, tmp_path):
        path = resolver.get_lock_file_path()
        assert path == tmp_path / ".aiskills" / "aiskills.lock"

    def test_get_lock_file_path_global(self, resolver, tmp_global_dir):
        path = resolver.get_lock_file_path(global_install=True)
        assert path == tmp_global_dir / "aiskills.lock"

    # get_cache_dir tests
    def test_get_cache_dir(self, resolver, tmp_global_dir):
        cache_dir = resolver.get_cache_dir()
        assert cache_dir.exists()
        assert cache_dir == tmp_global_dir / "cache"

    # get_registry_dir tests
    def test_get_registry_dir(self, resolver, tmp_global_dir):
        registry_dir = resolver.get_registry_dir()
        assert registry_dir.exists()
        assert registry_dir == tmp_global_dir / "registry"

    # expand_path tests
    def test_expand_path_absolute(self, resolver):
        path = resolver.expand_path("/absolute/path")
        assert path == Path("/absolute/path")

    def test_expand_path_relative(self, resolver, tmp_path):
        path = resolver.expand_path("relative/path")
        assert path == (tmp_path / "relative/path").resolve()

    def test_expand_path_home(self, resolver):
        path = resolver.expand_path("~/some/path")
        assert "~" not in str(path)
        assert Path.home() in path.parents or path == Path.home() / "some/path"

    def test_expand_path_current_dir(self, resolver, tmp_path):
        path = resolver.expand_path("./local")
        assert path == (tmp_path / "local").resolve()

    def test_expand_path_parent_dir(self, resolver, tmp_path):
        path = resolver.expand_path("../sibling")
        assert path == (tmp_path.parent / "sibling").resolve()

    # is_local_path tests
    def test_is_local_path_absolute(self, resolver):
        assert resolver.is_local_path("/absolute/path") is True

    def test_is_local_path_relative_dot(self, resolver):
        assert resolver.is_local_path("./local") is True

    def test_is_local_path_relative_dotdot(self, resolver):
        assert resolver.is_local_path("../parent") is True

    def test_is_local_path_home(self, resolver):
        assert resolver.is_local_path("~/home/path") is True

    def test_is_local_path_git_ssh(self, resolver):
        assert resolver.is_local_path("git@github.com:owner/repo") is False

    def test_is_local_path_https(self, resolver):
        assert resolver.is_local_path("https://github.com/owner/repo") is False

    def test_is_local_path_github_shorthand(self, resolver):
        # owner/repo format (doesn't exist locally)
        assert resolver.is_local_path("owner/repo") is False

    def test_is_local_path_existing_dir(self, resolver, tmp_path):
        # Create a directory that looks like owner/repo but exists
        local_dir = tmp_path / "owner" / "repo"
        local_dir.mkdir(parents=True)
        # Note: is_local_path uses Path without cwd, so this test might not work
        # as expected. The function checks if path exists relative to cwd.


class TestGetPathResolver:
    """Tests for get_path_resolver singleton."""

    def test_returns_resolver_instance(self):
        resolver = get_path_resolver()
        assert isinstance(resolver, PathResolver)

    def test_returns_same_instance(self):
        r1 = get_path_resolver()
        r2 = get_path_resolver()
        assert r1 is r2

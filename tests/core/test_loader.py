"""Tests for skill loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from aiskills.core.loader import (
    LoadError,
    SkillLoader,
    ValidationError,
    get_loader,
)
from aiskills.core.parser import ParseError
from aiskills.models.skill import Skill


class TestSkillLoader:
    """Tests for SkillLoader class."""

    @pytest.fixture
    def loader(self):
        return SkillLoader()

    # load() tests
    def test_load_simple_skill(self, loader, create_skill_file, simple_skill_content):
        skill_dir = create_skill_file("simple-skill", simple_skill_content)
        skill = loader.load(skill_dir)

        assert isinstance(skill, Skill)
        assert skill.name == "simple-skill"
        assert skill.version == "1.0.0"
        assert skill.source == "project"  # Default
        assert skill.path == str(skill_dir.absolute())

    def test_load_with_source_global(self, loader, create_skill_file, simple_skill_content):
        skill_dir = create_skill_file("skill", simple_skill_content)
        skill = loader.load(skill_dir, source="global")
        assert skill.source == "global"

    def test_load_with_source_cache(self, loader, create_skill_file, simple_skill_content):
        skill_dir = create_skill_file("skill", simple_skill_content)
        skill = loader.load(skill_dir, source="cache")
        assert skill.source == "cache"

    def test_load_with_location_types(self, loader, create_skill_file, simple_skill_content):
        for loc_type in [".aiskills", ".claude", ".agent"]:
            skill_dir = create_skill_file(f"skill-{loc_type}", simple_skill_content)
            skill = loader.load(skill_dir, location_type=loc_type)
            assert skill.location_type == loc_type

    def test_load_nonexistent_directory(self, loader, tmp_path):
        with pytest.raises(LoadError) as exc:
            loader.load(tmp_path / "nonexistent")
        assert "does not exist" in str(exc.value)

    def test_load_file_not_directory(self, loader, tmp_path):
        file_path = tmp_path / "not_a_dir"
        file_path.write_text("content")
        with pytest.raises(LoadError) as exc:
            loader.load(file_path)
        assert "not a directory" in str(exc.value)

    def test_load_missing_skill_file(self, loader, tmp_path):
        skill_dir = tmp_path / "empty-skill"
        skill_dir.mkdir()
        with pytest.raises(LoadError) as exc:
            loader.load(skill_dir)
        assert "No SKILL.md found" in str(exc.value)

    def test_load_oversized_skill(self, loader, tmp_path):
        skill_dir = tmp_path / "big-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        # Create a file larger than MAX_SKILL_SIZE_KB (500KB)
        content = "---\nname: big\ndescription: big\n---\n" + "x" * (600 * 1024)
        skill_file.write_text(content)

        with pytest.raises(LoadError) as exc:
            loader.load(skill_dir)
        assert "too large" in str(exc.value)

    def test_load_invalid_skill_file(self, loader, tmp_path):
        skill_dir = tmp_path / "invalid-skill"
        skill_dir.mkdir()
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text("Not valid YAML frontmatter")

        with pytest.raises(LoadError) as exc:
            loader.load(skill_dir)
        assert "Missing YAML frontmatter" in str(exc.value)

    def test_load_path_as_string(self, loader, create_skill_file, simple_skill_content):
        skill_dir = create_skill_file("skill", simple_skill_content)
        skill = loader.load(str(skill_dir))  # Pass as string
        assert skill.name == "simple-skill"

    # load_from_content() tests
    def test_load_from_content(self, loader, simple_skill_content):
        skill = loader.load_from_content(simple_skill_content)

        assert skill.name == "simple-skill"
        assert skill.path == "<memory>"
        assert skill.source == "cache"  # Default

    def test_load_from_content_custom_path(self, loader, simple_skill_content):
        skill = loader.load_from_content(
            simple_skill_content,
            path="/remote/skill",
            source="global",
            location_type=".claude",
        )
        assert skill.path == "/remote/skill"
        assert skill.source == "global"
        assert skill.location_type == ".claude"

    def test_load_from_content_invalid(self, loader):
        with pytest.raises(ParseError):
            loader.load_from_content("Invalid content")

    # validate_structure() tests
    def test_validate_structure_valid(self, loader, create_skill_file, simple_skill_content):
        skill_dir = create_skill_file("valid-skill", simple_skill_content)
        errors = loader.validate_structure(skill_dir)
        assert errors == []

    def test_validate_structure_nonexistent(self, loader, tmp_path):
        errors = loader.validate_structure(tmp_path / "nonexistent")
        assert "does not exist" in errors[0]

    def test_validate_structure_not_directory(self, loader, tmp_path):
        file_path = tmp_path / "file"
        file_path.write_text("content")
        errors = loader.validate_structure(file_path)
        assert "not a directory" in errors[0]

    def test_validate_structure_missing_skill_file(self, loader, tmp_path):
        skill_dir = tmp_path / "empty"
        skill_dir.mkdir()
        errors = loader.validate_structure(skill_dir)
        assert any("Missing SKILL.md" in e for e in errors)

    def test_validate_structure_invalid_skill_file(self, loader, tmp_path):
        skill_dir = tmp_path / "invalid"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("invalid yaml {{{{")
        errors = loader.validate_structure(skill_dir)
        assert any("Invalid SKILL.md" in e for e in errors)

    def test_validate_structure_suspicious_files(self, loader, create_skill_file, simple_skill_content):
        skill_dir = create_skill_file("suspicious", simple_skill_content)

        # Add suspicious files
        (skill_dir / ".env").write_text("SECRET=abc")
        (skill_dir / "credentials.json").write_text("{}")

        errors = loader.validate_structure(skill_dir)
        assert any(".env" in e for e in errors)
        assert any("credentials" in e for e in errors)

    def test_validate_structure_references_as_file(self, loader, create_skill_file, simple_skill_content):
        skill_dir = create_skill_file("bad-refs", simple_skill_content)
        (skill_dir / "references").write_text("not a directory")

        errors = loader.validate_structure(skill_dir)
        assert any("'references'" in e and "not a directory" in e for e in errors)

    # list_skill_dirs() tests
    def test_list_skill_dirs_empty(self, loader, tmp_path):
        dirs = loader.list_skill_dirs(tmp_path)
        assert dirs == []

    def test_list_skill_dirs_single(self, loader, create_skill_file, simple_skill_content, tmp_skills_dir):
        create_skill_file("skill-a", simple_skill_content)
        dirs = loader.list_skill_dirs(tmp_skills_dir)
        assert len(dirs) == 1
        assert dirs[0].name == "skill-a"

    def test_list_skill_dirs_multiple(self, loader, tmp_skills_dir, simple_skill_content):
        for name in ["alpha", "beta", "gamma"]:
            skill_dir = tmp_skills_dir / name
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(simple_skill_content.replace("simple-skill", name))

        dirs = loader.list_skill_dirs(tmp_skills_dir)
        assert len(dirs) == 3
        names = [d.name for d in dirs]
        assert "alpha" in names
        assert "beta" in names
        assert "gamma" in names

    def test_list_skill_dirs_returns_sorted(self, loader, tmp_skills_dir, simple_skill_content):
        for name in ["zebra", "alpha", "mango"]:
            skill_dir = tmp_skills_dir / name
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(simple_skill_content)

        dirs = loader.list_skill_dirs(tmp_skills_dir)
        names = [d.name for d in dirs]
        assert names == sorted(names)

    def test_list_skill_dirs_ignores_non_skills(self, loader, tmp_skills_dir, simple_skill_content):
        # Create one skill
        skill_dir = tmp_skills_dir / "real-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(simple_skill_content)

        # Create non-skill directories
        (tmp_skills_dir / "not-a-skill").mkdir()
        (tmp_skills_dir / "another").mkdir()
        (tmp_skills_dir / "README.md").write_text("Not a skill")

        dirs = loader.list_skill_dirs(tmp_skills_dir)
        assert len(dirs) == 1
        assert dirs[0].name == "real-skill"

    def test_list_skill_dirs_base_is_skill(self, loader, tmp_path, simple_skill_content):
        # When base_path itself contains SKILL.md
        (tmp_path / "SKILL.md").write_text(simple_skill_content)
        dirs = loader.list_skill_dirs(tmp_path)
        assert len(dirs) == 1
        assert dirs[0] == tmp_path

    def test_list_skill_dirs_nonexistent(self, loader, tmp_path):
        dirs = loader.list_skill_dirs(tmp_path / "nonexistent")
        assert dirs == []


class TestGetLoader:
    """Tests for get_loader singleton."""

    def test_returns_loader_instance(self):
        loader = get_loader()
        assert isinstance(loader, SkillLoader)

    def test_returns_same_instance(self):
        loader1 = get_loader()
        loader2 = get_loader()
        assert loader1 is loader2


class TestLoadError:
    """Tests for LoadError exception."""

    def test_error_message(self):
        error = LoadError("File not found")
        assert str(error) == "File not found"
        assert error.path is None

    def test_error_with_path(self):
        error = LoadError("Invalid content", path="/path/to/skill")
        assert "/path/to/skill" in str(error)
        assert "Invalid content" in str(error)
        assert error.path == "/path/to/skill"


class TestValidationError:
    """Tests for ValidationError exception."""

    def test_error_message(self):
        error = ValidationError("Validation failed")
        assert str(error) == "Validation failed"
        assert error.errors == ["Validation failed"]

    def test_error_with_multiple_errors(self):
        errors = ["Error 1", "Error 2", "Error 3"]
        error = ValidationError("Multiple errors", errors=errors)
        assert error.errors == errors

"""Tests for skill models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from aiskills.models.skill import (
    Skill,
    SkillAuthor,
    SkillIndex,
    SkillManifest,
    SkillMetadata,
    SkillRequirements,
    SkillStability,
    SkillTrigger,
)


class TestSkillAuthor:
    """Tests for SkillAuthor model."""

    def test_author_with_name_only(self):
        author = SkillAuthor(name="John Doe")
        assert author.name == "John Doe"
        assert author.email is None
        assert author.url is None

    def test_author_with_all_fields(self):
        author = SkillAuthor(
            name="Jane Doe",
            email="jane@example.com",
            url="https://jane.dev",
        )
        assert author.name == "Jane Doe"
        assert author.email == "jane@example.com"
        assert author.url == "https://jane.dev"

    def test_author_requires_name(self):
        with pytest.raises(ValidationError):
            SkillAuthor()


class TestSkillTrigger:
    """Tests for SkillTrigger model."""

    def test_trigger_with_pattern(self):
        trigger = SkillTrigger(pattern=r"debug|breakpoint")
        assert trigger.pattern == r"debug|breakpoint"
        assert trigger.file_pattern is None

    def test_trigger_with_file_pattern(self):
        trigger = SkillTrigger(file_pattern="*.py")
        assert trigger.file_pattern == "*.py"
        assert trigger.pattern is None

    def test_trigger_with_multiple_fields(self):
        trigger = SkillTrigger(
            pattern=r"error",
            file_pattern="*.log",
            condition="severity:high",
        )
        assert trigger.pattern == r"error"
        assert trigger.file_pattern == "*.log"
        assert trigger.condition == "severity:high"


class TestSkillRequirements:
    """Tests for SkillRequirements model."""

    def test_empty_requirements(self):
        reqs = SkillRequirements()
        assert reqs.tools == []
        assert reqs.packages == []
        assert reqs.min_python_version is None

    def test_requirements_with_tools(self):
        reqs = SkillRequirements(tools=["git", "docker"])
        assert "git" in reqs.tools
        assert "docker" in reqs.tools

    def test_requirements_with_packages(self):
        reqs = SkillRequirements(
            packages=["numpy", "pandas"],
            min_python_version="3.10",
        )
        assert "numpy" in reqs.packages
        assert reqs.min_python_version == "3.10"


class TestSkillMetadata:
    """Tests for SkillMetadata model."""

    def test_default_metadata(self):
        meta = SkillMetadata()
        assert meta.stability == SkillStability.STABLE
        assert meta.created_at is None
        assert meta.min_aiskills_version is None

    def test_metadata_with_stability(self):
        meta = SkillMetadata(stability=SkillStability.EXPERIMENTAL)
        assert meta.stability == SkillStability.EXPERIMENTAL

    def test_metadata_stability_values(self):
        assert SkillStability.EXPERIMENTAL.value == "experimental"
        assert SkillStability.BETA.value == "beta"
        assert SkillStability.STABLE.value == "stable"
        assert SkillStability.DEPRECATED.value == "deprecated"


class TestSkillManifest:
    """Tests for SkillManifest model."""

    def test_minimal_manifest(self):
        manifest = SkillManifest(
            name="test-skill",
            description="A test skill",
        )
        assert manifest.name == "test-skill"
        assert manifest.description == "A test skill"
        assert manifest.version == "1.0.0"  # Default
        assert manifest.tags == []
        assert manifest.dependencies == []

    def test_manifest_with_all_fields(self):
        manifest = SkillManifest(
            name="advanced-skill",
            description="An advanced test skill",
            version="2.1.0",
            tags=["python", "debugging"],
            category="development/testing",
            authors=[SkillAuthor(name="Test Author")],
            license="MIT",
        )
        assert manifest.name == "advanced-skill"
        assert manifest.version == "2.1.0"
        assert "python" in manifest.tags
        assert manifest.category == "development/testing"
        assert len(manifest.authors) == 1

    def test_manifest_requires_name(self):
        with pytest.raises(ValidationError):
            SkillManifest(description="Missing name")

    def test_manifest_requires_description(self):
        with pytest.raises(ValidationError):
            SkillManifest(name="missing-description")

    def test_has_dependencies_false(self):
        manifest = SkillManifest(name="test", description="test")
        assert manifest.has_dependencies is False

    def test_has_dependencies_true(self):
        from aiskills.models.dependency import SkillDependency

        manifest = SkillManifest(
            name="test",
            description="test",
            dependencies=[SkillDependency(name="other-skill")],
        )
        assert manifest.has_dependencies is True

    def test_has_composition_false(self):
        manifest = SkillManifest(name="test", description="test")
        assert manifest.has_composition is False

    def test_has_composition_with_extends(self):
        manifest = SkillManifest(
            name="test",
            description="test",
            extends="base-skill",
        )
        assert manifest.has_composition is True

    def test_has_composition_with_includes(self):
        manifest = SkillManifest(
            name="test",
            description="test",
            includes=["helper-skill"],
        )
        assert manifest.has_composition is True

    def test_has_variables_false(self):
        manifest = SkillManifest(name="test", description="test")
        assert manifest.has_variables is False

    def test_has_variables_true(self):
        from aiskills.models.variable import SkillVariable

        manifest = SkillManifest(
            name="test",
            description="test",
            variables={"lang": SkillVariable(type="string", default="python")},
        )
        assert manifest.has_variables is True


class TestSkill:
    """Tests for Skill model."""

    def test_skill_creation(self, sample_manifest, tmp_path):
        skill = Skill(
            manifest=sample_manifest,
            content="# Test\n\nContent here.",
            raw_content="---\nname: test\n---\n# Test",
            path=str(tmp_path),
        )
        assert skill.name == sample_manifest.name
        assert skill.version == sample_manifest.version
        assert skill.description == sample_manifest.description
        assert skill.source == "project"  # Default
        assert skill.content_hash != ""  # Computed

    def test_skill_content_hash_computed(self, sample_manifest, tmp_path):
        raw = "---\nname: test\n---\n# Content"
        skill = Skill(
            manifest=sample_manifest,
            content="# Content",
            raw_content=raw,
            path=str(tmp_path),
        )
        # Hash should be 16 chars (truncated SHA-256)
        assert len(skill.content_hash) == 16
        assert skill.content_hash.isalnum()

    def test_skill_different_content_different_hash(self, sample_manifest, tmp_path):
        skill1 = Skill(
            manifest=sample_manifest,
            content="Content 1",
            raw_content="---\nname: test\n---\nContent 1",
            path=str(tmp_path),
        )
        skill2 = Skill(
            manifest=sample_manifest,
            content="Content 2",
            raw_content="---\nname: test\n---\nContent 2",
            path=str(tmp_path),
        )
        assert skill1.content_hash != skill2.content_hash

    def test_skill_to_index(self, sample_skill):
        index = sample_skill.to_index()
        assert isinstance(index, SkillIndex)
        assert index.name == sample_skill.name
        assert index.version == sample_skill.version
        assert index.description == sample_skill.description
        assert index.path == sample_skill.path
        assert index.content_hash == sample_skill.content_hash

    def test_skill_sources(self, sample_manifest, tmp_path):
        for source in ["project", "global", "cache"]:
            skill = Skill(
                manifest=sample_manifest,
                content="test",
                raw_content="test",
                path=str(tmp_path),
                source=source,
            )
            assert skill.source == source

    def test_skill_location_types(self, sample_manifest, tmp_path):
        for loc_type in [".aiskills", ".claude", ".agent"]:
            skill = Skill(
                manifest=sample_manifest,
                content="test",
                raw_content="test",
                path=str(tmp_path),
                location_type=loc_type,
            )
            assert skill.location_type == loc_type


class TestSkillIndex:
    """Tests for SkillIndex model."""

    def test_skill_index_creation(self):
        index = SkillIndex(
            id="abc123",
            name="test-skill",
            description="A test skill",
            version="1.0.0",
            tags=["test"],
            source="project",
            path="/path/to/skill",
            content_hash="abcdef1234567890",
        )
        assert index.name == "test-skill"
        assert index.display_name == "test-skill@1.0.0"

    def test_skill_index_display_name(self):
        index = SkillIndex(
            id="1",
            name="my-skill",
            description="desc",
            version="2.3.4",
            source="global",
            path="/path",
            content_hash="hash",
        )
        assert index.display_name == "my-skill@2.3.4"

    def test_skill_index_optional_fields(self):
        index = SkillIndex(
            id="1",
            name="skill",
            description="desc",
            version="1.0.0",
            source="project",
            path="/path",
            content_hash="hash",
        )
        assert index.tags == []
        assert index.category is None
        assert index.embedding_id is None

    def test_skill_index_with_embedding(self):
        index = SkillIndex(
            id="1",
            name="skill",
            description="desc",
            version="1.0.0",
            source="project",
            path="/path",
            content_hash="hash",
            embedding_id="emb_123",
        )
        assert index.embedding_id == "emb_123"

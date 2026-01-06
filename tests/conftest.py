"""Global test fixtures for aiskills."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

import pytest

from aiskills.config import AppConfig, EmbeddingConfig, StorageConfig, VectorStoreConfig
from aiskills.models.skill import Skill, SkillIndex, SkillManifest

if TYPE_CHECKING:
    from collections.abc import Generator


# =============================================================================
# Path Fixtures
# =============================================================================


@pytest.fixture
def fixtures_dir() -> Path:
    """Return path to test fixtures directory."""
    return Path(__file__).parent / "fixtures"


@pytest.fixture
def valid_skills_dir(fixtures_dir: Path) -> Path:
    """Return path to valid skill fixtures."""
    return fixtures_dir / "valid"


@pytest.fixture
def invalid_skills_dir(fixtures_dir: Path) -> Path:
    """Return path to invalid skill fixtures."""
    return fixtures_dir / "invalid"


# =============================================================================
# Temporary Directory Fixtures
# =============================================================================


@pytest.fixture
def tmp_skills_dir(tmp_path: Path) -> Path:
    """Create a temporary skills directory structure."""
    skills_dir = tmp_path / ".aiskills" / "skills"
    skills_dir.mkdir(parents=True)
    return skills_dir


@pytest.fixture
def tmp_global_dir(tmp_path: Path) -> Path:
    """Create a temporary global aiskills directory."""
    global_dir = tmp_path / "global_aiskills"
    global_dir.mkdir(parents=True)
    (global_dir / "skills").mkdir()
    (global_dir / "cache").mkdir()
    (global_dir / "registry").mkdir()
    return global_dir


@pytest.fixture
def tmp_project_dir(tmp_path: Path) -> Path:
    """Create a temporary project directory with aiskills structure."""
    project_dir = tmp_path / "test_project"
    project_dir.mkdir(parents=True)
    (project_dir / ".aiskills" / "skills").mkdir(parents=True)
    return project_dir


# =============================================================================
# Configuration Fixtures
# =============================================================================


@pytest.fixture
def mock_config(tmp_global_dir: Path, tmp_path: Path) -> AppConfig:
    """Create a test configuration with temporary paths."""
    return AppConfig(
        storage=StorageConfig(
            global_dir=tmp_global_dir,
            project_dir=".aiskills",
        ),
        embedding=EmbeddingConfig(
            provider="none",  # Disable embeddings for unit tests
        ),
        vector_store=VectorStoreConfig(
            provider="none",  # Disable vector store for unit tests
            path=tmp_path / "vectors",
        ),
        auto_install_deps=False,
        validate_on_load=True,
        use_cache=False,
    )


@pytest.fixture
def mock_config_with_embeddings(tmp_global_dir: Path, tmp_path: Path) -> AppConfig:
    """Create a test configuration with embeddings enabled."""
    return AppConfig(
        storage=StorageConfig(
            global_dir=tmp_global_dir,
            project_dir=".aiskills",
        ),
        embedding=EmbeddingConfig(
            provider="fastembed",
            model="BAAI/bge-small-en-v1.5",
        ),
        vector_store=VectorStoreConfig(
            provider="chroma",
            path=tmp_path / "vectors",
        ),
        auto_install_deps=False,
        validate_on_load=True,
        use_cache=True,
    )


# =============================================================================
# Sample Skill Fixtures
# =============================================================================


SIMPLE_SKILL_MD = """\
---
name: simple-skill
description: A simple test skill for unit tests.
version: 1.0.0
tags: [test, simple]
---

# Simple Skill

This is a simple skill for testing purposes.

## Usage

Just use it!
"""


SKILL_WITH_VARIABLES_MD = """\
---
name: skill-with-variables
description: A skill that uses template variables.
version: 2.0.0
tags: [test, templates]
variables:
  language:
    type: string
    default: python
    enum: [python, javascript, rust, go]
  include_examples:
    type: boolean
    default: true
  max_depth:
    type: integer
    default: 5
    min: 1
    max: 10
---

# Skill for {{ language }}

This skill is configured for {{ language }}.

{% if include_examples %}
## Examples

Here are some examples for {{ language }}:

```{{ language }}
# Example code
```
{% endif %}

Max depth: {{ max_depth }}
"""


SKILL_WITH_DEPENDENCIES_MD = """\
---
name: skill-with-deps
description: A skill with dependencies on other skills.
version: 1.5.0
tags: [test, dependencies]
dependencies:
  - name: base-skill
    version: ">=1.0.0"
  - name: optional-skill
    version: "^2.0.0"
    optional: true
---

# Skill with Dependencies

This skill depends on other skills.
"""


SKILL_WITH_COMPOSITION_MD = """\
---
name: composed-skill
description: A skill that extends and includes other skills.
version: 3.0.0
tags: [test, composition]
extends: base-skill
includes:
  - helper-skill
  - utils-skill
---

# Composed Skill

This skill is composed from multiple skills.
"""


@pytest.fixture
def simple_skill_content() -> str:
    """Return content for a simple SKILL.md."""
    return SIMPLE_SKILL_MD


@pytest.fixture
def skill_with_variables_content() -> str:
    """Return content for a skill with variables."""
    return SKILL_WITH_VARIABLES_MD


@pytest.fixture
def skill_with_dependencies_content() -> str:
    """Return content for a skill with dependencies."""
    return SKILL_WITH_DEPENDENCIES_MD


@pytest.fixture
def skill_with_composition_content() -> str:
    """Return content for a composed skill."""
    return SKILL_WITH_COMPOSITION_MD


@pytest.fixture
def sample_manifest() -> SkillManifest:
    """Create a sample SkillManifest for testing."""
    return SkillManifest(
        name="test-skill",
        description="A test skill for unit tests.",
        version="1.0.0",
        tags=["test", "sample"],
        category="testing",
    )


@pytest.fixture
def sample_skill(sample_manifest: SkillManifest, tmp_path: Path) -> Skill:
    """Create a sample Skill instance for testing."""
    skill_dir = tmp_path / "test-skill"
    skill_dir.mkdir(parents=True)

    return Skill(
        manifest=sample_manifest,
        content="# Test Skill\n\nThis is test content.",
        raw_content=SIMPLE_SKILL_MD,
        path=str(skill_dir),
        source="project",
        location_type=".aiskills",
    )


@pytest.fixture
def sample_skill_index(sample_skill: Skill) -> SkillIndex:
    """Create a sample SkillIndex from the sample skill."""
    return sample_skill.to_index()


# =============================================================================
# File System Fixtures
# =============================================================================


@pytest.fixture
def create_skill_file(tmp_skills_dir: Path):
    """Factory fixture to create skill files in the temp directory."""

    def _create(name: str, content: str) -> Path:
        skill_dir = tmp_skills_dir / name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_file = skill_dir / "SKILL.md"
        skill_file.write_text(content)
        return skill_dir

    return _create


@pytest.fixture
def populated_skills_dir(
    tmp_skills_dir: Path,
    simple_skill_content: str,
    skill_with_variables_content: str,
) -> Path:
    """Create a skills directory with multiple skills."""
    # Create simple skill
    simple_dir = tmp_skills_dir / "simple-skill"
    simple_dir.mkdir()
    (simple_dir / "SKILL.md").write_text(simple_skill_content)

    # Create skill with variables
    vars_dir = tmp_skills_dir / "skill-with-variables"
    vars_dir.mkdir()
    (vars_dir / "SKILL.md").write_text(skill_with_variables_content)

    return tmp_skills_dir


# =============================================================================
# Environment Fixtures
# =============================================================================


@pytest.fixture
def clean_env() -> Generator[None, None, None]:
    """Ensure clean environment without aiskills env vars."""
    # Store original env vars
    original = {k: v for k, v in os.environ.items() if k.startswith("AISKILLS_")}

    # Remove aiskills env vars
    for key in original:
        del os.environ[key]

    yield

    # Restore original env vars
    os.environ.update(original)


@pytest.fixture
def env_with_vars() -> Generator[dict[str, str], None, None]:
    """Set up environment with aiskills variables."""
    test_vars = {
        "AISKILLS_LANGUAGE": "python",
        "AISKILLS_DEBUG": "true",
    }

    # Store original
    original = {k: os.environ.get(k) for k in test_vars}

    # Set test vars
    os.environ.update(test_vars)

    yield test_vars

    # Restore
    for key, value in original.items():
        if value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = value


# =============================================================================
# Cleanup Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_global_config():
    """Reset global config after each test."""
    from aiskills import config

    original = config._config
    yield
    config._config = original

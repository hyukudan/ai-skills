"""Tests for YAML frontmatter parser."""

from __future__ import annotations

import pytest

from aiskills.core.parser import ParseError, ParseResult, YAMLParser, get_parser


class TestYAMLParser:
    """Tests for YAMLParser class."""

    @pytest.fixture
    def parser(self):
        return YAMLParser()

    # Basic parsing tests
    def test_parse_simple_skill(self, parser, simple_skill_content):
        result = parser.parse(simple_skill_content)
        assert isinstance(result, ParseResult)
        assert result.manifest.name == "simple-skill"
        assert result.manifest.description == "A simple test skill for unit tests."
        assert result.manifest.version == "1.0.0"
        assert "test" in result.manifest.tags
        assert "Simple Skill" in result.content

    def test_parse_returns_raw_content(self, parser, simple_skill_content):
        result = parser.parse(simple_skill_content)
        assert result.raw_content == simple_skill_content

    def test_parse_strips_content(self, parser):
        content = """\
---
name: test
description: test
---

  Content with whitespace

"""
        result = parser.parse(content)
        assert result.content == "Content with whitespace"

    # Frontmatter validation tests
    def test_parse_missing_frontmatter(self, parser):
        content = "# No frontmatter here\n\nJust markdown."
        with pytest.raises(ParseError) as exc:
            parser.parse(content)
        assert "Missing YAML frontmatter" in str(exc.value)

    def test_parse_unclosed_frontmatter(self, parser):
        content = """\
---
name: test
description: test
# Missing closing ---
"""
        with pytest.raises(ParseError) as exc:
            parser.parse(content)
        assert "Unclosed frontmatter" in str(exc.value)

    def test_parse_invalid_yaml(self, parser):
        content = """\
---
name: test
description: [unclosed bracket
---
"""
        with pytest.raises(ParseError) as exc:
            parser.parse(content)
        assert "Invalid YAML" in str(exc.value)

    def test_parse_frontmatter_not_dict(self, parser):
        content = """\
---
- item1
- item2
---
"""
        with pytest.raises(ParseError) as exc:
            parser.parse(content)
        assert "must be a YAML mapping" in str(exc.value)

    # Required field validation
    def test_parse_missing_name(self, parser):
        content = """\
---
description: A skill without a name
version: 1.0.0
---
"""
        with pytest.raises(ParseError) as exc:
            parser.parse(content)
        assert "Missing required field: name" in str(exc.value)

    def test_parse_missing_description(self, parser):
        content = """\
---
name: no-description
version: 1.0.0
---
"""
        with pytest.raises(ParseError) as exc:
            parser.parse(content)
        assert "Missing required field: description" in str(exc.value)

    # Default values
    def test_parse_default_version(self, parser):
        content = """\
---
name: test
description: test
---
"""
        result = parser.parse(content)
        assert result.manifest.version == "1.0.0"

    def test_parse_default_tags_empty(self, parser):
        content = """\
---
name: test
description: test
---
"""
        result = parser.parse(content)
        assert result.manifest.tags == []

    # Multiline strings
    def test_parse_multiline_description_literal(self, parser):
        content = """\
---
name: test
description: |
  This is a multiline
  description using literal style.
  It preserves newlines.
---
"""
        result = parser.parse(content)
        assert "multiline" in result.manifest.description
        assert "\n" in result.manifest.description

    def test_parse_multiline_description_folded(self, parser):
        content = """\
---
name: test
description: >
  This is a folded
  multiline description.
---
"""
        result = parser.parse(content)
        assert "folded" in result.manifest.description

    # Authors parsing
    def test_parse_authors_string_list(self, parser):
        content = """\
---
name: test
description: test
authors:
  - John Doe
  - Jane Smith
---
"""
        result = parser.parse(content)
        assert len(result.manifest.authors) == 2
        assert result.manifest.authors[0].name == "John Doe"
        assert result.manifest.authors[1].name == "Jane Smith"

    def test_parse_authors_dict_list(self, parser):
        content = """\
---
name: test
description: test
authors:
  - name: John Doe
    email: john@example.com
    url: https://john.dev
---
"""
        result = parser.parse(content)
        assert result.manifest.authors[0].name == "John Doe"
        assert result.manifest.authors[0].email == "john@example.com"
        assert result.manifest.authors[0].url == "https://john.dev"

    # Dependencies parsing
    def test_parse_dependencies_string_list(self, parser):
        content = """\
---
name: test
description: test
dependencies:
  - base-skill
  - helper-skill
---
"""
        result = parser.parse(content)
        assert len(result.manifest.dependencies) == 2
        assert result.manifest.dependencies[0].name == "base-skill"
        assert result.manifest.dependencies[0].version == "*"

    def test_parse_dependencies_with_version_string(self, parser):
        content = """\
---
name: test
description: test
dependencies:
  - base-skill@^1.0.0
  - helper@>=2.0.0
---
"""
        result = parser.parse(content)
        assert result.manifest.dependencies[0].name == "base-skill"
        assert result.manifest.dependencies[0].version == "^1.0.0"
        assert result.manifest.dependencies[1].name == "helper"
        assert result.manifest.dependencies[1].version == ">=2.0.0"

    def test_parse_dependencies_dict_format(self, parser):
        content = """\
---
name: test
description: test
dependencies:
  - name: required-skill
    version: ">=1.0.0"
  - name: optional-skill
    version: "^2.0.0"
    optional: true
---
"""
        result = parser.parse(content)
        assert result.manifest.dependencies[0].name == "required-skill"
        assert result.manifest.dependencies[0].optional is False
        assert result.manifest.dependencies[1].name == "optional-skill"
        assert result.manifest.dependencies[1].optional is True

    # Variables parsing
    def test_parse_variables_full_spec(self, parser, skill_with_variables_content):
        result = parser.parse(skill_with_variables_content)
        vars = result.manifest.variables

        assert "language" in vars
        assert vars["language"].type == "string"
        assert vars["language"].default == "python"
        assert vars["language"].enum == ["python", "javascript", "rust", "go"]

        assert "include_examples" in vars
        assert vars["include_examples"].type == "boolean"
        assert vars["include_examples"].default is True

        assert "max_depth" in vars
        assert vars["max_depth"].type == "integer"
        assert vars["max_depth"].min == 1
        assert vars["max_depth"].max == 10

    def test_parse_variables_simple_default(self, parser):
        content = """\
---
name: test
description: test
variables:
  language: python
  count: 5
  enabled: true
---
"""
        result = parser.parse(content)
        vars = result.manifest.variables
        assert vars["language"].default == "python"
        assert vars["count"].default == 5
        assert vars["enabled"].default is True

    # Triggers parsing
    def test_parse_triggers_string_list(self, parser):
        content = """\
---
name: test
description: test
triggers:
  - "debug|breakpoint"
  - "error|exception"
---
"""
        result = parser.parse(content)
        assert len(result.manifest.triggers) == 2
        assert result.manifest.triggers[0].pattern == "debug|breakpoint"

    def test_parse_triggers_dict_format(self, parser):
        content = """\
---
name: test
description: test
triggers:
  - pattern: "test|spec"
    file_pattern: "*.test.py"
---
"""
        result = parser.parse(content)
        assert result.manifest.triggers[0].pattern == "test|spec"
        assert result.manifest.triggers[0].file_pattern == "*.test.py"

    # Conflicts parsing
    def test_parse_conflicts(self, parser):
        content = """\
---
name: test
description: test
conflicts:
  - old-skill
  - name: deprecated-skill
    version: "<1.0.0"
    reason: API changed
---
"""
        result = parser.parse(content)
        assert len(result.manifest.conflicts) == 2
        assert result.manifest.conflicts[0].name == "old-skill"
        assert result.manifest.conflicts[1].version == "<1.0.0"
        assert result.manifest.conflicts[1].reason == "API changed"

    # Composition fields
    def test_parse_extends(self, parser):
        content = """\
---
name: test
description: test
extends: base-skill
---
"""
        result = parser.parse(content)
        assert result.manifest.extends == "base-skill"

    def test_parse_includes(self, parser):
        content = """\
---
name: test
description: test
includes:
  - helper-a
  - helper-b
---
"""
        result = parser.parse(content)
        assert result.manifest.includes == ["helper-a", "helper-b"]

    # Requirements parsing
    def test_parse_requirements(self, parser):
        content = """\
---
name: test
description: test
requirements:
  tools:
    - git
    - docker
  packages:
    - numpy
  min_python_version: "3.10"
---
"""
        result = parser.parse(content)
        reqs = result.manifest.requirements
        assert "git" in reqs.tools
        assert "numpy" in reqs.packages
        assert reqs.min_python_version == "3.10"

    # Metadata parsing
    def test_parse_metadata(self, parser):
        content = """\
---
name: test
description: test
metadata:
  stability: experimental
  created_at: "2024-01-01"
  min_aiskills_version: "0.5.0"
---
"""
        result = parser.parse(content)
        meta = result.manifest.metadata
        assert meta.stability.value == "experimental"
        assert meta.created_at == "2024-01-01"
        assert meta.min_aiskills_version == "0.5.0"

    # Context field
    def test_parse_context(self, parser):
        content = """\
---
name: test
description: test
context: |
  Use this skill when debugging Python apps.
  Good for error tracing and profiling.
---
"""
        result = parser.parse(content)
        assert "debugging Python" in result.manifest.context

    # Category field
    def test_parse_category(self, parser):
        content = """\
---
name: test
description: test
category: development/debugging
---
"""
        result = parser.parse(content)
        assert result.manifest.category == "development/debugging"


class TestGetParser:
    """Tests for get_parser singleton."""

    def test_returns_parser_instance(self):
        parser = get_parser()
        assert isinstance(parser, YAMLParser)

    def test_returns_same_instance(self):
        parser1 = get_parser()
        parser2 = get_parser()
        assert parser1 is parser2


class TestParseError:
    """Tests for ParseError exception."""

    def test_error_message(self):
        error = ParseError("Something went wrong")
        assert str(error) == "Something went wrong"

    def test_error_with_line_number(self):
        error = ParseError("Invalid syntax", line=42)
        assert "Line 42" in str(error)
        assert "Invalid syntax" in str(error)
        assert error.line == 42

    def test_error_no_line_number(self):
        error = ParseError("General error")
        assert error.line is None

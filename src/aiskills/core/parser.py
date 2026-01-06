"""YAML frontmatter parser for SKILL.md files."""

from __future__ import annotations

import re
from dataclasses import dataclass

import yaml

from ..constants import FRONTMATTER_DELIMITER
from ..models.dependency import SkillConflict, SkillDependency
from ..models.skill import (
    SkillAuthor,
    SkillManifest,
    SkillMetadata,
    SkillRequirements,
    SkillStability,
    SkillTrigger,
)
from ..models.variable import SkillVariable


@dataclass
class ParseResult:
    """Result of parsing a SKILL.md file."""

    manifest: SkillManifest
    content: str
    raw_content: str


class ParseError(Exception):
    """Error parsing SKILL.md file."""

    def __init__(self, message: str, line: int | None = None):
        self.line = line
        if line:
            message = f"Line {line}: {message}"
        super().__init__(message)


class YAMLParser:
    """Parser for SKILL.md YAML frontmatter.

    Handles the full YAML spec including:
    - Multiline strings (| and >)
    - Arrays and objects
    - Nested structures
    - Custom types (dependencies, variables, etc.)
    """

    def parse(self, content: str) -> ParseResult:
        """Parse a SKILL.md file into manifest and content.

        Args:
            content: Full content of SKILL.md file

        Returns:
            ParseResult with manifest, content, and raw_content

        Raises:
            ParseError: If parsing fails
        """
        raw_content = content
        frontmatter_str, markdown_content = self._split_frontmatter(content)

        if not frontmatter_str:
            raise ParseError("Missing YAML frontmatter (file must start with ---)")

        try:
            frontmatter_data = yaml.safe_load(frontmatter_str)
        except yaml.YAMLError as e:
            raise ParseError(f"Invalid YAML: {e}") from e

        if not isinstance(frontmatter_data, dict):
            raise ParseError("Frontmatter must be a YAML mapping (key: value)")

        manifest = self._parse_manifest(frontmatter_data)

        return ParseResult(
            manifest=manifest,
            content=markdown_content.strip(),
            raw_content=raw_content,
        )

    def _split_frontmatter(self, content: str) -> tuple[str | None, str]:
        """Split content into frontmatter and markdown body.

        Returns:
            Tuple of (frontmatter_string, content_string)
            frontmatter_string is None if no frontmatter found
        """
        content = content.strip()

        if not content.startswith(FRONTMATTER_DELIMITER):
            return None, content

        # Find the closing delimiter
        # The pattern matches: ---\n<yaml>\n---
        pattern = rf"^{FRONTMATTER_DELIMITER}\s*\n(.*?)\n{FRONTMATTER_DELIMITER}\s*\n?"
        match = re.match(pattern, content, re.DOTALL)

        if not match:
            # Check if frontmatter is never closed
            if content.count(f"\n{FRONTMATTER_DELIMITER}") == 0:
                raise ParseError("Unclosed frontmatter (missing closing ---)")
            return None, content

        frontmatter = match.group(1)
        markdown = content[match.end() :]

        return frontmatter, markdown

    def _parse_manifest(self, data: dict) -> SkillManifest:
        """Parse frontmatter dict into SkillManifest."""
        # Validate required fields
        if "name" not in data:
            raise ParseError("Missing required field: name")
        if "description" not in data:
            raise ParseError("Missing required field: description")

        # Parse complex nested structures
        authors = self._parse_authors(data.get("authors", []))
        dependencies = self._parse_dependencies(data.get("dependencies", []))
        conflicts = self._parse_conflicts(data.get("conflicts", []))
        variables = self._parse_variables(data.get("variables", {}))
        triggers = self._parse_triggers(data.get("triggers", []))
        requirements = self._parse_requirements(data.get("requirements"))
        metadata = self._parse_metadata(data.get("metadata", {}))

        return SkillManifest(
            name=data["name"],
            description=data["description"],
            version=data.get("version", "1.0.0"),
            authors=authors,
            license=data.get("license"),
            tags=data.get("tags", []),
            category=data.get("category"),
            dependencies=dependencies,
            conflicts=conflicts,
            extends=data.get("extends"),
            includes=data.get("includes", []),
            variables=variables,
            context=data.get("context"),
            triggers=triggers,
            requirements=requirements,
            metadata=metadata,
        )

    def _parse_authors(self, data: list) -> list[SkillAuthor]:
        """Parse authors list."""
        authors = []
        for item in data:
            if isinstance(item, str):
                authors.append(SkillAuthor(name=item))
            elif isinstance(item, dict):
                authors.append(SkillAuthor(**item))
        return authors

    def _parse_dependencies(self, data: list) -> list[SkillDependency]:
        """Parse dependencies list.

        Supports formats:
        - "skill-name" (any version)
        - "skill-name@^1.0.0"
        - {name: "skill-name", version: ">=1.0.0", optional: true}
        """
        deps = []
        for item in data:
            if isinstance(item, str):
                # Parse "name@version" format
                if "@" in item:
                    name, version = item.rsplit("@", 1)
                    deps.append(SkillDependency(name=name, version=version))
                else:
                    deps.append(SkillDependency(name=item))
            elif isinstance(item, dict):
                deps.append(SkillDependency(**item))
        return deps

    def _parse_conflicts(self, data: list) -> list[SkillConflict]:
        """Parse conflicts list."""
        conflicts = []
        for item in data:
            if isinstance(item, str):
                conflicts.append(SkillConflict(name=item))
            elif isinstance(item, dict):
                conflicts.append(SkillConflict(**item))
        return conflicts

    def _parse_variables(self, data: dict) -> dict[str, SkillVariable]:
        """Parse variables dictionary."""
        variables = {}
        for name, spec in data.items():
            if isinstance(spec, dict):
                variables[name] = SkillVariable(**spec)
            else:
                # Simple default value
                variables[name] = SkillVariable(default=spec)
        return variables

    def _parse_triggers(self, data: list) -> list[SkillTrigger]:
        """Parse triggers list."""
        triggers = []
        for item in data:
            if isinstance(item, str):
                triggers.append(SkillTrigger(pattern=item))
            elif isinstance(item, dict):
                triggers.append(SkillTrigger(**item))
        return triggers

    def _parse_requirements(self, data: dict | None) -> SkillRequirements | None:
        """Parse requirements dict."""
        if not data:
            return None
        return SkillRequirements(**data)

    def _parse_metadata(self, data: dict) -> SkillMetadata:
        """Parse metadata dict."""
        # Convert stability string to enum
        if "stability" in data and isinstance(data["stability"], str):
            data["stability"] = SkillStability(data["stability"])
        return SkillMetadata(**data)


# Singleton instance
_parser: YAMLParser | None = None


def get_parser() -> YAMLParser:
    """Get the singleton parser instance."""
    global _parser
    if _parser is None:
        _parser = YAMLParser()
    return _parser

"""Remote registry source for skills.

Fetches skills from a centralized registry API with version management,
semantic versioning support, and update checking.
"""

from __future__ import annotations

import json
import os
import tempfile
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from urllib.parse import urljoin

from ..core.loader import SkillLoader, get_loader
from ..storage.cache import CacheManager, get_cache_manager
from ..utils.version import SemanticVersion, VersionConstraint, find_latest, is_newer
from .base import FetchedSkill, FetchError, SkillSource


@dataclass
class RegistrySkillInfo:
    """Information about a skill in the registry."""

    name: str
    slug: str  # URL-safe identifier
    description: str
    version: str
    versions: list[str] = field(default_factory=list)  # All available versions
    tags: list[str] = field(default_factory=list)
    category: str | None = None
    author: str | None = None
    downloads: int = 0
    stars: int = 0
    updated_at: str | None = None
    homepage: str | None = None
    repository: str | None = None


@dataclass
class RegistrySearchResult:
    """Search result from the registry."""

    skills: list[RegistrySkillInfo]
    total: int
    page: int
    per_page: int


class RegistryClient:
    """HTTP client for skill registry API.

    The registry API provides:
    - Search: GET /api/skills/search?q=query&limit=10
    - List: GET /api/skills?page=1&per_page=20
    - Get: GET /api/skills/{slug}
    - Download: GET /api/skills/{slug}/download?version=1.0.0
    - Versions: GET /api/skills/{slug}/versions
    """

    DEFAULT_REGISTRY = "https://registry.aiskills.dev"

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        timeout: int = 30,
    ):
        self.base_url = (
            base_url
            or os.environ.get("AISKILLS_REGISTRY_URL")
            or self.DEFAULT_REGISTRY
        )
        self.api_key = api_key or os.environ.get("AISKILLS_REGISTRY_KEY")
        self.timeout = timeout
        self._http_client = None

    def _get_client(self):
        """Get or create HTTP client."""
        if self._http_client is None:
            try:
                import httpx
                self._http_client = httpx.Client(timeout=self.timeout)
            except ImportError:
                raise ImportError(
                    "httpx is required for registry access. "
                    "Install with: pip install httpx"
                )
        return self._http_client

    def _headers(self) -> dict[str, str]:
        """Get request headers."""
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _request(self, method: str, path: str, **kwargs) -> dict[str, Any]:
        """Make HTTP request to registry."""
        client = self._get_client()
        url = urljoin(self.base_url, path)

        try:
            response = client.request(
                method, url,
                headers=self._headers(),
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise FetchError(f"Registry request failed: {e}")

    def search(
        self,
        query: str,
        limit: int = 10,
        category: str | None = None,
        tags: list[str] | None = None,
    ) -> RegistrySearchResult:
        """Search for skills in the registry.

        Args:
            query: Search query
            limit: Maximum results
            category: Filter by category
            tags: Filter by tags

        Returns:
            Search results
        """
        params = {"q": query, "limit": limit}
        if category:
            params["category"] = category
        if tags:
            params["tags"] = ",".join(tags)

        data = self._request("GET", "/api/skills/search", params=params)

        skills = [
            RegistrySkillInfo(
                name=s["name"],
                slug=s["slug"],
                description=s.get("description", ""),
                version=s.get("version", "1.0.0"),
                versions=s.get("versions", []),
                tags=s.get("tags", []),
                category=s.get("category"),
                author=s.get("author"),
                downloads=s.get("downloads", 0),
                stars=s.get("stars", 0),
                updated_at=s.get("updated_at"),
            )
            for s in data.get("skills", [])
        ]

        return RegistrySearchResult(
            skills=skills,
            total=data.get("total", len(skills)),
            page=data.get("page", 1),
            per_page=data.get("per_page", limit),
        )

    def get_skill(self, slug: str) -> RegistrySkillInfo:
        """Get skill details by slug.

        Args:
            slug: Skill slug/identifier

        Returns:
            Skill information
        """
        data = self._request("GET", f"/api/skills/{slug}")

        return RegistrySkillInfo(
            name=data["name"],
            slug=data["slug"],
            description=data.get("description", ""),
            version=data.get("version", "1.0.0"),
            versions=data.get("versions", []),
            tags=data.get("tags", []),
            category=data.get("category"),
            author=data.get("author"),
            downloads=data.get("downloads", 0),
            stars=data.get("stars", 0),
            updated_at=data.get("updated_at"),
            homepage=data.get("homepage"),
            repository=data.get("repository"),
        )

    def get_versions(self, slug: str) -> list[str]:
        """Get all available versions for a skill.

        Args:
            slug: Skill slug

        Returns:
            List of version strings (newest first)
        """
        data = self._request("GET", f"/api/skills/{slug}/versions")
        return data.get("versions", [])

    def download(
        self,
        slug: str,
        version: str | None = None,
        target_dir: Path | None = None,
    ) -> Path:
        """Download a skill from the registry.

        Args:
            slug: Skill slug
            version: Specific version (default: latest)
            target_dir: Directory to extract to (default: temp)

        Returns:
            Path to extracted skill directory
        """
        client = self._get_client()

        # Build download URL
        path = f"/api/skills/{slug}/download"
        params = {}
        if version:
            params["version"] = version

        url = urljoin(self.base_url, path)

        try:
            response = client.get(
                url,
                headers=self._headers(),
                params=params,
                follow_redirects=True,
            )
            response.raise_for_status()

            # Create temp directory if not specified
            if target_dir is None:
                target_dir = Path(tempfile.mkdtemp(prefix="aiskills-"))

            # Save and extract zip
            zip_path = target_dir / f"{slug}.zip"
            zip_path.write_bytes(response.content)

            extract_dir = target_dir / slug
            extract_dir.mkdir(parents=True, exist_ok=True)

            with zipfile.ZipFile(zip_path, "r") as zf:
                zf.extractall(extract_dir)

            zip_path.unlink()

            # Find SKILL.md (might be in subdirectory)
            skill_md = extract_dir / "SKILL.md"
            if not skill_md.exists():
                # Check one level down
                for subdir in extract_dir.iterdir():
                    if subdir.is_dir() and (subdir / "SKILL.md").exists():
                        return subdir

            return extract_dir

        except Exception as e:
            raise FetchError(f"Failed to download {slug}: {e}")

    def check_updates(
        self,
        installed: dict[str, str],  # name -> version
        include_prerelease: bool = False,
    ) -> dict[str, tuple[str, str]]:
        """Check for updates to installed skills.

        Args:
            installed: Dict of installed skill names to versions
            include_prerelease: Include prerelease versions

        Returns:
            Dict of skill name -> (current_version, latest_version)
            for skills with updates available
        """
        updates = {}

        for name, current_version in installed.items():
            try:
                # Try to get skill info from registry
                info = self.get_skill(name)
                versions = info.versions or [info.version]

                # Find latest version
                latest = find_latest(versions, include_prerelease)
                if latest and is_newer(current_version, latest):
                    updates[name] = (current_version, latest)

            except Exception:
                # Skip skills not in registry
                continue

        return updates

    def close(self):
        """Close HTTP client."""
        if self._http_client:
            self._http_client.close()
            self._http_client = None


class RegistrySource(SkillSource):
    """Handles registry:// URLs and slug references.

    Matches:
    - registry:skill-name - Skill from default registry
    - registry:skill-name@1.2.3 - Specific version
    - registry:skill-name@^1.0.0 - Version constraint
    - https://registry.example.com/skill-name - Custom registry
    """

    def __init__(
        self,
        client: RegistryClient | None = None,
        loader: SkillLoader | None = None,
        cache: CacheManager | None = None,
    ):
        self.client = client or RegistryClient()
        self.loader = loader or get_loader()
        self.cache = cache or get_cache_manager()

    def matches(self, source: str) -> bool:
        """Check if source is a registry reference."""
        if source.startswith("registry:"):
            return True
        # Also match bare skill names that look like registry slugs
        # (lowercase, hyphens, no slashes or special chars)
        if self._looks_like_slug(source):
            return True
        return False

    def _looks_like_slug(self, source: str) -> bool:
        """Check if source looks like a registry slug."""
        import re
        # Must not be a path or URL
        if "/" in source or source.startswith((".", "~", "http", "git@")):
            return False
        # Must match slug pattern
        slug_pattern = r"^[a-z0-9][a-z0-9-]*[a-z0-9]?(@[\d.^~>=<*a-zA-Z-]+)?$"
        return bool(re.match(slug_pattern, source))

    def _parse_source(self, source: str) -> tuple[str, str | None]:
        """Parse source into (slug, version_constraint).

        Args:
            source: Source string

        Returns:
            Tuple of (slug, version_constraint or None)
        """
        # Remove registry: prefix if present
        if source.startswith("registry:"):
            source = source[9:]

        # Split on @ for version
        if "@" in source:
            slug, version = source.rsplit("@", 1)
            return slug, version

        return source, None

    def fetch(self, source: str) -> list[FetchedSkill]:
        """Fetch skill from registry."""
        slug, version_constraint = self._parse_source(source)

        # Resolve version if constraint provided
        target_version = None
        if version_constraint:
            if version_constraint in ("latest", "*"):
                target_version = None  # Will get latest
            else:
                # Try to parse as constraint
                try:
                    constraint = VersionConstraint.parse(version_constraint)
                    # Get all versions and find matching
                    versions = self.client.get_versions(slug)
                    for v in versions:
                        try:
                            sv = SemanticVersion.parse(v)
                            if constraint.satisfies(sv):
                                target_version = v
                                break
                        except ValueError:
                            continue

                    if target_version is None:
                        raise FetchError(
                            f"No version matching '{version_constraint}' found",
                            source,
                        )
                except ValueError:
                    # Not a valid constraint, treat as exact version
                    target_version = version_constraint

        # Check cache first
        cache_key = f"{slug}@{target_version or 'latest'}"
        cached_path = self.cache.get("registry", cache_key)
        if cached_path and (cached_path / slug / "SKILL.md").exists():
            return [
                FetchedSkill(
                    name=slug,
                    path=cached_path / slug,
                    source_string=f"registry:{slug}@{target_version or 'latest'}",
                )
            ]

        # Download from registry
        cache_dir = self.cache.set("registry", cache_key)
        skill_path = self.client.download(slug, target_version, cache_dir)

        return [
            FetchedSkill(
                name=slug,
                path=skill_path,
                source_string=f"registry:{slug}@{target_version or 'latest'}",
            )
        ]

    def cleanup(self) -> None:
        """Close HTTP client."""
        self.client.close()


def get_registry_client() -> RegistryClient:
    """Get a registry client instance."""
    return RegistryClient()

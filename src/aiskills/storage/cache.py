"""Cache management for remote skills."""

from __future__ import annotations

import hashlib
import shutil
import time
from pathlib import Path

from .paths import PathResolver, get_path_resolver


class CacheManager:
    """Manages cache of remotely fetched skills.

    Cache structure:
    ~/.aiskills/cache/
    ├── github/
    │   └── <hash>/           # Hash of repo URL
    │       ├── .timestamp    # When cached
    │       └── <skill-dirs>/ # Cloned content
    └── git/
        └── <hash>/
            └── ...
    """

    # Cache TTL in seconds (24 hours)
    DEFAULT_TTL = 86400

    def __init__(self, paths: PathResolver | None = None, ttl: int | None = None):
        self.paths = paths or get_path_resolver()
        self.ttl = ttl or self.DEFAULT_TTL

    @property
    def cache_dir(self) -> Path:
        """Get cache directory."""
        return self.paths.get_cache_dir()

    def _hash_source(self, source: str) -> str:
        """Create a hash for a source URL."""
        return hashlib.sha256(source.encode()).hexdigest()[:12]

    def _get_cache_path(self, source_type: str, source: str) -> Path:
        """Get cache path for a source."""
        return self.cache_dir / source_type / self._hash_source(source)

    def _get_timestamp_file(self, cache_path: Path) -> Path:
        """Get timestamp file for a cache entry."""
        return cache_path / ".timestamp"

    def _is_expired(self, cache_path: Path) -> bool:
        """Check if a cache entry is expired."""
        timestamp_file = self._get_timestamp_file(cache_path)
        if not timestamp_file.exists():
            return True

        try:
            cached_time = float(timestamp_file.read_text().strip())
            return (time.time() - cached_time) > self.ttl
        except (ValueError, OSError):
            return True

    def _touch_timestamp(self, cache_path: Path) -> None:
        """Update timestamp for a cache entry."""
        timestamp_file = self._get_timestamp_file(cache_path)
        timestamp_file.write_text(str(time.time()))

    def get(self, source_type: str, source: str) -> Path | None:
        """Get cached path for a source if valid.

        Args:
            source_type: Type of source ("github", "git", etc.)
            source: Source identifier (URL, shorthand, etc.)

        Returns:
            Path to cached directory or None if not cached/expired
        """
        cache_path = self._get_cache_path(source_type, source)

        if not cache_path.exists():
            return None

        if self._is_expired(cache_path):
            # Clean up expired cache
            self.invalidate(source_type, source)
            return None

        return cache_path

    def set(self, source_type: str, source: str) -> Path:
        """Create cache directory for a source.

        Args:
            source_type: Type of source
            source: Source identifier

        Returns:
            Path to cache directory (created)
        """
        cache_path = self._get_cache_path(source_type, source)

        # Clean existing if present
        if cache_path.exists():
            shutil.rmtree(cache_path)

        cache_path.mkdir(parents=True, exist_ok=True)
        self._touch_timestamp(cache_path)

        return cache_path

    def invalidate(self, source_type: str, source: str) -> bool:
        """Invalidate (remove) a cache entry.

        Args:
            source_type: Type of source
            source: Source identifier

        Returns:
            True if cache was removed, False if didn't exist
        """
        cache_path = self._get_cache_path(source_type, source)

        if cache_path.exists():
            shutil.rmtree(cache_path)
            return True
        return False

    def clear(self, source_type: str | None = None) -> int:
        """Clear cache entries.

        Args:
            source_type: If provided, only clear this type; otherwise clear all

        Returns:
            Number of entries cleared
        """
        count = 0

        if source_type:
            type_dir = self.cache_dir / source_type
            if type_dir.exists():
                for entry in type_dir.iterdir():
                    if entry.is_dir():
                        shutil.rmtree(entry)
                        count += 1
        else:
            for type_dir in self.cache_dir.iterdir():
                if type_dir.is_dir():
                    for entry in type_dir.iterdir():
                        if entry.is_dir():
                            shutil.rmtree(entry)
                            count += 1

        return count

    def prune_expired(self) -> int:
        """Remove all expired cache entries.

        Returns:
            Number of entries pruned
        """
        count = 0

        for type_dir in self.cache_dir.iterdir():
            if not type_dir.is_dir():
                continue

            for entry in type_dir.iterdir():
                if entry.is_dir() and self._is_expired(entry):
                    shutil.rmtree(entry)
                    count += 1

        return count

    def get_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Dict with cache stats
        """
        total_entries = 0
        expired_entries = 0
        total_size = 0

        for type_dir in self.cache_dir.iterdir():
            if not type_dir.is_dir():
                continue

            for entry in type_dir.iterdir():
                if entry.is_dir():
                    total_entries += 1
                    if self._is_expired(entry):
                        expired_entries += 1
                    # Calculate size
                    for file in entry.rglob("*"):
                        if file.is_file():
                            total_size += file.stat().st_size

        return {
            "total_entries": total_entries,
            "expired_entries": expired_entries,
            "valid_entries": total_entries - expired_entries,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
        }


# Singleton instance
_cache: CacheManager | None = None


def get_cache_manager() -> CacheManager:
    """Get the singleton cache manager instance."""
    global _cache
    if _cache is None:
        _cache = CacheManager()
    return _cache

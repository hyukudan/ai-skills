"""Embedding cache for faster repeated queries."""

from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path
from typing import TYPE_CHECKING

from .base import EmbeddingProvider

if TYPE_CHECKING:
    pass


class EmbeddingCache:
    """LRU cache for embeddings with optional disk persistence.

    Caches embeddings to avoid regenerating them for repeated queries.
    Supports both in-memory LRU cache and disk persistence for cold starts.
    """

    def __init__(
        self,
        max_size: int = 1000,
        persist_path: Path | None = None,
        ttl_seconds: int = 86400 * 7,  # 7 days default
    ):
        """Initialize embedding cache.

        Args:
            max_size: Maximum number of embeddings to cache in memory
            persist_path: Path to persist cache to disk (optional)
            ttl_seconds: Time-to-live for cached embeddings
        """
        self.max_size = max_size
        self.persist_path = persist_path
        self.ttl_seconds = ttl_seconds

        # In-memory cache: {hash: (embedding, timestamp, access_count)}
        self._cache: dict[str, tuple[list[float], float, int]] = {}
        self._access_order: list[str] = []  # For LRU eviction

        # Stats
        self.hits = 0
        self.misses = 0

        # Load from disk if available
        if persist_path:
            self._load_from_disk()

    def _hash_text(self, text: str, provider_name: str) -> str:
        """Create a hash key for a text + provider combination."""
        content = f"{provider_name}:{text}"
        return hashlib.sha256(content.encode()).hexdigest()[:32]

    def get(self, text: str, provider_name: str) -> list[float] | None:
        """Get cached embedding for text.

        Args:
            text: Text that was embedded
            provider_name: Name of embedding provider (for cache key)

        Returns:
            Cached embedding or None if not found/expired
        """
        key = self._hash_text(text, provider_name)

        if key not in self._cache:
            self.misses += 1
            return None

        embedding, timestamp, count = self._cache[key]

        # Check TTL
        if time.time() - timestamp > self.ttl_seconds:
            del self._cache[key]
            if key in self._access_order:
                self._access_order.remove(key)
            self.misses += 1
            return None

        # Update access tracking for LRU
        self._cache[key] = (embedding, timestamp, count + 1)
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)

        self.hits += 1
        return embedding

    def put(self, text: str, provider_name: str, embedding: list[float]) -> None:
        """Cache an embedding.

        Args:
            text: Text that was embedded
            provider_name: Name of embedding provider
            embedding: The embedding vector
        """
        key = self._hash_text(text, provider_name)

        # Evict if at capacity
        while len(self._cache) >= self.max_size and self._access_order:
            oldest_key = self._access_order.pop(0)
            if oldest_key in self._cache:
                del self._cache[oldest_key]

        # Store
        self._cache[key] = (embedding, time.time(), 1)
        self._access_order.append(key)

    def _load_from_disk(self) -> None:
        """Load cache from disk."""
        if not self.persist_path or not self.persist_path.exists():
            return

        try:
            with open(self.persist_path, 'r') as f:
                data = json.load(f)

            now = time.time()
            for key, (embedding, timestamp, count) in data.items():
                # Skip expired entries
                if now - timestamp <= self.ttl_seconds:
                    self._cache[key] = (embedding, timestamp, count)
                    self._access_order.append(key)

            # Ensure we don't exceed max size
            while len(self._cache) > self.max_size and self._access_order:
                oldest_key = self._access_order.pop(0)
                if oldest_key in self._cache:
                    del self._cache[oldest_key]

        except Exception:
            pass  # Ignore corrupted cache

    def save_to_disk(self) -> None:
        """Persist cache to disk."""
        if not self.persist_path:
            return

        try:
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)
            with open(self.persist_path, 'w') as f:
                json.dump(self._cache, f)
        except Exception:
            pass  # Ignore write errors

    def clear(self) -> None:
        """Clear all cached embeddings."""
        self._cache.clear()
        self._access_order.clear()
        self.hits = 0
        self.misses = 0

        if self.persist_path and self.persist_path.exists():
            self.persist_path.unlink()

    @property
    def size(self) -> int:
        """Number of cached embeddings."""
        return len(self._cache)

    @property
    def hit_rate(self) -> float:
        """Cache hit rate (0-1)."""
        total = self.hits + self.misses
        return self.hits / total if total > 0 else 0.0

    def stats(self) -> dict:
        """Get cache statistics."""
        return {
            "size": self.size,
            "max_size": self.max_size,
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": f"{self.hit_rate:.1%}",
        }


class CachedEmbeddingProvider(EmbeddingProvider):
    """Wrapper that adds caching to any embedding provider.

    Caches query embeddings to avoid repeated computation.
    Document embeddings (batch) are not cached as they're typically one-time.
    """

    def __init__(
        self,
        provider: EmbeddingProvider,
        cache: EmbeddingCache | None = None,
    ):
        """Initialize cached provider.

        Args:
            provider: Underlying embedding provider
            cache: Cache instance (creates default if None)
        """
        self._provider = provider
        self._cache = cache or EmbeddingCache()

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for texts (not cached, typically one-time)."""
        return self._provider.embed(texts)

    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for query (cached)."""
        # Check cache first
        cached = self._cache.get(text, self._provider.name)
        if cached is not None:
            return cached

        # Generate and cache
        embedding = self._provider.embed_query(text)
        self._cache.put(text, self._provider.name, embedding)

        return embedding

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        return self._provider.dimension

    @property
    def name(self) -> str:
        """Get provider name."""
        return f"cached:{self._provider.name}"

    @property
    def cache(self) -> EmbeddingCache:
        """Access the cache for stats/management."""
        return self._cache

    def save_cache(self) -> None:
        """Persist cache to disk if configured."""
        self._cache.save_to_disk()


# Global cache instance
_global_cache: EmbeddingCache | None = None


def get_global_cache(cache_dir: Path | None = None) -> EmbeddingCache:
    """Get or create global embedding cache.

    Args:
        cache_dir: Directory for cache persistence

    Returns:
        Global EmbeddingCache instance
    """
    global _global_cache

    if _global_cache is None:
        persist_path = None
        if cache_dir:
            persist_path = cache_dir / "embedding_cache.json"

        _global_cache = EmbeddingCache(
            max_size=1000,
            persist_path=persist_path,
            ttl_seconds=86400 * 7,  # 7 days
        )

    return _global_cache

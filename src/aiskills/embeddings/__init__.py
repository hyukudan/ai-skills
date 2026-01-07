"""Embedding providers for semantic search."""

from .base import EmbeddingError, EmbeddingProvider
from .cache import CachedEmbeddingProvider, EmbeddingCache, get_global_cache
from .fastembed import FastEmbedProvider, get_fastembed_provider

__all__ = [
    "EmbeddingProvider",
    "EmbeddingError",
    "FastEmbedProvider",
    "get_fastembed_provider",
    "EmbeddingCache",
    "CachedEmbeddingProvider",
    "get_global_cache",
]

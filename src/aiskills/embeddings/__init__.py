"""Embedding providers for semantic search."""

from .base import EmbeddingError, EmbeddingProvider
from .fastembed import FastEmbedProvider, get_fastembed_provider

__all__ = [
    "EmbeddingProvider",
    "EmbeddingError",
    "FastEmbedProvider",
    "get_fastembed_provider",
]

"""Vector store backends for semantic search."""

from .base import SearchResult, VectorStoreError, VectorStoreProvider
from .chroma import ChromaVectorStore, get_chroma_store

__all__ = [
    "VectorStoreProvider",
    "VectorStoreError",
    "SearchResult",
    "ChromaVectorStore",
    "get_chroma_store",
]

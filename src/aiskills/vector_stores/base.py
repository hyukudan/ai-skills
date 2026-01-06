"""Base class for vector stores."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass
class SearchResult:
    """A single search result from vector store."""

    id: str
    document: str
    metadata: dict[str, Any]
    distance: float  # Lower is more similar
    score: float  # Normalized similarity (0-1, higher is better)


class VectorStoreProvider(ABC):
    """Abstract base class for vector stores.

    Vector stores persist embeddings and enable similarity search.
    """

    @abstractmethod
    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]] | None = None,
    ) -> None:
        """Add embeddings to the store.

        Args:
            ids: Unique identifiers for each embedding
            embeddings: Vector embeddings
            documents: Original text documents
            metadatas: Optional metadata for each document
        """
        ...

    @abstractmethod
    def query(
        self,
        embedding: list[float],
        n_results: int = 10,
        where: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """Query for similar embeddings.

        Args:
            embedding: Query embedding vector
            n_results: Maximum number of results
            where: Optional metadata filter

        Returns:
            List of search results sorted by similarity
        """
        ...

    @abstractmethod
    def delete(self, ids: list[str]) -> None:
        """Delete embeddings by ID.

        Args:
            ids: IDs to delete
        """
        ...

    @abstractmethod
    def get(self, ids: list[str]) -> list[dict[str, Any]]:
        """Get documents by ID.

        Args:
            ids: IDs to retrieve

        Returns:
            List of documents with metadata
        """
        ...

    @abstractmethod
    def count(self) -> int:
        """Get total number of documents in store."""
        ...

    @abstractmethod
    def clear(self) -> None:
        """Clear all documents from store."""
        ...


class VectorStoreError(Exception):
    """Error in vector store operations."""

    pass

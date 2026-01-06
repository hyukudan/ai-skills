"""Base class for embedding providers."""

from __future__ import annotations

from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers.

    Embedding providers convert text into vector representations
    for semantic search.
    """

    @abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for a list of texts.

        Args:
            texts: List of text strings to embed

        Returns:
            List of embedding vectors (each is a list of floats)
        """
        ...

    @abstractmethod
    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a single query text.

        Some providers optimize differently for queries vs documents.

        Args:
            text: Query text to embed

        Returns:
            Embedding vector
        """
        ...

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Get the dimension of embeddings produced by this provider."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Get the name/identifier of this provider."""
        ...


class EmbeddingError(Exception):
    """Error generating embeddings."""

    pass

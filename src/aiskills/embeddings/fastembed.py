"""FastEmbed embedding provider - local, no API keys needed."""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import EmbeddingError, EmbeddingProvider

if TYPE_CHECKING:
    from fastembed import TextEmbedding


class FastEmbedProvider(EmbeddingProvider):
    """Embedding provider using FastEmbed.

    FastEmbed provides fast, local embeddings without requiring API keys.
    Uses ONNX models for efficient inference.

    Default model: BAAI/bge-small-en-v1.5
    - Dimension: 384
    - Good balance of speed and quality
    - English-optimized but works for other languages
    """

    # Model info
    DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"
    MODEL_DIMENSIONS = {
        "BAAI/bge-small-en-v1.5": 384,
        "BAAI/bge-base-en-v1.5": 768,
        "BAAI/bge-large-en-v1.5": 1024,
        "sentence-transformers/all-MiniLM-L6-v2": 384,
    }

    def __init__(self, model_name: str | None = None):
        """Initialize FastEmbed provider.

        Args:
            model_name: Model to use (default: BAAI/bge-small-en-v1.5)
        """
        self.model_name = model_name or self.DEFAULT_MODEL
        self._model: TextEmbedding | None = None
        self._dimension: int | None = None

    def _get_model(self) -> TextEmbedding:
        """Lazy load the embedding model."""
        if self._model is None:
            try:
                from fastembed import TextEmbedding
            except ImportError as e:
                raise EmbeddingError(
                    "FastEmbed not installed. Install with: pip install aiskills[search]"
                ) from e

            try:
                self._model = TextEmbedding(model_name=self.model_name)
            except Exception as e:
                raise EmbeddingError(f"Failed to load model {self.model_name}: {e}") from e

        return self._model

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for texts."""
        if not texts:
            return []

        model = self._get_model()

        try:
            # FastEmbed returns a generator, convert to list
            embeddings = list(model.embed(texts))
            # Convert numpy float32 to native Python floats
            return [[float(v) for v in emb] for emb in embeddings]
        except Exception as e:
            raise EmbeddingError(f"Failed to generate embeddings: {e}") from e

    def embed_query(self, text: str) -> list[float]:
        """Generate embedding for a query."""
        model = self._get_model()

        try:
            # Use query_embed for queries (some models optimize for this)
            if hasattr(model, "query_embed"):
                embeddings = list(model.query_embed([text]))
            else:
                embeddings = list(model.embed([text]))

            # Convert numpy float32 to native Python floats
            return [float(v) for v in embeddings[0]]
        except Exception as e:
            raise EmbeddingError(f"Failed to generate query embedding: {e}") from e

    @property
    def dimension(self) -> int:
        """Get embedding dimension."""
        if self._dimension is None:
            # Try known dimensions first
            if self.model_name in self.MODEL_DIMENSIONS:
                self._dimension = self.MODEL_DIMENSIONS[self.model_name]
            else:
                # Generate a test embedding to get dimension
                test_emb = self.embed_query("test")
                self._dimension = len(test_emb)

        return self._dimension

    @property
    def name(self) -> str:
        """Get provider name."""
        return f"fastembed:{self.model_name}"


# Singleton instance
_provider: FastEmbedProvider | None = None


def get_fastembed_provider(model_name: str | None = None) -> FastEmbedProvider:
    """Get FastEmbed provider instance."""
    global _provider
    if _provider is None or (model_name and _provider.model_name != model_name):
        _provider = FastEmbedProvider(model_name)
    return _provider

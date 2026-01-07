"""Hybrid search combining semantic and BM25 text search."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .bm25 import BM25Index

if TYPE_CHECKING:
    from ..embeddings.base import EmbeddingProvider
    from ..vector_stores.base import VectorStoreProvider


@dataclass
class SearchResult:
    """Result from hybrid search."""

    id: str
    score: float
    semantic_score: float
    text_score: float
    metadata: dict


class HybridSearcher:
    """Combines semantic search with BM25 for improved results.

    Uses Reciprocal Rank Fusion (RRF) to merge results from both search methods.
    This provides the best of both worlds:
    - Semantic search: Understands meaning and context
    - BM25: Handles exact keyword matches and rare terms
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        vector_store: VectorStoreProvider,
        semantic_weight: float = 0.6,
        text_weight: float = 0.4,
        rrf_k: int = 60,  # RRF constant
    ):
        """Initialize hybrid searcher.

        Args:
            embedding_provider: Provider for generating embeddings
            vector_store: Vector store for semantic search
            semantic_weight: Weight for semantic search scores (0-1)
            text_weight: Weight for BM25 scores (0-1)
            rrf_k: Constant for RRF ranking (higher = smoother blending)
        """
        self.embedding_provider = embedding_provider
        self.vector_store = vector_store
        self.semantic_weight = semantic_weight
        self.text_weight = text_weight
        self.rrf_k = rrf_k

        # BM25 index for text search
        self.bm25_index = BM25Index()

        # Document storage for metadata
        self._documents: dict[str, dict] = {}

    def add(
        self,
        doc_id: str,
        text: str,
        embedding: list[float],
        metadata: dict | None = None,
    ) -> None:
        """Add a document to both indexes.

        Args:
            doc_id: Unique document ID
            text: Document text for BM25 indexing
            embedding: Pre-computed embedding vector
            metadata: Optional metadata
        """
        # Add to vector store
        self.vector_store.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata or {}],
        )

        # Add to BM25 index
        self.bm25_index.add(doc_id, text)

        # Store metadata
        self._documents[doc_id] = metadata or {}

    def remove(self, doc_id: str) -> bool:
        """Remove a document from both indexes.

        Args:
            doc_id: Document ID to remove

        Returns:
            True if removed from either index
        """
        removed_vector = False
        try:
            self.vector_store.delete([doc_id])
            removed_vector = True
        except Exception:
            pass

        removed_bm25 = self.bm25_index.remove(doc_id)

        if doc_id in self._documents:
            del self._documents[doc_id]

        return removed_vector or removed_bm25

    def search(
        self,
        query: str,
        limit: int = 10,
        min_score: float = 0.0,
        semantic_only: bool = False,
        text_only: bool = False,
    ) -> list[SearchResult]:
        """Search using hybrid approach.

        Args:
            query: Search query
            limit: Maximum results
            min_score: Minimum combined score threshold
            semantic_only: Use only semantic search
            text_only: Use only BM25 text search

        Returns:
            List of SearchResult sorted by combined score
        """
        if text_only:
            return self._text_search(query, limit, min_score)
        if semantic_only:
            return self._semantic_search(query, limit, min_score)

        return self._hybrid_search(query, limit, min_score)

    def _semantic_search(
        self, query: str, limit: int, min_score: float
    ) -> list[SearchResult]:
        """Perform semantic-only search."""
        query_embedding = self.embedding_provider.embed_query(query)

        results = self.vector_store.query(
            embedding=query_embedding,
            n_results=limit,
        )

        return [
            SearchResult(
                id=r.id,
                score=r.score,
                semantic_score=r.score,
                text_score=0.0,
                metadata=r.metadata,
            )
            for r in results
            if r.score >= min_score
        ]

    def _text_search(
        self, query: str, limit: int, min_score: float
    ) -> list[SearchResult]:
        """Perform BM25-only search."""
        results = self.bm25_index.search(query, limit=limit)

        # Normalize BM25 scores to 0-1 range
        max_score = results[0][1] if results else 1.0
        max_score = max(max_score, 0.001)  # Avoid division by zero

        return [
            SearchResult(
                id=doc_id,
                score=score / max_score,
                semantic_score=0.0,
                text_score=score / max_score,
                metadata=self._documents.get(doc_id, {}),
            )
            for doc_id, score in results
            if (score / max_score) >= min_score
        ]

    def _hybrid_search(
        self, query: str, limit: int, min_score: float
    ) -> list[SearchResult]:
        """Perform hybrid search using RRF."""
        # Get more results than needed for better fusion
        fetch_limit = min(limit * 3, 100)

        # Semantic search
        query_embedding = self.embedding_provider.embed_query(query)
        semantic_results = self.vector_store.query(
            embedding=query_embedding,
            n_results=fetch_limit,
        )

        # BM25 search
        text_results = self.bm25_index.search(query, limit=fetch_limit)

        # Build rank maps
        semantic_ranks: dict[str, int] = {
            r.id: rank for rank, r in enumerate(semantic_results)
        }
        text_ranks: dict[str, int] = {
            doc_id: rank for rank, (doc_id, _) in enumerate(text_results)
        }

        # Build score maps for reporting
        semantic_scores: dict[str, float] = {r.id: r.score for r in semantic_results}
        text_scores: dict[str, float] = {}
        if text_results:
            max_bm25 = max(score for _, score in text_results)
            max_bm25 = max(max_bm25, 0.001)
            text_scores = {doc_id: score / max_bm25 for doc_id, score in text_results}

        # Combine all document IDs
        all_ids = set(semantic_ranks.keys()) | set(text_ranks.keys())

        # Calculate RRF scores
        rrf_scores: list[tuple[str, float, float, float]] = []

        for doc_id in all_ids:
            # RRF formula: 1 / (k + rank)
            semantic_rrf = 0.0
            if doc_id in semantic_ranks:
                semantic_rrf = 1 / (self.rrf_k + semantic_ranks[doc_id])

            text_rrf = 0.0
            if doc_id in text_ranks:
                text_rrf = 1 / (self.rrf_k + text_ranks[doc_id])

            # Weighted combination
            combined = (
                self.semantic_weight * semantic_rrf + self.text_weight * text_rrf
            )

            rrf_scores.append((
                doc_id,
                combined,
                semantic_scores.get(doc_id, 0.0),
                text_scores.get(doc_id, 0.0),
            ))

        # Sort by combined score
        rrf_scores.sort(key=lambda x: x[1], reverse=True)

        # Normalize combined scores to 0-1
        max_combined = rrf_scores[0][1] if rrf_scores else 1.0
        max_combined = max(max_combined, 0.001)

        results = []
        for doc_id, combined, sem_score, txt_score in rrf_scores[:limit]:
            normalized_score = combined / max_combined
            if normalized_score >= min_score:
                # Get metadata from semantic results or storage
                metadata = self._documents.get(doc_id, {})
                for r in semantic_results:
                    if r.id == doc_id:
                        metadata = r.metadata
                        break

                results.append(SearchResult(
                    id=doc_id,
                    score=normalized_score,
                    semantic_score=sem_score,
                    text_score=txt_score,
                    metadata=metadata,
                ))

        return results

    def clear(self) -> None:
        """Clear all indexes."""
        self.vector_store.clear()
        self.bm25_index.clear()
        self._documents.clear()

    @property
    def size(self) -> int:
        """Number of indexed documents."""
        return self.bm25_index.size

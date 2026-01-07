"""BM25 text search implementation for skill matching."""

from __future__ import annotations

import math
import re
from collections import Counter
from dataclasses import dataclass, field


@dataclass
class BM25Index:
    """BM25 index for text search.

    Implements the Okapi BM25 ranking function for keyword-based search.
    This complements semantic search by handling exact keyword matches.
    """

    # BM25 parameters
    k1: float = 1.5  # Term frequency saturation
    b: float = 0.75  # Length normalization

    # Index data
    documents: dict[str, str] = field(default_factory=dict)  # id -> text
    doc_lengths: dict[str, int] = field(default_factory=dict)  # id -> length
    doc_freqs: dict[str, int] = field(default_factory=dict)  # term -> doc count
    term_freqs: dict[str, dict[str, int]] = field(default_factory=dict)  # id -> term -> count
    avg_doc_length: float = 0.0
    total_docs: int = 0

    def _tokenize(self, text: str) -> list[str]:
        """Tokenize text into searchable terms."""
        # Lowercase and split on non-alphanumeric
        text = text.lower()
        tokens = re.findall(r'\b[a-z0-9]+\b', text)
        # Filter very short tokens
        return [t for t in tokens if len(t) > 1]

    def add(self, doc_id: str, text: str) -> None:
        """Add a document to the index.

        Args:
            doc_id: Unique document identifier
            text: Document text content
        """
        tokens = self._tokenize(text)

        # Store document
        self.documents[doc_id] = text
        self.doc_lengths[doc_id] = len(tokens)

        # Count term frequencies
        term_counts = Counter(tokens)
        self.term_freqs[doc_id] = dict(term_counts)

        # Update document frequencies
        for term in set(tokens):
            self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1

        # Update statistics
        self.total_docs += 1
        self._update_avg_length()

    def remove(self, doc_id: str) -> bool:
        """Remove a document from the index.

        Args:
            doc_id: Document ID to remove

        Returns:
            True if removed, False if not found
        """
        if doc_id not in self.documents:
            return False

        # Update document frequencies
        if doc_id in self.term_freqs:
            for term in self.term_freqs[doc_id]:
                if term in self.doc_freqs:
                    self.doc_freqs[term] -= 1
                    if self.doc_freqs[term] <= 0:
                        del self.doc_freqs[term]

        # Remove document data
        del self.documents[doc_id]
        del self.doc_lengths[doc_id]
        if doc_id in self.term_freqs:
            del self.term_freqs[doc_id]

        self.total_docs -= 1
        self._update_avg_length()
        return True

    def _update_avg_length(self) -> None:
        """Update average document length."""
        if self.total_docs > 0:
            self.avg_doc_length = sum(self.doc_lengths.values()) / self.total_docs
        else:
            self.avg_doc_length = 0.0

    def _idf(self, term: str) -> float:
        """Calculate inverse document frequency for a term."""
        if term not in self.doc_freqs or self.total_docs == 0:
            return 0.0

        doc_freq = self.doc_freqs[term]
        # IDF with smoothing
        return math.log((self.total_docs - doc_freq + 0.5) / (doc_freq + 0.5) + 1)

    def _score_document(self, doc_id: str, query_terms: list[str]) -> float:
        """Calculate BM25 score for a document against query terms."""
        if doc_id not in self.term_freqs:
            return 0.0

        score = 0.0
        doc_len = self.doc_lengths.get(doc_id, 0)
        doc_terms = self.term_freqs[doc_id]

        for term in query_terms:
            if term not in doc_terms:
                continue

            # Term frequency in document
            tf = doc_terms[term]

            # IDF component
            idf = self._idf(term)

            # BM25 formula
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (
                1 - self.b + self.b * (doc_len / self.avg_doc_length)
                if self.avg_doc_length > 0 else 1
            )

            score += idf * (numerator / denominator)

        return score

    def search(
        self,
        query: str,
        limit: int = 10,
        min_score: float = 0.0,
    ) -> list[tuple[str, float]]:
        """Search for documents matching query.

        Args:
            query: Search query
            limit: Maximum results
            min_score: Minimum BM25 score threshold

        Returns:
            List of (doc_id, score) tuples sorted by score
        """
        query_terms = self._tokenize(query)
        if not query_terms:
            return []

        # Score all documents
        scores: list[tuple[str, float]] = []
        for doc_id in self.documents:
            score = self._score_document(doc_id, query_terms)
            if score >= min_score:
                scores.append((doc_id, score))

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:limit]

    def clear(self) -> None:
        """Clear the entire index."""
        self.documents.clear()
        self.doc_lengths.clear()
        self.doc_freqs.clear()
        self.term_freqs.clear()
        self.avg_doc_length = 0.0
        self.total_docs = 0

    @property
    def size(self) -> int:
        """Number of indexed documents."""
        return self.total_docs

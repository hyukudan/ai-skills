"""ChromaDB vector store - local, persistent, no server needed."""

from __future__ import annotations

from pathlib import Path
from typing import Any, TYPE_CHECKING

from .base import SearchResult, VectorStoreError, VectorStoreProvider

if TYPE_CHECKING:
    import chromadb
    from chromadb.api.models.Collection import Collection


class ChromaVectorStore(VectorStoreProvider):
    """Vector store using ChromaDB.

    ChromaDB provides:
    - Local persistence (SQLite + DuckDB)
    - No server required
    - Built-in metadata filtering
    - Automatic index management
    """

    COLLECTION_NAME = "aiskills"

    def __init__(
        self,
        persist_dir: Path | str | None = None,
        collection_name: str | None = None,
    ):
        """Initialize ChromaDB store.

        Args:
            persist_dir: Directory for persistence (None for in-memory)
            collection_name: Name of collection (default: aiskills)
        """
        self.persist_dir = Path(persist_dir) if persist_dir else None
        self.collection_name = collection_name or self.COLLECTION_NAME
        self._client: chromadb.ClientAPI | None = None
        self._collection: Collection | None = None

    def _get_client(self) -> chromadb.ClientAPI:
        """Get or create ChromaDB client."""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings
            except ImportError as e:
                raise VectorStoreError(
                    "ChromaDB not installed. Install with: pip install aiskills[search]"
                ) from e

            if self.persist_dir:
                self.persist_dir.mkdir(parents=True, exist_ok=True)
                self._client = chromadb.PersistentClient(
                    path=str(self.persist_dir),
                    settings=Settings(anonymized_telemetry=False),
                )
            else:
                self._client = chromadb.Client(
                    settings=Settings(anonymized_telemetry=False),
                )

        return self._client

    def _get_collection(self) -> Collection:
        """Get or create collection."""
        if self._collection is None:
            client = self._get_client()
            self._collection = client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"},
            )
        return self._collection

    def add(
        self,
        ids: list[str],
        embeddings: list[list[float]],
        documents: list[str],
        metadatas: list[dict[str, Any]] | None = None,
    ) -> None:
        """Add embeddings to ChromaDB."""
        if not ids:
            return

        collection = self._get_collection()

        # ChromaDB doesn't like None metadata
        if metadatas is None:
            metadatas = [{} for _ in ids]

        # Clean metadata (ChromaDB only supports str, int, float, bool)
        cleaned_metadatas = []
        for meta in metadatas:
            cleaned = {}
            for k, v in meta.items():
                if isinstance(v, (str, int, float, bool)):
                    cleaned[k] = v
                elif isinstance(v, list):
                    # Convert lists to comma-separated strings
                    cleaned[k] = ",".join(str(x) for x in v)
                elif v is not None:
                    cleaned[k] = str(v)
            cleaned_metadatas.append(cleaned)

        try:
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=documents,
                metadatas=cleaned_metadatas,
            )
        except Exception as e:
            raise VectorStoreError(f"Failed to add to ChromaDB: {e}") from e

    def query(
        self,
        embedding: list[float],
        n_results: int = 10,
        where: dict[str, Any] | None = None,
    ) -> list[SearchResult]:
        """Query ChromaDB for similar documents."""
        collection = self._get_collection()

        try:
            results = collection.query(
                query_embeddings=[embedding],
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"],
            )
        except Exception as e:
            raise VectorStoreError(f"ChromaDB query failed: {e}") from e

        # Convert to SearchResult list
        search_results: list[SearchResult] = []

        if not results["ids"] or not results["ids"][0]:
            return search_results

        ids = results["ids"][0]
        documents = results["documents"][0] if results["documents"] else [""] * len(ids)
        metadatas = results["metadatas"][0] if results["metadatas"] else [{}] * len(ids)
        distances = results["distances"][0] if results["distances"] else [0.0] * len(ids)

        for i, doc_id in enumerate(ids):
            # Convert distance to similarity score (cosine distance to similarity)
            distance = distances[i]
            score = 1.0 - min(distance, 1.0)  # Cosine distance is 0-2, but usually 0-1

            search_results.append(
                SearchResult(
                    id=doc_id,
                    document=documents[i] or "",
                    metadata=metadatas[i] or {},
                    distance=distance,
                    score=score,
                )
            )

        return search_results

    def delete(self, ids: list[str]) -> None:
        """Delete documents by ID."""
        if not ids:
            return

        collection = self._get_collection()

        try:
            collection.delete(ids=ids)
        except Exception as e:
            raise VectorStoreError(f"Failed to delete from ChromaDB: {e}") from e

    def get(self, ids: list[str]) -> list[dict[str, Any]]:
        """Get documents by ID."""
        if not ids:
            return []

        collection = self._get_collection()

        try:
            results = collection.get(
                ids=ids,
                include=["documents", "metadatas"],
            )
        except Exception as e:
            raise VectorStoreError(f"Failed to get from ChromaDB: {e}") from e

        documents: list[dict[str, Any]] = []
        for i, doc_id in enumerate(results["ids"]):
            documents.append({
                "id": doc_id,
                "document": results["documents"][i] if results["documents"] else "",
                "metadata": results["metadatas"][i] if results["metadatas"] else {},
            })

        return documents

    def count(self) -> int:
        """Get document count."""
        collection = self._get_collection()
        return collection.count()

    def clear(self) -> None:
        """Clear all documents."""
        client = self._get_client()

        try:
            client.delete_collection(self.collection_name)
            self._collection = None
        except Exception:
            pass  # Collection might not exist


# Factory function
def get_chroma_store(persist_dir: Path | str | None = None) -> ChromaVectorStore:
    """Create a ChromaDB vector store."""
    return ChromaVectorStore(persist_dir=persist_dir)

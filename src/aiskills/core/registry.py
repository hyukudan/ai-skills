"""Skill registry - indexes skills for semantic search."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from ..models.skill import Skill, SkillIndex
from ..storage.paths import PathResolver, get_path_resolver

if TYPE_CHECKING:
    from ..embeddings.base import EmbeddingProvider
    from ..vector_stores.base import VectorStoreProvider


class SkillRegistry:
    """Registry for indexing and searching skills.

    Combines:
    - Vector embeddings for semantic search
    - Metadata for filtering
    - Text matching for exact searches
    """

    def __init__(
        self,
        paths: PathResolver | None = None,
        embedding_provider: EmbeddingProvider | None = None,
        vector_store: VectorStoreProvider | None = None,
    ):
        self.paths = paths or get_path_resolver()
        self._embedding_provider = embedding_provider
        self._vector_store = vector_store
        self._index: dict[str, SkillIndex] = {}
        self._initialized = False

    def _load_index_from_store(self) -> None:
        """Load the in-memory index from the vector store."""
        if self._initialized:
            return

        try:
            store = self._get_vector_store()
            # Get all documents from the store
            count = store.count()
            if count == 0:
                self._initialized = True
                return

            # ChromaDB doesn't have a "get all" method easily,
            # so we'll query with a dummy embedding to get results
            # This is a workaround - we use the peek method if available
            collection = store._get_collection()
            results = collection.peek(limit=count)

            if not results["ids"]:
                self._initialized = True
                return

            # Rebuild the in-memory index
            for i, doc_id in enumerate(results["ids"]):
                metadata = results["metadatas"][i] if results["metadatas"] else {}
                document = results["documents"][i] if results["documents"] else ""

                name = metadata.get("name", "")
                if not name:
                    continue

                tags_str = metadata.get("tags", "")
                tags = tags_str.split(",") if tags_str else []

                # Extract description from document
                desc = ""
                if document:
                    for line in document.split("\n"):
                        if line.startswith("Description: "):
                            desc = line.replace("Description: ", "")
                            break

                index = SkillIndex(
                    id=doc_id,
                    name=name,
                    description=desc,
                    version=metadata.get("version", ""),
                    tags=tags,
                    category=metadata.get("category") or None,
                    source=metadata.get("source", ""),
                    path=metadata.get("path", ""),
                    content_hash=metadata.get("content_hash", ""),
                    embedding_id=doc_id,
                )
                self._index[name] = index

        except Exception:
            pass  # Store might not be initialized yet

        self._initialized = True

    def _get_embedding_provider(self) -> EmbeddingProvider:
        """Lazy load embedding provider."""
        if self._embedding_provider is None:
            from ..embeddings.fastembed import get_fastembed_provider
            self._embedding_provider = get_fastembed_provider()
        return self._embedding_provider

    def _get_vector_store(self) -> VectorStoreProvider:
        """Lazy load vector store."""
        if self._vector_store is None:
            from ..vector_stores.chroma import get_chroma_store
            registry_dir = self.paths.get_registry_dir()
            self._vector_store = get_chroma_store(registry_dir / "vectors")
        return self._vector_store

    def _build_search_text(self, skill: Skill) -> str:
        """Build text for embedding from skill metadata."""
        parts = [
            f"Skill: {skill.manifest.name}",
            f"Description: {skill.manifest.description}",
        ]

        if skill.manifest.tags:
            parts.append(f"Tags: {', '.join(skill.manifest.tags)}")

        if skill.manifest.category:
            parts.append(f"Category: {skill.manifest.category}")

        if skill.manifest.context:
            parts.append(f"Context: {skill.manifest.context}")

        return "\n".join(parts)

    def add(self, skill: Skill) -> None:
        """Add a skill to the registry.

        Args:
            skill: Skill to index
        """
        embedder = self._get_embedding_provider()
        store = self._get_vector_store()

        # Build search text
        search_text = self._build_search_text(skill)

        # Generate embedding
        embedding = embedder.embed_query(search_text)

        # Build metadata for filtering
        metadata = {
            "name": skill.manifest.name,
            "version": skill.manifest.version,
            "tags": ",".join(skill.manifest.tags),
            "category": skill.manifest.category or "",
            "source": skill.source,
            "path": skill.path,
            "content_hash": skill.content_hash,
        }

        # Store in vector DB
        store.add(
            ids=[skill.id],
            embeddings=[embedding],
            documents=[search_text],
            metadatas=[metadata],
        )

        # Update local index
        index = skill.to_index()
        index.embedding_id = skill.id
        self._index[skill.manifest.name] = index

    def remove(self, name: str) -> bool:
        """Remove a skill from the registry.

        Args:
            name: Skill name to remove

        Returns:
            True if removed, False if not found
        """
        if name not in self._index:
            return False

        index = self._index[name]
        if index.embedding_id:
            store = self._get_vector_store()
            store.delete([index.embedding_id])

        del self._index[name]
        return True

    def search(
        self,
        query: str,
        limit: int = 10,
        tags: list[str] | None = None,
        category: str | None = None,
        min_score: float = 0.0,
    ) -> list[tuple[SkillIndex, float]]:
        """Search for skills semantically.

        Args:
            query: Search query
            limit: Maximum results
            tags: Filter by tags (any match)
            category: Filter by category
            min_score: Minimum similarity score (0-1)

        Returns:
            List of (SkillIndex, score) tuples sorted by relevance
        """
        embedder = self._get_embedding_provider()
        store = self._get_vector_store()

        # Generate query embedding
        query_embedding = embedder.embed_query(query)

        # Build filter
        where = None
        if category:
            where = {"category": category}

        # Query vector store
        results = store.query(
            embedding=query_embedding,
            n_results=limit * 2,  # Get extra for post-filtering
            where=where,
        )

        # Post-filter and build results
        matches: list[tuple[SkillIndex, float]] = []

        for result in results:
            # Check minimum score
            if result.score < min_score:
                continue

            # Check tags filter
            if tags:
                result_tags = result.metadata.get("tags", "").split(",")
                if not any(t in result_tags for t in tags):
                    continue

            # Get skill index
            name = result.metadata.get("name", "")
            if name in self._index:
                matches.append((self._index[name], result.score))
            else:
                # Reconstruct from metadata
                index = SkillIndex(
                    id=result.id,
                    name=name,
                    description=result.document.split("\n")[1].replace("Description: ", ""),
                    version=result.metadata.get("version", ""),
                    tags=result.metadata.get("tags", "").split(",") if result.metadata.get("tags") else [],
                    category=result.metadata.get("category") or None,
                    source=result.metadata.get("source", ""),
                    path=result.metadata.get("path", ""),
                    content_hash=result.metadata.get("content_hash", ""),
                    embedding_id=result.id,
                )
                matches.append((index, result.score))

        # Sort by score and limit
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:limit]

    def search_text(
        self,
        query: str,
        limit: int = 10,
    ) -> list[SkillIndex]:
        """Simple text search on name and description.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching SkillIndex
        """
        self._load_index_from_store()

        query_lower = query.lower()
        matches: list[tuple[SkillIndex, int]] = []

        for name, index in self._index.items():
            score = 0

            # Name match (highest weight)
            if query_lower in name.lower():
                score += 100
            if name.lower().startswith(query_lower):
                score += 50

            # Description match
            if query_lower in index.description.lower():
                score += 30

            # Tag match
            for tag in index.tags:
                if query_lower in tag.lower():
                    score += 20

            # Category match
            if index.category and query_lower in index.category.lower():
                score += 10

            if score > 0:
                matches.append((index, score))

        # Sort by score
        matches.sort(key=lambda x: x[1], reverse=True)
        return [m[0] for m in matches[:limit]]

    def list_all(self) -> list[SkillIndex]:
        """List all indexed skills."""
        self._load_index_from_store()
        return list(self._index.values())

    def get(self, name: str) -> SkillIndex | None:
        """Get skill index by name."""
        self._load_index_from_store()
        return self._index.get(name)

    def rebuild(self, skills: list[Skill]) -> int:
        """Rebuild the entire index.

        Args:
            skills: All skills to index

        Returns:
            Number of skills indexed
        """
        # Clear existing
        store = self._get_vector_store()
        store.clear()
        self._index.clear()

        # Re-add all
        for skill in skills:
            self.add(skill)

        return len(skills)

    def count(self) -> int:
        """Get number of indexed skills."""
        self._load_index_from_store()
        return len(self._index)

    def sync_from_manager(self, manager) -> int:
        """Sync registry with installed skills from manager.

        Args:
            manager: SkillManager instance

        Returns:
            Number of skills synced
        """
        from .loader import get_loader

        loader = get_loader()
        skills: list[Skill] = []

        # Load all installed skills
        for skills_dir, location_type in self.paths.get_search_dirs():
            is_global = str(skills_dir).startswith(str(self.paths.global_base))

            for skill_dir in loader.list_skill_dirs(skills_dir):
                try:
                    skill = loader.load(
                        skill_dir,
                        source="global" if is_global else "project",
                        location_type=location_type,
                    )
                    skills.append(skill)
                except Exception:
                    continue

        return self.rebuild(skills)


# Singleton instance
_registry: SkillRegistry | None = None


def get_registry() -> SkillRegistry:
    """Get the singleton registry instance."""
    global _registry
    if _registry is None:
        _registry = SkillRegistry()
    return _registry

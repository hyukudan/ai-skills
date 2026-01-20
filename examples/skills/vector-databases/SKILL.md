---
name: vector-databases
description: |
  Comprehensive guide to vector databases for similarity search and RAG applications.
  Covers Pinecone, Qdrant, Chroma, pgvector, Weaviate, and Milvus with practical examples,
  indexing strategies, and production considerations.
version: 1.0.0
tags: [ai, vectors, embeddings, similarity-search, pinecone, qdrant, chroma, pgvector]
category: ai/vectors
trigger_phrases:
  - "vector database"
  - "vector search"
  - "similarity search"
  - "embedding storage"
  - "Pinecone"
  - "Qdrant"
  - "Chroma"
  - "pgvector"
  - "Weaviate"
  - "Milvus"
  - "nearest neighbor"
  - "ANN"
variables:
  database:
    type: string
    description: Primary vector database
    enum: [pinecone, qdrant, chroma, pgvector, weaviate, milvus]
    default: qdrant
  scale:
    type: string
    description: Scale of deployment
    enum: [local, production, enterprise]
    default: local
---

# Vector Databases Guide

## Core Philosophy

**Vector databases turn semantic similarity into fast lookups.** Choose based on scale, hosting preference, and required features.

> "The right vector database is the one that matches your operational constraints, not the one with the most features."

---

## Quick Decision Matrix

| Database | Best For | Hosting | Filtering | Price |
|----------|----------|---------|-----------|-------|
| **Pinecone** | Production, no ops | Managed only | Excellent | $$ |
| **Qdrant** | Self-hosted, full control | Both | Excellent | Free/$ |
| **Chroma** | Prototyping, local dev | Local/Docker | Basic | Free |
| **pgvector** | Existing Postgres | Self-hosted | SQL power | Free |
| **Weaviate** | GraphQL, multi-modal | Both | Good | Free/$ |
| **Milvus** | Massive scale | Self-hosted | Good | Free |

---

## 1. Core Concepts

### Vector Similarity

```python
import numpy as np

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors."""
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def euclidean_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Euclidean (L2) distance between vectors."""
    return np.linalg.norm(a - b)

def dot_product(a: np.ndarray, b: np.ndarray) -> float:
    """Dot product similarity (for normalized vectors = cosine)."""
    return np.dot(a, b)
```

### Distance Metrics

| Metric | Use When | Range |
|--------|----------|-------|
| **Cosine** | Text embeddings, normalized vectors | -1 to 1 |
| **Euclidean** | Image features, spatial data | 0 to ∞ |
| **Dot Product** | Normalized vectors, faster | -∞ to ∞ |

**Rule of thumb**: Use cosine for text, euclidean for images, dot product for speed.

---

## 2. Index Types

### HNSW (Hierarchical Navigable Small World)

Best for most use cases. Fast queries, good recall.

```
Layer 2:  [A]─────────────────[B]
           │                   │
Layer 1:  [A]───[C]───[D]───[B]
           │     │     │     │
Layer 0:  [A][E][C][F][D][G][B][H]  (all vectors)
```

**Parameters:**
- `M` (connections): 16-64 typical. Higher = better recall, more memory
- `ef_construct`: Build-time accuracy. 100-200 typical
- `ef_search`: Query-time accuracy vs speed trade-off

```python
# Qdrant HNSW config
from qdrant_client.models import HnswConfigDiff

hnsw_config = HnswConfigDiff(
    m=16,              # Connections per node
    ef_construct=100,  # Build accuracy
    full_scan_threshold=10000,  # Below this, just scan
)
```

### IVF (Inverted File Index)

Clusters vectors, searches relevant clusters only. Good for very large datasets.

```
Cluster 1: [v1, v5, v9, ...]
Cluster 2: [v2, v6, v12, ...]
Cluster 3: [v3, v7, v8, ...]
...
```

**Parameters:**
- `nlist`: Number of clusters. sqrt(n) is a starting point
- `nprobe`: Clusters to search. Higher = better recall, slower

### PQ (Product Quantization)

Compresses vectors for memory savings. Trades accuracy for space.

```python
# 768-dim vector → 96 bytes (8x compression)
# Split into 96 sub-vectors of 8 dims each
# Each sub-vector → 1 byte (256 centroids)
```

---

## 3. Database-Specific Guides

{% if database == "pinecone" %}

### Pinecone

Fully managed, serverless option available. Best for teams that don't want to manage infrastructure.

```python
from pinecone import Pinecone, ServerlessSpec

# Initialize
pc = Pinecone(api_key="your-api-key")

# Create index
pc.create_index(
    name="my-index",
    dimension=1536,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)

# Get index
index = pc.Index("my-index")

# Upsert vectors
index.upsert(
    vectors=[
        {
            "id": "doc1",
            "values": embedding,  # List of floats
            "metadata": {"source": "wiki", "category": "science"}
        }
    ],
    namespace="articles"  # Optional partitioning
)

# Query
results = index.query(
    vector=query_embedding,
    top_k=5,
    include_metadata=True,
    filter={"category": {"$eq": "science"}}  # Metadata filtering
)

for match in results.matches:
    print(f"{match.id}: {match.score}")
```

**Pinecone Filtering Syntax:**
```python
# Equality
{"category": {"$eq": "tech"}}

# In list
{"category": {"$in": ["tech", "science"]}}

# Numeric comparison
{"year": {"$gte": 2020}}

# Combine with AND
{"$and": [{"category": {"$eq": "tech"}}, {"year": {"$gte": 2020}}]}
```

{% elif database == "qdrant" %}

### Qdrant

Open-source, excellent filtering, can self-host or use cloud.

```python
from qdrant_client import QdrantClient
from qdrant_client.models import (
    VectorParams, Distance, PointStruct,
    Filter, FieldCondition, MatchValue
)

# Local (in-memory for dev)
client = QdrantClient(":memory:")

# Local persistent
client = QdrantClient(path="./qdrant_data")

# Cloud/Docker
client = QdrantClient(url="http://localhost:6333")

# Create collection
client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE
    )
)

# Upsert points
client.upsert(
    collection_name="documents",
    points=[
        PointStruct(
            id=1,
            vector=embedding,
            payload={"text": "...", "source": "wiki", "year": 2024}
        )
    ]
)

# Search with filter
results = client.search(
    collection_name="documents",
    query_vector=query_embedding,
    limit=5,
    query_filter=Filter(
        must=[
            FieldCondition(
                key="source",
                match=MatchValue(value="wiki")
            )
        ]
    )
)

for result in results:
    print(f"{result.id}: {result.score} - {result.payload}")
```

**Qdrant Advanced Features:**
```python
# Batch upsert for performance
client.upsert(
    collection_name="documents",
    points=points,
    wait=False  # Async write
)

# Named vectors (multiple embeddings per point)
client.create_collection(
    collection_name="multi",
    vectors_config={
        "title": VectorParams(size=384, distance=Distance.COSINE),
        "content": VectorParams(size=1536, distance=Distance.COSINE),
    }
)
```

{% elif database == "chroma" %}

### Chroma

Simple, embedded, perfect for prototyping and local development.

```python
import chromadb
from chromadb.utils import embedding_functions

# Persistent client
client = chromadb.PersistentClient(path="./chroma_data")

# Use OpenAI embeddings
openai_ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key="your-key",
    model_name="text-embedding-3-small"
)

# Create collection
collection = client.create_collection(
    name="documents",
    embedding_function=openai_ef,
    metadata={"hnsw:space": "cosine"}  # Distance metric
)

# Add documents (auto-embeds)
collection.add(
    ids=["doc1", "doc2"],
    documents=["First document text", "Second document text"],
    metadatas=[{"source": "wiki"}, {"source": "blog"}]
)

# Or add with pre-computed embeddings
collection.add(
    ids=["doc3"],
    embeddings=[embedding_vector],
    metadatas=[{"source": "api"}]
)

# Query
results = collection.query(
    query_texts=["search query"],  # Auto-embeds
    n_results=5,
    where={"source": "wiki"},  # Filter
    include=["documents", "metadatas", "distances"]
)

print(results["documents"])
print(results["distances"])
```

**Chroma Filtering:**
```python
# Simple equality
where={"source": "wiki"}

# Operators
where={"year": {"$gt": 2020}}

# Combine
where={"$and": [{"source": "wiki"}, {"year": {"$gte": 2020}}]}

# Document content filter
where_document={"$contains": "python"}
```

{% elif database == "pgvector" %}

### pgvector

Vector search in PostgreSQL. Great if you already use Postgres.

```sql
-- Enable extension
CREATE EXTENSION vector;

-- Create table with vector column
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536),  -- Dimension must match
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create HNSW index (recommended)
CREATE INDEX ON documents
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Or IVF index (for very large datasets)
CREATE INDEX ON documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Insert
INSERT INTO documents (content, embedding, metadata)
VALUES (
    'Document text here',
    '[0.1, 0.2, ...]'::vector,
    '{"source": "wiki"}'::jsonb
);

-- Search with cosine distance
SELECT id, content, 1 - (embedding <=> query_embedding) AS similarity
FROM documents
ORDER BY embedding <=> '[0.1, 0.2, ...]'::vector
LIMIT 5;

-- Search with filters (the power of SQL!)
SELECT id, content, 1 - (embedding <=> $1) AS similarity
FROM documents
WHERE metadata->>'source' = 'wiki'
  AND created_at > '2024-01-01'
ORDER BY embedding <=> $1
LIMIT 5;
```

**Python with pgvector:**
```python
import psycopg2
from pgvector.psycopg2 import register_vector

conn = psycopg2.connect("postgresql://...")
register_vector(conn)

cur = conn.cursor()

# Insert
cur.execute(
    "INSERT INTO documents (content, embedding) VALUES (%s, %s)",
    ("text", embedding)  # embedding is numpy array or list
)

# Search
cur.execute("""
    SELECT id, content, 1 - (embedding <=> %s) as similarity
    FROM documents
    ORDER BY embedding <=> %s
    LIMIT 5
""", (query_embedding, query_embedding))

results = cur.fetchall()
```

{% endif %}

---

## 4. Production Considerations

### Capacity Planning

```python
# Rough memory estimation for HNSW
def estimate_memory_gb(
    num_vectors: int,
    dimensions: int,
    m: int = 16,  # HNSW connections
) -> float:
    """Estimate memory for HNSW index."""
    # Vector storage
    vector_bytes = num_vectors * dimensions * 4  # float32

    # Graph storage (approximate)
    graph_bytes = num_vectors * m * 2 * 8  # links + levels

    # Overhead (~20%)
    total = (vector_bytes + graph_bytes) * 1.2

    return total / (1024 ** 3)  # Convert to GB

# Example: 1M vectors, 1536 dims
print(estimate_memory_gb(1_000_000, 1536))  # ~7.5 GB
```

### Batching for Performance

```python
def batch_upsert(client, vectors: list, batch_size: int = 100):
    """Upsert vectors in batches for better performance."""
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        client.upsert(
            collection_name="documents",
            points=batch,
            wait=False  # Async for speed
        )

    # Wait for final batch
    client.upsert(
        collection_name="documents",
        points=[],
        wait=True
    )
```

### Index Tuning

```python
# Production HNSW settings by scale
HNSW_CONFIGS = {
    "small": {      # < 100K vectors
        "m": 16,
        "ef_construct": 100,
        "ef_search": 50,
    },
    "medium": {     # 100K - 1M vectors
        "m": 32,
        "ef_construct": 200,
        "ef_search": 100,
    },
    "large": {      # > 1M vectors
        "m": 48,
        "ef_construct": 400,
        "ef_search": 200,
    },
}
```

### Monitoring

Track these metrics:
- **Query latency** (p50, p95, p99)
- **Recall rate** (if you have ground truth)
- **Index size** vs raw vector size
- **QPS** (queries per second)

```python
import time
from dataclasses import dataclass

@dataclass
class SearchMetrics:
    latency_ms: float
    num_results: int
    top_score: float

def search_with_metrics(client, query_vector, k: int = 5) -> tuple:
    """Search and return results with metrics."""
    start = time.perf_counter()

    results = client.search(
        collection_name="documents",
        query_vector=query_vector,
        limit=k
    )

    latency = (time.perf_counter() - start) * 1000

    metrics = SearchMetrics(
        latency_ms=latency,
        num_results=len(results),
        top_score=results[0].score if results else 0
    )

    return results, metrics
```

---

## 5. Common Patterns

### Hybrid Search (Vector + Keyword)

```python
from rank_bm25 import BM25Okapi

class HybridSearcher:
    """Combine vector similarity with BM25 keyword matching."""

    def __init__(self, vector_client, documents: list[str]):
        self.vector_client = vector_client
        self.documents = documents

        # Build BM25 index
        tokenized = [doc.split() for doc in documents]
        self.bm25 = BM25Okapi(tokenized)

    def search(self, query: str, query_vector: list, alpha: float = 0.7) -> list:
        """
        Hybrid search with configurable weighting.
        alpha: weight for vector search (1-alpha for BM25)
        """
        # Vector search
        vector_results = self.vector_client.search(
            collection_name="documents",
            query_vector=query_vector,
            limit=50
        )
        vector_scores = {r.id: r.score for r in vector_results}

        # BM25 search
        bm25_scores = self.bm25.get_scores(query.split())
        bm25_scores = dict(enumerate(bm25_scores))

        # Normalize scores
        vector_scores = self._normalize(vector_scores)
        bm25_scores = self._normalize(bm25_scores)

        # Combine
        all_ids = set(vector_scores.keys()) | set(bm25_scores.keys())
        combined = {}
        for doc_id in all_ids:
            v_score = vector_scores.get(doc_id, 0)
            b_score = bm25_scores.get(doc_id, 0)
            combined[doc_id] = alpha * v_score + (1 - alpha) * b_score

        # Sort by combined score
        return sorted(combined.items(), key=lambda x: x[1], reverse=True)

    def _normalize(self, scores: dict) -> dict:
        if not scores:
            return {}
        max_score = max(scores.values())
        if max_score == 0:
            return scores
        return {k: v / max_score for k, v in scores.items()}
```

### Multi-Tenant Isolation

```python
# Option 1: Namespaces (Pinecone)
index.upsert(vectors, namespace=f"tenant_{tenant_id}")
index.query(vector, namespace=f"tenant_{tenant_id}")

# Option 2: Metadata filtering (Qdrant, Chroma)
client.upsert(points=[
    PointStruct(id=1, vector=emb, payload={"tenant_id": "abc"})
])
client.search(
    query_vector=query,
    query_filter=Filter(must=[
        FieldCondition(key="tenant_id", match=MatchValue(value="abc"))
    ])
)

# Option 3: Separate collections (any DB)
client.create_collection(f"tenant_{tenant_id}")
```

### Incremental Updates

```python
def update_document(client, doc_id: str, new_embedding: list, new_metadata: dict):
    """Update a document's embedding and metadata."""
    # Most vector DBs support upsert (insert or update)
    client.upsert(
        collection_name="documents",
        points=[
            PointStruct(
                id=doc_id,
                vector=new_embedding,
                payload=new_metadata
            )
        ]
    )

def delete_document(client, doc_id: str):
    """Delete a document from the index."""
    client.delete(
        collection_name="documents",
        points_selector=PointIdsList(points=[doc_id])
    )
```

---

## Common Pitfalls

### 1. Wrong Distance Metric

```python
# BAD: Using euclidean for text embeddings
# Most text embeddings are normalized for cosine similarity

# GOOD: Match metric to embedding model
# OpenAI, Cohere → Cosine
# Some image models → Euclidean
```

### 2. Not Normalizing Embeddings

```python
# BAD: Assuming embeddings are normalized
index.upsert(vectors=raw_embeddings)

# GOOD: Normalize if using dot product
import numpy as np

def normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / norms

normalized = normalize(raw_embeddings)
```

### 3. Ignoring Index Warm-up

```python
# BAD: Expecting instant queries after bulk insert

# GOOD: Wait for indexing to complete
client.upsert(points=large_batch, wait=True)

# Or trigger optimization
client.update_collection(
    collection_name="documents",
    optimizer_config=OptimizersConfigDiff(indexing_threshold=0)
)
```

---

## Quick Reference

### Database Selection Flowchart

```
Need managed service with zero ops?
├── Yes → Pinecone
└── No → Self-host preference?
         ├── Kubernetes/Docker → Qdrant or Milvus
         └── Existing Postgres → pgvector

Prototyping or < 100K vectors?
└── Yes → Chroma (simplest setup)
```

### Index Selection

| Vectors | Index | Why |
|---------|-------|-----|
| < 10K | Flat/None | Brute force is fast enough |
| 10K - 1M | HNSW | Best recall/speed balance |
| > 1M | IVF + PQ | Memory efficiency |

---

## Related Skills

- `rag-patterns` - Using vectors for retrieval augmented generation
- `embeddings-guide` - Choosing and creating embeddings
- `semantic-search` - Building search systems

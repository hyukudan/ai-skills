---
name: rag-patterns
description: |
  Retrieval Augmented Generation (RAG) patterns and best practices. Use when building
  systems that combine document retrieval with LLM generation. Covers chunking strategies,
  embedding selection, retrieval methods, reranking, and production optimization.
license: MIT
allowed-tools: Read Edit Bash WebFetch
version: 1.0.0
tags: [ai, rag, embeddings, retrieval, llm, vector-search, langchain]
category: ai/rag
trigger_phrases:
  - "RAG"
  - "retrieval augmented"
  - "document retrieval"
  - "chunking strategy"
  - "embedding model"
  - "vector search"
  - "semantic search"
  - "knowledge base"
  - "document Q&A"
variables:
  use_case:
    type: string
    description: Primary RAG use case
    enum: [qa, search, chatbot, code]
    default: qa
  scale:
    type: string
    description: Scale of the system
    enum: [prototype, production, enterprise]
    default: prototype
---

# RAG Patterns Guide

## Core Philosophy

**RAG = Right Context + Right Model + Right Prompt.** The retrieval quality determines the ceiling of your system's performance.

> "Garbage in, garbage out applies doubly to RAG. Bad retrieval means bad answers, no matter how good your LLM."

---

## RAG Architecture Overview

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│  Documents  │────▶│   Chunking   │────▶│  Embedding  │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                                                ▼
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Answer    │◀────│     LLM      │◀────│  Retrieval  │
└─────────────┘     └──────────────┘     └─────────────┘
                           ▲
                           │
                    ┌──────┴──────┐
                    │    Query    │
                    └─────────────┘
```

---

## 1. Chunking Strategies

### The Chunking Dilemma

- **Too small**: Loses context, fragments meaning
- **Too large**: Dilutes relevance, wastes tokens
- **Just right**: Preserves semantic units

### Strategy Comparison

| Strategy | Best For | Chunk Size | Overlap |
|----------|----------|------------|---------|
| Fixed-size | Simple docs, logs | 500-1000 chars | 10-20% |
| Sentence-based | Articles, books | 3-5 sentences | 1 sentence |
| Semantic | Technical docs | Variable | By topic |
| Recursive | Structured content | Hierarchical | Parent context |

### Fixed-Size Chunking

```python
def fixed_chunk(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    """Simple fixed-size chunking with overlap."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks
```

**When to use**: Logs, code files, uniform documents

### Semantic Chunking

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""],  # Priority order
    length_function=len,
)

chunks = splitter.split_text(document)
```

**When to use**: Mixed content, markdown, documentation

### Document-Aware Chunking

```python
# For markdown with headers
def chunk_by_headers(markdown: str) -> list[dict]:
    """Chunk markdown preserving header context."""
    chunks = []
    current_headers = []
    current_content = []

    for line in markdown.split('\n'):
        if line.startswith('#'):
            if current_content:
                chunks.append({
                    'headers': current_headers.copy(),
                    'content': '\n'.join(current_content)
                })
                current_content = []

            level = len(line) - len(line.lstrip('#'))
            current_headers = current_headers[:level-1] + [line.strip('# ')]
        else:
            current_content.append(line)

    return chunks
```

---

## 2. Embedding Selection

### Model Comparison

| Model | Dimensions | Speed | Quality | Cost |
|-------|------------|-------|---------|------|
| OpenAI text-embedding-3-small | 1536 | Fast | Good | $0.02/1M |
| OpenAI text-embedding-3-large | 3072 | Medium | Excellent | $0.13/1M |
| Cohere embed-v3 | 1024 | Fast | Excellent | $0.10/1M |
| BGE-large-en | 1024 | Local | Very Good | Free |
| all-MiniLM-L6-v2 | 384 | Very Fast | Good | Free |

### Embedding Best Practices

```python
# 1. Batch your embeddings
embeddings = model.embed(texts, batch_size=100)  # Not one at a time

# 2. Normalize for cosine similarity
import numpy as np
normalized = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)

# 3. Cache embeddings
import hashlib
def get_cached_embedding(text: str, cache: dict) -> list[float]:
    key = hashlib.md5(text.encode()).hexdigest()
    if key not in cache:
        cache[key] = model.embed(text)
    return cache[key]
```

### Query vs Document Embeddings

Some models (like E5, BGE) need prefixes:

```python
# For E5 models
query_text = f"query: {user_question}"
doc_text = f"passage: {document_chunk}"

# For BGE models
query_text = f"Represent this sentence for searching: {user_question}"
```

---

## 3. Retrieval Methods

### Basic Vector Search

```python
from qdrant_client import QdrantClient

client = QdrantClient(":memory:")

# Search
results = client.search(
    collection_name="docs",
    query_vector=query_embedding,
    limit=5,
    score_threshold=0.7,  # Minimum similarity
)
```

### Hybrid Search (Vector + Keyword)

```python
# Combine BM25 (keyword) with vector search
from rank_bm25 import BM25Okapi

def hybrid_search(query: str, docs: list, alpha: float = 0.5) -> list:
    """
    alpha: weight for vector search (1-alpha for BM25)
    """
    # Vector scores
    vector_scores = vector_search(query, docs)

    # BM25 scores
    tokenized = [doc.split() for doc in docs]
    bm25 = BM25Okapi(tokenized)
    bm25_scores = bm25.get_scores(query.split())

    # Normalize and combine
    vector_norm = normalize(vector_scores)
    bm25_norm = normalize(bm25_scores)

    combined = alpha * vector_norm + (1 - alpha) * bm25_norm
    return sorted(zip(docs, combined), key=lambda x: x[1], reverse=True)
```

### Multi-Query Retrieval

```python
def multi_query_retrieve(question: str, retriever, llm) -> list:
    """Generate multiple query variations for better recall."""

    # Generate query variations
    prompt = f"""Generate 3 different versions of this question
    to improve document retrieval:

    Original: {question}

    Variations:"""

    variations = llm.generate(prompt).split('\n')

    # Retrieve for each variation
    all_docs = set()
    for query in [question] + variations:
        docs = retriever.search(query, k=3)
        all_docs.update(docs)

    return list(all_docs)
```

---

## 4. Reranking

### Why Rerank?

Embedding similarity does not equal answer relevance. Reranking uses cross-encoders for better accuracy.

```
Initial retrieval (fast, broad) → Reranking (slow, precise)
      100 candidates         →        Top 5
```

### Cross-Encoder Reranking

```python
from sentence_transformers import CrossEncoder

reranker = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

def rerank(query: str, documents: list[str], top_k: int = 5) -> list:
    """Rerank documents using cross-encoder."""
    pairs = [[query, doc] for doc in documents]
    scores = reranker.predict(pairs)

    ranked = sorted(zip(documents, scores), key=lambda x: x[1], reverse=True)
    return ranked[:top_k]
```

### Cohere Rerank API

```python
import cohere

co = cohere.Client("api-key")

results = co.rerank(
    query=question,
    documents=retrieved_docs,
    top_n=5,
    model="rerank-english-v2.0"
)
```

---

## 5. Query Processing

### Query Expansion

```python
def expand_query(query: str, llm) -> str:
    """Expand query with related terms."""
    prompt = f"""Given this search query, add relevant synonyms and related terms.
    Keep it concise.

    Query: {query}
    Expanded:"""

    return llm.generate(prompt)

# "python async" → "python async asyncio await coroutine concurrency"
```

### Hypothetical Document Embedding (HyDE)

```python
def hyde_search(question: str, llm, retriever) -> list:
    """Generate hypothetical answer, embed that instead of question."""

    # Generate hypothetical answer
    prompt = f"Write a short paragraph that answers: {question}"
    hypothetical = llm.generate(prompt)

    # Search using hypothetical answer's embedding
    return retriever.search(hypothetical)
```

---

## 6. Context Assembly

### Prompt Template

```python
RAG_PROMPT = """Answer the question based on the context below.
If the context doesn't contain the answer, say "I don't have enough information."

Context:
{context}

Question: {question}

Answer:"""
```

### Context Ordering

```python
def assemble_context(docs: list[str], max_tokens: int = 3000) -> str:
    """Assemble context with most relevant first, respecting token limit."""
    context_parts = []
    current_tokens = 0

    for i, doc in enumerate(docs):
        doc_tokens = count_tokens(doc)
        if current_tokens + doc_tokens > max_tokens:
            break

        # Add source reference
        context_parts.append(f"[Source {i+1}]\n{doc}")
        current_tokens += doc_tokens

    return "\n\n".join(context_parts)
```

---

## 7. Measuring Quality

### Key Metrics

| Metric | Measures | Target |
|--------|----------|--------|
| Retrieval Recall@k | % relevant docs in top k | > 80% |
| MRR (Mean Reciprocal Rank) | Position of first relevant doc | > 0.7 |
| Answer Faithfulness | Answer supported by context | > 90% |
| Answer Relevance | Answer addresses question | > 85% |

### Simple Quality Check

```python
def check_retrieval_quality(questions: list, ground_truth: list, retriever) -> dict:
    """Check retrieval quality metrics."""
    recalls = []
    mrrs = []

    for q, truth in zip(questions, ground_truth):
        retrieved = retriever.search(q, k=10)

        # Recall@10
        retrieved_set = set(retrieved)
        truth_set = set(truth)
        recall = len(retrieved_set & truth_set) / len(truth_set)
        recalls.append(recall)

        # MRR
        for i, doc in enumerate(retrieved):
            if doc in truth_set:
                mrrs.append(1 / (i + 1))
                break
        else:
            mrrs.append(0)

    return {
        'recall@10': sum(recalls) / len(recalls),
        'mrr': sum(mrrs) / len(mrrs)
    }
```

---

## Common Pitfalls

### 1. Ignoring Chunk Boundaries

```python
# BAD: Chunk cuts mid-sentence
"The algorithm works by first computing the"
"hash of each input and then comparing..."

# GOOD: Respect sentence boundaries
"The algorithm works by first computing the hash of each input."
"Then it compares the hashes to find matches..."
```

### 2. Not Handling No Results

```python
# BAD
context = "\n".join(retrieved_docs)
answer = llm.generate(prompt.format(context=context))

# GOOD
if not retrieved_docs or max(scores) < 0.5:
    return "I couldn't find relevant information to answer this question."

context = "\n".join(retrieved_docs)
answer = llm.generate(prompt.format(context=context))
```

### 3. Embedding Mismatch

```python
# BAD: Different models for indexing vs querying
index_embedding = openai_model.embed(doc)    # 1536 dims
query_embedding = local_model.embed(query)   # 384 dims  # Incompatible!

# GOOD: Same model always
embedding_model = OpenAIEmbeddings()
index_embedding = embedding_model.embed(doc)
query_embedding = embedding_model.embed(query)
```

---

{% if scale == "production" %}
## Production Considerations

### Scaling Vector Search

```python
# Use approximate nearest neighbor (ANN) for large scale
# Options: HNSW, IVF, PQ

# Qdrant with HNSW
client.create_collection(
    collection_name="docs",
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE,
    ),
    hnsw_config=HnswConfigDiff(
        m=16,              # Connections per node
        ef_construct=100,  # Build-time accuracy
    )
)
```

### Caching Strategy

```python
from functools import lru_cache
import hashlib

@lru_cache(maxsize=10000)
def cached_search(query_hash: str) -> list:
    # Cache frequent queries
    pass

def search_with_cache(query: str) -> list:
    query_hash = hashlib.md5(query.lower().strip().encode()).hexdigest()
    return cached_search(query_hash)
```

### Monitoring

Track these metrics in production:
- Retrieval latency (p50, p95, p99)
- Cache hit rate
- Empty result rate
- User feedback (thumbs up/down)
{% endif %}

---

## Quick Reference

### Recommended Stack by Scale

| Scale | Vector DB | Embedding | Reranker |
|-------|-----------|-----------|----------|
| Prototype | Chroma/Qdrant local | all-MiniLM | None |
| Production | Qdrant/Pinecone | OpenAI/Cohere | Cohere |
| Enterprise | Pinecone/Weaviate | OpenAI large | Cross-encoder |

### Chunking Quick Guide

| Content Type | Strategy | Size |
|--------------|----------|------|
| Documentation | Recursive by headers | 500-1000 |
| Code | By function/class | Whole unit |
| Chat logs | By conversation turn | Variable |
| Legal/contracts | By section/clause | 1000-2000 |

---

## Related Skills

- `vector-databases` - Deep dive into vector DB options
- `prompt-engineering` - Crafting effective RAG prompts
- `llm-integration` - Connecting to LLM providers

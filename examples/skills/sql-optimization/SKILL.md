---
name: sql-optimization
description: |
  SQL query optimization patterns and techniques. Covers EXPLAIN plans,
  indexing strategies, query rewriting, join optimization, and database-specific
  tuning for PostgreSQL, MySQL, and SQLite.
license: MIT
allowed-tools: Read Edit Bash
version: 1.0.0
tags: [sql, database, optimization, performance, indexing, postgres, mysql]
category: data/sql
trigger_phrases:
  - "SQL optimization"
  - "slow query"
  - "query performance"
  - "EXPLAIN"
  - "index strategy"
  - "database tuning"
  - "SQL performance"
  - "query plan"
variables:
  database:
    type: string
    description: Target database
    enum: [postgresql, mysql, sqlite]
    default: postgresql
---

# SQL Optimization Guide

## Core Philosophy

**Measure before optimizing.** Run EXPLAIN, check actual execution time, then fix the real bottleneck. Most performance issues are missing indexes or bad query patterns.

> "The best optimization is avoiding the query entirely. The second best is making sure it uses an index."

---

## Quick Diagnosis Checklist

```
□ Run EXPLAIN ANALYZE
□ Check for sequential scans on large tables
□ Look for missing indexes on JOIN/WHERE columns
□ Check for N+1 query patterns in application
□ Review row estimates vs actual rows
□ Check for expensive sorts
```

---

## 1. Reading EXPLAIN Plans

{% if database == "postgresql" %}

### PostgreSQL EXPLAIN

```sql
-- Basic explain
EXPLAIN SELECT * FROM orders WHERE customer_id = 123;

-- With execution stats (MUST run query)
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 123;

-- Full details
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders WHERE customer_id = 123;
```

### Understanding the Output

```
Seq Scan on orders  (cost=0.00..1234.00 rows=100 width=50)
  Filter: (customer_id = 123)
  Rows Removed by Filter: 9900
```

| Term | Meaning | Concern |
|------|---------|---------|
| **Seq Scan** | Full table scan | Add index |
| **Index Scan** | Using index | Good |
| **Index Only Scan** | Index covers query | Best |
| **Bitmap Heap Scan** | Index + heap lookup | OK for many rows |
| **Nested Loop** | For each row, scan other | Check inner scan |
| **Hash Join** | Build hash table | Memory usage |
| **Sort** | Sorting rows | Check if needed |

### Cost Numbers

```
(cost=0.00..1234.00 rows=100 width=50)
       ↑        ↑      ↑        ↑
    startup  total  estimated  row size
```

- **Startup cost**: Time to return first row
- **Total cost**: Time to return all rows
- **rows**: Estimated rows (can be wrong!)
- **width**: Average row size in bytes

{% elif database == "mysql" %}

### MySQL EXPLAIN

```sql
-- Basic explain
EXPLAIN SELECT * FROM orders WHERE customer_id = 123;

-- With execution details (MySQL 8.0+)
EXPLAIN ANALYZE SELECT * FROM orders WHERE customer_id = 123;

-- Format as JSON for more details
EXPLAIN FORMAT=JSON SELECT * FROM orders WHERE customer_id = 123;
```

### Key Columns

| Column | Meaning | Ideal |
|--------|---------|-------|
| **type** | Join type | const, ref, range |
| **possible_keys** | Indexes considered | Not empty |
| **key** | Index used | Not NULL |
| **rows** | Estimated rows | Low |
| **Extra** | Additional info | Using index |

### Type Values (Best to Worst)

```
const → eq_ref → ref → range → index → ALL
  ↓        ↓       ↓      ↓       ↓      ↓
single  unique  non-   range   full   full
row     match   unique  scan   index  table
                match          scan   scan
```

{% endif %}

---

## 2. Indexing Strategies

### When to Index

| Index When | Don't Index When |
|------------|------------------|
| Column in WHERE frequently | Low cardinality (few unique values) |
| Column in JOIN condition | Table is small (< 1000 rows) |
| Column in ORDER BY | Column rarely queried |
| Foreign keys | Heavy write workload |

### Index Types

```sql
-- B-tree (default, most common)
CREATE INDEX idx_customer_id ON orders(customer_id);

-- Composite index (column order matters!)
CREATE INDEX idx_customer_date ON orders(customer_id, created_at);

-- Partial index (PostgreSQL) - index subset of rows
CREATE INDEX idx_active_orders ON orders(customer_id)
WHERE status = 'active';

-- Covering index - includes all needed columns
CREATE INDEX idx_covering ON orders(customer_id)
INCLUDE (total, status);

-- Hash index (PostgreSQL) - equality only, faster
CREATE INDEX idx_hash ON orders USING hash(customer_id);
```

### Composite Index Rules

```sql
-- Index on (a, b, c) can be used for:
WHERE a = ?                    -- ✓ Uses index
WHERE a = ? AND b = ?          -- ✓ Uses index
WHERE a = ? AND b = ? AND c = ?  -- ✓ Uses index
WHERE b = ?                    -- ✗ Can't use index
WHERE a = ? AND c = ?          -- △ Uses only 'a' part

-- ORDER BY follows same rules
ORDER BY a                     -- ✓
ORDER BY a, b                  -- ✓
ORDER BY a, b, c               -- ✓
ORDER BY b, a                  -- ✗ Wrong order
```

### Index-Only Scans

```sql
-- Table: orders(id, customer_id, total, status, created_at)

-- BAD: Has to fetch from table
SELECT * FROM orders WHERE customer_id = 123;

-- BETTER: Can use index-only scan
SELECT customer_id, total FROM orders WHERE customer_id = 123;

-- Create covering index
CREATE INDEX idx_customer_covering ON orders(customer_id) INCLUDE (total);
```

---

## 3. Query Patterns

### Avoiding N+1 Queries

```sql
-- BAD: N+1 pattern (1 query + N queries)
SELECT * FROM customers;  -- Get 100 customers
-- Then for each customer:
SELECT * FROM orders WHERE customer_id = ?;  -- 100 queries!

-- GOOD: Single query with JOIN
SELECT c.*, o.*
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id;

-- Or batch load
SELECT * FROM orders WHERE customer_id IN (1, 2, 3, ...);
```

### Pagination

```sql
-- BAD: OFFSET scales poorly
SELECT * FROM orders ORDER BY id LIMIT 20 OFFSET 10000;
-- Has to skip 10000 rows!

-- GOOD: Keyset pagination
SELECT * FROM orders
WHERE id > 10000  -- Last seen ID
ORDER BY id
LIMIT 20;

-- With multiple columns
SELECT * FROM orders
WHERE (created_at, id) > ('2024-01-01', 12345)
ORDER BY created_at, id
LIMIT 20;
```

### Counting Efficiently

```sql
-- BAD: Full count on large table
SELECT COUNT(*) FROM orders WHERE status = 'pending';

-- BETTER: Approximate count (PostgreSQL)
SELECT reltuples::bigint FROM pg_class WHERE relname = 'orders';

-- Or use cached count
-- Maintain a counts table updated by triggers

-- GOOD: Count with limit check
SELECT EXISTS(SELECT 1 FROM orders WHERE status = 'pending');
```

### Batch Operations

```sql
-- BAD: Insert one at a time
INSERT INTO orders (customer_id, total) VALUES (1, 100);
INSERT INTO orders (customer_id, total) VALUES (2, 200);
...

-- GOOD: Batch insert
INSERT INTO orders (customer_id, total)
VALUES
  (1, 100),
  (2, 200),
  (3, 300);

-- With conflict handling (PostgreSQL)
INSERT INTO inventory (product_id, quantity)
VALUES (1, 10), (2, 20)
ON CONFLICT (product_id) DO UPDATE
SET quantity = inventory.quantity + EXCLUDED.quantity;
```

---

## 4. Join Optimization

### Join Order Matters

```sql
-- Let optimizer choose (usually best)
SELECT *
FROM orders o
JOIN customers c ON c.id = o.customer_id
JOIN products p ON p.id = o.product_id;

-- Force order if needed
SELECT /*+ LEADING(o c p) */ *  -- MySQL hint
FROM orders o
JOIN customers c ON c.id = o.customer_id
JOIN products p ON p.id = o.product_id;
```

### Reducing Join Cost

```sql
-- BAD: Join then filter
SELECT * FROM orders o
JOIN line_items li ON li.order_id = o.id
WHERE o.status = 'pending';

-- BETTER: Filter first (usually optimizer does this)
SELECT * FROM (
  SELECT * FROM orders WHERE status = 'pending'
) o
JOIN line_items li ON li.order_id = o.id;

-- BEST: Make sure index exists on orders(status)
```

### EXISTS vs JOIN vs IN

```sql
-- For checking existence, EXISTS is usually fastest
SELECT * FROM customers c
WHERE EXISTS (
  SELECT 1 FROM orders o WHERE o.customer_id = c.id
);

-- IN with subquery can be slow for large sets
SELECT * FROM customers
WHERE id IN (SELECT customer_id FROM orders);  -- Can be slow

-- JOIN returns duplicates if multiple matches
SELECT DISTINCT c.* FROM customers c
JOIN orders o ON o.customer_id = c.id;  -- Need DISTINCT
```

---

## 5. Common Anti-Patterns

### Functions on Indexed Columns

```sql
-- BAD: Function prevents index use
SELECT * FROM orders WHERE YEAR(created_at) = 2024;

-- GOOD: Range query uses index
SELECT * FROM orders
WHERE created_at >= '2024-01-01'
  AND created_at < '2025-01-01';

-- BAD: LOWER() prevents index use
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';

-- GOOD: Use expression index (PostgreSQL)
CREATE INDEX idx_email_lower ON users(LOWER(email));
-- Or store lowercase in separate column
```

### SELECT *

```sql
-- BAD: Fetches all columns
SELECT * FROM orders WHERE customer_id = 123;

-- GOOD: Only needed columns
SELECT id, total, status FROM orders WHERE customer_id = 123;

-- Benefits:
-- 1. Less data transfer
-- 2. Can use covering index
-- 3. Clearer intent
```

### OR Conditions

```sql
-- BAD: OR often prevents index use
SELECT * FROM orders
WHERE customer_id = 123 OR status = 'pending';

-- BETTER: UNION can use both indexes
SELECT * FROM orders WHERE customer_id = 123
UNION ALL
SELECT * FROM orders WHERE status = 'pending'
  AND customer_id != 123;  -- Avoid duplicates
```

### LIKE with Leading Wildcard

```sql
-- BAD: Can't use index
SELECT * FROM products WHERE name LIKE '%phone%';

-- Options:
-- 1. Full-text search (PostgreSQL)
SELECT * FROM products
WHERE to_tsvector('english', name) @@ to_tsquery('phone');

-- 2. Trigram index (PostgreSQL)
CREATE INDEX idx_name_trgm ON products
USING gin(name gin_trgm_ops);

-- 3. Trailing wildcard (if acceptable)
SELECT * FROM products WHERE name LIKE 'phone%';  -- Uses index
```

---

## 6. Query Rewriting

### Subquery to JOIN

```sql
-- Subquery (can be slower)
SELECT *
FROM orders
WHERE customer_id IN (
  SELECT id FROM customers WHERE country = 'US'
);

-- JOIN (often faster)
SELECT o.*
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE c.country = 'US';
```

### Correlated to Non-Correlated

```sql
-- Correlated subquery (runs for each row)
SELECT *
FROM orders o
WHERE total > (
  SELECT AVG(total) FROM orders WHERE customer_id = o.customer_id
);

-- Non-correlated (runs once, then joins)
SELECT o.*
FROM orders o
JOIN (
  SELECT customer_id, AVG(total) as avg_total
  FROM orders
  GROUP BY customer_id
) c ON c.customer_id = o.customer_id
WHERE o.total > c.avg_total;
```

### DISTINCT to GROUP BY

```sql
-- DISTINCT
SELECT DISTINCT customer_id FROM orders;

-- GROUP BY (same result, sometimes faster)
SELECT customer_id FROM orders GROUP BY customer_id;
```

---

## 7. PostgreSQL-Specific

{% if database == "postgresql" %}

### CTEs and Performance

```sql
-- Before PG12: CTEs were optimization fences
-- PG12+: Optimizer can inline CTEs

-- Force materialization if needed
WITH orders_cte AS MATERIALIZED (
  SELECT * FROM orders WHERE status = 'pending'
)
SELECT * FROM orders_cte;

-- Or allow inlining
WITH orders_cte AS NOT MATERIALIZED (
  SELECT * FROM orders WHERE status = 'pending'
)
SELECT * FROM orders_cte;
```

### Window Functions Efficiency

```sql
-- Avoid multiple passes
-- BAD: Two separate window operations
SELECT
  *,
  (SELECT COUNT(*) FROM orders o2 WHERE o2.customer_id = o.customer_id) as total_orders,
  (SELECT SUM(total) FROM orders o3 WHERE o3.customer_id = o.customer_id) as total_spent
FROM orders o;

-- GOOD: Single window function
SELECT
  *,
  COUNT(*) OVER (PARTITION BY customer_id) as total_orders,
  SUM(total) OVER (PARTITION BY customer_id) as total_spent
FROM orders;
```

### JSONB Performance

```sql
-- Index JSONB field
CREATE INDEX idx_data_email ON users USING gin((data->'email'));

-- Or specific path
CREATE INDEX idx_data_address ON users((data->>'city'));

-- Query using index
SELECT * FROM users WHERE data->>'city' = 'New York';
```

{% endif %}

---

## Quick Reference

### Index Decision Matrix

| Query Pattern | Index Type |
|--------------|------------|
| `WHERE a = ?` | B-tree on (a) |
| `WHERE a = ? AND b = ?` | Composite (a, b) |
| `WHERE a = ? ORDER BY b` | Composite (a, b) |
| `WHERE a IN (?, ?, ?)` | B-tree on (a) |
| `WHERE a LIKE 'prefix%'` | B-tree on (a) |
| `WHERE a LIKE '%substring%'` | Trigram/Full-text |
| `WHERE a @> ARRAY[?]` | GIN (array) |

### Performance Targets

| Metric | Target | Action if Exceeded |
|--------|--------|-------------------|
| Query time | < 100ms | Add indexes, rewrite |
| Rows scanned | 10x result | Add indexes |
| Seq scan on large table | Avoid | Add index |
| Memory usage | < work_mem | Tune or rewrite |

---

## Related Skills

- `postgresql-advanced` - Advanced PostgreSQL features
- `data-modeling` - Schema design patterns
- `database-migrations` - Schema change strategies

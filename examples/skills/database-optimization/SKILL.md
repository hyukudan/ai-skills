---
name: database-optimization
description: |
  Database performance optimization techniques. Covers cursor pagination, query
  optimization, N+1 problems, connection pooling, indexing strategies, lock
  contention, and slow query diagnosis. Use when queries are slow or DB is bottleneck.
version: 1.0.0
tags: [database, performance, sql, optimization, pagination, queries]
category: development/backend
scope:
  triggers:
    - slow query
    - database performance
    - pagination
    - cursor pagination
    - N+1
    - query optimization
    - connection pool
    - database bottleneck
---

# Database Optimization

## Pagination: Cursor vs Offset

### The Offset Problem

```sql
-- Offset pagination (common but broken at scale)
SELECT * FROM posts ORDER BY created_at DESC LIMIT 20 OFFSET 10000;

-- Why it's slow:
-- 1. DB must scan and discard 10,000 rows to return 20
-- 2. Gets worse as offset increases: O(offset + limit)
-- 3. Inconsistent results if data changes between pages
```

**Performance degradation:**
```
Offset 0:      ~5ms
Offset 1000:   ~50ms
Offset 10000:  ~500ms
Offset 100000: ~5000ms+  <- unusable
```

### Cursor Pagination (Keyset)

```sql
-- Instead of offset, use the last seen value as cursor
SELECT * FROM posts
WHERE created_at < '2024-01-15T10:30:00Z'  -- cursor
ORDER BY created_at DESC
LIMIT 20;

-- Why it's fast:
-- 1. Uses index directly, no row scanning
-- 2. Constant time O(limit) regardless of page depth
-- 3. Consistent results even with concurrent writes
```

**Implementation pattern:**

```python
# Encode cursor (timestamp + id for uniqueness)
def encode_cursor(post):
    return base64.b64encode(
        f"{post.created_at.isoformat()}:{post.id}".encode()
    ).decode()

def decode_cursor(cursor):
    decoded = base64.b64decode(cursor).decode()
    timestamp, id = decoded.rsplit(":", 1)
    return datetime.fromisoformat(timestamp), int(id)

# Query with cursor
def get_posts(cursor=None, limit=20):
    query = Post.query.order_by(Post.created_at.desc(), Post.id.desc())

    if cursor:
        ts, id = decode_cursor(cursor)
        # Tie-breaker: if same timestamp, use id
        query = query.filter(
            db.or_(
                Post.created_at < ts,
                db.and_(Post.created_at == ts, Post.id < id)
            )
        )

    posts = query.limit(limit + 1).all()  # +1 to check if more exist

    has_next = len(posts) > limit
    posts = posts[:limit]

    return {
        "data": posts,
        "next_cursor": encode_cursor(posts[-1]) if has_next else None
    }
```

**API response format:**

```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "MjAyNC0wMS0xNVQxMDozMDowMFo6MTIzNA==",
    "has_more": true
  }
}
```

### When to Use Each

| Use Case | Offset | Cursor |
|----------|--------|--------|
| Admin dashboard (small data) | OK | Overkill |
| User-facing feeds | NO | YES |
| Search results | Maybe | YES |
| "Jump to page 50" | Only option | Not possible |
| Infinite scroll | NO | YES |
| Data exports | NO | YES |

---

## N+1 Query Problem

### The Problem

```python
# BAD: N+1 queries
posts = Post.query.all()  # 1 query
for post in posts:
    print(post.author.name)  # N queries (one per post)

# Generated SQL:
# SELECT * FROM posts;
# SELECT * FROM users WHERE id = 1;
# SELECT * FROM users WHERE id = 2;
# ... repeated N times
```

### Solutions

**1. Eager Loading (JOIN)**

```python
# SQLAlchemy
posts = Post.query.options(joinedload(Post.author)).all()

# Django
posts = Post.objects.select_related('author').all()

# Generated SQL:
# SELECT posts.*, users.* FROM posts JOIN users ON posts.author_id = users.id
```

**2. Batch Loading (IN clause)**

```python
# SQLAlchemy
posts = Post.query.options(selectinload(Post.comments)).all()

# Django
posts = Post.objects.prefetch_related('comments').all()

# Generated SQL:
# SELECT * FROM posts;
# SELECT * FROM comments WHERE post_id IN (1, 2, 3, ...);
```

**3. DataLoader Pattern (GraphQL)**

```python
from promise import Promise
from promise.dataloader import DataLoader

class UserLoader(DataLoader):
    def batch_load_fn(self, user_ids):
        users = {u.id: u for u in User.query.filter(User.id.in_(user_ids))}
        return Promise.resolve([users.get(id) for id in user_ids])

# Usage: automatically batches within same request
user_loader = UserLoader()
user1 = user_loader.load(1)
user2 = user_loader.load(2)  # Batched with user1
```

### Detection

```sql
-- PostgreSQL: Enable logging
SET log_min_duration_statement = 0;  -- Log all queries

-- Look for patterns like:
-- SELECT * FROM users WHERE id = 1;
-- SELECT * FROM users WHERE id = 2;
-- (repeated)
```

---

## Query Optimization

### Read EXPLAIN Output

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders WHERE user_id = 123 AND status = 'pending';

-- Key things to look for:
-- Seq Scan        -> Missing index, full table scan
-- Index Scan      -> Using index (good)
-- Bitmap Scan     -> Multiple conditions combined
-- Sort            -> Memory/disk sort (check work_mem)
-- Hash Join       -> Building hash table
-- Nested Loop     -> O(n*m) - fine for small tables
-- actual rows     -> Compare with estimated rows
```

**Red flags:**
```
Seq Scan on orders (rows=1000000)  <- needs index
Sort Method: external merge Disk   <- increase work_mem
Rows Removed by Filter: 999990     <- index not selective
```

### Index Optimization

```sql
-- Composite index order matters
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- This query uses the index:
SELECT * FROM orders WHERE user_id = 123 AND status = 'pending';

-- This query CAN'T use the index efficiently:
SELECT * FROM orders WHERE status = 'pending';
-- (status is second column, can't skip user_id)

-- Covering index (avoids table lookup)
CREATE INDEX idx_orders_cover ON orders(user_id) INCLUDE (total, status);

SELECT total, status FROM orders WHERE user_id = 123;
-- Index-only scan, no heap fetch
```

### Common Optimizations

```sql
-- 1. EXISTS vs COUNT
-- BAD:
SELECT COUNT(*) > 0 FROM orders WHERE user_id = 123;
-- GOOD:
SELECT EXISTS(SELECT 1 FROM orders WHERE user_id = 123);

-- 2. Avoid functions on indexed columns
-- BAD (can't use index):
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';
-- GOOD (use functional index or fix data):
CREATE INDEX idx_users_email_lower ON users(LOWER(email));

-- 3. LIMIT subqueries
-- BAD:
SELECT * FROM posts WHERE author_id IN (SELECT id FROM users WHERE active);
-- GOOD (if you only need a few):
SELECT * FROM posts WHERE author_id IN (
  SELECT id FROM users WHERE active LIMIT 1000
);

-- 4. Batch operations
-- BAD:
DELETE FROM logs WHERE created_at < '2024-01-01';  -- locks table
-- GOOD:
DELETE FROM logs WHERE id IN (
  SELECT id FROM logs WHERE created_at < '2024-01-01' LIMIT 1000
);
-- Repeat until done
```

---

## Connection Pooling

### Why Pools Matter

```
Without pooling:
Request -> Create connection (~50ms) -> Query -> Close connection
Request -> Create connection (~50ms) -> Query -> Close connection

With pooling:
Request -> Get connection from pool (~0ms) -> Query -> Return to pool
Request -> Get connection from pool (~0ms) -> Query -> Return to pool
```

### Pool Sizing

```python
# Rule of thumb:
# connections = (core_count * 2) + effective_spindle_count

# For SSD with 4 cores:
# connections = (4 * 2) + 1 = 9

# But also consider:
# - Number of app instances
# - Connection limits on DB server
# - Blocking operations in code
```

**PostgreSQL config:**
```sql
-- Check current limits
SHOW max_connections;  -- Default 100

-- In postgresql.conf
max_connections = 100
```

**Application-side (SQLAlchemy):**
```python
engine = create_engine(
    DATABASE_URL,
    pool_size=5,           # Maintained connections
    max_overflow=10,       # Extra connections when pool exhausted
    pool_timeout=30,       # Wait time for connection
    pool_recycle=1800,     # Recycle connections after 30 min
    pool_pre_ping=True,    # Verify connection before use
)
```

### PgBouncer (Connection Multiplexer)

```ini
# pgbouncer.ini
[databases]
mydb = host=localhost dbname=mydb

[pgbouncer]
pool_mode = transaction    # session | transaction | statement
max_client_conn = 1000     # Client connections
default_pool_size = 20     # Connections per user/db pair
```

**Pool modes:**
```
session:     Connection held for entire client session
transaction: Connection returned after each transaction (recommended)
statement:   Connection returned after each statement (limited use)
```

---

## Lock Contention

### Types of Locks

```sql
-- Row-level locks
SELECT * FROM accounts WHERE id = 1 FOR UPDATE;  -- Exclusive
SELECT * FROM accounts WHERE id = 1 FOR SHARE;   -- Shared

-- Table-level locks (implicit)
ALTER TABLE users ADD COLUMN foo TEXT;  -- ACCESS EXCLUSIVE
CREATE INDEX CONCURRENTLY ...;          -- SHARE UPDATE EXCLUSIVE
```

### Deadlock Prevention

```sql
-- BAD: Inconsistent ordering
-- Transaction 1:
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- Transaction 2:
UPDATE accounts SET balance = balance - 50 WHERE id = 2;
UPDATE accounts SET balance = balance + 50 WHERE id = 1;
-- DEADLOCK!

-- GOOD: Consistent ordering (always lock lower ID first)
-- Transaction 1:
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;

-- Transaction 2:
UPDATE accounts SET balance = balance + 50 WHERE id = 1;
UPDATE accounts SET balance = balance - 50 WHERE id = 2;
```

### Advisory Locks (Application-level)

```sql
-- Acquire lock (blocks until available)
SELECT pg_advisory_lock(12345);

-- Try lock (returns immediately)
SELECT pg_try_advisory_lock(12345);  -- Returns true/false

-- Release
SELECT pg_advisory_unlock(12345);

-- Use case: Prevent duplicate cron jobs
SELECT pg_try_advisory_lock(hashtext('daily_report'));
-- If true, run job. If false, another instance is running.
```

---

## Slow Query Diagnosis

### Enable Logging

```sql
-- PostgreSQL
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1s
SELECT pg_reload_conf();

-- Or in postgresql.conf
log_min_duration_statement = 1000
log_statement = 'all'  # For debugging only
```

### Find Slow Queries

```sql
-- PostgreSQL: pg_stat_statements extension
CREATE EXTENSION pg_stat_statements;

SELECT
    round(total_exec_time::numeric, 2) as total_time_ms,
    calls,
    round(mean_exec_time::numeric, 2) as avg_time_ms,
    query
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 10;
```

### Index Usage Stats

```sql
-- Unused indexes (candidates for removal)
SELECT
    schemaname || '.' || relname AS table,
    indexrelname AS index,
    pg_size_pretty(pg_relation_size(i.indexrelid)) AS size,
    idx_scan as times_used
FROM pg_stat_user_indexes i
JOIN pg_index USING (indexrelid)
WHERE idx_scan = 0
AND NOT indisunique
ORDER BY pg_relation_size(i.indexrelid) DESC;

-- Missing indexes (sequential scans on large tables)
SELECT
    schemaname || '.' || relname AS table,
    seq_scan,
    seq_tup_read,
    idx_scan,
    n_live_tup as rows
FROM pg_stat_user_tables
WHERE seq_scan > 0
AND n_live_tup > 10000
ORDER BY seq_tup_read DESC;
```

---

## Maintenance

### VACUUM (PostgreSQL)

```sql
-- Dead rows accumulate from UPDATE/DELETE
-- VACUUM reclaims space and updates statistics

-- Manual vacuum
VACUUM ANALYZE users;

-- Aggressive vacuum (rewrites table)
VACUUM FULL users;  -- Locks table, use carefully

-- Check bloat
SELECT
    relname,
    n_dead_tup,
    n_live_tup,
    round(n_dead_tup * 100.0 / nullif(n_live_tup, 0), 2) as dead_pct
FROM pg_stat_user_tables
WHERE n_dead_tup > 1000
ORDER BY n_dead_tup DESC;
```

### Autovacuum Tuning

```sql
-- Check autovacuum activity
SELECT
    relname,
    last_vacuum,
    last_autovacuum,
    vacuum_count,
    autovacuum_count
FROM pg_stat_user_tables;

-- For high-write tables, tune thresholds
ALTER TABLE events SET (
    autovacuum_vacuum_threshold = 1000,
    autovacuum_vacuum_scale_factor = 0.05
);
```

### Index Maintenance

```sql
-- Rebuild bloated indexes
REINDEX INDEX CONCURRENTLY idx_orders_user;

-- Check index bloat (pg_stat_user_indexes)
SELECT
    indexrelname,
    pg_size_pretty(pg_relation_size(indexrelid)) as size,
    idx_scan as scans
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;
```

---

## Caching Strategies

### Query Cache (Application)

```python
import redis
import json

cache = redis.Redis()

def get_user(user_id):
    cache_key = f"user:{user_id}"

    # Try cache
    cached = cache.get(cache_key)
    if cached:
        return json.loads(cached)

    # Query DB
    user = db.query(User).get(user_id)

    # Cache for 5 minutes
    cache.setex(cache_key, 300, json.dumps(user.to_dict()))

    return user

def update_user(user_id, data):
    # Update DB
    user = db.query(User).get(user_id)
    user.update(data)
    db.commit()

    # Invalidate cache
    cache.delete(f"user:{user_id}")
```

### Materialized Views (PostgreSQL)

```sql
-- Create materialized view for expensive query
CREATE MATERIALIZED VIEW dashboard_stats AS
SELECT
    date_trunc('day', created_at) as day,
    COUNT(*) as orders,
    SUM(total) as revenue
FROM orders
GROUP BY 1;

-- Create index on materialized view
CREATE INDEX idx_dashboard_day ON dashboard_stats(day);

-- Refresh (blocks reads)
REFRESH MATERIALIZED VIEW dashboard_stats;

-- Refresh concurrently (requires unique index)
CREATE UNIQUE INDEX idx_dashboard_unique ON dashboard_stats(day);
REFRESH MATERIALIZED VIEW CONCURRENTLY dashboard_stats;
```

### Read Replicas

```python
# Route reads to replica, writes to primary
from sqlalchemy import create_engine

primary = create_engine("postgresql://primary/db")
replica = create_engine("postgresql://replica/db")

def get_engine(readonly=False):
    return replica if readonly else primary

# Usage
with get_engine(readonly=True).connect() as conn:
    result = conn.execute("SELECT * FROM users WHERE id = 1")
```

---

## Quick Checklist

```
Query slow? Check in order:
1. [ ] Is there an index? (EXPLAIN shows Seq Scan)
2. [ ] Is the index being used? (wrong column order, function on column)
3. [ ] Are statistics current? (ANALYZE table)
4. [ ] N+1 problem? (check query count)
5. [ ] Can you add LIMIT?
6. [ ] Can you cache?

Pagination:
1. [ ] Using cursor for user-facing lists
2. [ ] Offset only for admin/small datasets
3. [ ] Cursor includes tie-breaker (timestamp + id)

Connection issues:
1. [ ] Pool size appropriate for load
2. [ ] Connections being returned (no leaks)
3. [ ] Using PgBouncer for many short connections
```

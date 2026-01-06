---
name: performance-optimization
description: |
  Performance optimization techniques for applications and databases. Use when
  profiling slow code, optimizing queries, implementing caching, or improving
  response times. Covers profiling tools, common bottlenecks, and optimization patterns.
version: 1.0.0
tags: [performance, optimization, profiling, caching, scalability]
category: development/performance
variables:
  language:
    type: string
    description: Programming language
    enum: [python, javascript, typescript, go, java]
    default: python
  focus:
    type: string
    description: Optimization focus area
    enum: [cpu, memory, database, network, all]
    default: all
---

# Performance Optimization Guide

## Philosophy

**Measure, don't guess.** Premature optimization is the root of all evil, but ignoring performance is negligence.

### Optimization Process

```
1. MEASURE  → Profile to find actual bottlenecks
2. ANALYZE  → Understand why it's slow
3. OPTIMIZE → Fix the biggest bottleneck first
4. VERIFY   → Measure again to confirm improvement
5. REPEAT   → Until performance goals are met
```

> "Make it work, make it right, make it fast—in that order." — Kent Beck

---

## Profiling Tools

{% if language == "python" %}
### Python Profiling

**cProfile - CPU Profiling:**

```python
import cProfile
import pstats
from io import StringIO

def profile_function(func, *args, **kwargs):
    profiler = cProfile.Profile()
    profiler.enable()

    result = func(*args, **kwargs)

    profiler.disable()

    # Analyze results
    stream = StringIO()
    stats = pstats.Stats(profiler, stream=stream)
    stats.sort_stats('cumulative')
    stats.print_stats(20)

    print(stream.getvalue())
    return result

# Usage
profile_function(expensive_operation, data)

# Or from command line
# python -m cProfile -s cumulative script.py
```

**line_profiler - Line-by-Line:**

```python
# Install: pip install line_profiler
# Add @profile decorator to functions
@profile
def slow_function():
    result = []
    for i in range(10000):
        result.append(expensive_calculation(i))
    return result

# Run: kernprof -l -v script.py
```

**memory_profiler - Memory Usage:**

```python
from memory_profiler import profile

@profile
def memory_heavy_function():
    data = [i ** 2 for i in range(1000000)]
    return sum(data)

# Run: python -m memory_profiler script.py
```

**py-spy - Production Profiling:**

```bash
# Profile running process without modification
py-spy top --pid 12345

# Generate flame graph
py-spy record -o profile.svg --pid 12345
```

{% elif language == "javascript" or language == "typescript" %}
### Node.js Profiling

**Built-in Profiler:**

```bash
# Generate V8 profile
node --prof app.js

# Process the log
node --prof-process isolate-*.log > processed.txt
```

**clinic.js - Performance Toolkit:**

```bash
npm install -g clinic

# CPU profiling with flame graph
clinic flame -- node app.js

# Detect event loop issues
clinic doctor -- node app.js

# Memory profiling
clinic heap -- node app.js
```

**Performance Hooks:**

```typescript
import { performance, PerformanceObserver } from 'perf_hooks';

// Measure function duration
const measureAsync = async <T>(name: string, fn: () => Promise<T>): Promise<T> => {
  const start = performance.now();
  try {
    return await fn();
  } finally {
    const duration = performance.now() - start;
    console.log(`${name}: ${duration.toFixed(2)}ms`);
  }
};

// Usage
const result = await measureAsync('fetchUsers', () => db.users.findAll());
```

{% endif %}

---

{% if focus == "cpu" or focus == "all" %}
## CPU Optimization

### Algorithm Complexity

```
O(1)       → Constant: Hash lookup, array index
O(log n)   → Logarithmic: Binary search, balanced tree
O(n)       → Linear: Single loop, array scan
O(n log n) → Linearithmic: Good sorting (mergesort, quicksort)
O(n²)      → Quadratic: Nested loops, bubble sort
O(2ⁿ)      → Exponential: Recursive fibonacci (naive)
```

{% if language == "python" %}
**Optimize Hot Paths:**

```python
# BAD: O(n) lookup in list
def find_user(users: list, user_id: str):
    for user in users:
        if user.id == user_id:
            return user
    return None

# GOOD: O(1) lookup with dict
users_by_id = {user.id: user for user in users}
def find_user(user_id: str):
    return users_by_id.get(user_id)

# BAD: Repeated computation
def process_items(items):
    for item in items:
        config = load_config()  # Called N times!
        process(item, config)

# GOOD: Compute once
def process_items(items):
    config = load_config()  # Called once
    for item in items:
        process(item, config)
```

**Use Built-in Functions:**

```python
# BAD: Manual loop
total = 0
for x in numbers:
    total += x

# GOOD: Built-in (implemented in C)
total = sum(numbers)

# BAD: Manual membership check
found = False
for item in items:
    if item == target:
        found = True
        break

# GOOD: Use 'in' operator
found = target in items

# Even better: Use set for O(1) lookup
item_set = set(items)
found = target in item_set
```

**List Comprehensions vs Loops:**

```python
# Slower: append in loop
result = []
for x in range(1000):
    result.append(x ** 2)

# Faster: list comprehension
result = [x ** 2 for x in range(1000)]

# Even faster for large data: generator
result = (x ** 2 for x in range(1000))  # Lazy evaluation
```

{% elif language == "javascript" or language == "typescript" %}
**Optimize Hot Paths:**

```typescript
// BAD: Array.find is O(n)
const findUser = (users: User[], id: string) => users.find(u => u.id === id);

// GOOD: Map lookup is O(1)
const usersById = new Map(users.map(u => [u.id, u]));
const findUser = (id: string) => usersById.get(id);

// BAD: Repeated object creation
function process(items: Item[]) {
  items.forEach(item => {
    const config = { threshold: 100, multiplier: 1.5 }; // Created N times
    transform(item, config);
  });
}

// GOOD: Reuse object
function process(items: Item[]) {
  const config = { threshold: 100, multiplier: 1.5 }; // Created once
  items.forEach(item => transform(item, config));
}
```

**Avoid Array Method Chains:**

```typescript
// BAD: Multiple iterations
const result = items
  .filter(x => x.active)      // Iteration 1
  .map(x => x.value)          // Iteration 2
  .reduce((a, b) => a + b, 0); // Iteration 3

// GOOD: Single iteration
const result = items.reduce((sum, x) => {
  return x.active ? sum + x.value : sum;
}, 0);
```

{% endif %}

{% endif %}

---

{% if focus == "memory" or focus == "all" %}
## Memory Optimization

### Identify Memory Issues

{% if language == "python" %}
```python
import tracemalloc
import gc

# Start tracing
tracemalloc.start()

# Your code here
process_data()

# Get stats
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("Top 10 memory allocations:")
for stat in top_stats[:10]:
    print(stat)

# Check for reference cycles
gc.collect()
print(f"Uncollectable: {len(gc.garbage)}")
```

**Common Memory Issues:**

```python
# ISSUE: Holding references
class Cache:
    items = {}  # Class variable - never garbage collected!

# FIX: Use WeakValueDictionary
from weakref import WeakValueDictionary
class Cache:
    items = WeakValueDictionary()

# ISSUE: Large strings
data = file.read()  # Entire file in memory

# FIX: Stream processing
for line in file:
    process(line)

# ISSUE: Growing lists
results = []
for item in huge_dataset:
    results.append(transform(item))

# FIX: Generator for lazy evaluation
def transform_items(dataset):
    for item in dataset:
        yield transform(item)
```

{% elif language == "javascript" or language == "typescript" %}
```typescript
// ISSUE: Event listener memory leak
element.addEventListener('click', handler);
// Never removed!

// FIX: Use AbortController
const controller = new AbortController();
element.addEventListener('click', handler, { signal: controller.signal });
// Later: controller.abort();

// ISSUE: Closures holding references
function createHandler(largeData: Buffer) {
  return () => {
    // largeData is retained in closure even if unused!
    console.log('clicked');
  };
}

// FIX: Don't capture what you don't need
function createHandler() {
  return () => {
    console.log('clicked');
  };
}

// ISSUE: Unbounded caches
const cache = new Map<string, Data>();
function getData(key: string): Data {
  if (!cache.has(key)) {
    cache.set(key, fetchData(key)); // Grows forever!
  }
  return cache.get(key)!;
}

// FIX: LRU cache with size limit
import LRU from 'lru-cache';
const cache = new LRU<string, Data>({ max: 1000 });
```

{% endif %}

{% endif %}

---

{% if focus == "database" or focus == "all" %}
## Database Optimization

### Query Analysis

```sql
-- PostgreSQL: Analyze query plan
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- Look for:
-- Seq Scan → Full table scan (add index?)
-- High "actual time" → Slow operation
-- "rows=1000" but "loops=1000" → N+1 problem
```

### Indexing Strategy

```sql
-- Single column index
CREATE INDEX idx_users_email ON users(email);

-- Composite index (column order matters!)
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at DESC);

-- Partial index (smaller, faster)
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- Covering index (avoids table lookup)
CREATE INDEX idx_orders_summary ON orders(user_id) INCLUDE (total, status);
```

### N+1 Query Problem

{% if language == "python" %}
```python
# BAD: N+1 queries
users = db.query(User).all()
for user in users:
    orders = db.query(Order).filter(Order.user_id == user.id).all()
    # 1 query for users + N queries for orders

# GOOD: Eager loading
users = db.query(User).options(joinedload(User.orders)).all()
# 1 query with JOIN

# GOOD: Batch loading
users = db.query(User).all()
user_ids = [u.id for u in users]
orders = db.query(Order).filter(Order.user_id.in_(user_ids)).all()
# 2 queries total
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
// BAD: N+1 queries
const users = await db.user.findMany();
for (const user of users) {
  const orders = await db.order.findMany({ where: { userId: user.id } });
}

// GOOD: Include related data (Prisma)
const users = await db.user.findMany({
  include: { orders: true }
});

// GOOD: DataLoader for batching (GraphQL)
const orderLoader = new DataLoader(async (userIds) => {
  const orders = await db.order.findMany({
    where: { userId: { in: userIds } }
  });
  return userIds.map(id => orders.filter(o => o.userId === id));
});
```
{% endif %}

### Query Optimization Tips

```sql
-- Use LIMIT for pagination
SELECT * FROM orders ORDER BY created_at DESC LIMIT 20 OFFSET 40;

-- Select only needed columns
SELECT id, email, name FROM users;  -- Not SELECT *

-- Use EXISTS instead of COUNT for existence check
SELECT EXISTS(SELECT 1 FROM orders WHERE user_id = 123);

-- Batch inserts
INSERT INTO logs (message) VALUES ('a'), ('b'), ('c');

-- Use COPY for bulk loads (PostgreSQL)
COPY users FROM '/path/to/file.csv' WITH CSV HEADER;
```

{% endif %}

---

## Caching Strategies

### Cache Patterns

```
┌─────────────────────────────────────────────────┐
│              CACHING PATTERNS                    │
├─────────────────────────────────────────────────┤
│ Cache-Aside (Lazy Loading)                      │
│   1. Check cache                                │
│   2. If miss, fetch from DB                     │
│   3. Store in cache                             │
│   4. Return data                                │
├─────────────────────────────────────────────────┤
│ Write-Through                                   │
│   1. Write to cache AND DB                      │
│   2. Both always in sync                        │
├─────────────────────────────────────────────────┤
│ Write-Behind (Write-Back)                       │
│   1. Write to cache                             │
│   2. Async write to DB                          │
│   3. Better performance, risk of data loss      │
└─────────────────────────────────────────────────┘
```

{% if language == "python" %}
### Implementation

```python
import redis
import json
from functools import wraps
from datetime import timedelta

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cached(ttl: timedelta = timedelta(minutes=5), prefix: str = "cache"):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Build cache key
            key = f"{prefix}:{func.__name__}:{hash((args, tuple(sorted(kwargs.items()))))}"

            # Try cache
            cached_value = redis_client.get(key)
            if cached_value:
                return json.loads(cached_value)

            # Call function
            result = await func(*args, **kwargs)

            # Store in cache
            redis_client.setex(key, ttl, json.dumps(result))

            return result
        return wrapper
    return decorator

# Usage
@cached(ttl=timedelta(minutes=10))
async def get_user_profile(user_id: str) -> dict:
    return await db.users.find_one({"id": user_id})

# Invalidation
def invalidate_user_cache(user_id: str):
    pattern = f"cache:get_user_profile:*{user_id}*"
    for key in redis_client.scan_iter(pattern):
        redis_client.delete(key)
```
{% endif %}

### Cache Invalidation Strategies

```
1. Time-Based (TTL)
   - Simple, eventual consistency
   - Good for: read-heavy, tolerance for stale data

2. Event-Based
   - Invalidate on write/update
   - Good for: data that changes unpredictably

3. Version-Based
   - Include version in cache key
   - Good for: coordinated cache invalidation

4. Tag-Based
   - Associate cache entries with tags
   - Invalidate all entries with a tag
   - Good for: related data (user's posts, comments)
```

---

## Web Performance

### Response Time Optimization

```
Target latencies:
- API responses: < 200ms (p95)
- Page load: < 3s
- Time to interactive: < 5s
```

### HTTP Optimization

```python
# Compression
from fastapi import FastAPI
from fastapi.middleware.gzip import GZipMiddleware

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Response caching headers
from fastapi.responses import Response

@app.get("/static-data")
async def get_static_data(response: Response):
    response.headers["Cache-Control"] = "public, max-age=3600"
    return {"data": "..."}

# Pagination
@app.get("/items")
async def list_items(cursor: str = None, limit: int = 20):
    items = await db.items.find(after=cursor).limit(limit + 1)
    has_more = len(items) > limit
    return {
        "data": items[:limit],
        "next_cursor": items[-1].id if has_more else None
    }
```

---

## Optimization Checklist

### Before Optimizing
- [ ] Have performance requirements defined
- [ ] Have baseline measurements
- [ ] Have profiling data identifying bottlenecks
- [ ] Have tests to verify behavior

### Common Quick Wins
- [ ] Add database indexes for slow queries
- [ ] Implement caching for repeated computations
- [ ] Use connection pooling
- [ ] Enable compression (gzip/brotli)
- [ ] Fix N+1 query problems
- [ ] Use pagination for large datasets

### Avoid Premature Optimization
- [ ] Focus on clarity first
- [ ] Optimize only measured bottlenecks
- [ ] Document performance-critical code
- [ ] Keep optimization changes small and testable

---
name: caching-strategies
description: |
  Caching patterns and strategies for improving application performance.
  Use when implementing caching layers, choosing cache invalidation strategies,
  or optimizing read-heavy workloads with Redis, Memcached, or in-memory caches.
license: MIT
allowed-tools: Read Edit Bash
version: 1.0.0
tags: [caching, redis, performance, scalability, memory]
category: development/infrastructure
triggers:
  - cache
  - caching
  - redis
  - memcached
  - cdn
  - cache invalidation
  - cache miss
  - cache hit
  - ttl
variables:
  cache_type:
    type: string
    description: Type of cache implementation
    enum: [redis, in-memory, cdn, database]
    default: redis
  language:
    type: string
    description: Implementation language
    enum: [python, javascript, go]
    default: python
---

# Caching Strategies

## Why Cache?

```
Without cache:  Client ─────────────────────── Database
                        100ms per request

With cache:     Client ── Cache (hit) ──────── 1-5ms
                        │
                        └── Cache (miss) ──── Database ── 100ms
                                                          (then cached)
```

**Cache hit ratio target: 80-95%+**

---

## Caching Patterns

### 1. Cache-Aside (Lazy Loading)

Application manages cache explicitly.

```
Read:  Check cache → if miss → read DB → write cache → return
Write: Update DB → invalidate cache
```

{% if language == "python" %}
```python
from functools import lru_cache
import redis

redis_client = redis.Redis()

def get_user(user_id: str) -> dict:
    # Check cache
    cached = redis_client.get(f"user:{user_id}")
    if cached:
        return json.loads(cached)

    # Cache miss - load from DB
    user = db.users.find_one({"_id": user_id})
    if user:
        redis_client.setex(
            f"user:{user_id}",
            3600,  # TTL: 1 hour
            json.dumps(user)
        )
    return user

def update_user(user_id: str, data: dict):
    # Update DB first
    db.users.update_one({"_id": user_id}, {"$set": data})
    # Invalidate cache
    redis_client.delete(f"user:{user_id}")
```
{% elif language == "javascript" %}
```typescript
import Redis from 'ioredis';

const redis = new Redis();

async function getUser(userId: string): Promise<User | null> {
  // Check cache
  const cached = await redis.get(`user:${userId}`);
  if (cached) {
    return JSON.parse(cached);
  }

  // Cache miss - load from DB
  const user = await db.users.findOne({ _id: userId });
  if (user) {
    await redis.setex(`user:${userId}`, 3600, JSON.stringify(user));
  }
  return user;
}

async function updateUser(userId: string, data: Partial<User>): Promise<void> {
  await db.users.updateOne({ _id: userId }, { $set: data });
  await redis.del(`user:${userId}`);
}
```
{% else %}
```go
func GetUser(userID string) (*User, error) {
    // Check cache
    cached, err := redisClient.Get(ctx, "user:"+userID).Result()
    if err == nil {
        var user User
        json.Unmarshal([]byte(cached), &user)
        return &user, nil
    }

    // Cache miss - load from DB
    user, err := db.FindUser(userID)
    if err != nil {
        return nil, err
    }

    // Store in cache
    data, _ := json.Marshal(user)
    redisClient.SetEX(ctx, "user:"+userID, data, time.Hour)
    return user, nil
}
```
{% endif %}

**Pros:** Simple, only caches what's needed
**Cons:** Cache miss penalty, potential stale data

---

### 2. Write-Through

Write to cache and DB simultaneously.

```
Write: Write cache → Write DB (sync)
Read:  Read cache (always hit)
```

{% if language == "python" %}
```python
def create_user(user: dict) -> dict:
    # Write to DB
    result = db.users.insert_one(user)
    user["_id"] = str(result.inserted_id)

    # Write to cache (synchronously)
    redis_client.setex(
        f"user:{user['_id']}",
        3600,
        json.dumps(user)
    )
    return user
```
{% else %}
```typescript
async function createUser(user: User): Promise<User> {
  // Write to DB
  const result = await db.users.insertOne(user);
  user._id = result.insertedId;

  // Write to cache (synchronously)
  await redis.setex(`user:${user._id}`, 3600, JSON.stringify(user));
  return user;
}
```
{% endif %}

**Pros:** Cache always fresh, no miss on reads
**Cons:** Write latency, cache may have unused data

---

### 3. Write-Behind (Write-Back)

Write to cache immediately, async write to DB.

```
Write: Write cache → Queue DB write → Return immediately
       (Background worker persists to DB)
```

{% if language == "python" %}
```python
import asyncio
from collections import deque

write_queue = deque()

async def create_user_fast(user: dict) -> dict:
    user["_id"] = generate_id()

    # Write to cache immediately
    await redis_client.setex(
        f"user:{user['_id']}",
        3600,
        json.dumps(user)
    )

    # Queue for async DB write
    write_queue.append(("insert", "users", user))
    return user

async def background_writer():
    """Batch writes to database."""
    while True:
        batch = []
        while write_queue and len(batch) < 100:
            batch.append(write_queue.popleft())

        if batch:
            await db.bulk_write(batch)

        await asyncio.sleep(0.1)
```
{% else %}
```typescript
const writeQueue: Array<{op: string, data: any}> = [];

async function createUserFast(user: User): Promise<User> {
  user._id = generateId();

  // Write to cache immediately
  await redis.setex(`user:${user._id}`, 3600, JSON.stringify(user));

  // Queue for async DB write
  writeQueue.push({ op: 'insert', data: user });
  return user;
}

// Background worker
setInterval(async () => {
  const batch = writeQueue.splice(0, 100);
  if (batch.length > 0) {
    await db.bulkWrite(batch);
  }
}, 100);
```
{% endif %}

**Pros:** Very fast writes, batching efficiency
**Cons:** Data loss risk, complexity

---

## Cache Invalidation

> "There are only two hard things in Computer Science: cache invalidation and naming things." - Phil Karlton

### Strategies

#### 1. Time-Based (TTL)

```
Set TTL → Data expires automatically → Next read fetches fresh data
```

{% if language == "python" %}
```python
# Simple TTL
redis_client.setex("key", 3600, "value")  # 1 hour

# Sliding TTL (refresh on read)
def get_with_sliding_ttl(key: str, ttl: int = 3600):
    value = redis_client.get(key)
    if value:
        redis_client.expire(key, ttl)  # Reset TTL
    return value
```
{% else %}
```typescript
// Simple TTL
await redis.setex('key', 3600, 'value');

// Sliding TTL
async function getWithSlidingTTL(key: string, ttl = 3600) {
  const value = await redis.get(key);
  if (value) {
    await redis.expire(key, ttl);
  }
  return value;
}
```
{% endif %}

#### 2. Event-Based

```
DB change → Publish event → Invalidate cache
```

{% if language == "python" %}
```python
# Pub/Sub invalidation
def on_user_updated(user_id: str):
    redis_client.publish("cache:invalidate", f"user:{user_id}")

# Subscriber
def cache_invalidator():
    pubsub = redis_client.pubsub()
    pubsub.subscribe("cache:invalidate")
    for message in pubsub.listen():
        if message["type"] == "message":
            redis_client.delete(message["data"])
```
{% else %}
```typescript
// Pub/Sub invalidation
function onUserUpdated(userId: string) {
  redis.publish('cache:invalidate', `user:${userId}`);
}

// Subscriber
const subscriber = redis.duplicate();
subscriber.subscribe('cache:invalidate');
subscriber.on('message', (channel, key) => {
  redis.del(key);
});
```
{% endif %}

#### 3. Version-Based

```
Cache key includes version → Increment version to invalidate
```

{% if language == "python" %}
```python
def get_versioned(resource: str, id: str) -> dict:
    version = redis_client.get(f"{resource}:version") or "1"
    key = f"{resource}:{id}:v{version}"

    cached = redis_client.get(key)
    if cached:
        return json.loads(cached)

    data = fetch_from_db(resource, id)
    redis_client.setex(key, 3600, json.dumps(data))
    return data

def invalidate_all(resource: str):
    """Invalidate all cached items of this resource type."""
    redis_client.incr(f"{resource}:version")
```
{% else %}
```typescript
async function getVersioned(resource: string, id: string) {
  const version = await redis.get(`${resource}:version`) || '1';
  const key = `${resource}:${id}:v${version}`;

  const cached = await redis.get(key);
  if (cached) return JSON.parse(cached);

  const data = await fetchFromDb(resource, id);
  await redis.setex(key, 3600, JSON.stringify(data));
  return data;
}

async function invalidateAll(resource: string) {
  await redis.incr(`${resource}:version`);
}
```
{% endif %}

---

## Cache Key Design

### Best Practices

```
# Structure: {prefix}:{entity}:{id}:{variant}
user:123                    # Basic
user:123:profile            # Subset
user:123:friends:page:1     # Paginated
search:products:q=shoes     # Query-based
api:v2:users:123           # Versioned API
```

{% if language == "python" %}
```python
def cache_key(*parts, **kwargs) -> str:
    """Generate consistent cache keys."""
    base = ":".join(str(p) for p in parts)
    if kwargs:
        suffix = ":".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
        return f"{base}:{suffix}"
    return base

# Usage
cache_key("user", user_id)                    # "user:123"
cache_key("search", "products", q="shoes")    # "search:products:q=shoes"
```
{% else %}
```typescript
function cacheKey(...parts: (string | number)[]): string {
  return parts.join(':');
}

// With query params
function cacheKeyWithParams(
  base: string[],
  params: Record<string, string>
): string {
  const suffix = Object.entries(params)
    .sort(([a], [b]) => a.localeCompare(b))
    .map(([k, v]) => `${k}=${v}`)
    .join(':');
  return [...base, suffix].join(':');
}
```
{% endif %}

---

{% if cache_type == "redis" %}
## Redis Patterns

### Distributed Locking

```python
def acquire_lock(name: str, timeout: int = 10) -> str | None:
    """Acquire distributed lock using Redis."""
    token = str(uuid.uuid4())
    acquired = redis_client.set(
        f"lock:{name}",
        token,
        nx=True,  # Only if not exists
        ex=timeout
    )
    return token if acquired else None

def release_lock(name: str, token: str) -> bool:
    """Release lock only if we own it (uses Lua script for atomicity)."""
    # Use redis-py's built-in lock or transaction
    pipe = redis_client.pipeline(True)
    try:
        pipe.watch(f"lock:{name}")
        if pipe.get(f"lock:{name}") == token:
            pipe.multi()
            pipe.delete(f"lock:{name}")
            pipe.execute()
            return True
    except redis.WatchError:
        pass
    return False
```

### Rate Limiting

```python
def is_rate_limited(key: str, limit: int, window: int) -> bool:
    """Sliding window rate limiter."""
    now = time.time()
    pipeline = redis_client.pipeline()

    # Remove old entries
    pipeline.zremrangebyscore(key, 0, now - window)
    # Add current request
    pipeline.zadd(key, {str(now): now})
    # Count requests in window
    pipeline.zcard(key)
    # Set expiry
    pipeline.expire(key, window)

    results = pipeline.execute()
    return results[2] > limit
```

{% elif cache_type == "in-memory" %}
## In-Memory Caching

### LRU Cache

{% if language == "python" %}
```python
from functools import lru_cache
from cachetools import TTLCache, LRUCache

# Built-in LRU
@lru_cache(maxsize=1000)
def expensive_computation(x: int) -> int:
    return x ** x

# TTL + LRU with cachetools
cache = TTLCache(maxsize=1000, ttl=300)

def get_cached(key: str, fetch_func):
    if key in cache:
        return cache[key]
    value = fetch_func()
    cache[key] = value
    return value
```
{% else %}
```typescript
class LRUCache<K, V> {
  private cache = new Map<K, V>();
  private maxSize: number;

  constructor(maxSize: number) {
    this.maxSize = maxSize;
  }

  get(key: K): V | undefined {
    const value = this.cache.get(key);
    if (value !== undefined) {
      // Move to end (most recently used)
      this.cache.delete(key);
      this.cache.set(key, value);
    }
    return value;
  }

  set(key: K, value: V): void {
    if (this.cache.has(key)) {
      this.cache.delete(key);
    } else if (this.cache.size >= this.maxSize) {
      // Remove oldest (first item)
      const firstKey = this.cache.keys().next().value;
      this.cache.delete(firstKey);
    }
    this.cache.set(key, value);
  }
}
```
{% endif %}

{% elif cache_type == "cdn" %}
## CDN Caching

### Cache-Control Headers

```http
# Cache for 1 hour, allow CDN to cache
Cache-Control: public, max-age=3600

# Cache for 1 day, stale-while-revalidate for 1 hour
Cache-Control: public, max-age=86400, stale-while-revalidate=3600

# Private (user-specific), no CDN caching
Cache-Control: private, max-age=600

# No caching at all
Cache-Control: no-store

# Revalidate every time
Cache-Control: no-cache
```

### ETag Validation

```python
from hashlib import md5

@app.get("/api/products/{id}")
def get_product(id: str, request: Request):
    product = db.get_product(id)
    etag = md5(json.dumps(product).encode()).hexdigest()

    if request.headers.get("If-None-Match") == etag:
        return Response(status_code=304)

    return Response(
        content=json.dumps(product),
        headers={
            "ETag": etag,
            "Cache-Control": "public, max-age=300"
        }
    )
```

{% endif %}

---

## Cache Warming

Pre-populate cache before traffic hits.

{% if language == "python" %}
```python
async def warm_cache():
    """Pre-populate cache on startup."""
    # Get most accessed items
    popular_ids = await get_popular_item_ids(limit=1000)

    async def warm_item(item_id):
        data = await fetch_from_db(item_id)
        await redis_client.setex(f"item:{item_id}", 3600, json.dumps(data))

    # Warm in batches
    for batch in chunked(popular_ids, 100):
        await asyncio.gather(*[warm_item(id) for id in batch])

# Run on startup
asyncio.create_task(warm_cache())
```
{% else %}
```typescript
async function warmCache(): Promise<void> {
  const popularIds = await getPopularItemIds(1000);

  for (let i = 0; i < popularIds.length; i += 100) {
    const batch = popularIds.slice(i, i + 100);
    await Promise.all(batch.map(async (id) => {
      const data = await fetchFromDb(id);
      await redis.setex(`item:${id}`, 3600, JSON.stringify(data));
    }));
  }
}

// Run on startup
warmCache().catch(console.error);
```
{% endif %}

---

## Monitoring

Track these metrics:
- **Hit ratio**: `hits / (hits + misses)` - target > 80%
- **Latency**: Cache read/write times
- **Memory usage**: Eviction rates
- **Key count**: Total cached items

```python
# Simple hit/miss tracking
def get_cached_with_metrics(key: str):
    value = redis_client.get(key)
    if value:
        metrics.increment("cache.hit")
    else:
        metrics.increment("cache.miss")
    return value
```

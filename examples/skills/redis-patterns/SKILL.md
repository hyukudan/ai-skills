---
name: redis-patterns
description: |
  Redis data structures and patterns for caching, rate limiting, queues,
  pub/sub, and real-time features. Practical examples for common use cases.
version: 1.0.0
tags: [redis, caching, queues, pubsub, rate-limiting]
category: databases/redis
trigger_phrases:
  - "Redis"
  - "caching"
  - "rate limiting"
  - "message queue"
  - "pub/sub"
  - "session storage"
  - "leaderboard"
variables:
  use_case:
    type: string
    description: Primary use case
    enum: [caching, queues, realtime, general]
    default: caching
---

# Redis Patterns Guide

## Core Philosophy

**Redis is a data structure server, not just a cache.** Its power comes from atomic operations on rich data structures.

> "The right data structure makes the algorithm trivial."

---

## Data Structures Overview

| Structure | Use Case | Commands |
|-----------|----------|----------|
| **String** | Caching, counters | GET, SET, INCR |
| **Hash** | Objects, sessions | HGET, HSET, HGETALL |
| **List** | Queues, timelines | LPUSH, RPOP, LRANGE |
| **Set** | Unique items, tags | SADD, SMEMBERS, SINTER |
| **Sorted Set** | Leaderboards, timelines | ZADD, ZRANGE, ZRANK |
| **Stream** | Event logs, messaging | XADD, XREAD, XREADGROUP |

---

## 1. Caching Patterns

{% if use_case == "caching" %}

### Cache-Aside Pattern

```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, decode_responses=True)

def get_user(user_id: str) -> dict:
    """Cache-aside pattern: check cache first, then database."""
    cache_key = f"user:{user_id}"

    # Try cache
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)

    # Cache miss - fetch from database
    user = database.get_user(user_id)
    if user:
        # Cache for 1 hour
        r.setex(cache_key, 3600, json.dumps(user))

    return user

def update_user(user_id: str, data: dict):
    """Update database and invalidate cache."""
    database.update_user(user_id, data)
    r.delete(f"user:{user_id}")
```

### Write-Through Cache

```python
def save_user(user_id: str, data: dict):
    """Write to cache and database together."""
    cache_key = f"user:{user_id}"

    # Write to both
    database.save_user(user_id, data)
    r.setex(cache_key, 3600, json.dumps(data))
```

### Cache with Stale-While-Revalidate

```python
import time
import threading

def get_with_stale_revalidate(key: str, fetch_fn, ttl: int = 3600, stale_ttl: int = 60):
    """Return stale data while refreshing in background."""
    data = r.get(key)
    metadata = r.hgetall(f"{key}:meta")

    if data:
        expires_at = float(metadata.get('expires_at', 0))

        if time.time() < expires_at:
            return json.loads(data)  # Fresh data

        if time.time() < expires_at + stale_ttl:
            # Return stale, refresh in background
            threading.Thread(target=_refresh_cache, args=(key, fetch_fn, ttl)).start()
            return json.loads(data)

    # No data or too stale
    return _refresh_cache(key, fetch_fn, ttl)

def _refresh_cache(key: str, fetch_fn, ttl: int):
    """Refresh cache with fresh data."""
    data = fetch_fn()
    pipe = r.pipeline()
    pipe.setex(key, ttl + 60, json.dumps(data))
    pipe.hset(f"{key}:meta", 'expires_at', time.time() + ttl)
    pipe.execute()
    return data
```

{% endif %}

---

## 2. Rate Limiting

### Sliding Window Rate Limiter

```python
def is_rate_limited(user_id: str, limit: int = 100, window_seconds: int = 60) -> bool:
    """Sliding window rate limiter using sorted sets."""
    key = f"ratelimit:{user_id}"
    now = time.time()
    window_start = now - window_seconds

    pipe = r.pipeline()

    # Remove old entries
    pipe.zremrangebyscore(key, 0, window_start)

    # Count current window
    pipe.zcard(key)

    # Add current request
    pipe.zadd(key, {str(now): now})

    # Set expiry
    pipe.expire(key, window_seconds)

    results = pipe.execute()
    request_count = results[1]

    return request_count >= limit

# Usage
if is_rate_limited(user_id):
    return {"error": "Rate limit exceeded"}, 429
```

### Token Bucket Rate Limiter

```python
def check_rate_limit(user_id: str, tokens_per_second: float = 10, bucket_size: int = 100) -> bool:
    """Token bucket algorithm using Lua script for atomicity."""
    # Lua script ensures atomic check-and-update
    lua_script = """
    local key = KEYS[1]
    local rate = tonumber(ARGV[1])
    local capacity = tonumber(ARGV[2])
    local now = tonumber(ARGV[3])
    local requested = tonumber(ARGV[4])

    local data = redis.call('HMGET', key, 'tokens', 'last_update')
    local tokens = tonumber(data[1]) or capacity
    local last_update = tonumber(data[2]) or now

    local delta = (now - last_update) * rate
    tokens = math.min(capacity, tokens + delta)

    if tokens >= requested then
        tokens = tokens - requested
        redis.call('HMSET', key, 'tokens', tokens, 'last_update', now)
        redis.call('EXPIRE', key, 60)
        return 1
    end
    return 0
    """
    # Register and run the script
    script = r.register_script(lua_script)
    result = script(keys=[f"bucket:{user_id}"],
                    args=[tokens_per_second, bucket_size, time.time(), 1])
    return result == 1
```

---

## 3. Queues and Messaging

### Simple Queue

```python
def enqueue(queue_name: str, item: dict):
    """Add item to queue."""
    r.lpush(queue_name, json.dumps(item))

def dequeue(queue_name: str, timeout: int = 0):
    """Remove and return item from queue (blocking)."""
    result = r.brpop(queue_name, timeout=timeout)
    if result:
        return json.loads(result[1])
    return None

# Worker
while True:
    task = dequeue("tasks")
    if task:
        process(task)
```

### Reliable Queue with Acknowledgment

```python
def reliable_dequeue(queue_name: str, processing_queue: str, timeout: int = 0):
    """Move item to processing queue atomically."""
    result = r.brpoplpush(queue_name, processing_queue, timeout)
    return json.loads(result) if result else None

def acknowledge(processing_queue: str, item: str):
    """Remove from processing queue after successful processing."""
    r.lrem(processing_queue, 1, item)

def requeue_failed(processing_queue: str, queue_name: str):
    """Move failed items back to main queue."""
    while True:
        item = r.rpoplpush(processing_queue, queue_name)
        if not item:
            break
```

### Pub/Sub

```python
# Publisher
def publish_event(channel: str, event: dict):
    r.publish(channel, json.dumps(event))

# Subscriber
def subscribe_events(channels: list):
    pubsub = r.pubsub()
    pubsub.subscribe(*channels)

    for message in pubsub.listen():
        if message['type'] == 'message':
            event = json.loads(message['data'])
            handle_event(message['channel'], event)
```

---

## 4. Real-Time Features

### Leaderboard

```python
class Leaderboard:
    def __init__(self, name: str):
        self.key = f"leaderboard:{name}"

    def add_score(self, user_id: str, score: float):
        """Add or update user's score."""
        r.zadd(self.key, {user_id: score})

    def increment_score(self, user_id: str, delta: float):
        """Increment user's score."""
        r.zincrby(self.key, delta, user_id)

    def get_rank(self, user_id: str) -> int:
        """Get user's rank (0-indexed, None if not found)."""
        rank = r.zrevrank(self.key, user_id)
        return rank + 1 if rank is not None else None

    def get_top(self, n: int = 10) -> list:
        """Get top N users with scores."""
        results = r.zrevrange(self.key, 0, n - 1, withscores=True)
        return [{"user_id": user, "score": score, "rank": i + 1}
                for i, (user, score) in enumerate(results)]

    def get_around_user(self, user_id: str, count: int = 5) -> list:
        """Get users around a specific user."""
        rank = r.zrevrank(self.key, user_id)
        if rank is None:
            return []

        start = max(0, rank - count // 2)
        end = start + count - 1
        return r.zrevrange(self.key, start, end, withscores=True)
```

### Session Storage

```python
class SessionStore:
    def __init__(self, prefix: str = "session", ttl: int = 3600):
        self.prefix = prefix
        self.ttl = ttl

    def create(self, session_id: str, data: dict) -> str:
        """Create new session."""
        key = f"{self.prefix}:{session_id}"
        r.hset(key, mapping=data)
        r.expire(key, self.ttl)
        return session_id

    def get(self, session_id: str) -> dict:
        """Get session data."""
        key = f"{self.prefix}:{session_id}"
        data = r.hgetall(key)
        if data:
            r.expire(key, self.ttl)  # Extend TTL on access
        return data

    def update(self, session_id: str, data: dict):
        """Update session data."""
        key = f"{self.prefix}:{session_id}"
        r.hset(key, mapping=data)

    def destroy(self, session_id: str):
        """Delete session."""
        r.delete(f"{self.prefix}:{session_id}")
```

### Distributed Locking

```python
import uuid

class DistributedLock:
    def __init__(self, name: str, ttl: int = 10):
        self.key = f"lock:{name}"
        self.ttl = ttl
        self.token = str(uuid.uuid4())

    def acquire(self, blocking: bool = True, timeout: int = None) -> bool:
        """Acquire the lock."""
        start = time.time()

        while True:
            if r.set(self.key, self.token, nx=True, ex=self.ttl):
                return True

            if not blocking:
                return False

            if timeout and (time.time() - start) > timeout:
                return False

            time.sleep(0.1)

    def release(self):
        """Release the lock (only if we own it)."""
        # Use Lua script for atomic check-and-delete
        lua_script = """
        if redis.call('get', KEYS[1]) == ARGV[1] then
            return redis.call('del', KEYS[1])
        end
        return 0
        """
        script = r.register_script(lua_script)
        script(keys=[self.key], args=[self.token])

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, *args):
        self.release()

# Usage
with DistributedLock("resource-name"):
    # Critical section
    do_something()
```

---

## 5. Performance Tips

### Pipelining

```python
# BAD: Multiple round trips
for user_id in user_ids:
    r.get(f"user:{user_id}")

# GOOD: Single round trip
pipe = r.pipeline()
for user_id in user_ids:
    pipe.get(f"user:{user_id}")
results = pipe.execute()
```

### Memory Optimization

```python
# Use hashes for small objects (more memory efficient)
# Instead of: user:123:name, user:123:email, user:123:age
# Use: HSET user:123 name "John" email "john@example.com" age 30

# Use short key names in production
# user:123:profile -> u:123:p

# Set memory policies
# maxmemory 2gb
# maxmemory-policy allkeys-lru
```

---

## Quick Reference

### Common Commands

```bash
# Strings
SET key value EX 3600      # Set with expiry
GET key
INCR counter
INCRBY counter 5

# Hashes
HSET user:1 name "John" age 30
HGET user:1 name
HGETALL user:1

# Lists
LPUSH queue task1
RPOP queue
LRANGE queue 0 -1

# Sets
SADD tags:post:1 redis caching
SMEMBERS tags:post:1
SINTER tags:post:1 tags:post:2

# Sorted Sets
ZADD leaderboard 100 user1
ZREVRANGE leaderboard 0 9 WITHSCORES
ZRANK leaderboard user1
```

---

## Related Skills

- `caching-strategies` - General caching patterns
- `message-queues` - Queue comparison
- `distributed-systems` - Distributed patterns

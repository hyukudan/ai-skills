---
name: redis-patterns
description: |
  Decision frameworks for Redis. When to use which data structure,
  caching strategies, and common patterns for queues and real-time features.
version: 2.0.0
tags: [redis, caching, queues, pubsub, rate-limiting]
category: databases/redis
variables:
  use_case:
    type: string
    description: Primary use case
    enum: [caching, queues, realtime, rate-limiting]
    default: caching
scope:
  triggers:
    - Redis
    - caching
    - rate limiting
    - message queue
    - pub/sub
    - leaderboard
---

# Redis Patterns

You help choose the right Redis approach for the use case.

## When to Use Redis

```
REDIS DECISION:

Need persistence + fast access?
├── Data can be lost on restart? → Redis (in-memory)
├── Need durability? → Redis with AOF or PostgreSQL
└── Complex queries? → Not Redis, use database

Data access pattern?
├── Key-value lookups → Redis String/Hash
├── Ordered by score → Redis Sorted Set
├── FIFO processing → Redis List
├── Set operations → Redis Set
└── Time-series/logs → Redis Stream
```

| Need | Use Redis | Don't Use Redis |
|------|-----------|-----------------|
| Session storage | ✓ Fast, TTL built-in | Complex session data needing queries |
| Caching | ✓ Primary use case | Need consistency guarantees |
| Rate limiting | ✓ Atomic counters | N/A |
| Leaderboards | ✓ Sorted sets perfect | Complex ranking logic |
| Job queues | ✓ Lists/Streams | Need complex routing (use RabbitMQ) |
| Pub/Sub | ✓ Simple messaging | Need persistence (use Kafka) |

---

## Data Structure Selection

```
STRUCTURE DECISION:

Single value per key?
├── Yes → String (also for JSON blobs)
└── No ↓

Multiple fields per key?
├── Object-like data → Hash
└── No ↓

Ordered collection?
├── By insertion order → List
├── By score/rank → Sorted Set
└── No order needed → Set

Need message history?
├── Yes → Stream
└── No → Pub/Sub
```

| Data Structure | Best For | Avoid When |
|----------------|----------|------------|
| String | Cache values, counters, locks | Large objects (>1MB) |
| Hash | User profiles, settings | Need partial expiry on fields |
| List | Queues, recent items | Random access needed |
| Set | Tags, unique visitors | Need ordering |
| Sorted Set | Leaderboards, time-based data | Don't need ranking |
| Stream | Event sourcing, logs | Simple pub/sub is enough |

---

{% if use_case == "caching" %}
## Caching Patterns

### Pattern Selection

```
CACHE PATTERN DECISION:

Reads >> Writes?
├── Cache-aside (lazy loading)
└── No ↓

Data changes frequently?
├── Write-through (sync) or Write-behind (async)
└── No ↓

Can serve stale data briefly?
├── Yes → Stale-while-revalidate
└── No → Short TTL + invalidation
```

| Pattern | When | Trade-off |
|---------|------|-----------|
| Cache-aside | Read-heavy, can tolerate miss | First request slow |
| Write-through | Need consistency | Write latency |
| Write-behind | High write volume | Complexity, possible data loss |
| Stale-while-revalidate | UX-critical, staleness OK | May serve stale data |

### Cache-Aside Implementation

```python
def get_with_cache(key: str, fetch_fn, ttl: int = 3600):
    cached = r.get(key)
    if cached:
        return json.loads(cached)

    data = fetch_fn()
    if data:
        r.setex(key, ttl, json.dumps(data))
    return data

def invalidate(key: str):
    r.delete(key)
```

### Cache Invalidation Strategy

```
INVALIDATION DECISION:

Data update frequency?
├── Rare → Invalidate on write
├── Frequent → Short TTL, no explicit invalidation
└── Very frequent → Don't cache

Update patterns?
├── Single key → DELETE key
├── Pattern-based → SCAN + DELETE (slow!)
└── All related → Use cache tags/namespaces
```

{% elif use_case == "queues" %}
## Queue Patterns

### Queue Type Selection

```
QUEUE DECISION:

Need delivery guarantee?
├── At-least-once → Reliable queue with ack
├── At-most-once → Simple BRPOP
└── Exactly-once → Not Redis (use Kafka/RabbitMQ)

Multiple consumers?
├── Each gets same message → Pub/Sub or Stream
├── Each gets different message → List (competing consumers)
└── Consumer groups → Stream with XREADGROUP
```

| Pattern | Use Case | Redis Structure |
|---------|----------|-----------------|
| Simple queue | Fire-and-forget tasks | List (LPUSH/BRPOP) |
| Reliable queue | Must process each task | List + processing list |
| Fan-out | Broadcast to all | Pub/Sub |
| Consumer groups | Parallel processing | Stream + XREADGROUP |

### Reliable Queue with Acknowledgment

```python
# Dequeue atomically moves to processing list
result = r.brpoplpush("queue:tasks", "queue:processing", timeout=30)

# On success, remove from processing
r.lrem("queue:processing", 1, result)

# On failure/timeout, items remain in processing for retry
```

### Pub/Sub vs Streams

| Feature | Pub/Sub | Stream |
|---------|---------|--------|
| Message persistence | No | Yes |
| Consumer groups | No | Yes |
| Replay messages | No | Yes |
| Backpressure | No | Yes |

**Use Pub/Sub for:** Real-time notifications, chat
**Use Streams for:** Task queues, event sourcing, logs

{% elif use_case == "realtime" %}
## Real-Time Patterns

### Leaderboard with Sorted Sets

```python
# Add/update score (atomic)
r.zadd("leaderboard:weekly", {user_id: score})

# Increment score
r.zincrby("leaderboard:weekly", delta, user_id)

# Get rank (0-indexed)
rank = r.zrevrank("leaderboard:weekly", user_id)

# Get top 10
top = r.zrevrange("leaderboard:weekly", 0, 9, withscores=True)

# Get users around a player
r.zrevrange("leaderboard:weekly", rank - 5, rank + 5, withscores=True)
```

### Session Storage

```
SESSION PATTERN DECISION:

Session data structure?
├── Simple key-value → String (JSON blob)
├── Need partial updates → Hash (HSET/HGET)
└── Need field expiry → Separate keys (more complex)

TTL strategy?
├── Fixed TTL → EXPIRE on create
├── Sliding TTL → EXPIRE on each access
└── Explicit logout → DELETE
```

```python
# Hash-based session (partial updates)
r.hset(f"session:{sid}", mapping={"user_id": uid, "role": "admin"})
r.expire(f"session:{sid}", 3600)

# Extend on access
r.expire(f"session:{sid}", 3600)
```

### Distributed Locking

```
LOCK DECISION:

Coordination type?
├── Prevent concurrent access → SET NX with TTL
├── Need fairness → Redlock (complex)
└── High contention → Consider different approach

Lock duration?
├── Known max time → SET with EX
├── Unknown duration → SET + periodic renewal
└── Very short → May not need Redis
```

**Critical:** Always use Lua script for release to prevent race conditions:

```python
# Atomic release only if we own the lock
lua = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
end
return 0
"""
```

{% elif use_case == "rate-limiting" %}
## Rate Limiting Patterns

### Algorithm Selection

```
RATE LIMIT DECISION:

Traffic pattern?
├── Bursty → Token bucket (allows bursts up to limit)
├── Steady → Fixed window (simpler)
└── Precise → Sliding window (most accurate)

Implementation complexity tolerance?
├── Low → Fixed window counter
├── Medium → Sliding window with sorted set
└── High → Token bucket with Lua
```

| Algorithm | Pros | Cons |
|-----------|------|------|
| Fixed window | Simple, O(1) | Burst at window edge |
| Sliding window | Accurate | More memory (stores timestamps) |
| Token bucket | Handles bursts well | Most complex |

### Sliding Window (Recommended)

```python
def is_rate_limited(user_id: str, limit: int, window_sec: int) -> bool:
    key = f"ratelimit:{user_id}"
    now = time.time()

    pipe = r.pipeline()
    pipe.zremrangebyscore(key, 0, now - window_sec)  # Remove old
    pipe.zcard(key)  # Count current
    pipe.zadd(key, {str(now): now})  # Add this request
    pipe.expire(key, window_sec)
    _, count, _, _ = pipe.execute()

    return count >= limit
```

### Token Bucket (for API rate limiting)

Best when you want to allow bursts but maintain average rate.

```python
# Lua script for atomicity
lua = """
local tokens = tonumber(redis.call('hget', KEYS[1], 'tokens') or ARGV[2])
local last = tonumber(redis.call('hget', KEYS[1], 'ts') or ARGV[3])
local rate, capacity, now = tonumber(ARGV[1]), tonumber(ARGV[2]), tonumber(ARGV[3])

tokens = math.min(capacity, tokens + (now - last) * rate)
if tokens >= 1 then
    redis.call('hmset', KEYS[1], 'tokens', tokens - 1, 'ts', now)
    redis.call('expire', KEYS[1], 60)
    return 1
end
return 0
"""
```

{% endif %}

---

## Performance Patterns

### Pipelining (Always Use)

```python
# BAD: N round trips
for id in ids:
    r.get(f"user:{id}")

# GOOD: 1 round trip
pipe = r.pipeline()
for id in ids:
    pipe.get(f"user:{id}")
results = pipe.execute()
```

### Memory Optimization

| Pattern | Saves Memory | When |
|---------|-------------|------|
| Hash vs multiple strings | ~10x for small objects | <100 fields per hash |
| Short key names | Significant at scale | `u:123` vs `user:123` |
| Integer encoding | Automatic | Values that look like integers |
| Compression | Varies | Large string values |

### Key Naming Convention

```
{object}:{id}:{field}     → user:123:profile
{object}:{id}             → user:123 (hash)
{scope}:{object}:{id}     → cache:user:123
{action}:{scope}:{id}     → lock:payment:456
```

---

## Related Skills

- `caching-strategies` - General caching patterns
- `distributed-systems` - Coordination patterns

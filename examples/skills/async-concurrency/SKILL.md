---
name: async-concurrency
description: |
  Decision frameworks for async and concurrency. When to use async vs threading
  vs multiprocessing, and how to avoid common pitfalls.
license: MIT
allowed-tools: Read Edit Bash
version: 2.0.0
tags: [async, concurrency, threading, parallelism, performance]
category: development/patterns
variables:
  language:
    type: string
    description: Programming language
    enum: [python, javascript]
    default: python
  workload:
    type: string
    description: Type of workload
    enum: [io-bound, cpu-bound, mixed]
    default: io-bound
scope:
  triggers:
    - async
    - concurrent
    - parallel
    - threading
    - race condition
---

# Async & Concurrency

You help choose the right concurrency approach and avoid common pitfalls.

## Concurrency Decision Framework

```
WHAT TYPE OF WORK?

I/O-bound (network, disk, database):
├── Python → asyncio (preferred) or threading
├── JavaScript → async/await (native)
└── Many concurrent connections → async always

CPU-bound (computation, data processing):
├── Python → multiprocessing (bypasses GIL)
├── JavaScript → Worker threads
└── Single heavy task → dedicated process/worker

Mixed workload:
├── Async for I/O + process pool for CPU
└── Don't block event loop with CPU work
```

| Workload | Python | JavaScript |
|----------|--------|------------|
| API calls | `asyncio` + `aiohttp` | `async/await` + `fetch` |
| File I/O | `asyncio` or `ThreadPoolExecutor` | `fs/promises` |
| Database queries | Async driver (asyncpg, motor) | Async driver |
| Data processing | `multiprocessing` | `Worker` threads |
| Image/video | `ProcessPoolExecutor` | `Worker` or WASM |

---

{% if language == "python" %}
## Python Concurrency Selection

```
PYTHON DECISION TREE:

Need to wait for external resources?
├── Yes → asyncio (async/await)
└── No ↓

Need true parallelism for CPU work?
├── Yes → multiprocessing
└── No ↓

Calling blocking library that can't be async?
├── Yes → threading (or run_in_executor)
└── No → Single-threaded is fine
```

{% if workload == "io-bound" %}
### I/O-Bound: asyncio

**When to use:** HTTP clients, database queries, file I/O, websockets

**Key patterns:**

```python
# Concurrent requests (don't await one by one)
results = await asyncio.gather(*[fetch(url) for url in urls])

# Rate limiting with semaphore
semaphore = asyncio.Semaphore(10)
async with semaphore:
    result = await fetch(url)

# Timeout on external calls (always!)
result = await asyncio.wait_for(fetch(url), timeout=30.0)

# Handle partial failures
results = await asyncio.gather(*tasks, return_exceptions=True)
successes = [r for r in results if not isinstance(r, Exception)]
```

{% elif workload == "cpu-bound" %}
### CPU-Bound: multiprocessing

**When to use:** Data processing, image manipulation, ML inference, compression

**Key patterns:**

```python
from concurrent.futures import ProcessPoolExecutor

# Process pool for CPU work
def process_item(item):
    return heavy_computation(item)

with ProcessPoolExecutor() as executor:
    results = list(executor.map(process_item, items))

# Combine with async (don't block event loop)
async def async_cpu_work(data):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(process_pool, cpu_func, data)
```

{% elif workload == "mixed" %}
### Mixed: Async + Process Pool

**When to use:** Web server that does both I/O and computation

```python
# Async for I/O, executor for CPU
async def handle_request(data):
    # I/O - async
    external_data = await fetch_from_api(data['url'])

    # CPU - offload to process pool
    loop = asyncio.get_event_loop()
    processed = await loop.run_in_executor(
        process_pool,
        heavy_computation,
        external_data
    )

    return processed
```

{% endif %}

### Python Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| `time.sleep()` in async | Blocks event loop | `await asyncio.sleep()` |
| `requests.get()` in async | Blocking I/O | Use `aiohttp` |
| Fire-and-forget tasks | Task may be GC'd | Store in set, await later |
| Global mutable state with threads | Race conditions | Use locks or queues |
| Sharing objects between processes | Pickle overhead | Use shared memory or queues |

{% elif language == "javascript" %}
## JavaScript Concurrency Selection

```
JAVASCRIPT DECISION TREE:

Waiting for network/disk?
├── Yes → async/await (native)
└── No ↓

CPU-intensive computation?
├── Yes → Worker threads (Node) or Web Workers (browser)
└── No → Synchronous is fine

Blocking the event loop?
├── Yes → Move to Worker
└── No → Keep in main thread
```

{% if workload == "io-bound" %}
### I/O-Bound: async/await

**Key patterns:**

```typescript
// Concurrent requests
const results = await Promise.all(urls.map(url => fetch(url)));

// Handle partial failures
const results = await Promise.allSettled(urls.map(url => fetch(url)));
const successes = results.filter(r => r.status === 'fulfilled');

// Rate limiting (batch processing)
async function batchProcess<T, R>(
  items: T[],
  fn: (item: T) => Promise<R>,
  concurrency: number
): Promise<R[]> {
  const results: R[] = [];
  for (let i = 0; i < items.length; i += concurrency) {
    const batch = items.slice(i, i + concurrency);
    results.push(...await Promise.all(batch.map(fn)));
  }
  return results;
}
```

{% elif workload == "cpu-bound" %}
### CPU-Bound: Workers

**Node.js Worker Threads:**

```typescript
import { Worker, isMainThread, parentPort, workerData } from 'worker_threads';

// In worker file
if (!isMainThread) {
  const result = heavyComputation(workerData);
  parentPort?.postMessage(result);
}

// In main thread
function runInWorker(data: unknown): Promise<unknown> {
  return new Promise((resolve, reject) => {
    const worker = new Worker('./worker.js', { workerData: data });
    worker.on('message', resolve);
    worker.on('error', reject);
  });
}
```

{% endif %}

### JavaScript Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| Sync loops with await inside | Sequential, not parallel | `Promise.all()` outside loop |
| Unhandled promise rejections | Silent failures | Always catch or use `allSettled` |
| Long computation in main thread | Blocks UI/event loop | Move to Worker |
| Missing `AbortController` | Can't cancel requests | Add abort signal |

{% endif %}

---

## Race Condition Prevention

```
RACE CONDITION SCENARIOS:

Read-modify-write:
  Thread A reads 0, Thread B reads 0
  Both write 1, expected 2
  Fix: Lock/mutex around operation

Check-then-act:
  if (file.exists()) → file may be deleted before next line
  Fix: Atomic operation or lock

Publish before ready:
  Object shared before fully initialized
  Fix: Immutable objects or initialization locks
```

**Prevention strategies by language:**

{% if language == "python" %}
| Strategy | Use Case | Code |
|----------|----------|------|
| `asyncio.Lock` | Async shared state | `async with lock:` |
| `threading.Lock` | Thread shared state | `with lock:` |
| `Queue` | Thread-safe communication | `queue.put()`, `queue.get()` |
| Immutable data | Avoid mutation | `@dataclass(frozen=True)` |
{% else %}
| Strategy | Use Case | Code |
|----------|----------|------|
| Message passing | Workers | `postMessage()` / `onmessage` |
| `Atomics` | SharedArrayBuffer | `Atomics.add(view, 0, 1)` |
| Single-threaded | Main thread | JS is already single-threaded |
| Mutex class | Async critical sections | Custom lock implementation |
{% endif %}

---

## Common Patterns

### Backpressure (Don't overwhelm downstream)

```
BACKPRESSURE DECISION:

Producer faster than consumer?
├── Bounded queue (block producer when full)
├── Drop oldest/newest items
└── Rate limit producer

Memory growing unbounded?
├── Set queue maxsize
└── Process in batches
```

{% if language == "python" %}
```python
queue = asyncio.Queue(maxsize=100)  # Blocks when full
```
{% else %}
```typescript
// Process in controlled batches, not all at once
for (let i = 0; i < items.length; i += BATCH_SIZE) {
  await processBatch(items.slice(i, i + BATCH_SIZE));
}
```
{% endif %}

### Graceful Shutdown

```
SHUTDOWN SEQUENCE:

1. Stop accepting new work
2. Wait for in-flight work (with timeout)
3. Cancel remaining tasks
4. Clean up resources
```

{% if language == "python" %}
```python
async def shutdown(tasks: set[asyncio.Task], timeout: float = 30):
    for task in tasks:
        task.cancel()
    await asyncio.wait(tasks, timeout=timeout)
```
{% else %}
```typescript
// AbortController for cancellation
const controller = new AbortController();
fetch(url, { signal: controller.signal });
// On shutdown:
controller.abort();
```
{% endif %}

---

## Debugging Concurrency Issues

| Symptom | Likely Cause | Debug Approach |
|---------|--------------|----------------|
| Hangs indefinitely | Deadlock or await on never-resolving promise | Add timeouts, log task states |
| Inconsistent results | Race condition | Add locks, review shared state |
| Memory growth | Unbounded queues or fire-and-forget tasks | Track task count, set queue limits |
| Slow despite async | Blocking call in event loop | Profile, check for sync I/O |

{% if language == "python" %}
```python
# Enable debug mode
asyncio.get_event_loop().set_debug(True)
# Shows: slow callbacks, unawaited coroutines, etc.
```
{% endif %}

---

## Related Skills

- `error-handling` - Exception handling in concurrent code
- `performance-optimization` - Profiling async code

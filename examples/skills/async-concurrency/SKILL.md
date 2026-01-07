---
name: async-concurrency
description: |
  Asynchronous programming and concurrency patterns for Python and JavaScript.
  Use when implementing async operations, handling race conditions, managing
  thread safety, or optimizing I/O-bound workloads.
version: 1.0.0
tags: [async, concurrency, threading, parallelism, performance]
category: development/patterns
triggers:
  - async
  - await
  - concurrent
  - parallel
  - threading
  - race condition
  - deadlock
  - mutex
  - semaphore
  - event loop
variables:
  language:
    type: string
    description: Programming language
    enum: [python, javascript, typescript]
    default: python
  pattern:
    type: string
    description: Concurrency pattern to focus on
    enum: [async-await, threading, multiprocessing, workers]
    default: async-await
---

# Async & Concurrency Patterns

## Core Concepts

**Concurrency** = dealing with multiple things at once (structure)
**Parallelism** = doing multiple things at once (execution)

```
Concurrency:    ─A─┬─B─┬─A─┬─B─┬─A─  (interleaved)
Parallelism:    ─A─A─A─A─A─              (simultaneous)
                ─B─B─B─B─B─
```

---

{% if language == "python" %}
## Python Async/Await

### Basic Pattern

```python
import asyncio

async def fetch_data(url: str) -> dict:
    """Non-blocking I/O operation."""
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

async def main():
    # Run multiple requests concurrently
    urls = ["https://api.example.com/1", "https://api.example.com/2"]
    results = await asyncio.gather(*[fetch_data(url) for url in urls])
    return results

# Entry point
asyncio.run(main())
```

### Concurrency Primitives

```python
import asyncio

# Semaphore - limit concurrent operations
semaphore = asyncio.Semaphore(10)

async def rate_limited_fetch(url: str):
    async with semaphore:  # Max 10 concurrent
        return await fetch_data(url)

# Lock - mutual exclusion
lock = asyncio.Lock()
counter = 0

async def increment():
    global counter
    async with lock:
        temp = counter
        await asyncio.sleep(0.001)  # Simulate work
        counter = temp + 1

# Event - signal between tasks
event = asyncio.Event()

async def waiter():
    await event.wait()
    print("Event triggered!")

async def setter():
    await asyncio.sleep(1)
    event.set()
```

### Task Management

```python
import asyncio
from asyncio import Task

async def with_timeout(coro, timeout: float):
    """Run coroutine with timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        return None

async def with_cancellation():
    """Properly handle task cancellation."""
    task = asyncio.create_task(long_running())
    try:
        await asyncio.sleep(1)
        task.cancel()
        await task
    except asyncio.CancelledError:
        print("Task was cancelled")

async def gather_with_errors(*coros):
    """Gather results, capturing errors."""
    results = await asyncio.gather(*coros, return_exceptions=True)
    successes = [r for r in results if not isinstance(r, Exception)]
    failures = [r for r in results if isinstance(r, Exception)]
    return successes, failures
```

### Common Anti-Patterns

```python
# BAD: Blocking the event loop
async def bad_example():
    time.sleep(1)  # Blocks everything!
    requests.get(url)  # Blocking I/O!

# GOOD: Use async alternatives
async def good_example():
    await asyncio.sleep(1)  # Non-blocking
    async with aiohttp.ClientSession() as session:
        await session.get(url)  # Non-blocking

# BAD: Creating tasks without awaiting
async def fire_and_forget():
    asyncio.create_task(some_work())  # Task might be garbage collected!

# GOOD: Track all tasks
async def tracked_tasks():
    tasks = [asyncio.create_task(some_work()) for _ in range(10)]
    await asyncio.gather(*tasks)
```

{% if pattern == "threading" %}
### Threading (CPU-bound with GIL release)

```python
import threading
from concurrent.futures import ThreadPoolExecutor

# Thread-safe counter
class Counter:
    def __init__(self):
        self._value = 0
        self._lock = threading.Lock()

    def increment(self):
        with self._lock:
            self._value += 1

    @property
    def value(self):
        with self._lock:
            return self._value

# Thread pool for I/O operations
def fetch_all(urls: list[str]) -> list[dict]:
    with ThreadPoolExecutor(max_workers=10) as executor:
        return list(executor.map(fetch_sync, urls))

# Combining async and threads
async def run_in_thread(func, *args):
    """Run blocking function in thread pool."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, func, *args)
```

{% elif pattern == "multiprocessing" %}
### Multiprocessing (True Parallelism)

```python
from multiprocessing import Pool, Queue, Process
from concurrent.futures import ProcessPoolExecutor

# Process pool for CPU-bound work
def cpu_intensive(data):
    return sum(x * x for x in data)

def parallel_compute(datasets: list):
    with ProcessPoolExecutor() as executor:
        return list(executor.map(cpu_intensive, datasets))

# Shared state between processes
from multiprocessing import Manager

def with_shared_state():
    manager = Manager()
    shared_dict = manager.dict()
    shared_list = manager.list()

    def worker(d, l, item):
        d[item] = item * 2
        l.append(item)

    processes = [
        Process(target=worker, args=(shared_dict, shared_list, i))
        for i in range(10)
    ]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
```

{% endif %}

{% elif language == "javascript" or language == "typescript" %}
## JavaScript/TypeScript Async

### Basic Pattern

```typescript
async function fetchData(url: string): Promise<any> {
  const response = await fetch(url);
  return response.json();
}

// Concurrent requests
async function fetchAll(urls: string[]): Promise<any[]> {
  return Promise.all(urls.map(url => fetchData(url)));
}

// With error handling
async function fetchAllSafe(urls: string[]): Promise<PromiseSettledResult<any>[]> {
  return Promise.allSettled(urls.map(url => fetchData(url)));
}
```

### Concurrency Control

```typescript
// Semaphore implementation
class Semaphore {
  private permits: number;
  private waiting: (() => void)[] = [];

  constructor(permits: number) {
    this.permits = permits;
  }

  async acquire(): Promise<void> {
    if (this.permits > 0) {
      this.permits--;
      return;
    }
    await new Promise<void>(resolve => this.waiting.push(resolve));
  }

  release(): void {
    const next = this.waiting.shift();
    if (next) {
      next();
    } else {
      this.permits++;
    }
  }
}

// Usage
const semaphore = new Semaphore(5);

async function rateLimitedFetch(url: string): Promise<any> {
  await semaphore.acquire();
  try {
    return await fetchData(url);
  } finally {
    semaphore.release();
  }
}
```

### Batch Processing

```typescript
async function processBatch<T, R>(
  items: T[],
  processor: (item: T) => Promise<R>,
  batchSize: number = 10
): Promise<R[]> {
  const results: R[] = [];

  for (let i = 0; i < items.length; i += batchSize) {
    const batch = items.slice(i, i + batchSize);
    const batchResults = await Promise.all(batch.map(processor));
    results.push(...batchResults);
  }

  return results;
}
```

### Web Workers (True Parallelism)

```typescript
// worker.ts
self.onmessage = (e: MessageEvent) => {
  const result = heavyComputation(e.data);
  self.postMessage(result);
};

// main.ts
function runInWorker<T, R>(data: T): Promise<R> {
  return new Promise((resolve, reject) => {
    const worker = new Worker('./worker.ts');
    worker.onmessage = (e) => {
      resolve(e.data);
      worker.terminate();
    };
    worker.onerror = reject;
    worker.postMessage(data);
  });
}
```

{% endif %}

---

## Race Condition Prevention

### The Problem

```
Thread A:  read(x=0) ──────────────── write(x=1)
Thread B:       read(x=0) ── write(x=1)
Result: x=1 (expected x=2)
```

### Solutions

{% if language == "python" %}
```python
# 1. Use locks
lock = threading.Lock()
with lock:
    shared_value += 1

# 2. Use thread-safe data structures
from queue import Queue
from collections import deque
import threading

# 3. Use atomic operations
import threading
counter = threading.local()

# 4. Use immutable data
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class State:
    value: int

# Instead of mutating, create new
new_state = replace(old_state, value=new_value)
```
{% else %}
```typescript
// 1. Use atomic operations (SharedArrayBuffer)
const buffer = new SharedArrayBuffer(4);
const view = new Int32Array(buffer);
Atomics.add(view, 0, 1);

// 2. Use message passing (no shared state)
worker.postMessage({ type: 'INCREMENT' });

// 3. Use mutex pattern
class Mutex {
  private locked = false;
  private waiting: (() => void)[] = [];

  async lock(): Promise<() => void> {
    while (this.locked) {
      await new Promise<void>(r => this.waiting.push(r));
    }
    this.locked = true;
    return () => this.unlock();
  }

  private unlock(): void {
    this.locked = false;
    this.waiting.shift()?.();
  }
}
```
{% endif %}

---

## Common Patterns

### Producer-Consumer

{% if language == "python" %}
```python
import asyncio

async def producer(queue: asyncio.Queue):
    for i in range(10):
        await queue.put(i)
        await asyncio.sleep(0.1)
    await queue.put(None)  # Signal completion

async def consumer(queue: asyncio.Queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f"Processing {item}")
        queue.task_done()

async def main():
    queue = asyncio.Queue(maxsize=5)  # Backpressure
    await asyncio.gather(
        producer(queue),
        consumer(queue)
    )
```
{% else %}
```typescript
class AsyncQueue<T> {
  private queue: T[] = [];
  private waiting: ((value: T) => void)[] = [];

  async enqueue(item: T): Promise<void> {
    const waiter = this.waiting.shift();
    if (waiter) {
      waiter(item);
    } else {
      this.queue.push(item);
    }
  }

  async dequeue(): Promise<T> {
    if (this.queue.length > 0) {
      return this.queue.shift()!;
    }
    return new Promise(resolve => this.waiting.push(resolve));
  }
}
```
{% endif %}

### Debounce & Throttle

{% if language == "python" %}
```python
import asyncio
from functools import wraps

def debounce(wait: float):
    """Execute only after `wait` seconds of no calls."""
    def decorator(func):
        task = None
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal task
            if task:
                task.cancel()
            async def delayed():
                await asyncio.sleep(wait)
                await func(*args, **kwargs)
            task = asyncio.create_task(delayed())
        return wrapper
    return decorator

def throttle(rate: float):
    """Execute at most once per `rate` seconds."""
    def decorator(func):
        last_call = 0
        @wraps(func)
        async def wrapper(*args, **kwargs):
            nonlocal last_call
            now = asyncio.get_event_loop().time()
            if now - last_call >= rate:
                last_call = now
                return await func(*args, **kwargs)
        return wrapper
    return decorator
```
{% else %}
```typescript
function debounce<T extends (...args: any[]) => any>(
  func: T,
  wait: number
): (...args: Parameters<T>) => void {
  let timeout: NodeJS.Timeout;
  return (...args) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
}

function throttle<T extends (...args: any[]) => any>(
  func: T,
  limit: number
): (...args: Parameters<T>) => void {
  let inThrottle: boolean;
  return (...args) => {
    if (!inThrottle) {
      func(...args);
      inThrottle = true;
      setTimeout(() => (inThrottle = false), limit);
    }
  };
}
```
{% endif %}

---

## Debugging Tips

1. **Enable async tracing**
   {% if language == "python" %}
   ```python
   import asyncio
   asyncio.get_event_loop().set_debug(True)
   ```
   {% else %}
   ```typescript
   // Use --async-stack-traces flag
   node --async-stack-traces app.js
   ```
   {% endif %}

2. **Log task lifecycle**
3. **Use structured concurrency** (cancel child tasks when parent fails)
4. **Set timeouts on all external calls**
5. **Monitor event loop lag**

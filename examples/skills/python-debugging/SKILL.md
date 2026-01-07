---
name: python-debugging
description: |
  Comprehensive guide for debugging Python applications. Use when encountering
  bugs, errors, exceptions, or unexpected behavior in Python code. Covers
  systematic debugging approaches, common pitfalls, and advanced techniques.
version: 1.0.0
tags: [python, debugging, troubleshooting, errors]
category: development/debugging
trigger_phrases:
  - "debug python"
  - "python error"
  - "traceback"
  - "memory leak python"
  - "python exception"
  - "AttributeError"
  - "TypeError python"
  - "pdb debugger"
  - "python crash"
  - "fix python bug"
variables:
  framework:
    type: string
    description: The framework being used (if any)
    enum: [none, django, flask, fastapi, asyncio]
    default: none
  error_type:
    type: string
    description: Type of error being debugged
    enum: [exception, logic, performance, memory, concurrency]
    default: exception
---

# Python Debugging Guide

## Debugging Philosophy

**Systematic over random**: Never guess. Form hypotheses, test them methodically.

**Isolate before fixing**: Reproduce the bug in the smallest possible context before attempting a fix.

**Understand before patching**: A fix you don't understand is a bug waiting to happen.

---

## Phase 1: Information Gathering

### Read the Error Carefully

```python
# The traceback tells a story - read it bottom to top
Traceback (most recent call last):
  File "app.py", line 45, in process_data    # Where it started
    result = transform(data)
  File "utils.py", line 12, in transform      # The path it took
    return data.split(',')
AttributeError: 'NoneType' object has no attribute 'split'  # What went wrong
```

### Key Questions to Answer

1. **What** exactly is failing? (Error message, unexpected output)
2. **Where** in the code? (File, line, function)
3. **When** does it fail? (Always, sometimes, under specific conditions)
4. **What changed** recently? (New code, dependencies, data)

---

## Phase 2: Reproduction

### Create a Minimal Reproducer

```python
# Bad: "It fails somewhere in my 10,000 line app"
# Good: "This 10-line script reproduces the issue"

def minimal_reproducer():
    """Smallest code that shows the bug."""
    data = get_problematic_input()  # Exact input that causes failure
    result = failing_function(data)  # Isolated function call
    print(f"Expected: X, Got: {result}")
```

### Document the Environment

```bash
python --version
pip freeze | grep relevant-package
echo $RELEVANT_ENV_VAR
```

---

## Phase 3: Investigation Techniques

{% if error_type == "exception" %}
### Exception Debugging

```python
import traceback

try:
    risky_operation()
except Exception as e:
    # Full traceback with local variables
    traceback.print_exc()

    # Inspect the exception
    print(f"Type: {type(e).__name__}")
    print(f"Args: {e.args}")

    # For chained exceptions
    print(f"Cause: {e.__cause__}")
    print(f"Context: {e.__context__}")
```

**Common Exception Patterns:**

| Exception | Usual Cause | First Check |
|-----------|-------------|-------------|
| `AttributeError` | None value, typo | Print the object type |
| `KeyError` | Missing dict key | Print available keys |
| `TypeError` | Wrong argument type | Check function signature |
| `ImportError` | Missing/wrong package | Verify installation |

{% elif error_type == "logic" %}
### Logic Error Debugging

When code runs but produces wrong results:

```python
def debug_logic(func):
    """Decorator to trace function calls."""
    def wrapper(*args, **kwargs):
        print(f"CALL: {func.__name__}")
        print(f"  args: {args}")
        print(f"  kwargs: {kwargs}")
        result = func(*args, **kwargs)
        print(f"  return: {result}")
        return result
    return wrapper

# Apply to suspect functions
@debug_logic
def calculate_total(items):
    return sum(item.price for item in items)
```

**Assertion-Driven Debugging:**

```python
def process_order(order):
    assert order is not None, "Order cannot be None"
    assert len(order.items) > 0, "Order must have items"

    total = calculate_total(order.items)
    assert total > 0, f"Total should be positive, got {total}"

    discount = apply_discount(total, order.coupon)
    assert discount <= total, f"Discount {discount} exceeds total {total}"

    return total - discount
```

{% elif error_type == "performance" %}
### Performance Debugging

```python
import cProfile
import pstats
from io import StringIO

# Profile the slow code
profiler = cProfile.Profile()
profiler.enable()

slow_function()  # Your slow code here

profiler.disable()

# Analyze results
stream = StringIO()
stats = pstats.Stats(profiler, stream=stream)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 functions
print(stream.getvalue())
```

**Quick Timing:**

```python
import time
from contextlib import contextmanager

@contextmanager
def timer(name):
    start = time.perf_counter()
    yield
    elapsed = time.perf_counter() - start
    print(f"{name}: {elapsed:.4f}s")

with timer("database query"):
    results = db.query(complex_query)
```

{% elif error_type == "memory" %}
### Memory Debugging

```python
import tracemalloc
import gc

# Start tracing
tracemalloc.start()

# Your memory-intensive code
process_large_data()

# Get memory snapshot
snapshot = tracemalloc.take_snapshot()
top_stats = snapshot.statistics('lineno')

print("Top 10 memory allocations:")
for stat in top_stats[:10]:
    print(stat)

# Check for reference cycles
gc.collect()
print(f"Uncollectable objects: {gc.garbage}")
```

{% elif error_type == "concurrency" %}
### Concurrency Debugging

```python
import threading
import logging

# Enable thread debugging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(threadName)s] %(message)s'
)

# Trace lock acquisition
class DebugLock:
    def __init__(self, name):
        self.name = name
        self.lock = threading.Lock()

    def acquire(self):
        logging.debug(f"Acquiring {self.name}")
        self.lock.acquire()
        logging.debug(f"Acquired {self.name}")

    def release(self):
        logging.debug(f"Releasing {self.name}")
        self.lock.release()
```

{% endif %}

---

{% if framework == "django" %}
## Django-Specific Debugging

```python
# settings.py - Enable debug toolbar
INSTALLED_APPS += ['debug_toolbar']
MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']

# Log all SQL queries
LOGGING = {
    'version': 1,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        }
    }
}
```

```bash
# Django shell with enhanced debugging
python manage.py shell_plus --print-sql
```

{% elif framework == "fastapi" %}
## FastAPI-Specific Debugging

```python
from fastapi import FastAPI, Request
import logging

app = FastAPI(debug=True)

# Log all requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logging.info(f"{request.method} {request.url}")
    logging.info(f"Headers: {dict(request.headers)}")

    body = await request.body()
    if body:
        logging.info(f"Body: {body.decode()}")

    response = await call_next(request)
    logging.info(f"Status: {response.status_code}")
    return response
```

{% elif framework == "asyncio" %}
## Asyncio-Specific Debugging

```python
import asyncio

# Enable debug mode
asyncio.get_event_loop().set_debug(True)

# Trace coroutine execution
import sys

def trace_coroutines(frame, event, arg):
    if event == 'call' and asyncio.iscoroutinefunction(frame.f_code):
        print(f"CORO: {frame.f_code.co_name}")
    return trace_coroutines

sys.settrace(trace_coroutines)
```

{% endif %}

---

## Phase 4: Common Pitfalls

### Mutable Default Arguments

```python
# BUG: List is shared between calls
def append_to(item, target=[]):
    target.append(item)
    return target

# FIX: Use None as default
def append_to(item, target=None):
    if target is None:
        target = []
    target.append(item)
    return target
```

### Late Binding in Closures

```python
# BUG: All functions return 4
functions = [lambda: i for i in range(5)]

# FIX: Capture value at creation time
functions = [lambda i=i: i for i in range(5)]
```

### Silent Failures

```python
# BUG: Exception swallowed silently
try:
    risky_operation()
except:
    pass  # Never do this!

# FIX: At minimum, log the error
try:
    risky_operation()
except Exception as e:
    logger.exception("Operation failed")
    raise  # Or handle appropriately
```

---

## Debugging Tools Reference

| Tool | Use Case | Command |
|------|----------|---------|
| `pdb` | Interactive debugging | `python -m pdb script.py` |
| `ipdb` | Enhanced pdb with IPython | `import ipdb; ipdb.set_trace()` |
| `pudb` | Visual TUI debugger | `python -m pudb script.py` |
| `py-spy` | Sampling profiler | `py-spy top --pid PID` |
| `memory_profiler` | Line-by-line memory | `@profile` decorator |

---

## When to Ask for Help

After you've:
1. Read the full error message and traceback
2. Created a minimal reproducer
3. Searched for the error message online
4. Checked recent changes (git diff)
5. Reviewed relevant documentation

Include in your question:
- Exact error message
- Minimal code to reproduce
- Python version and relevant packages
- What you've already tried

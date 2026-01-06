---
name: error-handling
description: |
  Error handling strategies and exception management patterns. Use when implementing
  error handling, designing logging systems, or building resilient applications.
  Covers exception hierarchies, recovery strategies, and observability.
version: 1.0.0
tags: [error-handling, exceptions, logging, resilience, observability]
category: development/quality
variables:
  language:
    type: string
    description: Programming language
    enum: [python, javascript, typescript, go, java]
    default: python
  app_type:
    type: string
    description: Application type
    enum: [web-api, cli, library, worker]
    default: web-api
---

# Error Handling Guide

## Philosophy

**Errors are data, not surprises.** A well-designed system anticipates failures and handles them gracefully.

### Core Principles

1. **Fail fast** - Detect errors early, before they propagate
2. **Fail loud** - Log errors with enough context to debug
3. **Fail gracefully** - Provide useful feedback to users
4. **Fail safely** - Never expose sensitive information

> "The only truly reliable systems are those designed to fail gracefully."

---

## Error Categories

```
┌─────────────────────────────────────────────────────────────┐
│                    ERROR TAXONOMY                           │
├─────────────────────────────────────────────────────────────┤
│ RECOVERABLE                    │ UNRECOVERABLE              │
│ ─────────────                  │ ─────────────              │
│ • Validation errors            │ • Programming bugs          │
│ • Network timeouts             │ • Out of memory            │
│ • Rate limiting                │ • Disk full                │
│ • Resource not found           │ • Configuration missing    │
│                                │                            │
│ → Retry, fallback, user action │ → Log, alert, crash safely │
└─────────────────────────────────────────────────────────────┘
```

---

## Exception Design

{% if language == "python" %}
### Custom Exception Hierarchy

```python
class AppError(Exception):
    """Base exception for application errors."""

    def __init__(self, message: str, code: str = "UNKNOWN_ERROR", details: dict = None):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}

    def to_dict(self) -> dict:
        return {
            "error": {
                "code": self.code,
                "message": self.message,
                "details": self.details,
            }
        }


# Domain-specific errors
class ValidationError(AppError):
    """Invalid input data."""

    def __init__(self, message: str, field: str = None, **kwargs):
        super().__init__(message, code="VALIDATION_ERROR", **kwargs)
        if field:
            self.details["field"] = field


class NotFoundError(AppError):
    """Resource not found."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            f"{resource} with id '{identifier}' not found",
            code="NOT_FOUND",
            details={"resource": resource, "id": identifier}
        )


class AuthenticationError(AppError):
    """Authentication failed."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(message, code="AUTH_REQUIRED")


class AuthorizationError(AppError):
    """Authorization denied."""

    def __init__(self, action: str, resource: str):
        super().__init__(
            f"Not authorized to {action} {resource}",
            code="FORBIDDEN",
            details={"action": action, "resource": resource}
        )


class RateLimitError(AppError):
    """Rate limit exceeded."""

    def __init__(self, retry_after: int):
        super().__init__(
            "Rate limit exceeded",
            code="RATE_LIMITED",
            details={"retry_after": retry_after}
        )
```

### Using Custom Exceptions

```python
# Raising with context
def get_user(user_id: str) -> User:
    user = db.users.find_one({"id": user_id})
    if not user:
        raise NotFoundError("User", user_id)
    return User(**user)

def update_user(user_id: str, data: dict, requester: User):
    user = get_user(user_id)

    if requester.id != user.id and not requester.is_admin:
        raise AuthorizationError("update", "user")

    if "email" in data and not is_valid_email(data["email"]):
        raise ValidationError("Invalid email format", field="email")

    # ... update logic
```

{% elif language == "javascript" or language == "typescript" %}
### Custom Error Classes

```typescript
export class AppError extends Error {
  constructor(
    message: string,
    public code: string = 'UNKNOWN_ERROR',
    public statusCode: number = 500,
    public details: Record<string, unknown> = {}
  ) {
    super(message);
    this.name = 'AppError';
    Error.captureStackTrace(this, this.constructor);
  }

  toJSON() {
    return {
      error: {
        code: this.code,
        message: this.message,
        details: this.details,
      },
    };
  }
}

export class ValidationError extends AppError {
  constructor(message: string, field?: string) {
    super(message, 'VALIDATION_ERROR', 422, field ? { field } : {});
    this.name = 'ValidationError';
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string, id: string) {
    super(`${resource} with id '${id}' not found`, 'NOT_FOUND', 404, { resource, id });
    this.name = 'NotFoundError';
  }
}

export class AuthError extends AppError {
  constructor(message = 'Authentication required') {
    super(message, 'AUTH_REQUIRED', 401);
    this.name = 'AuthError';
  }
}
```

{% elif language == "go" %}
### Go Error Patterns

```go
package errors

import (
    "fmt"
)

// Sentinel errors for comparison
var (
    ErrNotFound      = fmt.Errorf("resource not found")
    ErrUnauthorized  = fmt.Errorf("unauthorized")
    ErrValidation    = fmt.Errorf("validation failed")
)

// Custom error type with context
type AppError struct {
    Code    string
    Message string
    Err     error  // Wrapped error
    Details map[string]interface{}
}

func (e *AppError) Error() string {
    if e.Err != nil {
        return fmt.Sprintf("%s: %v", e.Message, e.Err)
    }
    return e.Message
}

func (e *AppError) Unwrap() error {
    return e.Err
}

// Constructor functions
func NewNotFoundError(resource, id string) *AppError {
    return &AppError{
        Code:    "NOT_FOUND",
        Message: fmt.Sprintf("%s with id '%s' not found", resource, id),
        Err:     ErrNotFound,
        Details: map[string]interface{}{"resource": resource, "id": id},
    }
}

// Usage
func GetUser(id string) (*User, error) {
    user, err := db.FindUser(id)
    if err != nil {
        if errors.Is(err, sql.ErrNoRows) {
            return nil, NewNotFoundError("User", id)
        }
        return nil, fmt.Errorf("database error: %w", err)
    }
    return user, nil
}
```

{% endif %}

---

{% if app_type == "web-api" %}
## API Error Responses

### Consistent Error Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "field": "email",
      "reason": "Must be a valid email address"
    }
  },
  "request_id": "req_abc123"
}
```

### HTTP Status Code Mapping

```python
ERROR_STATUS_CODES = {
    "VALIDATION_ERROR": 422,
    "NOT_FOUND": 404,
    "AUTH_REQUIRED": 401,
    "FORBIDDEN": 403,
    "RATE_LIMITED": 429,
    "CONFLICT": 409,
    "INTERNAL_ERROR": 500,
}
```

{% if language == "python" %}
### FastAPI Error Handler

```python
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()

@app.exception_handler(AppError)
async def app_error_handler(request: Request, exc: AppError):
    return JSONResponse(
        status_code=ERROR_STATUS_CODES.get(exc.code, 500),
        content={
            "error": exc.to_dict()["error"],
            "request_id": request.state.request_id,
        }
    )

@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    # Log the full error for debugging
    logger.exception(
        "Unhandled exception",
        request_id=request.state.request_id,
        path=request.url.path,
    )

    # Return safe response to client
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
            },
            "request_id": request.state.request_id,
        }
    )
```
{% elif language == "javascript" or language == "typescript" %}
### Express Error Middleware

```typescript
import { Request, Response, NextFunction } from 'express';

export function errorHandler(
  err: Error,
  req: Request,
  res: Response,
  next: NextFunction
) {
  // Log full error
  logger.error('Request error', {
    error: err,
    requestId: req.id,
    path: req.path,
    method: req.method,
  });

  // Handle known errors
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      error: err.toJSON().error,
      requestId: req.id,
    });
  }

  // Handle unknown errors safely
  res.status(500).json({
    error: {
      code: 'INTERNAL_ERROR',
      message: 'An unexpected error occurred',
    },
    requestId: req.id,
  });
}

// Usage
app.use(errorHandler);
```
{% endif %}

{% endif %}

---

## Logging Best Practices

### Structured Logging

{% if language == "python" %}
```python
import structlog

logger = structlog.get_logger()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

# Usage
logger.info(
    "User created",
    user_id=user.id,
    email=user.email,
    source="registration"
)

# Error logging with context
try:
    process_order(order)
except Exception as e:
    logger.exception(
        "Order processing failed",
        order_id=order.id,
        customer_id=order.customer_id,
        error_type=type(e).__name__
    )
    raise
```

**Output:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info",
  "event": "User created",
  "user_id": "usr_123",
  "email": "user@example.com",
  "source": "registration"
}
```
{% elif language == "javascript" or language == "typescript" %}
```typescript
import pino from 'pino';

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => ({ level: label }),
  },
});

// Usage
logger.info({ userId: user.id, email: user.email }, 'User created');

// Error logging
try {
  await processOrder(order);
} catch (error) {
  logger.error(
    {
      orderId: order.id,
      customerId: order.customerId,
      error: error instanceof Error ? error.message : 'Unknown error',
      stack: error instanceof Error ? error.stack : undefined,
    },
    'Order processing failed'
  );
  throw error;
}
```
{% endif %}

### What to Log

```
✅ DO LOG:
- User actions (login, logout, permissions changes)
- Business events (order placed, payment processed)
- Errors with full context
- Performance metrics (slow queries, timeouts)
- Security events (failed auth, suspicious activity)

❌ DON'T LOG:
- Passwords (even hashed)
- Full credit card numbers
- Personal data (PII) unless required
- Session tokens or API keys
- High-frequency events without sampling
```

### Log Levels

```
DEBUG   → Developer information, verbose
INFO    → Business events, normal operations
WARNING → Unexpected but handled situations
ERROR   → Errors that need attention
FATAL   → System cannot continue
```

---

## Resilience Patterns

### Retry with Backoff

{% if language == "python" %}
```python
import asyncio
from functools import wraps
import random

def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential: bool = True,
    retryable_exceptions: tuple = (Exception,)
):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except retryable_exceptions as e:
                    last_exception = e

                    if attempt == max_attempts - 1:
                        raise

                    # Calculate delay with jitter
                    if exponential:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                    else:
                        delay = base_delay

                    delay *= (0.5 + random.random())  # Add jitter

                    logger.warning(
                        "Retry attempt",
                        attempt=attempt + 1,
                        max_attempts=max_attempts,
                        delay=delay,
                        error=str(e)
                    )

                    await asyncio.sleep(delay)

            raise last_exception

        return wrapper
    return decorator

# Usage
@retry(max_attempts=3, base_delay=1.0, retryable_exceptions=(ConnectionError, TimeoutError))
async def fetch_data(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
```
{% endif %}

### Circuit Breaker

```python
from enum import Enum
from datetime import datetime, timedelta

class CircuitState(Enum):
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: timedelta = timedelta(seconds=30)
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time = None

    async def call(self, func, *args, **kwargs):
        if self.state == CircuitState.OPEN:
            if datetime.now() - self.last_failure_time > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
            else:
                raise CircuitOpenError("Circuit is open")

        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failures = 0
        self.state = CircuitState.CLOSED

    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = datetime.now()

        if self.failures >= self.failure_threshold:
            self.state = CircuitState.OPEN
```

---

## Anti-Patterns

### Swallowing Exceptions

```python
# BAD: Silent failure
try:
    process_payment(order)
except Exception:
    pass  # What happened? Nobody knows!

# GOOD: Handle or re-raise
try:
    process_payment(order)
except PaymentError as e:
    logger.error("Payment failed", order_id=order.id, error=str(e))
    raise  # Or handle appropriately
```

### Generic Catch-All

```python
# BAD: Catching everything
try:
    result = do_something()
except Exception as e:
    return {"error": str(e)}  # Hides the real problem

# GOOD: Catch specific exceptions
try:
    result = do_something()
except ValidationError as e:
    return {"error": e.message, "field": e.field}
except NotFoundError as e:
    return {"error": "Resource not found"}
except Exception as e:
    logger.exception("Unexpected error")
    raise  # Let it propagate
```

### Exception as Control Flow

```python
# BAD: Using exceptions for normal flow
def find_user(email):
    try:
        return db.users.find_one(email=email)
    except:
        return None

# GOOD: Explicit return for expected cases
def find_user(email) -> User | None:
    return db.users.find_one(email=email)  # Returns None if not found
```

---

## Checklist

### Error Handling
- [ ] Custom exceptions for domain errors
- [ ] Consistent error response format
- [ ] Proper HTTP status codes
- [ ] No sensitive data in error messages

### Logging
- [ ] Structured logging (JSON)
- [ ] Request IDs for tracing
- [ ] Appropriate log levels
- [ ] No sensitive data in logs

### Resilience
- [ ] Retry for transient failures
- [ ] Timeouts on external calls
- [ ] Circuit breakers for dependencies
- [ ] Graceful degradation

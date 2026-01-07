---
name: logging-observability
description: |
  Comprehensive guide for application logging, metrics, and distributed tracing.
  Use when implementing observability, debugging production issues, or setting up
  monitoring. Covers structured logging, metrics collection, tracing, and alerting.
version: 1.0.0
tags: [logging, observability, metrics, tracing, monitoring, debugging]
category: devops/observability
trigger_phrases:
  - "add logging"
  - "structured logging"
  - "prometheus metrics"
  - "distributed tracing"
  - "opentelemetry"
  - "grafana"
  - "monitoring"
  - "observability"
  - "log levels"
  - "alerting"
variables:
  language:
    type: string
    description: Primary programming language
    enum: [python, javascript, typescript, go, java]
    default: python
  environment:
    type: string
    description: Deployment environment type
    enum: [local, cloud, kubernetes]
    default: cloud
  stack:
    type: string
    description: Observability stack
    enum: [basic, elk, datadog, grafana, aws]
    default: grafana
---

# Logging & Observability Guide

## The Three Pillars of Observability

```
┌─────────────────────────────────────────────────────────────┐
│                    OBSERVABILITY                             │
├───────────────────┬───────────────────┬─────────────────────┤
│      LOGS         │     METRICS       │      TRACES         │
│                   │                   │                     │
│  What happened    │  How much/many    │  Request flow       │
│  Discrete events  │  Aggregated data  │  Distributed path   │
│  Debug details    │  Trends/alerts    │  Latency breakdown  │
└───────────────────┴───────────────────┴─────────────────────┘
```

> "You can't fix what you can't see. Observability turns invisible failures into actionable insights."

---

## Structured Logging

### Why Structured Logs?

```
# BAD - Unstructured (hard to parse/search)
2024-01-15 10:23:45 INFO User john@example.com logged in from 192.168.1.1

# GOOD - Structured (machine-readable, searchable)
{
  "timestamp": "2024-01-15T10:23:45.123Z",
  "level": "info",
  "message": "User logged in",
  "user_email": "john@example.com",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0...",
  "request_id": "req_abc123",
  "duration_ms": 145
}
```

{% if language == "python" %}
### Python Structured Logging

```python
import structlog
import logging

# Configure structlog
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()  # JSON output
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

# Create logger
logger = structlog.get_logger()

# Usage with context
logger.info(
    "user_login",
    user_id="user_123",
    ip_address=request.client.host,
    user_agent=request.headers.get("user-agent"),
)

# Bind context for request lifecycle
log = logger.bind(request_id=request_id, user_id=current_user.id)
log.info("processing_order", order_id=order.id)
log.info("order_completed", total=order.total)
```

### Logging Configuration

```python
# logging_config.py
import os

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(timestamp)s %(level)s %(name)s %(message)s"
        },
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json" if os.getenv("ENV") == "production" else "standard",
            "stream": "ext://sys.stdout"
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": "app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5
        }
    },
    "root": {
        "level": os.getenv("LOG_LEVEL", "INFO"),
        "handlers": ["console", "file"]
    },
    "loggers": {
        "uvicorn": {"level": "WARNING"},
        "sqlalchemy": {"level": "WARNING"},
    }
}
```

{% elif language == "javascript" or language == "typescript" %}
### Node.js Structured Logging

```typescript
import pino from 'pino';

// Configure logger
const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  formatters: {
    level: (label) => ({ level: label }),
    bindings: (bindings) => ({
      pid: bindings.pid,
      host: bindings.hostname,
      service: 'my-service',
    }),
  },
  timestamp: pino.stdTimeFunctions.isoTime,
  // Pretty print in development
  transport: process.env.NODE_ENV !== 'production'
    ? { target: 'pino-pretty' }
    : undefined,
});

// Create child logger with context
const requestLogger = logger.child({
  requestId: req.id,
  userId: req.user?.id,
});

// Usage
requestLogger.info({ orderId: order.id }, 'Processing order');
requestLogger.info({ total: order.total, items: order.items.length }, 'Order completed');

// Error logging
requestLogger.error({ err, orderId: order.id }, 'Order processing failed');
```

### Express Middleware

```typescript
import { v4 as uuidv4 } from 'uuid';

// Request logging middleware
app.use((req, res, next) => {
  req.id = req.headers['x-request-id'] || uuidv4();
  req.log = logger.child({ requestId: req.id });

  const start = Date.now();

  res.on('finish', () => {
    req.log.info({
      method: req.method,
      url: req.url,
      statusCode: res.statusCode,
      duration: Date.now() - start,
      userAgent: req.headers['user-agent'],
    }, 'Request completed');
  });

  next();
});
```

{% elif language == "go" %}
### Go Structured Logging

```go
package main

import (
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

func NewLogger(env string) (*zap.Logger, error) {
    var config zap.Config

    if env == "production" {
        config = zap.NewProductionConfig()
        config.EncoderConfig.TimeKey = "timestamp"
        config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder
    } else {
        config = zap.NewDevelopmentConfig()
        config.EncoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder
    }

    return config.Build()
}

func main() {
    logger, _ := NewLogger(os.Getenv("ENV"))
    defer logger.Sync()

    // Structured logging
    logger.Info("user_login",
        zap.String("user_id", userID),
        zap.String("ip", ipAddress),
        zap.Duration("duration", elapsed),
    )

    // With context
    requestLogger := logger.With(
        zap.String("request_id", requestID),
        zap.String("user_id", userID),
    )
    requestLogger.Info("processing_order", zap.String("order_id", orderID))
}
```

{% endif %}

---

## Log Levels Strategy

### When to Use Each Level

| Level | When to Use | Example |
|-------|-------------|---------|
| **TRACE** | Detailed debugging, method entry/exit | `Entering processOrder with params...` |
| **DEBUG** | Development debugging info | `Cache miss for key user_123` |
| **INFO** | Normal operations, milestones | `Order #456 completed successfully` |
| **WARN** | Recoverable issues, deprecations | `Rate limit approaching: 80% used` |
| **ERROR** | Failures requiring attention | `Payment failed: insufficient funds` |
| **FATAL** | Unrecoverable, app shutting down | `Database connection lost, shutting down` |

### Level Guidelines

```
Production: INFO and above (no DEBUG/TRACE)
Staging: DEBUG and above
Development: All levels

# Environment-based configuration
LOG_LEVEL=info  # Production
LOG_LEVEL=debug # Staging/Dev
```

---

## What to Log

### Always Log

```python
# Authentication events
logger.info("auth_success", user_id=user.id, method="oauth2")
logger.warn("auth_failure", email=email, reason="invalid_password", attempts=3)

# Business transactions
logger.info("order_created", order_id=order.id, total=order.total, items=len(order.items))
logger.info("payment_processed", order_id=order.id, amount=amount, provider="stripe")

# External service calls
logger.info("external_api_call", service="payment", method="charge", duration_ms=145)
logger.error("external_api_error", service="payment", error=str(e), retries=3)

# Background jobs
logger.info("job_started", job_id=job.id, type="email_send")
logger.info("job_completed", job_id=job.id, duration_ms=2340)
```

### Never Log

```python
# NEVER log these:
# - Passwords (even hashed)
# - API keys / secrets
# - Credit card numbers
# - Social security numbers
# - Full session tokens
# - PII without masking

# BAD
logger.info("user_created", password=password)  # NEVER!

# GOOD - mask sensitive data
logger.info("payment", card_last_four="4242", amount=99.99)
logger.info("api_call", api_key_prefix=api_key[:8] + "...")
```

---

## Metrics

### Key Metrics Types

```
Counter   - Cumulative, always increases (requests_total, errors_total)
Gauge     - Current value, can go up/down (active_connections, queue_size)
Histogram - Distribution of values (request_duration, response_size)
Summary   - Similar to histogram, with percentiles
```

{% if language == "python" %}
### Prometheus Metrics in Python

```python
from prometheus_client import Counter, Histogram, Gauge, start_http_server

# Define metrics
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total HTTP requests',
    ['method', 'endpoint', 'status']
)

REQUEST_LATENCY = Histogram(
    'http_request_duration_seconds',
    'HTTP request latency',
    ['method', 'endpoint'],
    buckets=[.005, .01, .025, .05, .1, .25, .5, 1, 2.5, 5, 10]
)

ACTIVE_REQUESTS = Gauge(
    'http_requests_active',
    'Active HTTP requests'
)

DB_POOL_SIZE = Gauge(
    'db_pool_connections',
    'Database pool connections',
    ['state']  # idle, active
)

# Usage in middleware
@app.middleware("http")
async def metrics_middleware(request, call_next):
    ACTIVE_REQUESTS.inc()
    start_time = time.time()

    try:
        response = await call_next(request)
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        return response
    finally:
        REQUEST_LATENCY.labels(
            method=request.method,
            endpoint=request.url.path
        ).observe(time.time() - start_time)
        ACTIVE_REQUESTS.dec()

# Start metrics server
start_http_server(8000)  # /metrics endpoint
```

{% elif language == "javascript" or language == "typescript" %}
### Prometheus Metrics in Node.js

```typescript
import client from 'prom-client';

// Create registry
const register = new client.Registry();
client.collectDefaultMetrics({ register });

// Custom metrics
const httpRequestsTotal = new client.Counter({
  name: 'http_requests_total',
  help: 'Total HTTP requests',
  labelNames: ['method', 'route', 'status'],
  registers: [register],
});

const httpRequestDuration = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request latency',
  labelNames: ['method', 'route'],
  buckets: [0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2.5, 5, 10],
  registers: [register],
});

// Middleware
app.use((req, res, next) => {
  const end = httpRequestDuration.startTimer({ method: req.method, route: req.route?.path });

  res.on('finish', () => {
    end();
    httpRequestsTotal.inc({
      method: req.method,
      route: req.route?.path || 'unknown',
      status: res.statusCode,
    });
  });

  next();
});

// Metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.send(await register.metrics());
});
```

{% endif %}

### Essential Metrics Checklist

```
Request Metrics:
- [ ] requests_total (by method, endpoint, status)
- [ ] request_duration_seconds (histogram)
- [ ] request_size_bytes
- [ ] response_size_bytes

Error Metrics:
- [ ] errors_total (by type, endpoint)
- [ ] error_rate (percentage)

Resource Metrics:
- [ ] active_connections
- [ ] db_pool_size (idle, active)
- [ ] memory_usage_bytes
- [ ] cpu_usage_percent

Business Metrics:
- [ ] orders_total
- [ ] revenue_total
- [ ] user_signups_total
- [ ] active_users (gauge)
```

---

## Distributed Tracing

### Trace Propagation

```
Service A          Service B          Service C
    │                  │                  │
    │  trace_id: abc   │                  │
    │  span_id: 001    │                  │
    ├─────────────────►│                  │
    │                  │  trace_id: abc   │
    │                  │  span_id: 002    │
    │                  │  parent_id: 001  │
    │                  ├─────────────────►│
    │                  │                  │  trace_id: abc
    │                  │                  │  span_id: 003
    │                  │                  │  parent_id: 002
    │                  │◄─────────────────┤
    │◄─────────────────┤                  │
```

{% if language == "python" %}
### OpenTelemetry in Python

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor

# Setup tracing
provider = TracerProvider()
processor = BatchSpanProcessor(OTLPSpanExporter(endpoint="http://jaeger:4317"))
provider.add_span_processor(processor)
trace.set_tracer_provider(provider)

tracer = trace.get_tracer(__name__)

# Auto-instrument frameworks
FastAPIInstrumentor.instrument_app(app)
HTTPXClientInstrumentor().instrument()
SQLAlchemyInstrumentor().instrument(engine=engine)

# Manual spans
async def process_order(order_id: str):
    with tracer.start_as_current_span("process_order") as span:
        span.set_attribute("order.id", order_id)

        # Child span
        with tracer.start_as_current_span("validate_order"):
            validate(order)

        # Another child span
        with tracer.start_as_current_span("charge_payment"):
            charge(order)

        span.set_attribute("order.status", "completed")
```

{% elif language == "javascript" or language == "typescript" %}
### OpenTelemetry in Node.js

```typescript
import { NodeSDK } from '@opentelemetry/sdk-node';
import { getNodeAutoInstrumentations } from '@opentelemetry/auto-instrumentations-node';
import { OTLPTraceExporter } from '@opentelemetry/exporter-trace-otlp-http';
import { trace, SpanStatusCode } from '@opentelemetry/api';

// Initialize SDK
const sdk = new NodeSDK({
  traceExporter: new OTLPTraceExporter({
    url: 'http://jaeger:4318/v1/traces',
  }),
  instrumentations: [getNodeAutoInstrumentations()],
});

sdk.start();

// Manual tracing
const tracer = trace.getTracer('my-service');

async function processOrder(orderId: string) {
  return tracer.startActiveSpan('process_order', async (span) => {
    try {
      span.setAttribute('order.id', orderId);

      // Child span
      await tracer.startActiveSpan('validate_order', async (validateSpan) => {
        await validate(order);
        validateSpan.end();
      });

      // Another child span
      await tracer.startActiveSpan('charge_payment', async (paymentSpan) => {
        await charge(order);
        paymentSpan.end();
      });

      span.setStatus({ code: SpanStatusCode.OK });
    } catch (error) {
      span.setStatus({ code: SpanStatusCode.ERROR, message: error.message });
      span.recordException(error);
      throw error;
    } finally {
      span.end();
    }
  });
}
```

{% endif %}

---

{% if stack == "grafana" %}
## Grafana Stack Setup

### Components

```
┌─────────────────────────────────────────────────────────────┐
│                     Grafana Stack                           │
├───────────────┬───────────────┬───────────────┬────────────┤
│    Grafana    │     Loki      │  Prometheus   │   Tempo    │
│  (Dashboard)  │   (Logs)      │  (Metrics)    │  (Traces)  │
└───────┬───────┴───────┬───────┴───────┬───────┴─────┬──────┘
        │               │               │             │
        └───────────────┴───────────────┴─────────────┘
                               ▲
                               │
                    ┌──────────┴──────────┐
                    │   Your Application   │
                    └─────────────────────┘
```

### Docker Compose

```yaml
version: '3.8'
services:
  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true
    volumes:
      - grafana-data:/var/lib/grafana

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml

  loki:
    image: grafana/loki:latest
    ports:
      - "3100:3100"
    command: -config.file=/etc/loki/local-config.yaml

  tempo:
    image: grafana/tempo:latest
    ports:
      - "4317:4317"  # OTLP gRPC
      - "4318:4318"  # OTLP HTTP
    command: [ "-config.file=/etc/tempo.yaml" ]

volumes:
  grafana-data:
```

{% elif stack == "elk" %}
## ELK Stack Setup

### Components

```
Application → Filebeat → Logstash → Elasticsearch → Kibana
                            │
                            ▼
                      (Transform/Enrich)
```

### Docker Compose

```yaml
version: '3.8'
services:
  elasticsearch:
    image: elasticsearch:8.11.0
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
    ports:
      - "9200:9200"

  logstash:
    image: logstash:8.11.0
    volumes:
      - ./logstash.conf:/usr/share/logstash/pipeline/logstash.conf
    ports:
      - "5044:5044"

  kibana:
    image: kibana:8.11.0
    ports:
      - "5601:5601"
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

{% endif %}

---

## Alerting Best Practices

### Alert on Symptoms, Not Causes

```yaml
# BAD - Alerting on cause
- alert: HighCPU
  expr: cpu_usage > 80%
  # CPU can be high without affecting users

# GOOD - Alerting on symptom
- alert: HighLatency
  expr: histogram_quantile(0.99, http_request_duration_seconds) > 2
  for: 5m
  labels:
    severity: warning
  annotations:
    summary: "High request latency"
    description: "99th percentile latency is {{ $value }}s"
```

### Alerting Rules Template

```yaml
groups:
  - name: application
    rules:
      # Error rate alert
      - alert: HighErrorRate
        expr: |
          sum(rate(http_requests_total{status=~"5.."}[5m]))
          / sum(rate(http_requests_total[5m])) > 0.05
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Error rate above 5%"

      # Latency alert
      - alert: HighLatencyP99
        expr: |
          histogram_quantile(0.99,
            sum(rate(http_request_duration_seconds_bucket[5m])) by (le)
          ) > 2
        for: 5m
        labels:
          severity: warning

      # Availability alert
      - alert: ServiceDown
        expr: up == 0
        for: 1m
        labels:
          severity: critical
```

---

## Observability Checklist

### Before Production

```
Logging:
- [ ] Structured JSON logging configured
- [ ] Log levels appropriate for environment
- [ ] Sensitive data redacted
- [ ] Request IDs propagated
- [ ] Logs shipped to central system

Metrics:
- [ ] RED metrics (Rate, Errors, Duration)
- [ ] Resource metrics (CPU, memory, connections)
- [ ] Business metrics defined
- [ ] Dashboards created
- [ ] Alerts configured

Tracing:
- [ ] Trace context propagated across services
- [ ] Key operations have spans
- [ ] Trace sampling configured
- [ ] Trace backend accessible

General:
- [ ] Runbooks for common alerts
- [ ] On-call rotation defined
- [ ] Incident response process documented
```

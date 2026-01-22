---
name: nodejs-development
description: |
  Decision frameworks for Node.js development. When to use streams vs buffers,
  how to structure APIs vs CLIs, and common patterns that need attention.
version: 2.0.0
tags: [nodejs, javascript, backend, api, server]
category: development/nodejs
variables:
  app_type:
    type: string
    description: Type of Node.js application
    enum: [api, cli, worker, library]
    default: api
  runtime:
    type: string
    description: Runtime environment
    enum: [node, bun, deno]
    default: node
scope:
  triggers:
    - Node.js
    - Express
    - Fastify
    - CLI tool
    - backend
---

# Node.js Development

You help make Node.js architecture and pattern decisions.

## When to Use Node.js

```
NODE.JS DECISION:

Workload type?
├── I/O-bound (API calls, DB, files) → Node.js excels
├── CPU-bound (image processing, ML) → Consider workers or other language
└── Real-time (websockets, streaming) → Node.js excels

Team expertise?
├── JavaScript/TypeScript → Node.js natural fit
└── Other languages → Consider their ecosystems
```

| Use Case | Node.js? | Why |
|----------|----------|-----|
| REST API | ✓ | Event loop handles many connections |
| CLI tool | ✓ | Fast startup, good ecosystem |
| Websocket server | ✓ | Built for real-time |
| Image processing | ⚠️ | Use worker threads or Sharp |
| ML inference | ✗ | Use Python or dedicated service |
| Background jobs | ✓ | With proper job queue |

---

{% if app_type == "api" %}
## API Architecture Decisions

### Framework Selection

```
FRAMEWORK DECISION:

Need speed/performance?
├── Maximum → Fastify (~4x Express)
├── Standard → Express (most middleware/tutorials)
└── Full-featured → NestJS (enterprise patterns)

Project complexity?
├── Simple API → Express or Fastify
├── Large team/enterprise → NestJS
└── Microservice → Fastify or tRPC
```

| Framework | Best For | Trade-off |
|-----------|----------|-----------|
| Express | Most projects, learning | Slower, callback-based |
| Fastify | Performance-critical | Less middleware |
| NestJS | Enterprise, large teams | Steep learning curve |
| Hono | Edge, multi-runtime | Newer, smaller ecosystem |

### Project Structure

```
src/
├── routes/          # HTTP layer (thin)
├── services/        # Business logic
├── repositories/    # Data access
├── middleware/      # Auth, validation, logging
└── utils/           # Helpers, errors
```

**Key principle:** Routes should be thin - delegate to services.

### Middleware Order

```
REQUEST FLOW:

1. Security (helmet, cors)
2. Request parsing (json, urlencoded)
3. Logging (request start)
4. Auth (verify token)
5. Validation (check input)
6. Rate limiting
7. Route handler
8. Error handler (catch-all)
```

### Error Handling Pattern

```javascript
// Wrap async handlers (Express doesn't catch async errors)
const asyncHandler = fn => (req, res, next) =>
  Promise.resolve(fn(req, res, next)).catch(next);

// Error middleware (must have 4 params)
app.use((err, req, res, next) => {
  const status = err.statusCode || 500;
  const message = err.isOperational ? err.message : 'Internal error';
  res.status(status).json({ error: { message } });
});
```

{% elif app_type == "cli" %}
## CLI Architecture Decisions

### Framework Selection

```
CLI FRAMEWORK DECISION:

Complexity?
├── Simple (few commands) → Commander.js
├── Complex (subcommands, plugins) → Oclif
└── Interactive-heavy → Inquirer + custom

Distribution?
├── npm package → Standard setup
├── Single binary → pkg or Bun compile
└── Cross-platform installer → Consider Go/Rust
```

| Library | Use For |
|---------|---------|
| Commander | Command parsing, options |
| Inquirer | Interactive prompts |
| Chalk | Colored output |
| Ora | Spinners/progress |
| Conf | Config file storage |

### package.json Setup

```json
{
  "name": "my-cli",
  "type": "module",
  "bin": { "my-cli": "./bin/cli.js" },
  "files": ["bin", "dist"]
}
```

**bin/cli.js:**
```javascript
#!/usr/bin/env node
import '../dist/index.js';
```

{% elif app_type == "worker" %}
## Worker Architecture Decisions

### Job Queue Selection

```
QUEUE DECISION:

Persistence needed?
├── Yes → BullMQ (Redis) or pg-boss (Postgres)
└── No → In-memory queue

Existing infrastructure?
├── Have Redis → BullMQ
├── Have Postgres only → pg-boss
└── Need distributed → RabbitMQ or SQS
```

| Queue | Backed By | Best For |
|-------|-----------|----------|
| BullMQ | Redis | Most Node.js apps |
| pg-boss | Postgres | No Redis available |
| Agenda | MongoDB | Already using Mongo |
| SQS | AWS | AWS infrastructure |

### Worker Pattern

```javascript
// Graceful shutdown is critical for workers
const shutdown = async () => {
  await worker.close();  // Stop accepting jobs
  await worker.drain();  // Finish current jobs
  process.exit(0);
};
process.on('SIGTERM', shutdown);
```

{% elif app_type == "library" %}
## Library Architecture Decisions

### Module Format

```
MODULE FORMAT DECISION:

Target Node.js only?
├── ESM preferred (type: "module")
└── Support older Node → Dual CJS/ESM

Target browsers too?
├── Bundle with Rollup/tsup
└── Provide ESM + types
```

**package.json for dual format:**
```json
{
  "type": "module",
  "main": "./dist/index.cjs",
  "module": "./dist/index.js",
  "types": "./dist/index.d.ts",
  "exports": {
    ".": {
      "import": "./dist/index.js",
      "require": "./dist/index.cjs",
      "types": "./dist/index.d.ts"
    }
  }
}
```

{% endif %}

---

## Streams vs Buffers

```
STREAM DECISION:

Data size?
├── Small (<10MB) → Buffer (simpler)
├── Large/unknown → Stream (memory-safe)
└── Very large files → Stream required

Processing type?
├── Need all data at once → Buffer
├── Can process chunks → Stream
└── Transform pipeline → Stream
```

**Use streams for:**
- Large file processing
- HTTP responses with unknown size
- Real-time data processing
- Memory-constrained environments

**Use buffers for:**
- Small files
- Need random access
- Simpler code when size is known

---

## Async Patterns

### Concurrency Control

```
CONCURRENCY DECISION:

Processing many items?
├── Independent items → Promise.all() with limit
├── Must preserve order → for...of with await
└── Rate limited API → Use p-limit or semaphore

External service calls?
├── Has rate limit → Implement backoff + limit
├── No limit → Parallel with reasonable cap (10-50)
└── Unreliable → Add retry with exponential backoff
```

```javascript
// Limit concurrent operations
import pLimit from 'p-limit';
const limit = pLimit(10);
const results = await Promise.all(
  items.map(item => limit(() => process(item)))
);
```

### Event Loop Blocking

| Operation | Blocks? | Solution |
|-----------|---------|----------|
| `fs.readFileSync` | Yes | Use `fs.promises.readFile` |
| `JSON.parse(hugeString)` | Yes | Stream parse with `stream-json` |
| Crypto operations | Yes | Use `crypto` async methods |
| Heavy computation | Yes | Worker threads |
| `while(true)` | Yes | Don't do this |

---

## Common Anti-Patterns

| Anti-Pattern | Problem | Fix |
|--------------|---------|-----|
| `await` in loop | Sequential, slow | `Promise.all()` outside loop |
| Unhandled rejections | Silent failures | Global handler + logging |
| Blocking event loop | Server unresponsive | Async or worker threads |
| No request timeout | Hanging connections | Set timeout on requests |
| Sync file operations | Blocks all requests | Use async fs methods |
| No graceful shutdown | Data loss, broken connections | Handle SIGTERM/SIGINT |

---

## Essential Patterns

### Graceful Shutdown

```javascript
const shutdown = async (signal) => {
  server.close();                    // Stop new connections
  await Promise.all(connections.map(c => c.end()));  // Close existing
  await db.close();                  // Close DB pool
  process.exit(0);
};
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));
```

### Config Validation at Startup

```javascript
// Fail fast if config is invalid
const config = ConfigSchema.parse({
  port: process.env.PORT,
  dbUrl: process.env.DATABASE_URL,
});
// App won't start with missing/invalid config
```

### Health Check Endpoint

```javascript
app.get('/health', async (req, res) => {
  const dbOk = await db.raw('SELECT 1').then(() => true).catch(() => false);
  const status = dbOk ? 200 : 503;
  res.status(status).json({ status: dbOk ? 'ok' : 'degraded', db: dbOk });
});
```

---

## Checklist by App Type

{% if app_type == "api" %}
### API Checklist
- [ ] Async error handler wraps all routes
- [ ] Request validation (Zod, Joi)
- [ ] Rate limiting on public endpoints
- [ ] Health check endpoint
- [ ] Graceful shutdown
- [ ] Structured logging
- [ ] CORS configured
- [ ] Security headers (Helmet)
{% elif app_type == "cli" %}
### CLI Checklist
- [ ] Shebang in entry file
- [ ] `bin` field in package.json
- [ ] `--help` and `--version` flags
- [ ] Exit codes (0 success, 1 error)
- [ ] Colored output for TTY only
- [ ] Config file support (~/.config)
{% elif app_type == "worker" %}
### Worker Checklist
- [ ] Graceful shutdown (finish current job)
- [ ] Job retry with backoff
- [ ] Dead letter queue for failed jobs
- [ ] Health check (job queue connection)
- [ ] Concurrency limit
- [ ] Job timeout
{% elif app_type == "library" %}
### Library Checklist
- [ ] Dual CJS/ESM if needed
- [ ] TypeScript types included
- [ ] Minimal dependencies
- [ ] Peer dependencies declared
- [ ] README with examples
- [ ] Changelog maintained
{% endif %}

---

## Related Skills

- `async-concurrency` - Deep dive on async patterns
- `error-handling` - Comprehensive error strategies

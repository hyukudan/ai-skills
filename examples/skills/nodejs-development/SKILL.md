---
name: nodejs-development
description: |
  Node.js development patterns, best practices, and common solutions.
  Use when building Node.js applications, APIs, CLIs, or backend services.
  Covers async patterns, streams, modules, error handling, and deployment.
version: 1.0.0
tags: [nodejs, javascript, backend, api, server, async]
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
---

# Node.js Development Best Practices

## Philosophy

**Node.js excels at I/O-bound operations.** Use the event loop wisely, never block it.

```
Node.js Architecture:
┌─────────────────────────────────────────┐
│           Your JavaScript Code          │
└────────────────┬────────────────────────┘
                 │
          ┌──────▼──────┐
          │  Event Loop │ (Single-threaded)
          └──────┬──────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼───┐   ┌───▼────┐   ┌──▼──────┐
│Timers │   │ I/O    │   │ Workers │
│       │   │Polling │   │ (CPU)   │
└───────┘   └────────┘   └─────────┘
```

---

## Project Structure

{% if app_type == 'api' %}
### API Project Structure

```
my-api/
├── src/
│   ├── index.ts           # Entry point
│   ├── server.ts          # Server setup
│   ├── config/
│   │   ├── index.ts       # Configuration loader
│   │   └── database.ts    # DB configuration
│   ├── routes/
│   │   ├── index.ts       # Route aggregator
│   │   ├── users.ts       # /users routes
│   │   └── products.ts    # /products routes
│   ├── controllers/
│   │   ├── users.ts       # Request handlers
│   │   └── products.ts
│   ├── services/
│   │   ├── users.ts       # Business logic
│   │   └── products.ts
│   ├── models/
│   │   ├── user.ts        # Data models
│   │   └── product.ts
│   ├── middleware/
│   │   ├── auth.ts        # Authentication
│   │   ├── validate.ts    # Request validation
│   │   └── errorHandler.ts
│   └── utils/
│       ├── logger.ts
│       └── errors.ts
├── tests/
│   ├── unit/
│   └── integration/
├── package.json
├── tsconfig.json
└── .env.example
```
{% endif %}

{% if app_type == 'cli' %}
### CLI Project Structure

```
my-cli/
├── src/
│   ├── index.ts           # Entry point with shebang
│   ├── cli.ts             # Command definitions
│   ├── commands/
│   │   ├── init.ts        # init command
│   │   ├── build.ts       # build command
│   │   └── deploy.ts      # deploy command
│   ├── lib/
│   │   ├── config.ts      # Config file handling
│   │   └── prompts.ts     # Interactive prompts
│   └── utils/
│       ├── logger.ts
│       └── spinner.ts
├── bin/
│   └── my-cli             # Executable script
├── package.json           # bin field configured
└── tsconfig.json
```

```json
// package.json
{
  "name": "my-cli",
  "bin": {
    "my-cli": "./bin/my-cli"
  },
  "type": "module"
}
```
{% endif %}

---

## Async Patterns

### Promise-Based Code

```javascript
// BAD: Callback hell
fs.readFile('file1.txt', (err, data1) => {
  if (err) return handleError(err);
  fs.readFile('file2.txt', (err, data2) => {
    if (err) return handleError(err);
    // More nesting...
  });
});

// GOOD: Async/await
async function readFiles() {
  try {
    const data1 = await fs.promises.readFile('file1.txt', 'utf8');
    const data2 = await fs.promises.readFile('file2.txt', 'utf8');
    return { data1, data2 };
  } catch (error) {
    throw new AppError('Failed to read files', { cause: error });
  }
}

// GOOD: Parallel when independent
async function readFilesParallel() {
  const [data1, data2] = await Promise.all([
    fs.promises.readFile('file1.txt', 'utf8'),
    fs.promises.readFile('file2.txt', 'utf8'),
  ]);
  return { data1, data2 };
}
```

### Error Handling in Async Code

```javascript
// Always handle promise rejections
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection:', reason);
  // Log to error tracking service
  process.exit(1);
});

// Wrap async route handlers
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

// Usage in Express
app.get('/users/:id', asyncHandler(async (req, res) => {
  const user = await userService.findById(req.params.id);
  if (!user) {
    throw new NotFoundError('User not found');
  }
  res.json(user);
}));
```

### Controlling Concurrency

```javascript
// Process items with controlled concurrency
async function processWithLimit(items, limit, processor) {
  const results = [];
  const executing = new Set();

  for (const item of items) {
    const promise = processor(item).then(result => {
      executing.delete(promise);
      return result;
    });

    executing.add(promise);
    results.push(promise);

    if (executing.size >= limit) {
      await Promise.race(executing);
    }
  }

  return Promise.all(results);
}

// Usage
const urls = ['url1', 'url2', 'url3', /* ... 100 more */];
const responses = await processWithLimit(urls, 5, fetch);

// Or use p-limit package
import pLimit from 'p-limit';
const limit = pLimit(5);
const responses = await Promise.all(
  urls.map(url => limit(() => fetch(url)))
);
```

---

## Streams

### Reading Large Files

```javascript
import { createReadStream } from 'fs';
import { createInterface } from 'readline';

// Process large file line by line without loading into memory
async function processLargeFile(filePath) {
  const fileStream = createReadStream(filePath);
  const rl = createInterface({
    input: fileStream,
    crlfDelay: Infinity,
  });

  let lineCount = 0;
  for await (const line of rl) {
    lineCount++;
    // Process each line
    await processLine(line);
  }

  return lineCount;
}
```

### Transform Streams

```javascript
import { Transform, pipeline } from 'stream';
import { promisify } from 'util';
import { createReadStream, createWriteStream } from 'fs';
import { createGzip } from 'zlib';

const pipelineAsync = promisify(pipeline);

// Custom transform stream
class JsonLineTransform extends Transform {
  constructor() {
    super({ objectMode: true });
  }

  _transform(chunk, encoding, callback) {
    try {
      const data = JSON.parse(chunk);
      // Transform the data
      data.processed = true;
      data.timestamp = new Date().toISOString();
      callback(null, JSON.stringify(data) + '\n');
    } catch (error) {
      callback(error);
    }
  }
}

// Pipeline: read -> transform -> gzip -> write
await pipelineAsync(
  createReadStream('input.jsonl'),
  new JsonLineTransform(),
  createGzip(),
  createWriteStream('output.jsonl.gz')
);
```

### Streaming HTTP Response

```javascript
import { Readable } from 'stream';

// Stream large data to HTTP response
app.get('/export', async (req, res) => {
  res.setHeader('Content-Type', 'application/json');
  res.setHeader('Content-Disposition', 'attachment; filename="export.json"');

  const cursor = db.collection('items').find({}).stream();

  res.write('[\n');

  let first = true;
  for await (const doc of cursor) {
    if (!first) res.write(',\n');
    first = false;
    res.write(JSON.stringify(doc));
  }

  res.write('\n]');
  res.end();
});
```

---

## Error Handling

### Custom Error Classes

```javascript
// Base application error
class AppError extends Error {
  constructor(message, options = {}) {
    super(message);
    this.name = this.constructor.name;
    this.statusCode = options.statusCode || 500;
    this.code = options.code || 'INTERNAL_ERROR';
    this.isOperational = options.isOperational ?? true;

    Error.captureStackTrace(this, this.constructor);
  }
}

// Specific error types
class NotFoundError extends AppError {
  constructor(resource = 'Resource') {
    super(`${resource} not found`, {
      statusCode: 404,
      code: 'NOT_FOUND',
    });
  }
}

class ValidationError extends AppError {
  constructor(message, errors = []) {
    super(message, {
      statusCode: 400,
      code: 'VALIDATION_ERROR',
    });
    this.errors = errors;
  }
}

class UnauthorizedError extends AppError {
  constructor(message = 'Authentication required') {
    super(message, {
      statusCode: 401,
      code: 'UNAUTHORIZED',
    });
  }
}
```

### Global Error Handler

```javascript
// Express error middleware
function errorHandler(err, req, res, next) {
  // Log the error
  logger.error({
    message: err.message,
    stack: err.stack,
    code: err.code,
    path: req.path,
    method: req.method,
  });

  // Operational errors: send error response
  if (err.isOperational) {
    return res.status(err.statusCode).json({
      error: {
        code: err.code,
        message: err.message,
        ...(err.errors && { details: err.errors }),
      },
    });
  }

  // Programming errors: don't leak details
  res.status(500).json({
    error: {
      code: 'INTERNAL_ERROR',
      message: 'An unexpected error occurred',
    },
  });
}

// Register as last middleware
app.use(errorHandler);
```

---

{% if app_type == 'api' %}
## API Patterns

### Express/Fastify Setup

```javascript
import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import compression from 'compression';
import rateLimit from 'express-rate-limit';

const app = express();

// Security middleware
app.use(helmet());
app.use(cors({ origin: process.env.ALLOWED_ORIGINS?.split(',') }));

// Performance
app.use(compression());

// Rate limiting
app.use(rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per window
  standardHeaders: true,
  legacyHeaders: false,
}));

// Body parsing
app.use(express.json({ limit: '10kb' }));
app.use(express.urlencoded({ extended: true }));

// Request logging
app.use((req, res, next) => {
  const start = Date.now();
  res.on('finish', () => {
    logger.info({
      method: req.method,
      path: req.path,
      status: res.statusCode,
      duration: Date.now() - start,
    });
  });
  next();
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// API routes
app.use('/api/v1', apiRoutes);

// 404 handler
app.use((req, res) => {
  res.status(404).json({ error: { code: 'NOT_FOUND', message: 'Endpoint not found' } });
});

// Error handler
app.use(errorHandler);
```

### Request Validation

```javascript
import { z } from 'zod';

// Define schemas
const CreateUserSchema = z.object({
  email: z.string().email(),
  name: z.string().min(2).max(100),
  password: z.string().min(8),
  role: z.enum(['user', 'admin']).default('user'),
});

const QuerySchema = z.object({
  page: z.coerce.number().positive().default(1),
  limit: z.coerce.number().positive().max(100).default(20),
  sort: z.enum(['asc', 'desc']).default('desc'),
});

// Validation middleware
function validate(schema, source = 'body') {
  return (req, res, next) => {
    const result = schema.safeParse(req[source]);
    if (!result.success) {
      const errors = result.error.errors.map(e => ({
        field: e.path.join('.'),
        message: e.message,
      }));
      throw new ValidationError('Validation failed', errors);
    }
    req.validated = result.data;
    next();
  };
}

// Usage
app.post('/users',
  validate(CreateUserSchema),
  asyncHandler(async (req, res) => {
    const user = await userService.create(req.validated);
    res.status(201).json(user);
  })
);
```
{% endif %}

{% if app_type == 'cli' %}
## CLI Patterns

### Command Structure with Commander

```javascript
#!/usr/bin/env node
import { Command } from 'commander';
import { version } from '../package.json';

const program = new Command();

program
  .name('my-cli')
  .description('My awesome CLI tool')
  .version(version);

program
  .command('init')
  .description('Initialize a new project')
  .option('-t, --template <name>', 'template to use', 'default')
  .option('--skip-install', 'skip dependency installation')
  .action(async (options) => {
    const { init } = await import('./commands/init.js');
    await init(options);
  });

program
  .command('build')
  .description('Build the project')
  .option('-w, --watch', 'watch for changes')
  .option('-o, --output <dir>', 'output directory', 'dist')
  .action(async (options) => {
    const { build } = await import('./commands/build.js');
    await build(options);
  });

program.parse();
```

### Interactive Prompts

```javascript
import { input, select, confirm, password } from '@inquirer/prompts';
import chalk from 'chalk';
import ora from 'ora';

async function init(options) {
  console.log(chalk.bold('\n🚀 Project Setup\n'));

  const projectName = await input({
    message: 'Project name:',
    default: 'my-project',
    validate: (value) => /^[a-z0-9-]+$/.test(value) || 'Use lowercase letters, numbers, and hyphens',
  });

  const template = await select({
    message: 'Select template:',
    choices: [
      { value: 'minimal', name: 'Minimal - Basic setup' },
      { value: 'api', name: 'API - Express + TypeScript' },
      { value: 'fullstack', name: 'Fullstack - Next.js + API' },
    ],
  });

  const installDeps = await confirm({
    message: 'Install dependencies?',
    default: true,
  });

  // Show progress
  const spinner = ora('Creating project...').start();

  try {
    await createProject({ projectName, template });
    spinner.succeed(chalk.green('Project created!'));

    if (installDeps) {
      spinner.start('Installing dependencies...');
      await installDependencies(projectName);
      spinner.succeed(chalk.green('Dependencies installed!'));
    }

    console.log(chalk.bold('\n✅ Done! Next steps:\n'));
    console.log(`  cd ${projectName}`);
    console.log('  npm run dev\n');
  } catch (error) {
    spinner.fail(chalk.red('Failed to create project'));
    console.error(error.message);
    process.exit(1);
  }
}
```
{% endif %}

---

## Configuration Management

```javascript
import { z } from 'zod';

// Define config schema
const ConfigSchema = z.object({
  nodeEnv: z.enum(['development', 'production', 'test']).default('development'),
  port: z.coerce.number().default(3000),
  database: z.object({
    url: z.string().url(),
    pool: z.coerce.number().default(10),
  }),
  redis: z.object({
    url: z.string().url().optional(),
  }).optional(),
  jwt: z.object({
    secret: z.string().min(32),
    expiresIn: z.string().default('7d'),
  }),
  logging: z.object({
    level: z.enum(['debug', 'info', 'warn', 'error']).default('info'),
  }),
});

// Load and validate config
function loadConfig() {
  const result = ConfigSchema.safeParse({
    nodeEnv: process.env.NODE_ENV,
    port: process.env.PORT,
    database: {
      url: process.env.DATABASE_URL,
      pool: process.env.DB_POOL_SIZE,
    },
    redis: {
      url: process.env.REDIS_URL,
    },
    jwt: {
      secret: process.env.JWT_SECRET,
      expiresIn: process.env.JWT_EXPIRES_IN,
    },
    logging: {
      level: process.env.LOG_LEVEL,
    },
  });

  if (!result.success) {
    console.error('Invalid configuration:');
    result.error.errors.forEach(e => {
      console.error(`  ${e.path.join('.')}: ${e.message}`);
    });
    process.exit(1);
  }

  return result.data;
}

export const config = loadConfig();
```

---

## Graceful Shutdown

```javascript
import { createServer } from 'http';

const server = createServer(app);
const connections = new Set();

// Track connections
server.on('connection', (conn) => {
  connections.add(conn);
  conn.on('close', () => connections.delete(conn));
});

// Graceful shutdown handler
async function shutdown(signal) {
  console.log(`\n${signal} received. Starting graceful shutdown...`);

  // Stop accepting new connections
  server.close(() => {
    console.log('HTTP server closed');
  });

  // Close existing connections
  for (const conn of connections) {
    conn.end();
  }

  // Close database connections
  try {
    await db.close();
    console.log('Database connections closed');
  } catch (error) {
    console.error('Error closing database:', error);
  }

  // Close Redis
  if (redis) {
    await redis.quit();
    console.log('Redis connection closed');
  }

  console.log('Graceful shutdown complete');
  process.exit(0);
}

// Register shutdown handlers
process.on('SIGTERM', () => shutdown('SIGTERM'));
process.on('SIGINT', () => shutdown('SIGINT'));

// Start server
const PORT = config.port;
server.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
```

---

## Testing

```javascript
import { describe, it, expect, beforeAll, afterAll, beforeEach } from 'vitest';
import request from 'supertest';
import { app } from '../src/app';
import { db } from '../src/db';

describe('Users API', () => {
  beforeAll(async () => {
    await db.migrate.latest();
  });

  afterAll(async () => {
    await db.destroy();
  });

  beforeEach(async () => {
    await db('users').truncate();
  });

  describe('POST /api/users', () => {
    it('creates a new user', async () => {
      const response = await request(app)
        .post('/api/users')
        .send({
          email: 'test@example.com',
          name: 'Test User',
          password: 'password123',
        })
        .expect(201);

      expect(response.body).toMatchObject({
        email: 'test@example.com',
        name: 'Test User',
      });
      expect(response.body).not.toHaveProperty('password');
    });

    it('returns 400 for invalid email', async () => {
      const response = await request(app)
        .post('/api/users')
        .send({
          email: 'invalid-email',
          name: 'Test User',
          password: 'password123',
        })
        .expect(400);

      expect(response.body.error.code).toBe('VALIDATION_ERROR');
    });
  });
});
```

---

## Node.js Checklist

### Project Setup
- [ ] Use ES modules (`"type": "module"` in package.json)
- [ ] TypeScript with strict mode enabled
- [ ] Environment variables validated at startup
- [ ] Graceful shutdown handlers registered

### Performance
- [ ] Use streams for large data
- [ ] Connection pooling for databases
- [ ] Rate limiting on public endpoints
- [ ] Response compression enabled

### Security
- [ ] Helmet.js for security headers
- [ ] Input validation on all endpoints
- [ ] Parameterized queries (no string concat)
- [ ] Secrets in environment variables, never in code

### Reliability
- [ ] Health check endpoint
- [ ] Structured logging
- [ ] Error tracking integration
- [ ] Graceful shutdown handling

### Code Quality
- [ ] Async error handling (no unhandled rejections)
- [ ] Custom error classes with proper inheritance
- [ ] Integration tests for critical paths
- [ ] Linting and formatting automated

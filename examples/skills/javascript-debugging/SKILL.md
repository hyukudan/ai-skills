---
name: javascript-debugging
description: |
  Comprehensive guide for debugging JavaScript and Node.js applications.
  Use when encountering bugs, errors, exceptions, or unexpected behavior.
  Covers browser DevTools, Node.js debugging, async issues, and memory leaks.
license: MIT
allowed-tools: Read Edit Bash Grep
version: 1.0.0
tags: [javascript, debugging, nodejs, browser, devtools, errors]
category: development/debugging
variables:
  environment:
    type: string
    description: Runtime environment
    enum: [browser, nodejs, both]
    default: both
  framework:
    type: string
    description: Framework in use (if any)
    enum: [vanilla, react, vue, express, nextjs]
    default: vanilla
---

# JavaScript Debugging Guide

## Debugging Philosophy

**Debugging is detective work.** Follow the evidence, form hypotheses, and test them systematically.

```
1. REPRODUCE  → Can you reliably trigger the bug?
2. ISOLATE    → What's the minimal code that causes it?
3. IDENTIFY   → What's the root cause?
4. FIX        → Change only what's necessary
5. VERIFY     → Does the fix work? Any side effects?
```

---

## Quick Debugging Toolkit

### Console Methods (Beyond console.log)

```javascript
// Structured output
console.table([{name: 'Alice', age: 30}, {name: 'Bob', age: 25}]);

// Grouping related logs
console.group('User Authentication');
console.log('Checking credentials...');
console.log('Token valid');
console.groupEnd();

// Timing operations
console.time('fetchData');
await fetchData();
console.timeEnd('fetchData'); // fetchData: 235.5ms

// Stack trace without error
console.trace('How did we get here?');

// Conditional logging
console.assert(user.isAdmin, 'User should be admin', user);

// Counting occurrences
function processItem(item) {
  console.count('processItem called');
}
```

### Debugger Statement

```javascript
function problematicFunction(data) {
  debugger; // Execution pauses here when DevTools is open

  const result = data.map(item => {
    debugger; // Pause on each iteration
    return transform(item);
  });

  return result;
}
```

---

{% if environment in ['browser', 'both'] %}
## Browser DevTools

### Sources Panel Debugging

```javascript
// Set breakpoints in DevTools Sources panel:
// - Click line number for regular breakpoint
// - Right-click for conditional breakpoint
// - Use "Pause on exceptions" button

// Conditional breakpoint example (right-click line number):
// Condition: user.id === 'problem-user-123'
```

### Network Panel Tips

```javascript
// Debug fetch requests
fetch('/api/users')
  .then(response => {
    // Check Network panel for:
    // - Status code
    // - Response headers
    // - Response body
    // - Timing breakdown
    console.log('Response status:', response.status);
    return response.json();
  });
```

### Memory Panel (Finding Leaks)

```javascript
// Common memory leak patterns:

// 1. Forgotten event listeners
element.addEventListener('click', handler);
// Fix: element.removeEventListener('click', handler);

// 2. Detached DOM nodes
let detachedNodes = [];
function leak() {
  const div = document.createElement('div');
  detachedNodes.push(div); // Reference keeps it in memory
}

// 3. Closures holding references
function createHandler() {
  const largeData = new Array(1000000).fill('x');
  return function() {
    // largeData is retained even if unused
    console.log('clicked');
  };
}
```

### Performance Panel

```javascript
// Wrap slow code for profiling
console.profile('Slow Operation');
slowFunction();
console.profileEnd('Slow Operation');

// Or use Performance API
performance.mark('start');
slowFunction();
performance.mark('end');
performance.measure('slowFunction', 'start', 'end');
console.log(performance.getEntriesByName('slowFunction'));
```
{% endif %}

{% if environment in ['nodejs', 'both'] %}
## Node.js Debugging

### Built-in Debugger

```bash
# Start with inspector
node --inspect app.js

# Break on first line
node --inspect-brk app.js

# Then open chrome://inspect in Chrome
```

### VS Code Debugging

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "type": "node",
      "request": "launch",
      "name": "Debug Current File",
      "program": "${file}",
      "skipFiles": ["<node_internals>/**"]
    },
    {
      "type": "node",
      "request": "attach",
      "name": "Attach to Process",
      "port": 9229
    }
  ]
}
```

### Debug Environment Variables

```javascript
// Enable debug output for popular libraries
// DEBUG=express:* node app.js
// DEBUG=http,net node app.js

// Custom debug logging
const debug = require('debug')('myapp:server');
debug('Server starting on port %d', port);
```

### Heap Snapshots

```javascript
// Take heap snapshot programmatically
const v8 = require('v8');
const fs = require('fs');

function takeHeapSnapshot() {
  const snapshotFile = `heap-${Date.now()}.heapsnapshot`;
  const snapshot = v8.writeHeapSnapshot(snapshotFile);
  console.log(`Heap snapshot written to ${snapshot}`);
}

// Trigger with signal
process.on('SIGUSR2', takeHeapSnapshot);
```
{% endif %}

---

## Async Debugging

### Promise Debugging

```javascript
// Always add catch handlers
fetchData()
  .then(process)
  .then(save)
  .catch(error => {
    console.error('Pipeline failed:', error);
    console.error('Stack:', error.stack);
  });

// Async/await with proper error handling
async function loadUser(id) {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    return await response.json();
  } catch (error) {
    console.error(`Failed to load user ${id}:`, error);
    throw error; // Re-throw for caller to handle
  }
}
```

### Async Stack Traces

```javascript
// Enable long stack traces in Node.js
// node --async-stack-traces app.js

// Or use Error.captureStackTrace
class CustomError extends Error {
  constructor(message, cause) {
    super(message);
    this.cause = cause;
    Error.captureStackTrace(this, CustomError);
  }
}
```

### Race Condition Detection

```javascript
// Add logging to identify race conditions
let operationId = 0;

async function fetchWithLogging(url) {
  const id = ++operationId;
  console.log(`[${id}] Starting fetch: ${url}`);

  const result = await fetch(url);
  console.log(`[${id}] Completed fetch: ${url}`);

  return result;
}
```

---

## Common Error Patterns

### TypeError: Cannot read property 'x' of undefined

```javascript
// Problem
const user = getUser();
console.log(user.name); // TypeError if user is undefined

// Solution 1: Optional chaining
console.log(user?.name);

// Solution 2: Nullish coalescing
const name = user?.name ?? 'Anonymous';

// Solution 3: Guard clause
if (!user) {
  console.error('User not found');
  return;
}
console.log(user.name);
```

### ReferenceError: x is not defined

```javascript
// Problem: Variable scope
function outer() {
  if (true) {
    let innerVar = 'hello';
  }
  console.log(innerVar); // ReferenceError
}

// Solution: Declare in correct scope
function outer() {
  let innerVar;
  if (true) {
    innerVar = 'hello';
  }
  console.log(innerVar);
}
```

### Unhandled Promise Rejection

```javascript
// Catch unhandled rejections globally
process.on('unhandledRejection', (reason, promise) => {
  console.error('Unhandled Rejection at:', promise, 'reason:', reason);
  // Application specific logging, throwing an error, or other logic here
});

// In browser
window.addEventListener('unhandledrejection', event => {
  console.error('Unhandled rejection:', event.reason);
});
```

---

{% if framework == 'react' %}
## React-Specific Debugging

### React DevTools

```javascript
// Install React DevTools browser extension
// Use Components tab to inspect:
// - Component hierarchy
// - Props and state
// - Hooks values

// Use Profiler tab to find:
// - Unnecessary re-renders
// - Slow components
```

### Debug Re-renders

```javascript
// Why did this render?
import { useEffect, useRef } from 'react';

function useWhyDidYouUpdate(name, props) {
  const previousProps = useRef();

  useEffect(() => {
    if (previousProps.current) {
      const changes = {};
      Object.keys({...previousProps.current, ...props}).forEach(key => {
        if (previousProps.current[key] !== props[key]) {
          changes[key] = {
            from: previousProps.current[key],
            to: props[key]
          };
        }
      });
      if (Object.keys(changes).length) {
        console.log('[why-update]', name, changes);
      }
    }
    previousProps.current = props;
  });
}
```
{% endif %}

{% if framework == 'express' %}
## Express.js Debugging

### Request/Response Logging

```javascript
const express = require('express');
const app = express();

// Debug middleware
app.use((req, res, next) => {
  const start = Date.now();

  res.on('finish', () => {
    const duration = Date.now() - start;
    console.log(`${req.method} ${req.url} ${res.statusCode} - ${duration}ms`);
  });

  next();
});

// Or use morgan for structured logging
const morgan = require('morgan');
app.use(morgan('dev'));
```

### Error Handling Middleware

```javascript
// Error handling middleware (must have 4 parameters)
app.use((err, req, res, next) => {
  console.error('Error:', err.message);
  console.error('Stack:', err.stack);

  res.status(err.status || 500).json({
    error: process.env.NODE_ENV === 'production'
      ? 'Internal server error'
      : err.message
  });
});
```
{% endif %}

---

## Debugging Checklist

### Before You Start
- [ ] Can you reproduce the bug consistently?
- [ ] What's the expected behavior?
- [ ] What's the actual behavior?
- [ ] When did it start happening?

### Investigation
- [ ] Check the console for errors
- [ ] Review recent code changes
- [ ] Isolate the problem (binary search)
- [ ] Check input data validity
- [ ] Review async operation ordering

### Common Fixes
- [ ] Null/undefined checks
- [ ] Async/await error handling
- [ ] Event listener cleanup
- [ ] Correct variable scoping
- [ ] Type coercion issues

### After Fixing
- [ ] Verify the fix works
- [ ] Check for side effects
- [ ] Add regression test
- [ ] Document if it was tricky

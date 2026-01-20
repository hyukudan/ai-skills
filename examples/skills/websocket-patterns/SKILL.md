---
name: websocket-patterns
description: |
  WebSocket patterns for real-time applications. Covers connection management,
  authentication, scaling, heartbeats, and common use cases like chat and
  live updates.
version: 1.0.0
tags: [websocket, realtime, socket-io, ws, live-updates]
category: development/realtime
trigger_phrases:
  - "WebSocket"
  - "real-time"
  - "Socket.io"
  - "live updates"
  - "bidirectional"
  - "push notifications"
  - "chat application"
variables:
  framework:
    type: string
    description: WebSocket framework
    enum: [native, socket-io, ws]
    default: native
---

# WebSocket Patterns Guide

## Core Philosophy

**WebSockets are for bidirectional, low-latency communication.** Use them when you need real-time data push or frequent client-server messages.

> "Use WebSockets when HTTP polling would be wasteful, not just because it's cool."

---

## When to Use WebSockets

| Use Case | WebSocket | Alternative |
|----------|-----------|-------------|
| Chat/messaging | Yes | - |
| Live notifications | Yes | SSE |
| Collaborative editing | Yes | - |
| Gaming | Yes | - |
| Stock tickers | Maybe | SSE |
| Form submissions | No | HTTP |
| File uploads | No | HTTP |

---

## 1. Basic Implementation

### Server (Node.js with ws)

```typescript
import { WebSocketServer, WebSocket } from 'ws';

const wss = new WebSocketServer({ port: 8080 });

// Connection handling
wss.on('connection', (ws: WebSocket, req) => {
  console.log('Client connected');

  // Message handling
  ws.on('message', (data) => {
    const message = JSON.parse(data.toString());
    handleMessage(ws, message);
  });

  // Error handling
  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });

  // Connection closed
  ws.on('close', () => {
    console.log('Client disconnected');
  });

  // Send welcome message
  ws.send(JSON.stringify({ type: 'connected', timestamp: Date.now() }));
});

function handleMessage(ws: WebSocket, message: any) {
  switch (message.type) {
    case 'ping':
      ws.send(JSON.stringify({ type: 'pong' }));
      break;
    case 'subscribe':
      subscribeToChannel(ws, message.channel);
      break;
    default:
      console.log('Unknown message type:', message.type);
  }
}
```

### Client (Browser)

```typescript
class WebSocketClient {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  constructor(private url: string) {}

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        console.log('Connected');
        this.reconnectAttempts = 0;
        resolve();
      };

      this.ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        this.handleMessage(message);
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        reject(error);
      };

      this.ws.onclose = () => {
        console.log('Disconnected');
        this.attemptReconnect();
      };
    });
  }

  send(message: object): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    }
  }

  private handleMessage(message: any): void {
    // Dispatch to appropriate handler
    window.dispatchEvent(new CustomEvent('ws-message', { detail: message }));
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1);
      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
      setTimeout(() => this.connect(), delay);
    }
  }
}
```

---

## 2. Authentication

### Token-Based Auth

```typescript
// Server
wss.on('connection', async (ws, req) => {
  // Get token from query string or header
  const url = new URL(req.url!, `http://${req.headers.host}`);
  const token = url.searchParams.get('token');

  if (!token) {
    ws.close(4001, 'Authentication required');
    return;
  }

  try {
    const user = await verifyToken(token);
    (ws as any).user = user;
    console.log(`User ${user.id} connected`);
  } catch (error) {
    ws.close(4002, 'Invalid token');
    return;
  }
});

// Client
const ws = new WebSocket(`wss://api.example.com/ws?token=${authToken}`);
```

### Auth After Connection

```typescript
// Server
ws.on('message', async (data) => {
  const message = JSON.parse(data.toString());

  if (message.type === 'authenticate') {
    try {
      const user = await verifyToken(message.token);
      (ws as any).user = user;
      (ws as any).authenticated = true;
      ws.send(JSON.stringify({ type: 'authenticated', userId: user.id }));
    } catch (error) {
      ws.send(JSON.stringify({ type: 'auth_error', message: 'Invalid token' }));
    }
    return;
  }

  // Require auth for other messages
  if (!(ws as any).authenticated) {
    ws.send(JSON.stringify({ type: 'error', message: 'Not authenticated' }));
    return;
  }

  handleMessage(ws, message);
});
```

---

## 3. Heartbeat/Ping-Pong

```typescript
// Server-side heartbeat
const HEARTBEAT_INTERVAL = 30000;
const CLIENT_TIMEOUT = 35000;

wss.on('connection', (ws) => {
  (ws as any).isAlive = true;

  ws.on('pong', () => {
    (ws as any).isAlive = true;
  });
});

// Ping all clients periodically
const heartbeat = setInterval(() => {
  wss.clients.forEach((ws) => {
    if (!(ws as any).isAlive) {
      console.log('Client unresponsive, terminating');
      return ws.terminate();
    }

    (ws as any).isAlive = false;
    ws.ping();
  });
}, HEARTBEAT_INTERVAL);

wss.on('close', () => {
  clearInterval(heartbeat);
});
```

```typescript
// Client-side heartbeat
class WebSocketClient {
  private pingInterval: NodeJS.Timer | null = null;

  connect(): void {
    // ... connection setup

    this.ws.onopen = () => {
      this.startHeartbeat();
    };

    this.ws.onclose = () => {
      this.stopHeartbeat();
    };
  }

  private startHeartbeat(): void {
    this.pingInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send({ type: 'ping' });
      }
    }, 25000);
  }

  private stopHeartbeat(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
  }
}
```

---

## 4. Room/Channel Pattern

```typescript
// Server with rooms
const rooms = new Map<string, Set<WebSocket>>();

function joinRoom(ws: WebSocket, roomId: string): void {
  if (!rooms.has(roomId)) {
    rooms.set(roomId, new Set());
  }
  rooms.get(roomId)!.add(ws);
  (ws as any).rooms = (ws as any).rooms || new Set();
  (ws as any).rooms.add(roomId);
}

function leaveRoom(ws: WebSocket, roomId: string): void {
  rooms.get(roomId)?.delete(ws);
  (ws as any).rooms?.delete(roomId);
}

function broadcastToRoom(roomId: string, message: object, exclude?: WebSocket): void {
  const clients = rooms.get(roomId);
  if (!clients) return;

  const payload = JSON.stringify(message);
  clients.forEach((client) => {
    if (client !== exclude && client.readyState === WebSocket.OPEN) {
      client.send(payload);
    }
  });
}

// Clean up on disconnect
ws.on('close', () => {
  (ws as any).rooms?.forEach((roomId: string) => {
    leaveRoom(ws, roomId);
  });
});
```

---

## 5. Scaling with Redis Pub/Sub

```typescript
import { createClient } from 'redis';

const publisher = createClient();
const subscriber = createClient();

await publisher.connect();
await subscriber.connect();

// Subscribe to channel for cross-server messages
await subscriber.subscribe('ws-broadcast', (message) => {
  const { roomId, data, excludeServerId } = JSON.parse(message);

  // Don't broadcast our own messages back
  if (excludeServerId === SERVER_ID) return;

  broadcastToRoom(roomId, data);
});

// Broadcast to all servers
function broadcastGlobal(roomId: string, data: object): void {
  // Local broadcast
  broadcastToRoom(roomId, data);

  // Publish to other servers
  publisher.publish('ws-broadcast', JSON.stringify({
    roomId,
    data,
    excludeServerId: SERVER_ID,
  }));
}
```

---

## 6. Message Protocol Design

### Structured Messages

```typescript
// Message types
interface BaseMessage {
  type: string;
  id?: string;  // For request/response correlation
  timestamp?: number;
}

interface ChatMessage extends BaseMessage {
  type: 'chat';
  roomId: string;
  content: string;
  userId: string;
}

interface PresenceMessage extends BaseMessage {
  type: 'presence';
  userId: string;
  status: 'online' | 'offline' | 'away';
}

interface ErrorMessage extends BaseMessage {
  type: 'error';
  code: string;
  message: string;
  originalMessageId?: string;
}

// Type-safe handler
function handleMessage(ws: WebSocket, message: BaseMessage): void {
  switch (message.type) {
    case 'chat':
      handleChat(ws, message as ChatMessage);
      break;
    case 'presence':
      handlePresence(ws, message as PresenceMessage);
      break;
    default:
      sendError(ws, 'UNKNOWN_TYPE', `Unknown message type: ${message.type}`);
  }
}
```

### Request/Response Pattern

```typescript
// Client
class WebSocketClient {
  private pendingRequests = new Map<string, {
    resolve: Function;
    reject: Function;
    timeout: NodeJS.Timeout;
  }>();

  async request<T>(message: object, timeout = 10000): Promise<T> {
    const id = crypto.randomUUID();

    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(() => {
        this.pendingRequests.delete(id);
        reject(new Error('Request timeout'));
      }, timeout);

      this.pendingRequests.set(id, { resolve, reject, timeout: timeoutId });
      this.send({ ...message, id });
    });
  }

  private handleMessage(message: any): void {
    if (message.id && this.pendingRequests.has(message.id)) {
      const { resolve, reject, timeout } = this.pendingRequests.get(message.id)!;
      clearTimeout(timeout);
      this.pendingRequests.delete(message.id);

      if (message.type === 'error') {
        reject(new Error(message.message));
      } else {
        resolve(message);
      }
      return;
    }

    // Handle other messages...
  }
}

// Usage
const response = await client.request({ type: 'get_user', userId: '123' });
```

---

## 7. Common Use Cases

### Chat Room

```typescript
// Join room
ws.on('message', (data) => {
  const msg = JSON.parse(data.toString());

  if (msg.type === 'join') {
    joinRoom(ws, msg.roomId);
    broadcastToRoom(msg.roomId, {
      type: 'user_joined',
      userId: (ws as any).user.id,
      username: (ws as any).user.name,
    }, ws);
  }

  if (msg.type === 'chat') {
    broadcastToRoom(msg.roomId, {
      type: 'chat',
      userId: (ws as any).user.id,
      username: (ws as any).user.name,
      content: msg.content,
      timestamp: Date.now(),
    });
  }
});
```

### Live Notifications

```typescript
// Subscribe user to their notification channel
ws.on('message', (data) => {
  const msg = JSON.parse(data.toString());

  if (msg.type === 'subscribe_notifications') {
    joinRoom(ws, `notifications:${(ws as any).user.id}`);
  }
});

// From your application
function notifyUser(userId: string, notification: object): void {
  broadcastToRoom(`notifications:${userId}`, {
    type: 'notification',
    ...notification,
  });
}
```

---

## Quick Reference

### Close Codes

| Code | Meaning |
|------|---------|
| 1000 | Normal closure |
| 1001 | Going away |
| 1008 | Policy violation |
| 1011 | Server error |
| 4000-4999 | Application-specific |

### Ready States

```typescript
WebSocket.CONNECTING = 0;
WebSocket.OPEN = 1;
WebSocket.CLOSING = 2;
WebSocket.CLOSED = 3;
```

### Connection Checklist

- [ ] Authentication
- [ ] Heartbeat/ping-pong
- [ ] Reconnection logic
- [ ] Error handling
- [ ] Graceful shutdown
- [ ] Message validation

---

## Related Skills

- `graphql-development` - GraphQL subscriptions
- `redis-patterns` - Pub/sub for scaling
- `event-driven-architecture` - Event patterns

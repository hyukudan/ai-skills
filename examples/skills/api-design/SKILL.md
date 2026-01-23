---
name: api-design
description: |
  REST API design principles and best practices. Use when designing new APIs,
  reviewing API contracts, or improving existing endpoints. Covers resource
  modeling, HTTP semantics, error handling, versioning, and documentation.
license: MIT
allowed-tools: Read Edit Bash
version: 1.0.0
tags: [api, rest, http, design, backend]
category: development/architecture
variables:
  api_style:
    type: string
    description: API architectural style
    enum: [rest, graphql, grpc]
    default: rest
  auth_method:
    type: string
    description: Authentication approach
    enum: [jwt, oauth2, api-key, session]
    default: jwt
---

# API Design Guide

## Design Philosophy

**APIs are products.** Treat them with the same care as user interfaces.

- **Consistency** over cleverness
- **Predictability** over flexibility
- **Simplicity** over completeness

---

{% if api_style == "rest" %}
## RESTful Design Principles

### Resource-Oriented URLs

```
# Resources are nouns, not verbs
GET  /users           # List users
GET  /users/123       # Get user 123
POST /users           # Create user
PUT  /users/123       # Replace user 123
PATCH /users/123      # Update user 123
DELETE /users/123     # Delete user 123

# Nested resources for relationships
GET /users/123/orders           # User's orders
GET /users/123/orders/456       # Specific order
POST /users/123/orders          # Create order for user
```

### URL Anti-Patterns

```
# BAD - Verbs in URLs
POST /createUser
GET  /getUser/123
POST /users/123/delete

# BAD - Actions as resources
POST /users/123/activate

# GOOD - Use HTTP methods + resources
POST /users
GET  /users/123
DELETE /users/123
PATCH /users/123 { "status": "active" }
```

### HTTP Methods Semantics

| Method | Idempotent | Safe | Use Case |
|--------|------------|------|----------|
| GET | Yes | Yes | Retrieve resource |
| POST | No | No | Create resource |
| PUT | Yes | No | Replace resource |
| PATCH | No | No | Partial update |
| DELETE | Yes | No | Remove resource |

---

## Response Design

### Consistent Envelope

```json
// Success response
{
  "data": {
    "id": "123",
    "name": "John Doe",
    "email": "john@example.com"
  },
  "meta": {
    "request_id": "req_abc123"
  }
}

// Collection response
{
  "data": [
    { "id": "1", "name": "Item 1" },
    { "id": "2", "name": "Item 2" }
  ],
  "meta": {
    "total": 100,
    "page": 1,
    "per_page": 20
  },
  "links": {
    "self": "/items?page=1",
    "next": "/items?page=2",
    "last": "/items?page=5"
  }
}

// Error response
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": [
      {
        "field": "email",
        "message": "Must be a valid email address"
      }
    ]
  },
  "meta": {
    "request_id": "req_abc123"
  }
}
```

### HTTP Status Codes

**Success (2xx)**
```
200 OK              - Successful GET, PUT, PATCH, DELETE
201 Created         - Successful POST (include Location header)
204 No Content      - Successful DELETE with no body
```

**Client Errors (4xx)**
```
400 Bad Request     - Malformed syntax, invalid parameters
401 Unauthorized    - Missing/invalid authentication
403 Forbidden       - Authenticated but not authorized
404 Not Found       - Resource doesn't exist
409 Conflict        - Resource state conflict
422 Unprocessable   - Validation errors
429 Too Many Reqs   - Rate limit exceeded
```

**Server Errors (5xx)**
```
500 Internal Error  - Unexpected server error
502 Bad Gateway     - Upstream service error
503 Unavailable     - Service temporarily down
504 Gateway Timeout - Upstream timeout
```

{% elif api_style == "graphql" %}
## GraphQL Design Principles

### Schema Design

```graphql
type User {
  id: ID!
  email: String!
  name: String!
  orders(first: Int, after: String): OrderConnection!
  createdAt: DateTime!
}

type Order {
  id: ID!
  user: User!
  items: [OrderItem!]!
  total: Money!
  status: OrderStatus!
}

type Query {
  user(id: ID!): User
  users(first: Int, after: String, filter: UserFilter): UserConnection!
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
  updateUser(id: ID!, input: UpdateUserInput!): UpdateUserPayload!
}
```

### Query Patterns

```graphql
# Use connections for pagination
type UserConnection {
  edges: [UserEdge!]!
  pageInfo: PageInfo!
  totalCount: Int!
}

type UserEdge {
  node: User!
  cursor: String!
}

type PageInfo {
  hasNextPage: Boolean!
  hasPreviousPage: Boolean!
  startCursor: String
  endCursor: String
}
```

### Mutation Patterns

```graphql
input CreateUserInput {
  email: String!
  name: String!
  password: String!
}

type CreateUserPayload {
  user: User
  errors: [UserError!]!
}

type UserError {
  field: String
  message: String!
  code: ErrorCode!
}
```

{% endif %}

---

## Pagination

### Cursor-Based (Recommended)

```
GET /items?cursor=eyJpZCI6MTAwfQ&limit=20
```

```json
{
  "data": [...],
  "pagination": {
    "next_cursor": "eyJpZCI6MTIwfQ",
    "has_more": true
  }
}
```

**Advantages:**
- Stable with real-time data
- No skipped/duplicate items
- Efficient for large datasets

### Offset-Based (Simple)

```
GET /items?page=2&per_page=20
```

```json
{
  "data": [...],
  "pagination": {
    "total": 500,
    "page": 2,
    "per_page": 20,
    "total_pages": 25
  }
}
```

**Disadvantages:**
- Items shift with inserts/deletes
- Slow for large offsets

---

## Filtering & Sorting

### Query Parameters

```
# Filtering
GET /users?status=active&role=admin
GET /orders?created_after=2024-01-01&total_gte=100

# Sorting
GET /users?sort=created_at:desc,name:asc

# Field selection
GET /users?fields=id,name,email

# Combined
GET /orders?status=pending&sort=created_at:desc&fields=id,total&limit=10
```

### Complex Filters

```json
// POST /users/search
{
  "filter": {
    "and": [
      { "field": "status", "op": "eq", "value": "active" },
      { "or": [
        { "field": "role", "op": "eq", "value": "admin" },
        { "field": "created_at", "op": "gt", "value": "2024-01-01" }
      ]}
    ]
  },
  "sort": [
    { "field": "name", "direction": "asc" }
  ],
  "page": { "limit": 20, "cursor": "abc123" }
}
```

---

{% if auth_method == "jwt" %}
## JWT Authentication

### Token Structure

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIs...
```

### Token Payload

```json
{
  "sub": "user_123",           // Subject (user ID)
  "iat": 1704067200,           // Issued at
  "exp": 1704153600,           // Expiration
  "scope": "read write",       // Permissions
  "iss": "api.example.com"     // Issuer
}
```

### Refresh Flow

```
POST /auth/refresh
{
  "refresh_token": "..."
}

Response:
{
  "access_token": "...",
  "expires_in": 3600
}
```

{% elif auth_method == "oauth2" %}
## OAuth2 Authentication

### Authorization Code Flow

```
1. Redirect to authorization
GET /oauth/authorize?
  client_id=xxx&
  redirect_uri=https://app.com/callback&
  response_type=code&
  scope=read+write&
  state=random123

2. User authorizes, redirected back
GET /callback?code=auth_code&state=random123

3. Exchange code for tokens
POST /oauth/token
{
  "grant_type": "authorization_code",
  "code": "auth_code",
  "client_id": "xxx",
  "client_secret": "xxx",
  "redirect_uri": "https://app.com/callback"
}
```

{% elif auth_method == "api-key" %}
## API Key Authentication

### Header-Based

```
X-API-Key: sk_live_abc123xyz
```

### Key Management

```
POST /api-keys
{
  "name": "Production Server",
  "scopes": ["read", "write"]
}

Response:
{
  "id": "key_123",
  "key": "sk_live_abc123xyz",  // Only shown once!
  "prefix": "sk_live_abc",
  "scopes": ["read", "write"]
}
```

{% endif %}

---

## Versioning

### URL Path (Recommended)

```
/v1/users
/v2/users
```

**Pros:** Explicit, cacheable, easy routing
**Cons:** URL changes between versions

### Header-Based

```
Accept: application/vnd.api+json; version=2
```

**Pros:** Clean URLs
**Cons:** Harder to test, less visible

### Version Lifecycle

```
v1 - Deprecated (sunset in 6 months)
v2 - Stable (current)
v3 - Beta (breaking changes possible)
```

---

## Error Handling

### Error Response Structure

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "User with ID 123 not found",
    "details": {
      "resource": "User",
      "id": "123"
    },
    "help_url": "https://docs.api.com/errors/RESOURCE_NOT_FOUND"
  },
  "request_id": "req_abc123"
}
```

### Common Error Codes

```
AUTH_REQUIRED        - 401 - Authentication needed
AUTH_INVALID         - 401 - Invalid credentials
FORBIDDEN            - 403 - Not authorized
NOT_FOUND            - 404 - Resource doesn't exist
VALIDATION_ERROR     - 422 - Input validation failed
RATE_LIMITED         - 429 - Too many requests
INTERNAL_ERROR       - 500 - Server error
```

---

## Rate Limiting

### Headers

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1704067200
```

### 429 Response

```json
{
  "error": {
    "code": "RATE_LIMITED",
    "message": "Rate limit exceeded",
    "retry_after": 60
  }
}
```

---

## Documentation

Every endpoint should document:

1. **URL and method**
2. **Authentication requirements**
3. **Request parameters/body**
4. **Response format**
5. **Error responses**
6. **Example requests/responses**
7. **Rate limits**

### OpenAPI Example

```yaml
paths:
  /users/{id}:
    get:
      summary: Get user by ID
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
      responses:
        200:
          description: User found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        404:
          description: User not found
```

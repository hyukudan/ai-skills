---
name: database-design
description: |
  Database schema design principles for SQL and NoSQL databases. Use when designing
  new databases, optimizing existing schemas, planning migrations, or choosing between
  database types. Covers normalization, indexing, relationships, and scaling patterns.
version: 1.0.0
tags: [database, sql, nosql, schema, design, postgresql, mongodb]
category: development/backend
variables:
  database_type:
    type: string
    description: Type of database
    enum: [postgresql, mysql, mongodb, redis, sqlite]
    default: postgresql
  scale:
    type: string
    description: Expected scale of the application
    enum: [small, medium, large]
    default: medium
---

# Database Design Guide

## Design Philosophy

**Data outlives code.** Your schema decisions today will constrain your options for years.

### Core Principles

1. **Model the domain, not the UI** - Schemas should reflect business reality
2. **Normalize first, denormalize with purpose** - Start correct, optimize later
3. **Indexes are not magic** - They trade write speed for read speed
4. **Plan for change** - Migrations are inevitable

---

## Data Modeling Process

### Step 1: Identify Entities

```
Questions to ask:
1. What are the core "things" in the domain?
2. What uniquely identifies each thing?
3. What attributes does each thing have?
4. What are the relationships between things?
```

### Step 2: Define Relationships

```
One-to-One (1:1)
  User ←→ Profile
  - Rare, often better as single table
  - Use when: optional data, different access patterns

One-to-Many (1:N)
  User ←→ Posts
  - Most common relationship
  - Foreign key on the "many" side

Many-to-Many (M:N)
  Posts ←→ Tags
  - Requires junction/join table
  - Junction table can have its own attributes
```

---

{% if database_type == "postgresql" or database_type == "mysql" or database_type == "sqlite" %}
## Relational Database Design

### Normalization

**First Normal Form (1NF):**
- Eliminate repeating groups
- Each cell contains single value

```sql
-- BAD: Repeating groups
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  customer_name VARCHAR(100),
  items VARCHAR(500)  -- "item1,item2,item3"
);

-- GOOD: Separate table
CREATE TABLE order_items (
  id SERIAL PRIMARY KEY,
  order_id INT REFERENCES orders(id),
  product_id INT REFERENCES products(id),
  quantity INT
);
```

**Second Normal Form (2NF):**
- Must be in 1NF
- No partial dependencies (all non-key columns depend on entire primary key)

**Third Normal Form (3NF):**
- Must be in 2NF
- No transitive dependencies (non-key columns don't depend on other non-key columns)

```sql
-- BAD: Transitive dependency
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  customer_id INT,
  customer_email VARCHAR(100),  -- Depends on customer_id, not order
  total DECIMAL
);

-- GOOD: Separate concerns
CREATE TABLE customers (
  id SERIAL PRIMARY KEY,
  email VARCHAR(100) UNIQUE
);

CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  customer_id INT REFERENCES customers(id),
  total DECIMAL
);
```

### Table Design Patterns

{% if database_type == "postgresql" %}
```sql
-- Complete table with best practices
CREATE TABLE users (
  -- Primary key: UUID for distributed systems, SERIAL for simplicity
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Required fields with constraints
  email VARCHAR(255) NOT NULL UNIQUE,
  username VARCHAR(50) NOT NULL UNIQUE,

  -- Optional fields
  display_name VARCHAR(100),
  bio TEXT,

  -- Enums for controlled values
  status VARCHAR(20) NOT NULL DEFAULT 'active'
    CHECK (status IN ('active', 'inactive', 'suspended')),

  -- JSON for flexible schema
  preferences JSONB DEFAULT '{}',

  -- Timestamps (always include these)
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  deleted_at TIMESTAMPTZ  -- Soft delete
);

-- Index for common queries
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_status ON users(status) WHERE deleted_at IS NULL;
CREATE INDEX idx_users_preferences ON users USING GIN (preferences);

-- Trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER users_updated_at
  BEFORE UPDATE ON users
  FOR EACH ROW EXECUTE FUNCTION update_updated_at();
```
{% elif database_type == "mysql" %}
```sql
CREATE TABLE users (
  id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  username VARCHAR(50) NOT NULL UNIQUE,
  display_name VARCHAR(100),
  status ENUM('active', 'inactive', 'suspended') DEFAULT 'active',
  preferences JSON,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  deleted_at TIMESTAMP NULL,

  INDEX idx_status (status),
  INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
```
{% endif %}

### Relationship Patterns

```sql
-- One-to-Many: User has many posts
CREATE TABLE posts (
  id SERIAL PRIMARY KEY,
  user_id INT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
  title VARCHAR(200) NOT NULL,
  content TEXT,
  published_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_posts_user ON posts(user_id);
CREATE INDEX idx_posts_published ON posts(published_at) WHERE published_at IS NOT NULL;

-- Many-to-Many: Posts have many tags
CREATE TABLE tags (
  id SERIAL PRIMARY KEY,
  name VARCHAR(50) NOT NULL UNIQUE,
  slug VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE post_tags (
  post_id INT REFERENCES posts(id) ON DELETE CASCADE,
  tag_id INT REFERENCES tags(id) ON DELETE CASCADE,
  PRIMARY KEY (post_id, tag_id)
);

-- Self-referential: Categories with parent
CREATE TABLE categories (
  id SERIAL PRIMARY KEY,
  parent_id INT REFERENCES categories(id) ON DELETE SET NULL,
  name VARCHAR(100) NOT NULL,
  path LTREE  -- PostgreSQL extension for hierarchy
);
```

### Indexing Strategy

```sql
-- B-tree (default): Equality and range queries
CREATE INDEX idx_orders_date ON orders(created_at);

-- Hash: Only equality queries (PostgreSQL 10+)
CREATE INDEX idx_users_email_hash ON users USING HASH (email);

-- GIN: Full-text search, JSONB, arrays
CREATE INDEX idx_posts_search ON posts USING GIN (to_tsvector('english', title || ' ' || content));
CREATE INDEX idx_users_tags ON users USING GIN (tags);

-- Partial: Index subset of rows
CREATE INDEX idx_active_users ON users(email) WHERE status = 'active';

-- Covering: Include columns to avoid table lookup
CREATE INDEX idx_orders_summary ON orders(user_id) INCLUDE (total, status);

-- Composite: Multiple columns (order matters!)
CREATE INDEX idx_orders_user_date ON orders(user_id, created_at DESC);
```

**Index Guidelines:**
```
✅ Index columns used in:
   - WHERE clauses
   - JOIN conditions
   - ORDER BY clauses
   - Foreign keys

❌ Avoid indexing:
   - Low cardinality columns (boolean, status with few values)
   - Frequently updated columns
   - Small tables (< 1000 rows)
```

{% endif %}

{% if database_type == "mongodb" %}
## MongoDB Schema Design

### Document Structure

```javascript
// Embedded document (denormalized)
// Use when: data is always accessed together, 1:1 or 1:few
{
  _id: ObjectId("..."),
  email: "user@example.com",
  profile: {                    // Embedded
    displayName: "John Doe",
    bio: "Developer",
    avatar: "https://..."
  },
  addresses: [                  // Embedded array (1:few)
    { type: "home", street: "123 Main", city: "NYC" },
    { type: "work", street: "456 Office", city: "NYC" }
  ]
}

// Referenced document (normalized)
// Use when: data accessed independently, 1:many, many:many
{
  _id: ObjectId("..."),
  email: "user@example.com",
  organizationId: ObjectId("...")  // Reference
}
```

### Schema Patterns

```javascript
// Pattern: Polymorphic schema
// Single collection with different document structures
{
  _id: ObjectId("..."),
  type: "blog_post",
  title: "My Post",
  content: "..."
}
{
  _id: ObjectId("..."),
  type: "video",
  title: "My Video",
  url: "https://...",
  duration: 300
}

// Pattern: Bucket (time-series data)
{
  _id: ObjectId("..."),
  sensorId: "sensor-001",
  date: ISODate("2024-01-15"),
  readings: [
    { time: ISODate("2024-01-15T00:00:00Z"), value: 23.5 },
    { time: ISODate("2024-01-15T00:01:00Z"), value: 23.6 },
    // ... up to ~200 readings per document
  ],
  count: 200,
  sum: 4720,
  min: 23.1,
  max: 24.2
}

// Pattern: Extended reference
// Duplicate frequently-accessed fields to avoid joins
{
  _id: ObjectId("..."),
  title: "Order #1234",
  customerId: ObjectId("..."),
  customerName: "John Doe",      // Duplicated for display
  customerEmail: "john@..."      // Duplicated for notifications
}
```

### Indexing in MongoDB

```javascript
// Single field index
db.users.createIndex({ email: 1 })

// Compound index
db.orders.createIndex({ userId: 1, createdAt: -1 })

// Text index for search
db.posts.createIndex({ title: "text", content: "text" })

// Partial index
db.users.createIndex(
  { email: 1 },
  { partialFilterExpression: { status: "active" } }
)

// TTL index (auto-delete old documents)
db.sessions.createIndex(
  { createdAt: 1 },
  { expireAfterSeconds: 86400 }  // 24 hours
)

// Unique sparse (allow multiple nulls)
db.users.createIndex(
  { phoneNumber: 1 },
  { unique: true, sparse: true }
)
```

{% endif %}

{% if database_type == "redis" %}
## Redis Data Modeling

### Data Structures

```redis
# Strings - Simple key-value
SET user:123:name "John Doe"
SET user:123:email "john@example.com"
SETEX session:abc123 3600 "user:123"  # Expires in 1 hour

# Hashes - Object storage
HSET user:123 name "John Doe" email "john@example.com" status "active"
HGET user:123 name
HGETALL user:123

# Lists - Ordered, duplicates allowed
LPUSH notifications:123 "New message"
LRANGE notifications:123 0 9  # Last 10

# Sets - Unique values
SADD user:123:roles "admin" "editor"
SISMEMBER user:123:roles "admin"
SINTER user:123:roles user:456:roles  # Common roles

# Sorted Sets - Ranked data
ZADD leaderboard 1000 "user:123" 950 "user:456"
ZREVRANGE leaderboard 0 9 WITHSCORES  # Top 10
```

### Common Patterns

```redis
# Rate limiting (sliding window)
MULTI
ZADD requests:user:123 <timestamp> <request_id>
ZREMRANGEBYSCORE requests:user:123 0 <timestamp - window>
ZCARD requests:user:123
EXEC

# Caching with TTL
SET cache:user:123 "<json>" EX 300  # 5 min cache
GET cache:user:123

# Pub/Sub
PUBLISH chat:room:general "Hello everyone!"
SUBSCRIBE chat:room:general

# Distributed lock
SET lock:resource:123 <unique_id> NX EX 30
# ... do work ...
DEL lock:resource:123  # Release (with Lua for safety)
```

{% endif %}

---

{% if scale == "medium" or scale == "large" %}
## Scaling Patterns

### Read Replicas

```
Primary (writes) ──→ Replica 1 (reads)
                 ──→ Replica 2 (reads)
                 ──→ Replica 3 (reads)

Use cases:
- Read-heavy workloads (90%+ reads)
- Geographic distribution
- Analytics queries
```

### Sharding Strategies

```
1. Range-based sharding
   Shard A: users 1-1M
   Shard B: users 1M-2M
   ⚠️ Risk: Hot spots if ranges uneven

2. Hash-based sharding
   Shard = hash(user_id) % num_shards
   ✅ Even distribution
   ⚠️ Range queries across shards expensive

3. Directory-based sharding
   Lookup service maps keys to shards
   ✅ Flexible rebalancing
   ⚠️ Lookup service is single point of failure
```

### Partitioning (PostgreSQL)

```sql
-- Range partitioning by date
CREATE TABLE events (
  id SERIAL,
  event_type VARCHAR(50),
  payload JSONB,
  created_at TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (created_at);

CREATE TABLE events_2024_01 PARTITION OF events
  FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE events_2024_02 PARTITION OF events
  FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- List partitioning by region
CREATE TABLE orders (
  id SERIAL,
  region VARCHAR(10),
  total DECIMAL
) PARTITION BY LIST (region);

CREATE TABLE orders_us PARTITION OF orders FOR VALUES IN ('US');
CREATE TABLE orders_eu PARTITION OF orders FOR VALUES IN ('EU', 'UK');
```

{% endif %}

---

## Migration Best Practices

### Safe Migration Pattern

```sql
-- Step 1: Add new column (nullable)
ALTER TABLE users ADD COLUMN new_email VARCHAR(255);

-- Step 2: Backfill data (in batches)
UPDATE users SET new_email = email WHERE new_email IS NULL LIMIT 1000;

-- Step 3: Deploy code that writes to both columns

-- Step 4: Add constraints
ALTER TABLE users ALTER COLUMN new_email SET NOT NULL;
ALTER TABLE users ADD CONSTRAINT unique_new_email UNIQUE (new_email);

-- Step 5: Deploy code that reads from new column

-- Step 6: Remove old column
ALTER TABLE users DROP COLUMN email;
ALTER TABLE users RENAME COLUMN new_email TO email;
```

### Zero-Downtime Migrations

```
✅ SAFE operations:
- Adding nullable column
- Adding index CONCURRENTLY
- Adding table
- Dropping unused column (after code deploys)

⚠️ CAREFUL operations:
- Adding NOT NULL constraint (use CHECK first)
- Changing column type (may lock table)
- Adding UNIQUE constraint (creates index)

❌ AVOID in production:
- Dropping column still in use
- Renaming column without transition period
- Large data migrations without batching
```

---

## Query Optimization

### EXPLAIN Cheatsheet

```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'test@example.com';

-- Read the output:
-- Seq Scan = Full table scan (bad for large tables)
-- Index Scan = Using index (good)
-- Bitmap Heap Scan = Multiple index results combined
-- Hash Join = Building hash table for join
-- Nested Loop = For each row, scan other table

-- Key metrics:
-- actual time = Execution time
-- rows = Rows processed
-- loops = Times operation repeated
```

### Common Optimizations

```sql
-- Avoid SELECT *
SELECT id, email, name FROM users;  -- Only needed columns

-- Use EXISTS instead of COUNT
SELECT EXISTS(SELECT 1 FROM orders WHERE user_id = 123);

-- Batch inserts
INSERT INTO logs (message, level) VALUES
  ('msg1', 'info'),
  ('msg2', 'error'),
  ('msg3', 'info');

-- Use CTEs for readability (may affect performance)
WITH active_users AS (
  SELECT id FROM users WHERE status = 'active'
)
SELECT * FROM orders WHERE user_id IN (SELECT id FROM active_users);
```

---

## Anti-Patterns

### Entity-Attribute-Value (EAV)

```sql
-- BAD: EAV pattern
CREATE TABLE attributes (
  entity_id INT,
  attribute_name VARCHAR(50),
  attribute_value TEXT
);

-- Problems: No type safety, complex queries, poor performance

-- BETTER: JSONB for flexible schema
CREATE TABLE entities (
  id SERIAL PRIMARY KEY,
  attributes JSONB
);
```

### God Tables

```sql
-- BAD: Everything in one table
CREATE TABLE data (
  id SERIAL,
  type VARCHAR(50),
  field1 VARCHAR(100),
  field2 VARCHAR(100),
  field3 VARCHAR(100),
  -- ... 50 more nullable columns
);

-- BETTER: Proper normalization or document DB
```

### Missing Timestamps

```sql
-- BAD: No audit trail
CREATE TABLE orders (id SERIAL, total DECIMAL);

-- GOOD: Always include timestamps
CREATE TABLE orders (
  id SERIAL PRIMARY KEY,
  total DECIMAL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
```

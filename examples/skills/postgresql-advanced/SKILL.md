---
name: postgresql-advanced
description: |
  Advanced PostgreSQL patterns and features. Covers CTEs, window functions,
  JSONB operations, full-text search, partitioning, and performance tuning
  for production databases.
version: 1.0.0
tags: [postgresql, database, sql, performance, jsonb]
category: databases/postgresql
trigger_phrases:
  - "PostgreSQL"
  - "Postgres"
  - "CTE"
  - "window function"
  - "JSONB"
  - "full-text search"
  - "partitioning"
  - "postgres performance"
variables:
  focus:
    type: string
    description: Focus area
    enum: [queries, jsonb, performance, admin]
    default: queries
---

# Advanced PostgreSQL Guide

## Core Philosophy

**PostgreSQL can do more than you think.** Before adding Redis, Elasticsearch, or another database, check if Postgres can handle it.

> "PostgreSQL is not just a database—it's a data platform."

---

## 1. Common Table Expressions (CTEs)

### Basic CTE

```sql
WITH active_users AS (
    SELECT user_id, email, last_login
    FROM users
    WHERE last_login > NOW() - INTERVAL '30 days'
)
SELECT
    u.user_id,
    u.email,
    COUNT(o.id) as order_count
FROM active_users u
LEFT JOIN orders o ON o.user_id = u.user_id
GROUP BY u.user_id, u.email;
```

### Recursive CTE (Hierarchies)

```sql
-- Org chart / category tree
WITH RECURSIVE org_tree AS (
    -- Base case: top-level managers
    SELECT id, name, manager_id, 1 as level
    FROM employees
    WHERE manager_id IS NULL

    UNION ALL

    -- Recursive case: employees under managers
    SELECT e.id, e.name, e.manager_id, t.level + 1
    FROM employees e
    INNER JOIN org_tree t ON e.manager_id = t.id
)
SELECT * FROM org_tree ORDER BY level, name;

-- With path tracking
WITH RECURSIVE category_path AS (
    SELECT id, name, parent_id, name::text as path
    FROM categories
    WHERE parent_id IS NULL

    UNION ALL

    SELECT c.id, c.name, c.parent_id, cp.path || ' > ' || c.name
    FROM categories c
    INNER JOIN category_path cp ON c.parent_id = cp.id
)
SELECT * FROM category_path;
```

### Multiple CTEs

```sql
WITH
monthly_sales AS (
    SELECT
        DATE_TRUNC('month', order_date) as month,
        SUM(total) as revenue
    FROM orders
    GROUP BY 1
),
monthly_costs AS (
    SELECT
        DATE_TRUNC('month', expense_date) as month,
        SUM(amount) as costs
    FROM expenses
    GROUP BY 1
)
SELECT
    COALESCE(s.month, c.month) as month,
    COALESCE(s.revenue, 0) as revenue,
    COALESCE(c.costs, 0) as costs,
    COALESCE(s.revenue, 0) - COALESCE(c.costs, 0) as profit
FROM monthly_sales s
FULL OUTER JOIN monthly_costs c ON s.month = c.month
ORDER BY month;
```

---

## 2. Window Functions

### Ranking Functions

```sql
-- ROW_NUMBER, RANK, DENSE_RANK comparison
SELECT
    product_name,
    category,
    price,
    ROW_NUMBER() OVER (PARTITION BY category ORDER BY price DESC) as row_num,
    RANK() OVER (PARTITION BY category ORDER BY price DESC) as rank,
    DENSE_RANK() OVER (PARTITION BY category ORDER BY price DESC) as dense_rank
FROM products;

-- Top N per group
WITH ranked AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY category ORDER BY sales DESC) as rn
    FROM products
)
SELECT * FROM ranked WHERE rn <= 3;
```

### Running Calculations

```sql
-- Running total
SELECT
    order_date,
    amount,
    SUM(amount) OVER (ORDER BY order_date) as running_total,
    AVG(amount) OVER (ORDER BY order_date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as rolling_7day_avg
FROM orders;

-- Month-over-month change
SELECT
    month,
    revenue,
    LAG(revenue) OVER (ORDER BY month) as prev_month,
    revenue - LAG(revenue) OVER (ORDER BY month) as change,
    ROUND(100.0 * (revenue - LAG(revenue) OVER (ORDER BY month)) /
          NULLIF(LAG(revenue) OVER (ORDER BY month), 0), 2) as pct_change
FROM monthly_revenue;
```

### Percentiles and Distribution

```sql
-- Percentiles
SELECT
    category,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY price) as median_price,
    PERCENTILE_CONT(0.9) WITHIN GROUP (ORDER BY price) as p90_price,
    PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY price) as p99_price
FROM products
GROUP BY category;

-- NTILE for bucketing
SELECT
    customer_id,
    total_spent,
    NTILE(4) OVER (ORDER BY total_spent DESC) as spending_quartile
FROM customer_stats;
```

---

## 3. JSONB Operations

{% if focus == "jsonb" %}

### Basic Operations

```sql
-- Create table with JSONB
CREATE TABLE events (
    id SERIAL PRIMARY KEY,
    event_type TEXT,
    data JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Insert JSON
INSERT INTO events (event_type, data)
VALUES (
    'purchase',
    '{"user_id": 123, "items": [{"sku": "ABC", "qty": 2}], "total": 99.99}'
);

-- Access fields
SELECT
    data->>'user_id' as user_id,           -- text
    (data->>'total')::numeric as total,     -- cast to numeric
    data->'items'->0->>'sku' as first_sku,  -- nested access
    data->'items' as items_array            -- JSONB array
FROM events;
```

### Querying JSONB

```sql
-- Filter by JSON field
SELECT * FROM events
WHERE data->>'user_id' = '123';

-- Contains operator
SELECT * FROM events
WHERE data @> '{"event_type": "purchase"}';

-- Key exists
SELECT * FROM events
WHERE data ? 'discount_code';

-- Any key exists
SELECT * FROM events
WHERE data ?| array['discount_code', 'promo_id'];
```

### JSONB Indexing

```sql
-- GIN index for general queries
CREATE INDEX idx_events_data ON events USING GIN (data);

-- Specific path index
CREATE INDEX idx_events_user ON events ((data->>'user_id'));

-- Expression index for computed values
CREATE INDEX idx_events_total ON events (((data->>'total')::numeric));
```

### JSONB Aggregation

```sql
-- Build JSON object from rows
SELECT jsonb_build_object(
    'user_id', user_id,
    'orders', jsonb_agg(
        jsonb_build_object('id', order_id, 'total', total)
    )
)
FROM orders
GROUP BY user_id;

-- Expand JSONB array to rows
SELECT
    e.id,
    item->>'sku' as sku,
    (item->>'qty')::int as quantity
FROM events e,
     jsonb_array_elements(e.data->'items') as item;
```

{% endif %}

---

## 4. Full-Text Search

```sql
-- Create tsvector column
ALTER TABLE articles ADD COLUMN search_vector tsvector;

UPDATE articles SET search_vector =
    setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(body, '')), 'B');

-- Create GIN index
CREATE INDEX idx_articles_search ON articles USING GIN(search_vector);

-- Search query
SELECT
    title,
    ts_rank(search_vector, query) as rank
FROM articles,
     to_tsquery('english', 'postgresql & performance') query
WHERE search_vector @@ query
ORDER BY rank DESC
LIMIT 10;

-- With highlights
SELECT
    title,
    ts_headline('english', body, to_tsquery('postgresql & performance'),
                'StartSel=<b>, StopSel=</b>, MaxWords=50') as snippet
FROM articles
WHERE search_vector @@ to_tsquery('postgresql & performance');
```

---

## 5. Table Partitioning

```sql
-- Create partitioned table (by range)
CREATE TABLE measurements (
    id SERIAL,
    sensor_id INT,
    measured_at TIMESTAMP NOT NULL,
    value NUMERIC
) PARTITION BY RANGE (measured_at);

-- Create partitions
CREATE TABLE measurements_2024_01
    PARTITION OF measurements
    FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');

CREATE TABLE measurements_2024_02
    PARTITION OF measurements
    FOR VALUES FROM ('2024-02-01') TO ('2024-03-01');

-- Auto-create partitions (with pg_partman extension)
-- Or create them programmatically

-- Hash partitioning (for load distribution)
CREATE TABLE orders (
    id SERIAL,
    customer_id INT,
    order_date DATE
) PARTITION BY HASH (customer_id);

CREATE TABLE orders_0 PARTITION OF orders FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE orders_1 PARTITION OF orders FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE orders_2 PARTITION OF orders FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE orders_3 PARTITION OF orders FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

---

## 6. Performance Tuning

{% if focus == "performance" %}

### Query Analysis

```sql
-- Detailed explain
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT)
SELECT * FROM orders WHERE customer_id = 123;

-- Timing and memory
EXPLAIN (ANALYZE, TIMING, BUFFERS, MEMORY)
SELECT * FROM large_table WHERE created_at > '2024-01-01';
```

### Index Strategies

```sql
-- Partial index (index subset of rows)
CREATE INDEX idx_active_orders ON orders(customer_id)
WHERE status = 'active';

-- Covering index (include extra columns)
CREATE INDEX idx_orders_covering ON orders(customer_id)
INCLUDE (order_date, total);

-- Expression index
CREATE INDEX idx_orders_year ON orders(EXTRACT(YEAR FROM order_date));

-- Multi-column index (column order matters!)
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date DESC);
```

### Configuration Tuning

```sql
-- Check current settings
SHOW shared_buffers;
SHOW work_mem;
SHOW effective_cache_size;

-- Recommended settings (adjust for your hardware)
-- shared_buffers = 25% of RAM (max ~8GB)
-- effective_cache_size = 75% of RAM
-- work_mem = RAM / max_connections / 4 (for sorting)
-- maintenance_work_mem = 512MB-2GB (for VACUUM, CREATE INDEX)
```

### Identifying Slow Queries

```sql
-- Enable pg_stat_statements extension
CREATE EXTENSION pg_stat_statements;

-- Top queries by total time
SELECT
    query,
    calls,
    ROUND(total_exec_time::numeric, 2) as total_ms,
    ROUND(mean_exec_time::numeric, 2) as avg_ms,
    rows
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;

-- Queries with high row counts vs returned
SELECT
    query,
    calls,
    rows,
    ROUND(100.0 * shared_blks_hit / NULLIF(shared_blks_hit + shared_blks_read, 0), 2) as cache_hit_ratio
FROM pg_stat_statements
ORDER BY shared_blks_read DESC
LIMIT 20;
```

{% endif %}

---

## 7. Useful Patterns

### Upsert (INSERT ... ON CONFLICT)

```sql
INSERT INTO inventory (product_id, quantity, updated_at)
VALUES (123, 10, NOW())
ON CONFLICT (product_id) DO UPDATE SET
    quantity = inventory.quantity + EXCLUDED.quantity,
    updated_at = NOW();
```

### Batch Updates with FROM

```sql
-- Update from another table
UPDATE orders o
SET status = 'shipped',
    shipped_at = s.ship_date
FROM shipments s
WHERE s.order_id = o.id
  AND s.status = 'delivered';
```

### Generate Series

```sql
-- Date range
SELECT generate_series(
    '2024-01-01'::date,
    '2024-12-31'::date,
    '1 day'::interval
) as date;

-- Fill in missing dates
SELECT
    d.date,
    COALESCE(o.count, 0) as order_count
FROM generate_series('2024-01-01', '2024-01-31', '1 day') d(date)
LEFT JOIN (
    SELECT DATE(order_date) as date, COUNT(*) as count
    FROM orders
    GROUP BY 1
) o ON o.date = d.date;
```

---

## Quick Reference

### Data Types Cheatsheet

| Type | Use Case |
|------|----------|
| `SERIAL` | Auto-increment IDs |
| `UUID` | Distributed IDs |
| `TIMESTAMP WITH TIME ZONE` | Always for timestamps |
| `NUMERIC(p,s)` | Money, precise decimals |
| `JSONB` | Semi-structured data |
| `TEXT[]` | Arrays |
| `INET` | IP addresses |

### Common Functions

```sql
-- String
CONCAT(a, b), COALESCE(a, 'default'), NULLIF(a, '')

-- Date
NOW(), CURRENT_DATE, DATE_TRUNC('month', ts), EXTRACT(YEAR FROM ts)

-- JSON
jsonb_build_object(), jsonb_agg(), jsonb_array_elements()

-- Array
array_agg(), unnest(), array_length(), ANY(array)
```

---

## Related Skills

- `sql-optimization` - General SQL optimization
- `data-modeling` - Schema design
- `database-migrations` - Schema changes

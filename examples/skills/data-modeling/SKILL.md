---
name: data-modeling
description: |
  Data modeling patterns for transactional and analytical systems. Covers
  normalization, dimensional modeling, star/snowflake schemas, slowly changing
  dimensions, and modern approaches like Data Vault.
version: 1.0.0
tags: [data, modeling, schema, dimensional, warehouse, star-schema]
category: data/modeling
trigger_phrases:
  - "data model"
  - "schema design"
  - "dimensional modeling"
  - "star schema"
  - "snowflake schema"
  - "normalization"
  - "data warehouse"
  - "SCD"
  - "slowly changing"
variables:
  system_type:
    type: string
    description: Target system type
    enum: [oltp, olap, hybrid]
    default: olap
---

# Data Modeling Guide

## Core Philosophy

**Model for your queries.** OLTP systems optimize for writes (normalize). OLAP systems optimize for reads (denormalize). Know your access patterns first.

> "A data model is a contract between the data producer and consumer."

---

## Modeling Approaches

| Approach | Best For | Pros | Cons |
|----------|----------|------|------|
| **3NF (Normalized)** | OLTP | Data integrity, less redundancy | Complex queries |
| **Star Schema** | Analytics | Simple queries, fast reads | Redundancy |
| **Snowflake** | Large dims | Less redundancy than star | More joins |
| **Data Vault** | Enterprise DW | Auditability, flexibility | Complexity |
| **One Big Table** | Simple analytics | No joins | Data quality risk |

---

## 1. OLTP: Normalization

{% if system_type == "oltp" %}

### Normal Forms

**1NF**: No repeating groups, atomic values
```sql
-- BAD (not 1NF)
CREATE TABLE orders (
  id INT,
  products TEXT  -- "Product1, Product2, Product3"
);

-- GOOD (1NF)
CREATE TABLE orders (id INT PRIMARY KEY);
CREATE TABLE order_items (
  order_id INT REFERENCES orders(id),
  product_id INT,
  quantity INT
);
```

**2NF**: 1NF + no partial dependencies
```sql
-- BAD (not 2NF) - product_name depends only on product_id
CREATE TABLE order_items (
  order_id INT,
  product_id INT,
  product_name TEXT,  -- Partial dependency!
  quantity INT,
  PRIMARY KEY (order_id, product_id)
);

-- GOOD (2NF)
CREATE TABLE products (
  id INT PRIMARY KEY,
  name TEXT
);
CREATE TABLE order_items (
  order_id INT,
  product_id INT REFERENCES products(id),
  quantity INT,
  PRIMARY KEY (order_id, product_id)
);
```

**3NF**: 2NF + no transitive dependencies
```sql
-- BAD (not 3NF) - city depends on zip, not directly on customer
CREATE TABLE customers (
  id INT PRIMARY KEY,
  name TEXT,
  zip_code TEXT,
  city TEXT  -- Transitive dependency!
);

-- GOOD (3NF)
CREATE TABLE zip_codes (
  zip TEXT PRIMARY KEY,
  city TEXT
);
CREATE TABLE customers (
  id INT PRIMARY KEY,
  name TEXT,
  zip_code TEXT REFERENCES zip_codes(zip)
);
```

### When to Denormalize

Even in OLTP, strategic denormalization helps:

```sql
-- Add computed column for frequent queries
ALTER TABLE orders ADD COLUMN total_amount DECIMAL
  GENERATED ALWAYS AS (
    SELECT SUM(quantity * price) FROM order_items WHERE order_id = orders.id
  ) STORED;

-- Or use a trigger to maintain
CREATE TRIGGER update_order_total
AFTER INSERT OR UPDATE ON order_items
FOR EACH ROW EXECUTE FUNCTION recalculate_order_total();
```

{% endif %}

---

## 2. OLAP: Dimensional Modeling

{% if system_type == "olap" or system_type == "hybrid" %}

### Star Schema

```
              ┌──────────────┐
              │  dim_date    │
              └──────┬───────┘
                     │
┌──────────────┐     │     ┌──────────────┐
│ dim_customer │─────┼─────│ dim_product  │
└──────────────┘     │     └──────────────┘
                     │
              ┌──────┴───────┐
              │  fact_sales  │
              └──────────────┘
```

```sql
-- Dimension tables (descriptive)
CREATE TABLE dim_customer (
  customer_key SERIAL PRIMARY KEY,  -- Surrogate key
  customer_id INT,                   -- Natural key
  name TEXT,
  email TEXT,
  segment TEXT,
  -- SCD fields
  valid_from DATE,
  valid_to DATE,
  is_current BOOLEAN
);

CREATE TABLE dim_product (
  product_key SERIAL PRIMARY KEY,
  product_id INT,
  name TEXT,
  category TEXT,
  subcategory TEXT,
  brand TEXT
);

CREATE TABLE dim_date (
  date_key INT PRIMARY KEY,  -- YYYYMMDD format
  date DATE,
  year INT,
  quarter INT,
  month INT,
  month_name TEXT,
  day INT,
  day_of_week INT,
  day_name TEXT,
  is_weekend BOOLEAN,
  is_holiday BOOLEAN
);

-- Fact table (measurable events)
CREATE TABLE fact_sales (
  sale_key SERIAL PRIMARY KEY,
  date_key INT REFERENCES dim_date(date_key),
  customer_key INT REFERENCES dim_customer(customer_key),
  product_key INT REFERENCES dim_product(product_key),
  -- Measures
  quantity INT,
  unit_price DECIMAL(10,2),
  total_amount DECIMAL(10,2),
  discount_amount DECIMAL(10,2)
);
```

### Fact Table Types

| Type | Description | Example |
|------|-------------|---------|
| **Transaction** | One row per event | Sales, clicks |
| **Periodic Snapshot** | State at regular intervals | Daily inventory |
| **Accumulating Snapshot** | Lifecycle milestones | Order fulfillment |
| **Factless** | Events without measures | Student attendance |

```sql
-- Accumulating snapshot: Order lifecycle
CREATE TABLE fact_order_lifecycle (
  order_key INT PRIMARY KEY,
  customer_key INT,
  order_date_key INT,
  ship_date_key INT,      -- NULL until shipped
  delivery_date_key INT,  -- NULL until delivered
  return_date_key INT,    -- NULL unless returned
  order_amount DECIMAL,
  days_to_ship INT,       -- Calculated when shipped
  days_to_deliver INT     -- Calculated when delivered
);
```

### Slowly Changing Dimensions (SCD)

**Type 1**: Overwrite (lose history)
```sql
UPDATE dim_customer
SET segment = 'Enterprise'
WHERE customer_id = 123;
```

**Type 2**: Add new row (keep full history)
```sql
-- Close current record
UPDATE dim_customer
SET valid_to = CURRENT_DATE, is_current = FALSE
WHERE customer_id = 123 AND is_current = TRUE;

-- Insert new record
INSERT INTO dim_customer (customer_id, name, segment, valid_from, valid_to, is_current)
VALUES (123, 'Acme Corp', 'Enterprise', CURRENT_DATE, '9999-12-31', TRUE);
```

**Type 3**: Add column (limited history)
```sql
ALTER TABLE dim_customer ADD COLUMN previous_segment TEXT;

UPDATE dim_customer
SET previous_segment = segment,
    segment = 'Enterprise'
WHERE customer_id = 123;
```

{% endif %}

---

## 3. Date Dimension

Essential for any analytics:

```sql
-- Generate date dimension
INSERT INTO dim_date
SELECT
  TO_CHAR(d, 'YYYYMMDD')::INT as date_key,
  d as date,
  EXTRACT(YEAR FROM d) as year,
  EXTRACT(QUARTER FROM d) as quarter,
  EXTRACT(MONTH FROM d) as month,
  TO_CHAR(d, 'Month') as month_name,
  EXTRACT(DAY FROM d) as day,
  EXTRACT(DOW FROM d) as day_of_week,
  TO_CHAR(d, 'Day') as day_name,
  EXTRACT(DOW FROM d) IN (0, 6) as is_weekend,
  FALSE as is_holiday  -- Update separately
FROM generate_series('2020-01-01'::date, '2030-12-31'::date, '1 day') as d;
```

### Fiscal Calendar Support

```sql
ALTER TABLE dim_date ADD COLUMN
  fiscal_year INT,
  fiscal_quarter INT,
  fiscal_month INT;

-- Example: FY starts in July
UPDATE dim_date
SET
  fiscal_year = CASE WHEN month >= 7 THEN year + 1 ELSE year END,
  fiscal_quarter = CASE
    WHEN month IN (7,8,9) THEN 1
    WHEN month IN (10,11,12) THEN 2
    WHEN month IN (1,2,3) THEN 3
    ELSE 4
  END;
```

---

## 4. Common Patterns

### Junk Dimension

Group low-cardinality flags into one dimension:

```sql
-- Instead of many boolean columns in fact
-- BAD
CREATE TABLE fact_sales (
  is_online BOOLEAN,
  is_promotion BOOLEAN,
  is_gift BOOLEAN,
  ...
);

-- GOOD: Junk dimension
CREATE TABLE dim_sale_flags (
  flag_key INT PRIMARY KEY,
  is_online BOOLEAN,
  is_promotion BOOLEAN,
  is_gift BOOLEAN
);
-- Pre-populate all combinations (2^3 = 8 rows)

CREATE TABLE fact_sales (
  flag_key INT REFERENCES dim_sale_flags(flag_key),
  ...
);
```

### Degenerate Dimension

Business key stored in fact (no separate dimension):

```sql
CREATE TABLE fact_sales (
  sale_key SERIAL PRIMARY KEY,
  invoice_number TEXT,  -- Degenerate dimension (no lookup needed)
  ...
);
```

### Role-Playing Dimension

Same dimension used multiple times:

```sql
CREATE TABLE fact_flights (
  flight_key SERIAL PRIMARY KEY,
  departure_date_key INT REFERENCES dim_date(date_key),
  arrival_date_key INT REFERENCES dim_date(date_key),
  ...
);

-- In queries, alias the dimension
SELECT *
FROM fact_flights f
JOIN dim_date dep ON f.departure_date_key = dep.date_key
JOIN dim_date arr ON f.arrival_date_key = arr.date_key;
```

### Bridge Table (Many-to-Many)

```sql
-- Customers can belong to multiple segments over time
CREATE TABLE bridge_customer_segment (
  customer_key INT,
  segment_key INT,
  weight DECIMAL DEFAULT 1.0,  -- For proportional allocation
  PRIMARY KEY (customer_key, segment_key)
);

-- Query with bridge
SELECT segment, SUM(sales * weight)
FROM fact_sales f
JOIN bridge_customer_segment b ON f.customer_key = b.customer_key
JOIN dim_segment s ON b.segment_key = s.segment_key
GROUP BY segment;
```

---

## 5. Modern Approaches

### Wide Tables (One Big Table)

Simple but powerful for many analytics use cases:

```sql
CREATE TABLE analytics_events (
  event_id UUID PRIMARY KEY,
  event_timestamp TIMESTAMP,
  event_type TEXT,
  -- User context (denormalized)
  user_id TEXT,
  user_email TEXT,
  user_segment TEXT,
  user_created_at TIMESTAMP,
  -- Session context
  session_id TEXT,
  device_type TEXT,
  browser TEXT,
  -- Event-specific (JSONB for flexibility)
  properties JSONB
);
```

### Activity Schema

Flexible modeling for event data:

```sql
CREATE TABLE activities (
  activity_id UUID PRIMARY KEY,
  activity_ts TIMESTAMP,
  entity_type TEXT,      -- 'user', 'order', 'product'
  entity_id TEXT,
  activity_type TEXT,    -- 'viewed', 'purchased', 'returned'
  attributes JSONB
);

-- Query: User's purchase history
SELECT * FROM activities
WHERE entity_type = 'user'
  AND entity_id = '123'
  AND activity_type = 'purchased';
```

---

## Quick Reference

### Choosing a Model

```
┌─────────────────────────────────────────┐
│ What's your primary use case?           │
├─────────────────────────────────────────┤
│ ├── OLTP (transactions)                 │
│ │   └── 3NF Normalized                  │
│ │                                       │
│ ├── OLAP (analytics)                    │
│ │   ├── Simple queries → Star Schema    │
│ │   ├── Large dims → Snowflake          │
│ │   └── Need history → Data Vault       │
│ │                                       │
│ └── Event data                          │
│     ├── Known schema → Wide table       │
│     └── Flexible → Activity schema      │
└─────────────────────────────────────────┘
```

### Naming Conventions

| Element | Convention | Example |
|---------|------------|---------|
| Dimension | `dim_` prefix | `dim_customer` |
| Fact | `fact_` prefix | `fact_sales` |
| Bridge | `bridge_` prefix | `bridge_customer_segment` |
| Surrogate key | `_key` suffix | `customer_key` |
| Natural key | `_id` suffix | `customer_id` |

---

## Related Skills

- `sql-optimization` - Query performance
- `data-pipelines` - Loading data into models
- `dbt-patterns` - Modeling with dbt

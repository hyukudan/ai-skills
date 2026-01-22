---
name: pandas-data-analysis
description: |
  Decision frameworks for pandas operations. When to use groupby vs pivot_table,
  merge vs concat, apply vs vectorized. Focus on choosing the right approach.
version: 2.0.0
tags: [python, pandas, data-analysis, dataframe, data-cleaning]
category: data/analysis
variables:
  focus:
    type: string
    description: Primary focus area
    enum: [cleaning, transformation, aggregation, performance]
    default: cleaning
  data_size:
    type: string
    description: Dataset size affects approach
    enum: [small, medium, large]
    default: medium
scope:
  triggers:
    - pandas
    - dataframe
    - data cleaning
    - data wrangling
    - groupby
    - merge dataframes
---

# Pandas Data Analysis

You help choose the right pandas approach for data tasks.

## Decision Framework

```
TASK → SIZE CHECK → METHOD SELECTION → VALIDATION

Small (<100K rows)  → Any approach works, optimize for readability
Medium (100K-10M)   → Choose vectorized, avoid apply()
Large (>10M rows)   → Consider chunking or Polars/SQL
```

---

## When to Use What

| Task | Use This | Not This | Why |
|------|----------|----------|-----|
| Row-wise math | `df['a'] + df['b']` | `df.apply(lambda...)` | 100x faster vectorized |
| Conditional column | `np.where()` or `np.select()` | `df.apply(if/else)` | Vectorized |
| String operations | `.str.method()` | `apply(str_func)` | Optimized C code |
| Group summaries | `groupby().agg()` | Loop over groups | Native optimization |
| Reshape wide→long | `melt()` | Manual loop | Purpose-built |
| Reshape long→wide | `pivot_table()` | Nested loops | Handles aggregation |
| Combine datasets | `merge()` for keys, `concat()` for stacking | Manual alignment | Index-aware |

---

{% if focus == "cleaning" %}
## Data Cleaning Decisions

### Missing Values: Fill vs Drop

```
MISSING DATA DECISION:

< 5% missing → Fill with median/mode (numeric) or "Unknown" (categorical)
5-20% missing → Fill with group statistics or model imputation
> 20% missing → Consider dropping column or flagging as separate category
Random pattern → Safe to fill
Systematic pattern → Investigate cause before filling
```

**Fill Strategy Selection:**

| Data Type | Pattern | Best Fill |
|-----------|---------|-----------|
| Numeric, normal dist | Random | Mean |
| Numeric, skewed | Random | Median |
| Numeric, time series | Sequential | Forward fill |
| Categorical | Random | Mode or "Missing" category |
| Categorical | Grouped | Group mode via `transform` |

```python
# Group-aware fill (better than global mean)
df['value'] = df.groupby('category')['value'].transform(
    lambda x: x.fillna(x.median())
)
```

### Duplicates: Which to Keep

```
DUPLICATE DECISION:

Exact duplicates → Keep first (or last if data is append-only)
Partial duplicates (same key, different values):
  - Most recent timestamp → keep='last'
  - Most complete record → Sort by null count first
  - Aggregate values → groupby().agg() instead of drop_duplicates
```

### Type Coercion Failures

```python
# Safe conversion with error handling
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')  # Bad → NaN
df['date'] = pd.to_datetime(df['date'], errors='coerce')

# THEN investigate what failed
failed = df[df['amount'].isna() & df['amount_original'].notna()]
```

### Outlier Handling

| Method | Use When | Threshold |
|--------|----------|-----------|
| IQR | Unknown distribution | 1.5×IQR (mild), 3×IQR (extreme) |
| Z-score | Normal distribution | \|z\| > 3 |
| Domain rules | Known constraints | Business-specific |
| Winsorize | Keep rows, cap values | 1st/99th percentile |

{% elif focus == "transformation" %}
## Transformation Decisions

### Conditional Columns

```
CONDITIONS DECISION:

2 outcomes → np.where(condition, true_val, false_val)
3+ outcomes → np.select([cond1, cond2], [val1, val2], default)
Complex logic → Define function, use vectorized operations inside
Lookup table → df['col'].map(dict) or merge with lookup df
```

**Performance comparison:**
```python
# FAST: np.select for multiple conditions
df['tier'] = np.select(
    [df['amount'] > 10000, df['amount'] > 1000],
    ['gold', 'silver'],
    default='bronze'
)

# SLOW: apply with if/else (avoid for >10K rows)
df['tier'] = df['amount'].apply(lambda x: 'gold' if x > 10000 else ...)
```

### Reshaping: Pivot vs Melt vs Stack

```
RESHAPE DECISION:

Long → Wide (values become columns):
  - With aggregation needed → pivot_table()
  - No aggregation, unique index → pivot()
  - Multi-level index → unstack()

Wide → Long (columns become values):
  - Column names to rows → melt()
  - Multi-level columns → stack()
```

| Start Shape | End Shape | Use |
|-------------|-----------|-----|
| One row per (date, product) | Products as columns | `pivot_table` |
| Quarters as columns (Q1-Q4) | One row per quarter | `melt` |
| Hierarchical columns | Flat with multi-index | `stack` |

### Time Series Operations

```
TIME OPERATION DECISION:

Fixed calendar periods → resample('M'/'W'/'D')
Rolling calculations → rolling(window=n)
Expanding from start → expanding()
Comparisons to prior period → shift(n)
```

**Common patterns:**
```python
# Month-over-month change
df['mom_change'] = df.groupby('product')['sales'].pct_change()

# Rolling 7-day average
df['rolling_avg'] = df.groupby('product')['sales'].transform(
    lambda x: x.rolling(7, min_periods=1).mean()
)

# Year-to-date cumulative
df['ytd'] = df.groupby([df['date'].dt.year, 'product'])['sales'].cumsum()
```

{% elif focus == "aggregation" %}
## Aggregation Decisions

### GroupBy vs Pivot Table

```
AGGREGATION DECISION:

Results as rows → groupby().agg()
Results as matrix (row/column headers) → pivot_table()
Need original rows with group stats → groupby().transform()
Filter groups by condition → groupby().filter()
```

| Need | Method | Returns |
|------|--------|---------|
| Sum by category | `groupby('cat')['val'].sum()` | Series |
| Multiple stats | `groupby('cat').agg({'val': ['sum', 'mean']})` | DataFrame |
| Category × Region matrix | `pivot_table(index='cat', columns='region')` | Wide DataFrame |
| Add group total to each row | `groupby('cat')['val'].transform('sum')` | Series (same length) |

### Named Aggregations (Preferred)

```python
# Clear, explicit output column names
result = df.groupby('category').agg(
    total_sales=('sales', 'sum'),
    avg_order=('order_value', 'mean'),
    unique_customers=('customer_id', 'nunique'),
    first_order=('date', 'min'),
)
```

### Custom Aggregations

```python
# Weighted average (can't use built-in)
def weighted_avg(group):
    return (group['value'] * group['weight']).sum() / group['weight'].sum()

df.groupby('category').apply(weighted_avg, include_groups=False)

# Multiple custom in one pass
df.groupby('category')['value'].agg([
    ('range', lambda x: x.max() - x.min()),
    ('cv', lambda x: x.std() / x.mean()),  # Coefficient of variation
])
```

### Transform vs Apply vs Agg

```
GROUPBY METHOD DECISION:

agg() → Reduce groups to summary (one row per group)
transform() → Broadcast result back to original shape
apply() → Flexible but slower, use for complex multi-column logic
filter() → Keep/drop entire groups based on condition
```

{% elif focus == "performance" %}
## Performance Decisions

{% if data_size == "large" %}
### Large Dataset Strategy (>10M rows)

```
LARGE DATA DECISION TREE:

Can SQL do it? → Use SQL (pandas for final formatting only)
One-time analysis? → Chunked processing
Repeated analysis? → Consider Polars or DuckDB
Memory constrained? → dtype optimization + chunking
```

**Chunked aggregation pattern:**
```python
def chunked_groupby(filepath, groupby_cols, agg_dict, chunksize=500000):
    """Memory-efficient grouped aggregation."""
    partial_results = []

    for chunk in pd.read_csv(filepath, chunksize=chunksize):
        partial = chunk.groupby(groupby_cols).agg(agg_dict)
        partial_results.append(partial)

    # Re-aggregate partials
    combined = pd.concat(partial_results)
    return combined.groupby(level=groupby_cols).sum()  # Adjust agg as needed
```

{% endif %}

### Vectorization Rules

```
VECTORIZATION DECISION:

Built-in operation exists? → Use it (sum, mean, str.contains, etc.)
Element-wise math? → Use operators directly: df['a'] + df['b']
Conditional logic? → np.where / np.select
Need apply()? → Write vectorized logic inside if possible
```

**Speed comparison (1M rows):**

| Approach | Time |
|----------|------|
| `df['a'] + df['b']` | ~5ms |
| `df.apply(lambda r: r['a'] + r['b'], axis=1)` | ~30s |
| `[row['a'] + row['b'] for _, row in df.iterrows()]` | ~60s |

### Memory Optimization

```python
# Automatic dtype optimization
def optimize_dtypes(df):
    for col in df.select_dtypes(include=['int64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='integer')
    for col in df.select_dtypes(include=['float64']).columns:
        df[col] = pd.to_numeric(df[col], downcast='float')
    for col in df.select_dtypes(include=['object']).columns:
        if df[col].nunique() / len(df) < 0.5:  # Low cardinality
            df[col] = df[col].astype('category')
    return df
```

### Query Optimization

```
FILTER DECISION:

Simple condition → Boolean indexing: df[df['a'] > 5]
Complex conditions → query(): df.query('a > 5 and b < 10')
Multiple values → isin(): df[df['status'].isin(['A', 'B', 'C'])]
```

{% endif %}

---

## Merge vs Concat vs Join

```
COMBINING DATA DECISION:

Same columns, stack rows → concat([df1, df2])
Same rows, add columns → concat([df1, df2], axis=1)
Match on key columns → merge(df1, df2, on='key')
Match on index → df1.join(df2)
```

| Scenario | Method | Key Param |
|----------|--------|-----------|
| Append new records | `concat` | `ignore_index=True` |
| Add lookup values | `merge` | `how='left'` |
| Many-to-many relationship | `merge` | Validate with `validate='m:m'` |
| Debug missing matches | `merge` | `indicator=True` |

---

## Common Antipatterns

| Antipattern | Problem | Fix |
|-------------|---------|-----|
| `for idx, row in df.iterrows()` | 1000x slower than vectorized | Use vectorized operations |
| `df['new'] = df.apply(lambda...)` | Slow for row-wise | `np.where` or vectorized |
| `df = df.append(row)` | O(n) per append | Collect in list, concat once |
| Chained indexing `df['a']['b']` | May create copy | `df.loc[:, ('a', 'b')]` |
| `df[df['a'] == x]['b'] = y` | SettingWithCopyWarning | `df.loc[df['a'] == x, 'b'] = y` |
| Global fillna before groupby | Loses group patterns | Fill within groups |

---

## When NOT to Use Pandas

| Situation | Better Alternative |
|-----------|-------------------|
| >50M rows, complex transforms | Polars, DuckDB, or SQL |
| Production data pipelines | SQL or Spark |
| Real-time processing | Native Python or specialized tools |
| Simple CSV to database | Direct SQL COPY |
| Already in SQL database | Query there, pandas for final format |

---

## Related Skills

- `sql-optimization` - When SQL is better than pandas
- `polars-guide` - Faster alternative for large data

---
name: pandas-data-analysis
description: |
  Essential pandas patterns for data analysis. Covers data loading, cleaning,
  transformation, aggregation, merging, and performance optimization with
  practical examples for common data tasks.
version: 1.0.0
tags: [python, pandas, data-analysis, dataframe, data-cleaning]
category: data/analysis
trigger_phrases:
  - "pandas"
  - "dataframe"
  - "data cleaning"
  - "data wrangling"
  - "data analysis"
  - "CSV processing"
  - "merge dataframes"
  - "groupby"
variables:
  focus:
    type: string
    description: Primary focus area
    enum: [cleaning, transformation, aggregation, performance]
    default: cleaning
---

# Pandas Data Analysis Guide

## Core Philosophy

**DataFrames are for exploration, not production.** Use pandas for analysis and prototyping. For production pipelines, consider Polars or SQL.

> "If you're writing loops over DataFrame rows, you're doing it wrong."

---

## Quick Reference

```python
import pandas as pd
import numpy as np

# Essential operations
df.head()           # First 5 rows
df.info()           # Column types and nulls
df.describe()       # Statistical summary
df.shape            # (rows, columns)
df.dtypes           # Column data types
df.isnull().sum()   # Null count per column
df.nunique()        # Unique values per column
```

---

## 1. Data Loading

### Reading Files

```python
# CSV with common options
df = pd.read_csv(
    'data.csv',
    parse_dates=['date_column'],
    dtype={'id': str, 'amount': float},
    usecols=['id', 'date_column', 'amount'],  # Only load needed columns
    nrows=1000,  # For testing
    na_values=['', 'NA', 'null', '-'],
)

# Large files: chunked reading
chunks = pd.read_csv('large.csv', chunksize=10000)
for chunk in chunks:
    process(chunk)

# Excel
df = pd.read_excel('data.xlsx', sheet_name='Sheet1')

# JSON
df = pd.read_json('data.json', orient='records')

# SQL
from sqlalchemy import create_engine
engine = create_engine('postgresql://user:pass@host/db')
df = pd.read_sql('SELECT * FROM users', engine)
```

### Memory Optimization on Load

```python
# Downcast numeric types
df = pd.read_csv('data.csv')
df['int_col'] = pd.to_numeric(df['int_col'], downcast='integer')
df['float_col'] = pd.to_numeric(df['float_col'], downcast='float')

# Use categories for low-cardinality strings
df['status'] = df['status'].astype('category')

# Check memory usage
print(df.memory_usage(deep=True) / 1e6)  # MB per column
```

---

## 2. Data Cleaning

{% if focus == "cleaning" %}

### Handling Missing Values

```python
# Find missing
df.isnull().sum()
df[df['column'].isnull()]  # Rows with nulls

# Fill strategies
df['col'].fillna(0)                    # Constant
df['col'].fillna(df['col'].mean())     # Mean
df['col'].fillna(df['col'].median())   # Median
df['col'].fillna(method='ffill')       # Forward fill
df['col'].fillna(method='bfill')       # Backward fill

# Fill with group mean
df['col'] = df.groupby('category')['col'].transform(
    lambda x: x.fillna(x.mean())
)

# Drop rows/columns with nulls
df.dropna()                           # Any null
df.dropna(subset=['important_col'])   # Null in specific column
df.dropna(thresh=3)                   # Keep rows with at least 3 non-null
```

### Handling Duplicates

```python
# Find duplicates
df.duplicated().sum()
df[df.duplicated(subset=['id'], keep=False)]  # Show all duplicates

# Remove duplicates
df.drop_duplicates()
df.drop_duplicates(subset=['id'], keep='first')
df.drop_duplicates(subset=['id'], keep='last')
```

### Type Conversion

```python
# String to numeric
df['amount'] = pd.to_numeric(df['amount'], errors='coerce')  # Invalid → NaN

# String to datetime
df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')

# Fix mixed types
df['col'] = df['col'].astype(str).str.strip()

# Boolean conversion
df['flag'] = df['flag'].map({'yes': True, 'no': False, 'Y': True, 'N': False})
```

### String Cleaning

```python
# Access string methods via .str
df['name'] = df['name'].str.strip()
df['name'] = df['name'].str.lower()
df['name'] = df['name'].str.replace(r'\s+', ' ', regex=True)

# Extract patterns
df['area_code'] = df['phone'].str.extract(r'\((\d{3})\)')

# Split into columns
df[['first', 'last']] = df['name'].str.split(' ', n=1, expand=True)
```

### Outlier Detection

```python
# IQR method
Q1 = df['value'].quantile(0.25)
Q3 = df['value'].quantile(0.75)
IQR = Q3 - Q1
mask = (df['value'] >= Q1 - 1.5*IQR) & (df['value'] <= Q3 + 1.5*IQR)
df_clean = df[mask]

# Z-score method
from scipy import stats
df['zscore'] = stats.zscore(df['value'])
df_clean = df[df['zscore'].abs() <= 3]
```

{% endif %}

---

## 3. Data Transformation

{% if focus == "transformation" %}

### Column Operations

```python
# Create new column
df['total'] = df['quantity'] * df['price']

# Conditional column
df['size'] = np.where(df['amount'] > 1000, 'large', 'small')

# Multiple conditions
df['tier'] = np.select(
    [df['amount'] > 10000, df['amount'] > 1000, df['amount'] > 0],
    ['platinum', 'gold', 'silver'],
    default='bronze'
)

# Apply function
df['clean_name'] = df['name'].apply(lambda x: x.strip().title())

# Map values
df['status_code'] = df['status'].map({'active': 1, 'inactive': 0})
```

### Reshaping Data

```python
# Pivot: rows to columns
pivot = df.pivot(index='date', columns='product', values='sales')

# Pivot table with aggregation
pivot = pd.pivot_table(
    df,
    index='region',
    columns='quarter',
    values='sales',
    aggfunc='sum',
    fill_value=0
)

# Melt: columns to rows
melted = pd.melt(
    df,
    id_vars=['id', 'name'],
    value_vars=['q1', 'q2', 'q3', 'q4'],
    var_name='quarter',
    value_name='sales'
)

# Stack/Unstack
stacked = df.set_index(['category', 'subcategory']).stack()
unstacked = stacked.unstack()
```

### Date Operations

```python
# Extract date parts
df['year'] = df['date'].dt.year
df['month'] = df['date'].dt.month
df['day_of_week'] = df['date'].dt.dayofweek
df['is_weekend'] = df['date'].dt.dayofweek >= 5

# Date arithmetic
df['days_since'] = (pd.Timestamp.now() - df['date']).dt.days

# Resample time series
daily = df.set_index('date').resample('D').sum()
monthly = df.set_index('date').resample('M').agg({
    'sales': 'sum',
    'customers': 'nunique'
})

# Rolling windows
df['rolling_avg'] = df['value'].rolling(window=7).mean()
df['rolling_sum'] = df['value'].rolling(window=30).sum()
```

### Window Functions

```python
# Rank within groups
df['rank'] = df.groupby('category')['sales'].rank(ascending=False)

# Cumulative operations
df['cumsum'] = df.groupby('category')['sales'].cumsum()
df['pct_of_total'] = df['sales'] / df.groupby('category')['sales'].transform('sum')

# Lag/Lead
df['prev_value'] = df.groupby('id')['value'].shift(1)
df['next_value'] = df.groupby('id')['value'].shift(-1)
df['change'] = df['value'] - df['prev_value']
```

{% endif %}

---

## 4. Aggregation

{% if focus == "aggregation" %}

### GroupBy Basics

```python
# Single aggregation
df.groupby('category')['sales'].sum()

# Multiple aggregations
df.groupby('category')['sales'].agg(['sum', 'mean', 'count'])

# Different aggregations per column
df.groupby('category').agg({
    'sales': 'sum',
    'quantity': 'mean',
    'customer_id': 'nunique'
})

# Named aggregations (cleaner output)
df.groupby('category').agg(
    total_sales=('sales', 'sum'),
    avg_quantity=('quantity', 'mean'),
    unique_customers=('customer_id', 'nunique')
)
```

### Multi-Level GroupBy

```python
# Group by multiple columns
df.groupby(['category', 'region']).agg({
    'sales': 'sum'
}).reset_index()

# Unstack for pivot-like result
df.groupby(['category', 'region'])['sales'].sum().unstack(fill_value=0)
```

### Custom Aggregations

```python
# Custom function
def range_func(x):
    return x.max() - x.min()

df.groupby('category')['value'].agg(range_func)

# Multiple custom functions
df.groupby('category')['value'].agg([
    ('range', lambda x: x.max() - x.min()),
    ('cv', lambda x: x.std() / x.mean()),  # Coefficient of variation
])

# Apply with multiple columns
def weighted_avg(group):
    return (group['value'] * group['weight']).sum() / group['weight'].sum()

df.groupby('category').apply(weighted_avg)
```

### Filter Groups

```python
# Keep groups meeting condition
df.groupby('category').filter(lambda x: x['sales'].sum() > 10000)

# Transform (broadcast back to original shape)
df['category_total'] = df.groupby('category')['sales'].transform('sum')
df['pct_of_category'] = df['sales'] / df['category_total']
```

{% endif %}

---

## 5. Merging Data

### Join Types

```python
# Inner join (only matching rows)
merged = pd.merge(df1, df2, on='id', how='inner')

# Left join (all from left, matching from right)
merged = pd.merge(df1, df2, on='id', how='left')

# Full outer join (all rows)
merged = pd.merge(df1, df2, on='id', how='outer')

# Different column names
merged = pd.merge(
    df1, df2,
    left_on='customer_id',
    right_on='id',
    how='left'
)

# Multiple keys
merged = pd.merge(df1, df2, on=['id', 'date'], how='left')
```

### Handling Duplicates in Merge

```python
# Validate merge (raises error if not 1:1)
merged = pd.merge(df1, df2, on='id', validate='one_to_one')

# Indicator for debugging
merged = pd.merge(df1, df2, on='id', how='outer', indicator=True)
# _merge column: 'left_only', 'right_only', 'both'
```

### Concatenation

```python
# Vertical stack
combined = pd.concat([df1, df2], ignore_index=True)

# Horizontal stack
combined = pd.concat([df1, df2], axis=1)

# With keys for source tracking
combined = pd.concat([df1, df2], keys=['source1', 'source2'])
```

---

## 6. Performance Optimization

{% if focus == "performance" %}

### Vectorized Operations

```python
# BAD: Looping
result = []
for idx, row in df.iterrows():
    result.append(row['a'] + row['b'])
df['sum'] = result

# GOOD: Vectorized
df['sum'] = df['a'] + df['b']

# BAD: Apply with Python function
df['result'] = df['value'].apply(lambda x: x ** 2 + 2 * x + 1)

# GOOD: Vectorized
df['result'] = df['value'] ** 2 + 2 * df['value'] + 1
```

### Memory Optimization

```python
def optimize_dtypes(df):
    """Reduce memory by optimizing dtypes."""
    for col in df.columns:
        col_type = df[col].dtype

        if col_type == 'object':
            # Check if can be category
            if df[col].nunique() / len(df) < 0.5:
                df[col] = df[col].astype('category')
        elif col_type == 'float64':
            df[col] = pd.to_numeric(df[col], downcast='float')
        elif col_type == 'int64':
            df[col] = pd.to_numeric(df[col], downcast='integer')

    return df

# Before/after comparison
print(f"Before: {df.memory_usage(deep=True).sum() / 1e6:.2f} MB")
df = optimize_dtypes(df)
print(f"After: {df.memory_usage(deep=True).sum() / 1e6:.2f} MB")
```

### Query Optimization

```python
# Use query() for complex filters (faster for large DataFrames)
df.query('age > 30 and status == "active"')

# Use isin() instead of multiple OR conditions
df[df['status'].isin(['active', 'pending', 'review'])]

# Boolean indexing is fast
mask = (df['a'] > 5) & (df['b'] < 10)
df[mask]
```

### Chunked Processing

```python
def process_large_file(filepath, chunksize=100000):
    """Process large file in chunks."""
    results = []

    for chunk in pd.read_csv(filepath, chunksize=chunksize):
        # Process each chunk
        processed = chunk.groupby('category')['value'].sum()
        results.append(processed)

    # Combine results
    return pd.concat(results).groupby(level=0).sum()
```

{% endif %}

---

## Quick Reference

### Common Operations Cheatsheet

| Task | Code |
|------|------|
| Select columns | `df[['a', 'b']]` |
| Filter rows | `df[df['a'] > 5]` |
| Sort | `df.sort_values('a', ascending=False)` |
| Rename columns | `df.rename(columns={'old': 'new'})` |
| Drop columns | `df.drop(columns=['a', 'b'])` |
| Reset index | `df.reset_index(drop=True)` |
| Set index | `df.set_index('id')` |
| Value counts | `df['col'].value_counts()` |
| Cross-tab | `pd.crosstab(df['a'], df['b'])` |

### Method Chaining

```python
# Clean style with method chaining
result = (
    df
    .query('status == "active"')
    .assign(total=lambda x: x['price'] * x['quantity'])
    .groupby('category')
    .agg(total_sales=('total', 'sum'))
    .sort_values('total_sales', ascending=False)
    .head(10)
)
```

---

## Related Skills

- `sql-optimization` - When SQL is better than pandas
- `data-visualization` - Visualizing pandas DataFrames
- `polars-guide` - Faster alternative to pandas

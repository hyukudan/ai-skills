---
name: data-pipelines
description: |
  Data pipeline patterns for ETL/ELT workflows. Covers Airflow, dbt, batch vs streaming,
  data quality checks, incremental loading, and pipeline orchestration best practices.
version: 1.0.0
tags: [data, etl, elt, airflow, dbt, pipelines, orchestration]
category: data/pipelines
trigger_phrases:
  - "data pipeline"
  - "ETL"
  - "ELT"
  - "Airflow"
  - "dbt"
  - "data ingestion"
  - "batch processing"
  - "data orchestration"
  - "incremental load"
variables:
  tool:
    type: string
    description: Primary pipeline tool
    enum: [airflow, dbt, prefect, dagster]
    default: airflow
  pattern:
    type: string
    description: Pipeline pattern
    enum: [batch, streaming, hybrid]
    default: batch
---

# Data Pipelines Guide

## Core Philosophy

**ELT over ETL when possible.** Load raw data first, transform in the warehouse. It's cheaper, more flexible, and easier to debug.

> "The best pipeline is the one you don't have to maintain at 3 AM."

---

## Pipeline Patterns

```
ETL (Traditional):
Source → Extract → Transform → Load → Target

ELT (Modern):
Source → Extract → Load → Transform (in warehouse) → Serve
```

| Pattern | Best For | Tools |
|---------|----------|-------|
| **ETL** | Complex transforms, legacy systems | Airflow, Luigi |
| **ELT** | Cloud warehouses, analytics | dbt, Airflow + dbt |
| **Streaming** | Real-time, events | Kafka, Flink, Spark |
| **Hybrid** | Mixed requirements | Combination |

---

## 1. Airflow Basics

{% if tool == "airflow" %}

### DAG Structure

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from datetime import timedelta

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'email_on_failure': True,
    'email': ['alerts@company.com'],
    'retries': 3,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id='daily_sales_pipeline',
    default_args=default_args,
    description='Daily sales data processing',
    schedule_interval='0 6 * * *',  # 6 AM daily
    start_date=days_ago(1),
    catchup=False,
    tags=['sales', 'daily'],
) as dag:

    extract = PythonOperator(
        task_id='extract_sales_data',
        python_callable=extract_sales,
    )

    transform = PythonOperator(
        task_id='transform_sales_data',
        python_callable=transform_sales,
    )

    load = PythonOperator(
        task_id='load_to_warehouse',
        python_callable=load_to_warehouse,
    )

    # Define dependencies
    extract >> transform >> load
```

### Task Dependencies

```python
# Linear
task1 >> task2 >> task3

# Parallel then converge
[task1, task2] >> task3

# Fan out
task1 >> [task2, task3, task4]

# Complex
task1 >> task2
task1 >> task3
[task2, task3] >> task4
```

### Passing Data Between Tasks

```python
from airflow.operators.python import PythonOperator

def extract(**context):
    """Extract data and push to XCom."""
    data = fetch_from_api()
    # Push to XCom (small data only!)
    context['ti'].xcom_push(key='record_count', value=len(data))
    return data  # Also pushed as return value

def transform(**context):
    """Pull data from XCom."""
    # Pull from specific task
    data = context['ti'].xcom_pull(task_ids='extract')
    count = context['ti'].xcom_pull(task_ids='extract', key='record_count')
    return process(data)

extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract,
    provide_context=True,
)

transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform,
    provide_context=True,
)
```

### Sensors

```python
from airflow.sensors.filesystem import FileSensor
from airflow.sensors.sql import SqlSensor
from airflow.sensors.external_task import ExternalTaskSensor

# Wait for file
wait_for_file = FileSensor(
    task_id='wait_for_file',
    filepath='/data/input/sales_{{ ds }}.csv',
    poke_interval=60,  # Check every 60 seconds
    timeout=3600,      # Timeout after 1 hour
    mode='poke',       # or 'reschedule' for long waits
)

# Wait for database condition
wait_for_data = SqlSensor(
    task_id='wait_for_data',
    conn_id='postgres_conn',
    sql="SELECT COUNT(*) FROM staging WHERE date = '{{ ds }}'",
    success=lambda x: x[0][0] > 0,
)

# Wait for another DAG
wait_for_upstream = ExternalTaskSensor(
    task_id='wait_for_upstream',
    external_dag_id='upstream_dag',
    external_task_id='final_task',
    execution_delta=timedelta(hours=1),
)
```

### Dynamic Task Generation

```python
from airflow.utils.task_group import TaskGroup

# Process multiple tables dynamically
tables = ['users', 'orders', 'products']

with DAG(...) as dag:
    with TaskGroup('process_tables') as process_group:
        for table in tables:
            PythonOperator(
                task_id=f'process_{table}',
                python_callable=process_table,
                op_kwargs={'table': table},
            )

    start >> process_group >> end
```

{% endif %}

---

## 2. dbt Patterns

{% if tool == "dbt" %}

### Project Structure

```
dbt_project/
├── dbt_project.yml
├── models/
│   ├── staging/           # Raw data cleaning
│   │   ├── stg_orders.sql
│   │   └── stg_customers.sql
│   ├── intermediate/      # Business logic
│   │   └── int_orders_enriched.sql
│   └── marts/             # Final tables
│       ├── dim_customers.sql
│       └── fct_orders.sql
├── tests/
│   └── assert_positive_amounts.sql
└── macros/
    └── generate_schema_name.sql
```

### Model Example

```sql
-- models/staging/stg_orders.sql
{{ config(
    materialized='view',
    tags=['staging', 'daily']
) }}

WITH source AS (
    SELECT * FROM {{ source('raw', 'orders') }}
),

cleaned AS (
    SELECT
        id AS order_id,
        customer_id,
        CAST(order_date AS DATE) AS order_date,
        CAST(amount AS DECIMAL(10, 2)) AS order_amount,
        status,
        _loaded_at
    FROM source
    WHERE id IS NOT NULL
)

SELECT * FROM cleaned
```

### Incremental Models

```sql
-- models/marts/fct_orders.sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge'
) }}

SELECT
    o.order_id,
    o.customer_id,
    c.customer_name,
    o.order_date,
    o.order_amount,
    o.status
FROM {{ ref('stg_orders') }} o
LEFT JOIN {{ ref('dim_customers') }} c
    ON o.customer_id = c.customer_id

{% if is_incremental() %}
WHERE o._loaded_at > (SELECT MAX(_loaded_at) FROM {{ this }})
{% endif %}
```

### Tests

```yaml
# models/schema.yml
version: 2

models:
  - name: fct_orders
    description: "Fact table for orders"
    columns:
      - name: order_id
        tests:
          - unique
          - not_null
      - name: order_amount
        tests:
          - not_null
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 1000000
      - name: customer_id
        tests:
          - relationships:
              to: ref('dim_customers')
              field: customer_id
```

### Macros

```sql
-- macros/cents_to_dollars.sql
{% macro cents_to_dollars(column_name) %}
    ROUND({{ column_name }} / 100.0, 2)
{% endmacro %}

-- Usage in model
SELECT
    order_id,
    {{ cents_to_dollars('amount_cents') }} AS amount_dollars
FROM {{ ref('stg_orders') }}
```

{% endif %}

---

## 3. Incremental Loading Patterns

### Timestamp-Based

```python
def incremental_load(source_table: str, target_table: str, conn):
    """Load only new/updated records."""

    # Get last loaded timestamp
    last_loaded = conn.execute(f"""
        SELECT COALESCE(MAX(updated_at), '1900-01-01')
        FROM {target_table}
    """).scalar()

    # Extract new records
    new_records = conn.execute(f"""
        SELECT * FROM {source_table}
        WHERE updated_at > '{last_loaded}'
    """)

    # Upsert to target
    conn.execute(f"""
        INSERT INTO {target_table}
        SELECT * FROM staging
        ON CONFLICT (id) DO UPDATE SET
            updated_at = EXCLUDED.updated_at,
            -- ... other columns
    """)
```

### Change Data Capture (CDC)

```python
# Using Debezium-style CDC
def process_cdc_event(event: dict):
    """Process CDC event from Kafka."""
    operation = event['op']  # c=create, u=update, d=delete
    before = event.get('before')
    after = event.get('after')

    if operation == 'c':
        insert_record(after)
    elif operation == 'u':
        update_record(after['id'], after)
    elif operation == 'd':
        soft_delete_record(before['id'])
```

### Partition-Based

```sql
-- Load by date partition
INSERT INTO warehouse.orders
PARTITION (order_date = '{{ ds }}')
SELECT * FROM staging.orders
WHERE order_date = '{{ ds }}';

-- Replace partition (idempotent)
INSERT OVERWRITE TABLE warehouse.orders
PARTITION (order_date = '{{ ds }}')
SELECT * FROM staging.orders
WHERE order_date = '{{ ds }}';
```

---

## 4. Data Quality Checks

### Schema Validation

```python
from pydantic import BaseModel, validator
from typing import Optional
from datetime import date

class OrderRecord(BaseModel):
    """Validate order records."""
    order_id: str
    customer_id: str
    order_date: date
    amount: float
    status: str

    @validator('amount')
    def amount_positive(cls, v):
        if v < 0:
            raise ValueError('Amount must be positive')
        return v

    @validator('status')
    def valid_status(cls, v):
        valid = ['pending', 'completed', 'cancelled']
        if v not in valid:
            raise ValueError(f'Status must be one of {valid}')
        return v

def validate_batch(records: list[dict]) -> tuple[list, list]:
    """Validate batch, return valid and invalid records."""
    valid, invalid = [], []
    for record in records:
        try:
            validated = OrderRecord(**record)
            valid.append(validated.dict())
        except Exception as e:
            invalid.append({'record': record, 'error': str(e)})
    return valid, invalid
```

### Great Expectations

```python
import great_expectations as gx

# Create expectation suite
context = gx.get_context()

validator = context.sources.pandas_default.read_csv("orders.csv")

# Add expectations
validator.expect_column_to_exist("order_id")
validator.expect_column_values_to_not_be_null("order_id")
validator.expect_column_values_to_be_unique("order_id")
validator.expect_column_values_to_be_between("amount", min_value=0)
validator.expect_column_values_to_be_in_set(
    "status",
    ["pending", "completed", "cancelled"]
)

# Validate
results = validator.validate()
if not results.success:
    raise DataQualityError(results)
```

### Row Count Checks

```python
def check_row_counts(source_count: int, target_count: int, tolerance: float = 0.01):
    """Verify row counts match within tolerance."""
    if source_count == 0:
        raise ValueError("Source has no records")

    diff_pct = abs(source_count - target_count) / source_count

    if diff_pct > tolerance:
        raise ValueError(
            f"Row count mismatch: source={source_count}, "
            f"target={target_count}, diff={diff_pct:.2%}"
        )
```

---

## 5. Error Handling

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)
def load_to_warehouse(data):
    """Load with automatic retry."""
    conn = get_connection()
    conn.execute("INSERT INTO target SELECT * FROM staging")
```

### Dead Letter Queue

```python
def process_with_dlq(records: list, dlq_table: str):
    """Process records, send failures to dead letter queue."""
    for record in records:
        try:
            process_record(record)
        except Exception as e:
            # Send to DLQ for manual review
            conn.execute(f"""
                INSERT INTO {dlq_table} (record, error, timestamp)
                VALUES (%s, %s, NOW())
            """, [json.dumps(record), str(e)])
```

### Idempotency

```python
def idempotent_load(batch_id: str, data: list):
    """Idempotent load using batch tracking."""

    # Check if already processed
    if is_batch_processed(batch_id):
        logger.info(f"Batch {batch_id} already processed, skipping")
        return

    try:
        # Process in transaction
        with db.transaction():
            load_data(data)
            mark_batch_processed(batch_id)
    except Exception:
        # Transaction rolls back, can safely retry
        raise
```

---

## 6. Monitoring

### Pipeline Metrics

```python
import time
from dataclasses import dataclass
from typing import Optional

@dataclass
class PipelineMetrics:
    pipeline_name: str
    run_id: str
    start_time: float
    end_time: Optional[float] = None
    records_processed: int = 0
    records_failed: int = 0
    status: str = "running"

    @property
    def duration_seconds(self) -> float:
        end = self.end_time or time.time()
        return end - self.start_time

    def to_dict(self) -> dict:
        return {
            "pipeline": self.pipeline_name,
            "run_id": self.run_id,
            "duration_s": self.duration_seconds,
            "records_processed": self.records_processed,
            "records_failed": self.records_failed,
            "status": self.status,
        }

# Usage
metrics = PipelineMetrics(
    pipeline_name="daily_orders",
    run_id=str(uuid.uuid4()),
    start_time=time.time()
)

try:
    records = extract_data()
    metrics.records_processed = len(records)
    load_data(records)
    metrics.status = "success"
except Exception as e:
    metrics.status = "failed"
    raise
finally:
    metrics.end_time = time.time()
    send_to_monitoring(metrics.to_dict())
```

### Alerting

```python
def alert_on_failure(pipeline_name: str, error: Exception):
    """Send alert on pipeline failure."""
    message = f"""
    Pipeline Failed: {pipeline_name}
    Time: {datetime.now()}
    Error: {str(error)}

    Check logs for details.
    """

    # Slack
    requests.post(SLACK_WEBHOOK, json={"text": message})

    # PagerDuty (critical pipelines)
    if is_critical_pipeline(pipeline_name):
        trigger_pagerduty(pipeline_name, error)
```

---

## Quick Reference

### Scheduling Cron Expressions

| Expression | Meaning |
|------------|---------|
| `0 * * * *` | Every hour |
| `0 6 * * *` | 6 AM daily |
| `0 0 * * 0` | Midnight Sunday |
| `0 0 1 * *` | First of month |
| `*/15 * * * *` | Every 15 minutes |

### Pipeline Checklist

- [ ] Idempotent (safe to retry)
- [ ] Incremental (not full reload)
- [ ] Data quality checks
- [ ] Logging and metrics
- [ ] Alerting on failure
- [ ] Documented dependencies
- [ ] Tested with sample data
- [ ] Handles schema changes

---

## Related Skills

- `sql-optimization` - Optimizing SQL transforms
- `data-modeling` - Schema design for pipelines
- `airflow-advanced` - Advanced Airflow patterns

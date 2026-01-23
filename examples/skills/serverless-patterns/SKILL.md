---
name: serverless-patterns
description: |
  Serverless architecture patterns and best practices. Covers Lambda optimization,
  event-driven design, API patterns, cold starts, and production-ready serverless
  applications across AWS, GCP, and Azure.
license: MIT
allowed-tools: Read Edit Bash
version: 1.0.0
tags: [serverless, lambda, cloud-functions, api-gateway, event-driven]
category: cloud/serverless
trigger_phrases:
  - "serverless"
  - "Lambda"
  - "Cloud Functions"
  - "Azure Functions"
  - "cold start"
  - "event-driven"
  - "FaaS"
variables:
  provider:
    type: string
    description: Cloud provider
    enum: [aws, gcp, azure]
    default: aws
---

# Serverless Patterns Guide

## Core Philosophy

**Pay for what you use, scale to zero.** Serverless removes server management but adds complexity in other areas. Understand the trade-offs.

> "Serverless is not about no servers—it's about no server management."

---

## When Serverless Works Well

| Good Fit | Poor Fit |
|----------|----------|
| Variable/unpredictable load | Constant high load |
| Event-driven workloads | Long-running processes |
| APIs with bursty traffic | Real-time with strict latency |
| Batch processing | Stateful applications |
| Rapid prototyping | Complex orchestration |

---

## 1. Function Design Patterns

### Single-Purpose Functions

```python
# GOOD: One function, one job
def process_order(event, context):
    """Process a single order."""
    order = parse_event(event)
    validate_order(order)
    save_to_database(order)
    return success_response(order.id)

# BAD: God function
def handle_everything(event, context):
    """Does too many things."""
    if event['type'] == 'order':
        # 100 lines of order logic
    elif event['type'] == 'user':
        # 100 lines of user logic
    elif event['type'] == 'payment':
        # 100 lines of payment logic
```

### Handler Pattern

```python
# handler.py - Keep handler thin
import json
from service import OrderService

def lambda_handler(event, context):
    """Thin handler delegates to service layer."""
    try:
        body = json.loads(event.get('body', '{}'))
        service = OrderService()
        result = service.create_order(body)
        return {
            'statusCode': 201,
            'body': json.dumps(result)
        }
    except ValidationError as e:
        return {'statusCode': 400, 'body': json.dumps({'error': str(e)})}
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': 'Internal error'})}

# service.py - Business logic here
class OrderService:
    def __init__(self):
        self.db = get_database_connection()

    def create_order(self, data: dict) -> dict:
        """Create order with all business logic."""
        self.validate(data)
        order = Order.from_dict(data)
        self.db.save(order)
        return order.to_dict()
```

### Dependency Injection for Testing

```python
# Testable function design
class OrderHandler:
    def __init__(self, db=None, event_bus=None):
        self.db = db or DynamoDBClient()
        self.event_bus = event_bus or EventBridge()

    def handle(self, event, context):
        order = self.db.get_order(event['order_id'])
        order.process()
        self.db.save(order)
        self.event_bus.publish('order.processed', order)
        return order

# In Lambda
handler_instance = OrderHandler()
lambda_handler = handler_instance.handle

# In tests
def test_order_processing():
    mock_db = MockDatabase()
    mock_events = MockEventBus()
    handler = OrderHandler(db=mock_db, event_bus=mock_events)

    result = handler.handle({'order_id': '123'}, None)

    assert result.status == 'processed'
    assert mock_events.published[0]['type'] == 'order.processed'
```

---

## 2. Cold Start Optimization

### Understanding Cold Starts

```
Cold Start Timeline:
├── Download code (~100-500ms)
├── Start runtime (~100-200ms)
├── Initialize dependencies (~100-2000ms)  ← Your code
└── Execute handler (~10-100ms)

Warm Invocation:
└── Execute handler (~10-100ms)
```

### Optimization Strategies

```python
# 1. Move initialization outside handler
import boto3

# Initialized ONCE per container (cold start)
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('orders')

def lambda_handler(event, context):
    # Uses pre-initialized client (warm)
    return table.get_item(Key={'id': event['id']})


# 2. Lazy loading for rarely-used dependencies
_heavy_client = None

def get_heavy_client():
    global _heavy_client
    if _heavy_client is None:
        _heavy_client = HeavyClient()  # Only loaded when needed
    return _heavy_client


# 3. Minimize deployment package
# requirements.txt - only what you need
boto3  # Often pre-installed in Lambda
requests
# NOT: pandas, numpy (unless required)


# 4. Use Lambda Layers for shared dependencies
# Layer structure:
# python/
#   └── lib/
#       └── python3.11/
#           └── site-packages/
#               └── my_package/
```

### Provisioned Concurrency

```bash
# Keep functions warm
aws lambda put-provisioned-concurrency-config \
  --function-name my-function \
  --qualifier prod \
  --provisioned-concurrent-executions 5

# With auto-scaling
aws application-autoscaling register-scalable-target \
  --service-namespace lambda \
  --resource-id function:my-function:prod \
  --scalable-dimension lambda:function:ProvisionedConcurrency \
  --min-capacity 5 \
  --max-capacity 100
```

---

## 3. Event-Driven Patterns

### Event Source Mapping

```python
# SQS Trigger
def process_sqs_messages(event, context):
    """Process batch of SQS messages."""
    failed_ids = []

    for record in event['Records']:
        try:
            body = json.loads(record['body'])
            process_message(body)
        except Exception as e:
            # Partial batch failure
            failed_ids.append(record['messageId'])

    # Return failed items for retry
    return {
        'batchItemFailures': [
            {'itemIdentifier': msg_id} for msg_id in failed_ids
        ]
    }


# S3 Trigger
def process_s3_upload(event, context):
    """Process uploaded file."""
    for record in event['Records']:
        bucket = record['s3']['bucket']['name']
        key = record['s3']['object']['key']

        # Process file
        s3 = boto3.client('s3')
        response = s3.get_object(Bucket=bucket, Key=key)
        content = response['Body'].read()

        process_file(key, content)


# EventBridge/CloudWatch Events
def scheduled_job(event, context):
    """Run on schedule (cron)."""
    # event contains schedule details
    run_daily_report()
```

### Fan-Out Pattern

```
                    ┌──→ Lambda (process type A)
                    │
SNS Topic ──────────┼──→ Lambda (process type B)
    ↑               │
    │               └──→ SQS → Lambda (async processing)
    │
Event Source
```

```python
# Publisher
def publish_event(event_type: str, data: dict):
    """Publish to SNS for fan-out."""
    sns = boto3.client('sns')
    sns.publish(
        TopicArn='arn:aws:sns:region:account:events',
        Message=json.dumps(data),
        MessageAttributes={
            'event_type': {
                'DataType': 'String',
                'StringValue': event_type
            }
        }
    )

# Subscriber with filter
# SNS subscription filter policy:
{
    "event_type": ["order.created", "order.updated"]
}
```

### Saga Pattern (Distributed Transactions)

```python
# Step Functions state machine for saga
{
    "StartAt": "CreateOrder",
    "States": {
        "CreateOrder": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:...:create-order",
            "Next": "ProcessPayment",
            "Catch": [{
                "ErrorEquals": ["States.ALL"],
                "Next": "CompensateOrder"
            }]
        },
        "ProcessPayment": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:...:process-payment",
            "Next": "ReserveInventory",
            "Catch": [{
                "ErrorEquals": ["States.ALL"],
                "Next": "RefundPayment"
            }]
        },
        "ReserveInventory": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:...:reserve-inventory",
            "End": true,
            "Catch": [{
                "ErrorEquals": ["States.ALL"],
                "Next": "RefundPayment"
            }]
        },
        "RefundPayment": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:...:refund-payment",
            "Next": "CompensateOrder"
        },
        "CompensateOrder": {
            "Type": "Task",
            "Resource": "arn:aws:lambda:...:cancel-order",
            "End": true
        }
    }
}
```

---

## 4. API Patterns

### REST API with Lambda

```python
# Router pattern
from typing import Callable

routes: dict[tuple[str, str], Callable] = {}

def route(method: str, path: str):
    """Decorator to register routes."""
    def decorator(func):
        routes[(method, path)] = func
        return func
    return decorator

@route('GET', '/users')
def list_users(event):
    return {'users': get_all_users()}

@route('POST', '/users')
def create_user(event):
    body = json.loads(event['body'])
    user = create_new_user(body)
    return {'user': user, 'statusCode': 201}

@route('GET', '/users/{id}')
def get_user(event):
    user_id = event['pathParameters']['id']
    return {'user': get_user_by_id(user_id)}

def lambda_handler(event, context):
    method = event['httpMethod']
    path = event['resource']  # e.g., '/users/{id}'

    handler = routes.get((method, path))
    if not handler:
        return {'statusCode': 404, 'body': '{"error": "Not found"}'}

    try:
        result = handler(event)
        status = result.pop('statusCode', 200)
        return {
            'statusCode': status,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps(result)
        }
    except Exception as e:
        return {'statusCode': 500, 'body': json.dumps({'error': str(e)})}
```

### WebSocket API

```python
# Connection management
def connect_handler(event, context):
    """Handle WebSocket connect."""
    connection_id = event['requestContext']['connectionId']
    save_connection(connection_id)
    return {'statusCode': 200}

def disconnect_handler(event, context):
    """Handle WebSocket disconnect."""
    connection_id = event['requestContext']['connectionId']
    remove_connection(connection_id)
    return {'statusCode': 200}

def message_handler(event, context):
    """Handle WebSocket message."""
    connection_id = event['requestContext']['connectionId']
    body = json.loads(event['body'])

    # Broadcast to all connections
    api_gateway = boto3.client(
        'apigatewaymanagementapi',
        endpoint_url=f"https://{event['requestContext']['domainName']}/{event['requestContext']['stage']}"
    )

    for conn_id in get_all_connections():
        try:
            api_gateway.post_to_connection(
                ConnectionId=conn_id,
                Data=json.dumps({'message': body['message']})
            )
        except api_gateway.exceptions.GoneException:
            remove_connection(conn_id)

    return {'statusCode': 200}
```

---

## 5. Error Handling & Observability

### Structured Error Handling

```python
class LambdaError(Exception):
    """Base error with status code."""
    status_code = 500
    message = "Internal error"

class ValidationError(LambdaError):
    status_code = 400
    message = "Validation failed"

class NotFoundError(LambdaError):
    status_code = 404
    message = "Resource not found"

def error_handler(func):
    """Decorator for consistent error handling."""
    def wrapper(event, context):
        try:
            return func(event, context)
        except LambdaError as e:
            return {
                'statusCode': e.status_code,
                'body': json.dumps({'error': e.message, 'details': str(e)})
            }
        except Exception as e:
            # Log unexpected errors
            print(f"Unexpected error: {e}")
            return {
                'statusCode': 500,
                'body': json.dumps({'error': 'Internal server error'})
            }
    return wrapper
```

### Structured Logging

```python
import json
import logging

class JsonFormatter(logging.Formatter):
    """JSON formatter for CloudWatch."""
    def format(self, record):
        log_data = {
            'timestamp': self.formatTime(record),
            'level': record.levelname,
            'message': record.getMessage(),
            'function': record.funcName,
        }
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        return json.dumps(log_data)

logger = logging.getLogger()
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)

# Usage
logger.info('Processing order', extra={
    'order_id': '123',
    'customer_id': '456',
    'amount': 99.99
})
```

---

## Quick Reference

### Memory vs CPU

| Memory | vCPUs | Use Case |
|--------|-------|----------|
| 128 MB | 0.083 | Simple transforms |
| 512 MB | 0.333 | API handlers |
| 1024 MB | 0.583 | Data processing |
| 1769 MB | 1.0 | CPU-bound tasks |
| 10240 MB | 6.0 | Heavy computation |

### Timeout Guidelines

| Use Case | Timeout |
|----------|---------|
| API Gateway | 3-10s |
| SQS processing | 30s-5min |
| Batch processing | 5-15min |
| Step Functions | 15min max |

### Cost Formula

```
Cost = (Requests × $0.20/million) + (GB-seconds × $0.0000166667)

Example: 1M requests, 256MB, 200ms average
= (1M × $0.20/1M) + (1M × 0.256GB × 0.2s × $0.0000166667)
= $0.20 + $0.85
= $1.05/month
```

---

## Related Skills

- `aws-fundamentals` - AWS service basics
- `infrastructure-as-code` - Deploy serverless with IaC
- `event-driven-architecture` - Event design patterns

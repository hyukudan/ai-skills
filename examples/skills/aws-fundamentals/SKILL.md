---
name: aws-fundamentals
description: |
  Essential AWS services and patterns for developers. Covers EC2, S3, Lambda, IAM,
  RDS, DynamoDB, and common architectural patterns with practical examples
  and CLI commands.
license: MIT
allowed-tools: Read Edit Bash
version: 1.0.0
tags: [aws, cloud, ec2, s3, lambda, iam, devops]
category: cloud/aws
trigger_phrases:
  - "AWS"
  - "Amazon Web Services"
  - "EC2"
  - "S3"
  - "Lambda"
  - "IAM"
  - "cloud infrastructure"
  - "AWS CLI"
variables:
  focus:
    type: string
    description: Service focus area
    enum: [compute, storage, database, security]
    default: compute
---

# AWS Fundamentals Guide

## Core Philosophy

**Start simple, scale as needed.** AWS has 200+ services. You need about 10 for most applications. Master the fundamentals first.

> "The best architecture is the simplest one that meets your requirements."

---

## Essential Services Map

```
┌─────────────────────────────────────────────────────────┐
│                      COMPUTE                             │
│  EC2 (VMs) │ Lambda (Serverless) │ ECS/EKS (Containers) │
├─────────────────────────────────────────────────────────┤
│                      STORAGE                             │
│     S3 (Objects) │ EBS (Block) │ EFS (File System)      │
├─────────────────────────────────────────────────────────┤
│                      DATABASE                            │
│   RDS (SQL) │ DynamoDB (NoSQL) │ ElastiCache (Cache)    │
├─────────────────────────────────────────────────────────┤
│                      NETWORKING                          │
│  VPC │ Route 53 (DNS) │ CloudFront (CDN) │ ALB/NLB      │
├─────────────────────────────────────────────────────────┤
│                      SECURITY                            │
│   IAM │ KMS (Encryption) │ Secrets Manager │ WAF        │
└─────────────────────────────────────────────────────────┘
```

---

## 1. IAM (Identity & Access Management)

### Fundamental Concepts

| Concept | Description | Example |
|---------|-------------|---------|
| **User** | Person or app | developer@company.com |
| **Group** | Collection of users | Developers, Admins |
| **Role** | Temporary permissions | EC2 instance role |
| **Policy** | Permission rules | AllowS3Read |

### Policy Structure

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3BucketAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:PutObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-bucket",
        "arn:aws:s3:::my-bucket/*"
      ],
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "192.168.1.0/24"
        }
      }
    }
  ]
}
```

### Common IAM Patterns

```bash
# Create user
aws iam create-user --user-name developer

# Attach policy to user
aws iam attach-user-policy \
  --user-name developer \
  --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess

# Create role for EC2
aws iam create-role \
  --role-name EC2S3Access \
  --assume-role-policy-document file://trust-policy.json

# trust-policy.json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {"Service": "ec2.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }
  ]
}
```

### Least Privilege Examples

```json
// BAD: Too permissive
{
  "Effect": "Allow",
  "Action": "s3:*",
  "Resource": "*"
}

// GOOD: Specific permissions
{
  "Effect": "Allow",
  "Action": ["s3:GetObject"],
  "Resource": "arn:aws:s3:::my-app-bucket/public/*"
}
```

---

## 2. EC2 (Elastic Compute Cloud)

{% if focus == "compute" %}

### Instance Types Quick Reference

| Type | Use Case | Example |
|------|----------|---------|
| **t3** | General, burstable | Web servers, dev |
| **m6i** | Balanced | Production apps |
| **c6i** | Compute intensive | Data processing |
| **r6i** | Memory intensive | Databases, caching |
| **g4dn** | GPU | ML inference |

### Launch Instance (CLI)

```bash
# Launch EC2 instance
aws ec2 run-instances \
  --image-id ami-0c55b159cbfafe1f0 \
  --instance-type t3.micro \
  --key-name my-key \
  --security-group-ids sg-12345678 \
  --subnet-id subnet-12345678 \
  --iam-instance-profile Name=EC2S3Access \
  --tag-specifications 'ResourceType=instance,Tags=[{Key=Name,Value=my-server}]'

# Get instance public IP
aws ec2 describe-instances \
  --instance-ids i-12345678 \
  --query 'Reservations[0].Instances[0].PublicIpAddress'

# Stop/Start instance
aws ec2 stop-instances --instance-ids i-12345678
aws ec2 start-instances --instance-ids i-12345678
```

### User Data (Bootstrap Script)

```bash
#!/bin/bash
# Install and start nginx
yum update -y
yum install -y nginx
systemctl start nginx
systemctl enable nginx

# Install app dependencies
yum install -y python3 python3-pip
pip3 install flask gunicorn

# Pull app from S3
aws s3 cp s3://my-bucket/app.zip /home/ec2-user/
cd /home/ec2-user && unzip app.zip

# Start app
gunicorn --bind 0.0.0.0:8000 app:app
```

### Security Groups

```bash
# Create security group
aws ec2 create-security-group \
  --group-name web-server-sg \
  --description "Web server security group" \
  --vpc-id vpc-12345678

# Allow HTTP/HTTPS
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# Allow SSH from specific IP
aws ec2 authorize-security-group-ingress \
  --group-id sg-12345678 \
  --protocol tcp \
  --port 22 \
  --cidr 203.0.113.0/32
```

{% endif %}

---

## 3. S3 (Simple Storage Service)

{% if focus == "storage" %}

### Bucket Operations

```bash
# Create bucket
aws s3 mb s3://my-unique-bucket-name-12345

# Upload file
aws s3 cp file.txt s3://my-bucket/path/file.txt

# Upload directory
aws s3 sync ./local-dir s3://my-bucket/remote-dir

# Download file
aws s3 cp s3://my-bucket/file.txt ./local-file.txt

# List objects
aws s3 ls s3://my-bucket/path/

# Delete object
aws s3 rm s3://my-bucket/file.txt

# Delete bucket (must be empty)
aws s3 rb s3://my-bucket
```

### Bucket Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "PublicReadGetObject",
      "Effect": "Allow",
      "Principal": "*",
      "Action": "s3:GetObject",
      "Resource": "arn:aws:s3:::my-website-bucket/*"
    }
  ]
}
```

### Python SDK (boto3)

```python
import boto3

s3 = boto3.client('s3')

# Upload file
s3.upload_file('local.txt', 'my-bucket', 'remote.txt')

# Upload with metadata
s3.upload_file(
    'local.txt',
    'my-bucket',
    'remote.txt',
    ExtraArgs={
        'ContentType': 'text/plain',
        'Metadata': {'author': 'john'}
    }
)

# Generate presigned URL (temporary access)
url = s3.generate_presigned_url(
    'get_object',
    Params={'Bucket': 'my-bucket', 'Key': 'file.txt'},
    ExpiresIn=3600  # 1 hour
)

# List objects
response = s3.list_objects_v2(Bucket='my-bucket', Prefix='path/')
for obj in response.get('Contents', []):
    print(obj['Key'], obj['Size'])
```

### Storage Classes

| Class | Use Case | Retrieval |
|-------|----------|-----------|
| **Standard** | Frequent access | Instant |
| **Intelligent-Tiering** | Unknown patterns | Instant |
| **Standard-IA** | Infrequent access | Instant |
| **Glacier Instant** | Archive, quick access | Instant |
| **Glacier Flexible** | Archive | Minutes-hours |
| **Glacier Deep** | Long-term archive | Hours |

{% endif %}

---

## 4. Lambda (Serverless Compute)

### Basic Function

```python
# lambda_function.py
import json

def lambda_handler(event, context):
    """Process incoming event."""
    name = event.get('name', 'World')

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({'message': f'Hello, {name}!'})
    }
```

### Deploy with CLI

```bash
# Create deployment package
zip function.zip lambda_function.py

# Create function
aws lambda create-function \
  --function-name my-function \
  --runtime python3.11 \
  --handler lambda_function.lambda_handler \
  --role arn:aws:iam::123456789:role/lambda-role \
  --zip-file fileb://function.zip \
  --timeout 30 \
  --memory-size 256

# Update function code
aws lambda update-function-code \
  --function-name my-function \
  --zip-file fileb://function.zip

# Invoke function
aws lambda invoke \
  --function-name my-function \
  --payload '{"name": "AWS"}' \
  output.json
```

### API Gateway Integration

```python
# Lambda for API Gateway
def lambda_handler(event, context):
    # Parse request
    http_method = event['httpMethod']
    path = event['path']
    body = json.loads(event.get('body', '{}'))
    query_params = event.get('queryStringParameters', {})

    # Route handling
    if http_method == 'GET' and path == '/users':
        return get_users(query_params)
    elif http_method == 'POST' and path == '/users':
        return create_user(body)
    else:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Not found'})
        }
```

---

## 5. RDS & DynamoDB

{% if focus == "database" %}

### RDS Quick Start

```bash
# Create PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier my-postgres \
  --db-instance-class db.t3.micro \
  --engine postgres \
  --master-username admin \
  --master-user-password secretpassword \
  --allocated-storage 20 \
  --vpc-security-group-ids sg-12345678

# Get endpoint
aws rds describe-db-instances \
  --db-instance-identifier my-postgres \
  --query 'DBInstances[0].Endpoint.Address'
```

### DynamoDB Basics

```python
import boto3

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('users')

# Put item
table.put_item(Item={
    'user_id': '123',
    'email': 'user@example.com',
    'name': 'John Doe',
    'created_at': '2024-01-01'
})

# Get item
response = table.get_item(Key={'user_id': '123'})
item = response.get('Item')

# Query (needs index on sort key)
response = table.query(
    KeyConditionExpression='user_id = :uid',
    ExpressionAttributeValues={':uid': '123'}
)

# Scan (expensive, use sparingly)
response = table.scan(
    FilterExpression='contains(email, :domain)',
    ExpressionAttributeValues={':domain': '@example.com'}
)

# Update item
table.update_item(
    Key={'user_id': '123'},
    UpdateExpression='SET #n = :name, updated_at = :now',
    ExpressionAttributeNames={'#n': 'name'},
    ExpressionAttributeValues={
        ':name': 'Jane Doe',
        ':now': '2024-01-15'
    }
)
```

{% endif %}

---

## 6. Common Architectures

### Three-Tier Web App

```
Internet
    │
    ▼
┌───────────┐
│    ALB    │  (Application Load Balancer)
└─────┬─────┘
      │
      ▼
┌───────────┐
│  EC2/ECS  │  (Web/App tier in private subnet)
│  Auto     │
│  Scaling  │
└─────┬─────┘
      │
      ▼
┌───────────┐
│   RDS     │  (Database in private subnet)
│  Multi-AZ │
└───────────┘
```

### Serverless API

```
API Gateway → Lambda → DynamoDB
      │
      └──→ S3 (static files)
```

### Event-Driven

```
S3 Upload → Lambda → SQS → Lambda → DynamoDB
                 └──→ SNS (notification)
```

---

## Quick Reference

### AWS CLI Profiles

```bash
# Configure profile
aws configure --profile dev
# Enter: Access Key, Secret Key, Region, Output format

# Use profile
aws s3 ls --profile dev

# Set default profile
export AWS_PROFILE=dev
```

### Common CLI Commands

```bash
# Identity check
aws sts get-caller-identity

# List resources
aws ec2 describe-instances
aws s3 ls
aws lambda list-functions
aws rds describe-db-instances

# CloudWatch logs
aws logs tail /aws/lambda/my-function --follow
```

### Cost-Saving Tips

| Service | Tip |
|---------|-----|
| EC2 | Use Spot/Reserved for predictable workloads |
| S3 | Lifecycle policies for old objects |
| Lambda | Right-size memory allocation |
| RDS | Use Aurora Serverless for variable load |

---

## Related Skills

- `serverless-patterns` - Advanced serverless architectures
- `infrastructure-as-code` - Terraform/CloudFormation
- `cost-optimization` - Reducing AWS spend

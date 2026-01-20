---
name: cost-optimization
description: |
  Cloud cost optimization strategies and patterns. Covers AWS, GCP, and Azure
  cost analysis, right-sizing, reserved instances, spot instances, and
  FinOps best practices.
version: 1.0.0
tags: [cloud, cost, finops, optimization, aws, gcp, azure]
category: cloud/finops
trigger_phrases:
  - "cloud costs"
  - "cost optimization"
  - "reduce AWS bill"
  - "FinOps"
  - "reserved instances"
  - "spot instances"
  - "right-sizing"
  - "cloud spend"
variables:
  provider:
    type: string
    description: Cloud provider
    enum: [aws, gcp, azure, multi]
    default: aws
---

# Cloud Cost Optimization Guide

## Core Philosophy

**Optimize for value, not just cost.** The cheapest option isn't always the best. Focus on cost efficiency relative to business value.

> "The goal isn't to spend less—it's to get more value for what you spend."

---

## Cost Optimization Framework

```
┌─────────────────────────────────────────────────────────┐
│                 COST OPTIMIZATION                        │
├─────────────────────────────────────────────────────────┤
│  1. VISIBILITY     │ Know what you're spending          │
│  2. RIGHT-SIZE     │ Match resources to actual needs    │
│  3. COMMITMENT     │ Reserved/Savings Plans for steady  │
│  4. SPOT/PREEMPT   │ Interruptible for flexible work    │
│  5. ARCHITECTURE   │ Design for cost efficiency         │
│  6. GOVERNANCE     │ Policies to prevent waste          │
└─────────────────────────────────────────────────────────┘
```

---

## 1. Cost Visibility

### AWS Cost Analysis

```bash
# Enable Cost Explorer (console or CLI)
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity MONTHLY \
  --metrics "BlendedCost" "UnblendedCost" \
  --group-by Type=DIMENSION,Key=SERVICE

# Get cost by tag
aws ce get-cost-and-usage \
  --time-period Start=2024-01-01,End=2024-01-31 \
  --granularity DAILY \
  --metrics "BlendedCost" \
  --group-by Type=TAG,Key=Environment
```

### Cost Allocation Tags

```yaml
# Required tags for cost tracking
- Environment: dev/staging/prod
- Team: engineering/data/platform
- Project: project-name
- Owner: team-email
- CostCenter: department-code

# Terraform implementation
locals {
  required_tags = {
    Environment = var.environment
    Team        = var.team
    Project     = var.project
    CostCenter  = var.cost_center
    ManagedBy   = "terraform"
  }
}
```

### Budget Alerts

```bash
# Create budget with alert
aws budgets create-budget \
  --account-id 123456789012 \
  --budget '{
    "BudgetName": "Monthly-EC2",
    "BudgetLimit": {"Amount": "1000", "Unit": "USD"},
    "TimeUnit": "MONTHLY",
    "BudgetType": "COST",
    "CostFilters": {"Service": ["Amazon Elastic Compute Cloud - Compute"]}
  }' \
  --notifications-with-subscribers '[{
    "Notification": {
      "NotificationType": "ACTUAL",
      "ComparisonOperator": "GREATER_THAN",
      "Threshold": 80,
      "ThresholdType": "PERCENTAGE"
    },
    "Subscribers": [{
      "SubscriptionType": "EMAIL",
      "Address": "alerts@company.com"
    }]
  }]'
```

---

## 2. Right-Sizing

### EC2 Right-Sizing

```python
import boto3

def analyze_ec2_utilization():
    """Find underutilized EC2 instances."""
    cloudwatch = boto3.client('cloudwatch')
    ec2 = boto3.client('ec2')

    instances = ec2.describe_instances()
    recommendations = []

    for reservation in instances['Reservations']:
        for instance in reservation['Instances']:
            instance_id = instance['InstanceId']
            instance_type = instance['InstanceType']

            # Get CPU utilization (last 14 days)
            cpu_stats = cloudwatch.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                StartTime=datetime.now() - timedelta(days=14),
                EndTime=datetime.now(),
                Period=3600,
                Statistics=['Average', 'Maximum']
            )

            if cpu_stats['Datapoints']:
                avg_cpu = sum(d['Average'] for d in cpu_stats['Datapoints']) / len(cpu_stats['Datapoints'])
                max_cpu = max(d['Maximum'] for d in cpu_stats['Datapoints'])

                # Recommendation logic
                if avg_cpu < 10 and max_cpu < 30:
                    recommendations.append({
                        'instance_id': instance_id,
                        'current_type': instance_type,
                        'avg_cpu': avg_cpu,
                        'max_cpu': max_cpu,
                        'recommendation': 'Consider downsizing or terminating'
                    })
                elif avg_cpu < 20:
                    recommendations.append({
                        'instance_id': instance_id,
                        'current_type': instance_type,
                        'avg_cpu': avg_cpu,
                        'recommendation': 'Consider smaller instance type'
                    })

    return recommendations
```

### RDS Right-Sizing

```sql
-- Check connection utilization
SELECT
  COUNT(*) as active_connections,
  (SELECT setting::int FROM pg_settings WHERE name = 'max_connections') as max_connections,
  ROUND(COUNT(*) * 100.0 / (SELECT setting::int FROM pg_settings WHERE name = 'max_connections'), 2) as utilization_pct
FROM pg_stat_activity;

-- Check database size
SELECT
  datname,
  pg_size_pretty(pg_database_size(datname)) as size
FROM pg_database
ORDER BY pg_database_size(datname) DESC;
```

### Instance Type Recommendations

| Current Avg CPU | Current Max CPU | Action |
|-----------------|-----------------|--------|
| < 5% | < 20% | Terminate or downsize 2 levels |
| 5-20% | < 40% | Downsize 1 level |
| 20-60% | < 80% | Optimal |
| > 60% | > 80% | Consider upsizing |

---

## 3. Commitment Discounts

### Reserved Instances vs Savings Plans

| Feature | Reserved Instances | Savings Plans |
|---------|-------------------|---------------|
| Discount | Up to 72% | Up to 72% |
| Flexibility | Instance-specific | Any instance |
| Applies to | EC2, RDS, ElastiCache | EC2, Lambda, Fargate |
| Commitment | 1 or 3 years | 1 or 3 years |
| Best for | Stable, predictable | Variable workloads |

### Savings Plan Calculator

```python
def calculate_savings_plan_coverage(hourly_commitment: float, on_demand_hourly: float) -> dict:
    """Calculate savings plan ROI."""
    monthly_commitment = hourly_commitment * 730  # hours/month
    monthly_on_demand = on_demand_hourly * 730

    # Assume 30% average discount
    discount_rate = 0.30
    effective_coverage = monthly_commitment / (1 - discount_rate)

    savings = min(effective_coverage, monthly_on_demand) * discount_rate
    excess_commitment = max(0, effective_coverage - monthly_on_demand)

    return {
        'monthly_commitment': monthly_commitment,
        'monthly_on_demand': monthly_on_demand,
        'monthly_savings': savings,
        'excess_commitment': excess_commitment,
        'effective_discount': savings / monthly_on_demand if monthly_on_demand > 0 else 0
    }

# Example: $100/hour commitment, $150/hour actual usage
print(calculate_savings_plan_coverage(100, 150))
```

### When to Commit

```
Analyze 3+ months of steady-state usage
                │
                ▼
       Is usage predictable?
         /            \
        No            Yes
        │              │
        ▼              ▼
    Savings Plans   Reserved Instances
    (flexibility)   (max discount)
                         │
                         ▼
                  1-year or 3-year?
                   /          \
              Uncertain    Confident
                 │             │
                 ▼             ▼
             1-year         3-year
           (lower risk)   (max savings)
```

---

## 4. Spot/Preemptible Instances

### When to Use Spot

| Good For | Bad For |
|----------|---------|
| Batch processing | User-facing APIs |
| CI/CD workers | Databases |
| Data processing | Stateful services |
| Dev/test environments | Time-critical jobs |
| ML training | Single points of failure |

### Spot Best Practices

```hcl
# Terraform: Spot with fallback
resource "aws_autoscaling_group" "mixed" {
  name                = "mixed-instances"
  min_size            = 2
  max_size            = 10
  desired_capacity    = 4
  vpc_zone_identifier = var.subnet_ids

  mixed_instances_policy {
    instances_distribution {
      on_demand_base_capacity                  = 1  # Always 1 on-demand
      on_demand_percentage_above_base_capacity = 25 # 25% on-demand, 75% spot
      spot_allocation_strategy                 = "capacity-optimized"
    }

    launch_template {
      launch_template_specification {
        launch_template_id = aws_launch_template.app.id
      }

      override {
        instance_type = "m5.large"
      }
      override {
        instance_type = "m5a.large"
      }
      override {
        instance_type = "m4.large"
      }
    }
  }
}
```

### Spot Interruption Handling

```python
import requests
import time

def check_spot_interruption():
    """Check for spot instance interruption notice."""
    try:
        # EC2 metadata endpoint
        response = requests.get(
            'http://169.254.169.254/latest/meta-data/spot/instance-action',
            timeout=2
        )
        if response.status_code == 200:
            return response.json()  # {'action': 'terminate', 'time': '...'}
    except requests.exceptions.RequestException:
        pass
    return None

def graceful_shutdown():
    """Handle spot interruption gracefully."""
    # Stop accepting new work
    stop_accepting_requests()

    # Complete in-flight work
    complete_current_tasks()

    # Checkpoint state to S3/EBS
    save_checkpoint()

    # Deregister from load balancer
    deregister_from_elb()

# Monitor for interruption
while True:
    interruption = check_spot_interruption()
    if interruption:
        print(f"Spot interruption in 2 minutes: {interruption}")
        graceful_shutdown()
        break
    time.sleep(5)
```

---

## 5. Architecture Patterns

### Serverless for Variable Load

```
Before: EC2 (always on)
Cost: 24/7 × $0.10/hour = $73/month

After: Lambda (pay per use)
1M requests × 200ms × 256MB
Cost: ~$4/month

Savings: 95%
```

### Auto-Scaling Policies

```hcl
# Scale based on target tracking (recommended)
resource "aws_autoscaling_policy" "cpu" {
  name                   = "cpu-target-tracking"
  autoscaling_group_name = aws_autoscaling_group.app.name
  policy_type            = "TargetTrackingScaling"

  target_tracking_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ASGAverageCPUUtilization"
    }
    target_value = 50.0  # Target 50% CPU
  }
}

# Scheduled scaling for predictable patterns
resource "aws_autoscaling_schedule" "night" {
  scheduled_action_name  = "scale-down-night"
  autoscaling_group_name = aws_autoscaling_group.app.name
  min_size               = 1
  max_size               = 3
  desired_capacity       = 1
  recurrence             = "0 22 * * *"  # 10 PM
}

resource "aws_autoscaling_schedule" "morning" {
  scheduled_action_name  = "scale-up-morning"
  autoscaling_group_name = aws_autoscaling_group.app.name
  min_size               = 2
  max_size               = 10
  desired_capacity       = 4
  recurrence             = "0 6 * * 1-5"  # 6 AM weekdays
}
```

### Storage Tiering

```python
# S3 Lifecycle policy
lifecycle_rules = {
    'Rules': [
        {
            'ID': 'archive-old-data',
            'Status': 'Enabled',
            'Transitions': [
                {
                    'Days': 30,
                    'StorageClass': 'STANDARD_IA'  # 40% cheaper
                },
                {
                    'Days': 90,
                    'StorageClass': 'GLACIER'  # 80% cheaper
                },
                {
                    'Days': 365,
                    'StorageClass': 'DEEP_ARCHIVE'  # 95% cheaper
                }
            ],
            'Expiration': {
                'Days': 2555  # Delete after 7 years
            }
        }
    ]
}
```

---

## 6. Quick Wins

### Immediate Actions

| Action | Typical Savings | Effort |
|--------|-----------------|--------|
| Delete unused EBS volumes | 5-15% | Low |
| Terminate stopped instances | 5-10% | Low |
| Delete old snapshots | 3-8% | Low |
| Release unused Elastic IPs | 1-3% | Low |
| Delete unused load balancers | 2-5% | Low |
| Right-size RDS instances | 10-30% | Medium |
| Use Savings Plans | 20-40% | Medium |
| Implement auto-scaling | 15-30% | Medium |

### Waste Detection Script

```python
import boto3

def find_waste():
    """Find common sources of cloud waste."""
    findings = []

    ec2 = boto3.client('ec2')

    # Unused EBS volumes
    volumes = ec2.describe_volumes(
        Filters=[{'Name': 'status', 'Values': ['available']}]
    )
    for vol in volumes['Volumes']:
        findings.append({
            'type': 'unused_ebs',
            'resource': vol['VolumeId'],
            'size_gb': vol['Size'],
            'monthly_cost': vol['Size'] * 0.10  # ~$0.10/GB-month
        })

    # Unattached Elastic IPs
    addresses = ec2.describe_addresses()
    for addr in addresses['Addresses']:
        if 'InstanceId' not in addr:
            findings.append({
                'type': 'unused_eip',
                'resource': addr['PublicIp'],
                'monthly_cost': 3.60  # ~$0.005/hour
            })

    # Old snapshots (>90 days)
    snapshots = ec2.describe_snapshots(OwnerIds=['self'])
    for snap in snapshots['Snapshots']:
        age = (datetime.now(snap['StartTime'].tzinfo) - snap['StartTime']).days
        if age > 90:
            findings.append({
                'type': 'old_snapshot',
                'resource': snap['SnapshotId'],
                'age_days': age,
                'size_gb': snap['VolumeSize']
            })

    return findings
```

---

## Quick Reference

### Pricing Models Comparison

| Model | Discount | Commitment | Flexibility |
|-------|----------|------------|-------------|
| On-Demand | 0% | None | Full |
| Savings Plan | 30-40% | 1-3 years | High |
| Reserved | 40-72% | 1-3 years | Low |
| Spot | 60-90% | None | Interruptible |

### Monthly Cost Estimators

```python
# EC2 monthly cost
ec2_monthly = hourly_rate * 730  # hours/month

# Lambda monthly cost (simplified)
lambda_monthly = (
    requests * 0.20 / 1_000_000 +  # Request cost
    gb_seconds * 0.0000166667       # Compute cost
)

# S3 monthly cost
s3_monthly = (
    storage_gb * 0.023 +           # Storage
    get_requests * 0.0004 / 1000 + # GET requests
    put_requests * 0.005 / 1000    # PUT requests
)
```

---

## Related Skills

- `aws-fundamentals` - AWS service basics
- `infrastructure-as-code` - IaC for consistent deployments
- `serverless-patterns` - Cost-effective serverless

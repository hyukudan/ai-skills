---
name: infrastructure-as-code
description: |
  Infrastructure as Code (IaC) patterns and best practices. Covers Terraform,
  CloudFormation, Pulumi with practical examples for common infrastructure
  patterns, state management, and CI/CD integration.
version: 1.0.0
tags: [iac, terraform, cloudformation, pulumi, devops, infrastructure]
category: cloud/iac
trigger_phrases:
  - "infrastructure as code"
  - "IaC"
  - "Terraform"
  - "CloudFormation"
  - "Pulumi"
  - "provision infrastructure"
  - "terraform plan"
  - "terraform apply"
variables:
  tool:
    type: string
    description: IaC tool
    enum: [terraform, cloudformation, pulumi]
    default: terraform
---

# Infrastructure as Code Guide

## Core Philosophy

**Infrastructure should be versioned, reviewed, and tested like application code.** No manual changes. Everything through code.

> "If it's not in code, it doesn't exist."

---

## Tool Comparison

| Feature | Terraform | CloudFormation | Pulumi |
|---------|-----------|----------------|--------|
| Multi-cloud | Yes | AWS only | Yes |
| Language | HCL | YAML/JSON | Python/TS/Go |
| State | Remote/Local | AWS managed | Remote |
| Learning curve | Medium | Medium | Low (if you know the language) |

---

## 1. Terraform Fundamentals

{% if tool == "terraform" %}

### Project Structure

```
infrastructure/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   └── prod/
├── modules/
│   ├── vpc/
│   ├── ecs/
│   └── rds/
└── shared/
    └── backend.tf
```

### Basic Configuration

```hcl
# main.tf
terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "my-terraform-state"
    key            = "prod/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "terraform"
      Project     = var.project_name
    }
  }
}
```

### Variables and Outputs

```hcl
# variables.tf
variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "instance_config" {
  description = "EC2 instance configuration"
  type = object({
    instance_type = string
    ami_id        = string
    volume_size   = number
  })
  default = {
    instance_type = "t3.micro"
    ami_id        = "ami-0c55b159cbfafe1f0"
    volume_size   = 20
  }
}

# outputs.tf
output "vpc_id" {
  description = "ID of the created VPC"
  value       = aws_vpc.main.id
}

output "public_subnets" {
  description = "List of public subnet IDs"
  value       = aws_subnet.public[*].id
}
```

### Resources Example

```hcl
# VPC
resource "aws_vpc" "main" {
  cidr_block           = var.vpc_cidr
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "${var.project_name}-vpc"
  }
}

# Subnets with count
resource "aws_subnet" "public" {
  count                   = length(var.availability_zones)
  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(var.vpc_cidr, 8, count.index)
  availability_zone       = var.availability_zones[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project_name}-public-${count.index + 1}"
  }
}

# Using for_each
resource "aws_security_group" "services" {
  for_each = var.services

  name        = "${var.project_name}-${each.key}-sg"
  description = "Security group for ${each.key}"
  vpc_id      = aws_vpc.main.id

  dynamic "ingress" {
    for_each = each.value.ports
    content {
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
    }
  }
}
```

### Modules

```hcl
# modules/vpc/main.tf
variable "name" {
  type = string
}

variable "cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "azs" {
  type = list(string)
}

resource "aws_vpc" "this" {
  cidr_block = var.cidr
  # ...
}

output "vpc_id" {
  value = aws_vpc.this.id
}

# Using the module
module "vpc" {
  source = "../../modules/vpc"

  name = "production"
  cidr = "10.0.0.0/16"
  azs  = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

# Reference module output
resource "aws_instance" "app" {
  subnet_id = module.vpc.public_subnets[0]
  # ...
}
```

### State Management

```hcl
# Backend configuration
terraform {
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "projects/myapp/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-locks"  # For locking
    encrypt        = true
  }
}

# Initialize with backend config
# terraform init -backend-config=backend.hcl
```

```bash
# Common commands
terraform init          # Initialize, download providers
terraform plan          # Preview changes
terraform apply         # Apply changes
terraform destroy       # Destroy all resources

# With variables
terraform plan -var="environment=prod"
terraform plan -var-file="prod.tfvars"

# Target specific resource
terraform apply -target=aws_instance.app

# Import existing resource
terraform import aws_instance.app i-1234567890abcdef0

# State commands
terraform state list
terraform state show aws_instance.app
terraform state mv aws_instance.app aws_instance.web
terraform state rm aws_instance.old
```

{% endif %}

---

## 2. CloudFormation

{% if tool == "cloudformation" %}

### Template Structure

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'Production VPC and EC2 infrastructure'

Parameters:
  Environment:
    Type: String
    AllowedValues: [dev, staging, prod]
    Default: dev

  InstanceType:
    Type: String
    Default: t3.micro
    AllowedValues: [t3.micro, t3.small, t3.medium]

Conditions:
  IsProd: !Equals [!Ref Environment, prod]

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-vpc'

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      MapPublicIpOnLaunch: true
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-public-subnet'

  WebServer:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0c55b159cbfafe1f0
      InstanceType: !If [IsProd, t3.small, !Ref InstanceType]
      SubnetId: !Ref PublicSubnet
      Tags:
        - Key: Name
          Value: !Sub '${AWS::StackName}-web'

Outputs:
  VpcId:
    Description: VPC ID
    Value: !Ref VPC
    Export:
      Name: !Sub '${AWS::StackName}-VpcId'

  WebServerIP:
    Description: Web server public IP
    Value: !GetAtt WebServer.PublicIp
```

### Nested Stacks

```yaml
# Parent stack
Resources:
  NetworkStack:
    Type: AWS::CloudFormation::Stack
    Properties:
      TemplateURL: https://s3.amazonaws.com/mybucket/network.yaml
      Parameters:
        Environment: !Ref Environment

  ComputeStack:
    Type: AWS::CloudFormation::Stack
    DependsOn: NetworkStack
    Properties:
      TemplateURL: https://s3.amazonaws.com/mybucket/compute.yaml
      Parameters:
        VpcId: !GetAtt NetworkStack.Outputs.VpcId
        SubnetIds: !GetAtt NetworkStack.Outputs.SubnetIds
```

### CLI Commands

```bash
# Validate template
aws cloudformation validate-template --template-body file://template.yaml

# Create stack
aws cloudformation create-stack \
  --stack-name my-app \
  --template-body file://template.yaml \
  --parameters ParameterKey=Environment,ParameterValue=prod \
  --capabilities CAPABILITY_IAM

# Update stack
aws cloudformation update-stack \
  --stack-name my-app \
  --template-body file://template.yaml

# Delete stack
aws cloudformation delete-stack --stack-name my-app

# Create change set (preview)
aws cloudformation create-change-set \
  --stack-name my-app \
  --change-set-name my-changes \
  --template-body file://template.yaml
```

{% endif %}

---

## 3. Best Practices

### Environment Separation

```hcl
# Use workspaces OR separate state files

# Option 1: Workspaces (simpler)
# terraform workspace new dev
# terraform workspace new prod
# terraform workspace select prod

resource "aws_instance" "app" {
  instance_type = terraform.workspace == "prod" ? "t3.medium" : "t3.micro"
}

# Option 2: Separate directories (recommended for production)
# environments/
#   dev/
#     main.tf
#     terraform.tfvars
#   prod/
#     main.tf
#     terraform.tfvars
```

### Secrets Management

```hcl
# NEVER store secrets in state or code

# Option 1: AWS Secrets Manager
data "aws_secretsmanager_secret_version" "db_password" {
  secret_id = "prod/database/password"
}

resource "aws_db_instance" "main" {
  password = data.aws_secretsmanager_secret_version.db_password.secret_string
}

# Option 2: Environment variables
# export TF_VAR_db_password="secret"

variable "db_password" {
  type      = string
  sensitive = true  # Won't show in logs
}
```

### Tagging Strategy

```hcl
locals {
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "terraform"
    Owner       = var.team
    CostCenter  = var.cost_center
  }
}

resource "aws_instance" "app" {
  # ...
  tags = merge(local.common_tags, {
    Name = "${var.project_name}-app"
    Role = "application"
  })
}
```

### Prevent Accidental Destruction

```hcl
resource "aws_db_instance" "production" {
  # ...

  lifecycle {
    prevent_destroy = true  # Terraform will error on destroy
  }
}

resource "aws_instance" "app" {
  # ...

  lifecycle {
    create_before_destroy = true  # Create new before destroying old
    ignore_changes = [
      ami,  # Don't update if AMI changes
    ]
  }
}
```

---

## 4. CI/CD Integration

### GitHub Actions

```yaml
name: Terraform

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

env:
  TF_VERSION: 1.5.0
  AWS_REGION: us-east-1

jobs:
  plan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Setup Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: ${{ env.TF_VERSION }}

      - name: Terraform Init
        run: terraform init

      - name: Terraform Format Check
        run: terraform fmt -check

      - name: Terraform Plan
        run: terraform plan -out=tfplan

      - name: Upload Plan
        uses: actions/upload-artifact@v3
        with:
          name: tfplan
          path: tfplan

  apply:
    needs: plan
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    environment: production
    steps:
      - uses: actions/checkout@v3

      - name: Download Plan
        uses: actions/download-artifact@v3
        with:
          name: tfplan

      - name: Terraform Apply
        run: terraform apply -auto-approve tfplan
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/antonbabenko/pre-commit-terraform
    rev: v1.77.0
    hooks:
      - id: terraform_fmt
      - id: terraform_validate
      - id: terraform_docs
      - id: terraform_tflint
      - id: terraform_checkov
        args:
          - --args=--quiet
          - --args=--compact
```

---

## 5. Common Patterns

### Multi-Region Deployment

```hcl
# Use provider aliases
provider "aws" {
  alias  = "primary"
  region = "us-east-1"
}

provider "aws" {
  alias  = "secondary"
  region = "eu-west-1"
}

module "app_us" {
  source = "./modules/app"
  providers = {
    aws = aws.primary
  }
}

module "app_eu" {
  source = "./modules/app"
  providers = {
    aws = aws.secondary
  }
}
```

### Blue-Green Infrastructure

```hcl
variable "active_environment" {
  description = "Which environment is live (blue or green)"
  type        = string
  default     = "blue"
}

resource "aws_lb_target_group" "blue" {
  name = "app-blue"
  # ...
}

resource "aws_lb_target_group" "green" {
  name = "app-green"
  # ...
}

resource "aws_lb_listener_rule" "app" {
  # ...
  action {
    type             = "forward"
    target_group_arn = var.active_environment == "blue" ? aws_lb_target_group.blue.arn : aws_lb_target_group.green.arn
  }
}
```

---

## Quick Reference

### Terraform Commands

```bash
terraform init          # Initialize
terraform plan          # Preview
terraform apply         # Execute
terraform destroy       # Remove all
terraform fmt           # Format code
terraform validate      # Check syntax
terraform output        # Show outputs
terraform refresh       # Sync state
terraform import        # Import existing
terraform state list    # List resources
```

### Common Issues

| Issue | Solution |
|-------|----------|
| State lock stuck | `terraform force-unlock LOCK_ID` |
| Resource changed outside TF | `terraform refresh` |
| Provider version conflict | Pin versions in `required_providers` |
| Cycle dependency | Use `depends_on` explicitly |

---

## Related Skills

- `aws-fundamentals` - AWS service details
- `gitops-patterns` - GitOps with IaC
- `cost-optimization` - Optimizing cloud costs

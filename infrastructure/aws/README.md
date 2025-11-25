# AWS Infrastructure

This directory contains Terraform configurations for deploying the Arbor Energy Plan Agent to AWS.

## Architecture

```
                                    ┌─────────────────────────────────────────────────┐
                                    │                     VPC                         │
                                    │  ┌────────────────────────────────────────────┐ │
                                    │  │              Public Subnets                │ │
Internet ──► Route 53 ──► ALB ──────┼──►  (ALB, NAT Gateway)                       │ │
                         (HTTPS)    │  └────────────────────────────────────────────┘ │
                           │        │  ┌────────────────────────────────────────────┐ │
                           │        │  │             Private Subnets                │ │
                           ├────────┼──►                                            │ │
                           │        │  │  ┌─────────────┐    ┌─────────────┐       │ │
                           │        │  │  │   Backend   │    │  Frontend   │       │ │
                           │        │  │  │   (ECS)     │    │   (ECS)     │       │ │
                           │        │  │  └──────┬──────┘    └─────────────┘       │ │
                           │        │  │         │                                  │ │
                           │        │  │    ┌────┴────┐                            │ │
                           │        │  │    ▼         ▼                            │ │
                           │        │  │ ┌─────┐  ┌─────┐                          │ │
                           │        │  │ │ RDS │  │Redis│                          │ │
                           │        │  │ └─────┘  └─────┘                          │ │
                           │        │  └────────────────────────────────────────────┘ │
                                    └─────────────────────────────────────────────────┘
```

## Resources Created

| Resource | Description |
|----------|-------------|
| VPC | Virtual Private Cloud with public and private subnets |
| ALB | Application Load Balancer with HTTPS |
| ECS Cluster | Fargate cluster for running containers |
| ECR | Container registries for backend and frontend |
| RDS PostgreSQL | Managed PostgreSQL 16 database |
| ElastiCache Redis | Managed Redis 7 cache |
| Secrets Manager | Secure storage for credentials |
| CloudWatch | Logs and monitoring |
| Auto Scaling | CPU/memory-based scaling for ECS services |

## Prerequisites

1. **AWS CLI** configured with appropriate credentials
2. **Terraform** >= 1.0
3. **Domain name** with Route 53 hosted zone (optional but recommended)

## Deployment Steps

### 1. Initialize Terraform Backend

First, create the S3 bucket and DynamoDB table for Terraform state:

```bash
# Create S3 bucket for state
aws s3api create-bucket \
    --bucket arbor-terraform-state \
    --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
    --bucket arbor-terraform-state \
    --versioning-configuration Status=Enabled

# Create DynamoDB table for state locking
aws dynamodb create-table \
    --table-name terraform-locks \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --billing-mode PAY_PER_REQUEST
```

### 2. Configure Variables

```bash
cd infrastructure/aws
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your values
```

### 3. Initialize and Plan

```bash
terraform init
terraform plan
```

### 4. Apply Infrastructure

```bash
terraform apply
```

### 5. Build and Push Docker Images

```bash
# Get ECR login
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build and push backend
cd backend
docker build -f Dockerfile.prod -t arbor-backend .
docker tag arbor-backend:latest <backend-ecr-url>:latest
docker push <backend-ecr-url>:latest

# Build and push frontend
cd frontend
docker build -f Dockerfile.prod -t arbor-frontend --build-arg NEXT_PUBLIC_API_URL=https://your-domain.com .
docker tag arbor-frontend:latest <frontend-ecr-url>:latest
docker push <frontend-ecr-url>:latest
```

### 6. Run Database Migrations

```bash
# Connect to ECS and run migrations
aws ecs run-task \
    --cluster arbor-production-cluster \
    --task-definition arbor-production-backend \
    --launch-type FARGATE \
    --network-configuration "awsvpcConfiguration={subnets=[subnet-xxx],securityGroups=[sg-xxx],assignPublicIp=DISABLED}" \
    --overrides '{"containerOverrides":[{"name":"backend","command":["alembic","upgrade","head"]}]}'
```

### 7. Configure DNS (if using Route 53)

```bash
# Get ALB DNS name
terraform output alb_dns_name

# Create Route 53 record pointing to ALB
```

## Cost Estimation (Production)

| Resource | Monthly Cost (est.) |
|----------|---------------------|
| ECS Fargate (4 tasks) | ~$60 |
| RDS db.t3.medium | ~$50 |
| ElastiCache cache.t3.micro | ~$15 |
| ALB | ~$20 |
| NAT Gateway | ~$35 |
| Data Transfer | ~$10 |
| **Total** | **~$190/month** |

*Costs vary by region and usage. Use AWS Calculator for accurate estimates.*

## Staging Environment

For a lower-cost staging environment:

```hcl
# terraform.tfvars for staging
environment = "staging"

backend_desired_count  = 1
frontend_desired_count = 1
backend_min_capacity   = 1
frontend_min_capacity  = 1

db_instance_class = "db.t3.micro"
redis_node_type   = "cache.t3.micro"
```

## Destroying Infrastructure

```bash
# WARNING: This will delete all resources including databases!
terraform destroy
```

## Security Considerations

- All traffic is encrypted in transit (TLS 1.3)
- Database and Redis are in private subnets
- Credentials stored in Secrets Manager
- Security groups follow principle of least privilege
- RDS deletion protection enabled in production

## Troubleshooting

### ECS Tasks Not Starting

```bash
# Check task logs
aws logs get-log-events \
    --log-group-name /ecs/arbor-production/backend \
    --log-stream-name <stream-name>

# Check task status
aws ecs describe-tasks \
    --cluster arbor-production-cluster \
    --tasks <task-arn>
```

### Database Connection Issues

```bash
# Test connectivity from ECS task
aws ecs execute-command \
    --cluster arbor-production-cluster \
    --task <task-id> \
    --container backend \
    --interactive \
    --command "/bin/sh"
```

### SSL Certificate Not Validated

Ensure DNS validation records are created in Route 53 or your DNS provider.

---

*Last Updated: January 27, 2025*

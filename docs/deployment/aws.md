# ARIA AWS Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying ARIA Emergency Response Platform on Amazon Web Services (AWS).

**Architecture:** ECS Fargate + RDS + ElastiCache + ALB

**Estimated Deployment Time:** 2-3 hours  
**Estimated Monthly Cost:** $150-$300 (depends on usage)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [AWS Services Used](#aws-services-used)
4. [Deployment Steps](#deployment-steps)
5. [Infrastructure as Code](#infrastructure-as-code)
6. [Configuration](#configuration)
7. [Monitoring & Logging](#monitoring--logging)
8. [SSL/HTTPS Setup](#sslhttps-setup)
9. [Scaling](#scaling)
10. [Backup & Disaster Recovery](#backup--disaster-recovery)
11. [Cost Optimization](#cost-optimization)
12. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### AWS Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AWS CLOUD INFRASTRUCTURE                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                         ROUTE 53                                 │  │
│  │                    DNS Management                                │  │
│  │              aria-emergency.com → ALB                            │  │
│  └────────────────────────┬─────────────────────────────────────────┘  │
│                           │                                             │
│                           ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                    CLOUDFRONT (Optional)                         │  │
│  │                    CDN for static assets                         │  │
│  └────────────────────────┬─────────────────────────────────────────┘  │
│                           │                                             │
│                           ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              APPLICATION LOAD BALANCER (ALB)                     │  │
│  │              - HTTPS/SSL Termination                             │  │
│  │              - Health checks                                     │  │
│  │              - Target groups                                     │  │
│  └───────────┬──────────────────────────┬──────────────────────────┘  │
│              │                          │                              │
│              ▼                          ▼                              │
│  ┌──────────────────────┐   ┌──────────────────────┐                 │
│  │  ECS SERVICE:        │   │  ECS SERVICE:        │                 │
│  │  Backend (FastAPI)   │   │  Frontend (Nginx)    │                 │
│  │  ├─ Task 1           │   │  ├─ Task 1           │                 │
│  │  ├─ Task 2           │   │  └─ Task 2           │                 │
│  │  └─ Task 3           │   │                      │                 │
│  │  Auto-scaling: 2-10  │   │  Auto-scaling: 2-5   │                 │
│  └──────────┬───────────┘   └──────────────────────┘                 │
│             │                                                          │
│             │  ┌──────────────────────────────────────────────────┐  │
│             └─>│              VPC NETWORKING                       │  │
│                │  ┌────────────────┐    ┌────────────────┐       │  │
│                │  │  Public Subnet │    │ Private Subnet │       │  │
│                │  │  (ALB, NAT GW) │    │  (ECS Tasks)   │       │  │
│                │  └────────────────┘    └────────────────┘       │  │
│                │                                                   │  │
│                │  Availability Zones: us-east-1a, us-east-1b      │  │
│                └───────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      DATA LAYER                                  │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │                                                                  │  │
│  │  ┌─────────────────────┐       ┌─────────────────────┐         │  │
│  │  │   RDS PostgreSQL    │       │  ElastiCache Redis  │         │  │
│  │  │   - Multi-AZ        │       │  - Cluster mode     │         │  │
│  │  │   - PostGIS enabled │       │  - Auto-failover    │         │  │
│  │  │   - Automated backup│       │  - 2 nodes          │         │  │
│  │  │   - Read replicas   │       │                     │         │  │
│  │  └─────────────────────┘       └─────────────────────┘         │  │
│  │                                                                  │  │
│  │  ┌─────────────────────┐                                        │  │
│  │  │     S3 BUCKETS      │                                        │  │
│  │  │  - Static assets    │                                        │  │
│  │  │  - ML models        │                                        │  │
│  │  │  - Backups          │                                        │  │
│  │  │  - Logs             │                                        │  │
│  │  └─────────────────────┘                                        │  │
│  │                                                                  │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                  SECRETS & CONFIGURATION                         │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │  - AWS Secrets Manager (API keys)                               │  │
│  │  - Parameter Store (config)                                     │  │
│  │  - IAM Roles & Policies                                         │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              MONITORING & OBSERVABILITY                          │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │  - CloudWatch Logs & Metrics                                     │  │
│  │  - CloudWatch Alarms                                             │  │
│  │  - X-Ray (Distributed tracing)                                   │  │
│  │  - CloudTrail (Audit logs)                                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Required Tools

- **AWS CLI** v2.x: https://aws.amazon.com/cli/
- **Docker**: For building container images
- **Terraform** (optional): For infrastructure as code
- **AWS Account**: With appropriate permissions

### AWS Account Setup

1. **Create AWS Account**: https://aws.amazon.com/
2. **Configure billing alerts**
3. **Enable MFA** on root account
4. **Create IAM user** with admin permissions

### Configure AWS CLI

```bash
# Install AWS CLI
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Configure credentials
aws configure

# Enter:
# AWS Access Key ID: YOUR_ACCESS_KEY
# AWS Secret Access Key: YOUR_SECRET_KEY
# Default region: us-east-1
# Default output format: json

# Verify
aws sts get-caller-identity
```

---

## AWS Services Used

### Core Services

| Service | Purpose | Estimated Cost |
|---------|---------|----------------|
| **ECS Fargate** | Container orchestration | $50-100/month |
| **RDS PostgreSQL** | Managed database | $40-80/month |
| **ElastiCache Redis** | Managed cache | $15-30/month |
| **Application Load Balancer** | Load balancing | $20-25/month |
| **Route 53** | DNS management | $0.50/month |
| **ECR** | Container registry | $1-5/month |
| **S3** | Object storage | $5-10/month |
| **CloudWatch** | Monitoring & logs | $10-20/month |
| **Secrets Manager** | Secret storage | $2-5/month |

**Total:** ~$150-300/month (varies with traffic and usage)

---

## Deployment Steps

### Step 1: Create VPC and Networking

```bash
# Create VPC
aws ec2 create-vpc \
  --cidr-block 10.0.0.0/16 \
  --tag-specifications 'ResourceType=vpc,Tags=[{Key=Name,Value=aria-vpc}]'

# Note the VPC ID from output
export VPC_ID=vpc-xxxxxxxxx

# Create Internet Gateway
aws ec2 create-internet-gateway \
  --tag-specifications 'ResourceType=internet-gateway,Tags=[{Key=Name,Value=aria-igw}]'

export IGW_ID=igw-xxxxxxxxx

# Attach Internet Gateway to VPC
aws ec2 attach-internet-gateway \
  --vpc-id $VPC_ID \
  --internet-gateway-id $IGW_ID

# Create Public Subnets (2 AZs for high availability)
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.1.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=aria-public-1a}]'

aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.2.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=aria-public-1b}]'

# Create Private Subnets
aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.10.0/24 \
  --availability-zone us-east-1a \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=aria-private-1a}]'

aws ec2 create-subnet \
  --vpc-id $VPC_ID \
  --cidr-block 10.0.11.0/24 \
  --availability-zone us-east-1b \
  --tag-specifications 'ResourceType=subnet,Tags=[{Key=Name,Value=aria-private-1b}]'

# Create NAT Gateway (for private subnets to access internet)
aws ec2 allocate-address --domain vpc
export EIP_ID=eipalloc-xxxxxxxxx

aws ec2 create-nat-gateway \
  --subnet-id $PUBLIC_SUBNET_1A \
  --allocation-id $EIP_ID \
  --tag-specifications 'ResourceType=nat-gateway,Tags=[{Key=Name,Value=aria-nat-gw}]'
```

---

### Step 2: Create Security Groups

```bash
# ALB Security Group
aws ec2 create-security-group \
  --group-name aria-alb-sg \
  --description "Security group for ARIA ALB" \
  --vpc-id $VPC_ID

export ALB_SG=sg-xxxxxxxxx

# Allow HTTP and HTTPS
aws ec2 authorize-security-group-ingress \
  --group-id $ALB_SG \
  --protocol tcp \
  --port 80 \
  --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id $ALB_SG \
  --protocol tcp \
  --port 443 \
  --cidr 0.0.0.0/0

# ECS Security Group
aws ec2 create-security-group \
  --group-name aria-ecs-sg \
  --description "Security group for ARIA ECS tasks" \
  --vpc-id $VPC_ID

export ECS_SG=sg-yyyyyyyyy

# Allow traffic from ALB
aws ec2 authorize-security-group-ingress \
  --group-id $ECS_SG \
  --protocol tcp \
  --port 8000 \
  --source-group $ALB_SG

# RDS Security Group
aws ec2 create-security-group \
  --group-name aria-rds-sg \
  --description "Security group for ARIA RDS" \
  --vpc-id $VPC_ID

export RDS_SG=sg-zzzzzzzzz

# Allow PostgreSQL from ECS
aws ec2 authorize-security-group-ingress \
  --group-id $RDS_SG \
  --protocol tcp \
  --port 5432 \
  --source-group $ECS_SG

# Redis Security Group
aws ec2 create-security-group \
  --group-name aria-redis-sg \
  --description "Security group for ARIA Redis" \
  --vpc-id $VPC_ID

export REDIS_SG=sg-aaaaaaaaa

# Allow Redis from ECS
aws ec2 authorize-security-group-ingress \
  --group-id $REDIS_SG \
  --protocol tcp \
  --port 6379 \
  --source-group $ECS_SG
```

---

### Step 3: Create RDS PostgreSQL Database

```bash
# Create DB Subnet Group
aws rds create-db-subnet-group \
  --db-subnet-group-name aria-db-subnet-group \
  --db-subnet-group-description "Subnet group for ARIA database" \
  --subnet-ids $PRIVATE_SUBNET_1A $PRIVATE_SUBNET_1B

# Create RDS Instance with PostGIS
aws rds create-db-instance \
  --db-instance-identifier aria-postgres \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --engine-version 14.7 \
  --master-username ariaadmin \
  --master-user-password "CHANGE_THIS_PASSWORD" \
  --allocated-storage 50 \
  --storage-type gp3 \
  --storage-encrypted \
  --vpc-security-group-ids $RDS_SG \
  --db-subnet-group-name aria-db-subnet-group \
  --multi-az \
  --backup-retention-period 7 \
  --preferred-backup-window "03:00-04:00" \
  --preferred-maintenance-window "sun:04:00-sun:05:00" \
  --enable-cloudwatch-logs-exports postgresql upgrade \
  --deletion-protection \
  --tags Key=Name,Value=aria-postgres

# Wait for RDS to be available (10-15 minutes)
aws rds wait db-instance-available --db-instance-identifier aria-postgres

# Get RDS endpoint
aws rds describe-db-instances \
  --db-instance-identifier aria-postgres \
  --query 'DBInstances[0].Endpoint.Address' \
  --output text
```

**Enable PostGIS Extension:**

```bash
# Connect to RDS
psql -h <RDS_ENDPOINT> -U ariaadmin -d postgres

# Run in psql:
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
\q
```

---

### Step 4: Create ElastiCache Redis Cluster

```bash
# Create Cache Subnet Group
aws elasticache create-cache-subnet-group \
  --cache-subnet-group-name aria-redis-subnet-group \
  --cache-subnet-group-description "Subnet group for ARIA Redis" \
  --subnet-ids $PRIVATE_SUBNET_1A $PRIVATE_SUBNET_1B

# Create Redis Cluster
aws elasticache create-replication-group \
  --replication-group-id aria-redis \
  --replication-group-description "Redis cluster for ARIA" \
  --engine redis \
  --engine-version 7.0 \
  --cache-node-type cache.t3.micro \
  --num-cache-clusters 2 \
  --automatic-failover-enabled \
  --multi-az-enabled \
  --cache-subnet-group-name aria-redis-subnet-group \
  --security-group-ids $REDIS_SG \
  --at-rest-encryption-enabled \
  --transit-encryption-enabled \
  --snapshot-retention-limit 5 \
  --snapshot-window "03:00-05:00"

# Wait for Redis to be available
aws elasticache wait replication-group-available \
  --replication-group-id aria-redis

# Get Redis endpoint
aws elasticache describe-replication-groups \
  --replication-group-id aria-redis \
  --query 'ReplicationGroups[0].NodeGroups[0].PrimaryEndpoint.Address' \
  --output text
```

---

### Step 5: Create S3 Buckets

```bash
# Bucket for static assets
aws s3 mb s3://aria-static-assets-$(date +%s)

# Bucket for ML models
aws s3 mb s3://aria-ml-models-$(date +%s)

# Bucket for backups
aws s3 mb s3://aria-backups-$(date +%s)

# Enable versioning on backups bucket
aws s3api put-bucket-versioning \
  --bucket aria-backups-$(date +%s) \
  --versioning-configuration Status=Enabled

# Upload ML models
aws s3 sync ./models/ s3://aria-ml-models-$(date +%s)/
```

---

### Step 6: Store Secrets in AWS Secrets Manager

```bash
# Create secret for database credentials
aws secretsmanager create-secret \
  --name aria/database/credentials \
  --description "Database credentials for ARIA" \
  --secret-string '{
    "username":"ariaadmin",
    "password":"CHANGE_THIS_PASSWORD",
    "host":"'$RDS_ENDPOINT'",
    "port":"5432",
    "database":"aria_prod"
  }'

# Create secret for API keys
aws secretsmanager create-secret \
  --name aria/api/keys \
  --description "External API keys for ARIA" \
  --secret-string '{
    "openai_api_key":"sk-your-openai-key",
    "google_maps_api_key":"AIza-your-google-key",
    "twilio_account_sid":"AC-your-twilio-sid",
    "twilio_auth_token":"your-twilio-token",
    "sendgrid_api_key":"SG.your-sendgrid-key"
  }'

# Create secret for application config
aws secretsmanager create-secret \
  --name aria/app/config \
  --description "Application configuration for ARIA" \
  --secret-string '{
    "secret_key":"'$(openssl rand -hex 32)'",
    "jwt_algorithm":"HS256"
  }'
```

---

### Step 7: Build and Push Docker Images to ECR

```bash
# Create ECR repositories
aws ecr create-repository --repository-name aria/backend
aws ecr create-repository --repository-name aria/frontend

# Get ECR login credentials
aws ecr get-login-password --region us-east-1 | \
  docker login --username AWS --password-stdin <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com

# Build backend image
cd backend
docker build -t aria/backend:latest .
docker tag aria/backend:latest <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/aria/backend:latest
docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/aria/backend:latest

# Build frontend image
cd ../frontend
docker build -t aria/frontend:latest .
docker tag aria/frontend:latest <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/aria/frontend:latest
docker push <AWS_ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/aria/frontend:latest
```

---

### Step 8: Create ECS Cluster

```bash
# Create ECS cluster
aws ecs create-cluster \
  --cluster-name aria-cluster \
  --capacity-providers FARGATE FARGATE_SPOT \
  --default-capacity-provider-strategy \
    capacityProvider=FARGATE,weight=1,base=1 \
    capacityProvider=FARGATE_SPOT,weight=4

# Create CloudWatch Log Group
aws logs create-log-group --log-group-name /ecs/aria-backend
aws logs create-log-group --log-group-name /ecs/aria-frontend
```

---

### Step 9: Create IAM Roles

**Task Execution Role:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ecs-tasks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

```bash
aws iam create-role \
  --role-name ariaECSTaskExecutionRole \
  --assume-role-policy-document file://task-execution-role.json

aws iam attach-role-policy \
  --role-name ariaECSTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Add permissions for Secrets Manager
aws iam put-role-policy \
  --role-name ariaECSTaskExecutionRole \
  --policy-name SecretsManagerAccess \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "secretsmanager:GetSecretValue"
        ],
        "Resource": "arn:aws:secretsmanager:us-east-1:*:secret:aria/*"
      }
    ]
  }'
```

**Task Role:**

```bash
aws iam create-role \
  --role-name ariaECSTaskRole \
  --assume-role-policy-document file://task-execution-role.json

# Add permissions for S3 (ML models)
aws iam put-role-policy \
  --role-name ariaECSTaskRole \
  --policy-name S3Access \
  --policy-document '{
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": [
          "s3:GetObject",
          "s3:ListBucket"
        ],
        "Resource": [
          "arn:aws:s3:::aria-ml-models-*/*",
          "arn:aws:s3:::aria-ml-models-*"
        ]
      }
    ]
  }'
```

---

### Step 10: Create ECS Task Definitions

**Backend Task Definition:**

```json
{
  "family": "aria-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "executionRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/ariaECSTaskExecutionRole",
  "taskRoleArn": "arn:aws:iam::<ACCOUNT_ID>:role/ariaECSTaskRole",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "<ACCOUNT_ID>.dkr.ecr.us-east-1.amazonaws.com/aria/backend:latest",
      "cpu": 1024,
      "memory": 2048,
      "essential": true,
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        },
        {
          "name": "DEBUG",
          "value": "false"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<ACCOUNT_ID>:secret:aria/database/credentials:url::"
        },
        {
          "name": "OPENAI_API_KEY",
          "valueFrom": "arn:aws:secretsmanager:us-east-1:<ACCOUNT_ID>:secret:aria/api/keys:openai_api_key::"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/aria-backend",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3,
        "startPeriod": 60
      }
    }
  ]
}
```

```bash
aws ecs register-task-definition --cli-input-json file://backend-task-definition.json
```

---

### Step 11: Create Application Load Balancer

```bash
# Create ALB
aws elbv2 create-load-balancer \
  --name aria-alb \
  --subnets $PUBLIC_SUBNET_1A $PUBLIC_SUBNET_1B \
  --security-groups $ALB_SG \
  --scheme internet-facing \
  --type application \
  --ip-address-type ipv4 \
  --tags Key=Name,Value=aria-alb

export ALB_ARN=<ALB_ARN_FROM_OUTPUT>

# Create Target Groups
aws elbv2 create-target-group \
  --name aria-backend-tg \
  --protocol HTTP \
  --port 8000 \
  --vpc-id $VPC_ID \
  --target-type ip \
  --health-check-enabled \
  --health-check-path /health \
  --health-check-interval-seconds 30 \
  --health-check-timeout-seconds 5 \
  --healthy-threshold-count 2 \
  --unhealthy-threshold-count 3

export BACKEND_TG_ARN=<TG_ARN_FROM_OUTPUT>

aws elbv2 create-target-group \
  --name aria-frontend-tg \
  --protocol HTTP \
  --port 80 \
  --vpc-id $VPC_ID \
  --target-type ip \
  --health-check-enabled \
  --health-check-path / \
  --health-check-interval-seconds 30

export FRONTEND_TG_ARN=<TG_ARN_FROM_OUTPUT>

# Create Listeners
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTP \
  --port 80 \
  --default-actions Type=forward,TargetGroupArn=$FRONTEND_TG_ARN
```

---

### Step 12: Create ECS Services

```bash
# Backend Service
aws ecs create-service \
  --cluster aria-cluster \
  --service-name aria-backend \
  --task-definition aria-backend \
  --desired-count 2 \
  --launch-type FARGATE \
  --platform-version LATEST \
  --network-configuration "awsvpcConfiguration={
    subnets=[$PRIVATE_SUBNET_1A,$PRIVATE_SUBNET_1B],
    securityGroups=[$ECS_SG],
    assignPublicIp=DISABLED
  }" \
  --load-balancers "targetGroupArn=$BACKEND_TG_ARN,containerName=backend,containerPort=8000" \
  --health-check-grace-period-seconds 60 \
  --deployment-configuration "minimumHealthyPercent=100,maximumPercent=200" \
  --enable-execute-command

# Frontend Service
aws ecs create-service \
  --cluster aria-cluster \
  --service-name aria-frontend \
  --task-definition aria-frontend \
  --desired-count 2 \
  --launch-type FARGATE \
  --platform-version LATEST \
  --network-configuration "awsvpcConfiguration={
    subnets=[$PRIVATE_SUBNET_1A,$PRIVATE_SUBNET_1B],
    securityGroups=[$ECS_SG],
    assignPublicIp=DISABLED
  }" \
  --load-balancers "targetGroupArn=$FRONTEND_TG_ARN,containerName=frontend,containerPort=80" \
  --health-check-grace-period-seconds 30 \
  --deployment-configuration "minimumHealthyPercent=100,maximumPercent=200"
```

---

### Step 13: Configure Auto Scaling

```bash
# Register scalable target
aws application-autoscaling register-scalable-target \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/aria-cluster/aria-backend \
  --min-capacity 2 \
  --max-capacity 10

# Create scaling policy (CPU-based)
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/aria-cluster/aria-backend \
  --policy-name aria-backend-cpu-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 70.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ECSServiceAverageCPUUtilization"
    },
    "ScaleInCooldown": 300,
    "ScaleOutCooldown": 60
  }'

# Create scaling policy (Request-based)
aws application-autoscaling put-scaling-policy \
  --service-namespace ecs \
  --scalable-dimension ecs:service:DesiredCount \
  --resource-id service/aria-cluster/aria-backend \
  --policy-name aria-backend-request-scaling \
  --policy-type TargetTrackingScaling \
  --target-tracking-scaling-policy-configuration '{
    "TargetValue": 1000.0,
    "PredefinedMetricSpecification": {
      "PredefinedMetricType": "ALBRequestCountPerTarget",
      "ResourceLabel": "app/aria-alb/*/targetgroup/aria-backend-tg/*"
    }
  }'
```

---

## SSL/HTTPS Setup

### Option 1: AWS Certificate Manager (Free)

```bash
# Request certificate
aws acm request-certificate \
  --domain-name aria-emergency.com \
  --subject-alternative-names www.aria-emergency.com api.aria-emergency.com \
  --validation-method DNS

# Note certificate ARN
export CERT_ARN=<CERTIFICATE_ARN>

# Add DNS records for validation (follow ACM console instructions)

# Wait for validation
aws acm wait certificate-validated --certificate-arn $CERT_ARN

# Add HTTPS listener to ALB
aws elbv2 create-listener \
  --load-balancer-arn $ALB_ARN \
  --protocol HTTPS \
  --port 443 \
  --certificates CertificateArn=$CERT_ARN \
  --default-actions Type=forward,TargetGroupArn=$FRONTEND_TG_ARN

# Redirect HTTP to HTTPS
aws elbv2 modify-listener \
  --listener-arn $HTTP_LISTENER_ARN \
  --default-actions Type=redirect,RedirectConfig="{
    Protocol=HTTPS,
    Port=443,
    StatusCode=HTTP_301
  }"
```

---

## Monitoring & Logging

### CloudWatch Alarms

```bash
# High CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name aria-backend-high-cpu \
  --alarm-description "Backend CPU above 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --dimensions Name=ServiceName,Value=aria-backend Name=ClusterName,Value=aria-cluster

# High memory alarm
aws cloudwatch put-metric-alarm \
  --alarm-name aria-backend-high-memory \
  --alarm-description "Backend memory above 85%" \
  --metric-name MemoryUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 85 \
  --comparison-operator GreaterThanThreshold

# RDS storage alarm
aws cloudwatch put-metric-alarm \
  --alarm-name aria-rds-low-storage \
  --alarm-description "RDS storage below 10GB" \
  --metric-name FreeStorageSpace \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 10000000000 \
  --comparison-operator LessThanThreshold \
  --dimensions Name=DBInstanceIdentifier,Value=aria-postgres
```

### Log Insights Queries

```sql
-- Query errors in last hour
fields @timestamp, @message
| filter @message like /ERROR/
| sort @timestamp desc
| limit 100

-- Query slow API requests
fields @timestamp, request_path, response_time
| filter response_time > 2000
| sort response_time desc
| limit 50

-- Count incidents by severity
stats count() by severity
| sort count() desc
```

---

## Backup & Disaster Recovery

### Automated RDS Backups

```bash
# Modify RDS to increase backup retention
aws rds modify-db-instance \
  --db-instance-identifier aria-postgres \
  --backup-retention-period 14 \
  --preferred-backup-window "03:00-04:00" \
  --apply-immediately

# Create manual snapshot
aws rds create-db-snapshot \
  --db-instance-identifier aria-postgres \
  --db-snapshot-identifier aria-postgres-snapshot-$(date +%Y%m%d)
```

### Disaster Recovery Plan

1. **RPO (Recovery Point Objective):** 1 hour
2. **RTO (Recovery Time Objective):** 4 hours
3. **Multi-region failover** (optional advanced setup)

---

## Cost Optimization

### Strategies

1. **Use Fargate Spot:** Save up to 70% on compute
2. **Reserved Instances:** For RDS and ElastiCache
3. **S3 Lifecycle Policies:** Move old logs to Glacier
4. **Auto-scaling:** Scale down during low traffic
5. **CloudWatch Log Retention:** Limit to 30 days

### Example Cost Reduction

```bash
# Set log retention
aws logs put-retention-policy \
  --log-group-name /ecs/aria-backend \
  --retention-in-days 30

# S3 lifecycle policy
aws s3api put-bucket-lifecycle-configuration \
  --bucket aria-backups-* \
  --lifecycle-configuration file://lifecycle.json
```

---

## Troubleshooting

### Common Issues

**1. ECS Tasks Won't Start**
- Check CloudWatch logs: `/ecs/aria-backend`
- Verify secrets exist in Secrets Manager
- Check security group allows outbound traffic

**2. ALB Health Checks Failing**
- Verify `/health` endpoint works
- Check security groups allow ALB → ECS traffic
- Increase health check grace period

**3. High Costs**
- Review CloudWatch billing metrics
- Check for idle resources
- Enable cost allocation tags

---

## Quick Reference

```bash
# Deploy new version
docker build -t aria/backend:v1.1 .
docker push <ECR_URI>/aria/backend:v1.1
aws ecs update-service --cluster aria-cluster --service aria-backend --force-new-deployment

# View logs
aws logs tail /ecs/aria-backend --follow

# Scale service
aws ecs update-service --cluster aria-cluster --service aria-backend --desired-count 5

# Get service status
aws ecs describe-services --cluster aria-cluster --services aria-backend
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-09-06  
**Maintained By:** ARIA Development Team

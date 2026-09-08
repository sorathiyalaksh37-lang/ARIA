# ARIA GCP Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying ARIA Emergency Response Platform on Google Cloud Platform (GCP).

**Architecture:** Cloud Run + Cloud SQL + Memorystore + Cloud Load Balancing

**Estimated Deployment Time:** 2-3 hours  
**Estimated Monthly Cost:** $120-$250 (depends on usage)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [GCP Services Used](#gcp-services-used)
4. [Deployment Steps](#deployment-steps)
5. [Configuration](#configuration)
6. [Monitoring & Logging](#monitoring--logging)
7. [SSL/HTTPS Setup](#sslhttps-setup)
8. [Scaling](#scaling)
9. [Backup & Disaster Recovery](#backup--disaster-recovery)
10. [Cost Optimization](#cost-optimization)
11. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

### GCP Deployment Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    GOOGLE CLOUD PLATFORM                                │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      CLOUD DNS                                   │  │
│  │              aria-emergency.com → Load Balancer                  │  │
│  └────────────────────────┬─────────────────────────────────────────┘  │
│                           │                                             │
│                           ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                 CLOUD CDN (Optional)                             │  │
│  │                Static content caching                            │  │
│  └────────────────────────┬─────────────────────────────────────────┘  │
│                           │                                             │
│                           ▼                                             │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              CLOUD LOAD BALANCER (HTTPS)                         │  │
│  │              - SSL termination                                   │  │
│  │              - Backend services routing                          │  │
│  │              - Health checks                                     │  │
│  └───────────┬──────────────────────────┬──────────────────────────┘  │
│              │                          │                              │
│              ▼                          ▼                              │
│  ┌──────────────────────┐   ┌──────────────────────┐                 │
│  │  CLOUD RUN:          │   │  CLOUD RUN:          │                 │
│  │  Backend (FastAPI)   │   │  Frontend (Nginx)    │                 │
│  │  ├─ Instance 1       │   │  ├─ Instance 1       │                 │
│  │  ├─ Instance 2       │   │  └─ Instance 2       │                 │
│  │  └─ Instance N       │   │                      │                 │
│  │  Scale: 1-100        │   │  Scale: 1-50         │                 │
│  │  CPU: 1, Memory: 2Gi │   │  CPU: 0.5, Memory:1Gi│                 │
│  └──────────┬───────────┘   └──────────────────────┘                 │
│             │                                                          │
│             │  ┌──────────────────────────────────────────────────┐  │
│             └─>│              VPC NETWORK                          │  │
│                │  Private Google Access enabled                    │  │
│                │  Serverless VPC Connector                         │  │
│                └───────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      DATA LAYER                                  │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │                                                                  │  │
│  │  ┌─────────────────────┐       ┌─────────────────────┐         │  │
│  │  │  Cloud SQL          │       │  Memorystore Redis  │         │  │
│  │  │  PostgreSQL 14      │       │  - Standard tier    │         │  │
│  │  │  - PostGIS enabled  │       │  - 5GB memory       │         │  │
│  │  │  - High availability│       │  - Auto-failover    │         │  │
│  │  │  - Auto backups     │       │                     │         │  │
│  │  │  - Read replicas    │       │                     │         │  │
│  │  └─────────────────────┘       └─────────────────────┘         │  │
│  │                                                                  │  │
│  │  ┌─────────────────────┐                                        │  │
│  │  │  CLOUD STORAGE      │                                        │  │
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
│  │  - Secret Manager (API keys, credentials)                       │  │
│  │  - IAM & Service Accounts                                       │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │              MONITORING & OBSERVABILITY                          │  │
│  ├──────────────────────────────────────────────────────────────────┤  │
│  │  - Cloud Monitoring (Metrics & Dashboards)                       │  │
│  │  - Cloud Logging (Centralized logs)                              │  │
│  │  - Cloud Trace (Distributed tracing)                             │  │
│  │  - Cloud Profiler (Performance profiling)                        │  │
│  │  - Error Reporting (Exception tracking)                          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

### Required Tools

- **gcloud CLI**: https://cloud.google.com/sdk/docs/install
- **Docker**: For building container images
- **Terraform** (optional): For infrastructure as code
- **GCP Account**: With billing enabled

### GCP Account Setup

1. **Create GCP Account**: https://console.cloud.google.com/
2. **Create Project**: `aria-emergency-prod`
3. **Enable Billing**
4. **Install gcloud CLI**

### Configure gcloud CLI

```bash
# Install gcloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Initialize gcloud
gcloud init

# Select or create project
gcloud projects create aria-emergency-prod
gcloud config set project aria-emergency-prod

# Enable billing (required)
# Go to: https://console.cloud.google.com/billing/linkedaccount

# Verify
gcloud config list
```

---

## GCP Services Used

### Core Services

| Service | Purpose | Estimated Cost |
|---------|---------|----------------|
| **Cloud Run** | Serverless containers | $30-80/month |
| **Cloud SQL (PostgreSQL)** | Managed database | $35-70/month |
| **Memorystore (Redis)** | Managed cache | $20-35/month |
| **Cloud Load Balancing** | HTTPS load balancer | $20-25/month |
| **Cloud Storage** | Object storage | $5-10/month |
| **Container Registry** | Container images | $1-5/month |
| **Secret Manager** | Secret storage | $1-3/month |
| **Cloud Monitoring** | Monitoring & logs | $10-20/month |

**Total:** ~$120-250/month (varies with traffic)

---

## Deployment Steps

### Step 1: Enable Required APIs

```bash
# Enable all required GCP APIs
gcloud services enable \
  run.googleapis.com \
  sql-component.googleapis.com \
  sqladmin.googleapis.com \
  redis.googleapis.com \
  compute.googleapis.com \
  vpcaccess.googleapis.com \
  storage-api.googleapis.com \
  secretmanager.googleapis.com \
  cloudresourcemanager.googleapis.com \
  container-registry.googleapis.com \
  cloudtrace.googleapis.com \
  cloudprofiler.googleapis.com \
  cloudbuild.googleapis.com \
  dns.googleapis.com

# Verify enabled services
gcloud services list --enabled
```

---

### Step 2: Create VPC Network and Connector

```bash
# Create VPC network
gcloud compute networks create aria-vpc \
  --subnet-mode=custom \
  --bgp-routing-mode=regional

# Create subnet
gcloud compute networks subnets create aria-subnet \
  --network=aria-vpc \
  --region=us-central1 \
  --range=10.0.0.0/24

# Create Serverless VPC Connector (for Cloud Run → Cloud SQL/Redis)
gcloud compute networks vpc-access connectors create aria-connector \
  --region=us-central1 \
  --subnet=aria-subnet \
  --min-instances=2 \
  --max-instances=10 \
  --machine-type=e2-micro

# Verify connector
gcloud compute networks vpc-access connectors describe aria-connector \
  --region=us-central1
```

---

### Step 3: Create Cloud SQL PostgreSQL Instance

```bash
# Create Cloud SQL instance with PostGIS
gcloud sql instances create aria-postgres \
  --database-version=POSTGRES_14 \
  --tier=db-custom-2-7680 \
  --region=us-central1 \
  --network=projects/$(gcloud config get-value project)/global/networks/aria-vpc \
  --no-assign-ip \
  --availability-type=REGIONAL \
  --backup-start-time=03:00 \
  --maintenance-window-day=SUN \
  --maintenance-window-hour=04 \
  --enable-bin-log \
  --retained-backups-count=7 \
  --storage-auto-increase \
  --storage-size=50GB \
  --database-flags=cloudsql.enable_pg_net=on

# Set root password
gcloud sql users set-password postgres \
  --instance=aria-postgres \
  --password=CHANGE_THIS_SECURE_PASSWORD

# Create application database
gcloud sql databases create aria_prod \
  --instance=aria-postgres

# Create application user
gcloud sql users create ariauser \
  --instance=aria-postgres \
  --password=APPLICATION_PASSWORD

# Get connection name
gcloud sql instances describe aria-postgres \
  --format='value(connectionName)'

# Connect and enable PostGIS
gcloud sql connect aria-postgres --user=postgres
# In psql:
\c aria_prod
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
\q
```

---

### Step 4: Create Memorystore Redis Instance

```bash
# Create Redis instance
gcloud redis instances create aria-redis \
  --size=5 \
  --region=us-central1 \
  --network=projects/$(gcloud config get-value project)/global/networks/aria-vpc \
  --tier=STANDARD_HA \
  --redis-version=redis_7_0

# Wait for creation (3-5 minutes)
gcloud redis instances describe aria-redis --region=us-central1

# Get Redis host and port
export REDIS_HOST=$(gcloud redis instances describe aria-redis \
  --region=us-central1 \
  --format='value(host)')
export REDIS_PORT=$(gcloud redis instances describe aria-redis \
  --region=us-central1 \
  --format='value(port)')

echo "Redis endpoint: $REDIS_HOST:$REDIS_PORT"
```

---

### Step 5: Create Cloud Storage Buckets

```bash
# Create buckets
gsutil mb -l us-central1 gs://aria-static-assets-$(gcloud config get-value project)
gsutil mb -l us-central1 gs://aria-ml-models-$(gcloud config get-value project)
gsutil mb -l us-central1 gs://aria-backups-$(gcloud config get-value project)

# Set lifecycle policy for backups
cat > lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {"age": 90}
      }
    ]
  }
}
EOF

gsutil lifecycle set lifecycle.json gs://aria-backups-$(gcloud config get-value project)

# Upload ML models
gsutil -m cp -r ./models/* gs://aria-ml-models-$(gcloud config get-value project)/

# Set permissions (private)
gsutil iam ch allUsers:objectViewer gs://aria-static-assets-$(gcloud config get-value project)
```

---

### Step 6: Store Secrets in Secret Manager

```bash
# Create secrets for database credentials
echo -n "postgresql://ariauser:APPLICATION_PASSWORD@/aria_prod?host=/cloudsql/PROJECT:REGION:aria-postgres" | \
  gcloud secrets create database-url --data-file=-

# Create secret for API keys
cat > api-keys.json << EOF
{
  "openai_api_key": "sk-your-openai-key",
  "google_maps_api_key": "AIza-your-google-key",
  "twilio_account_sid": "AC-your-twilio-sid",
  "twilio_auth_token": "your-twilio-token",
  "sendgrid_api_key": "SG.your-sendgrid-key"
}
EOF

gcloud secrets create api-keys --data-file=api-keys.json
rm api-keys.json

# Create secret for application config
echo -n "$(openssl rand -hex 32)" | gcloud secrets create secret-key --data-file=-

# Grant Cloud Run access to secrets
PROJECT_NUMBER=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')

gcloud secrets add-iam-policy-binding database-url \
  --member=serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

gcloud secrets add-iam-policy-binding api-keys \
  --member=serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor

gcloud secrets add-iam-policy-binding secret-key \
  --member=serviceAccount:$PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor
```

---

### Step 7: Build and Push Container Images

```bash
# Set up Docker authentication for GCR
gcloud auth configure-docker

# Build and push backend
cd backend
gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/aria-backend:latest

# Build and push frontend
cd ../frontend
gcloud builds submit --tag gcr.io/$(gcloud config get-value project)/aria-frontend:latest

# Verify images
gcloud container images list
```

---

### Step 8: Deploy Backend to Cloud Run

```bash
# Get Cloud SQL connection name
export SQL_CONNECTION=$(gcloud sql instances describe aria-postgres \
  --format='value(connectionName)')

# Deploy backend service
gcloud run deploy aria-backend \
  --image gcr.io/$(gcloud config get-value project)/aria-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="ENVIRONMENT=production,DEBUG=false" \
  --set-secrets="DATABASE_URL=database-url:latest,OPENAI_API_KEY=api-keys:latest:openai_api_key,SECRET_KEY=secret-key:latest" \
  --add-cloudsql-instances=$SQL_CONNECTION \
  --vpc-connector=aria-connector \
  --cpu=2 \
  --memory=2Gi \
  --min-instances=1 \
  --max-instances=100 \
  --concurrency=80 \
  --timeout=300 \
  --port=8000

# Get backend URL
export BACKEND_URL=$(gcloud run services describe aria-backend \
  --region us-central1 \
  --format='value(status.url)')

echo "Backend URL: $BACKEND_URL"
```

---

### Step 9: Deploy Frontend to Cloud Run

```bash
# Deploy frontend service
gcloud run deploy aria-frontend \
  --image gcr.io/$(gcloud config get-value project)/aria-frontend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="REACT_APP_API_BASE_URL=$BACKEND_URL" \
  --cpu=0.5 \
  --memory=1Gi \
  --min-instances=1 \
  --max-instances=50 \
  --concurrency=80 \
  --port=80

# Get frontend URL
export FRONTEND_URL=$(gcloud run services describe aria-frontend \
  --region us-central1 \
  --format='value(status.url)')

echo "Frontend URL: $FRONTEND_URL"
```

---

### Step 10: Set Up Load Balancer with Custom Domain

```bash
# Reserve static IP
gcloud compute addresses create aria-lb-ip \
  --global

# Get IP address
export STATIC_IP=$(gcloud compute addresses describe aria-lb-ip \
  --global \
  --format='value(address)')

echo "Static IP: $STATIC_IP"

# Create serverless NEG for backend
gcloud compute network-endpoint-groups create aria-backend-neg \
  --region=us-central1 \
  --network-endpoint-type=serverless \
  --cloud-run-service=aria-backend

# Create serverless NEG for frontend
gcloud compute network-endpoint-groups create aria-frontend-neg \
  --region=us-central1 \
  --network-endpoint-type=serverless \
  --cloud-run-service=aria-frontend

# Create backend services
gcloud compute backend-services create aria-backend-service \
  --global

gcloud compute backend-services add-backend aria-backend-service \
  --global \
  --network-endpoint-group=aria-backend-neg \
  --network-endpoint-group-region=us-central1

gcloud compute backend-services create aria-frontend-service \
  --global

gcloud compute backend-services add-backend aria-frontend-service \
  --global \
  --network-endpoint-group=aria-frontend-neg \
  --network-endpoint-group-region=us-central1

# Create URL map
gcloud compute url-maps create aria-lb \
  --default-service aria-frontend-service

# Add path matcher for API
gcloud compute url-maps add-path-matcher aria-lb \
  --path-matcher-name=api-matcher \
  --default-service=aria-frontend-service \
  --path-rules="/api/*=aria-backend-service,/docs=aria-backend-service,/health=aria-backend-service"

# Create SSL certificate (managed)
gcloud compute ssl-certificates create aria-ssl-cert \
  --domains=aria-emergency.com,www.aria-emergency.com

# Create HTTPS proxy
gcloud compute target-https-proxies create aria-https-proxy \
  --url-map=aria-lb \
  --ssl-certificates=aria-ssl-cert

# Create forwarding rule
gcloud compute forwarding-rules create aria-https-rule \
  --global \
  --target-https-proxy=aria-https-proxy \
  --address=aria-lb-ip \
  --ports=443

# Create HTTP to HTTPS redirect
gcloud compute url-maps import aria-redirect \
  --global \
  --source /dev/stdin << EOF
name: aria-redirect
defaultUrlRedirect:
  httpsRedirect: true
  redirectResponseCode: MOVED_PERMANENTLY_DEFAULT
EOF

gcloud compute target-http-proxies create aria-http-proxy \
  --url-map=aria-redirect

gcloud compute forwarding-rules create aria-http-rule \
  --global \
  --target-http-proxy=aria-http-proxy \
  --address=aria-lb-ip \
  --ports=80
```

---

### Step 11: Configure Cloud DNS

```bash
# Create DNS zone
gcloud dns managed-zones create aria-zone \
  --dns-name=aria-emergency.com \
  --description="DNS zone for ARIA"

# Add A record
gcloud dns record-sets transaction start --zone=aria-zone

gcloud dns record-sets transaction add $STATIC_IP \
  --name=aria-emergency.com. \
  --ttl=300 \
  --type=A \
  --zone=aria-zone

gcloud dns record-sets transaction add $STATIC_IP \
  --name=www.aria-emergency.com. \
  --ttl=300 \
  --type=A \
  --zone=aria-zone

gcloud dns record-sets transaction execute --zone=aria-zone

# Get nameservers
gcloud dns managed-zones describe aria-zone \
  --format='value(nameServers)'

# Update nameservers at your domain registrar
```

---

## Monitoring & Logging

### Cloud Monitoring Dashboard

```bash
# Create custom dashboard
gcloud monitoring dashboards create --config-from-file=- << EOF
{
  "displayName": "ARIA Production Dashboard",
  "mosaicLayout": {
    "columns": 12,
    "tiles": [
      {
        "width": 6,
        "height": 4,
        "widget": {
          "title": "Cloud Run Request Count",
          "xyChart": {
            "dataSets": [{
              "timeSeriesQuery": {
                "timeSeriesFilter": {
                  "filter": "resource.type=\"cloud_run_revision\" AND metric.type=\"run.googleapis.com/request_count\"",
                  "aggregation": {
                    "alignmentPeriod": "60s",
                    "perSeriesAligner": "ALIGN_RATE"
                  }
                }
              }
            }]
          }
        }
      }
    ]
  }
}
EOF
```

### Log-based Metrics

```bash
# Create metric for errors
gcloud logging metrics create aria-errors \
  --description="Count of error logs" \
  --log-filter='severity >= ERROR'

# Create alert policy
gcloud alpha monitoring policies create \
  --notification-channels=CHANNEL_ID \
  --display-name="ARIA High Error Rate" \
  --condition-display-name="Error rate > 10/min" \
  --condition-threshold-value=10 \
  --condition-threshold-duration=60s \
  --condition-aggregation-alignment-period=60s \
  --condition-aggregation-per-series-aligner=ALIGN_RATE \
  --condition-filter='metric.type="logging.googleapis.com/user/aria-errors" resource.type="cloud_run_revision"'
```

---

## Scaling Configuration

### Backend Auto-scaling

```bash
# Update backend with custom scaling
gcloud run services update aria-backend \
  --region us-central1 \
  --min-instances=2 \
  --max-instances=100 \
  --cpu-throttling \
  --concurrency=80 \
  --cpu-boost
```

### Database Scaling

```bash
# Scale up Cloud SQL
gcloud sql instances patch aria-postgres \
  --tier=db-custom-4-15360

# Add read replica
gcloud sql instances create aria-postgres-read-replica \
  --master-instance-name=aria-postgres \
  --tier=db-custom-2-7680 \
  --region=us-central1
```

---

## Backup & Disaster Recovery

### Automated Backups

```bash
# SQL backups (automatic)
gcloud sql backups list --instance=aria-postgres

# Create on-demand backup
gcloud sql backups create --instance=aria-postgres

# Restore from backup
gcloud sql backups restore BACKUP_ID \
  --backup-instance=aria-postgres \
  --backup-id=BACKUP_ID
```

---

## Cost Optimization

### Strategies

1. **Use minimum instances wisely**
2. **Enable CPU allocation only during request**
3. **Use Cloud CDN for static assets**
4. **Set appropriate timeout values**
5. **Monitor and optimize concurrency**

```bash
# Optimize backend for cost
gcloud run services update aria-backend \
  --region us-central1 \
  --min-instances=0 \
  --cpu-throttling \
  --timeout=60

# Enable Cloud CDN
gcloud compute backend-services update aria-frontend-service \
  --enable-cdn \
  --global
```

---

## Troubleshooting

### Check Logs

```bash
# Backend logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=aria-backend" \
  --limit=50 \
  --format=json

# Filter errors
gcloud logging read "resource.type=cloud_run_revision AND severity>=ERROR" \
  --limit=20
```

### Test Connectivity

```bash
# Test backend health
curl https://aria-emergency.com/api/health

# Test from Cloud Shell
gcloud run services proxy aria-backend --region=us-central1
```

---

## Quick Reference

```bash
# Deploy new version
gcloud builds submit --tag gcr.io/PROJECT_ID/aria-backend:v1.1
gcloud run deploy aria-backend --image gcr.io/PROJECT_ID/aria-backend:v1.1 --region us-central1

# View logs
gcloud run logs read aria-backend --region us-central1

# Scale service
gcloud run services update aria-backend --max-instances=200 --region us-central1

# Get service URL
gcloud run services describe aria-backend --region us-central1 --format='value(status.url)'
```

---

**Document Version:** 1.0  
**Last Updated:** 2026-09-06  
**Maintained By:** ARIA Development Team

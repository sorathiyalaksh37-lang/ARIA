# ARIA Docker Setup Guide

## Overview

This guide explains how to run ARIA Emergency Response Platform using Docker and Docker Compose.

**Advantages of Docker Setup:**
- ✅ Consistent environment across machines
- ✅ No manual dependency installation
- ✅ Easy to start/stop all services
- ✅ Isolated from host system
- ✅ Production-like setup locally

**Estimated Setup Time:** 15-20 minutes

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Service Architecture](#service-architecture)
4. [Configuration](#configuration)
5. [Running Services](#running-services)
6. [Service Profiles](#service-profiles)
7. [Data Persistence](#data-persistence)
8. [Monitoring](#monitoring)
9. [Troubleshooting](#troubleshooting)
10. [Advanced Usage](#advanced-usage)

---

## Prerequisites

### Required Software

| Software | Version | Download Link |
|----------|---------|---------------|
| **Docker** | 20.10+ | https://docs.docker.com/get-docker/ |
| **Docker Compose** | 2.0+ | Included with Docker Desktop |
| **Git** | Latest | https://git-scm.com/downloads |
| **Git LFS** | Latest | https://git-lfs.github.com/ |

### System Requirements

**Minimum:**
- **CPU:** 4 cores
- **RAM:** 8 GB
- **Disk:** 15 GB free space
- **OS:** macOS, Linux, or Windows 10+ with WSL2

**Recommended:**
- **CPU:** 8 cores
- **RAM:** 16 GB
- **Disk:** 30 GB SSD
- **OS:** Linux or macOS

---

## Quick Start

### 1. Clone Repository

```bash
git clone https://github.com/sorathiyalaksh37-lang/ARIA.git
cd ARIA

# Pull LFS files (ML models)
git lfs install
git lfs pull
```

### 2. Configure Environment

```bash
# Copy environment file
cp .env.example .env

# Edit with your API keys
nano .env
```

**Minimum Required Configuration:**

```bash
# Database
POSTGRES_USER=aria_user
POSTGRES_PASSWORD=change_this_password
POSTGRES_DB=aria_dev

# Security
SECRET_KEY=generate_a_secure_random_key

# API Keys
OPENAI_API_KEY=sk-your-key-here
GOOGLE_MAPS_API_KEY=AIza-your-key-here
TWILIO_ACCOUNT_SID=AC-your-sid-here
TWILIO_AUTH_TOKEN=your-token-here
SENDGRID_API_KEY=SG.your-key-here
```

### 3. Start Services

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Check status
docker-compose ps
```

### 4. Verify

```bash
# Check backend health
curl http://localhost:8000/health

# Open frontend
open http://localhost:3000

# Open API docs
open http://localhost:8000/docs
```

**That's it! 🎉**

---

## Service Architecture

### Docker Compose Services

```
┌─────────────────────────────────────────────────────┐
│              ARIA Docker Stack                      │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────┐     ┌─────────────┐              │
│  │  Frontend   │     │   Backend   │              │
│  │  React+Nginx│     │   FastAPI   │              │
│  │  Port: 3000 │     │  Port: 8000 │              │
│  └──────┬──────┘     └──────┬──────┘              │
│         │                   │                       │
│         └───────┬───────────┘                       │
│                 │                                    │
│    ┌────────────┴────────────┐                     │
│    │                         │                      │
│  ┌─┴────────┐          ┌─────┴────┐               │
│  │PostgreSQL│          │  Redis   │               │
│  │+ PostGIS │          │  Cache   │               │
│  │Port: 5432│          │Port: 6379│               │
│  └──────────┘          └──────────┘               │
│                                                     │
│  Optional Services (profiles):                     │
│  ┌─────────────────────────────────────────────┐  │
│  │  Production Profile                         │  │
│  │  - Nginx Reverse Proxy (Port 80/443)       │  │
│  │  - Celery Worker (Background tasks)        │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
│  ┌─────────────────────────────────────────────┐  │
│  │  Monitoring Profile                         │  │
│  │  - Prometheus (Port 9090)                   │  │
│  │  - Grafana (Port 3001)                      │  │
│  └─────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Service Details

| Service | Image | Ports | Purpose |
|---------|-------|-------|---------|
| **postgres** | postgis/postgis:15-3.3 | 5432 | Database with spatial support |
| **redis** | redis:7-alpine | 6379 | Cache and WebSocket backend |
| **backend** | Custom (FastAPI) | 8000 | API server |
| **frontend** | Custom (React+Nginx) | 3000 | Web interface |
| **nginx** | nginx:1.25-alpine | 80, 443 | Reverse proxy (production) |
| **celery-worker** | Custom | - | Background tasks (production) |
| **prometheus** | prom/prometheus | 9090 | Metrics collection (monitoring) |
| **grafana** | grafana/grafana | 3001 | Dashboards (monitoring) |

---

## Configuration

### Environment File (.env)

Create a `.env` file in the project root:

```bash
# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
POSTGRES_USER=aria_user
POSTGRES_PASSWORD=secure_password_here
POSTGRES_DB=aria_dev

# ============================================================================
# SECURITY
# ============================================================================
# Generate with: openssl rand -hex 32
SECRET_KEY=your_secret_key_minimum_32_characters_long

# ============================================================================
# API KEYS
# ============================================================================
OPENAI_API_KEY=sk-proj-your-openai-key-here
GOOGLE_MAPS_API_KEY=AIzaSy-your-google-maps-key-here
TWILIO_ACCOUNT_SID=AC-your-twilio-sid-here
TWILIO_AUTH_TOKEN=your-twilio-auth-token-here
TWILIO_PHONE_NUMBER=+1234567890
SENDGRID_API_KEY=SG.your-sendgrid-key-here
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
SENDGRID_FROM_NAME=ARIA Emergency Response

# ============================================================================
# MONITORING (Optional)
# ============================================================================
GRAFANA_PASSWORD=admin_change_this
```

### Dockerfile: Backend

Located at `backend/Dockerfile`:

```dockerfile
# Multi-stage build for optimization

# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /build

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY app/ ./app/
COPY models/ ./models/

# Create non-root user
RUN useradd -m -u 1000 aria && \
    chown -R aria:aria /app
USER aria

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=40s \
  CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Dockerfile: Frontend

Located at `frontend/Dockerfile`:

```dockerfile
# Multi-stage build

# Stage 1: Build
FROM node:18-alpine as builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy source and build
COPY . .
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:1.25-alpine

# Copy built files
COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Non-root user
RUN chown -R nginx:nginx /usr/share/nginx/html && \
    chown -R nginx:nginx /var/cache/nginx && \
    chown -R nginx:nginx /var/log/nginx && \
    touch /var/run/nginx.pid && \
    chown -R nginx:nginx /var/run/nginx.pid

USER nginx

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD wget --quiet --tries=1 --spider http://localhost || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

---

## Running Services

### Basic Commands

```bash
# Start all services
docker-compose up -d

# Start with logs
docker-compose up

# Stop all services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v

# Restart specific service
docker-compose restart backend

# View logs
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend

# Check service status
docker-compose ps

# Execute command in container
docker-compose exec backend bash
docker-compose exec postgres psql -U aria_user -d aria_dev
```

### Build and Rebuild

```bash
# Build images
docker-compose build

# Build without cache
docker-compose build --no-cache

# Rebuild and restart
docker-compose up -d --build

# Rebuild specific service
docker-compose build backend
```

---

## Service Profiles

Docker Compose profiles allow you to run different service combinations.

### Development Profile (Default)

**Services:** postgres, redis, backend, frontend

```bash
docker-compose up -d
```

**Access:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

### Production Profile

**Services:** All default services + nginx + celery-worker

```bash
docker-compose --profile production up -d
```

**Additional Services:**
- **Nginx:** Reverse proxy on port 80/443
- **Celery:** Background task worker

**Access:**
- Application: http://localhost (port 80)
- HTTPS: https://localhost (port 443) - requires SSL setup

---

### Monitoring Profile

**Services:** All default services + prometheus + grafana

```bash
docker-compose --profile monitoring up -d
```

**Additional Services:**
- **Prometheus:** Metrics at http://localhost:9090
- **Grafana:** Dashboards at http://localhost:3001

**Default Grafana Credentials:**
- Username: `admin`
- Password: (from GRAFANA_PASSWORD env var, default: `admin`)

---

### Combined Profiles

Run multiple profiles together:

```bash
# Production + Monitoring
docker-compose --profile production --profile monitoring up -d
```

---

## Data Persistence

### Docker Volumes

Data is persisted in Docker volumes:

```bash
# List volumes
docker volume ls | grep aria

# Inspect volume
docker volume inspect aria_postgres_data

# Backup database
docker-compose exec postgres pg_dump -U aria_user aria_dev > backup.sql

# Restore database
cat backup.sql | docker-compose exec -T postgres psql -U aria_user aria_dev
```

### Volume Locations

```
aria_postgres_data    → /var/lib/docker/volumes/aria_postgres_data
aria_redis_data       → /var/lib/docker/volumes/aria_redis_data
aria_prometheus_data  → /var/lib/docker/volumes/aria_prometheus_data
aria_grafana_data     → /var/lib/docker/volumes/aria_grafana_data
```

### Backup Strategy

```bash
#!/bin/bash
# backup.sh

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/$DATE"
mkdir -p $BACKUP_DIR

# Backup PostgreSQL
docker-compose exec -T postgres pg_dump -U aria_user aria_dev > $BACKUP_DIR/postgres.sql

# Backup Redis
docker-compose exec -T redis redis-cli SAVE
docker cp aria-redis:/data/dump.rdb $BACKUP_DIR/redis.rdb

# Backup volumes
docker run --rm -v aria_postgres_data:/data -v $(pwd)/$BACKUP_DIR:/backup \
  alpine tar czf /backup/postgres_volume.tar.gz -C /data .

echo "✅ Backup completed: $BACKUP_DIR"
```

---

## Monitoring

### Service Health

```bash
# Check health status
docker-compose ps

# Health check for specific service
docker inspect --format='{{.State.Health.Status}}' aria-backend

# View health logs
docker inspect --format='{{range .State.Health.Log}}{{.Output}}{{end}}' aria-backend
```

### Resource Usage

```bash
# View resource usage
docker stats

# Specific services
docker stats aria-backend aria-postgres aria-redis
```

### Logs

```bash
# Tail all logs
docker-compose logs -f

# Last 100 lines
docker-compose logs --tail=100

# Specific service with timestamps
docker-compose logs -f --timestamps backend

# Search logs
docker-compose logs | grep ERROR

# Export logs
docker-compose logs > aria_logs_$(date +%Y%m%d).log
```

---

## Troubleshooting

### Service Won't Start

**Check logs:**
```bash
docker-compose logs backend
```

**Common issues:**

1. **Port already in use:**
   ```bash
   # Find process using port
   lsof -ti:8000
   
   # Kill process
   kill -9 $(lsof -ti:8000)
   
   # Or change port in docker-compose.yml
   ```

2. **Environment variables missing:**
   ```bash
   # Check if .env file exists
   ls -la .env
   
   # Verify variables are loaded
   docker-compose config
   ```

3. **Image build failed:**
   ```bash
   # Rebuild without cache
   docker-compose build --no-cache backend
   ```

---

### Database Connection Issues

**Symptoms:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solutions:**

1. Check if PostgreSQL is healthy:
   ```bash
   docker-compose ps postgres
   # State should be "Up (healthy)"
   ```

2. Wait for startup:
   ```bash
   # PostgreSQL needs time to initialize
   docker-compose logs -f postgres
   # Wait for "database system is ready to accept connections"
   ```

3. Check connection from backend:
   ```bash
   docker-compose exec backend python -c "
   from app.core.database import engine
   import asyncio
   
   async def test():
       async with engine.connect() as conn:
           result = await conn.execute('SELECT 1')
           print('✅ Connection successful')
   
   asyncio.run(test())
   "
   ```

---

### ML Models Not Loading

**Symptoms:**
```
FileNotFoundError: models/triage_classifier.pkl not found
```

**Solutions:**

1. Ensure Git LFS files are pulled:
   ```bash
   git lfs pull
   ls -lh models/
   # Files should be >1MB, not small pointers
   ```

2. Rebuild backend image:
   ```bash
   docker-compose build --no-cache backend
   ```

3. Check models directory is mounted:
   ```bash
   docker-compose exec backend ls -la models/
   ```

---

### High Memory Usage

**Check memory usage:**
```bash
docker stats --no-stream
```

**Solutions:**

1. **Limit resources in docker-compose.yml:**
   ```yaml
   services:
     backend:
       deploy:
         resources:
           limits:
             cpus: '2.0'
             memory: 2G
           reservations:
             memory: 1G
   ```

2. **Clean up unused resources:**
   ```bash
   # Remove unused images
   docker image prune -a
   
   # Remove unused volumes
   docker volume prune
   
   # Full cleanup
   docker system prune -a --volumes
   ```

---

### Container Keeps Restarting

**Check restart count:**
```bash
docker-compose ps
```

**View last logs before crash:**
```bash
docker-compose logs --tail=50 backend
```

**Disable auto-restart for debugging:**
```yaml
services:
  backend:
    restart: "no"  # Change from "unless-stopped"
```

**Interactive debugging:**
```bash
# Override entrypoint
docker-compose run --rm backend bash

# Run commands manually
python -c "from app.main import app; print('OK')"
```

---

## Advanced Usage

### Custom Docker Compose Override

Create `docker-compose.override.yml`:

```yaml
version: '3.8'

services:
  backend:
    volumes:
      - ./backend/app:/app/app  # Hot reload
    environment:
      - DEBUG=true
      - LOG_LEVEL=DEBUG
    ports:
      - "8000:8000"
      - "5678:5678"  # Debugger port
```

This file is automatically loaded with `docker-compose up`.

---

### Development with Hot Reload

```yaml
# docker-compose.dev.yml
services:
  backend:
    command: uvicorn app.main:app --reload --host 0.0.0.0
    volumes:
      - ./backend/app:/app/app
      - ./backend/models:/app/models
    environment:
      - WATCHFILES_FORCE_POLLING=true  # For Docker on some systems
```

**Run:**
```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

---

### Running Tests in Docker

```bash
# Backend tests
docker-compose exec backend pytest tests/ -v --cov=app

# Frontend tests
docker-compose exec frontend npm test

# Or run in isolated container
docker-compose run --rm backend pytest tests/
```

---

### Database Migrations

```bash
# Generate migration
docker-compose exec backend alembic revision --autogenerate -m "Add new field"

# Apply migrations
docker-compose exec backend alembic upgrade head

# Rollback
docker-compose exec backend alembic downgrade -1
```

---

### Shell Access

```bash
# Backend shell
docker-compose exec backend bash

# Python REPL
docker-compose exec backend python

# Database shell
docker-compose exec postgres psql -U aria_user -d aria_dev

# Redis shell
docker-compose exec redis redis-cli
```

---

### Network Inspection

```bash
# List networks
docker network ls | grep aria

# Inspect network
docker network inspect aria_aria-network

# Test connectivity between services
docker-compose exec backend ping postgres
docker-compose exec backend curl http://redis:6379
```

---

### Production Optimization

**1. Multi-stage builds** (already implemented)

**2. Image size optimization:**
```dockerfile
# Use slim base images
FROM python:3.11-slim

# Combine RUN commands
RUN apt-get update && apt-get install -y pkg1 pkg2 \
    && rm -rf /var/lib/apt/lists/*

# Clean up after installation
RUN pip install --no-cache-dir -r requirements.txt
```

**3. Layer caching:**
```dockerfile
# Copy requirements first (changes less frequently)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Copy code last (changes frequently)
COPY app/ ./app/
```

---

## Performance Tuning

### PostgreSQL

```yaml
services:
  postgres:
    command:
      - "postgres"
      - "-c"
      - "max_connections=200"
      - "-c"
      - "shared_buffers=256MB"
      - "-c"
      - "effective_cache_size=1GB"
      - "-c"
      - "work_mem=16MB"
```

### Redis

```yaml
services:
  redis:
    command: redis-server --maxmemory 512mb --maxmemory-policy allkeys-lru
```

### Backend

```yaml
services:
  backend:
    environment:
      - WORKERS=4  # CPU cores
      - DATABASE_POOL_SIZE=20
      - DATABASE_MAX_OVERFLOW=10
```

---

## Security Best Practices

1. **Use secrets for sensitive data:**
   ```yaml
   services:
     backend:
       secrets:
         - db_password
         - api_keys
   
   secrets:
     db_password:
       file: ./secrets/db_password.txt
   ```

2. **Run as non-root user** (already implemented)

3. **Use read-only root filesystem:**
   ```yaml
   services:
     backend:
       read_only: true
       tmpfs:
         - /tmp
   ```

4. **Drop unnecessary capabilities:**
   ```yaml
   services:
     backend:
       cap_drop:
         - ALL
       cap_add:
         - NET_BIND_SERVICE
   ```

5. **Scan images for vulnerabilities:**
   ```bash
   docker scan aria-backend:latest
   ```

---

## Quick Reference

### Essential Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Rebuild
docker-compose up -d --build

# Logs
docker-compose logs -f

# Status
docker-compose ps

# Shell
docker-compose exec backend bash

# Clean up
docker-compose down -v
docker system prune -a
```

---

## Next Steps

- [Local Setup Guide](local.md) - For non-Docker development
- [AWS Deployment Guide](../deployment/aws.md) - Deploy to AWS
- [GCP Deployment Guide](../deployment/gcp.md) - Deploy to GCP

---

**Document Version:** 1.0  
**Last Updated:** 2026-09-06  
**Maintained By:** ARIA Development Team

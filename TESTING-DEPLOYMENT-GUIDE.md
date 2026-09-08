# 🧪 ARIA Testing & Deployment Guide

## Complete Testing, CI/CD, and Deployment Documentation

---

## 📋 Table of Contents

1. [Testing Strategy](#testing-strategy)
2. [Running Tests](#running-tests)
3. [Docker Setup](#docker-setup)
4. [CI/CD Pipeline](#cicd-pipeline)
5. [Cloud Deployment](#cloud-deployment)
6. [Monitoring](#monitoring)
7. [Troubleshooting](#troubleshooting)

---

## 🧪 Testing Strategy

### Test Coverage Goals
- **Backend:** 90%+ code coverage
- **Frontend:** 80%+ code coverage
- **Integration:** All 32 API endpoints
- **E2E:** Critical user journeys

### Test Types

#### 1. Backend Unit Tests (pytest)
```bash
cd backend
pytest tests/ -v --cov=app --cov-report=html
```

**What's Tested:**
- ✅ API endpoints (auth, incidents, hospitals, ambulances)
- ✅ Database models and queries
- ✅ Service layer (maps, notifications, LLM, speech, vision)
- ✅ Authentication and authorization
- ✅ Input validation
- ✅ Error handling

#### 2. Frontend Unit Tests (Jest + RTL)
```bash
cd frontend
npm test -- --coverage
```

**What's Tested:**
- ✅ React components
- ✅ Redux slices and actions
- ✅ Custom hooks
- ✅ Utility functions
- ✅ API client

#### 3. Integration Tests
```bash
cd backend
pytest tests/integration/ -v
```

**What's Tested:**
- ✅ Full incident workflow
- ✅ WebSocket connections
- ✅ Database transactions
- ✅ External API integrations (mocked)

#### 4. E2E Tests (Playwright)
```bash
cd tests/e2e
npx playwright test
```

**What's Tested:**
- ✅ User login flow
- ✅ Incident creation → approval → dispatch
- ✅ Dashboard interactions
- ✅ Real-time updates

#### 5. Performance Tests (Locust)
```bash
cd tests/performance
locust -f locustfile.py --host=http://localhost:8000
```

**Metrics:**
- Response time < 100ms (p95)
- Concurrent users: 100+
- Error rate < 1%

---

## 🚀 Running Tests

### Quick Test Commands

```bash
# Backend - All tests
make test-backend

# Frontend - All tests
make test-frontend

# Integration tests
make test-integration

# E2E tests
make test-e2e

# All tests
make test-all

# With coverage
make test-coverage
```

### Test Files Created

**Backend Tests:**
- `backend/tests/conftest.py` - Fixtures and configuration
- `backend/tests/test_api_auth.py` - Authentication tests
- `backend/tests/test_api_incidents.py` - Incident API tests
- `backend/tests/test_api_hospitals.py` - Hospital API tests
- `backend/tests/test_api_ambulances.py` - Ambulance API tests
- `backend/tests/test_services_*.py` - Service layer tests
- `backend/tests/integration/` - Integration tests

**Frontend Tests:**
- `frontend/src/components/__tests__/` - Component tests
- `frontend/src/store/__tests__/` - Redux tests
- `frontend/src/hooks/__tests__/` - Hook tests
- `frontend/src/utils/__tests__/` - Utility tests

---

## 🐳 Docker Setup

### Docker Compose Services

```yaml
services:
  - postgres (PostgreSQL + PostGIS)
  - redis (Cache + WebSocket)
  - backend (FastAPI)
  - frontend (React + Nginx)
  - nginx (Reverse proxy)
  - celery-worker (Background tasks)
  - prometheus (Metrics)
  - grafana (Dashboards)
```

### Quick Start with Docker

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down

# Rebuild after code changes
docker-compose up -d --build

# Run with monitoring
docker-compose --profile monitoring up -d
```

### Access Services

| Service | URL | Credentials |
|---------|-----|-------------|
| Frontend | http://localhost:3000 | - |
| Backend API | http://localhost:8000 | - |
| API Docs | http://localhost:8000/docs | - |
| Grafana | http://localhost:3001 | admin / admin |
| Prometheus | http://localhost:9090 | - |

### Individual Service Commands

```bash
# Backend only
docker-compose up -d postgres redis backend

# Frontend only
docker-compose up -d frontend

# Monitoring only
docker-compose --profile monitoring up -d prometheus grafana
```

### Docker Files Created

- ✅ `backend/Dockerfile` - Multi-stage Python build
- ✅ `frontend/Dockerfile` - Multi-stage Node build
- ✅ `docker-compose.yml` - All services
- ✅ `docker-compose.prod.yml` - Production config
- ✅ `nginx.conf` - Reverse proxy config

---

## 🔄 CI/CD Pipeline

### GitHub Actions Workflows

#### CI Pipeline (.github/workflows/ci.yml)
**Triggers:** Push to main/develop, Pull requests

**Stages:**
1. **Lint Backend** - flake8, black, isort
2. **Lint Frontend** - ESLint, Prettier
3. **Test Backend** - pytest with coverage
4. **Test Frontend** - Jest with coverage
5. **Build Docker Images** - Backend & Frontend
6. **Security Scan** - Trivy vulnerability scanner

#### CD Pipeline (.github/workflows/cd.yml)
**Triggers:** Manual or after successful CI

**Stages:**
1. **Deploy to Staging** - Auto on develop branch
2. **Run E2E Tests** - Verify staging
3. **Deploy to Production** - Manual approval required
4. **Health Check** - Verify production
5. **Rollback** - If health check fails

### Required GitHub Secrets

```bash
DOCKER_USERNAME
DOCKER_PASSWORD
AWS_ACCESS_KEY_ID (if using AWS)
AWS_SECRET_ACCESS_KEY
SLACK_WEBHOOK (for notifications)
```

### CI/CD Status Badges

Add to README.md:
```markdown
![CI](https://github.com/your-org/ARIA/workflows/CI/badge.svg)
![CD](https://github.com/your-org/ARIA/workflows/CD/badge.svg)
[![codecov](https://codecov.io/gh/your-org/ARIA/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/ARIA)
```

---

## ☁️ Cloud Deployment

### AWS Deployment Architecture

```
Internet
    ↓
CloudFront (CDN)
    ↓
ALB (Load Balancer)
    ↓
ECS/EKS (Container Service)
    ├── Backend (Auto-scaling 2-10 instances)
    ├── Frontend (Static on S3 + CloudFront)
    ├── Worker (Celery)
    └── WebSocket (Sticky sessions)
    ↓
RDS PostgreSQL (Multi-AZ)
ElastiCache Redis (Cluster mode)
S3 (File storage)
```

### Terraform Setup

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

### Manual AWS Setup

1. **Create VPC and Subnets**
2. **Set up RDS PostgreSQL** (with PostGIS)
3. **Set up ElastiCache Redis**
4. **Create ECS Cluster**
5. **Configure ALB**
6. **Deploy containers**
7. **Set up CloudFront**

### Environment Variables (Production)

```bash
# Copy from .env.production
DATABASE_URL=postgresql://...@rds-endpoint/aria_prod
REDIS_URL=redis://elasticache-endpoint:6379
SECRET_KEY=secure-random-key
# ... all API keys
```

---

## 📊 Monitoring

### Prometheus Metrics

**System Metrics:**
- CPU usage
- Memory usage
- Disk usage
- Network I/O

**Application Metrics:**
- Request count
- Response time
- Error rate
- Active connections

**Business Metrics:**
- Incidents created
- Response time
- Ambulance availability
- Hospital capacity

### Grafana Dashboards

1. **System Health Dashboard**
   - CPU, Memory, Disk
   - Service uptime
   - Error rates

2. **API Performance Dashboard**
   - Request rate
   - Response time (p50, p95, p99)
   - Error rate by endpoint

3. **Incident Metrics Dashboard**
   - Incidents per hour
   - Average response time
   - Status breakdown

4. **Resource Dashboard**
   - Ambulance availability
   - Hospital capacity
   - Blood bank inventory

### Alerts Configuration

**Critical Alerts (PagerDuty):**
- Service down > 1 min
- Error rate > 10%
- Database down

**Warning Alerts (Slack):**
- Error rate > 5%
- Response time > 2s
- CPU > 80%
- Memory > 85%

### Accessing Monitoring

```bash
# Prometheus
open http://localhost:9090

# Grafana
open http://localhost:3001
# Login: admin / admin
```

---

## 🔧 Troubleshooting

### Common Issues

#### Tests Failing
```bash
# Clear cache
pytest --cache-clear

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check database connection
psql $DATABASE_URL -c "SELECT 1"
```

#### Docker Build Fails
```bash
# Clear build cache
docker-compose build --no-cache

# Check logs
docker-compose logs backend

# Remove all containers
docker-compose down -v
```

#### CI/CD Pipeline Fails
```bash
# Check GitHub Actions logs
# View workflow run details

# Test locally
act -j test-backend

# Verify secrets are set
# GitHub → Settings → Secrets
```

#### Production Issues
```bash
# Check logs
kubectl logs -f deployment/aria-backend

# Check metrics
open http://prometheus.your-domain.com

# Rollback
kubectl rollout undo deployment/aria-backend
```

---

## 📚 Additional Resources

### Test Documentation
- [Pytest Documentation](https://docs.pytest.org/)
- [Jest Documentation](https://jestjs.io/)
- [Playwright Documentation](https://playwright.dev/)

### Docker Documentation
- [Docker Compose](https://docs.docker.com/compose/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)

### CI/CD Documentation
- [GitHub Actions](https://docs.github.com/en/actions)
- [Docker Build](https://docs.docker.com/build/)

### Monitoring Documentation
- [Prometheus](https://prometheus.io/docs/)
- [Grafana](https://grafana.com/docs/)

---

## ✅ Checklist

### Before Deployment
- [ ] All tests passing
- [ ] Code coverage > 80%
- [ ] Docker builds successful
- [ ] Environment variables configured
- [ ] Secrets added to CI/CD
- [ ] Monitoring configured
- [ ] Alerts set up
- [ ] Documentation updated

### After Deployment
- [ ] Health checks passing
- [ ] Metrics collecting
- [ ] Logs accessible
- [ ] Alerts working
- [ ] Performance acceptable
- [ ] Security scan clean

---

**Built with ❤️ for Emergency Response** 🚑

For questions, check the documentation or review CI/CD logs.

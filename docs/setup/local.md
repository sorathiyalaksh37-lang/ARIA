# ARIA Local Development Setup Guide

## Overview

This guide will help you set up the ARIA Emergency Response Platform on your local development machine.

**Estimated Setup Time:** 30-45 minutes

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Requirements](#system-requirements)
3. [Installation Steps](#installation-steps)
4. [Configuration](#configuration)
5. [Running the Application](#running-the-application)
6. [Verification](#verification)
7. [Development Workflow](#development-workflow)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required Software

| Software | Version | Purpose | Download Link |
|----------|---------|---------|---------------|
| **Python** | 3.11+ | Backend runtime | https://www.python.org/downloads/ |
| **Node.js** | 18+ LTS | Frontend build | https://nodejs.org/ |
| **PostgreSQL** | 14+ | Database | https://www.postgresql.org/download/ |
| **PostGIS** | 3.3+ | Spatial extension | Included with PostgreSQL |
| **Redis** | 7.0+ | Cache & sessions | https://redis.io/download/ |
| **Git** | Latest | Version control | https://git-scm.com/downloads |
| **Git LFS** | Latest | Large file storage | https://git-lfs.github.com/ |

### Optional Tools

- **pgAdmin** - PostgreSQL GUI
- **RedisInsight** - Redis GUI
- **Postman** - API testing
- **VS Code** - Code editor (recommended)

---

## System Requirements

### Minimum Requirements

- **OS:** macOS 12+, Ubuntu 20.04+, Windows 10+ (WSL2)
- **CPU:** 4 cores (2.0 GHz)
- **RAM:** 8 GB
- **Disk:** 10 GB free space
- **Network:** Stable internet connection

### Recommended Requirements

- **CPU:** 8 cores (2.5 GHz+)
- **RAM:** 16 GB
- **Disk:** 20 GB SSD
- **Network:** High-speed internet for API calls

---

## Installation Steps

### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/sorathiyalaksh37-lang/ARIA.git
cd ARIA

# Install Git LFS (if not already installed)
git lfs install

# Pull LFS files (ML models)
git lfs pull
```

**Verify:**
```bash
ls -lh models/
# Should show model files (~182 MB total)
```

---

### Step 2: Install PostgreSQL and PostGIS

#### macOS (Homebrew)

```bash
# Install PostgreSQL
brew install postgresql@14

# Install PostGIS
brew install postgis

# Start PostgreSQL service
brew services start postgresql@14

# Verify installation
psql --version
# Expected: psql (PostgreSQL) 14.x
```

#### Ubuntu/Debian

```bash
# Add PostgreSQL repository
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -

# Install PostgreSQL and PostGIS
sudo apt update
sudo apt install -y postgresql-14 postgresql-14-postgis-3

# Start PostgreSQL
sudo systemctl start postgresql
sudo systemctl enable postgresql
```

#### Windows (WSL2)

Follow Ubuntu instructions above in WSL2 environment.

---

### Step 3: Create Database

```bash
# Create database user
sudo -u postgres createuser -s aria_user

# Set password for user
sudo -u postgres psql -c "ALTER USER aria_user PASSWORD 'aria_password';"

# Create database
sudo -u postgres createdb -O aria_user aria_dev

# Enable PostGIS extension
sudo -u postgres psql -d aria_dev -c "CREATE EXTENSION postgis;"

# Verify PostGIS installation
sudo -u postgres psql -d aria_dev -c "SELECT PostGIS_Version();"
```

**Expected Output:**
```
         postgis_version          
---------------------------------
 3.3 USE_GEOS=1 USE_PROJ=1 ...
```

---

### Step 4: Install Redis

#### macOS (Homebrew)

```bash
# Install Redis
brew install redis

# Start Redis service
brew services start redis

# Verify
redis-cli ping
# Expected: PONG
```

#### Ubuntu/Debian

```bash
# Install Redis
sudo apt install -y redis-server

# Start Redis
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Verify
redis-cli ping
```

---

### Step 5: Backend Setup

```bash
# Navigate to backend directory
cd /path/to/ARIA/backend

# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows (WSL):
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
# Expected: fastapi 0.109.0
```

---

### Step 6: Frontend Setup

```bash
# Navigate to frontend directory
cd /path/to/ARIA/frontend

# Install dependencies
npm install

# Verify installation
npm list react
# Expected: react@18.2.0
```

---

## Configuration

### Step 1: Backend Environment Variables

```bash
# Copy example env file
cd backend
cp .env.example .env

# Edit .env file
nano .env  # or use your preferred editor
```

**Required Configuration:**

```bash
# Database
DATABASE_URL=postgresql+asyncpg://aria_user:aria_password@localhost:5432/aria_dev

# Redis
REDIS_URL=redis://localhost:6379/0

# Security (generate a secure key)
SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))")

# OpenAI API Key
OPENAI_API_KEY=sk-your-actual-openai-key-here

# Google Maps API Key
GOOGLE_MAPS_API_KEY=AIza-your-actual-google-maps-key-here

# Twilio (SMS)
TWILIO_ACCOUNT_SID=AC-your-twilio-sid-here
TWILIO_AUTH_TOKEN=your-twilio-auth-token-here
TWILIO_PHONE_NUMBER=+1234567890

# SendGrid (Email)
SENDGRID_API_KEY=SG.your-sendgrid-key-here
SENDGRID_FROM_EMAIL=noreply@yourdomain.com
SENDGRID_FROM_NAME=ARIA Emergency Response
```

**Get API Keys:**

1. **OpenAI:** https://platform.openai.com/api-keys
   - Create account → API keys → Create new key
   - Required models: GPT-4, Whisper, GPT-4V

2. **Google Maps:** https://console.cloud.google.com/apis/credentials
   - Create project → Enable APIs:
     - Geocoding API
     - Directions API
     - Distance Matrix API
     - Places API
   - Create credentials → API key
   - **Important:** Enable billing on Google Cloud

3. **Twilio:** https://console.twilio.com/
   - Sign up → Get trial account
   - Copy Account SID and Auth Token
   - Get a phone number

4. **SendGrid:** https://app.sendgrid.com/settings/api_keys
   - Sign up → Create API Key
   - Set permissions: Full Access

---

### Step 2: Frontend Environment Variables

```bash
# Copy example env file
cd frontend
cp .env.example .env.development

# Edit .env.development
nano .env.development
```

**Configuration:**

```bash
# API endpoints
REACT_APP_API_BASE_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/api/v1/ws

# Google Maps (same key as backend)
REACT_APP_GOOGLE_MAPS_API_KEY=AIza-your-actual-google-maps-key-here

# Environment
NODE_ENV=development
```

---

### Step 3: Database Initialization

```bash
# Navigate to backend
cd backend
source venv/bin/activate

# Create tables (run Python script)
python -c "
from app.core.database import engine, Base
from app.models import *
import asyncio

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print('✅ Database tables created')

asyncio.run(init_db())
"
```

**Alternative: Using Alembic (recommended for production)**

```bash
# Initialize Alembic (first time only)
alembic init alembic

# Generate initial migration
alembic revision --autogenerate -m "Initial schema"

# Apply migration
alembic upgrade head
```

---

### Step 4: Load Sample Data (Optional)

```bash
# Load sample hospitals, ambulances
cd backend
python scripts/load_sample_data.py

# Verify
psql -U aria_user -d aria_dev -c "SELECT COUNT(*) FROM hospitals;"
psql -U aria_user -d aria_dev -c "SELECT COUNT(*) FROM ambulances;"
```

---

## Running the Application

### Method 1: Separate Terminals (Recommended for Development)

**Terminal 1: Backend**

```bash
cd /path/to/ARIA/backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 --log-level info
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [xxxxx] using WatchFiles
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     ✅ PostgreSQL connected
INFO:     ✅ Redis connected
INFO:     ✅ ML models loaded (5/5)
INFO:     Application startup complete.
```

**Terminal 2: Frontend**

```bash
cd /path/to/ARIA/frontend
npm start
```

**Expected Output:**
```
Compiled successfully!

You can now view aria-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000

Note that the development build is not optimized.
To create a production build, use npm run build.

webpack compiled successfully
```

---

### Method 2: Using Shell Script

```bash
# Make script executable
chmod +x start-dev.sh

# Run
./start-dev.sh
```

**Contents of `start-dev.sh`:**
```bash
#!/bin/bash

# Start backend in background
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend in background
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "✅ Backend running on http://localhost:8000"
echo "✅ Frontend running on http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
```

---

## Verification

### 1. Backend Health Check

```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "database": "connected",
  "redis": "connected",
  "ml_models": {
    "loaded": 5,
    "models": [
      "triage_classifier",
      "hospital_ranker",
      "resource_predictor",
      "eta_predictor",
      "hotspot_predictor"
    ]
  },
  "timestamp": "2026-09-06T10:30:00Z"
}
```

---

### 2. API Documentation

Open browser and navigate to:

- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **OpenAPI JSON:** http://localhost:8000/openapi.json

---

### 3. Test Authentication

```bash
# Register a user
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "Test123!@#",
    "full_name": "Test User",
    "role": "dispatcher"
  }'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Test123!@#"
  }'
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "expires_in": 1800,
  "user": {
    "id": 1,
    "username": "testuser",
    "email": "test@example.com",
    "role": "dispatcher"
  }
}
```

---

### 4. Test WebSocket Connection

**JavaScript (Browser Console):**

```javascript
const ws = new WebSocket('ws://localhost:8000/api/v1/ws?token=YOUR_ACCESS_TOKEN&channels=incidents');

ws.onopen = () => {
  console.log('✅ WebSocket connected');
};

ws.onmessage = (event) => {
  console.log('📨 Message:', JSON.parse(event.data));
};

ws.onerror = (error) => {
  console.error('❌ WebSocket error:', error);
};
```

---

### 5. Test ML Service

```bash
cd backend
source venv/bin/activate

python << EOF
import asyncio
from app.services.ml_service import get_ml_service

async def test():
    ml = get_ml_service()
    
    # Test triage prediction
    result = await ml.predict_severity(
        description="Car accident with multiple injuries",
        location="Mumbai, India",
        incident_type="ACCIDENT"
    )
    
    print("✅ Triage Prediction:")
    print(f"   Severity: {result['severity']}")
    print(f"   Confidence: {result['confidence']:.2%}")

asyncio.run(test())
EOF
```

---

### 6. Frontend Verification

1. Open http://localhost:3000 in browser
2. You should see the ARIA dashboard
3. Check browser console for errors (should be none)
4. Try logging in with test credentials

---

## Development Workflow

### Hot Reload

Both backend and frontend support hot reload:

**Backend:**
- Edit Python files in `backend/app/`
- Uvicorn automatically restarts
- See changes immediately

**Frontend:**
- Edit React files in `frontend/src/`
- Webpack automatically recompiles
- Browser automatically refreshes

---

### Database Migrations

When you change database models:

```bash
cd backend
source venv/bin/activate

# Generate migration
alembic revision --autogenerate -m "Description of change"

# Review generated migration in alembic/versions/

# Apply migration
alembic upgrade head

# Rollback if needed
alembic downgrade -1
```

---

### Running Tests

**Backend Tests:**

```bash
cd backend
source venv/bin/activate
pytest tests/ -v --cov=app
```

**Frontend Tests:**

```bash
cd frontend
npm test
```

---

### Code Formatting

**Backend (Python):**

```bash
cd backend
source venv/bin/activate

# Format with black
black app/

# Sort imports
isort app/

# Lint
flake8 app/
```

**Frontend (TypeScript):**

```bash
cd frontend

# Format
npm run format

# Lint
npm run lint
```

---

## Troubleshooting

### Issue: PostgreSQL Connection Refused

**Symptoms:**
```
sqlalchemy.exc.OperationalError: could not connect to server
```

**Solutions:**

1. Check if PostgreSQL is running:
   ```bash
   # macOS
   brew services list | grep postgresql
   
   # Linux
   sudo systemctl status postgresql
   ```

2. Check connection details:
   ```bash
   psql -U aria_user -d aria_dev
   # If this works, check DATABASE_URL in .env
   ```

3. Check PostgreSQL logs:
   ```bash
   # macOS
   tail -f /usr/local/var/log/postgresql@14.log
   
   # Linux
   sudo tail -f /var/log/postgresql/postgresql-14-main.log
   ```

---

### Issue: Redis Connection Error

**Symptoms:**
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solutions:**

1. Check if Redis is running:
   ```bash
   redis-cli ping
   # Expected: PONG
   ```

2. Start Redis:
   ```bash
   # macOS
   brew services start redis
   
   # Linux
   sudo systemctl start redis-server
   ```

3. Check Redis logs:
   ```bash
   # macOS
   tail -f /usr/local/var/log/redis.log
   
   # Linux
   sudo tail -f /var/log/redis/redis-server.log
   ```

---

### Issue: ML Models Not Loading

**Symptoms:**
```
FileNotFoundError: [Errno 2] No such file or directory: '../models/triage_classifier.pkl'
```

**Solutions:**

1. Verify Git LFS installation:
   ```bash
   git lfs install
   git lfs pull
   ```

2. Check model files:
   ```bash
   ls -lh models/
   # Should see .pkl files, not pointers
   ```

3. If files are small (<1KB), they're LFS pointers:
   ```bash
   # Re-pull LFS files
   git lfs fetch --all
   git lfs checkout
   ```

---

### Issue: Port Already in Use

**Symptoms:**
```
OSError: [Errno 48] Address already in use
```

**Solutions:**

1. Find process using port:
   ```bash
   # macOS/Linux
   lsof -ti:8000  # for backend
   lsof -ti:3000  # for frontend
   ```

2. Kill process:
   ```bash
   kill -9 $(lsof -ti:8000)
   ```

3. Or use different port:
   ```bash
   uvicorn app.main:app --port 8001
   ```

---

### Issue: OpenAI API Key Invalid

**Symptoms:**
```
openai.error.AuthenticationError: Incorrect API key provided
```

**Solutions:**

1. Verify API key:
   - Go to https://platform.openai.com/api-keys
   - Check if key is active
   - Check usage limits

2. Test key directly:
   ```bash
   curl https://api.openai.com/v1/models \
     -H "Authorization: Bearer YOUR_API_KEY"
   ```

3. Check .env file:
   ```bash
   grep OPENAI_API_KEY backend/.env
   # Should not have quotes or spaces
   ```

---

### Issue: Google Maps API Not Working

**Symptoms:**
```
google.maps.error: The provided API key is invalid
```

**Solutions:**

1. Enable required APIs:
   - Geocoding API
   - Directions API
   - Distance Matrix API
   - Places API

2. Check API restrictions:
   - Go to Google Cloud Console
   - APIs & Services → Credentials
   - Edit API key → Remove restrictions for testing

3. Verify billing is enabled:
   - Google Cloud Console → Billing
   - Enable billing account

---

### Issue: Frontend Not Loading

**Symptoms:**
- Blank page
- Console errors about API connection

**Solutions:**

1. Check backend is running:
   ```bash
   curl http://localhost:8000/health
   ```

2. Check environment variables:
   ```bash
   cat frontend/.env.development
   # Verify REACT_APP_API_BASE_URL is correct
   ```

3. Clear browser cache and rebuild:
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   npm start
   ```

---

## Next Steps

After successful setup:

1. **Read Documentation**
   - [API Guide](../../BACKEND-API-GUIDE.md)
   - [Architecture Overview](../architecture/overview.md)
   - [Contributing Guide](../contributing.md)

2. **Explore Features**
   - Test incident creation workflow
   - Monitor agent execution
   - Check real-time updates

3. **Start Development**
   - Pick a feature from issues
   - Create a branch
   - Make changes and test
   - Submit pull request

---

## Quick Reference

### Essential Commands

```bash
# Start backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Start frontend
cd frontend && npm start

# Run tests
cd backend && pytest tests/ -v
cd frontend && npm test

# Check health
curl http://localhost:8000/health

# View API docs
open http://localhost:8000/docs

# View frontend
open http://localhost:3000

# Database shell
psql -U aria_user -d aria_dev

# Redis shell
redis-cli

# View logs
tail -f backend/logs/aria.log
```

---

## Support

- **Documentation:** `/docs` directory
- **API Docs:** http://localhost:8000/docs
- **Issues:** GitHub Issues
- **Discussions:** GitHub Discussions

---

**Happy coding! 🚀**

**Document Version:** 1.0  
**Last Updated:** 2026-09-06  
**Maintained By:** ARIA Development Team

# 🚀 ARIA Quick Start Guide

This guide will help you start the ARIA Emergency Response System in under 5 minutes!

## Prerequisites

✅ **You have:**
- Python 3.14 installed
- Node.js v25.4 installed
- Docker Desktop installed
- Git repository cloned

## 🎯 Quick Start (Recommended)

### Option 1: Using the Startup Script (Easiest)

```bash
# Make the script executable (first time only)
chmod +x start-project.sh stop-project.sh

# Start the entire system
./start-project.sh
```

This will:
- ✅ Start Docker Desktop (if not running)
- ✅ Start PostgreSQL database
- ✅ Start Redis cache
- ✅ Install Python dependencies
- ✅ Start FastAPI backend on http://localhost:8000
- ✅ Install Node.js dependencies
- ✅ Start React frontend on http://localhost:3000

**Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

**To stop everything:**
```bash
./stop-project.sh
```

---

### Option 2: Using Docker Compose

```bash
# Start all services with Docker
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Stop all services
docker-compose down
```

---

### Option 3: Manual Setup (Step by Step)

#### 1. Start Infrastructure Services

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis

# Verify they're running
docker-compose ps
```

#### 2. Start Backend

```bash
cd backend

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start the backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Backend will be available at: http://localhost:8000

#### 3. Start Frontend (in a new terminal)

```bash
cd frontend

# Install dependencies (first time only)
npm install

# Start the frontend
npm start
```

Frontend will be available at: http://localhost:3000

---

## 📊 Verify Installation

### Check Backend
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2024-...",
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

### Check Frontend
Open your browser to http://localhost:3000 and you should see the ARIA dashboard.

---

## 🔍 Troubleshooting

### Docker Issues
```bash
# Check if Docker is running
docker info

# If not, start Docker Desktop manually
open -a Docker

# Wait 30 seconds and try again
```

### Database Connection Issues
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Backend Issues
```bash
# Check backend logs
tail -f logs/backend.log

# Or if running manually, check the terminal output
```

### Frontend Issues
```bash
# Check frontend logs
tail -f logs/frontend.log

# Clear node_modules and reinstall
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or for port 3000
lsof -i :3000
kill -9 <PID>
```

---

## 🧪 Test the System

### Create a Test Incident

1. Open http://localhost:3000
2. Click "Report Incident"
3. Fill in the form:
   - **Location:** Any address
   - **Severity:** Critical
   - **Description:** "Traffic accident with injuries"
4. Click "Submit"
5. Watch the AI agents process the incident in real-time!

### Test the API

```bash
# Create an incident via API
curl -X POST http://localhost:8000/api/v1/incidents \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Downtown",
    "severity": "critical",
    "description": "Medical emergency",
    "latitude": 40.7128,
    "longitude": -74.0060
  }'
```

---

## 📚 Next Steps

1. **Explore the Documentation:**
   - Architecture: `docs/architecture/overview.md`
   - API Guide: `BACKEND-API-GUIDE.md`
   - Setup Details: `docs/setup/local.md`

2. **Configure API Keys:**
   - See `SETUP-API-KEYS.md` for required API keys
   - Edit `backend/.env` with your keys

3. **Run Tests:**
   ```bash
   # Backend tests
   cd backend
   pytest

   # Frontend tests
   cd frontend
   npm test
   ```

4. **View ML Model Performance:**
   - See `ML-MODELS-ACCURACY-REPORT.md`

---

## 🛠️ Useful Commands

### View All Services
```bash
docker-compose ps
```

### View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f postgres
```

### Restart Services
```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
```

### Database Commands
```bash
# Access PostgreSQL
docker-compose exec postgres psql -U aria_user -d aria_dev

# Run SQL query
docker-compose exec postgres psql -U aria_user -d aria_dev -c "SELECT COUNT(*) FROM incidents;"
```

### Redis Commands
```bash
# Access Redis CLI
docker-compose exec redis redis-cli

# Check Redis keys
docker-compose exec redis redis-cli KEYS '*'
```

---

## 🎉 Success!

You now have ARIA running locally! The system is processing emergency incidents with:
- 🧠 5 ML models for intelligent predictions
- 🤖 14 AI agents orchestrated by LangGraph
- 📍 Real-time tracking and resource allocation
- 💬 WebSocket updates
- 🗺️ Interactive maps

**Need help?** Check the full documentation in the `/docs` folder or see `README.md`.

---

## 🔐 Default Credentials

**Database:**
- Host: localhost
- Port: 5432
- Database: aria_dev
- Username: aria_user
- Password: aria_password

**Redis:**
- Host: localhost
- Port: 6379
- Database: 0

---

**Happy Emergency Response Managing! 🚑🏥**

# ARIA Backend API - Complete Usage Guide

**Version:** 1.0.0  
**Status:** Phase 3 - 60% Complete  
**Date:** August 24, 2026

---

## 🎯 What's Been Added

### ✅ New Features (Just Implemented)

1. **Complete ML Service Integration** (`app/services/ml_service.py`)
   - Loads all 5 trained models on startup
   - Async prediction methods
   - Caching for performance
   - Health checks for each model
   - Error handling and fallbacks

2. **Authentication System** (`app/api/v1/auth.py`)
   - User registration
   - Login with JWT tokens
   - Token refresh mechanism
   - Get current user info
   - Change password
   - Logout

3. **WebSocket Real-Time Updates** (`app/api/v1/websocket.py`)
   - Live dashboard updates
   - Incident status changes
   - Ambulance GPS tracking
   - AI agent execution status
   - Hospital availability
   - Connection management
   - Heartbeat mechanism
   - Channel subscriptions

---

## 📊 Current API Status

| Endpoint Category | Status | Endpoints |
|-------------------|--------|-----------|
| **Authentication** | ✅ Complete | 6 endpoints |
| **Incidents** | ✅ Complete | 9 endpoints |
| **WebSocket** | ✅ Complete | Real-time updates |
| **ML Predictions** | ✅ Service Ready | 5 models integrated |
| Hospitals | ❌ TODO | 0/6 |
| Ambulances | ❌ TODO | 0/6 |
| Dashboard | ❌ TODO | 0/5 |
| Blood Banks | ❌ TODO | 0/4 |

**Total:** 15 working endpoints + WebSocket + ML service

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Setup Database

```bash
# Create PostgreSQL database
createdb aria_db

# Enable PostGIS
psql aria_db -c "CREATE EXTENSION postgis;"
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 4. Run Server

```bash
uvicorn app.main:app --reload --port 8000
```

### 5. Access API Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔐 Authentication Flow

### 1. Register User

```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "testuser",
    "password": "SecurePass123!",
    "full_name": "Test User",
    "role": "DISPATCHER"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "User registered successfully",
  "data": {
    "user_id": "uuid",
    "username": "testuser",
    "email": "user@example.com"
  }
}
```

### 2. Login

```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "SecurePass123!"
  }'
```

**Response:**
```json
{
  "success": true,
  "message": "Login successful",
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

### 3. Use Token

Add to request headers:
```
Authorization: Bearer YOUR_ACCESS_TOKEN
```

### 4. Refresh Token

```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Authorization: Bearer YOUR_REFRESH_TOKEN"
```

---

## 📡 WebSocket Real-Time Updates

### Connect to WebSocket

```javascript
// JavaScript example
const token = "YOUR_JWT_ACCESS_TOKEN";
const channels = "dashboard,incidents,ambulances";

const ws = new WebSocket(
  `ws://localhost:8000/api/v1/ws?token=${token}&channels=${channels}`
);

ws.onopen = () => {
  console.log('Connected to ARIA real-time updates');
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Event:', message.type);
  console.log('Data:', message.data);
  
  // Handle different event types
  switch(message.type) {
    case 'incident.created':
      updateIncidentList(message.data);
      break;
    case 'ambulance.location_updated':
      updateAmbulanceMarker(message.data);
      break;
    case 'agent.completed':
      showNotification(message.data);
      break;
  }
};

ws.onerror = (error) => {
  console.error('WebSocket error:', error);
};

ws.onclose = () => {
  console.log('Disconnected from ARIA');
  // Implement reconnection logic
};
```

### Python Example

```python
import websockets
import json
import asyncio

async def connect_to_aria():
    token = "YOUR_JWT_ACCESS_TOKEN"
    uri = f"ws://localhost:8000/api/v1/ws?token={token}&channels=incidents"
    
    async with websockets.connect(uri) as websocket:
        print("Connected to ARIA")
        
        # Listen for messages
        while True:
            message = await websocket.recv()
            data = json.loads(message)
            print(f"Received: {data['type']}")
            print(f"Data: {data['data']}")

asyncio.run(connect_to_aria())
```

### Available Channels

| Channel | Events | Description |
|---------|--------|-------------|
| **dashboard** | stats_updated | Overall system statistics |
| **incidents** | created, updated, dispatched, plan.generated, plan.approved | Incident lifecycle events |
| **ambulances** | location_updated, status_changed | Real-time ambulance tracking |
| **agents** | started, completed, failed | AI agent execution status |
| **hospitals** | availability_changed | Hospital capacity updates |

### Event Types

#### Incidents
```javascript
// incident.created
{
  "type": "incident.created",
  "data": {
    "incident_id": "uuid",
    "incident_code": "INC-20260824160000",
    "severity": "CRITICAL",
    "location": {...},
    "timestamp": "2026-08-24T16:00:00Z"
  }
}

// incident.dispatched
{
  "type": "incident.dispatched",
  "data": {
    "incident_id": "uuid",
    "ambulance_id": "uuid",
    "hospital_id": "uuid",
    "eta_minutes": 15
  }
}
```

#### Ambulances
```javascript
// ambulance.location_updated
{
  "type": "ambulance.location_updated",
  "data": {
    "ambulance_id": "uuid",
    "latitude": 19.0760,
    "longitude": 72.8777,
    "speed": 45,
    "heading": 180,
    "timestamp": "2026-08-24T16:00:00Z"
  }
}
```

#### AI Agents
```javascript
// agent.completed
{
  "type": "agent.completed",
  "data": {
    "agent": "TriageAgent",
    "status": "completed",
    "incident_id": "uuid",
    "result": {
      "severity": "CRITICAL",
      "confidence": 0.98
    }
  }
}
```

---

## 🤖 ML Predictions API

The ML service is automatically loaded on startup. Use these methods in your endpoints:

### In Your Endpoint Code

```python
from app.services.ml_service import get_ml_service
from fastapi import Depends

@router.post("/predict-severity")
async def predict_severity(
    description: str,
    ml_service: MLService = Depends(get_ml_service)
):
    result = await ml_service.predict_severity(description)
    return result
```

### Available Prediction Methods

#### 1. Predict Severity

```python
result = await ml_service.predict_severity(
    description="Patient with chest pain and difficulty breathing",
    location="Mumbai",
    incident_type="MEDICAL"
)

# Returns:
{
    "severity": "CRITICAL",
    "confidence": 0.98,
    "probabilities": {
        "CRITICAL": 0.98,
        "HIGH": 0.015,
        "MODERATE": 0.004,
        "LOW": 0.001
    },
    "model_version": "1.0"
}
```

#### 2. Rank Hospitals

```python
ranked = await ml_service.rank_hospitals(
    incident_lat=19.0760,
    incident_lon=72.8777,
    severity="CRITICAL",
    hospitals=hospital_list,
    top_k=10
)

# Returns: List of top 10 hospitals with rank_score
```

#### 3. Predict ETA

```python
eta = await ml_service.predict_eta(
    origin_lat=19.0760,
    origin_lon=72.8777,
    dest_lat=19.1136,
    dest_lon=72.8697,
    traffic_level="HIGH",
    weather="RAIN"
)

# Returns:
{
    "eta_minutes": 18.5,
    "eta_seconds": 1110,
    "confidence_interval": {
        "lower": 15.7,
        "upper": 21.3
    },
    "distance_km": 6.2
}
```

#### 4. Predict Resources

```python
resources = await ml_service.predict_resource_availability(
    hospital_id="uuid",
    current_occupancy=85,
    time_features={"hour": 14, "day_of_week": 2, "is_weekend": 0},
    hours_ahead=24
)

# Returns:
{
    "hospital_id": "uuid",
    "predicted_available_beds": 12,
    "hours_ahead": 24,
    "confidence": 0.85
}
```

#### 5. Detect Hotspots

```python
hotspots = await ml_service.detect_hotspots(
    incidents=incident_list,
    radius_km=0.5,
    min_incidents=10
)

# Returns:
{
    "hotspots": [
        {
            "cluster_id": 1,
            "incident_count": 45,
            "center_lat": 19.0760,
            "center_lon": 72.8777
        }
    ],
    "anomalies": [...],
    "total_incidents": 1000
}
```

### ML Service Health Check

```python
health = ml_service.get_model_health()

# Returns:
{
    "models_loaded": true,
    "triage_classifier": true,
    "hospital_ranker": true,
    "resource_predictor": true,
    "eta_predictor": true,
    "hotspot_predictor": true,
    "model_info": {...}
}
```

---

## 🔄 Complete Workflow Example

### Create and Process Incident

```python
# 1. Create incident
response = await client.post(
    "/api/v1/incidents",
    json={
        "description": "Multiple vehicle accident on highway",
        "incident_type": "ACCIDENT",
        "location": {
            "latitude": 19.0760,
            "longitude": 72.8777,
            "city": "Mumbai"
        },
        "victim_count": 3
    },
    headers={"Authorization": f"Bearer {token}"}
)
incident_id = response.json()["data"]["incident_id"]

# 2. Process with AI (automatically triggers ML + agents)
await client.post(
    f"/api/v1/incidents/{incident_id}/process",
    headers={"Authorization": f"Bearer {token}"}
)

# 3. Monitor via WebSocket
# WebSocket will receive events:
# - agent.started (TriageAgent)
# - agent.completed (severity predicted)
# - agent.started (HospitalAgent)
# - plan.generated
# - incident.updated (status: AWAITING_APPROVAL)

# 4. Approve plan
await client.post(
    f"/api/v1/incidents/{incident_id}/approve",
    json={
        "approved": true,
        "notes": "Plan approved by dispatcher"
    },
    headers={"Authorization": f"Bearer {token}"}
)

# 5. Dispatch
await client.post(
    f"/api/v1/incidents/{incident_id}/dispatch",
    headers={"Authorization": f"Bearer {token}"}
)

# 6. WebSocket receives:
# - incident.dispatched
# - ambulance.status_changed
# - ambulance.location_updated (real-time tracking)
```

---

## 🧪 Testing the APIs

### Using cURL

```bash
# 1. Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d @register.json

# 2. Login
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d @login.json | jq -r '.data.access_token')

# 3. Create incident
curl -X POST http://localhost:8000/api/v1/incidents \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d @incident.json

# 4. List incidents
curl -X GET "http://localhost:8000/api/v1/incidents?page=1&page_size=20" \
  -H "Authorization: Bearer $TOKEN"
```

### Using Python Requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Login
response = requests.post(
    f"{BASE_URL}/api/v1/auth/login",
    json={"username": "testuser", "password": "password"}
)
token = response.json()["data"]["access_token"]

# Create incident
headers = {"Authorization": f"Bearer {token}"}
response = requests.post(
    f"{BASE_URL}/api/v1/incidents",
    json={
        "description": "Emergency incident",
        "incident_type": "MEDICAL",
        "location": {"latitude": 19.0760, "longitude": 72.8777}
    },
    headers=headers
)

print(response.json())
```

---

## 📝 Environment Variables

```env
# Required
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/aria_db
SECRET_KEY=your-secret-key-min-32-characters
OPENAI_API_KEY=sk-...

# Optional
MODEL_PATH=../models
ENABLE_ML_PREDICTIONS=True
RATE_LIMIT_PER_MINUTE=60
LOG_LEVEL=INFO
```

---

## 🐛 Common Issues & Solutions

### 1. ML Models Not Loading

**Problem:** Models fail to load on startup

**Solution:**
```bash
# Check model path
ls -la models/

# Ensure all model files exist
ls models/*.pkl models/*.txt

# Check permissions
chmod 644 models/*
```

### 2. WebSocket Connection Fails

**Problem:** Cannot connect to WebSocket

**Solutions:**
- Ensure token is valid (not expired)
- Check channel names are valid
- Verify WebSocket URL (ws:// not wss:// for local)

### 3. Database Connection Error

**Problem:** Cannot connect to PostgreSQL

**Solution:**
```bash
# Check PostgreSQL is running
psql -U postgres -d aria_db -c "SELECT 1"

# Check PostGIS extension
psql -U postgres -d aria_db -c "SELECT PostGIS_version()"

# Verify DATABASE_URL in .env
```

---

## 📚 API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## 🎯 Next Steps

### TODO - Remaining Endpoints

1. **Hospital Endpoints** (6 endpoints)
   - GET /hospitals
   - POST /hospitals/nearby
   - POST /hospitals/rank
   - PUT /hospitals/{id}/capacity

2. **Ambulance Endpoints** (6 endpoints)
   - GET /ambulances
   - GET /ambulances/available
   - POST /ambulances/nearest
   - PUT /ambulances/{id}/location

3. **Dashboard Endpoints** (5 endpoints)
   - GET /dashboard/stats
   - GET /dashboard/active-incidents
   - GET /dashboard/resource-status

4. **LangGraph Agents** (9 agents)
   - Implement complete agent orchestration
   - Connect to incident workflow
   - Human-in-the-loop approval

---

## 🚀 Deployment Checklist

- [ ] Setup PostgreSQL + PostGIS
- [ ] Configure environment variables
- [ ] Run database migrations
- [ ] Load ML models
- [ ] Setup Redis (for caching)
- [ ] Configure CORS origins
- [ ] Setup SSL certificates
- [ ] Configure reverse proxy (Nginx)
- [ ] Setup monitoring (Prometheus)
- [ ] Configure logging
- [ ] Run tests
- [ ] Setup CI/CD pipeline

---

**Status:** 60% Complete - Core functionality working!  
**Last Updated:** August 24, 2026  
**Next Update:** After Hospital + Ambulance APIs complete

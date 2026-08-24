# ARIA Backend - FastAPI Application

**Status:** Phase 3 - Backend Development ✅ In Progress  
**Version:** 1.0.0

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # ✅ FastAPI app with middleware
│   ├── core/
│   │   ├── __init__.py           # ✅ Core exports
│   │   ├── config.py             # ✅ Settings & configuration
│   │   ├── security.py           # ✅ Authentication & JWT
│   │   └── database.py           # ✅ SQLAlchemy async setup
│   ├── models/
│   │   ├── __init__.py           # ✅ Model exports
│   │   ├── user.py               # ✅ User model
│   │   ├── incident.py           # ✅ Incident + History models
│   │   ├── hospital.py           # ✅ Hospital model with PostGIS
│   │   └── ambulance.py          # ✅ Ambulance model
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── incident.py           # ✅ Incident schemas
│   │   ├── hospital.py           # TODO
│   │   ├── ambulance.py          # TODO
│   │   └── response.py           # ✅ Standard responses
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── incidents.py     # ✅ Complete incident endpoints
│   │   │   ├── hospitals.py     # TODO
│   │   │   ├── ambulances.py    # TODO
│   │   │   ├── blood_banks.py   # TODO
│   │   │   ├── dashboard.py     # TODO
│   │   │   └── auth.py          # TODO
│   │   └── dependencies.py       # TODO
│   ├── services/
│   │   ├── __init__.py
│   │   ├── ml_service.py         # TODO - ML model integration
│   │   └── agent_service.py      # TODO - LangGraph agents
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── triage_agent.py       # TODO
│   │   ├── hospital_agent.py     # TODO
│   │   ├── ambulance_agent.py    # TODO
│   │   └── coordinator.py        # TODO
│   └── utils/
│       ├── __init__.py
│       └── helpers.py            # TODO
├── alembic/
│   ├── env.py
│   └── versions/
├── tests/
├── requirements.txt              # ✅ All dependencies
├── .env.example                  # ✅ Environment template
└── README.md                     # ✅ This file
```

---

## ✅ Completed Features

### 1. Core Infrastructure
- ✅ FastAPI application with lifespan management
- ✅ CORS middleware configured
- ✅ Rate limiting (SlowAPI)
- ✅ Request ID tracking
- ✅ Comprehensive logging
- ✅ Error handling & validation
- ✅ Prometheus metrics
- ✅ Health check endpoints

### 2. Database Models
- ✅ User model with roles (admin, dispatcher, medical_staff, driver, viewer)
- ✅ Incident model with PostGIS geometry
- ✅ IncidentHistory for audit trail
- ✅ Hospital model with spatial indexing
- ✅ Ambulance model with real-time tracking
- ✅ All relationships defined

### 3. Authentication & Security
- ✅ JWT token generation (access + refresh)
- ✅ Password hashing (bcrypt)
- ✅ Role-based access control
- ✅ Bearer token authentication
- ✅ Current user dependencies

### 4. Incident Management API (Complete)
- ✅ POST /incidents - Create incident
- ✅ GET /incidents/{id} - Get details
- ✅ GET /incidents - List with filters
- ✅ POST /incidents/{id}/process - Trigger AI workflow
- ✅ POST /incidents/{id}/approve - Approve plan
- ✅ POST /incidents/{id}/modify - Modify plan
- ✅ POST /incidents/{id}/dispatch - Execute dispatch
- ✅ GET /incidents/{id}/status - Real-time status
- ✅ GET /incidents/{id}/history - Audit trail

### 5. Pydantic Schemas
- ✅ Incident schemas (Create, Update, Response, Process, Approval)
- ✅ Standard response schemas
- ✅ Error response schemas
- ✅ Pagination response

---

## 🚧 TODO - Remaining Work

### Priority 1: Complete API Endpoints

#### Auth Endpoints (`api/v1/auth.py`)
```python
POST /api/v1/auth/register
POST /api/v1/auth/login
POST /api/v1/auth/refresh
POST /api/v1/auth/logout
GET  /api/v1/auth/me
```

#### Hospital Endpoints (`api/v1/hospitals.py`)
```python
GET  /api/v1/hospitals - List/search hospitals
GET  /api/v1/hospitals/{id} - Get hospital details
POST /api/v1/hospitals/nearby - Find nearby hospitals
POST /api/v1/hospitals/rank - Rank hospitals for incident
PUT  /api/v1/hospitals/{id}/capacity - Update capacity
```

#### Ambulance Endpoints (`api/v1/ambulances.py`)
```python
GET  /api/v1/ambulances - List ambulances
GET  /api/v1/ambulances/available - Get available ambulances
POST /api/v1/ambulances/nearest - Find nearest ambulance
PUT  /api/v1/ambulances/{id}/location - Update location
PUT  /api/v1/ambulances/{id}/status - Update status
```

#### Dashboard Endpoints (`api/v1/dashboard.py`)
```python
GET /api/v1/dashboard/stats - Overall statistics
GET /api/v1/dashboard/active-incidents - Active incidents map
GET /api/v1/dashboard/resource-status - Resource availability
GET /api/v1/dashboard/hotspots - Incident hotspots
GET /api/v1/dashboard/analytics - Time-series analytics
```

### Priority 2: ML Service Integration

Create `services/ml_service.py`:
```python
class MLService:
    def __init__(self):
        self.triage_model = load_model("triage_xgboost.pkl")
        self.hospital_ranker = load_model("hospital_ranker.txt")
        self.eta_predictor = load_model("eta_predictor.pkl")
        self.hotspot_detector = load_model("hotspot_dbscan.pkl")
        self.resource_predictor = load_model("resource_predictor_gb.pkl")
    
    async def predict_severity(self, description: str) -> dict
    async def rank_hospitals(self, incident, hospitals) -> list
    async def predict_eta(self, origin, destination) -> dict
    async def predict_resources(self, hospital_id, hours) -> dict
    async def detect_hotspots(self, incidents) -> list
```

### Priority 3: LangGraph Agent System

Create agent orchestrator in `services/agent_service.py`:
```python
class AgentOrchestrator:
    def __init__(self):
        self.triage_agent = TriageAgent()
        self.hospital_agent = HospitalAgent()
        self.ambulance_agent = AmbulanceAgent()
        self.blood_agent = BloodAgent()
        self.route_agent = RouteAgent()
        self.rag_agent = RAGAgent()
        self.plan_agent = PlanAgent()
        self.communication_agent = CommunicationAgent()
        self.coordinator_agent = CoordinatorAgent()
    
    async def process_incident(self, incident_id: UUID) -> dict:
        # Orchestrate all agents
        pass
```

### Priority 4: Database Migrations

Setup Alembic:
```bash
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### Priority 5: Testing

Create test suite:
```python
tests/
├── conftest.py
├── test_auth.py
├── test_incidents.py
├── test_hospitals.py
├── test_ambulances.py
└── test_agents.py
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Setup Environment

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 3. Setup Database

```bash
# Install PostgreSQL with PostGIS
brew install postgresql postgis  # macOS

# Create database
createdb aria_db

# Enable PostGIS
psql aria_db -c "CREATE EXTENSION postgis;"

# Run migrations
alembic upgrade head
```

### 4. Run Application

```bash
# Development
uvicorn app.main:app --reload --port 8000

# Production
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 5. Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## 📊 Database Schema

### Users Table
- id (UUID, PK)
- email, username (unique)
- hashed_password
- role (admin, dispatcher, medical_staff, driver, viewer)
- is_active, is_verified
- timestamps

### Incidents Table
- id (UUID, PK)
- incident_code (unique)
- location (PostGIS POINT)
- latitude, longitude
- description, incident_type, severity
- status (REPORTED → TRIAGED → ... → COMPLETED)
- assigned_hospital_id, assigned_ambulance_id
- response_plan (JSON)
- ml predictions
- approval tracking
- timestamps

### Hospitals Table
- id (UUID, PK)
- location (PostGIS POINT)
- name, address, city
- capacity (beds, ICU, ventilators)
- specialties (array)
- ratings, metrics
- blood_inventory (JSON)
- timestamps

### Ambulances Table
- id (UUID, PK)
- vehicle_number (unique)
- current_location (PostGIS POINT, real-time)
- ambulance_type (BASIC, ALS, CRITICAL_CARE)
- status (AVAILABLE, DISPATCHED, EN_ROUTE, etc.)
- equipment (JSON)
- driver, crew info
- timestamps

---

## 🔐 Authentication Flow

1. **Register**: POST /api/v1/auth/register
2. **Login**: POST /api/v1/auth/login → Returns access_token + refresh_token
3. **Use Token**: Add header `Authorization: Bearer {access_token}`
4. **Refresh**: POST /api/v1/auth/refresh with refresh_token
5. **Logout**: POST /api/v1/auth/logout

---

## 🎯 API Usage Examples

### Create Incident
```bash
curl -X POST http://localhost:8000/api/v1/incidents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Patient with chest pain and difficulty breathing",
    "incident_type": "MEDICAL",
    "location": {
      "latitude": 19.0760,
      "longitude": 72.8777,
      "address": "123 Main St, Mumbai",
      "city": "Mumbai"
    },
    "victim_count": 1,
    "reporter_name": "John Doe",
    "reporter_phone": "+91 98765 43210",
    "blood_required": false,
    "ambulance_required": true
  }'
```

### List Incidents
```bash
curl "http://localhost:8000/api/v1/incidents?status=REPORTED&page=1&page_size=20" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Get Incident Status
```bash
curl "http://localhost:8000/api/v1/incidents/{incident_id}/status" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📝 Environment Variables

Key variables in `.env`:

```env
# Database
DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/aria_db

# Security
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI (for LangGraph agents)
OPENAI_API_KEY=sk-...

# ML Models
MODEL_PATH=../models
ENABLE_ML_PREDICTIONS=True

# Rate Limiting
RATE_LIMIT_PER_MINUTE=60
```

---

## 🧪 Testing

```bash
# Run tests
pytest

# With coverage
pytest --cov=app --cov-report=html

# Specific test
pytest tests/test_incidents.py -v
```

---

## 📦 Deployment

### Docker

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Docker Compose

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/aria
    depends_on:
      - db
      - redis
  
  db:
    image: postgis/postgis:15-3.3
    environment:
      POSTGRES_DB: aria
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
  
  redis:
    image: redis:7-alpine
```

---

## 🔧 Development

### Adding a New Endpoint

1. Create router in `app/api/v1/your_endpoint.py`
2. Define Pydantic schemas in `app/schemas/`
3. Create database models in `app/models/` (if needed)
4. Register router in `app/main.py`
5. Write tests in `tests/`

### Adding a New Agent

1. Create agent file in `app/agents/your_agent.py`
2. Implement LangGraph StateGraph
3. Define input/output schemas
4. Register in `app/services/agent_service.py`
5. Add tests

---

## 📚 Documentation

- API Docs: http://localhost:8000/docs
- Health Check: http://localhost:8000/health
- Metrics: http://localhost:8000/metrics

---

## 🎯 Next Steps

1. **Week 1**: Complete remaining API endpoints (hospitals, ambulances, auth)
2. **Week 2**: Integrate ML models service
3. **Week 3**: Implement LangGraph agent system
4. **Week 4**: Testing, monitoring, deployment

---

**Status**: Foundation complete, ready for feature development!
**Created**: August 24, 2026  
**Last Updated**: August 24, 2026

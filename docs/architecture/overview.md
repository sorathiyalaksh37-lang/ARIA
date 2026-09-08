# ARIA System Architecture Overview

## Executive Summary

ARIA (AI-powered Rapid Incident Assessment) is a comprehensive emergency response coordination platform that leverages artificial intelligence, machine learning, and distributed agent systems to optimize emergency resource allocation and response times.

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        ARIA PLATFORM                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                   FRONTEND LAYER                         │  │
│  │  - React.js Dashboard                                    │  │
│  │  - Real-time Map (Leaflet/MapLibre)                      │  │
│  │  - WebSocket Client                                      │  │
│  │  - Redux State Management                                │  │
│  └─────────────────┬────────────────────────────────────────┘  │
│                    │ HTTPS/WSS                                  │
│  ┌─────────────────┴────────────────────────────────────────┐  │
│  │                   API GATEWAY LAYER                      │  │
│  │  - FastAPI (Python 3.11)                                 │  │
│  │  - JWT Authentication                                    │  │
│  │  - Rate Limiting (SlowAPI)                               │  │
│  │  - CORS Middleware                                       │  │
│  │  - Prometheus Metrics                                    │  │
│  └─────────┬──────────────┬──────────────┬─────────────────┘  │
│            │              │              │                      │
│  ┌─────────┴────┐  ┌──────┴──────┐  ┌──┴─────────────────┐   │
│  │   REST API   │  │  WebSocket  │  │  GraphQL (Future)  │   │
│  │  32+ Endpoints│  │  Real-time  │  │                    │   │
│  └─────────┬────┘  └──────┬──────┘  └────────────────────┘   │
│            │              │                                     │
│  ┌─────────┴──────────────┴─────────────────────────────────┐ │
│  │              BUSINESS LOGIC LAYER                        │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │  ┌──────────────────────────────────────────────────┐   │ │
│  │  │      LANGGRAPH AGENT ORCHESTRATOR                │   │ │
│  │  │  - StateGraph Workflow Engine                    │   │ │
│  │  │  - 14 Specialized Agents                         │   │ │
│  │  │  - Human-in-the-Loop Coordination                │   │ │
│  │  └──────────────────────────────────────────────────┘   │ │
│  │                                                           │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │ │
│  │  │  ML Service  │  │  Maps Service│  │ LLM Service  │  │ │
│  │  │  5 Models    │  │  Google Maps │  │  GPT-4       │  │ │
│  │  │  Prediction  │  │  OSRM        │  │  Whisper     │  │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │ │
│  │                                                           │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │ │
│  │  │Notification  │  │Vision Service│  │Weather Service│ │ │
│  │  │SMS/Email     │  │  GPT-4V      │  │  OpenWeather │  │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                    │                                            │
│  ┌─────────────────┴────────────────────────────────────────┐ │
│  │               DATA PERSISTENCE LAYER                     │ │
│  ├──────────────────────────────────────────────────────────┤ │
│  │  ┌──────────────────┐  ┌──────────────┐  ┌───────────┐ │ │
│  │  │   PostgreSQL     │  │    Redis     │  │  MinIO    │ │ │
│  │  │   + PostGIS      │  │   Cache      │  │  S3-like  │ │ │
│  │  │   Relational DB  │  │   WebSocket  │  │  Storage  │ │ │
│  │  └──────────────────┘  └──────────────┘  └───────────┘ │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │            EXTERNAL INTEGRATIONS                        │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │  • OpenAI (GPT-4, Whisper, Vision)                      │  │
│  │  • Google Maps (Geocoding, Directions, Places)          │  │
│  │  • Twilio (SMS Notifications)                           │  │
│  │  • SendGrid (Email Notifications)                       │  │
│  │  • OpenWeather (Weather Data)                           │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │         MONITORING & OBSERVABILITY                      │  │
│  ├─────────────────────────────────────────────────────────┤  │
│  │  • Prometheus (Metrics Collection)                      │  │
│  │  • Grafana (Visualization)                              │  │
│  │  • Python Logging (Structured Logs)                     │  │
│  │  • Health Checks & Alerts                               │  │
│  └─────────────────────────────────────────────────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Frontend Layer

**Technology Stack:**
- React.js 18.2.0 with TypeScript
- Redux Toolkit for state management
- Material-UI (MUI) for components
- Leaflet/MapLibre GL for mapping
- WebSocket for real-time updates
- Axios for HTTP requests

**Key Components:**
- **Dashboard:** Real-time incident monitoring
- **Incident Management:** Create, view, manage incidents
- **Map View:** Geographic visualization of resources
- **Agent Monitor:** Track AI agent execution
- **Resource Tracker:** Monitor ambulances, hospitals, blood banks
- **Analytics:** Historical data and trends

**State Management:**
```
Redux Store
├── auth (user, tokens, permissions)
├── incidents (list, details, filters)
├── agents (status, logs, metrics)
├── resources (ambulances, hospitals, blood banks)
├── map (markers, routes, layers)
└── notifications (alerts, toasts)
```

---

### 2. API Gateway Layer

**Technology Stack:**
- FastAPI 0.109.0 (Python 3.11)
- Uvicorn ASGI server
- Pydantic for validation
- python-jose for JWT
- slowapi for rate limiting

**Features:**
- **Authentication:** JWT-based with refresh tokens
- **Authorization:** Role-based access control (RBAC)
- **Rate Limiting:** Per-user and per-endpoint limits
- **CORS:** Configurable cross-origin policies
- **Validation:** Request/response schema validation
- **Documentation:** Auto-generated OpenAPI/Swagger

**API Endpoints:**
```
Authentication (6 endpoints)
├── POST /auth/register
├── POST /auth/login
├── POST /auth/refresh
├── GET /auth/me
├── PUT /auth/password
└── POST /auth/logout

Incidents (9 endpoints)
├── POST /incidents
├── GET /incidents/{id}
├── GET /incidents
├── POST /incidents/{id}/process
├── POST /incidents/{id}/approve
├── POST /incidents/{id}/modify
├── POST /incidents/{id}/dispatch
├── GET /incidents/{id}/status
└── GET /incidents/{id}/history

Hospitals (6 endpoints)
├── GET /hospitals
├── POST /hospitals/nearby
├── POST /hospitals/rank
├── GET /hospitals/{id}
├── PUT /hospitals/{id}/capacity
└── GET /hospitals/{id}/availability

Ambulances (6 endpoints)
├── GET /ambulances
├── GET /ambulances/available
├── POST /ambulances/nearest
├── GET /ambulances/{id}
├── PUT /ambulances/{id}/location
└── PUT /ambulances/{id}/status

Dashboard (5 endpoints)
├── GET /dashboard/stats
├── GET /dashboard/active-incidents
├── GET /dashboard/resource-status
├── GET /dashboard/hotspots
└── GET /dashboard/analytics

WebSocket (1 endpoint)
└── WS /ws (with channel subscriptions)
```

---

### 3. LangGraph Agent System

**Architecture Pattern:** Multi-Agent Orchestration with Human-in-the-Loop

**Agent Workflow:**
```
┌─────────────┐
│   Incident  │
│   Created   │
└──────┬──────┘
       │
       ▼
┌─────────────────────────────────────────────────────────┐
│            LANGGRAPH STATE GRAPH                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  START                                                  │
│    │                                                    │
│    ▼                                                    │
│  ┌──────────────┐                                      │
│  │Triage Agent  │ ML Severity Classification           │
│  └──────┬───────┘                                      │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐                                      │
│  │Hospital Agent│ Spatial Search + ML Ranking          │
│  └──────┬───────┘                                      │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐                                      │
│  │Ambulance Agt │ Find Nearest + ETA Prediction        │
│  └──────┬───────┘                                      │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐                                      │
│  │  Blood Agent │ Blood Bank Search (Conditional)      │
│  └──────┬───────┘                                      │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐                                      │
│  │  Route Agent │ Optimized Route Calculation          │
│  └──────┬───────┘                                      │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐                                      │
│  │   RAG Agent  │ Medical Protocol Retrieval           │
│  └──────┬───────┘                                      │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐                                      │
│  │  Plan Agent  │ Generate Response Plan               │
│  └──────┬───────┘                                      │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐                                      │
│  │Coordinator   │ ◄──── HUMAN-IN-THE-LOOP              │
│  │   Agent      │       Approval/Rejection             │
│  └──────┬───────┘                                      │
│         │                                               │
│    ┌────┴────┐                                         │
│    │         │                                          │
│ APPROVE   REJECT/MODIFY                                │
│    │         │                                          │
│    │         └──────► (Loop back to Plan Agent)        │
│    │                                                    │
│    ▼                                                    │
│  ┌──────────────┐                                      │
│  │Communication │ Send SMS/Email Notifications         │
│  │    Agent     │                                      │
│  └──────┬───────┘                                      │
│         │                                               │
│         ▼                                               │
│  ┌──────────────┐                                      │
│  │ Monitoring   │ Collect Metrics & Health             │
│  │    Agent     │                                      │
│  └──────┬───────┘                                      │
│         │                                               │
│         ▼                                               │
│       END                                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**Agent Descriptions:**

1. **Triage Agent:** Uses ML classifier (99.99% accuracy) to determine incident severity
2. **Hospital Agent:** Finds nearby hospitals using PostGIS, ranks with ML model
3. **Ambulance Agent:** Locates available ambulances, predicts ETA
4. **Blood Agent:** Searches blood banks when blood transfusion needed
5. **Route Agent:** Calculates optimized routes considering traffic
6. **RAG Agent:** Retrieves relevant medical protocols (future enhancement)
7. **Plan Agent:** Generates comprehensive response plan
8. **Coordinator Agent:** Presents plan to human operator for approval
9. **Communication Agent:** Sends SMS/Email to all stakeholders
10. **Monitoring Agent:** Tracks system health and workflow metrics

---

### 4. Machine Learning Layer

**ML Service Architecture:**

```
┌────────────────────────────────────────────────┐
│           ML SERVICE MANAGER                   │
├────────────────────────────────────────────────┤
│                                                │
│  Model Loading (Startup)                       │
│  ├── Load 5 trained models from disk           │
│  ├── Load metadata & scalers                   │
│  └── Initialize prediction pipelines           │
│                                                │
│  Prediction Pipeline                           │
│  ├── Feature preprocessing                     │
│  ├── Model inference                           │
│  ├── Result post-processing                    │
│  └── Caching with @lru_cache                   │
│                                                │
│  Health Checks                                 │
│  ├── Model availability                        │
│  ├── Prediction latency                        │
│  └── Error rate monitoring                     │
│                                                │
└────────────────────────────────────────────────┘
```

**5 Trained Models:**

| Model | Type | Purpose | Accuracy | Input | Output |
|-------|------|---------|----------|-------|--------|
| Triage Classifier | Random Forest | Severity classification | 99.99% | Description, location, time | CRITICAL/MODERATE/MINOR |
| Hospital Ranker | LightGBM | Rank hospitals by suitability | NDCG: 0.9919 | Hospital features, incident | Ranked list |
| Resource Predictor | XGBoost | Predict required resources | MAE: 6.17 | Incident details | Ambulances, beds needed |
| ETA Predictor | XGBoost | Predict arrival time | MAE: 1.32 min | Distance, traffic, time | Minutes |
| Hotspot Predictor | K-Means + DBSCAN | Identify high-risk areas | Precision: 1.00 | Historical incidents | Hotspot locations |

**Model Storage:**
- Location: `models/` directory
- Format: Joblib pickle files (.pkl)
- Git LFS: Used for version control (182 MB)
- Metadata: JSON files with training info

---

### 5. Data Persistence Layer

**PostgreSQL with PostGIS:**

**Schema Overview:**
```
users
├── id (PK)
├── username
├── email
├── hashed_password
├── role (ENUM: admin, dispatcher, coordinator, responder, viewer)
├── created_at
└── is_active

incidents
├── id (PK)
├── title
├── description
├── incident_type (ENUM)
├── severity (ENUM: critical, moderate, minor)
├── status (ENUM: pending, processing, approved, dispatched, completed)
├── location (POINT - PostGIS)
├── latitude, longitude
├── reporter_name
├── reporter_phone
├── created_by_id (FK → users)
├── assigned_hospital_id (FK → hospitals)
├── assigned_ambulance_id (FK → ambulances)
├── created_at
└── updated_at

hospitals
├── id (PK)
├── name
├── address
├── city, state, pincode
├── location (POINT - PostGIS)
├── latitude, longitude
├── phone
├── email
├── total_beds
├── available_beds
├── icu_beds
├── ventilators
├── specializations (ARRAY)
├── is_active
├── created_at
└── updated_at

ambulances
├── id (PK)
├── vehicle_number
├── ambulance_type (ENUM: basic, advanced, air)
├── status (ENUM: available, dispatched, busy, maintenance)
├── location (POINT - PostGIS)
├── latitude, longitude
├── driver_name
├── driver_phone
├── equipment (JSON)
├── current_incident_id (FK → incidents)
├── home_hospital_id (FK → hospitals)
├── is_active
├── created_at
└── updated_at

incident_history
├── id (PK)
├── incident_id (FK → incidents)
├── status
├── notes
├── changed_by_id (FK → users)
├── metadata (JSON)
└── created_at
```

**PostGIS Spatial Indexes:**
```sql
CREATE INDEX idx_incidents_location ON incidents USING GIST(location);
CREATE INDEX idx_hospitals_location ON hospitals USING GIST(location);
CREATE INDEX idx_ambulances_location ON ambulances USING GIST(location);
```

**Redis Cache:**
- Session storage
- WebSocket connection management
- Rate limiting counters
- Temporary data caching
- Real-time location updates

---

### 6. External Integration Layer

**Service Integrations:**

**1. OpenAI Services:**
```
┌─────────────────────────────────────────┐
│         OpenAI Integration              │
├─────────────────────────────────────────┤
│                                         │
│  GPT-4 (LLM Service)                    │
│  ├── Incident parsing                   │
│  ├── Severity assessment                │
│  ├── Protocol generation                │
│  └── Natural language understanding     │
│                                         │
│  Whisper (Speech Service)               │
│  ├── Audio transcription                │
│  ├── Multiple languages                 │
│  └── Emergency call processing          │
│                                         │
│  GPT-4 Vision (Vision Service)          │
│  ├── Injury detection                   │
│  ├── Scene analysis                     │
│  └── Image-based triage                 │
│                                         │
└─────────────────────────────────────────┘
```

**2. Google Maps Services:**
```
┌─────────────────────────────────────────┐
│       Google Maps Integration           │
├─────────────────────────────────────────┤
│                                         │
│  Geocoding API                          │
│  ├── Address → Coordinates              │
│  ├── Coordinates → Address              │
│  └── Place search                       │
│                                         │
│  Directions API                         │
│  ├── Route calculation                  │
│  ├── Real-time traffic                  │
│  ├── ETA estimation                     │
│  └── Turn-by-turn navigation            │
│                                         │
│  Places API                             │
│  ├── Nearby search                      │
│  ├── Place details                      │
│  └── Autocomplete                       │
│                                         │
│  Fallback: OSRM + Nominatim             │
│  └── Open-source alternatives           │
│                                         │
└─────────────────────────────────────────┘
```

**3. Notification Services:**
```
┌─────────────────────────────────────────┐
│     Notification Integration            │
├─────────────────────────────────────────┤
│                                         │
│  Twilio (SMS Service)                   │
│  ├── Send SMS notifications             │
│  ├── Template-based messages            │
│  ├── Delivery status tracking           │
│  └── Phone number validation            │
│                                         │
│  SendGrid (Email Service)               │
│  ├── HTML email templates               │
│  ├── Transactional emails               │
│  ├── Delivery analytics                 │
│  └── Bounce handling                    │
│                                         │
│  Notification Orchestrator              │
│  ├── Multi-channel coordination         │
│  ├── Priority-based sending             │
│  ├── Retry logic                        │
│  └── Failure handling                   │
│                                         │
└─────────────────────────────────────────┘
```

---

### 7. Monitoring & Observability

**Prometheus Metrics:**
```
# Application Metrics
http_requests_total
http_request_duration_seconds
http_requests_in_progress

# Business Metrics
incidents_created_total
incidents_by_severity
agent_execution_duration_seconds
ml_predictions_total
ml_prediction_errors_total

# System Metrics
database_connections
redis_operations_total
external_api_calls_total
```

**Grafana Dashboards:**
1. System Health Dashboard
2. API Performance Dashboard
3. Business Metrics Dashboard
4. ML Model Performance Dashboard

**Logging:**
- Structured JSON logging
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Log rotation and archival
- Centralized log aggregation (future)

---

## Technology Stack Summary

### Backend
- **Language:** Python 3.11
- **Framework:** FastAPI 0.109.0
- **ASGI Server:** Uvicorn
- **Database ORM:** SQLAlchemy 2.0.25 (async)
- **Database:** PostgreSQL 14+ with PostGIS
- **Cache:** Redis 7.0+
- **ML:** scikit-learn, XGBoost, LightGBM
- **AI:** LangChain 0.1.4, LangGraph 0.0.20

### Frontend
- **Language:** TypeScript
- **Framework:** React.js 18.2.0
- **State Management:** Redux Toolkit
- **UI Library:** Material-UI (MUI)
- **Mapping:** Leaflet / MapLibre GL
- **Build Tool:** Vite / Create React App

### Infrastructure
- **Containerization:** Docker
- **Orchestration:** Docker Compose / Kubernetes
- **CI/CD:** GitHub Actions
- **Monitoring:** Prometheus + Grafana
- **Reverse Proxy:** Nginx

### External Services
- **AI:** OpenAI (GPT-4, Whisper, Vision)
- **Maps:** Google Maps API
- **SMS:** Twilio
- **Email:** SendGrid
- **Weather:** OpenWeather

---

## Deployment Architecture

### Development Environment
```
Localhost
├── PostgreSQL (localhost:5432)
├── Redis (localhost:6379)
├── Backend (localhost:8000)
└── Frontend (localhost:3000)
```

### Production Environment
```
Cloud Infrastructure (AWS/GCP/Azure)
├── Load Balancer (HTTPS)
├── Container Cluster (Kubernetes)
│   ├── Frontend Pods (Nginx + React)
│   ├── Backend Pods (FastAPI)
│   └── Worker Pods (Celery - future)
├── Managed PostgreSQL (RDS/CloudSQL)
├── Managed Redis (ElastiCache/MemoryStore)
├── Object Storage (S3/Cloud Storage)
├── Monitoring Stack (Prometheus + Grafana)
└── CDN (CloudFront/Cloud CDN)
```

---

## Security Architecture

### Authentication Flow
```
1. User → POST /auth/login (username, password)
2. Backend → Verify credentials
3. Backend → Generate JWT access token (30 min expiry)
4. Backend → Generate JWT refresh token (7 day expiry)
5. Backend → Return tokens
6. User → Store tokens securely
7. User → Include "Authorization: Bearer {token}" in requests
8. Backend → Validate token on each request
9. Token expired → Use refresh token to get new access token
```

### Authorization (RBAC)
```
Roles:
├── Admin (full access)
├── Dispatcher (create/manage incidents)
├── Coordinator (approve/reject plans)
├── Responder (view assigned incidents)
└── Viewer (read-only access)

Permissions enforced at:
├── API endpoint level
├── Database row level
└── Frontend UI level
```

### Data Security
- Passwords hashed with bcrypt
- JWT signed with HS256
- HTTPS/TLS for all traffic
- SQL injection prevention (SQLAlchemy)
- XSS prevention (input sanitization)
- CSRF protection
- Rate limiting per user/IP

---

## Scalability Considerations

### Horizontal Scaling
- Stateless API design (scales easily)
- Session data in Redis (shared state)
- Database read replicas
- CDN for static assets
- Load balancer with health checks

### Vertical Scaling
- ML model serving optimization
- Database query optimization
- Connection pooling
- Caching strategies

### Performance Optimization
- Database indexes on frequently queried columns
- Redis caching for hot data
- Async I/O for external API calls
- Background tasks with Celery (future)
- WebSocket connection pooling

---

## Disaster Recovery

### Backup Strategy
- Database: Daily automated backups
- Object storage: Cross-region replication
- Config: Version controlled in Git
- Models: Git LFS with versioning

### High Availability
- Multi-region deployment
- Database replication
- Redis clustering
- Automated failover
- Health checks and auto-recovery

---

## Future Enhancements

1. **RAG System:** Full implementation of retrieval-augmented generation
2. **Mobile Apps:** Native iOS and Android applications
3. **IoT Integration:** Ambulance telemetry, hospital bed sensors
4. **Blockchain:** Immutable audit trail
5. **Advanced Analytics:** Predictive modeling, trend analysis
6. **Multi-language:** Internationalization support
7. **Voice Interface:** Alexa/Google Assistant integration
8. **Smart City Integration:** Traffic signal priority, public transport coordination

---

## Conclusion

ARIA represents a state-of-the-art emergency response platform that combines traditional software engineering best practices with cutting-edge AI technologies. The architecture is designed for scalability, reliability, and extensibility while maintaining security and performance.

---

**Document Version:** 1.0  
**Last Updated:** 2026-09-06  
**Maintained By:** ARIA Development Team

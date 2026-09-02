# ARIA Platform - Complete Integration Guide

**Comprehensive guide for frontend-backend integration, API usage, and troubleshooting**

Version: 1.0.0  
Last Updated: 2024

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [API Endpoints Reference](#api-endpoints-reference)
3. [Frontend Integration](#frontend-integration)
4. [External Services Integration](#external-services-integration)
5. [WebSocket Real-Time Updates](#websocket-real-time-updates)
6. [Error Handling](#error-handling)
7. [Testing & Debugging](#testing--debugging)
8. [Common Issues & Solutions](#common-issues--solutions)
9. [Performance Optimization](#performance-optimization)
10. [Security Considerations](#security-considerations)

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                     ARIA Platform                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐      ┌──────────────┐     ┌────────────┐ │
│  │   Frontend   │◄────►│   Backend    │◄───►│  Database  │ │
│  │  React + TS  │      │   FastAPI    │     │ PostgreSQL │ │
│  └──────────────┘      └──────────────┘     └────────────┘ │
│         │                      │                             │
│         │                      ▼                             │
│         │            ┌──────────────────┐                    │
│         │            │  External APIs   │                    │
│         │            ├──────────────────┤                    │
│         │            │ • OpenAI (LLM)   │                    │
│         │            │ • Google Maps    │                    │
│         │            │ • Twilio (SMS)   │                    │
│         │            │ • SendGrid       │                    │
│         │            │ • Weather API    │                    │
│         │            └──────────────────┘                    │
│         │                                                     │
│         └──────────► WebSocket (Real-time)                   │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

**Frontend:**
- React 18 with TypeScript
- Material-UI (MUI) for components
- Leaflet for maps with heatmap support
- Axios for HTTP requests
- Socket.io-client for WebSocket

**Backend:**
- FastAPI (Python)
- SQLAlchemy ORM with async support
- Pydantic for validation
- LangGraph for AI agents
- Redis for caching

**External Services:**
- OpenAI GPT-4, Whisper, Vision
- Google Maps APIs
- Twilio SMS
- SendGrid Email
- OpenWeatherMap

---

## API Endpoints Reference

### Base URL

- **Development:** `http://localhost:8000/api/v1`
- **Production:** `https://api.aria-emergency.com/api/v1`

### Authentication Endpoints

#### POST `/auth/register`
Register a new user account.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe",
  "role": "dispatcher"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "dispatcher"
  }
}
```

#### POST `/auth/login`
Authenticate and receive JWT tokens.

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "token_type": "bearer",
    "expires_in": 1800
  }
}
```

#### GET `/auth/me`
Get current user profile.

**Headers:** `Authorization: Bearer {access_token}`

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "email": "user@example.com",
    "full_name": "John Doe",
    "role": "dispatcher",
    "created_at": "2024-01-01T00:00:00Z"
  }
}
```

### Incident Endpoints

#### POST `/incidents`
Create a new emergency incident.

**Headers:** `Authorization: Bearer {access_token}`

**Request:**
```json
{
  "type": "medical_emergency",
  "severity": "high",
  "description": "Patient with chest pain and difficulty breathing",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "reporter_name": "Jane Smith",
  "reporter_phone": "+15551234567"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": 123,
    "incident_number": "INC-2024-000123",
    "type": "medical_emergency",
    "severity": "high",
    "status": "pending",
    "created_at": "2024-01-01T12:00:00Z"
  }
}
```

#### GET `/incidents/{id}`
Get incident details by ID.

#### GET `/incidents`
List all incidents with filters.

**Query Parameters:**
- `status`: Filter by status (pending, in_progress, resolved)
- `severity`: Filter by severity (low, medium, high, critical)
- `skip`: Pagination offset (default: 0)
- `limit`: Results per page (default: 100)

#### POST `/incidents/{id}/process`
Process incident through AI agent pipeline.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "incident_id": 123,
    "triage_result": {
      "severity": "high",
      "priority": 1,
      "estimated_response_time": 8
    },
    "recommended_actions": [
      "Dispatch ALS ambulance",
      "Alert nearest Level 1 trauma center",
      "Prepare for cardiac emergency"
    ]
  }
}
```

### Hospital Endpoints

#### GET `/hospitals`
List all hospitals.

#### GET `/hospitals/nearby`
Find hospitals near a location.

**Query Parameters:**
- `latitude`: Location latitude (required)
- `longitude`: Location longitude (required)
- `radius`: Search radius in km (default: 10)
- `specialty`: Filter by specialty (optional)

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "City General Hospital",
      "latitude": 37.7750,
      "longitude": -122.4200,
      "distance_km": 0.5,
      "available_beds": 12,
      "trauma_level": 1
    }
  ]
}
```

#### POST `/hospitals/rank`
Rank hospitals for an incident.

**Request:**
```json
{
  "incident_id": 123,
  "max_results": 5
}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "ranked_hospitals": [
      {
        "hospital": { /* hospital object */ },
        "score": 95.5,
        "distance_km": 2.3,
        "eta_minutes": 8,
        "ranking_factors": {
          "proximity": 0.9,
          "availability": 0.95,
          "capability": 1.0,
          "specialization": 0.98
        }
      }
    ]
  }
}
```

### Ambulance Endpoints

#### GET `/ambulances`
List all ambulances.

#### GET `/ambulances/nearest`
Find nearest available ambulances.

**Query Parameters:**
- `latitude`: Location latitude (required)
- `longitude`: Location longitude (required)
- `limit`: Max results (default: 5)
- `ambulance_type`: Filter by type (als, bls)

#### PATCH `/ambulances/{id}/location`
Update ambulance location.

**Request:**
```json
{
  "latitude": 37.7751,
  "longitude": -122.4195
}
```

#### PATCH `/ambulances/{id}/status`
Update ambulance status.

**Request:**
```json
{
  "status": "en_route"
}
```

**Valid statuses:** `available`, `en_route`, `on_scene`, `transporting`, `at_hospital`, `out_of_service`

### Dashboard Endpoints

#### GET `/dashboard/stats`
Get dashboard statistics.

**Response (200):**
```json
{
  "success": true,
  "data": {
    "active_incidents": 5,
    "available_ambulances": 12,
    "avg_response_time": 7.5,
    "incidents_today": 23,
    "incidents_resolved": 18
  }
}
```

#### GET `/dashboard/active-incidents`
Get currently active incidents.

#### GET `/dashboard/agent-status`
Get AI agent system status.

### Resource Allocation Endpoints

#### GET `/resource-allocation/hotspots`
Get predicted incident hotspots.

**Query Parameters:**
- `hours_ahead`: Prediction horizon (1-72 hours, default: 24)
- `grid_size`: Grid resolution (10-100, default: 50)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "hotspots": [
      {
        "latitude": 37.7749,
        "longitude": -122.4194,
        "risk_score": 0.85,
        "predicted_incidents": 4,
        "hour": 18,
        "timestamp": "2024-01-01T18:00:00Z"
      }
    ],
    "hours_ahead": 24,
    "count": 45
  }
}
```

#### GET `/resource-allocation/demand-forecast`
Get incident demand forecast.

**Query Parameters:**
- `hours_ahead`: Forecast horizon (1-168 hours, default: 24)

**Response (200):**
```json
{
  "success": true,
  "data": {
    "forecast_generated_at": "2024-01-01T12:00:00Z",
    "hours_ahead": 24,
    "forecasts": [
      {
        "timestamp": "2024-01-01T13:00:00Z",
        "hour": 13,
        "predicted_incidents": 3.5,
        "ambulance_demand": 3,
        "bed_demand": 2,
        "confidence": 0.75
      }
    ],
    "total_predicted_incidents": 42,
    "peak_hour": {
      "hour": 18,
      "predicted_incidents": 5.2
    }
  }
}
```

#### GET `/resource-allocation/ambulance-positioning`
Get ambulance repositioning recommendations.

#### GET `/resource-allocation/coverage-gaps`
Identify coverage gaps.

**Query Parameters:**
- `target_response_time`: Target in minutes (5-15, default: 8)

#### GET `/resource-allocation/heatmap`
Get heatmap data for visualization.

**Query Parameters:**
- `metric`: Heatmap type (risk, demand, coverage, incidents)

#### GET `/resource-allocation/optimization-summary`
Get comprehensive optimization summary.

#### POST `/resource-allocation/apply-recommendations`
Apply repositioning recommendations.

**Request:**
```json
{
  "ambulance_ids": ["AMB-001", "AMB-002"]
}
```

---

## Frontend Integration

### API Client Setup

The frontend uses Axios with interceptors for authentication and error handling.

**Location:** `frontend/src/api/client.ts`

```typescript
import axios from 'axios';

const apiClient = axios.create({
  baseURL: process.env.REACT_APP_API_BASE_URL,
  timeout: 15000,
});

// Attach JWT token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle 401 and refresh token
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Attempt token refresh
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const { data } = await axios.post('/auth/refresh', null, {
            headers: { Authorization: `Bearer ${refreshToken}` }
          });
          localStorage.setItem('access_token', data.data.access_token);
          // Retry original request
          return apiClient(error.config);
        } catch {
          // Refresh failed, redirect to login
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);
```

### Using the API Client

#### Example: Create Incident

```typescript
import { apiClient } from './api/client';

const createIncident = async (incidentData) => {
  try {
    const response = await apiClient.post('/incidents', incidentData);
    return response.data.data;
  } catch (error) {
    console.error('Failed to create incident:', error);
    throw error;
  }
};

// Usage in component
const handleSubmit = async (formData) => {
  try {
    const incident = await createIncident(formData);
    toast.success(`Incident ${incident.incident_number} created`);
    navigate(`/incidents/${incident.id}`);
  } catch (error) {
    toast.error('Failed to create incident');
  }
};
```

#### Example: Resource Allocation

```typescript
import resourceAllocationApi from './api/resourceAllocation';

const ResourceAllocation = () => {
  const [hotspots, setHotspots] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadHotspots();
  }, []);

  const loadHotspots = async () => {
    try {
      const data = await resourceAllocationApi.getHotspots(24, 50);
      setHotspots(data.hotspots);
    } catch (error) {
      console.error('Failed to load hotspots:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <ResourceHeatmap hotspots={hotspots} />
    </div>
  );
};
```

### Error Handling

#### Standardized Error Response

All API errors follow this format:

```json
{
  "success": false,
  "message": "Validation error",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format",
      "code": "invalid_format"
    }
  ]
}
```

#### Frontend Error Handling

```typescript
const handleApiError = (error: any) => {
  if (error.response) {
    // Server responded with error
    const { status, data } = error.response;
    
    switch (status) {
      case 400:
        toast.error(data.message || 'Invalid request');
        break;
      case 401:
        toast.error('Please log in to continue');
        navigate('/login');
        break;
      case 403:
        toast.error('You do not have permission');
        break;
      case 404:
        toast.error('Resource not found');
        break;
      case 500:
        toast.error('Server error. Please try again later');
        break;
      default:
        toast.error('An error occurred');
    }
  } else if (error.request) {
    // Request made but no response
    toast.error('No response from server. Check your connection');
  } else {
    // Something else happened
    toast.error('Request failed');
  }
};
```

---

## External Services Integration

### Google Maps Service

**Backend:** `backend/app/services/maps_service.py`

#### Geocoding Example

```python
from app.services.maps_service import maps_service

# Address to coordinates
result = await maps_service.geocode("123 Main St, San Francisco, CA")
# Returns: {"latitude": 37.7749, "longitude": -122.4194, ...}

# Coordinates to address
address = await maps_service.reverse_geocode(37.7749, -122.4194)
```

#### Route Calculation

```python
route = await maps_service.calculate_route(
    origin=(37.7749, -122.4194),
    destination=(37.7849, -122.4094),
    waypoints=[(37.7799, -122.4144)]
)
# Returns route with duration, distance, steps
```

### LLM Service (OpenAI)

**Backend:** `backend/app/services/llm_service.py`

#### Incident Analysis

```python
from app.services.llm_service import llm_service

analysis = await llm_service.analyze_incident_description(
    description="Patient with severe chest pain, sweating, shortness of breath",
    context={"age": 65, "location": "home"}
)
# Returns structured analysis with severity, injuries, requirements
```

#### Treatment Protocol Generation

```python
protocol = await llm_service.generate_treatment_protocol(
    incident_type="cardiac_emergency",
    severity="critical",
    symptoms=["chest pain", "dyspnea", "diaphoresis"],
    patient_age=65
)
# Returns step-by-step treatment protocol for paramedics
```

### SMS Service (Twilio)

**Backend:** `backend/app/services/sms_service.py`

```python
from app.services.sms_service import sms_service

# Send SMS with email fallback
result = await sms_service.send_sms(
    to="+15551234567",
    message="Ambulance AMB-001 dispatched to your location. ETA: 8 minutes.",
    fallback_email="patient@example.com"
)
```

### Vision Service (GPT-4 Vision)

**Backend:** `backend/app/services/vision_service.py`

```python
from app.services.vision_service import vision_service

# Analyze injury image
with open("injury_photo.jpg", "rb") as f:
    image_data = f.read()

analysis = await vision_service.analyze_injury_image(
    image_data=image_data,
    additional_context="Patient fell from ladder"
)
# Returns severity, injury types, recommendations
```

---

## WebSocket Real-Time Updates

### Backend WebSocket Events

**Endpoint:** `ws://localhost:8000/api/v1/ws`

**Events Emitted by Server:**
- `incident_created` - New incident created
- `incident_updated` - Incident status changed
- `ambulance_dispatched` - Ambulance assigned to incident
- `ambulance_location_update` - Ambulance location changed
- `agent_status_update` - AI agent status changed

### Frontend WebSocket Integration

```typescript
import io from 'socket.io-client';

const socket = io(process.env.REACT_APP_WS_URL, {
  auth: {
    token: localStorage.getItem('access_token')
  }
});

// Subscribe to incidents
socket.emit('subscribe_incidents');

// Listen for incident updates
socket.on('incident_created', (data) => {
  console.log('New incident:', data);
  // Update UI
  setIncidents(prev => [data, ...prev]);
});

socket.on('incident_updated', (data) => {
  console.log('Incident updated:', data);
  // Update specific incident in UI
  setIncidents(prev =>
    prev.map(inc => inc.id === data.id ? data : inc)
  );
});

// Subscribe to ambulance updates
socket.emit('subscribe_ambulances');

socket.on('ambulance_location_update', (data) => {
  // Update ambulance marker on map
  updateAmbulanceMarker(data.ambulance_id, data.latitude, data.longitude);
});

// Cleanup on unmount
useEffect(() => {
  return () => {
    socket.disconnect();
  };
}, []);
```

---

## Testing & Debugging

### Running Integration Tests

#### Full Python Test Suite

```bash
# Install test dependencies
cd backend/tests
pip install -r requirements.txt

# Run all integration tests
cd ..
python tests/integration/test_full_integration.py

# Expected output:
# ✓ PASS System health check (0.15s)
# ✓ PASS User login (0.43s)
# ...
# Total Tests: 32
# Passed: 32
# Failed: 0
# Pass Rate: 100.0%
```

#### Quick Bash Test Script

```bash
# From project root
./test_integration.sh

# Tests all endpoints with curl
# Provides color-coded pass/fail output
```

#### WebSocket Testing

```bash
python backend/tests/integration/test_websocket.py

# Tests WebSocket connection and events
# Listen for 30 seconds for real-time updates
```

### Manual API Testing with cURL

#### Test Authentication

```bash
# Register
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!","full_name":"Test User","role":"dispatcher"}'

# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Test123!"}'

# Save token
export TOKEN="your-access-token-here"
```

#### Test Incident Creation

```bash
curl -X POST http://localhost:8000/api/v1/incidents \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "type":"medical_emergency",
    "severity":"high",
    "description":"Test incident",
    "latitude":37.7749,
    "longitude":-122.4194,
    "reporter_name":"Test",
    "reporter_phone":"+15551234567"
  }'
```

### Debugging Tips

#### Enable Debug Logging

```python
# In backend/.env
DEBUG=True
LOG_LEVEL=DEBUG

# This will log:
# - All SQL queries
# - HTTP requests/responses
# - External API calls
# - Agent execution steps
```

#### Frontend Debug Mode

```bash
# In frontend/.env
REACT_APP_ENABLE_DEBUG_LOGS=true

# Open browser console to see:
# - API request/response logs
# - WebSocket events
# - State changes
```

#### Check Service Health

```bash
# Backend health
curl http://localhost:8000/health

# Database connection
curl http://localhost:8000/api/health

# Check logs
tail -f backend/logs/aria.log
```

---

## Common Issues & Solutions

### Issue: "Invalid API Key" for External Services

**Symptoms:**
- 401 Unauthorized errors
- "API key not found" messages

**Solutions:**
1. Check `.env` file has correct keys (no quotes, no spaces)
2. Verify keys are active in provider dashboards
3. Restart backend server after updating `.env`
4. Check for typos in environment variable names

### Issue: CORS Errors in Frontend

**Symptoms:**
- Browser console shows CORS policy errors
- Requests blocked by browser

**Solutions:**
1. Verify `CORS_ORIGINS` in backend `.env` includes frontend URL
2. Check frontend is running on expected port (3000)
3. Restart backend after CORS changes
4. Clear browser cache

### Issue: WebSocket Connection Fails

**Symptoms:**
- "WebSocket connection failed" in console
- Real-time updates not working

**Solutions:**
1. Check backend WebSocket endpoint is running
2. Verify WebSocket URL in frontend `.env`
3. Check firewall isn't blocking WebSocket connections
4. Ensure JWT token is valid and being sent

### Issue: Database Connection Error

**Symptoms:**
- "Could not connect to database" errors
- 500 errors on all endpoints

**Solutions:**
1. Verify PostgreSQL is running: `pg_isready`
2. Check `DATABASE_URL` in `.env` is correct
3. Verify database exists: `psql -l`
4. Check credentials and permissions
5. Run migrations: `alembic upgrade head`

### Issue: ML Models Not Loading

**Symptoms:**
- Warnings about missing model files
- Hotspot predictions return empty results

**Solutions:**
1. Check `MODEL_PATH` in `.env` points to correct directory
2. Verify model files exist in models directory
3. Train models if not present (see ML documentation)
4. Set `ENABLE_ML_PREDICTIONS=False` to use fallback logic

### Issue: Frontend Can't Connect to Backend

**Symptoms:**
- "Network Error" messages
- All API calls fail

**Solutions:**
1. Verify backend is running: `curl http://localhost:8000/health`
2. Check `REACT_APP_API_BASE_URL` in frontend `.env`
3. Ensure no other service is using port 8000
4. Check firewall rules
5. Try accessing API directly in browser

### Issue: Token Expired / 401 Errors

**Symptoms:**
- Logged out unexpectedly
- 401 errors on authenticated endpoints

**Solutions:**
1. Tokens expire after 30 minutes by default
2. Frontend should auto-refresh using refresh token
3. Check refresh token interceptor is working
4. Clear localStorage and log in again
5. Adjust `ACCESS_TOKEN_EXPIRE_MINUTES` if needed

---

## Performance Optimization

### Backend Optimization

#### Database Query Optimization

```python
# Use eager loading to avoid N+1 queries
from sqlalchemy.orm import selectinload

incidents = await db.execute(
    select(Incident)
    .options(selectinload(Incident.ambulance))
    .options(selectinload(Incident.hospital))
)

# Use pagination
incidents = await db.execute(
    select(Incident)
    .offset(skip)
    .limit(limit)
)
```

#### Caching with Redis

```python
import redis
from functools import lru_cache

# Cache expensive operations
@lru_cache(maxsize=128)
async def get_nearby_hospitals(lat, lng, radius):
    # Expensive database query
    return results

# Use Redis for distributed caching
redis_client = redis.Redis(host='localhost', port=6379)

# Cache API responses
cache_key = f"hospitals:nearby:{lat}:{lng}:{radius}"
cached = redis_client.get(cache_key)
if cached:
    return json.loads(cached)

# Compute and cache
result = compute_nearby_hospitals()
redis_client.setex(cache_key, 300, json.dumps(result))  # 5 min TTL
```

#### Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/v1/incidents")
@limiter.limit("60/minute")
async def list_incidents():
    # Endpoint logic
    pass
```

### Frontend Optimization

#### Lazy Loading Components

```typescript
// routes/index.tsx
const ResourceAllocation = lazy(() => import('../pages/ResourceAllocation'));

// Wrap in Suspense
<Suspense fallback={<LoadingSpinner />}>
  <ResourceAllocation />
</Suspense>
```

#### Debouncing API Calls

```typescript
import { debounce } from 'lodash';

const debouncedSearch = useMemo(
  () => debounce(async (query) => {
    const results = await apiClient.get(`/search?q=${query}`);
    setResults(results.data);
  }, 500),
  []
);

const handleSearchChange = (e) => {
  debouncedSearch(e.target.value);
};
```

#### Memoization

```typescript
import { useMemo, useCallback } from 'react';

// Memoize expensive computations
const sortedIncidents = useMemo(() => {
  return incidents.sort((a, b) => 
    new Date(b.created_at) - new Date(a.created_at)
  );
}, [incidents]);

// Memoize callbacks
const handleIncidentClick = useCallback((id) => {
  navigate(`/incidents/${id}`);
}, [navigate]);
```

---

## Security Considerations

### Authentication & Authorization

1. **JWT Tokens:**
   - Access tokens expire after 30 minutes
   - Refresh tokens expire after 7 days
   - Store only in httpOnly cookies or secure localStorage
   - Never log tokens

2. **Role-Based Access Control (RBAC):**
   ```python
   from app.models.user import UserRole
   
   @router.get("/admin/users")
   async def get_users(
       current_user: User = Depends(get_current_user)
   ):
       if current_user.role != UserRole.ADMIN:
           raise HTTPException(status_code=403)
   ```

3. **Input Validation:**
   - All inputs validated with Pydantic
   - Sanitize user-provided content
   - Use parameterized queries (SQLAlchemy ORM)

### API Security

1. **Rate Limiting:**
   - 60 requests per minute per IP
   - 1000 requests per hour per IP
   - Configurable in `.env`

2. **CORS Configuration:**
   ```python
   # Only allow specific origins
   CORS_ORIGINS=["https://app.aria-emergency.com"]
   ```

3. **HTTPS Only:**
   - Use HTTPS in production
   - Set `Secure` and `HttpOnly` flags on cookies
   - Enable HSTS headers

### Data Protection

1. **Sensitive Data:**
   - Never log passwords, tokens, or API keys
   - Encrypt sensitive fields in database
   - Use environment variables for secrets

2. **PII Handling:**
   - Log minimal personally identifiable information
   - Implement data retention policies
   - Provide data export/deletion endpoints

3. **API Key Security:**
   - Rotate keys regularly (90 days)
   - Use separate keys for dev/staging/prod
   - Monitor usage for anomalies
   - Revoke compromised keys immediately

---

## Support & Resources

### Documentation
- API Reference: `/docs` (Swagger UI)
- ReDoc: `/redoc` (Alternative API docs)
- Setup Guide: `SETUP-API-KEYS.md`
- Backend API Guide: `BACKEND-API-GUIDE.md`

### Logging & Monitoring
- Application logs: `backend/logs/aria.log`
- Access logs: Configured in FastAPI
- Metrics endpoint: `/metrics` (Prometheus format)

### Getting Help
1. Check this integration guide
2. Review error logs
3. Run integration tests to isolate issue
4. Check external service status pages
5. Review GitHub issues (if applicable)

---

**Document Version:** 1.0.0  
**Last Updated:** 2024  
**Maintained By:** ARIA Platform Team

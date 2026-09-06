# ARIA Complete Integration Guide

## 🎯 Overview

This guide covers the complete integration of all services for the ARIA Emergency Response Platform.

## 📦 What Has Been Created

### Backend Services (Python/FastAPI)

#### 1. **Maps Services** (`backend/app/services/maps/`)
- ✅ `google_maps_service.py` - Google Maps API integration (geocoding, routing, places, traffic)
- ✅ `osrm_service.py` - Open Source Routing Machine (fallback routing)
- ✅ `geocoding_service.py` - Unified geocoding with automatic fallback

**Features:**
- Address ↔ GPS coordinates conversion
- Multi-route optimization
- Real-time traffic consideration
- Distance matrix calculations
- Nearby places search
- Address autocomplete
- Automatic fallback to OSM/OSRM if Google fails

#### 2. **Notification Services** (`backend/app/services/notifications/`)
- ✅ `sms_service.py` - Twilio SMS integration
- ✅ `email_service.py` - SendGrid email integration
- ✅ `notification_service.py` - Orchestrator with intelligent routing
- ✅ `templates.py` - All SMS and HTML email templates

**Features:**
- SMS notifications with delivery tracking
- HTML email templates
- Batch notifications
- Priority-based routing (emergency → SMS first)
- User preference management
- Automatic fallback (SMS fails → Email)

**Templates:**
- Incident Created
- Ambulance Dispatched
- Patient En Route
- Blood Required
- Plan Approved/Rejected
- Family Notifications

#### 3. **LLM Services** (`backend/app/services/llm/`)
- ✅ `llm_service.py` - OpenAI GPT-4 integration
- ✅ `prompts.py` - All LLM prompts for various tasks

**Features:**
- Incident understanding and parsing
- Extract structured data from descriptions
- Incident classification and severity assessment
- Location extraction
- Multi-language support detection
- Summarization (incident, handoff, family-friendly)
- Response protocol generation
- Triage protocol (START protocol)
- Resource recommendations

#### 4. **Speech Services** (`backend/app/services/speech/`)
- ✅ `whisper_service.py` - OpenAI Whisper for speech-to-text

**Features:**
- Audio file transcription (mp3, wav, m4a, etc.)
- Multi-language transcription
- Real-time emergency call transcription
- Audio bytes transcription
- Translation to English
- Automatic emergency info extraction

#### 5. **Vision Services** (`backend/app/services/vision/`)
- ✅ `vision_service.py` - OpenAI GPT-4V for image analysis

**Features:**
- Injury detection from images
- Severity assessment
- Body part identification
- Injury type classification (bleeding, burns, fractures)
- First aid recommendations
- Hospital specialty recommendations
- Multi-image analysis
- Scene safety assessment

### Frontend Integration (React/TypeScript)

#### 6. **Core Utilities** (`frontend/src/utils/`)
- ✅ `apiClient.ts` - Axios-based API client with auth & error handling
- ✅ `errorHandler.ts` - Centralized error handling
- ✅ `apiTester.ts` - Comprehensive API testing utility

**Features:**
- Automatic token refresh
- Request/response interceptors
- Error handling with toast notifications
- File upload with progress tracking
- Retry with exponential backoff
- WebSocket connection testing

### Configuration Files

#### 7. **Environment Files**
- ✅ `.env.development` - Backend development config
- ✅ `.env.staging` - Backend staging config
- ✅ `.env.production` - Backend production config
- ✅ `frontend/.env.development` - Frontend development config
- ✅ `frontend/.env.staging` - Frontend staging config
- ✅ `frontend/.env.production` - Frontend production config

#### 8. **Dependencies**
- ✅ `backend/requirements-integration.txt` - Additional Python packages

## 🚀 Setup Instructions

### 1. Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-integration.txt
```

### 2. Configure Environment Variables

#### Backend (.env)
```bash
# Copy the development env file
cp ../.env.development backend/.env

# Edit and add your API keys
nano backend/.env
```

**Required API Keys:**
- `OPENAI_API_KEY` - For GPT-4, Whisper, and Vision
- `GOOGLE_MAPS_API_KEY` - For Google Maps
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER` - For SMS
- `SENDGRID_API_KEY` - For emails
- `OPENWEATHER_API_KEY` - For weather data

#### Frontend (.env)
```bash
cd frontend
cp .env.development .env
nano .env
```

### 3. Start Services

#### Backend
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

#### Frontend
```bash
cd frontend
npm install
npm start
```

### 4. Test Integration

Open browser console and run:
```javascript
import { apiTester } from './utils/apiTester';

// Run all API tests
apiTester.runAllTests().then(results => {
  console.log('Test Results:', results);
});
```

## 📡 API Endpoints Overview

### Authentication
- `POST /api/v1/auth/login` - Login
- `POST /api/v1/auth/refresh` - Refresh token
- `GET /api/v1/auth/me` - Get current user

### Incidents
- `POST /api/v1/incidents` - Create incident
- `GET /api/v1/incidents` - List incidents
- `GET /api/v1/incidents/{id}` - Get incident details
- `POST /api/v1/incidents/{id}/approve` - Approve plan
- `POST /api/v1/incidents/{id}/reject` - Reject plan
- `POST /api/v1/incidents/{id}/dispatch` - Dispatch resources
- `PATCH /api/v1/incidents/{id}/status` - Update status

### Hospitals
- `GET /api/v1/hospitals` - List hospitals
- `GET /api/v1/hospitals/nearby` - Find nearby hospitals
- `POST /api/v1/hospitals/rank` - Rank hospitals (ML)
- `POST /api/v1/hospitals/availability` - Check bed availability (ML)

### Ambulances
- `GET /api/v1/ambulances` - List ambulances
- `GET /api/v1/ambulances/available` - Available ambulances
- `POST /api/v1/ambulances/nearest` - Find nearest (ML + ETA)
- `PATCH /api/v1/ambulances/{id}/location` - Update GPS location
- `PATCH /api/v1/ambulances/{id}/status` - Update status

### Dashboard
- `GET /api/v1/dashboard/stats` - System statistics
- `GET /api/v1/dashboard/active-incidents` - Active incidents for map
- `GET /api/v1/dashboard/agent-status` - All 9 agent statuses
- `GET /api/v1/dashboard/hotspots` - Incident hotspots (ML)

### Resource Allocation
- `POST /api/v1/resource-allocation/allocate` - Allocate resources
- `GET /api/v1/resource-allocation/history` - Allocation history

### WebSocket
- `WS /api/v1/ws?token={jwt}` - Real-time updates

## 🔥 Real-Time Events

WebSocket events broadcast to connected clients:

```javascript
// Incident events
"incident.created"
"incident.updated"
"incident.plan_generated"
"incident.plan_approved"
"incident.plan_rejected"
"incident.dispatched"
"incident.completed"

// Resource events
"ambulance.location_updated"
"ambulance.status_changed"
"ambulance.assigned"
"hospital.bed_update"

// Agent events
"agent.status_changed"
"agent.error"
```

## 🎨 Frontend Integration Examples

### 1. Create Incident with Voice
```typescript
import { whisperService } from '@/services/whisperService';
import { incidentService } from '@/services/incidentService';

// Record audio
const audioBlob = await recordAudio();

// Transcribe
const transcript = await whisperService.transcribe(audioBlob);

// Extract info with LLM
const incidentData = await llmService.parseIncident(transcript.text);

// Create incident
const incident = await incidentService.create(incidentData);
```

### 2. Upload Injury Image
```typescript
import { visionService } from '@/services/visionService';

// Upload image
const file = event.target.files[0];
const analysis = await visionService.analyzeInjury(file);

// Use analysis in incident
incidentData.injuries = analysis.injuries_identified;
incidentData.severity = analysis.severity_assessment;
```

### 3. Real-time Updates
```typescript
import { useWebSocket } from '@/hooks/useWebSocket';

function IncidentMap() {
  const { lastMessage } = useWebSocket();
  
  useEffect(() => {
    if (lastMessage?.type === 'ambulance.location_updated') {
      updateAmbulanceMarker(lastMessage.data);
    }
  }, [lastMessage]);
}
```

### 4. Send Notifications
```typescript
import { notificationService } from '@/services/notificationService';

// Send incident notification
await notificationService.send({
  type: 'incident_created',
  recipients: [coordinator],
  data: incident,
  priority: 'emergency'
});
```

## 🧪 Testing

### Backend Unit Tests
```bash
cd backend
pytest tests/integration/
```

### Frontend API Tests
```bash
cd frontend
npm test
```

### Manual Testing Checklist

#### ✅ Authentication
- [ ] Login with credentials
- [ ] Token refresh on 401
- [ ] Logout clears tokens

#### ✅ Incident Workflow
- [ ] Create incident (form)
- [ ] Create incident (voice)
- [ ] View incident details
- [ ] Approve plan
- [ ] Reject plan with reason
- [ ] Dispatch resources
- [ ] Real-time status updates

#### ✅ Map Integration
- [ ] View all hospitals on map
- [ ] View nearby hospitals
- [ ] View ambulances with real-time tracking
- [ ] Route polyline display
- [ ] Traffic overlay

#### ✅ Notifications
- [ ] SMS sent on incident creation
- [ ] Email sent on incident creation
- [ ] SMS sent on ambulance dispatch
- [ ] Email sent on plan approval

#### ✅ AI Features
- [ ] Voice transcription works
- [ ] Image analysis detects injuries
- [ ] LLM extracts incident info
- [ ] Protocols generated correctly

#### ✅ Real-time Updates
- [ ] WebSocket connects
- [ ] Ambulance locations update
- [ ] Incident status updates broadcast
- [ ] Agent status visible

## 🔧 Troubleshooting

### Common Issues

**1. API Key Errors**
- Ensure all API keys are set in `.env`
- Check API key permissions and quotas
- Verify API services are enabled

**2. WebSocket Connection Fails**
- Check JWT token is valid
- Ensure WebSocket URL is correct
- Check firewall/proxy settings

**3. Geocoding Fails**
- Google Maps falls back to Nominatim automatically
- Check rate limits
- Verify address format

**4. SMS/Email Not Sending**
- Verify Twilio/SendGrid credentials
- Check phone number format (E.164)
- Check SendGrid sender verification

**5. ML Model Errors**
- Ensure models are trained and saved
- Check MODEL_PATH in config
- Verify PostGIS extension for spatial queries

## 📊 Monitoring

### Logs
```bash
# Backend logs
tail -f backend/logs/aria_dev.log

# Error logs
grep ERROR backend/logs/aria_dev.log
```

### Metrics
```bash
# Prometheus metrics endpoint
curl http://localhost:8000/metrics
```

### Health Check
```bash
# System health
curl http://localhost:8000/health

# API health
curl http://localhost:8000/api/health
```

## 🚦 Deployment

### Backend (Docker)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt requirements-integration.txt ./
RUN pip install -r requirements.txt -r requirements-integration.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend (Docker)
```dockerfile
FROM node:18-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 📚 Next Steps

1. **Add More API Endpoints** (as needed)
   - Blood banks CRUD
   - User management
   - Reports and analytics

2. **Enhance Frontend**
   - Complete all page implementations
   - Add more visualizations
   - Implement offline mode

3. **Improve ML Models**
   - Retrain with more data
   - Add model versioning
   - A/B testing framework

4. **Security Hardening**
   - Rate limiting per user
   - Input validation
   - API key rotation
   - Audit logging

5. **Performance Optimization**
   - Redis caching
   - Database indexing
   - CDN for static assets
   - Image optimization

## 🎓 Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [OpenAI API](https://platform.openai.com/docs/)
- [Google Maps API](https://developers.google.com/maps)
- [Twilio Docs](https://www.twilio.com/docs)
- [SendGrid Docs](https://docs.sendgrid.com/)
- [React Documentation](https://react.dev/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)

## 💡 Support

For issues or questions:
1. Check this guide
2. Review API documentation at `/docs`
3. Check logs for error messages
4. Review test results from `apiTester`

---

**Built with ❤️ for Emergency Response**

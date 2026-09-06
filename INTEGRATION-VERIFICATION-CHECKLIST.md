# 🔍 ARIA Integration Verification Checklist

Use this checklist to systematically verify that all integration components are working correctly.

---

## 📋 Pre-Verification Setup

### Step 1: Install Dependencies
- [ ] Backend dependencies installed (`pip install -r requirements-integration.txt`)
- [ ] Frontend dependencies installed (`npm install`)
- [ ] PostgreSQL running with PostGIS extension
- [ ] Redis running and accessible

### Step 2: Configure Environment
- [ ] `backend/.env` file created with all API keys
- [ ] `frontend/.env` file created
- [ ] Database URL configured correctly
- [ ] Redis URL configured correctly

### Step 3: API Keys Configured
- [ ] `OPENAI_API_KEY` set (for GPT-4, Whisper, Vision)
- [ ] `GOOGLE_MAPS_API_KEY` set
- [ ] `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` set
- [ ] `TWILIO_PHONE_NUMBER` set
- [ ] `SENDGRID_API_KEY` set
- [ ] `SENDGRID_FROM_EMAIL` verified in SendGrid

---

## 🔧 Backend Service Verification

### Google Maps Services

#### Geocoding
```bash
# Test from Python
cd backend
source venv/bin/activate
python3 << EOF
import asyncio
from app.services.maps.google_maps_service import google_maps_service

async def test():
    result = await google_maps_service.geocode_address("1600 Amphitheatre Parkway, Mountain View, CA")
    print("✅ Geocoding:", result)

asyncio.run(test())
EOF
```
- [ ] Address geocoded successfully
- [ ] Returns latitude and longitude
- [ ] Returns formatted address

#### Reverse Geocoding
```python
# In Python shell
result = await google_maps_service.reverse_geocode(37.7749, -122.4194)
```
- [ ] Coordinates reverse geocoded
- [ ] Returns formatted address

#### Routing
```python
# In Python shell
result = await google_maps_service.get_directions((37.7749, -122.4194), (37.7849, -122.4094))
```
- [ ] Route calculated successfully
- [ ] Returns distance and duration
- [ ] Returns polyline
- [ ] Traffic data included

#### OSRM Fallback
```python
from app.services.maps.osrm_service import osrm_service
result = await osrm_service.get_route((37.7749, -122.4194), (37.7849, -122.4094))
```
- [ ] OSRM routing works as fallback
- [ ] Returns distance and duration

### Notification Services

#### SMS Service
```python
from app.services.notifications.sms_service import sms_service
result = await sms_service.send_sms("+1234567890", "Test SMS from ARIA")
```
- [ ] SMS sent successfully
- [ ] Returns message SID
- [ ] SMS received on phone
- [ ] Delivery status trackable

#### Email Service
```python
from app.services.notifications.email_service import email_service
result = await email_service.send_email(
    "test@example.com",
    "Test Email",
    "<h1>Test HTML Email</h1>",
    "Test Plain Email"
)
```
- [ ] Email sent successfully
- [ ] Returns message ID
- [ ] Email received in inbox
- [ ] HTML formatting correct

#### Notification Orchestrator
```python
from app.services.notifications.notification_service import notification_service, NotificationType
result = await notification_service.send_notification(
    NotificationType.INCIDENT_CREATED,
    {"name": "Test User", "email": "test@example.com", "phone": "+1234567890"},
    {"incident_id": "TEST-001", "incident_type": "test", "severity": "high", "location": "Test Location", "victim_count": 1, "created_at": "2026-09-06T12:00:00", "description": "Test incident", "portal_url": "http://localhost:3000"}
)
```
- [ ] Notification sent via SMS
- [ ] Notification sent via Email
- [ ] Both channels reported success

### LLM Services

#### Incident Parsing
```python
from app.services.llm.llm_service import llm_service
result = await llm_service.parse_incident_description(
    "Car accident on Highway 101, 3 victims with severe injuries, multiple vehicles involved"
)
```
- [ ] Incident parsed successfully
- [ ] Returns structured JSON
- [ ] Incident type identified
- [ ] Severity assessed
- [ ] Victim count extracted
- [ ] Injuries identified

#### Summarization
```python
result = await llm_service.summarize_incident(
    "Long incident description here..."
)
```
- [ ] Summary generated
- [ ] Concise and clear
- [ ] Key information preserved

#### Protocol Generation
```python
result = await llm_service.generate_response_protocol(
    "road_accident",
    "critical",
    ["head trauma", "fracture", "bleeding"]
)
```
- [ ] Protocol generated
- [ ] Includes steps
- [ ] Includes equipment list
- [ ] Includes warnings

### Speech Services

#### Whisper Transcription
```python
from app.services.speech.whisper_service import whisper_service
# Prepare test audio file
result = await whisper_service.transcribe_audio("test_audio.mp3")
```
- [ ] Audio transcribed
- [ ] Returns text
- [ ] Language detected
- [ ] Duration calculated

### Vision Services

#### Image Analysis
```python
from app.services.vision.vision_service import vision_service
# Prepare test injury image
result = await vision_service.analyze_injury_image("test_injury.jpg")
```
- [ ] Image analyzed
- [ ] Injuries identified
- [ ] Severity assessed
- [ ] Body parts identified
- [ ] Recommendations provided

---

## 🎨 Frontend Integration Verification

### API Client

Open browser console and test:

```javascript
// 1. Import API client
import { apiClient } from './utils/apiClient';

// 2. Test health endpoint
const health = await apiClient.get('/health');
console.log('Health:', health);

// 3. Test login
const login = await apiClient.post('/api/v1/auth/login', {
  username: 'admin',
  password: 'admin123'
});
console.log('Login:', login);

// 4. Test authenticated endpoint
const me = await apiClient.get('/api/v1/auth/me');
console.log('Current User:', me);
```

Checklist:
- [ ] Health check successful
- [ ] Login successful
- [ ] Token stored in localStorage
- [ ] Authenticated requests work
- [ ] Authorization header set automatically

### Error Handler

```javascript
import { errorHandler } from './utils/errorHandler';

// Test error handling
try {
  await apiClient.get('/api/v1/nonexistent');
} catch (error) {
  const handled = errorHandler.handle(error);
  console.log('Error handled:', handled);
}
```

- [ ] 404 error caught
- [ ] Toast notification shown
- [ ] User-friendly message displayed
- [ ] Error logged in console (dev mode)

### API Tester

```javascript
import { apiTester } from './utils/apiTester';

// Run all tests
const results = await apiTester.runAllTests();
console.log('Test Results:', results);
```

Expected Results:
- [ ] All authentication tests pass
- [ ] Incident creation test passes
- [ ] Hospital endpoints respond
- [ ] Ambulance endpoints respond
- [ ] Dashboard endpoints respond
- [ ] WebSocket connects successfully
- [ ] Overall pass rate > 90%

---

## 🔄 End-to-End Workflow Tests

### Workflow 1: Create Incident (Form)
1. [ ] Navigate to incident creation page
2. [ ] Fill in all required fields
3. [ ] Submit form
4. [ ] Incident created successfully
5. [ ] Redirected to incident details
6. [ ] Notification sent (check SMS/Email)

### Workflow 2: Create Incident (Voice)
1. [ ] Click voice input button
2. [ ] Record audio description
3. [ ] Stop recording
4. [ ] Audio transcribed automatically
5. [ ] Incident fields populated
6. [ ] Review and submit
7. [ ] Incident created

### Workflow 3: Upload Injury Image
1. [ ] Navigate to incident form
2. [ ] Upload injury image
3. [ ] Image analyzed by Vision AI
4. [ ] Injury details populated automatically
5. [ ] Review suggestions
6. [ ] Submit incident

### Workflow 4: Approve Plan → Dispatch
1. [ ] View incident with pending plan
2. [ ] Review generated plan
3. [ ] Click approve button
4. [ ] Approval notification sent
5. [ ] Click dispatch button
6. [ ] Resources allocated
7. [ ] Dispatch notifications sent
8. [ ] Status updated to "dispatched"
9. [ ] Real-time updates received

### Workflow 5: Real-time Tracking
1. [ ] Open dashboard
2. [ ] View active incidents map
3. [ ] See ambulance locations
4. [ ] Update ambulance location (API)
5. [ ] Marker updates in real-time
6. [ ] No page refresh needed

---

## 🔌 WebSocket Verification

### Connect to WebSocket
```javascript
const wsUrl = 'ws://localhost:8000/api/v1/ws';
const token = localStorage.getItem('access_token');
const ws = new WebSocket(`${wsUrl}?token=${token}`);

ws.onopen = () => console.log('✅ WebSocket connected');
ws.onmessage = (event) => console.log('📨 Message:', JSON.parse(event.data));
ws.onerror = (error) => console.error('❌ WebSocket error:', error);
ws.onclose = () => console.log('🔌 WebSocket closed');
```

Test Events:
- [ ] Connection established
- [ ] `incident.created` event received
- [ ] `incident.updated` event received
- [ ] `ambulance.location_updated` event received
- [ ] `plan_generated` event received
- [ ] `plan_approved` event received
- [ ] Connection persists during activity

---

## 🚦 Performance Tests

### Backend Performance
```bash
# Use Apache Bench
ab -n 1000 -c 10 http://localhost:8000/health

# Check response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost:8000/api/v1/incidents
```

Metrics:
- [ ] Average response time < 200ms (health)
- [ ] Average response time < 500ms (API endpoints)
- [ ] 99th percentile < 1s
- [ ] No 500 errors under load
- [ ] Memory usage stable

### Frontend Performance
```javascript
// Measure component render time
console.time('IncidentList Render');
// Render component
console.timeEnd('IncidentList Render');
```

- [ ] Initial load < 3s
- [ ] API requests < 1s
- [ ] Component renders < 100ms
- [ ] No memory leaks
- [ ] Smooth animations (60fps)

---

## 🔐 Security Verification

### Authentication
- [ ] Login required for protected routes
- [ ] Token expiration works (wait 30 min)
- [ ] Token refresh automatic
- [ ] Logout clears tokens
- [ ] Cannot access API without token

### Authorization
- [ ] Different roles have different permissions
- [ ] 403 errors for unauthorized actions
- [ ] User cannot see others' private data

### Input Validation
- [ ] SQL injection prevented (try: `' OR '1'='1`)
- [ ] XSS prevented (try: `<script>alert('XSS')</script>`)
- [ ] File upload restrictions work
- [ ] Phone number validation works
- [ ] Email validation works

### API Security
- [ ] CORS configured correctly
- [ ] Rate limiting active (try 100 requests/sec)
- [ ] HTTPS enforced (production)
- [ ] API keys not exposed in frontend

---

## 📊 Monitoring & Logging

### Logs
```bash
# Check backend logs
tail -f backend/logs/aria_dev.log

# Filter errors
grep ERROR backend/logs/aria_dev.log

# Check access logs
grep "POST /api/v1/incidents" backend/logs/aria_dev.log
```

- [ ] Logs being written
- [ ] Timestamps correct
- [ ] Log levels appropriate
- [ ] No sensitive data in logs (passwords, tokens)
- [ ] Request IDs present

### Metrics
```bash
# Check Prometheus metrics
curl http://localhost:8000/metrics
```

- [ ] Metrics endpoint accessible
- [ ] Request count tracked
- [ ] Response time tracked
- [ ] Error rate tracked

---

## 🐛 Error Handling Tests

### Network Errors
- [ ] Stop backend → Frontend shows "Network Error"
- [ ] Slow network → Loading states shown
- [ ] Connection restored → Auto-retry works

### API Errors
- [ ] 400 Bad Request → Validation error shown
- [ ] 401 Unauthorized → Redirect to login
- [ ] 403 Forbidden → Permission error shown
- [ ] 404 Not Found → Not found page/message
- [ ] 500 Server Error → Generic error + retry option
- [ ] 503 Unavailable → Service unavailable message

### Fallback Mechanisms
- [ ] Google Maps fails → OSRM used
- [ ] Geocoding fails → Nominatim used
- [ ] SMS fails → Email sent instead
- [ ] LLM timeout → Rule-based fallback (if implemented)

---

## ✅ Final Verification

### Documentation
- [ ] README.md is clear
- [ ] COMPLETE-INTEGRATION-GUIDE.md is comprehensive
- [ ] API documentation at `/docs` is complete
- [ ] Code comments are helpful
- [ ] Environment variables documented

### Code Quality
- [ ] No console errors in browser
- [ ] No Python errors in logs
- [ ] TypeScript compilation successful
- [ ] No ESLint warnings
- [ ] Code formatted consistently

### Deployment Readiness
- [ ] Production .env template exists
- [ ] Docker files prepared (if using Docker)
- [ ] Database migrations ready
- [ ] Static files optimized
- [ ] CDN configuration ready (if needed)

---

## 🎉 Sign-Off

When all items above are checked:

**Date:** _______________

**Verified by:** _______________

**Status:** ✅ Ready for Production / ⚠️ Needs Attention / ❌ Not Ready

**Notes:**
_________________________________________________
_________________________________________________
_________________________________________________

---

## 📞 Troubleshooting Quick Reference

### Issue: API Key Error
**Solution:** Verify API key in `.env`, check quotas, ensure service is enabled

### Issue: WebSocket Won't Connect
**Solution:** Check JWT token, verify WebSocket URL, check firewall

### Issue: SMS Not Sending
**Solution:** Verify Twilio credentials, check phone format (E.164), check balance

### Issue: Email Not Sending
**Solution:** Verify SendGrid key, check sender verification, check spam folder

### Issue: Geocoding Fails
**Solution:** Check Google Maps key, verify billing enabled, fallback should activate

### Issue: LLM Timeout
**Solution:** Increase timeout, check OpenAI API status, verify API key

### Issue: Database Connection Error
**Solution:** Check PostgreSQL running, verify DATABASE_URL, check PostGIS installed

### Issue: Redis Connection Error
**Solution:** Check Redis running, verify REDIS_URL, check Redis password if set

---

**Good luck with your integration testing!** 🚀

For detailed help, see [COMPLETE-INTEGRATION-GUIDE.md](./COMPLETE-INTEGRATION-GUIDE.md)

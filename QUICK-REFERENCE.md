# 🚀 ARIA Quick Reference Card

Quick commands and code snippets for daily development.

---

## 🎯 Quick Start

```bash
# Setup (one time)
./setup-integration.sh

# Start Backend
cd backend && source venv/bin/activate && uvicorn app.main:app --reload

# Start Frontend (new terminal)
cd frontend && npm start

# Run Tests
cd backend && pytest tests/
cd frontend && npm test
```

---

## 🔑 Environment Variables

```bash
# Required API Keys
OPENAI_API_KEY=sk-...
GOOGLE_MAPS_API_KEY=AIza...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
SENDGRID_API_KEY=SG...
```

---

## 📡 Common API Calls

### Authentication
```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Get current user
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Create Incident
```bash
curl -X POST http://localhost:8000/api/v1/incidents \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Road Accident",
    "description": "Multiple vehicle collision",
    "incident_type": "road_accident",
    "severity": "high",
    "latitude": 37.7749,
    "longitude": -122.4194,
    "victim_count": 3
  }'
```

### Get Dashboard Stats
```bash
curl http://localhost:8000/api/v1/dashboard/stats \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🐍 Python Quick Tests

### Test Geocoding
```python
import asyncio
from app.services.maps.geocoding_service import geocoding_service

async def test():
    result = await geocoding_service.geocode_address("Times Square, New York")
    print(result)

asyncio.run(test())
```

### Test SMS
```python
from app.services.notifications.sms_service import sms_service

result = await sms_service.send_sms(
    "+1234567890",
    "Test SMS from ARIA"
)
print(result)
```

### Test LLM
```python
from app.services.llm.llm_service import llm_service

result = await llm_service.parse_incident_description(
    "Car accident, 2 victims, Highway 101"
)
print(result)
```

---

## ⚛️ React Quick Snippets

### Use API Client
```typescript
import { apiClient } from '@/utils/apiClient';

// GET
const incidents = await apiClient.get('/api/v1/incidents');

// POST
const incident = await apiClient.post('/api/v1/incidents', data);

// PATCH
const updated = await apiClient.patch(`/api/v1/incidents/${id}`, data);

// Upload File
const result = await apiClient.upload('/api/v1/vision/analyze', file, 
  (progress) => console.log(`${progress}%`)
);
```

### Handle Errors
```typescript
import { errorHandler, safeAsync } from '@/utils/errorHandler';

// Wrapped call
const [data, error] = await safeAsync(
  () => apiClient.get('/api/v1/incidents')
);

if (error) {
  console.error('Failed:', error.message);
}
```

### WebSocket Connection
```typescript
import { useWebSocket } from '@/hooks/useWebSocket';

function Component() {
  const { lastMessage, sendMessage } = useWebSocket();
  
  useEffect(() => {
    if (lastMessage?.type === 'incident.created') {
      console.log('New incident:', lastMessage.data);
    }
  }, [lastMessage]);
}
```

---

## 🗺️ Maps Integration

### Geocode Address
```typescript
// Frontend
const response = await apiClient.post('/api/v1/maps/geocode', {
  address: "1600 Amphitheatre Parkway, Mountain View, CA"
});

// Backend Python
from app.services.maps.google_maps_service import google_maps_service
result = await google_maps_service.geocode_address(address)
```

### Get Directions
```typescript
// Frontend
const response = await apiClient.post('/api/v1/maps/directions', {
  origin: { lat: 37.7749, lng: -122.4194 },
  destination: { lat: 37.7849, lng: -122.4094 }
});

// Backend Python
result = await google_maps_service.get_directions(
    (37.7749, -122.4194),
    (37.7849, -122.4094)
)
```

---

## 📧 Notifications

### Send SMS
```python
from app.services.notifications.sms_service import sms_service

await sms_service.send_sms(
    to="+1234567890",
    message="Emergency notification",
    priority="emergency"
)
```

### Send Email
```python
from app.services.notifications.email_service import email_service

await email_service.send_email(
    to="user@example.com",
    subject="Incident Alert",
    html_content="<h1>Emergency</h1>",
    plain_content="Emergency"
)
```

### Send Both (Orchestrator)
```python
from app.services.notifications.notification_service import notification_service, NotificationType

await notification_service.send_notification(
    notification_type=NotificationType.INCIDENT_CREATED,
    recipient={
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "+1234567890"
    },
    data=incident_data,
    priority="emergency"
)
```

---

## 🤖 AI Services

### Parse Incident (LLM)
```python
from app.services.llm.llm_service import llm_service

result = await llm_service.parse_incident_description(
    description="Car crash on Highway 101, 3 injured"
)
# Returns: incident_type, severity, injuries, etc.
```

### Transcribe Audio (Whisper)
```python
from app.services.speech.whisper_service import whisper_service

result = await whisper_service.transcribe_audio("call.mp3")
# Returns: text, language, duration
```

### Analyze Image (Vision)
```python
from app.services.vision.vision_service import vision_service

result = await vision_service.analyze_injury_image("injury.jpg")
# Returns: injuries, severity, recommendations
```

---

## 🔍 Debugging

### Check Logs
```bash
# Tail logs
tail -f backend/logs/aria_dev.log

# Filter errors
grep ERROR backend/logs/aria_dev.log

# Watch real-time
watch -n 1 "tail -20 backend/logs/aria_dev.log"
```

### Test API Health
```bash
# Backend health
curl http://localhost:8000/health

# Database health
curl http://localhost:8000/health | jq '.database'

# All services
curl http://localhost:8000/health | jq
```

### Browser Console Tests
```javascript
// Test API
await apiClient.get('/health')

// Check auth
console.log(localStorage.getItem('access_token'))

// Run all tests
import { apiTester } from './utils/apiTester';
await apiTester.runAllTests()
```

---

## 🔧 Common Fixes

### "Cannot connect to database"
```bash
# Check PostgreSQL
pg_isready

# Restart PostgreSQL
brew services restart postgresql@14  # macOS
sudo systemctl restart postgresql    # Linux
```

### "Redis connection refused"
```bash
# Check Redis
redis-cli ping

# Restart Redis
brew services restart redis          # macOS
sudo systemctl restart redis         # Linux
```

### "Module not found"
```bash
# Backend
pip install -r requirements.txt -r requirements-integration.txt

# Frontend
npm install
```

### "API key invalid"
```bash
# Check env file
cat backend/.env | grep API_KEY

# Verify keys work
curl "https://api.openai.com/v1/models" \
  -H "Authorization: Bearer YOUR_OPENAI_KEY"
```

---

## 📊 Performance Monitoring

### Check Response Times
```bash
# Time an API call
time curl http://localhost:8000/api/v1/incidents

# Apache Bench
ab -n 100 -c 10 http://localhost:8000/health
```

### Monitor Resources
```bash
# CPU/Memory
top | grep python
top | grep node

# Database connections
psql -c "SELECT count(*) FROM pg_stat_activity;"
```

---

## 🧪 Testing Commands

### Backend Tests
```bash
# All tests
pytest

# Specific test
pytest tests/integration/test_full_integration.py

# With coverage
pytest --cov=app tests/

# Verbose
pytest -v
```

### Frontend Tests
```bash
# All tests
npm test

# Watch mode
npm test -- --watch

# Coverage
npm test -- --coverage
```

### API Testing
```bash
# Using httpie
http POST localhost:8000/api/v1/auth/login username=admin password=admin123

# Using curl
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

---

## 🚀 Deployment Commands

### Build Frontend
```bash
cd frontend
npm run build
```

### Build Backend Docker
```bash
cd backend
docker build -t aria-backend .
docker run -p 8000:8000 aria-backend
```

### Database Migration
```bash
cd backend
alembic upgrade head
```

---

## 🔗 Useful URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Redoc | http://localhost:8000/redoc |
| Metrics | http://localhost:8000/metrics |
| Health Check | http://localhost:8000/health |

---

## 📱 Phone Number Formats

```
# E.164 format (required for Twilio)
+1234567890     # USA
+91234567890    # India
+44234567890    # UK

# Invalid formats
(123) 456-7890
123-456-7890
1234567890 (no +)
```

---

## 🎨 Common React Patterns

### Loading State
```typescript
const [loading, setLoading] = useState(false);

const fetchData = async () => {
  setLoading(true);
  try {
    const data = await apiClient.get('/api/v1/data');
  } finally {
    setLoading(false);
  }
};
```

### Error Handling
```typescript
const [error, setError] = useState<string | null>(null);

try {
  await apiClient.post('/api/v1/action', data);
  setError(null);
} catch (err) {
  const handled = errorHandler.handle(err);
  setError(handled.message);
}
```

### Form Submission
```typescript
const handleSubmit = async (e: React.FormEvent) => {
  e.preventDefault();
  const [result, error] = await safeAsync(
    () => apiClient.post('/api/v1/incidents', formData)
  );
  
  if (error) return;
  navigate(`/incidents/${result.id}`);
};
```

---

## 💾 Data Formats

### Incident Object
```json
{
  "id": "INC-2026-001",
  "title": "Road Accident",
  "description": "Multiple vehicle collision",
  "incident_type": "road_accident",
  "severity": "high",
  "status": "pending",
  "latitude": 37.7749,
  "longitude": -122.4194,
  "victim_count": 3,
  "created_at": "2026-09-06T12:00:00Z"
}
```

### Location Object
```json
{
  "latitude": 37.7749,
  "longitude": -122.4194,
  "address": "Market St, San Francisco, CA"
}
```

### Notification Object
```json
{
  "type": "incident_created",
  "recipient": {
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+1234567890"
  },
  "priority": "high"
}
```

---

## 🎯 Git Commands

```bash
# Check status
git status

# Create feature branch
git checkout -b feature/new-feature

# Commit changes
git add .
git commit -m "feat: add new feature"

# Push to remote
git push origin feature/new-feature

# Pull latest
git pull origin main
```

---

**Keep this reference handy!** 📌

For complete documentation, see:
- [Complete Integration Guide](./COMPLETE-INTEGRATION-GUIDE.md)
- [Verification Checklist](./INTEGRATION-VERIFICATION-CHECKLIST.md)
- [Summary](./INTEGRATION-COMPLETE-SUMMARY.md)

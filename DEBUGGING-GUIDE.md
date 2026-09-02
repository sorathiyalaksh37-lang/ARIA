# ARIA Platform - Debugging Guide

**Quick reference for troubleshooting common issues**

---

## Quick Diagnostic Commands

```bash
# Check all services
./check_services.sh

# Test API endpoints
./test_integration.sh

# Check logs
tail -f backend/logs/aria.log

# Test database connection
psql $DATABASE_URL -c "SELECT 1"

# Test Redis connection
redis-cli ping

# Check Python dependencies
pip list | grep -E "fastapi|sqlalchemy|openai"

# Check Node dependencies
cd frontend && npm list | grep -E "react|axios|leaflet"
```

---

## Common Error Messages & Solutions

### 🔴 Backend Errors

#### "ModuleNotFoundError: No module named 'X'"

**Cause:** Missing Python dependency

**Solution:**
```bash
cd backend
pip install -r requirements.txt
# or for specific package
pip install package-name
```

#### "sqlalchemy.exc.OperationalError: could not connect to server"

**Cause:** Database not running or wrong credentials

**Solution:**
```bash
# Check PostgreSQL is running
pg_isready

# Start PostgreSQL
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql

# Verify DATABASE_URL in .env
# Format: postgresql+asyncpg://user:pass@localhost:5432/dbname
```

#### "openai.error.AuthenticationError: Invalid API key"

**Cause:** Wrong or missing OpenAI API key

**Solution:**
1. Check `.env` file: `OPENAI_API_KEY=sk-...`
2. Verify key at https://platform.openai.com/api-keys
3. Ensure no quotes around key
4. Restart backend server

#### "CORS policy: No 'Access-Control-Allow-Origin' header"

**Cause:** Frontend origin not in CORS_ORIGINS

**Solution:**
```bash
# In backend/.env
CORS_ORIGINS=["http://localhost:3000","http://localhost:8080"]

# Restart backend
```

#### "422 Unprocessable Entity"

**Cause:** Request body validation failed

**Solution:**
1. Check API documentation for required fields
2. Ensure correct data types
3. Check request example in `/docs`
4. Look at error response for specific field errors

---

### 🔵 Frontend Errors

#### "Cannot read property 'X' of undefined"

**Cause:** Accessing nested property before data loads

**Solution:**
```typescript
// Use optional chaining
const name = incident?.reporter?.name;

// Or check before access
if (incident && incident.reporter) {
  const name = incident.reporter.name;
}

// Provide default
const name = incident?.reporter?.name || 'Unknown';
```

#### "Network Error" / "ERR_CONNECTION_REFUSED"

**Cause:** Backend not running or wrong URL

**Solution:**
```bash
# Check backend is running
curl http://localhost:8000/health

# Check REACT_APP_API_BASE_URL in frontend/.env
# Should be: http://localhost:8000/api/v1

# Restart backend if needed
cd backend && uvicorn app.main:app --reload
```

#### "401 Unauthorized" on all requests

**Cause:** Token expired or missing

**Solution:**
```typescript
// Clear storage and re-login
localStorage.clear();
window.location.href = '/login';

// Check token interceptor is configured
// See frontend/src/api/client.ts
```

#### "Module not found: Can't resolve 'X'"

**Cause:** Missing npm package

**Solution:**
```bash
cd frontend
npm install
# or for specific package
npm install package-name
```

---

### 🟡 Integration Issues

#### SMS not sending (Twilio)

**Symptoms:** No error but SMS not received

**Diagnosis:**
```bash
# Check Twilio credentials
echo $TWILIO_ACCOUNT_SID  # Should start with AC
echo $TWILIO_AUTH_TOKEN
echo $TWILIO_PHONE_NUMBER  # Should start with +

# Test manually
curl -X POST https://api.twilio.com/2010-04-01/Accounts/$TWILIO_ACCOUNT_SID/Messages.json \
  --data-urlencode "Body=Test" \
  --data-urlencode "From=$TWILIO_PHONE_NUMBER" \
  --data-urlencode "To=+1234567890" \
  -u "$TWILIO_ACCOUNT_SID:$TWILIO_AUTH_TOKEN"
```

**Solutions:**
1. Trial accounts can only send to verified numbers
2. Check phone number format (+1234567890)
3. Verify from number is purchased in Twilio console
4. Check Twilio activity logs for details

#### Google Maps not loading

**Symptoms:** Map shows gray background

**Diagnosis:**
```bash
# Test API key
curl "https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway&key=$GOOGLE_MAPS_API_KEY"

# Check console for specific error
# Open browser DevTools → Console
```

**Solutions:**
1. Verify API key in backend/.env
2. Enable required APIs in Google Cloud Console:
   - Geocoding API
   - Directions API
   - Distance Matrix API
   - Places API
3. Check API key restrictions aren't blocking requests
4. Wait 5-10 minutes for new keys to activate

#### WebSocket disconnecting repeatedly

**Symptoms:** "WebSocket disconnected" messages in console

**Diagnosis:**
```bash
# Check WebSocket endpoint
curl -i -N -H "Connection: Upgrade" \
  -H "Upgrade: websocket" \
  -H "Host: localhost:8000" \
  -H "Origin: http://localhost:3000" \
  http://localhost:8000/api/v1/ws

# Check logs
tail -f backend/logs/aria.log | grep -i websocket
```

**Solutions:**
1. Check token is valid
2. Verify WS_URL in frontend/.env
3. Check reverse proxy (nginx) WebSocket configuration
4. Increase timeout settings
5. Check firewall rules

---

## Step-by-Step Debugging Procedures

### Procedure 1: Debug Backend 500 Error

1. **Check the logs:**
   ```bash
   tail -n 100 backend/logs/aria.log
   ```

2. **Enable debug mode:**
   ```bash
   # In backend/.env
   DEBUG=True
   LOG_LEVEL=DEBUG
   ```

3. **Restart backend:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

4. **Reproduce the error** and check logs for stack trace

5. **Common causes:**
   - Database query error → Check SQL syntax
   - External API failure → Check API keys and quotas
   - Missing data → Check data validation
   - Import error → Check dependencies installed

### Procedure 2: Debug Frontend API Call Failure

1. **Open browser DevTools** (F12)

2. **Go to Network tab** and reproduce issue

3. **Click failed request** to see:
   - Request URL → Is it correct?
   - Request Headers → Is Authorization header present?
   - Request Payload → Is data formatted correctly?
   - Response → What error did server return?

4. **Check console** for JavaScript errors

5. **Test same request with cURL:**
   ```bash
   curl -X POST http://localhost:8000/api/v1/endpoint \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer $TOKEN" \
     -d '{"field":"value"}'
   ```

6. **Compare** cURL result with frontend request

### Procedure 3: Debug ML Model Issues

1. **Check model files exist:**
   ```bash
   ls -la models/
   # Should see:
   # - hotspot_predictor.pkl
   # - demand_forecaster.pkl
   # - severity_predictor.pkl
   ```

2. **Test model loading:**
   ```python
   import pickle
   with open('models/hotspot_predictor.pkl', 'rb') as f:
       model = pickle.load(f)
   print(type(model))  # Should show sklearn model
   ```

3. **Check model predictions:**
   ```python
   import numpy as np
   features = np.array([[37.77, -122.42, 18, 3, 0, 1, 0.5]])
   prediction = model.predict(features)
   print(prediction)  # Should return numeric value
   ```

4. **Fallback to rule-based:**
   ```bash
   # In backend/.env
   ENABLE_ML_PREDICTIONS=False
   ```

### Procedure 4: Debug Database Issues

1. **Test connection:**
   ```bash
   psql $DATABASE_URL -c "SELECT version()"
   ```

2. **Check migrations:**
   ```bash
   cd backend
   alembic current  # Show current migration
   alembic history  # Show all migrations
   alembic upgrade head  # Apply all migrations
   ```

3. **Check tables exist:**
   ```sql
   psql $DATABASE_URL -c "\dt"
   ```

4. **Check table structure:**
   ```sql
   psql $DATABASE_URL -c "\d incidents"
   ```

5. **Test query:**
   ```sql
   psql $DATABASE_URL -c "SELECT COUNT(*) FROM incidents"
   ```

---

## Performance Debugging

### Slow API Response

**Tools:**
```bash
# Time a request
time curl http://localhost:8000/api/v1/incidents

# Profile with Python
python -m cProfile -s cumulative backend/app/main.py

# Check database query time
# Add to code:
import time
start = time.time()
result = await db.execute(query)
print(f"Query took: {time.time() - start}s")
```

**Common causes:**
- N+1 query problem → Use eager loading
- Missing database index → Add index
- Large data transfer → Add pagination
- External API timeout → Increase timeout or add caching

### High Memory Usage

**Check:**
```bash
# Backend memory
ps aux | grep uvicorn

# Database connections
psql $DATABASE_URL -c "SELECT count(*) FROM pg_stat_activity"
```

**Solutions:**
- Close database connections properly
- Limit query result sizes
- Use streaming for large datasets
- Clear caches periodically

### Frontend Performance Issues

**Tools:**
- Chrome DevTools → Performance tab
- React DevTools → Profiler
- Lighthouse audit

**Common issues:**
- Too many re-renders → Use React.memo, useMemo
- Large bundle size → Code splitting, lazy loading
- Memory leaks → Clean up useEffect subscriptions
- Expensive computations → Move to Web Worker

---

## Debugging Checklist

### Before Starting Development

- [ ] Backend runs: `uvicorn app.main:app --reload`
- [ ] Frontend runs: `npm start`
- [ ] Database connected: `psql $DATABASE_URL -c "SELECT 1"`
- [ ] Redis connected: `redis-cli ping`
- [ ] API health check passes: `curl localhost:8000/health`
- [ ] Can login to frontend
- [ ] WebSocket connects

### Before Deploying

- [ ] All tests pass: `./test_integration.sh`
- [ ] No errors in logs
- [ ] Database migrations applied
- [ ] Environment variables set correctly
- [ ] External API keys validated
- [ ] CORS configured for production domain
- [ ] Rate limiting configured
- [ ] Monitoring set up

### When Investigating Bug

- [ ] Can reproduce consistently?
- [ ] What changed recently?
- [ ] Check error logs
- [ ] Check external service status
- [ ] Test in isolation
- [ ] Verify environment configuration
- [ ] Check recent commits
- [ ] Test with fresh database

---

## Useful Commands Reference

### Backend

```bash
# Start backend
cd backend
uvicorn app.main:app --reload --port 8000

# Run with specific workers
uvicorn app.main:app --workers 4

# Shell with app context
python
>>> from app.core.database import get_db
>>> from app.models.incident import Incident

# Run migrations
alembic upgrade head
alembic downgrade -1
alembic revision --autogenerate -m "message"

# Check routes
python -c "from app.main import app; print([r.path for r in app.routes])"
```

### Frontend

```bash
# Start frontend
cd frontend
npm start

# Build for production
npm run build

# Run tests
npm test

# Check bundle size
npm run build && ls -lh build/static/js/

# Clear cache
rm -rf node_modules package-lock.json
npm install
```

### Database

```bash
# Connect to database
psql $DATABASE_URL

# Export database
pg_dump $DATABASE_URL > backup.sql

# Import database
psql $DATABASE_URL < backup.sql

# Reset database
psql $DATABASE_URL -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
alembic upgrade head
```

### Testing

```bash
# Integration tests
python backend/tests/integration/test_full_integration.py

# Quick bash tests
./test_integration.sh

# WebSocket tests
python backend/tests/integration/test_websocket.py

# Frontend tests
cd frontend && npm test

# Load testing (if you have ab installed)
ab -n 1000 -c 10 http://localhost:8000/api/v1/incidents
```

---

## Getting More Help

### Logs to Check
1. `backend/logs/aria.log` - Application logs
2. Browser console (F12) - Frontend errors
3. Network tab - API requests/responses
4. PostgreSQL logs - Database errors
5. Redis logs - Cache issues

### Information to Collect
When reporting an issue:
- Error message (full stack trace)
- Steps to reproduce
- Environment (dev/staging/prod)
- Recent changes
- Relevant logs
- API request/response if applicable
- Browser and OS version (for frontend issues)

### External Service Status Pages
- OpenAI: https://status.openai.com/
- Google Cloud: https://status.cloud.google.com/
- Twilio: https://status.twilio.com/
- SendGrid: https://status.sendgrid.com/
- OpenWeatherMap: https://openweathermap.statuspage.io/

---

**Last Updated:** 2024  
**Version:** 1.0.0

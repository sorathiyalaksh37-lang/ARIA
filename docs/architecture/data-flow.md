# ARIA Data Flow Architecture

## Overview

This document describes the complete data flow through the ARIA emergency response platform, from incident creation to resource dispatch.

---

## End-to-End Incident Flow

### Complete Workflow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ARIA INCIDENT WORKFLOW                               │
└─────────────────────────────────────────────────────────────────────────────┘

  Emergency Call/Web Form
         │
         ▼
  ┌──────────────────┐
  │  1. INCIDENT     │  User creates incident via:
  │     CREATION     │  - Web form (dispatcher)
  └────────┬─────────┘  - API call
           │            - Future: Voice (Whisper transcription)
           │
           ▼
  ┌──────────────────┐
  │  2. DATABASE     │  Store incident in PostgreSQL
  │     STORAGE      │  - Generate incident ID
  └────────┬─────────┘  - Set status = PENDING
           │            - Store location (PostGIS POINT)
           │            - Audit trail created
           │
           ▼
  ┌──────────────────┐
  │  3. WEBSOCKET    │  Broadcast incident.created event
  │     BROADCAST    │  - All connected clients notified
  └────────┬─────────┘  - Dashboard updates in real-time
           │
           │
           ▼
  ┌─────────────────────────────────────────────────────────────────────────┐
  │                  4. LANGGRAPH AGENT ORCHESTRATOR                        │
  │                                                                         │
  │   Status: PROCESSING                                                    │
  │                                                                         │
  │   ┌──────────────────────────────────────────────────────────────┐    │
  │   │ Agent 1: TRIAGE AGENT                                        │    │
  │   ├──────────────────────────────────────────────────────────────┤    │
  │   │ Input:  description, location, time                          │    │
  │   │ Action: ML prediction (Random Forest)                        │    │
  │   │ Output: severity = CRITICAL/MODERATE/MINOR                   │    │
  │   │         confidence score                                     │    │
  │   └────────────────────────┬─────────────────────────────────────┘    │
  │                            │                                            │
  │                            ▼                                            │
  │   ┌──────────────────────────────────────────────────────────────┐    │
  │   │ Agent 2: HOSPITAL AGENT                                      │    │
  │   ├──────────────────────────────────────────────────────────────┤    │
  │   │ Input:  incident location, severity                          │    │
  │   │ Query:  PostGIS spatial search (10km radius)                 │    │
  │   │         SELECT * FROM hospitals                              │    │
  │   │         WHERE ST_DWithin(location, incident_loc, 10000)      │    │
  │   │ Action: ML ranking (LightGBM)                                │    │
  │   │         - Distance                                           │    │
  │   │         - Specialization match                               │    │
  │   │         - Bed availability                                   │    │
  │   │         - Historical performance                             │    │
  │   │ Output: ranked_hospitals = [hosp1, hosp2, ...]              │    │
  │   │         selected_hospital = top choice                       │    │
  │   └────────────────────────┬─────────────────────────────────────┘    │
  │                            │                                            │
  │                            ▼                                            │
  │   ┌──────────────────────────────────────────────────────────────┐    │
  │   │ Agent 3: AMBULANCE AGENT                                     │    │
  │   ├──────────────────────────────────────────────────────────────┤    │
  │   │ Input:  incident location, severity, selected hospital       │    │
  │   │ Query:  Find available ambulances                            │    │
  │   │         SELECT * FROM ambulances                             │    │
  │   │         WHERE status = 'available'                           │    │
  │   │         AND ST_DWithin(location, incident_loc, 50000)        │    │
  │   │ Action: Calculate distance to each ambulance                 │    │
  │   │         ML ETA prediction (XGBoost)                          │    │
  │   │ Output: selected_ambulance                                   │    │
  │   │         estimated_pickup_eta                                 │    │
  │   │         estimated_hospital_eta                               │    │
  │   └────────────────────────┬─────────────────────────────────────┘    │
  │                            │                                            │
  │                            ▼                                            │
  │   ┌──────────────────────────────────────────────────────────────┐    │
  │   │ Agent 4: BLOOD AGENT (Conditional)                           │    │
  │   ├──────────────────────────────────────────────────────────────┤    │
  │   │ Condition: IF blood transfusion needed                       │    │
  │   │ Input:    blood_type, quantity                               │    │
  │   │ Query:    Find nearby blood banks with stock                 │    │
  │   │ Output:   selected_blood_bank, reserved_units                │    │
  │   └────────────────────────┬─────────────────────────────────────┘    │
  │                            │                                            │
  │                            ▼                                            │
  │   ┌──────────────────────────────────────────────────────────────┐    │
  │   │ Agent 5: ROUTE AGENT                                         │    │
  │   ├──────────────────────────────────────────────────────────────┤    │
  │   │ Input:  ambulance_location → incident → hospital             │    │
  │   │ API:    Google Maps Directions API                           │    │
  │   │         - With real-time traffic                             │    │
  │   │         - Optimized for emergency vehicles                   │    │
  │   │ Output: route_polyline, distance, duration                   │    │
  │   │         turn_by_turn_directions                              │    │
  │   └────────────────────────┬─────────────────────────────────────┘    │
  │                            │                                            │
  │                            ▼                                            │
  │   ┌──────────────────────────────────────────────────────────────┐    │
  │   │ Agent 6: RAG AGENT (Future Enhancement)                      │    │
  │   ├──────────────────────────────────────────────────────────────┤    │
  │   │ Input:  incident_type, severity                              │    │
  │   │ Action: Query vector database for medical protocols          │    │
  │   │ Output: relevant_protocols, treatment_guidelines             │    │
  │   └────────────────────────┬─────────────────────────────────────┘    │
  │                            │                                            │
  │                            ▼                                            │
  │   ┌──────────────────────────────────────────────────────────────┐    │
  │   │ Agent 7: PLAN AGENT                                          │    │
  │   ├──────────────────────────────────────────────────────────────┤    │
  │   │ Input:  All data from previous agents                        │    │
  │   │ Action: Generate comprehensive response plan                 │    │
  │   │ Output: ResponsePlan {                                       │    │
  │   │           incident_summary                                   │    │
  │   │           severity_assessment                                │    │
  │   │           hospital: {name, address, eta}                     │    │
  │   │           ambulance: {number, type, eta}                     │    │
  │   │           route: {distance, duration, polyline}              │    │
  │   │           blood: {bank, type, units} (if needed)             │    │
  │   │           total_response_time                                │    │
  │   │           recommendations                                    │    │
  │   │         }                                                     │    │
  │   └────────────────────────┬─────────────────────────────────────┘    │
  │                            │                                            │
  │                            ▼                                            │
  │   ┌──────────────────────────────────────────────────────────────┐    │
  │   │ Agent 8: COORDINATOR AGENT                                   │    │
  │   ├──────────────────────────────────────────────────────────────┤    │
  │   │ Action: HUMAN-IN-THE-LOOP                                    │    │
  │   │         - Present plan to coordinator                        │    │
  │   │         - Wait for approval/rejection                        │    │
  │   │         - Handle modifications                               │    │
  │   │                                                              │    │
  │   │ Decision: APPROVE / REJECT / MODIFY                          │    │
  │   │                                                              │    │
  │   │ If REJECTED: Loop back to Plan Agent with feedback           │    │
  │   │ If MODIFIED: Loop back with specific changes                 │    │
  │   │ If APPROVED: Continue to next agent                          │    │
  │   └────────────────────────┬─────────────────────────────────────┘    │
  │                            │                                            │
  │                            ▼ (APPROVED)                                │
  │   ┌──────────────────────────────────────────────────────────────┐    │
  │   │ Agent 9: COMMUNICATION AGENT                                 │    │
  │   ├──────────────────────────────────────────────────────────────┤    │
  │   │ Action: Send notifications to all stakeholders               │    │
  │   │                                                              │    │
  │   │ Hospital:                                                    │    │
  │   │   → SMS: "Emergency incoming: CRITICAL, ETA 8 min"          │    │
  │   │   → Email: Full incident details                            │    │
  │   │                                                              │    │
  │   │ Ambulance:                                                   │    │
  │   │   → SMS: "Dispatch to [address], Critical patient"          │    │
  │   │   → Route details                                           │    │
  │   │                                                              │    │
  │   │ Reporter (Future):                                          │    │
  │   │   → SMS: "Help is on the way, ETA 5 minutes"                │    │
  │   └────────────────────────┬─────────────────────────────────────┘    │
  │                            │                                            │
  │                            ▼                                            │
  │   ┌──────────────────────────────────────────────────────────────┐    │
  │   │ Agent 10: MONITORING AGENT                                   │    │
  │   ├──────────────────────────────────────────────────────────────┤    │
  │   │ Action: Collect workflow metrics                             │    │
  │   │         - Total execution time                               │    │
  │   │         - Agent execution times                              │    │
  │   │         - Success/failure status                             │    │
  │   │         - System health check                                │    │
  │   │ Output: metrics stored for Prometheus                        │    │
  │   └──────────────────────────────────────────────────────────────┘    │
  │                                                                         │
  └─────────────────────────────────────────────────────────────────────────┘
           │
           │ Status: APPROVED
           │
           ▼
  ┌──────────────────┐
  │  5. DATABASE     │  Update incident status = APPROVED
  │     UPDATE       │  - Link hospital, ambulance
  └────────┬─────────┘  - Store response plan
           │            - Update history
           │
           ▼
  ┌──────────────────┐
  │  6. WEBSOCKET    │  Broadcast incident.approved event
  │     BROADCAST    │  - Plan generated
  └────────┬─────────┘  - Resources allocated
           │
           │
           ▼
  ┌──────────────────┐
  │  7. DISPATCH     │  POST /incidents/{id}/dispatch
  │     EXECUTION    │  
  └────────┬─────────┘  Status: DISPATCHED
           │
           ├─────────────────┐
           │                 │
           ▼                 ▼
  ┌──────────────┐   ┌──────────────┐
  │  Update      │   │  Update      │
  │  Ambulance   │   │  Hospital    │
  │  Status =    │   │  Capacity    │
  │  DISPATCHED  │   │  (Reserve    │
  └──────┬───────┘   │   bed)       │
         │           └──────┬───────┘
         │                  │
         └────────┬─────────┘
                  │
                  ▼
  ┌──────────────────┐
  │  8. REAL-TIME    │  Continuous updates via WebSocket
  │     TRACKING     │  
  └────────┬─────────┘  - Ambulance GPS location
           │            - Incident status changes
           │            - ETA updates
           │
           ▼
  ┌──────────────────┐
  │  9. COMPLETION   │  Manual or automatic
  │                  │  Status: COMPLETED
  └────────┬─────────┘  - Record outcome
           │            - Release resources
           │            - Generate report
           │
           ▼
  ┌──────────────────┐
  │  10. ANALYTICS   │  Store for ML training
  │      STORAGE     │  - Response time
  └──────────────────┘  - Outcome
                        - Resource utilization
```

---

## Detailed Data Flows

### 1. Authentication Flow

```
Client                          Backend                     Database
  │                               │                            │
  │  POST /auth/login             │                            │
  │  {username, password}         │                            │
  ├──────────────────────────────>│                            │
  │                               │                            │
  │                               │  Query user                │
  │                               │  WHERE username = ?        │
  │                               ├───────────────────────────>│
  │                               │                            │
  │                               │<───────────────────────────┤
  │                               │  User record               │
  │                               │                            │
  │                               │  Verify password           │
  │                               │  (bcrypt.checkpw)          │
  │                               │                            │
  │                               │  Generate JWT tokens       │
  │                               │  - access_token (30m)      │
  │                               │  - refresh_token (7d)      │
  │                               │                            │
  │<──────────────────────────────┤                            │
  │  {access_token, refresh_token,│                            │
  │   user_info}                  │                            │
  │                               │                            │
  │  Store tokens in localStorage │                            │
  │                               │                            │
  │  GET /incidents               │                            │
  │  Authorization: Bearer token  │                            │
  ├──────────────────────────────>│                            │
  │                               │                            │
  │                               │  Decode & verify JWT       │
  │                               │  Check expiry              │
  │                               │  Extract user_id           │
  │                               │                            │
  │                               │  Check permissions         │
  │                               │  (RBAC)                    │
  │                               │                            │
  │                               │  Query incidents           │
  │                               ├───────────────────────────>│
  │                               │<───────────────────────────┤
  │                               │                            │
  │<──────────────────────────────┤                            │
  │  {incidents: [...]}           │                            │
  │                               │                            │
```

---

### 2. Real-Time WebSocket Flow

```
Client                    Backend                   Redis                Database
  │                         │                        │                     │
  │  WS /ws?token=JWT       │                        │                     │
  │  &channels=incidents    │                        │                     │
  ├────────────────────────>│                        │                     │
  │                         │                        │                     │
  │                         │  Verify JWT            │                     │
  │                         │                        │                     │
  │                         │  Store connection      │                     │
  │                         ├───────────────────────>│                     │
  │                         │  conn_id → user_id     │                     │
  │                         │                        │                     │
  │<────────────────────────┤                        │                     │
  │  {type: "connected"}    │                        │                     │
  │                         │                        │                     │
  │  Send heartbeat         │                        │                     │
  │  every 30s              │                        │                     │
  ├────────────────────────>│                        │                     │
  │<────────────────────────┤                        │                     │
  │  {type: "pong"}         │                        │                     │
  │                         │                        │                     │
  │                         │                        │                     │
  │  [Event occurs: New incident created]            │                     │
  │                         │                        │                     │
  │                         │  Store incident        │                     │
  │                         ├───────────────────────────────────────────> │
  │                         │                        │                     │
  │                         │  Broadcast event       │                     │
  │                         ├───────────────────────>│                     │
  │                         │  PUBLISH incidents     │                     │
  │                         │  {type: "incident.     │                     │
  │                         │   created", data: {}}  │                     │
  │                         │                        │                     │
  │                         │  Get subscribers       │                     │
  │                         │<───────────────────────┤                     │
  │                         │  [conn1, conn2, ...]   │                     │
  │                         │                        │                     │
  │<────────────────────────┤                        │                     │
  │  {type: "incident.      │                        │                     │
  │   created",             │                        │                     │
  │   data: {...}}          │                        │                     │
  │                         │                        │                     │
  │  Update UI in real-time │                        │                     │
  │                         │                        │                     │
```

---

### 3. ML Prediction Flow

```
API Request               ML Service              Model Files          Database
  │                         │                        │                   │
  │  POST /hospitals/rank   │                        │                   │
  │  {incident_data}        │                        │                   │
  ├────────────────────────>│                        │                   │
  │                         │                        │                   │
  │                         │  Load model (cached)   │                   │
  │                         ├───────────────────────>│                   │
  │                         │<───────────────────────┤                   │
  │                         │  LightGBM model        │                   │
  │                         │                        │                   │
  │                         │  Query hospital data   │                   │
  │                         ├───────────────────────────────────────────>│
  │                         │<───────────────────────────────────────────┤
  │                         │  Hospital features     │                   │
  │                         │                        │                   │
  │                         │  Preprocess features   │                   │
  │                         │  - Normalize distance  │                   │
  │                         │  - Encode categories   │                   │
  │                         │  - Scale values        │                   │
  │                         │                        │                   │
  │                         │  Model.predict()       │                   │
  │                         │                        │                   │
  │                         │  Post-process results  │                   │
  │                         │  - Sort by score       │                   │
  │                         │  - Apply filters       │                   │
  │                         │  - Format output       │                   │
  │                         │                        │                   │
  │<────────────────────────┤                        │                   │
  │  {ranked_hospitals:     │                        │                   │
  │   [...]}                │                        │                   │
  │                         │                        │                   │
```

---

### 4. External API Integration Flow

**Google Maps Routing:**

```
Route Agent          Maps Service       Google Maps API      Fallback (OSRM)
  │                      │                    │                     │
  │  Get route           │                    │                     │
  │  A → B               │                    │                     │
  ├─────────────────────>│                    │                     │
  │                      │                    │                     │
  │                      │  API Request       │                     │
  │                      ├───────────────────>│                     │
  │                      │  directions API    │                     │
  │                      │  with traffic      │                     │
  │                      │                    │                     │
  │                      │<───────────────────┤                     │
  │                      │  Route data        │                     │
  │                      │                    │                     │
  │<─────────────────────┤                    │                     │
  │  {polyline, distance,│                    │                     │
  │   duration}          │                    │                     │
  │                      │                    │                     │
  │                      │                    │                     │
  │  [If Google fails]   │                    │                     │
  │                      │                    │                     │
  │                      │  Retry with OSRM   │                     │
  │                      ├────────────────────────────────────────> │
  │                      │                    │                     │
  │                      │<────────────────────────────────────────┤
  │                      │  Route data        │                     │
  │                      │                    │                     │
  │<─────────────────────┤                    │                     │
  │  {route_from_osrm}   │                    │                     │
  │                      │                    │                     │
```

**Notification Flow:**

```
Communication     Notification        Twilio         SendGrid
     Agent          Service            API            API
       │               │                 │              │
       │  Send         │                 │              │
       │  notifications│                 │              │
       ├──────────────>│                 │              │
       │               │                 │              │
       │               │  Check priority │              │
       │               │  (Critical →    │              │
       │               │   SMS first)    │              │
       │               │                 │              │
       │               │  Send SMS       │              │
       │               ├────────────────>│              │
       │               │  hospital phone │              │
       │               │                 │              │
       │               │<────────────────┤              │
       │               │  message_sid    │              │
       │               │                 │              │
       │               │  Send Email     │              │
       │               ├─────────────────────────────> │
       │               │  HTML template  │              │
       │               │                 │              │
       │               │<─────────────────────────────┤
       │               │  message_id     │              │
       │               │                 │              │
       │<──────────────┤                 │              │
       │  {success,    │                 │              │
       │   message_ids}│                 │              │
       │               │                 │              │
```

---

### 5. State Management Flow (LangGraph)

```
┌─────────────────────────────────────────────────────────────┐
│                    AGENT STATE                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  incident: IncidentInfo {                                   │
│    id, description, location, severity, type                │
│  }                                                          │
│                                                             │
│  analysis: AnalysisResult {                                 │
│    severity: "CRITICAL"                                     │
│    confidence: 0.98                                         │
│    requires_blood: true                                     │
│  }                                                          │
│                                                             │
│  hospitals: List[Hospital] [                                │
│    {id: 1, name: "City Hospital", distance: 2.3km},        │
│    {id: 2, name: "General Hospital", distance: 3.1km}      │
│  ]                                                          │
│                                                             │
│  selected_hospital: Hospital {                              │
│    id: 1, name: "City Hospital", ...                        │
│  }                                                          │
│                                                             │
│  ambulances: List[Ambulance] [                              │
│    {id: "AMB-001", type: "ADVANCED", distance: 1.2km},     │
│  ]                                                          │
│                                                             │
│  selected_ambulance: Ambulance {                            │
│    id: "AMB-001", ...                                       │
│  }                                                          │
│                                                             │
│  route: RouteInfo {                                         │
│    polyline: "encoded_string",                              │
│    distance: 5.5km,                                         │
│    duration: 8 minutes                                      │
│  }                                                          │
│                                                             │
│  blood_bank: BloodBank {  # Optional                        │
│    id: 3, name: "Central Blood Bank"                        │
│  }                                                          │
│                                                             │
│  response_plan: ResponsePlan {                              │
│    summary: "...",                                          │
│    total_time: 15 minutes,                                  │
│    recommendations: [...]                                   │
│  }                                                          │
│                                                             │
│  approval_status: "APPROVED" | "PENDING" | "REJECTED"       │
│                                                             │
│  notifications_sent: {                                      │
│    hospital: {sms: true, email: true},                      │
│    ambulance: {sms: true}                                   │
│  }                                                          │
│                                                             │
│  metrics: {                                                 │
│    total_time: 2.3s,                                        │
│    agent_times: {...}                                       │
│  }                                                          │
│                                                             │
│  errors: []                                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘

Each agent:
1. Receives current state
2. Performs its task
3. Updates relevant state fields
4. Returns modified state
5. State flows to next agent

State is immutable (functional approach)
Agents create new state copies with updates
```

---

## Database Query Patterns

### Spatial Queries (PostGIS)

```sql
-- Find nearby hospitals
SELECT 
    id, name, address,
    ST_Distance(location, ST_SetSRID(ST_MakePoint(?, ?), 4326)) as distance
FROM hospitals
WHERE 
    ST_DWithin(
        location, 
        ST_SetSRID(ST_MakePoint(?, ?), 4326),
        10000  -- 10km radius in meters
    )
    AND is_active = true
    AND available_beds > 0
ORDER BY distance
LIMIT 10;
```

```sql
-- Find ambulances in area
SELECT 
    id, vehicle_number, ambulance_type,
    ST_AsGeoJSON(location) as location_geojson,
    ST_Distance(location, incident_location) as distance
FROM ambulances
WHERE 
    status = 'available'
    AND ST_DWithin(location, incident_location, 50000)
ORDER BY distance;
```

### Incident History Tracking

```sql
-- Insert history entry
INSERT INTO incident_history (
    incident_id, status, notes, 
    changed_by_id, metadata, created_at
) VALUES (?, ?, ?, ?, ?, NOW());

-- Query incident timeline
SELECT 
    ih.status,
    ih.notes,
    ih.created_at,
    u.username as changed_by
FROM incident_history ih
JOIN users u ON ih.changed_by_id = u.id
WHERE ih.incident_id = ?
ORDER BY ih.created_at DESC;
```

---

## Caching Strategy

### Redis Cache Patterns

```
Cache Keys:
├── session:{user_id} → User session data (30 min TTL)
├── ws:connections → Set of active WebSocket connections
├── incident:{id} → Cached incident details (5 min TTL)
├── hospitals:nearby:{lat},{lon} → Nearby hospitals (10 min TTL)
├── ambulances:available → List of available ambulances (1 min TTL)
├── ml:prediction:{hash} → ML prediction results (1 hour TTL)
└── rate_limit:{user_id}:{endpoint} → Rate limit counters (1 min TTL)

Cache Invalidation:
- On incident update → Delete incident:{id}
- On ambulance status change → Delete ambulances:available
- On hospital update → Delete hospitals:nearby:*
```

---

## Performance Metrics

### Typical Latencies

```
Operation                          Latency        Target
─────────────────────────────────────────────────────────
Database query (indexed)           5-10ms         <50ms
Database query (spatial)           20-50ms        <100ms
ML model prediction                50-100ms       <200ms
Google Maps API call               200-500ms      <1s
SMS send (Twilio)                  500-1000ms     <2s
Email send (SendGrid)              100-300ms      <500ms
WebSocket broadcast                5-10ms         <20ms
Full agent workflow                2-5s           <10s
```

### Throughput Targets

```
Metric                             Current        Target
─────────────────────────────────────────────────────────
API requests/second                100            1000
Concurrent WebSocket connections   500            5000
Incidents processed/hour           50             500
Database connections (pool)        20             100
```

---

## Error Handling & Retry Logic

### Agent Retry Flow

```
Agent Execution
    │
    ├─ Try 1
    │   └─ Fail → Wait 1s
    │
    ├─ Try 2  
    │   └─ Fail → Wait 2s
    │
    ├─ Try 3
    │   └─ Fail → Return error state
    │
    └─ Success → Continue

Each agent has max 3 retries
Exponential backoff: 2^(retry-1) seconds
Errors logged and added to state.errors[]
```

### External API Fallbacks

```
Primary Service Fails
    │
    ├─ Google Maps → OSRM → Nominatim
    ├─ OpenAI GPT-4 → GPT-3.5-turbo → Rule-based
    └─ Twilio → SendGrid (email as fallback)
```

---

## Conclusion

The ARIA data flow architecture ensures:
- **Reliability:** Multiple fallbacks and retry logic
- **Performance:** Optimized queries and caching
- **Scalability:** Stateless design, horizontal scaling
- **Observability:** Comprehensive metrics and logging
- **Real-time:** WebSocket for instant updates
- **Intelligence:** ML and AI throughout the pipeline

---

**Document Version:** 1.0  
**Last Updated:** 2026-09-06  
**Maintained By:** ARIA Development Team

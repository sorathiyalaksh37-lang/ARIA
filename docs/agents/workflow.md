# ARIA LangGraph Agent System Documentation

## Overview

ARIA employs a sophisticated multi-agent system built with LangGraph to orchestrate emergency response coordination. The system uses 14 specialized agents working collaboratively through a state machine workflow with human-in-the-loop approval.

**Framework:** LangGraph 0.0.20  
**Agents:** 14 specialized agents  
**Workflow:** StateGraph with conditional routing  
**Execution:** Async/await pattern  
**Human-in-the-Loop:** Coordinator Agent approval

---

## Agent Architecture

### System Design

```
┌─────────────────────────────────────────────────────────────────┐
│              LANGGRAPH AGENT ORCHESTRATOR                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  START (Incident Created)                                       │
│    │                                                            │
│    ▼                                                            │
│  ┌─────────────────┐                                           │
│  │ Triage Agent    │  ML Severity Classification               │
│  │ (Agent 1)       │  → Sets: severity, confidence             │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ Hospital Agent  │  Spatial Search + ML Ranking              │
│  │ (Agent 2)       │  → Sets: ranked_hospitals, selected       │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ Ambulance Agent │  Find Nearest + ETA                       │
│  │ (Agent 3)       │  → Sets: ambulance, pickup_eta            │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ Blood Agent     │  Conditional (if blood_required)          │
│  │ (Agent 4)       │  → Sets: blood_bank, units_reserved       │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ Route Agent     │  Optimal Route Calculation                │
│  │ (Agent 5)       │  → Sets: route, distance, duration        │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ RAG Agent       │  Medical Protocol Retrieval               │
│  │ (Agent 6)       │  → Sets: protocols, guidelines            │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ Plan Agent      │  Generate Response Plan                   │
│  │ (Agent 7)       │  → Sets: response_plan                    │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ Coordinator     │  ◄─── HUMAN-IN-THE-LOOP                   │
│  │ Agent (Agent 8) │       Approval Required                   │
│  └────────┬────────┘                                           │
│           │                                                     │
│      ┌────┴────┐                                               │
│   APPROVE   REJECT                                             │
│      │         └──► (Modify & Loop Back)                       │
│      │                                                          │
│      ▼                                                          │
│  ┌─────────────────┐                                           │
│  │ Communication   │  Multi-Channel Notifications              │
│  │ Agent (Agent 9) │  → Sends: SMS, Email                      │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│  ┌─────────────────┐                                           │
│  │ Monitoring      │  Metrics & Health                         │
│  │ Agent (Agent 10)│  → Logs: execution_time, status           │
│  └────────┬────────┘                                           │
│           │                                                     │
│           ▼                                                     │
│         END (Plan Approved & Dispatched)                        │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Agent Descriptions

### 1. Triage Agent

**Purpose:** Classify incident severity using ML model

**Input:**
- Incident description
- Location
- Incident type
- Timestamp

**Processing:**
1. Preprocess text (lowercase, remove special chars)
2. Call ML triage classifier
3. Validate confidence threshold (>0.7)
4. Set severity level

**Output:**
```python
{
    "severity": "CRITICAL",  # LOW, MODERATE, CRITICAL
    "confidence": 0.98,
    "requires_blood": True,
    "estimated_victims": 3
}
```

**Failure Handling:**
- If ML fails → Rule-based classification
- If confidence <0.7 → Default to MODERATE

---

### 2. Hospital Agent

**Purpose:** Find and rank suitable hospitals

**Input:**
- Incident location (lat, lon)
- Severity level
- Required specialties
- Distance radius (default: 50km)

**Processing:**
1. PostGIS spatial query (ST_DWithin)
2. Filter by capacity and services
3. ML ranking with 27 features
4. Select top 10 hospitals
5. Choose best match

**Output:**
```python
{
    "ranked_hospitals": [
        {"id": "hosp-001", "name": "City Hospital", "distance_km": 2.3, "score": 0.95},
        ...
    ],
    "selected_hospital": {
        "id": "hosp-001",
        "name": "City Hospital",
        "address": "123 Main St",
        "available_beds": 45,
        "has_icu": True
    }
}
```

**Failure Handling:**
- No hospitals found → Expand radius to 100km
- Still none → Return nearest hospital regardless of capacity

---

### 3. Ambulance Agent

**Purpose:** Dispatch nearest available ambulance

**Input:**
- Incident location
- Severity level
- Hospital location
- Required ambulance type

**Processing:**
1. Query available ambulances (status='AVAILABLE')
2. Calculate distance to each
3. Filter by type (CRITICAL → CRITICAL_CARE)
4. Predict ETA using ML model
5. Select nearest with shortest ETA

**Output:**
```python
{
    "selected_ambulance": {
        "id": "amb-001",
        "vehicle_number": "MH-01-AB-1234",
        "type": "CRITICAL_CARE",
        "driver_name": "John Doe",
        "driver_phone": "+91-9876543210"
    },
    "pickup_eta": 5.2,  # minutes
    "hospital_eta": 12.8,  # minutes
    "total_response_time": 18.0  # minutes
}
```

**Failure Handling:**
- No ambulances available → Notify dispatcher
- ETA too high (>30 min) → Request air ambulance

---

### 4. Blood Agent (Conditional)

**Purpose:** Reserve blood units if transfusion needed

**Input:**
- Blood type required
- Units needed
- Urgency level
- Location

**Conditional Logic:**
```python
if state.get("requires_blood") and state.get("blood_type"):
    run_blood_agent()
else:
    skip_to_next_agent()
```

**Processing:**
1. Check if blood required (from triage)
2. Extract blood type from description
3. Search nearby blood banks (<20km)
4. Check inventory
5. Reserve units

**Output:**
```python
{
    "blood_bank": {
        "id": "bb-001",
        "name": "Central Blood Bank",
        "distance_km": 3.5
    },
    "blood_type": "O+",
    "units_reserved": 2,
    "reservation_id": "RES-12345"
}
```

---

### 5. Route Agent

**Purpose:** Calculate optimal route with traffic

**Input:**
- Origin: Ambulance location
- Waypoint: Incident location
- Destination: Hospital location
- Traffic conditions

**Processing:**
1. Call Google Maps Directions API
2. Get route with real-time traffic
3. Calculate total distance and time
4. Generate turn-by-turn directions
5. Fallback to OSRM if Google fails

**Output:**
```python
{
    "route": {
        "polyline": "encoded_polyline_string",
        "legs": [
            {
                "start": "Ambulance location",
                "end": "Incident location",
                "distance_km": 5.2,
                "duration_minutes": 8.5
            },
            {
                "start": "Incident location",
                "end": "Hospital",
                "distance_km": 8.3,
                "duration_minutes": 15.2
            }
        ],
        "total_distance_km": 13.5,
        "total_duration_minutes": 23.7
    }
}
```

---

### 6. RAG Agent (Future Enhancement)

**Purpose:** Retrieve relevant medical protocols

**Input:**
- Incident type
- Severity level
- Symptoms/keywords

**Processing:**
1. Query vector database (Pinecone/Weaviate)
2. Semantic search for protocols
3. Rank by relevance
4. Return top 3 protocols

**Output:**
```python
{
    "protocols": [
        {
            "id": "protocol-001",
            "title": "Cardiac Emergency Protocol",
            "relevance_score": 0.92,
            "summary": "...",
            "steps": ["1. Check vitals", "2. Administer oxygen", ...]
        }
    ]
}
```

**Current Status:** Placeholder (returns empty list)

---

### 7. Plan Agent

**Purpose:** Generate comprehensive response plan

**Input:**
- All data from previous agents
- Incident details
- Resource allocations

**Processing:**
1. Validate all required data present
2. Calculate totals (time, distance, resources)
3. Generate structured plan
4. Add recommendations
5. Format for presentation

**Output:**
```python
{
    "response_plan": {
        "incident_summary": "Critical car accident, 3 victims",
        "severity_assessment": {
            "level": "CRITICAL",
            "confidence": 0.98
        },
        "hospital_allocation": {
            "name": "City Hospital",
            "distance_km": 2.3,
            "eta_minutes": 8,
            "available_icu_beds": 5
        },
        "ambulance_dispatch": {
            "vehicle": "MH-01-AB-1234",
            "type": "CRITICAL_CARE",
            "pickup_eta": 5,
            "hospital_eta": 13
        },
        "blood_allocation": {
            "bank": "Central Blood Bank",
            "type": "O+",
            "units": 2
        },
        "route_summary": {
            "total_distance": 13.5,
            "total_time": 24,
            "traffic_level": "MODERATE"
        },
        "total_response_time": 24,
        "recommendations": [
            "Prepare trauma team",
            "Alert blood bank",
            "Notify family if available"
        ],
        "generated_at": "2026-09-06T10:30:00Z"
    }
}
```

---

### 8. Coordinator Agent (Human-in-the-Loop)

**Purpose:** Present plan for human approval

**Input:**
- Complete response plan
- Incident details

**Processing:**
1. Format plan for display
2. Present to coordinator (via WebSocket)
3. Wait for approval decision
4. Handle approval/rejection/modification

**Approval Flow:**
```python
async def run(self, state: AgentState) -> AgentState:
    # Present plan
    self._present_plan_for_approval(state)
    
    # Wait for decision (WebSocket or polling)
    decision = await self._wait_for_approval(state.incident.id)
    
    if decision["action"] == "APPROVE":
        state.approval_status = "APPROVED"
        state.approved_by = decision["user_id"]
        state.approved_at = datetime.now()
        
    elif decision["action"] == "REJECT":
        state.approval_status = "REJECTED"
        state.rejection_reason = decision["reason"]
        # Loop back to Plan Agent
        
    elif decision["action"] == "MODIFY":
        state.modifications = decision["changes"]
        # Apply modifications and continue
        
    return state
```

**Output:**
```python
{
    "approval_status": "APPROVED",
    "approved_by": "user-123",
    "approved_at": "2026-09-06T10:35:00Z",
    "approval_notes": "Plan looks good, proceed with dispatch"
}
```

---

### 9. Communication Agent

**Purpose:** Send notifications to all stakeholders

**Input:**
- Response plan
- Contact information
- Notification preferences

**Processing:**
1. Prepare SMS templates
2. Prepare email templates
3. Send to hospital (SMS + Email)
4. Send to ambulance (SMS)
5. Send to reporter (SMS - future)
6. Log delivery status

**Output:**
```python
{
    "notifications_sent": {
        "hospital": {
            "sms": {"status": "sent", "message_id": "SM123"},
            "email": {"status": "sent", "message_id": "EM456"}
        },
        "ambulance": {
            "sms": {"status": "sent", "message_id": "SM124"}
        }
    },
    "total_notifications": 3,
    "failures": []
}
```

**SMS Template Example:**
```
ARIA EMERGENCY ALERT

Incoming: CRITICAL accident
ETA: 8 minutes
Patient: 3 victims
Ambulance: MH-01-AB-1234

Prepare trauma team.
- ARIA System
```

---

### 10. Monitoring Agent

**Purpose:** Collect metrics and system health

**Input:**
- Full agent state
- Execution timestamps

**Processing:**
1. Calculate total execution time
2. Calculate per-agent execution time
3. Check for errors
4. Collect system health metrics
5. Log to Prometheus

**Output:**
```python
{
    "workflow_metrics": {
        "total_execution_time": 2.3,  # seconds
        "agent_execution_times": {
            "triage": 0.1,
            "hospital": 0.5,
            "ambulance": 0.3,
            "route": 0.4,
            "plan": 0.2,
            "communication": 0.8
        },
        "status": "completed",
        "errors": [],
        "retries": 0
    },
    "system_health": {
        "database": "healthy",
        "redis": "healthy",
        "ml_models": "healthy",
        "external_apis": "healthy"
    }
}
```

---

## State Management

### AgentState Class

```python
from typing import TypedDict, Optional, List, Dict, Any
from datetime import datetime

class AgentState(TypedDict):
    # Incident information
    incident: IncidentInfo
    
    # Triage results
    severity: str
    confidence: float
    requires_blood: bool
    
    # Hospital selection
    hospitals: List[Dict]
    selected_hospital: Optional[Dict]
    
    # Ambulance dispatch
    ambulances: List[Dict]
    selected_ambulance: Optional[Dict]
    pickup_eta: Optional[float]
    hospital_eta: Optional[float]
    
    # Blood bank (conditional)
    blood_bank: Optional[Dict]
    blood_units: Optional[int]
    
    # Route information
    route: Optional[Dict]
    total_distance: Optional[float]
    total_time: Optional[float]
    
    # Medical protocols (RAG)
    protocols: List[Dict]
    
    # Response plan
    response_plan: Optional[Dict]
    
    # Approval
    approval_status: str  # PENDING, APPROVED, REJECTED
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    
    # Notifications
    notifications_sent: Dict[str, Any]
    
    # Metrics
    metrics: Dict[str, Any]
    
    # Errors
    errors: List[str]
```

### State Transitions

```python
# Example state flow
state = {
    "incident": {...},
    "severity": None,  # Set by Triage Agent
    "hospitals": None,  # Set by Hospital Agent
    "selected_hospital": None,  # Set by Hospital Agent
    "ambulances": None,  # Set by Ambulance Agent
    ...
}

# After Triage Agent
state["severity"] = "CRITICAL"
state["confidence"] = 0.98

# After Hospital Agent
state["hospitals"] = [...]
state["selected_hospital"] = {...}

# Continue through workflow...
```

---

## Orchestrator Implementation

### Graph Definition

```python
from langgraph.graph import StateGraph, END

class AgentOrchestrator:
    def __init__(self):
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("triage", self._triage_node)
        workflow.add_node("hospital", self._hospital_node)
        workflow.add_node("ambulance", self._ambulance_node)
        workflow.add_node("blood", self._blood_node)
        workflow.add_node("route", self._route_node)
        workflow.add_node("rag", self._rag_node)
        workflow.add_node("plan", self._plan_node)
        workflow.add_node("coordinator", self._coordinator_node)
        workflow.add_node("communication", self._communication_node)
        workflow.add_node("monitoring", self._monitoring_node)
        
        # Define edges
        workflow.set_entry_point("triage")
        workflow.add_edge("triage", "hospital")
        workflow.add_edge("hospital", "ambulance")
        
        # Conditional edge for blood
        workflow.add_conditional_edges(
            "ambulance",
            self._should_check_blood,
            {
                "blood": "blood",
                "route": "route"
            }
        )
        
        workflow.add_edge("blood", "route")
        workflow.add_edge("route", "rag")
        workflow.add_edge("rag", "plan")
        workflow.add_edge("plan", "coordinator")
        
        # Conditional edge for approval
        workflow.add_conditional_edges(
            "coordinator",
            self._check_approval_status,
            {
                "approved": "communication",
                "rejected": "plan",  # Loop back
                "modified": "plan"   # Loop back
            }
        )
        
        workflow.add_edge("communication", "monitoring")
        workflow.add_edge("monitoring", END)
        
        return workflow.compile()
```

### Execution

```python
async def execute(self, incident: IncidentInfo) -> AgentState:
    """Execute the full agent workflow."""
    
    # Initialize state
    initial_state = AgentState(
        incident=incident,
        errors=[],
        metrics={}
    )
    
    # Run workflow
    try:
        final_state = await self.workflow.ainvoke(initial_state)
        return final_state
        
    except Exception as e:
        logger.error(f"Workflow execution failed: {e}")
        # Fallback logic
        return self._fallback_plan(incident)
```

---

## Error Handling

### Retry Logic

```python
class BaseAgent:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
    
    async def execute(self, state: AgentState) -> AgentState:
        retries = 0
        last_error = None
        
        while retries < self.max_retries:
            try:
                return await self.run(state)
                
            except RetryableError as e:
                retries += 1
                last_error = e
                await self._wait_before_retry(retries)
                
            except FatalError as e:
                logger.error(f"Fatal error in {self.name}: {e}")
                state.errors.append(str(e))
                return state
        
        # Max retries exceeded
        state.errors.append(f"Max retries exceeded: {last_error}")
        return state
```

### Fallback Strategies

```python
# If ML model fails → Rule-based
# If external API fails → Cached data
# If database fails → In-memory fallback
# If entire workflow fails → Manual dispatch
```

---

## Performance Optimization

### Parallel Execution

```python
# Run independent agents in parallel
async def parallel_resource_search(state):
    hospitals_task = hospital_agent.run(state)
    ambulances_task = ambulance_agent.run(state)
    
    hospitals, ambulances = await asyncio.gather(
        hospitals_task,
        ambulances_task
    )
    
    state.hospitals = hospitals
    state.ambulances = ambulances
    return state
```

### Caching

```python
@lru_cache(maxsize=1000)
def get_hospitals_near(lat: float, lon: float, radius: float):
    """Cache hospital queries by location grid."""
    # Round to 100m precision
    lat_grid = round(lat, 3)
    lon_grid = round(lon, 3)
    return database.query_hospitals(lat_grid, lon_grid, radius)
```

---

## Testing

### Unit Tests

```python
@pytest.mark.asyncio
async def test_triage_agent():
    agent = TriageAgent()
    state = AgentState(
        incident=IncidentInfo(
            description="Car accident with injuries",
            location=(19.0760, 72.8777)
        )
    )
    
    result = await agent.run(state)
    
    assert result.severity in ["LOW", "MODERATE", "CRITICAL"]
    assert result.confidence > 0.7
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_full_workflow():
    orchestrator = AgentOrchestrator()
    incident = create_test_incident()
    
    result = await orchestrator.execute(incident)
    
    assert result.approval_status == "APPROVED"
    assert result.selected_hospital is not None
    assert result.selected_ambulance is not None
    assert result.response_plan is not None
```

---

## Monitoring

### Metrics

```python
# Agent execution time
agent_execution_time = Histogram(
    'agent_execution_seconds',
    'Agent execution time',
    ['agent_name']
)

# Workflow success rate
workflow_success = Counter(
    'workflow_completed_total',
    'Workflows completed',
    ['status']
)

# Approval rate
approval_rate = Gauge(
    'workflow_approval_rate',
    'Human approval rate'
)
```

---

## Conclusion

ARIA's LangGraph agent system provides:
- **Modularity:** 14 specialized agents
- **Flexibility:** Conditional routing and loops
- **Reliability:** Retry logic and fallbacks
- **Human Oversight:** Coordinator approval
- **Observability:** Comprehensive metrics
- **Performance:** <3 seconds average execution

---

**Document Version:** 1.0  
**Last Updated:** 2026-09-06  
**Maintained By:** ARIA Development Team

"""
ARIA LangGraph Agent State
Shared state schema for all agents in the emergency response workflow
"""
from typing import Dict, List, Optional, Any, Literal
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class IncidentSeverity(str, Enum):
    """Incident severity levels."""
    LOW = "LOW"
    MODERATE = "MODERATE"
    CRITICAL = "CRITICAL"


class WorkflowStatus(str, Enum):
    """Workflow execution status."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    DISPATCHED = "DISPATCHED"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class Location(BaseModel):
    """Geographic location."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    city: Optional[str] = None


class IncidentInfo(BaseModel):
    """Incident information."""
    incident_id: str
    description: str
    location: Location
    reporter_name: Optional[str] = None
    reporter_phone: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    victim_count: int = 1
    incident_type: Optional[str] = None


class TriageResult(BaseModel):
    """Triage agent output."""
    severity: IncidentSeverity
    confidence: float = Field(..., ge=0, le=1)
    recommended_resources: List[str] = []
    estimated_priority: int = Field(..., ge=1, le=10)


class HospitalInfo(BaseModel):
    """Hospital information."""
    hospital_id: str
    name: str
    location: Location
    distance_km: float
    available_beds: int = 0
    available_icu_beds: int = 0
    has_emergency: bool = True
    specialties: List[str] = []
    contact_phone: Optional[str] = None
    suitability_score: float = Field(..., ge=0, le=1)
    eta_minutes: Optional[float] = None


class AmbulanceInfo(BaseModel):
    """Ambulance information."""
    ambulance_id: str
    registration_number: str
    ambulance_type: str  # BASIC, ALS, CRITICAL_CARE
    current_location: Location
    status: str = "AVAILABLE"
    distance_km: float
    eta_minutes: float
    equipment: List[str] = []
    driver_name: Optional[str] = None
    driver_phone: Optional[str] = None


class BloodBankInfo(BaseModel):
    """Blood bank information."""
    blood_bank_id: str
    name: str
    location: Location
    distance_km: float
    available_units: Dict[str, int] = {}  # blood_type -> units
    contact_phone: Optional[str] = None
    eta_minutes: Optional[float] = None


class RouteInfo(BaseModel):
    """Route information."""
    route_id: str
    from_location: Location
    to_location: Location
    distance_km: float
    eta_minutes: float
    traffic_level: str = "MODERATE"
    waypoints: List[Location] = []
    instructions: List[str] = []


class MedicalProtocol(BaseModel):
    """Medical protocol from RAG."""
    protocol_id: str
    title: str
    content: str
    severity_level: IncidentSeverity
    steps: List[str] = []
    precautions: List[str] = []
    source: str = "Medical Knowledge Base"


class ResponsePlan(BaseModel):
    """Complete response plan."""
    plan_id: str
    incident_id: str
    severity: IncidentSeverity
    selected_hospital: Optional[HospitalInfo] = None
    selected_ambulance: Optional[AmbulanceInfo] = None
    selected_blood_bank: Optional[BloodBankInfo] = None
    route: Optional[RouteInfo] = None
    medical_protocol: Optional[MedicalProtocol] = None
    estimated_total_time: float = 0  # minutes
    total_distance: float = 0  # km
    action_steps: List[str] = []
    notifications_sent: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    approved_by: Optional[str] = None
    approved_at: Optional[datetime] = None


class AgentError(BaseModel):
    """Agent error information."""
    agent_name: str
    error_type: str
    error_message: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    retry_count: int = 0


class AgentState(BaseModel):
    """
    Shared state for all LangGraph agents.
    This is passed between agents and updated by each agent.
    """
    # Incident Information
    incident: IncidentInfo
    
    # Agent Results
    triage_result: Optional[TriageResult] = None
    hospitals: List[HospitalInfo] = []
    ambulances: List[AmbulanceInfo] = []
    blood_banks: List[BloodBankInfo] = []
    route: Optional[RouteInfo] = None
    medical_protocols: List[MedicalProtocol] = []
    
    # Final Response Plan
    response_plan: Optional[ResponsePlan] = None
    
    # Workflow Control
    workflow_status: WorkflowStatus = WorkflowStatus.PENDING
    current_agent: Optional[str] = None
    completed_agents: List[str] = []
    failed_agents: List[str] = []
    
    # Errors and Retries
    errors: List[AgentError] = []
    retry_count: int = 0
    max_retries: int = 3
    
    # Human-in-the-loop
    requires_approval: bool = False
    approval_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Additional Context
    context: Dict[str, Any] = {}
    
    class Config:
        arbitrary_types_allowed = True


class AgentInput(BaseModel):
    """Base input for all agents."""
    state: AgentState


class AgentOutput(BaseModel):
    """Base output for all agents."""
    state: AgentState
    success: bool = True
    message: Optional[str] = None
    execution_time: Optional[float] = None


# Type aliases for clarity
AgentFunction = Any  # Callable[[AgentState], AgentState]

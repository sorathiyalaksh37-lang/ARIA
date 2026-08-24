"""
Incident Pydantic Schemas
"""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from uuid import UUID

from app.models.incident import IncidentSeverity, IncidentType, IncidentStatus


class IncidentLocation(BaseModel):
    """Location schema."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    address: Optional[str] = None
    city: Optional[str] = None


class IncidentCreate(BaseModel):
    """Schema for creating incident."""
    description: str = Field(..., min_length=10, max_length=2000)
    incident_type: IncidentType
    location: IncidentLocation
    victim_count: int = Field(1, ge=1, le=100)
    
    # Reporter
    reporter_name: Optional[str] = Field(None, max_length=255)
    reporter_phone: Optional[str] = Field(None, max_length=20)
    reporter_relationship: Optional[str] = Field(None, max_length=100)
    
    # Medical requirements
    blood_required: bool = False
    blood_type: Optional[str] = Field(None, pattern="^(A|B|AB|O)[+-]$")
    ambulance_required: bool = True
    hospital_required: bool = True


class IncidentUpdate(BaseModel):
    """Schema for updating incident."""
    description: Optional[str] = Field(None, min_length=10, max_length=2000)
    severity: Optional[IncidentSeverity] = None
    status: Optional[IncidentStatus] = None
    assigned_hospital_id: Optional[UUID] = None
    assigned_ambulance_id: Optional[UUID] = None
    approval_notes: Optional[str] = None


class IncidentResponse(BaseModel):
    """Schema for incident response."""
    id: UUID
    incident_code: str
    description: str
    incident_type: IncidentType
    severity: IncidentSeverity
    status: IncidentStatus
    
    latitude: float
    longitude: float
    address: Optional[str]
    city: Optional[str]
    
    victim_count: int
    priority_score: Optional[float]
    
    # AI predictions
    predicted_severity: Optional[IncidentSeverity]
    ml_confidence: Optional[float]
    
    # Assignment
    assigned_hospital_id: Optional[UUID]
    assigned_ambulance_id: Optional[UUID]
    estimated_response_time: Optional[int]
    
    # Timestamps
    reported_at: datetime
    triaged_at: Optional[datetime]
    dispatched_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class IncidentProcess(BaseModel):
    """Schema for processing incident through AI workflow."""
    force_processing: bool = False
    override_ml: bool = False
    
    
class IncidentApproval(BaseModel):
    """Schema for approving/rejecting incident plan."""
    approved: bool
    notes: Optional[str] = Field(None, max_length=1000)
    modifications: Optional[Dict[str, Any]] = None


class IncidentPlanModification(BaseModel):
    """Schema for modifying incident plan."""
    assigned_hospital_id: Optional[UUID] = None
    assigned_ambulance_id: Optional[UUID] = None
    response_plan_updates: Optional[Dict[str, Any]] = None
    notes: Optional[str] = Field(None, max_length=1000)


class IncidentHistoryResponse(BaseModel):
    """Schema for incident history entry."""
    id: UUID
    incident_id: UUID
    status: IncidentStatus
    change_type: Optional[str]
    changes: Optional[Dict[str, Any]]
    notes: Optional[str]
    changed_at: datetime
    
    class Config:
        from_attributes = True


class IncidentListFilter(BaseModel):
    """Schema for filtering incidents."""
    status: Optional[List[IncidentStatus]] = None
    severity: Optional[List[IncidentSeverity]] = None
    incident_type: Optional[List[IncidentType]] = None
    city: Optional[str] = None
    from_date: Optional[datetime] = None
    to_date: Optional[datetime] = None
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)

"""
Incident Database Model
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
import uuid
import enum

from app.core.database import Base


class IncidentSeverity(str, enum.Enum):
    """Incident severity levels."""
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class IncidentType(str, enum.Enum):
    """Incident types."""
    MEDICAL = "MEDICAL"
    ACCIDENT = "ACCIDENT"
    FIRE = "FIRE"
    VIOLENCE = "VIOLENCE"
    NATURAL_DISASTER = "NATURAL_DISASTER"
    OTHER = "OTHER"


class IncidentStatus(str, enum.Enum):
    """Incident status."""
    REPORTED = "REPORTED"
    TRIAGED = "TRIAGED"
    PLAN_GENERATED = "PLAN_GENERATED"
    AWAITING_APPROVAL = "AWAITING_APPROVAL"
    APPROVED = "APPROVED"
    DISPATCHED = "DISPATCHED"
    EN_ROUTE = "EN_ROUTE"
    ON_SCENE = "ON_SCENE"
    TRANSPORTING = "TRANSPORTING"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class Incident(Base):
    """Incident model with PostGIS geometry."""
    __tablename__ = "incidents"
    
    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_code = Column(String(50), unique=True, index=True, nullable=False)
    
    # Location
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(String(500))
    city = Column(String(100), index=True)
    
    # Incident details
    description = Column(Text, nullable=False)
    incident_type = Column(SQLEnum(IncidentType), nullable=False, index=True)
    severity = Column(SQLEnum(IncidentSeverity), nullable=False, index=True)
    victim_count = Column(Integer, default=1)
    
    # Status tracking
    status = Column(SQLEnum(IncidentStatus), default=IncidentStatus.REPORTED, nullable=False, index=True)
    priority_score = Column(Float)
    
    # Reporter information
    reporter_name = Column(String(255))
    reporter_phone = Column(String(20))
    reporter_relationship = Column(String(100))
    
    # Medical details
    blood_required = Column(Boolean, default=False)
    blood_type = Column(String(10))
    ambulance_required = Column(Boolean, default=True)
    hospital_required = Column(Boolean, default=True)
    
    # AI/ML predictions
    predicted_severity = Column(SQLEnum(IncidentSeverity))
    ml_confidence = Column(Float)
    
    # Response plan
    response_plan = Column(JSON)  # Full AI-generated plan
    assigned_hospital_id = Column(UUID(as_uuid=True), ForeignKey("hospitals.id"))
    assigned_ambulance_id = Column(UUID(as_uuid=True), ForeignKey("ambulances.id"))
    estimated_response_time = Column(Integer)  # minutes
    
    # Human approval
    requires_approval = Column(Boolean, default=True)
    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime)
    approval_notes = Column(Text)
    
    # Timestamps
    reported_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    triaged_at = Column(DateTime)
    dispatched_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    created_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    assigned_hospital = relationship("Hospital", back_populates="incidents", foreign_keys=[assigned_hospital_id])
    assigned_ambulance = relationship("Ambulance", back_populates="incidents", foreign_keys=[assigned_ambulance_id])
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
    history = relationship("IncidentHistory", back_populates="incident", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        # Spatial index on location
        # Created automatically by PostGIS
    )
    
    def __repr__(self):
        return f"<Incident {self.incident_code}>"


class IncidentHistory(Base):
    """Incident status history for audit trail."""
    __tablename__ = "incident_history"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"), nullable=False, index=True)
    
    # Change tracking
    status = Column(SQLEnum(IncidentStatus), nullable=False)
    changed_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    changed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Change details
    change_type = Column(String(50))  # status_change, assignment, approval, etc.
    changes = Column(JSON)  # Detailed change log
    notes = Column(Text)
    
    # Relationships
    incident = relationship("Incident", back_populates="history")
    user = relationship("User")
    
    def __repr__(self):
        return f"<IncidentHistory {self.incident_id} - {self.status}>"

"""
Ambulance Database Model
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
import uuid
import enum

from app.core.database import Base


class AmbulanceType(str, enum.Enum):
    """Ambulance types."""
    BASIC = "BASIC"
    ALS = "ALS"  # Advanced Life Support
    CRITICAL_CARE = "CRITICAL_CARE"
    AIR_AMBULANCE = "AIR_AMBULANCE"


class AmbulanceStatus(str, enum.Enum):
    """Ambulance availability status."""
    AVAILABLE = "AVAILABLE"
    DISPATCHED = "DISPATCHED"
    EN_ROUTE = "EN_ROUTE"
    ON_SCENE = "ON_SCENE"
    TRANSPORTING = "TRANSPORTING"
    AT_HOSPITAL = "AT_HOSPITAL"
    OFFLINE = "OFFLINE"
    MAINTENANCE = "MAINTENANCE"


class Ambulance(Base):
    """Ambulance model with real-time tracking."""
    __tablename__ = "ambulances"
    
    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_number = Column(String(50), unique=True, index=True, nullable=False)
    ambulance_code = Column(String(50), unique=True, index=True)
    
    # Type & equipment
    ambulance_type = Column(SQLEnum(AmbulanceType), nullable=False, index=True)
    equipment = Column(JSON)  # List of available medical equipment
    has_ventilator = Column(Boolean, default=False)
    has_defibrillator = Column(Boolean, default=False)
    has_oxygen = Column(Boolean, default=True)
    
    # Location (real-time)
    current_location = Column(Geometry('POINT', srid=4326))
    latitude = Column(Float)
    longitude = Column(Float)
    last_location_update = Column(DateTime)
    
    # Base station
    base_station = Column(String(255))
    base_location = Column(Geometry('POINT', srid=4326))
    base_city = Column(String(100), index=True)
    
    # Status
    status = Column(SQLEnum(AmbulanceStatus), default=AmbulanceStatus.AVAILABLE, nullable=False, index=True)
    is_active = Column(Boolean, default=True)
    
    # Current assignment
    current_incident_id = Column(UUID(as_uuid=True), ForeignKey("incidents.id"))
    
    # Driver & crew
    driver_name = Column(String(255))
    driver_phone = Column(String(20))
    paramedic_name = Column(String(255))
    paramedic_phone = Column(String(20))
    crew_size = Column(Integer, default=2)
    
    # Organization
    organization = Column(String(255))
    is_government = Column(Boolean, default=False)
    
    # Contact
    contact_number = Column(String(20))
    emergency_contact = Column(String(20))
    
    # Performance metrics
    total_trips = Column(Integer, default=0)
    average_response_time = Column(Float)  # minutes
    last_maintenance = Column(DateTime)
    next_maintenance = Column(DateTime)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    incidents = relationship("Incident", back_populates="assigned_ambulance")
    
    # Indexes
    __table_args__ = (
        # Spatial index created automatically by PostGIS
    )
    
    def __repr__(self):
        return f"<Ambulance {self.vehicle_number}>"

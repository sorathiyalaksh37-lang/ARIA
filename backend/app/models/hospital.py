"""
Hospital Database Model
"""
from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, Text
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from geoalchemy2 import Geometry
import uuid

from app.core.database import Base


class Hospital(Base):
    """Hospital model with PostGIS geometry."""
    __tablename__ = "hospitals"
    
    # Primary fields
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(500), nullable=False, index=True)
    hospital_code = Column(String(50), unique=True, index=True)
    
    # Location
    location = Column(Geometry('POINT', srid=4326), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    address = Column(Text)
    city = Column(String(100), index=True)
    state = Column(String(100))
    pincode = Column(String(10))
    
    # Contact
    phone = Column(String(20))
    emergency_phone = Column(String(20))
    email = Column(String(255))
    website = Column(String(500))
    
    # Capacity
    total_beds = Column(Integer, default=0)
    available_beds = Column(Integer, default=0)
    icu_beds = Column(Integer, default=0)
    available_icu_beds = Column(Integer, default=0)
    ventilators = Column(Integer, default=0)
    available_ventilators = Column(Integer, default=0)
    
    # Specialties
    specialties = Column(ARRAY(String))  # ["cardiology", "neurology", ...]
    trauma_center = Column(Boolean, default=False)
    burn_unit = Column(Boolean, default=False)
    maternity_unit = Column(Boolean, default=False)
    pediatric_unit = Column(Boolean, default=False)
    
    # Ratings & metrics
    rating = Column(Float)
    total_reviews = Column(Integer, default=0)
    success_rate = Column(Float)
    average_wait_time = Column(Integer)  # minutes
    
    # Blood bank
    has_blood_bank = Column(Boolean, default=False)
    blood_inventory = Column(JSON)  # {"A+": 10, "O-": 5, ...}
    
    # Operational
    is_active = Column(Boolean, default=True)
    accepts_emergency = Column(Boolean, default=True)
    is_government = Column(Boolean, default=False)
    
    # Additional data
    facilities = Column(JSON)
    operating_hours = Column(JSON)
    insurance_accepted = Column(ARRAY(String))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_capacity_update = Column(DateTime)
    
    # Relationships
    incidents = relationship("Incident", back_populates="assigned_hospital")
    
    # Indexes
    __table_args__ = (
        # Spatial index created automatically by PostGIS
    )
    
    def __repr__(self):
        return f"<Hospital {self.name}>"

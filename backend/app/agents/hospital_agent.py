"""
ARIA Hospital Agent
Finds and ranks suitable hospitals
"""
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from geoalchemy2.functions import ST_Distance, ST_DWithin
from geoalchemy2.elements import WKTElement

from app.agents.base_agent import BaseAgent
from app.agents.state import AgentState, HospitalInfo, Location, IncidentSeverity
from app.models.hospital import Hospital
from app.services.ml_service import MLService


class HospitalAgent(BaseAgent):
    """
    Hospital Agent: Finds and ranks hospitals based on location, capacity, and specialty.
    Uses LightGBM LambdaMART model trained on 63K hospitals.
    """
    
    def __init__(
        self, 
        ml_service: MLService, 
        db_session: AsyncSession,
        max_retries: int = 3,
        max_distance_km: float = 20.0,
        max_results: int = 10
    ):
        """
        Initialize hospital agent.
        
        Args:
            ml_service: ML service instance
            db_session: Database session
            max_retries: Maximum retries on failure
            max_distance_km: Maximum search radius in km
            max_results: Maximum number of hospitals to return
        """
        super().__init__(name="HospitalAgent", max_retries=max_retries)
        self.ml_service = ml_service
        self.db = db_session
        self.max_distance_km = max_distance_km
        self.max_results = max_results
    
    async def run(self, state: AgentState) -> AgentState:
        """
        Find and rank suitable hospitals.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with ranked hospitals
        """
        self._log_state_update(
            "Starting hospital search",
            latitude=state.incident.location.latitude,
            longitude=state.incident.location.longitude,
            max_distance=self.max_distance_km
        )
        
        # Validate triage result exists
        if not state.triage_result:
            raise ValueError("Triage result required before hospital search")
        
        severity = state.triage_result.severity
        
        # Query nearby hospitals from database
        hospitals = await self._query_nearby_hospitals(
            state.incident.location,
            severity
        )
        
        if not hospitals:
            self.logger.warning(f"⚠️ No hospitals found within {self.max_distance_km}km")
            # Try expanding search radius
            self.logger.info("🔍 Expanding search to 50km...")
            hospitals = await self._query_nearby_hospitals(
                state.incident.location,
                severity,
                max_distance_km=50.0
            )
        
        if not hospitals:
            raise ValueError(f"No hospitals found within 50km of incident location")
        
        self.logger.info(f"📍 Found {len(hospitals)} candidate hospitals")
        
        # Prepare data for ML ranking
        ranking_input = {
            "incident_location": {
                "latitude": state.incident.location.latitude,
                "longitude": state.incident.location.longitude
            },
            "severity": severity.value,
            "timestamp": state.incident.timestamp.isoformat(),
            "hospitals": hospitals
        }
        
        # Call ML service for ranking
        self.logger.info("🏥 Ranking hospitals using ML model...")
        ranked_hospitals = await self.ml_service.rank_hospitals(ranking_input)
        
        # Convert to HospitalInfo objects
        hospital_infos = []
        for rank, hosp_data in enumerate(ranked_hospitals[:self.max_results], 1):
            hospital_info = HospitalInfo(
                hospital_id=hosp_data["hospital_id"],
                name=hosp_data["name"],
                location=Location(
                    latitude=hosp_data["latitude"],
                    longitude=hosp_data["longitude"],
                    address=hosp_data.get("address"),
                    city=hosp_data.get("city")
                ),
                distance_km=hosp_data["distance_km"],
                available_beds=hosp_data.get("available_beds", 0),
                available_icu_beds=hosp_data.get("available_icu_beds", 0),
                has_emergency=hosp_data.get("has_emergency", True),
                specialties=hosp_data.get("specialties", []),
                contact_phone=hosp_data.get("contact_phone"),
                suitability_score=hosp_data["suitability_score"],
                eta_minutes=hosp_data.get("eta_minutes")
            )
            hospital_infos.append(hospital_info)
            
            self.logger.info(
                f"  #{rank}: {hospital_info.name} "
                f"({hospital_info.distance_km:.1f}km, score: {hospital_info.suitability_score:.3f})"
            )
        
        # Update state
        state.hospitals = hospital_infos
        
        # Store top hospital in context
        if hospital_infos:
            state.context["top_hospital_id"] = hospital_infos[0].hospital_id
            state.context["top_hospital_name"] = hospital_infos[0].name
        
        self._log_state_update(
            "Hospital ranking completed",
            hospitals_found=len(hospital_infos),
            top_hospital=hospital_infos[0].name if hospital_infos else "None"
        )
        
        return state
    
    async def _query_nearby_hospitals(
        self,
        location: Location,
        severity: IncidentSeverity,
        max_distance_km: float = None
    ) -> List[dict]:
        """
        Query nearby hospitals from database using PostGIS.
        
        Args:
            location: Incident location
            severity: Incident severity
            max_distance_km: Maximum search radius
            
        Returns:
            List of hospital data dictionaries
        """
        if max_distance_km is None:
            max_distance_km = self.max_distance_km
        
        # Create point from incident location
        incident_point = WKTElement(
            f'POINT({location.longitude} {location.latitude})',
            srid=4326
        )
        
        # Build query
        query = select(Hospital).where(
            ST_DWithin(
                Hospital.location,
                incident_point,
                max_distance_km * 1000  # Convert km to meters
            )
        )
        
        # Filter by requirements based on severity
        if severity == IncidentSeverity.CRITICAL:
            query = query.where(
                Hospital.has_emergency == True,
                Hospital.icu_beds > 0
            )
        elif severity == IncidentSeverity.MODERATE:
            query = query.where(Hospital.has_emergency == True)
        
        # Order by distance
        query = query.order_by(
            ST_Distance(Hospital.location, incident_point)
        ).limit(100)  # Limit to 100 for ranking
        
        # Execute query
        result = await self.db.execute(query)
        hospitals_db = result.scalars().all()
        
        # Convert to dict format
        hospitals = []
        for hospital in hospitals_db:
            # Calculate distance
            distance_query = select(
                func.ST_Distance(
                    Hospital.location,
                    incident_point
                )
            ).where(Hospital.id == hospital.id)
            
            distance_result = await self.db.execute(distance_query)
            distance_meters = distance_result.scalar()
            distance_km = distance_meters / 1000 if distance_meters else 0
            
            hospital_dict = {
                "hospital_id": str(hospital.id),
                "name": hospital.name,
                "latitude": hospital.latitude,
                "longitude": hospital.longitude,
                "address": hospital.address,
                "city": hospital.city,
                "distance_km": round(distance_km, 2),
                "available_beds": hospital.beds or 0,
                "available_icu_beds": hospital.icu_beds or 0,
                "has_emergency": hospital.has_emergency or False,
                "specialties": hospital.specialties or [],
                "contact_phone": hospital.phone,
                "has_ventilators": hospital.ventilators and hospital.ventilators > 0,
                "has_blood_bank": hospital.blood_bank or False
            }
            hospitals.append(hospital_dict)
        
        return hospitals

"""
ARIA Ambulance Agent
Finds and dispatches ambulances
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from geoalchemy2.functions import ST_Distance
from geoalchemy2.elements import WKTElement

from app.agents.base_agent import BaseAgent
from app.agents.state import AgentState, AmbulanceInfo, Location, IncidentSeverity
from app.models.ambulance import Ambulance
from app.services.ml_service import MLService


class AmbulanceAgent(BaseAgent):
    """
    Ambulance Agent: Finds and dispatches nearest available ambulances.
    Considers ambulance type, equipment, and ETA.
    """
    
    def __init__(
        self,
        ml_service: MLService,
        db_session: AsyncSession,
        max_retries: int = 3,
        max_distance_km: float = 30.0,
        max_results: int = 5
    ):
        """
        Initialize ambulance agent.
        
        Args:
            ml_service: ML service instance
            db_session: Database session
            max_retries: Maximum retries
            max_distance_km: Maximum search radius
            max_results: Maximum ambulances to return
        """
        super().__init__(name="AmbulanceAgent", max_retries=max_retries)
        self.ml_service = ml_service
        self.db = db_session
        self.max_distance_km = max_distance_km
        self.max_results = max_results
    
    async def run(self, state: AgentState) -> AgentState:
        """
        Find and dispatch suitable ambulances.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with ambulances
        """
        self._log_state_update(
            "Starting ambulance search",
            latitude=state.incident.location.latitude,
            longitude=state.incident.location.longitude
        )
        
        # Validate triage result
        if not state.triage_result:
            raise ValueError("Triage result required before ambulance search")
        
        severity = state.triage_result.severity
        
        # Determine required ambulance type
        required_type = self._determine_ambulance_type(severity, state.incident)
        
        # Query available ambulances
        ambulances = await self._query_available_ambulances(
            state.incident.location,
            required_type,
            severity
        )
        
        if not ambulances:
            self.logger.warning(
                f"⚠️ No {required_type} ambulances available within {self.max_distance_km}km"
            )
            # Try any available ambulance
            self.logger.info("🔍 Searching for any available ambulance...")
            ambulances = await self._query_available_ambulances(
                state.incident.location,
                ambulance_type=None,
                severity=severity
            )
        
        if not ambulances:
            raise ValueError("No ambulances available in the area")
        
        self.logger.info(f"🚑 Found {len(ambulances)} available ambulances")
        
        # Calculate ETA for each ambulance using ML model
        ambulances_with_eta = await self._calculate_etas(
            ambulances,
            state.incident.location,
            severity
        )
        
        # Sort by ETA (fastest first)
        ambulances_with_eta.sort(key=lambda x: x["eta_minutes"])
        
        # Convert to AmbulanceInfo objects
        ambulance_infos = []
        for rank, amb_data in enumerate(ambulances_with_eta[:self.max_results], 1):
            ambulance_info = AmbulanceInfo(
                ambulance_id=amb_data["ambulance_id"],
                registration_number=amb_data["registration_number"],
                ambulance_type=amb_data["ambulance_type"],
                current_location=Location(
                    latitude=amb_data["latitude"],
                    longitude=amb_data["longitude"],
                    address=amb_data.get("base_location")
                ),
                status=amb_data["status"],
                distance_km=amb_data["distance_km"],
                eta_minutes=amb_data["eta_minutes"],
                equipment=amb_data.get("equipment", []),
                driver_name=amb_data.get("driver_name"),
                driver_phone=amb_data.get("driver_phone")
            )
            ambulance_infos.append(ambulance_info)
            
            self.logger.info(
                f"  #{rank}: {ambulance_info.registration_number} "
                f"({ambulance_info.ambulance_type}) - "
                f"ETA: {ambulance_info.eta_minutes:.1f} min, "
                f"Distance: {ambulance_info.distance_km:.1f}km"
            )
        
        # Update state
        state.ambulances = ambulance_infos
        
        # Store best ambulance in context
        if ambulance_infos:
            state.context["best_ambulance_id"] = ambulance_infos[0].ambulance_id
            state.context["best_ambulance_eta"] = ambulance_infos[0].eta_minutes
        
        self._log_state_update(
            "Ambulance search completed",
            ambulances_found=len(ambulance_infos),
            best_eta=f"{ambulance_infos[0].eta_minutes:.1f} min" if ambulance_infos else "N/A"
        )
        
        return state
    
    def _determine_ambulance_type(
        self,
        severity: IncidentSeverity,
        incident
    ) -> str:
        """
        Determine required ambulance type based on severity.
        
        Args:
            severity: Incident severity
            incident: Incident information
            
        Returns:
            Ambulance type: BASIC, ALS, or CRITICAL_CARE
        """
        if severity == IncidentSeverity.CRITICAL:
            return "CRITICAL_CARE"
        elif severity == IncidentSeverity.MODERATE:
            return "ALS"  # Advanced Life Support
        else:
            return "BASIC"
    
    async def _query_available_ambulances(
        self,
        location: Location,
        ambulance_type: Optional[str] = None,
        severity: IncidentSeverity = None
    ) -> List[dict]:
        """
        Query available ambulances from database.
        
        Args:
            location: Incident location
            ambulance_type: Required ambulance type (or None for any)
            severity: Incident severity
            
        Returns:
            List of ambulance data dictionaries
        """
        # Create point from incident location
        incident_point = WKTElement(
            f'POINT({location.longitude} {location.latitude})',
            srid=4326
        )
        
        # Build query
        query = select(Ambulance).where(
            Ambulance.status == "AVAILABLE"
        )
        
        # Filter by type if specified
        if ambulance_type:
            query = query.where(Ambulance.ambulance_type == ambulance_type)
        
        # Order by distance
        query = query.order_by(
            ST_Distance(Ambulance.location, incident_point)
        ).limit(20)  # Limit to 20 nearest
        
        # Execute query
        result = await self.db.execute(query)
        ambulances_db = result.scalars().all()
        
        # Convert to dict format
        ambulances = []
        for ambulance in ambulances_db:
            # Calculate distance
            distance_query = select(
                ST_Distance(
                    Ambulance.location,
                    incident_point
                )
            ).where(Ambulance.id == ambulance.id)
            
            distance_result = await self.db.execute(distance_query)
            distance_meters = distance_result.scalar()
            distance_km = distance_meters / 1000 if distance_meters else 0
            
            # Skip if too far
            if distance_km > self.max_distance_km:
                continue
            
            ambulance_dict = {
                "ambulance_id": str(ambulance.id),
                "registration_number": ambulance.registration_number,
                "ambulance_type": ambulance.ambulance_type,
                "latitude": ambulance.latitude,
                "longitude": ambulance.longitude,
                "base_location": ambulance.base_location,
                "status": ambulance.status,
                "distance_km": round(distance_km, 2),
                "equipment": ambulance.equipment or [],
                "driver_name": ambulance.driver_name,
                "driver_phone": ambulance.driver_phone
            }
            ambulances.append(ambulance_dict)
        
        return ambulances
    
    async def _calculate_etas(
        self,
        ambulances: List[dict],
        incident_location: Location,
        severity: IncidentSeverity
    ) -> List[dict]:
        """
        Calculate ETA for each ambulance using ML model.
        
        Args:
            ambulances: List of ambulance data
            incident_location: Incident location
            severity: Incident severity
            
        Returns:
            Ambulances with ETA added
        """
        for ambulance in ambulances:
            try:
                # Prepare ETA prediction input
                eta_input = {
                    "from_location": {
                        "latitude": ambulance["latitude"],
                        "longitude": ambulance["longitude"]
                    },
                    "to_location": {
                        "latitude": incident_location.latitude,
                        "longitude": incident_location.longitude
                    },
                    "distance_km": ambulance["distance_km"],
                    "ambulance_type": ambulance["ambulance_type"],
                    "severity": severity.value,
                    "use_siren": severity in [IncidentSeverity.CRITICAL, IncidentSeverity.MODERATE]
                }
                
                # Call ML service for ETA prediction
                eta_result = await self.ml_service.predict_eta(eta_input)
                ambulance["eta_minutes"] = eta_result["eta_minutes"]
                
            except Exception as e:
                self.logger.warning(
                    f"Failed to predict ETA for ambulance {ambulance['ambulance_id']}: {e}"
                )
                # Fallback: estimate based on distance (60 km/h average)
                ambulance["eta_minutes"] = (ambulance["distance_km"] / 60) * 60
        
        return ambulances

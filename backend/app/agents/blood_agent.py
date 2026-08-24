"""
ARIA Blood Agent
Finds and reserves blood from blood banks
"""
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from geoalchemy2.functions import ST_Distance
from geoalchemy2.elements import WKTElement

from app.agents.base_agent import BaseAgent
from app.agents.state import AgentState, BloodBankInfo, Location, IncidentSeverity
from app.models.blood_bank import BloodBank


class BloodAgent(BaseAgent):
    """
    Blood Agent: Finds blood banks and checks availability.
    Only activates if blood is required based on incident description.
    """
    
    def __init__(
        self,
        db_session: AsyncSession,
        max_retries: int = 3,
        max_distance_km: float = 25.0,
        max_results: int = 5
    ):
        """
        Initialize blood agent.
        
        Args:
            db_session: Database session
            max_retries: Maximum retries
            max_distance_km: Maximum search radius
            max_results: Maximum blood banks to return
        """
        super().__init__(name="BloodAgent", max_retries=max_retries)
        self.db = db_session
        self.max_distance_km = max_distance_km
        self.max_results = max_results
    
    async def run(self, state: AgentState) -> AgentState:
        """
        Find blood banks if blood is required.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with blood banks
        """
        # Check if blood is needed
        needs_blood = self._check_blood_requirement(state)
        
        if not needs_blood:
            self.logger.info("ℹ️ Blood not required for this incident - skipping")
            state.blood_banks = []
            return state
        
        self._log_state_update(
            "Starting blood bank search",
            latitude=state.incident.location.latitude,
            longitude=state.incident.location.longitude
        )
        
        # Determine required blood type (if mentioned in description)
        required_blood_type = self._extract_blood_type(state.incident.description)
        
        # Query nearby blood banks
        blood_banks = await self._query_nearby_blood_banks(
            state.incident.location,
            required_blood_type
        )
        
        if not blood_banks:
            self.logger.warning(
                f"⚠️ No blood banks found within {self.max_distance_km}km"
            )
            # Expand search
            blood_banks = await self._query_nearby_blood_banks(
                state.incident.location,
                required_blood_type,
                max_distance_km=50.0
            )
        
        if not blood_banks:
            self.logger.warning("⚠️ No blood banks available in extended area")
            state.blood_banks = []
            return state
        
        self.logger.info(f"🩸 Found {len(blood_banks)} blood banks")
        
        # Convert to BloodBankInfo objects
        blood_bank_infos = []
        for rank, bb_data in enumerate(blood_banks[:self.max_results], 1):
            blood_bank_info = BloodBankInfo(
                blood_bank_id=bb_data["blood_bank_id"],
                name=bb_data["name"],
                location=Location(
                    latitude=bb_data["latitude"],
                    longitude=bb_data["longitude"],
                    address=bb_data.get("address"),
                    city=bb_data.get("city")
                ),
                distance_km=bb_data["distance_km"],
                available_units=bb_data["available_units"],
                contact_phone=bb_data.get("contact_phone"),
                eta_minutes=bb_data.get("eta_minutes")
            )
            blood_bank_infos.append(blood_bank_info)
            
            # Log availability
            total_units = sum(bb_data["available_units"].values())
            self.logger.info(
                f"  #{rank}: {blood_bank_info.name} - "
                f"{blood_bank_info.distance_km:.1f}km, "
                f"{total_units} total units available"
            )
            
            if required_blood_type:
                units = bb_data["available_units"].get(required_blood_type, 0)
                self.logger.info(f"        {required_blood_type}: {units} units")
        
        # Update state
        state.blood_banks = blood_bank_infos
        
        # Store in context
        if blood_bank_infos:
            state.context["blood_required"] = True
            state.context["required_blood_type"] = required_blood_type
            state.context["nearest_blood_bank"] = blood_bank_infos[0].name
        
        self._log_state_update(
            "Blood bank search completed",
            blood_banks_found=len(blood_bank_infos),
            blood_type=required_blood_type or "Any"
        )
        
        return state
    
    def _check_blood_requirement(self, state: AgentState) -> bool:
        """
        Check if blood is required based on incident and triage.
        
        Args:
            state: Agent state
            
        Returns:
            True if blood is required
        """
        # Check triage result
        if state.triage_result:
            if "BLOOD_BANK" in state.triage_result.recommended_resources:
                return True
        
        # Check incident description for blood-related keywords
        description_lower = state.incident.description.lower()
        blood_keywords = [
            "blood", "bleeding", "hemorrhage", "transfusion",
            "bleed", "stab", "gunshot", "laceration",
            "severe injury", "trauma", "accident"
        ]
        
        return any(keyword in description_lower for keyword in blood_keywords)
    
    def _extract_blood_type(self, description: str) -> Optional[str]:
        """
        Extract blood type from incident description if mentioned.
        
        Args:
            description: Incident description
            
        Returns:
            Blood type (e.g., "O+") or None
        """
        blood_types = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"]
        description_upper = description.upper()
        
        for blood_type in blood_types:
            if blood_type in description_upper:
                return blood_type
        
        return None
    
    async def _query_nearby_blood_banks(
        self,
        location: Location,
        required_blood_type: Optional[str] = None,
        max_distance_km: float = None
    ) -> List[dict]:
        """
        Query nearby blood banks from database.
        
        Args:
            location: Incident location
            required_blood_type: Required blood type
            max_distance_km: Maximum search radius
            
        Returns:
            List of blood bank data dictionaries
        """
        if max_distance_km is None:
            max_distance_km = self.max_distance_km
        
        # Create point from incident location
        incident_point = WKTElement(
            f'POINT({location.longitude} {location.latitude})',
            srid=4326
        )
        
        # Build query
        query = select(BloodBank).where(
            BloodBank.available_24x7 == True
        )
        
        # Order by distance
        query = query.order_by(
            ST_Distance(BloodBank.location, incident_point)
        ).limit(20)
        
        # Execute query
        result = await self.db.execute(query)
        blood_banks_db = result.scalars().all()
        
        # Convert to dict format
        blood_banks = []
        for bb in blood_banks_db:
            # Calculate distance
            distance_query = select(
                ST_Distance(
                    BloodBank.location,
                    incident_point
                )
            ).where(BloodBank.id == bb.id)
            
            distance_result = await self.db.execute(distance_query)
            distance_meters = distance_result.scalar()
            distance_km = distance_meters / 1000 if distance_meters else 0
            
            # Skip if too far
            if distance_km > max_distance_km:
                continue
            
            # Parse blood inventory (stored as JSON in database)
            available_units = bb.blood_inventory or {}
            
            # Filter by required type if specified
            if required_blood_type:
                if available_units.get(required_blood_type, 0) == 0:
                    continue  # Skip if required type not available
            
            blood_bank_dict = {
                "blood_bank_id": str(bb.id),
                "name": bb.name,
                "latitude": bb.latitude,
                "longitude": bb.longitude,
                "address": bb.address,
                "city": bb.city,
                "distance_km": round(distance_km, 2),
                "available_units": available_units,
                "contact_phone": bb.phone,
                "license_number": bb.license_number,
                "accreditation": bb.accreditation
            }
            blood_banks.append(blood_bank_dict)
        
        # Sort by distance
        blood_banks.sort(key=lambda x: x["distance_km"])
        
        return blood_banks

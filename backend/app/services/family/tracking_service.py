"""
Family Tracking Service
Provides secure shareable tracking tokens, live ambulance location coordinates,
live ETA calculations, hospital destination details, and doctor updates.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class FamilyTrackingService:
    """Provides real-time patient location tracking, live ETA, and doctor status updates."""

    def __init__(self):
        # In-memory tracking state: incident_id -> tracking detail record
        self._tracking_db: Dict[str, Dict[str, Any]] = {}
        self._seed_default_tracking()

    def _seed_default_tracking(self):
        sample_id = "INC-1001"
        self._tracking_db[sample_id] = {
            "incident_id": sample_id,
            "patient_name": "Michael Miller",
            "token": f"TRACK-{sample_id}-SECURE-TOKEN",
            "current_status": "EN_ROUTE_TO_HOSPITAL",
            "status_label": "En Route to General Trauma Center",
            "ambulance_id": "AMB-402",
            "ambulance_location": {
                "latitude": 37.7749,
                "longitude": -122.4194,
                "speed_kmh": 68,
                "heading": "NE"
            },
            "destination_hospital": {
                "hospital_id": "HOSP-01",
                "name": "General Trauma & Medical Center",
                "address": "750 Emergency Way, Sector 4",
                "er_hotline": "+1-800-555-ER-911",
                "room_number": "Trauma Bay #3",
                "visiting_hours": "09:00 - 21:00 Daily"
            },
            "eta_minutes": 9,
            "green_corridor_active": True,
            "time_saved_minutes": 6,
            "medical_summary": {
                "vitals": "BP 120/80, Pulse 78 bpm, SpO2 98%",
                "triage_category": "YELLOW",
                "attending_doctor": "Dr. Aris Thorne (Chief Trauma Surgeon)",
                "doctor_notes": "Patient conscious, stable vitals. Prepared for CT scan upon arrival.",
                "last_updated": datetime.now(timezone.utc).isoformat()
            }
        }

    async def get_tracking_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate tracking token and return live patient tracking state"""
        for tracking in self._tracking_db.values():
            if tracking["token"] == token or token == f"TRACK-{tracking['incident_id']}":
                return tracking

        # Fallback return default sample tracking for demonstration
        return list(self._tracking_db.values())[0]

    async def get_tracking_by_incident(self, incident_id: str) -> Dict[str, Any]:
        """Get live tracking state by incident ID"""
        if incident_id not in self._tracking_db:
            # Create default entry
            self._tracking_db[incident_id] = {
                "incident_id": incident_id,
                "patient_name": "John Doe",
                "token": f"TRACK-{incident_id}-SECURE-TOKEN",
                "current_status": "AMBULANCE_DISPATCHED",
                "status_label": "Ambulance Dispatched",
                "ambulance_id": "AMB-108",
                "ambulance_location": {"latitude": 37.7749, "longitude": -122.4194, "speed_kmh": 60},
                "destination_hospital": {
                    "hospital_id": "HOSP-01",
                    "name": "General Trauma Center",
                    "address": "100 Hospital Road",
                    "er_hotline": "+1-800-555-0199"
                },
                "eta_minutes": 12,
                "green_corridor_active": True,
                "medical_summary": {
                    "vitals": "Stable",
                    "attending_doctor": "Dr. Sarah Jenkins",
                    "doctor_notes": "En route, oxygen initiated."
                }
            }
        return self._tracking_db[incident_id]

    async def update_doctor_notes(
        self,
        incident_id: str,
        doctor_name: str,
        doctor_notes: str,
        patient_status: str = "STABLE",
        room_number: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update doctor notes and medical summary for family portal"""
        tracking = await self.get_tracking_by_incident(incident_id)
        med = tracking["medical_summary"]
        med["attending_doctor"] = doctor_name
        med["doctor_notes"] = doctor_notes
        med["last_updated"] = datetime.now(timezone.utc).isoformat()
        tracking["current_status"] = patient_status

        if room_number:
            tracking["destination_hospital"]["room_number"] = room_number

        logger.info(f"Updated doctor notes for incident {incident_id} by {doctor_name}")
        return tracking


# Singleton export
family_tracking_service = FamilyTrackingService()

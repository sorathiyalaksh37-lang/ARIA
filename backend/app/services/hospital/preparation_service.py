"""
Hospital Preparation Service
Orchestrates pre-arrival preparation checklists for incoming emergency patients,
tracks staff check-off progress, checks completion time, and alerts on missed critical items.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.services.hospital.checklist_templates import CHECKLIST_TEMPLATES

logger = logging.getLogger(__name__)


class HospitalPreparationService:
    """Manages hospital pre-arrival preparation checklists and staff readiness tracking."""

    def __init__(self):
        # Active preparation records: incident_id -> Prep Record
        self._prep_db: Dict[str, Dict[str, Any]] = {}
        self._seed_default_prep()

    def _seed_default_prep(self):
        sample_id = "INC-1001"
        template = CHECKLIST_TEMPLATES["TRAUMA"]

        items_state = []
        for idx, item in enumerate(template["items"]):
            items_state.append({
                **item,
                "completed": idx < 4,  # First 4 completed
                "completed_by_staff_id": "STF-902" if idx < 4 else None,
                "completed_at": datetime.utcnow().isoformat() if idx < 4 else None
            })

        self._prep_db[sample_id] = {
            "incident_id": sample_id,
            "hospital_id": "HOSP-01",
            "hospital_name": "General Trauma Center",
            "patient_name": "Michael Miller",
            "emergency_category": "TRAUMA",
            "template_id": template["template_id"],
            "template_name": template["name"],
            "eta_minutes": 7,
            "created_at": datetime.utcnow().isoformat(),
            "items": items_state,
            "is_completed": False
        }

    async def generate_checklist(
        self,
        incident_id: str,
        emergency_category: str = "TRAUMA",
        hospital_id: str = "HOSP-01",
        hospital_name: str = "General Trauma Center",
        patient_name: str = "Emergency Patient",
        eta_minutes: int = 10
    ) -> Dict[str, Any]:
        """Auto-generate pre-arrival preparation checklist for an incoming patient"""
        cat_upper = emergency_category.upper()
        template = CHECKLIST_TEMPLATES.get(cat_upper, CHECKLIST_TEMPLATES["TRAUMA"])

        items_state = []
        for item in template["items"]:
            items_state.append({
                **item,
                "completed": False,
                "completed_by_staff_id": None,
                "completed_at": None
            })

        prep_record = {
            "incident_id": incident_id,
            "hospital_id": hospital_id,
            "hospital_name": hospital_name,
            "patient_name": patient_name,
            "emergency_category": cat_upper,
            "template_id": template["template_id"],
            "template_name": template["name"],
            "target_prep_time_minutes": template["target_prep_time_minutes"],
            "eta_minutes": eta_minutes,
            "created_at": datetime.utcnow().isoformat(),
            "items": items_state,
            "is_completed": False
        }

        self._prep_db[incident_id] = prep_record
        logger.info(f"Generated pre-arrival checklist for incident {incident_id} ({cat_upper}) at {hospital_name}")
        return await self.get_checklist(incident_id)

    async def get_checklist(self, incident_id: str) -> Dict[str, Any]:
        """Get live pre-arrival preparation checklist and readiness metrics"""
        if incident_id not in self._prep_db:
            # Auto-generate trauma default if not existing
            await self.generate_checklist(incident_id=incident_id)

        prep = self._prep_db[incident_id]
        items = prep["items"]

        total_count = len(items)
        completed_count = sum(1 for i in items if i["completed"])
        progress_percentage = round((completed_count / total_count * 100.0), 1) if total_count > 0 else 0.0

        # Check missed critical items
        missed_critical = [i for i in items if i["is_critical"] and not i["completed"]]
        critical_alert = len(missed_critical) > 0 and prep["eta_minutes"] <= 5

        prep_status = "READY" if completed_count == total_count else "IN_PROGRESS"

        return {
            **prep,
            "total_items": total_count,
            "completed_items": completed_count,
            "progress_percentage": progress_percentage,
            "prep_status": prep_status,
            "missed_critical_count": len(missed_critical),
            "missed_critical_items": missed_critical,
            "critical_warning_alert": critical_alert
        }

    async def toggle_item(
        self,
        incident_id: str,
        item_id: str,
        completed: bool,
        staff_id: str = "STF-902"
    ) -> Dict[str, Any]:
        """Toggle checklist item completion state with staff ID timestamp logging"""
        if incident_id not in self._prep_db:
            await self.generate_checklist(incident_id=incident_id)

        prep = self._prep_db[incident_id]
        for item in prep["items"]:
            if item["item_id"] == item_id:
                item["completed"] = completed
                item["completed_by_staff_id"] = staff_id if completed else None
                item["completed_at"] = datetime.utcnow().isoformat() if completed else None
                break

        # Check if all completed
        if all(i["completed"] for i in prep["items"]):
            prep["is_completed"] = True
            prep["completed_at"] = datetime.utcnow().isoformat()

        logger.info(f"Updated item {item_id} (completed={completed}) by staff {staff_id} for incident {incident_id}")
        return await self.get_checklist(incident_id)

    async def get_hospital_summary(self, hospital_id: str = "HOSP-01") -> Dict[str, Any]:
        """Get pre-arrival readiness metrics for all incoming patients at a hospital"""
        active_preps = [p for p in self._prep_db.values() if p["hospital_id"] == hospital_id]
        return {
            "hospital_id": hospital_id,
            "active_incoming_patients_count": len(active_preps),
            "incoming_preps": active_preps
        }


# Singleton export
hospital_prep_service = HospitalPreparationService()

"""
Family Notification Service
Dispatches automatic milestone updates to family contacts via SMS, Email, WhatsApp, and Voice calls.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

from app.services.family.contact_service import family_contact_service

logger = logging.getLogger(__name__)

MILESTONES = {
    "INCIDENT_CREATED": {
        "title": "🚨 Emergency Alert: ARIA Response Activated",
        "severity": "CRITICAL",
        "description": "An emergency response has been dispatched for your family member."
    },
    "AMBULANCE_ARRIVED": {
        "title": "🚑 Paramedics Arrived on Scene",
        "severity": "IMPORTANT",
        "description": "Emergency responders have arrived on scene and are providing immediate care."
    },
    "PATIENT_EN_ROUTE": {
        "title": "🚨 En Route to Hospital",
        "severity": "IMPORTANT",
        "description": "Ambulance is en route to hospital with live traffic corridor enabled."
    },
    "HOSPITAL_ARRIVED": {
        "title": "🏥 Reached Hospital Emergency Room",
        "severity": "SUCCESS",
        "description": "Patient has arrived at hospital trauma center and admitted for care."
    },
    "STATUS_CHANGED": {
        "title": "📋 Patient Medical Status Update",
        "severity": "INFO",
        "description": "Updated medical assessment from attending medical team."
    },
    "VISITATION_READY": {
        "title": "💚 Family Visitation Now Permitted",
        "severity": "SUCCESS",
        "description": "Family members may now visit the patient at hospital."
    }
}


class FamilyNotificationService:
    """Dispatches multi-channel notifications and logs communication history."""

    def __init__(self):
        # Notification history audit log: incident_id -> List of dispatched notifications
        self._history_db: Dict[str, List[Dict[str, Any]]] = {}

        # Default sample history
        self._seed_default_history()

    def _seed_default_history(self):
        sample_id = "INC-1001"
        self._history_db[sample_id] = [
            {
                "notification_id": "NOTIF-101",
                "incident_id": sample_id,
                "event_type": "INCIDENT_CREATED",
                "recipient_name": "Sarah Miller",
                "recipient_contact": "+1-555-019-2834",
                "channel": "WHATSAPP",
                "status": "DELIVERED",
                "summary": "🚨 Emergency alert dispatched with live tracking link.",
                "timestamp": datetime.utcnow().isoformat()
            },
            {
                "notification_id": "NOTIF-102",
                "incident_id": sample_id,
                "event_type": "AMBULANCE_ARRIVED",
                "recipient_name": "Sarah Miller",
                "recipient_contact": "+1-555-019-2834",
                "channel": "WHATSAPP",
                "status": "DELIVERED",
                "summary": "🚑 Paramedics arrived on scene at 19:05.",
                "timestamp": datetime.utcnow().isoformat()
            }
        ]

    async def notify_milestone(
        self,
        incident_id: str,
        event_type: str,
        hospital_name: str = "General Trauma Center",
        eta_minutes: int = 12,
        patient_status: str = "STABLE",
        doctor_notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Dispatch automatic notifications to all opted-in family contacts for an incident"""
        contacts = await family_contact_service.get_contacts(incident_id)

        if not contacts:
            return {"error": f"No registered family contacts for incident {incident_id}"}

        milestone_info = MILESTONES.get(event_type, {
            "title": f"Update: {event_type}",
            "severity": "INFO",
            "description": "Status update."
        })

        tracking_link = f"https://aria-emergency.com/family-portal?incident_id={incident_id}&token=TRACK-{incident_id}"

        dispatched_logs = []

        for c in contacts:
            if not c.get("opt_in_notifications", True):
                continue

            channel = c.get("preferred_channel", "SMS").upper()
            privacy = c.get("privacy_level", "FULL_MEDICAL")

            # Content tailoring based on privacy consent tier
            if privacy == "EMERGENCY_ONLY":
                medical_details = "Basic status: In transport / Admitted."
            else:
                medical_details = f"Patient Status: {patient_status}. " + (f"Doctor Notes: {doctor_notes}" if doctor_notes else "")

            sms_text = (
                f"🚨 ARIA FAMILY UPDATE ({milestone_info['title']}):\n"
                f"Hospital: {hospital_name} | ETA: {eta_minutes} mins\n"
                f"{medical_details}\n"
                f"Live Tracking & Status Link: {tracking_link}"
            )

            email_html = (
                f"<h2>{milestone_info['title']}</h2>"
                f"<p><strong>Hospital Destination:</strong> {hospital_name}</p>"
                f"<p><strong>Estimated Arrival Time:</strong> {eta_minutes} minutes</p>"
                f"<p><strong>Medical Overview:</strong> {medical_details}</p>"
                f"<p><a href='{tracking_link}'>Click here to open ARIA Family Live Tracking Portal</a></p>"
            )

            whatsapp_payload = {
                "recipient": c["phone"],
                "template": "family_emergency_update_v1",
                "body": sms_text,
                "tracking_url": tracking_link,
                "eta_minutes": eta_minutes,
                "hospital": hospital_name
            }

            voice_script = (
                f"Hello {c['name']}, this is an automated emergency update from ARIA for incident {incident_id}. "
                f"{milestone_info['description']} The patient is being transported to {hospital_name} with an ETA of {eta_minutes} minutes."
            )

            notif_record = {
                "notification_id": f"NOTIF-{len(self._history_db.get(incident_id, [])) + 101}",
                "incident_id": incident_id,
                "event_type": event_type,
                "recipient_name": c["name"],
                "recipient_contact": c["phone"] if channel in ["SMS", "WHATSAPP", "VOICE"] else c["email"],
                "channel": channel,
                "status": "DELIVERED",
                "summary": milestone_info['title'],
                "payload_preview": {
                    "sms": sms_text if channel == "SMS" else None,
                    "email": email_html if channel == "EMAIL" else None,
                    "whatsapp": whatsapp_payload if channel == "WHATSAPP" else None,
                    "voice": voice_script if channel == "VOICE" else None
                },
                "timestamp": datetime.utcnow().isoformat()
            }

            if incident_id not in self._history_db:
                self._history_db[incident_id] = []
            self._history_db[incident_id].append(notif_record)
            dispatched_logs.append(notif_record)

        logger.info(f"Dispatched milestone {event_type} to {len(dispatched_logs)} contacts for incident {incident_id}")

        return {
            "incident_id": incident_id,
            "event_type": event_type,
            "contacts_notified_count": len(dispatched_logs),
            "dispatched_logs": dispatched_logs,
            "tracking_link": tracking_link
        }

    async def get_history(self, incident_id: str) -> List[Dict[str, Any]]:
        """Get full notification communication history for an incident"""
        return self._history_db.get(incident_id, [])


# Singleton export
family_notification_service = FamilyNotificationService()

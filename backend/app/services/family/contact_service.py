"""
Family Contact Service
Manages emergency contacts for patients, primary/secondary designation,
communication preferences (SMS, Email, WhatsApp, Voice), languages, and privacy consent levels.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class FamilyContactService:
    """Manages family emergency contacts, communication preferences, and patient consent."""

    def __init__(self):
        # In-memory store: incident_id -> List of contact records
        self._contacts_db: Dict[str, List[Dict[str, Any]]] = {}

        # Default sample contacts for demonstration
        self._seed_default_contacts()

    def _seed_default_contacts(self):
        sample_incident = "INC-1001"
        self._contacts_db[sample_incident] = [
            {
                "contact_id": "CONT-101",
                "incident_id": sample_incident,
                "name": "Sarah Miller",
                "phone": "+1-555-019-2834",
                "email": "sarah.miller@example.com",
                "relationship": "Spouse",
                "is_primary": True,
                "preferred_channel": "WHATSAPP",
                "language": "en",
                "privacy_level": "FULL_MEDICAL",
                "opt_in_notifications": True,
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "contact_id": "CONT-102",
                "incident_id": sample_incident,
                "name": "David Miller",
                "phone": "+1-555-014-9821",
                "email": "david.m@example.com",
                "relationship": "Brother",
                "is_primary": False,
                "preferred_channel": "SMS",
                "language": "en",
                "privacy_level": "EMERGENCY_ONLY",
                "opt_in_notifications": True,
                "created_at": datetime.utcnow().isoformat()
            }
        ]

    async def add_contact(
        self,
        incident_id: str,
        name: str,
        phone: str,
        email: str,
        relationship: str,
        is_primary: bool = False,
        preferred_channel: str = "WHATSAPP",
        language: str = "en",
        privacy_level: str = "FULL_MEDICAL"
    ) -> Dict[str, Any]:
        """Add a new family emergency contact to an incident"""
        if incident_id not in self._contacts_db:
            self._contacts_db[incident_id] = []

        # If marking as primary, unmark existing primary contacts for this incident
        if is_primary:
            for c in self._contacts_db[incident_id]:
                c["is_primary"] = False

        contact_id = f"CONT-{len(self._contacts_db[incident_id]) + 101}"
        record = {
            "contact_id": contact_id,
            "incident_id": incident_id,
            "name": name,
            "phone": phone,
            "email": email,
            "relationship": relationship,
            "is_primary": is_primary,
            "preferred_channel": preferred_channel.upper(),
            "language": language,
            "privacy_level": privacy_level.upper(),  # EMERGENCY_ONLY or FULL_MEDICAL
            "opt_in_notifications": True,
            "created_at": datetime.utcnow().isoformat()
        }

        self._contacts_db[incident_id].append(record)
        logger.info(f"Added family contact {contact_id} ({name}) for incident {incident_id}")
        return record

    async def get_contacts(self, incident_id: str) -> List[Dict[str, Any]]:
        """Get all registered family contacts for an incident"""
        return self._contacts_db.get(incident_id, [])

    async def get_primary_contact(self, incident_id: str) -> Optional[Dict[str, Any]]:
        """Get primary family contact for an incident"""
        contacts = await self.get_contacts(incident_id)
        for c in contacts:
            if c.get("is_primary"):
                return c
        return contacts[0] if contacts else None

    async def update_consent(
        self,
        incident_id: str,
        contact_id: str,
        opt_in: bool,
        privacy_level: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update consent settings for a family contact"""
        contacts = await self.get_contacts(incident_id)
        for c in contacts:
            if c["contact_id"] == contact_id:
                c["opt_in_notifications"] = opt_in
                if privacy_level:
                    c["privacy_level"] = privacy_level.upper()
                return c

        return {"error": f"Contact {contact_id} not found"}


# Singleton export
family_contact_service = FamilyContactService()

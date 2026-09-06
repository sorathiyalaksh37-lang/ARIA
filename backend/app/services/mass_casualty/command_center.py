"""
Mass Casualty Command Center Module
Maintains real-time incident dashboard state, timeline log, communication log, and role assignments.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from app.services.mass_casualty.triage import triage_manager
from app.services.mass_casualty.coordinator import mass_casualty_coordinator

logger = logging.getLogger(__name__)


class CommandCenterManager:
    """Manages command center state, timeline logs, communication logs, and operational overview."""

    def __init__(self):
        self._timeline_log: List[Dict[str, Any]] = [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "event": "Mass Casualty Mode Activated",
                "severity": "CRITICAL",
                "author": "Incident Commander"
            }
        ]
        self._communication_log: List[Dict[str, Any]] = [
            {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "recipient": "All Regional Hospitals",
                "type": "HOSPITAL_SURGE_ALERT",
                "message": "Level 2 Mass Casualty Alert dispatched to 3 regional trauma centers."
            }
        ]

    def add_timeline_event(self, event: str, severity: str = "INFO", author: str = "Command Center") -> Dict[str, Any]:
        """Log a timeline event"""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "event": event,
            "severity": severity,
            "author": author
        }
        self._timeline_log.append(entry)
        return entry

    def add_communication_log(self, recipient: str, comm_type: str, message: str) -> Dict[str, Any]:
        """Log a communication entry"""
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "recipient": recipient,
            "type": comm_type,
            "message": message
        }
        self._communication_log.append(entry)
        return entry

    async def get_command_center_summary(self) -> Dict[str, Any]:
        """
        Return comprehensive command center summary:
        - MCI Status
        - Triage Counts (RED, YELLOW, GREEN, BLACK)
        - Hospital Distribution
        - Blood Bank Reservations
        - Timeline Log
        - Communication Log
        """
        triage_summary = await triage_manager.get_triage_summary()
        victims = await triage_manager.get_all_victims()
        distribution = await mass_casualty_coordinator.calculate_hospital_distribution(triage_summary)
        blood_res = await mass_casualty_coordinator.coordinate_blood_bank_reservations(triage_summary["total_victims"])
        comms = await mass_casualty_coordinator.generate_mass_communications(
            triage_summary.get("incident_id") or "MCI-INC-101",
            triage_summary["total_victims"],
            triage_summary
        )

        return {
            "mci_active": triage_manager.is_mci_active(),
            "incident_id": triage_summary.get("incident_id") or "MCI-INC-101",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "triage_summary": triage_summary,
            "total_victims_tagged": len(victims),
            "victims_list": victims,
            "hospital_distribution": distribution,
            "blood_bank_reservations": blood_res,
            "mass_communications": comms,
            "timeline_log": self._timeline_log[-15:],
            "communication_log": self._communication_log[-15:]
        }


# Singleton export
command_center_manager = CommandCenterManager()

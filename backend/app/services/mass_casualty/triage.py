"""
Mass Casualty Triage Module
Implements START (Simple Triage and Rapid Treatment) algorithm, digital/physical barcode tagging,
auto-activation detection (>10 victims), and triage officer management.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

TRIAGE_CATEGORIES = {
    "RED": {
        "label": "IMMEDIATE (RED)",
        "color": "#ef4444",
        "description": "Life-threatening injuries requiring immediate medical intervention",
        "priority": 1
    },
    "YELLOW": {
        "label": "DELAYED (YELLOW)",
        "color": "#f59e0b",
        "description": "Serious injuries requiring hospital care within 1-2 hours",
        "priority": 2
    },
    "GREEN": {
        "label": "MINOR (GREEN)",
        "color": "#10b981",
        "description": "Walking wounded with minor cuts, contusions, or minor sprains",
        "priority": 3
    },
    "BLACK": {
        "label": "DECEASED / EXPECTANT (BLACK)",
        "color": "#1e293b",
        "description": "No breathing after airway positioning or fatal non-survivable trauma",
        "priority": 4
    }
}


class TriageManager:
    """Manages START triage categorization, victim barcode tags, and auto-activation."""

    def __init__(self):
        self._mci_active: bool = False
        self._mci_incident_id: Optional[str] = None
        self._victims_db: Dict[str, Dict[str, Any]] = {}
        self._triage_officer: Optional[str] = "Officer James Vance (Badge #402)"

    def check_auto_activation(self, victim_count: int, nearby_incidents_count: int = 1) -> bool:
        """Auto-activate Mass Casualty Mode if victim_count > 10 or multiple cluster incidents"""
        should_activate = victim_count >= 10 or nearby_incidents_count >= 3
        if should_activate and not self._mci_active:
            self.activate_mci(
                incident_id="MCI-CLUSTER-AUTO-01",
                reason=f"Auto-activated: Victim count ({victim_count}) >= 10 or high incident density"
            )
        return should_activate

    def activate_mci(self, incident_id: str, reason: str = "Manual Activation by Coordinator") -> Dict[str, Any]:
        """Activate Mass Casualty Mode"""
        self._mci_active = True
        self._mci_incident_id = incident_id
        logger.warning(f"🚨 MASS CASUALTY MODE ACTIVATED for incident {incident_id}. Reason: {reason}")
        return {
            "mci_active": True,
            "incident_id": incident_id,
            "activation_timestamp": datetime.utcnow().isoformat(),
            "reason": reason,
            "triage_officer": self._triage_officer
        }

    def deactivate_mci(self) -> Dict[str, Any]:
        """Deactivate Mass Casualty Mode"""
        self._mci_active = False
        logger.info("Mass Casualty Mode deactivated. Returning to standard operations.")
        return {
            "mci_active": False,
            "deactivation_timestamp": datetime.utcnow().isoformat()
        }

    def is_mci_active(self) -> bool:
        return self._mci_active

    def evaluate_start_triage(
        self,
        can_walk: bool,
        breathing_rate_bpm: Optional[int],
        has_radial_pulse: bool,
        follows_simple_commands: bool
    ) -> str:
        """
        START (Simple Triage and Rapid Treatment) Algorithm Logic:
        1. Can walk? -> GREEN
        2. Breathing rate? None after reposition -> BLACK | >30 bpm -> RED
        3. Pulse / Perfusion? No pulse -> RED
        4. Mental status? Cannot follow simple commands -> RED | Follows commands -> YELLOW
        """
        if can_walk:
            return "GREEN"

        if breathing_rate_bpm is None or breathing_rate_bpm == 0:
            return "BLACK"

        if breathing_rate_bpm > 30:
            return "RED"

        if not has_radial_pulse:
            return "RED"

        if not follows_simple_commands:
            return "RED"

        return "YELLOW"

    async def register_victim_triage(
        self,
        triage_category: str,  # RED, YELLOW, GREEN, BLACK
        injury_description: str,
        location: Dict[str, float],
        age_group: str = "adult",
        assigned_hospital_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Tag and register a victim into the Mass Casualty Tracking System"""
        cat_key = triage_category.upper()
        if cat_key not in TRIAGE_CATEGORIES:
            cat_key = "YELLOW"

        tag_seq = len(self._victims_db) + 1
        victim_tag_id = f"MCI-TAG-{cat_key}-{tag_seq:03d}"

        victim_record = {
            "victim_tag_id": victim_tag_id,
            "triage_category": cat_key,
            "triage_label": TRIAGE_CATEGORIES[cat_key]["label"],
            "color": TRIAGE_CATEGORIES[cat_key]["color"],
            "priority": TRIAGE_CATEGORIES[cat_key]["priority"],
            "injury_description": injury_description,
            "age_group": age_group,
            "location": location,
            "assigned_hospital_id": assigned_hospital_id,
            "assigned_ambulance_id": None,
            "transport_status": "WAITING_FOR_AMBULANCE",  # WAITING_FOR_AMBULANCE, IN_TRANSIT, DELIVERED
            "triage_timestamp": datetime.utcnow().isoformat(),
            "triage_officer": self._triage_officer
        }

        self._victims_db[victim_tag_id] = victim_record
        logger.info(f"Registered victim triage tag: {victim_tag_id} ({cat_key})")
        return victim_record

    async def get_all_victims(self) -> List[Dict[str, Any]]:
        """Return all registered victims sorted by triage priority (RED first)"""
        records = list(self._victims_db.values())
        records.sort(key=lambda x: x.get("priority", 99))
        return records

    async def get_triage_summary(self) -> Dict[str, Any]:
        """Compute tally breakdown by triage color category"""
        counts = {"RED": 0, "YELLOW": 0, "GREEN": 0, "BLACK": 0}
        for v in self._victims_db.values():
            cat = v.get("triage_category", "YELLOW")
            if cat in counts:
                counts[cat] += 1

        total = len(self._victims_db)
        return {
            "mci_active": self._mci_active,
            "incident_id": self._mci_incident_id,
            "total_victims": total,
            "category_counts": counts,
            "critical_immediate_red": counts["RED"],
            "triage_officer": self._triage_officer
        }


# Singleton export
triage_manager = TriageManager()

"""
Mass Casualty Package
Exposes triage_manager, mass_casualty_coordinator, and command_center_manager.
"""

from app.services.mass_casualty.triage import triage_manager, TriageManager
from app.services.mass_casualty.coordinator import mass_casualty_coordinator, MassCasualtyCoordinator
from app.services.mass_casualty.command_center import command_center_manager, CommandCenterManager

__all__ = [
    "triage_manager",
    "TriageManager",
    "mass_casualty_coordinator",
    "MassCasualtyCoordinator",
    "command_center_manager",
    "CommandCenterManager",
]

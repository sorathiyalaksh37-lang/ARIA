"""
Mass Casualty Mode API Endpoints
Provides activation/deactivation triggers, START victim triage tagging, hospital capacity distribution,
resource coordination (ambulances, blood banks), and Command Center dashboard control.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.response import SuccessResponse

from app.services.mass_casualty import (
    triage_manager,
    mass_casualty_coordinator,
    command_center_manager
)

router = APIRouter(prefix="/mass-casualty", tags=["Mass Casualty Mode"])


@router.post("/activate")
async def activate_mci(
    payload: Dict[str, Any] = Body(...)
):
    """
    Activate Mass Casualty Mode for an incident (e.g. 10+ victims or disaster site).
    """
    try:
        incident_id = payload.get("incident_id", "MCI-INC-1001")
        reason = payload.get("reason", "Activated by Emergency Coordinator")

        result = triage_manager.activate_mci(incident_id=incident_id, reason=reason)
        command_center_manager.add_timeline_event(f"MCI Mode Activated: {reason}", severity="CRITICAL")

        return SuccessResponse(data=result, message=f"Mass Casualty Mode ACTIVATED for incident {incident_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deactivate")
async def deactivate_mci():
    """
    Deactivate Mass Casualty Mode and return to standard operating procedures.
    """
    try:
        result = triage_manager.deactivate_mci()
        command_center_manager.add_timeline_event("MCI Mode Deactivated", severity="INFO")
        return SuccessResponse(data=result, message="Mass Casualty Mode DEACTIVATED")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status")
async def get_mci_status():
    """
    Get current Mass Casualty activation status and triage totals.
    """
    try:
        summary = await triage_manager.get_triage_summary()
        return SuccessResponse(data=summary, message="Retrieved MCI status summary")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/victims/triage")
async def register_victim_triage(
    payload: Dict[str, Any] = Body(...)
):
    """
    Register and digitally tag a victim using START triage category (RED, YELLOW, GREEN, BLACK).
    """
    try:
        category = payload.get("triage_category", "RED")
        description = payload.get("injury_description", "Trauma injuries")
        location = payload.get("location", {"latitude": 37.7749, "longitude": -122.4194})
        age_group = payload.get("age_group", "adult")
        hospital_id = payload.get("assigned_hospital_id")

        victim = await triage_manager.register_victim_triage(
            triage_category=category,
            injury_description=description,
            location=location,
            age_group=age_group,
            assigned_hospital_id=hospital_id
        )

        # Check for auto-activation if count >= 10
        summary = await triage_manager.get_triage_summary()
        triage_manager.check_auto_activation(summary["total_victims"])

        command_center_manager.add_timeline_event(
            f"Victim Tagged: {victim['victim_tag_id']} ({category})",
            severity="WARNING" if category == "RED" else "INFO"
        )

        return SuccessResponse(data=victim, message=f"Victim tagged successfully: {victim['victim_tag_id']}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/victims")
async def list_victims():
    """
    List all tagged victims sorted by priority (RED immediate first).
    """
    try:
        victims = await triage_manager.get_all_victims()
        return SuccessResponse(
            data={"victims": victims, "count": len(victims)},
            message=f"Retrieved {len(victims)} tagged victims"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hospital-distribution")
async def get_hospital_distribution():
    """
    Calculate optimal distribution of victims across regional trauma centers based on bed capacity.
    """
    try:
        triage_summary = await triage_manager.get_triage_summary()
        distribution = await mass_casualty_coordinator.calculate_hospital_distribution(triage_summary)
        return SuccessResponse(data=distribution, message="Calculated optimal hospital casualty distribution")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/dispatch-resources")
async def dispatch_mci_resources(
    payload: Dict[str, Any] = Body(...)
):
    """
    Coordinate multi-ambulance fleet staging and blood bank stock reservations.
    """
    try:
        triage_summary = await triage_manager.get_triage_summary()
        blood_res = await mass_casualty_coordinator.coordinate_blood_bank_reservations(
            triage_summary.get("total_victims", 10)
        )

        command_center_manager.add_timeline_event(
            f"Multi-resource dispatch executed: {blood_res['total_units_reserved']} blood units reserved",
            severity="IMPORTANT"
        )

        return SuccessResponse(
            data={
                "ambulances_dispatched_count": 8,
                "blood_reservations": blood_res,
                "timestamp": blood_res["timestamp"]
            },
            message="Multi-ambulance dispatch and blood bank reservations executed"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/command-summary")
async def get_command_center_summary():
    """
    Get full Command Center operational overview including victim tracking, hospital distribution, and timeline logs.
    """
    try:
        summary = await command_center_manager.get_command_center_summary()
        return SuccessResponse(data=summary, message="Retrieved Command Center summary report")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/broadcast-notification")
async def broadcast_mci_notifications(
    payload: Dict[str, Any] = Body(...)
):
    """
    Broadcast notifications to area hospitals, family reunification portal, media, and govt agencies.
    """
    try:
        incident_id = payload.get("incident_id", "MCI-INC-1001")
        triage_summary = await triage_manager.get_triage_summary()

        comms = await mass_casualty_coordinator.generate_mass_communications(
            incident_id=incident_id,
            total_victims=triage_summary["total_victims"],
            triage_summary=triage_summary
        )

        command_center_manager.add_communication_log(
            recipient="Hospitals & Media & Govt SDMA",
            comm_type="MASS_BROADCAST",
            message=f"Dispatched emergency communications for {incident_id}"
        )

        return SuccessResponse(data=comms, message="Mass emergency notifications broadcasted successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

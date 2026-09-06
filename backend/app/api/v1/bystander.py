"""
Bystander First Aid System API Endpoints
Provides multi-language first aid protocols, bystander resource locator (AEDs, CPR civilians),
multi-channel instruction delivery, scene confirmation, and EMS escalation.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.response import SuccessResponse

from app.services.bystander import (
    protocol_manager,
    bystander_location_service,
    bystander_service
)

router = APIRouter(prefix="/bystander", tags=["Bystander First Aid"])


@router.get("/protocols")
async def list_protocols(
    lang: str = Query("en", description="Target language code: en, hi, mr, ta, te, bn")
):
    """
    List all available first aid protocols translated into requested language.
    Supported languages: English (en), Hindi (hi), Marathi (mr), Tamil (ta), Telugu (te), Bengali (bn).
    """
    try:
        protocols = protocol_manager.list_all_protocols(lang=lang)
        return SuccessResponse(
            data={
                "protocols": protocols,
                "language": lang,
                "count": len(protocols)
            },
            message=f"Retrieved {len(protocols)} first aid protocols in language '{lang}'"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/protocols/{protocol_id}")
async def get_protocol_detail(
    protocol_id: str,
    lang: str = Query("en", description="Language code: en, hi, mr, ta, te, bn")
):
    """
    Get detailed step-by-step instructions, compression rate, video URL, and warnings for a protocol.
    """
    protocol = protocol_manager.get_protocol(protocol_id, lang=lang)
    if not protocol:
        raise HTTPException(status_code=404, detail=f"Protocol '{protocol_id}' not found")

    return SuccessResponse(
        data=protocol,
        message=f"Retrieved protocol '{protocol_id}' in language '{lang}'"
    )


@router.get("/nearby-resources")
async def get_nearby_resources(
    latitude: float = Query(37.7749, description="Incident latitude"),
    longitude: float = Query(-122.4194, description="Incident longitude"),
    radius_km: float = Query(3.0, description="Search radius in kilometers")
):
    """
    Find nearby CPR-certified civilians, AED defibrillator units, pharmacies, and emergency clinics.
    Includes Google Maps turn-by-turn walking links and AED access codes.
    """
    try:
        resources = await bystander_location_service.find_nearby_resources(
            incident_lat=latitude,
            incident_lng=longitude,
            radius_km=radius_km
        )
        return SuccessResponse(
            data=resources,
            message="Nearby bystander resources and AED locations located"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/deliver-instructions")
async def deliver_instructions(
    payload: Dict[str, Any] = Body(...)
):
    """
    Deliver first aid instructions across 5 channels: SMS, Voice call, Web guide, WhatsApp, and App Push.
    """
    try:
        incident_id = payload.get("incident_id", "INC-1001")
        protocol_id = payload.get("protocol_id", "cpr")
        bystander_phone = payload.get("bystander_phone", "+91-9876543210")
        language = payload.get("language", "en")
        lat = payload.get("latitude", 37.7749)
        lng = payload.get("longitude", -122.4194)

        result = await bystander_service.deliver_first_aid_instructions(
            incident_id=incident_id,
            protocol_id=protocol_id,
            bystander_phone=bystander_phone,
            language=language,
            incident_lat=lat,
            incident_lng=lng
        )

        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])

        return SuccessResponse(
            data=result,
            message="Multi-channel first aid instructions dispatched successfully"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/confirm-arrival")
async def confirm_arrival(
    payload: Dict[str, Any] = Body(...)
):
    """
    Confirm bystander arrival at victim's scene location.
    """
    try:
        session_id = payload.get("session_id", "BS-INC-1001-0000")
        res = await bystander_service.confirm_bystander_arrival(session_id)
        return SuccessResponse(data=res, message=res["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/confirm-action")
async def confirm_action(
    payload: Dict[str, Any] = Body(...)
):
    """
    Log a completed first aid step/action (e.g. CPR started, Tourniquet applied).
    """
    try:
        session_id = payload.get("session_id", "BS-INC-1001-0000")
        action_step = payload.get("action_step", "CPR Chest Compressions Started")
        notes = payload.get("notes")

        res = await bystander_service.confirm_action_performed(session_id, action_step, notes)
        return SuccessResponse(data=res, message=res["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update-status")
async def update_victim_status(
    payload: Dict[str, Any] = Body(...)
):
    """
    Update victim status (STABLE, UNRESPONSIVE, DETERIORATING, REVIVED).
    Auto-escalates to EMS if unresponsive or deteriorating.
    """
    try:
        session_id = payload.get("session_id", "BS-INC-1001-0000")
        victim_status = payload.get("victim_status", "STABLE")
        notes = payload.get("notes")

        res = await bystander_service.update_victim_status(session_id, victim_status, notes)
        return SuccessResponse(data=res, message=res["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/escalate")
async def escalate_to_ems(
    payload: Dict[str, Any] = Body(...)
):
    """
    Manually trigger high-priority EMS dispatch escalation.
    """
    try:
        session_id = payload.get("session_id", "BS-INC-1001-0000")
        reason = payload.get("reason", "Bystander requested urgent EMS escalation")

        res = await bystander_service.escalate_to_ems(session_id, reason)
        return SuccessResponse(data=res, message="Case escalated to EMS dispatch")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

"""
Family Communication System API Endpoints
Provides contact management, automatic multi-channel notification dispatch,
tokenized patient live tracking, consent management, and doctor update endpoints.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.response import SuccessResponse

from app.services.family import (
    family_contact_service,
    family_notification_service,
    family_tracking_service
)

router = APIRouter(prefix="/family", tags=["Family Communication System"])


@router.post("/contacts")
async def add_family_contact(
    payload: Dict[str, Any] = Body(...)
):
    """
    Register a family emergency contact for an incident.
    Specify primary/secondary status, channel preference (SMS, Email, WhatsApp, Voice),
    language preference, and privacy level (EMERGENCY_ONLY or FULL_MEDICAL).
    """
    try:
        incident_id = payload.get("incident_id", "INC-1001")
        name = payload.get("name", "Jane Doe")
        phone = payload.get("phone", "+1-555-019-2834")
        email = payload.get("email", "jane.doe@example.com")
        relationship = payload.get("relationship", "Spouse")
        is_primary = payload.get("is_primary", False)
        preferred_channel = payload.get("preferred_channel", "WHATSAPP")
        language = payload.get("language", "en")
        privacy_level = payload.get("privacy_level", "FULL_MEDICAL")

        contact = await family_contact_service.add_contact(
            incident_id=incident_id,
            name=name,
            phone=phone,
            email=email,
            relationship=relationship,
            is_primary=is_primary,
            preferred_channel=preferred_channel,
            language=language,
            privacy_level=privacy_level
        )

        return SuccessResponse(data=contact, message=f"Family contact '{name}' added successfully")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/contacts/{incident_id}")
async def get_family_contacts(incident_id: str):
    """
    Get all registered family contacts for an incident.
    """
    try:
        contacts = await family_contact_service.get_contacts(incident_id)
        return SuccessResponse(
            data={"contacts": contacts, "count": len(contacts)},
            message=f"Retrieved {len(contacts)} contacts for incident {incident_id}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/notify-event")
async def notify_family_milestone(
    payload: Dict[str, Any] = Body(...)
):
    """
    Trigger automatic milestone notification to family contacts.
    Milestones: INCIDENT_CREATED, AMBULANCE_ARRIVED, PATIENT_EN_ROUTE, HOSPITAL_ARRIVED, STATUS_CHANGED, VISITATION_READY.
    """
    try:
        incident_id = payload.get("incident_id", "INC-1001")
        event_type = payload.get("event_type", "PATIENT_EN_ROUTE")
        hospital_name = payload.get("hospital_name", "General Trauma Center")
        eta_minutes = payload.get("eta_minutes", 10)
        patient_status = payload.get("patient_status", "STABLE")
        doctor_notes = payload.get("doctor_notes")

        res = await family_notification_service.notify_milestone(
            incident_id=incident_id,
            event_type=event_type,
            hospital_name=hospital_name,
            eta_minutes=eta_minutes,
            patient_status=patient_status,
            doctor_notes=doctor_notes
        )

        if "error" in res:
            raise HTTPException(status_code=400, detail=res["error"])

        return SuccessResponse(data=res, message=f"Notification milestone '{event_type}' dispatched successfully")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tracking/{token}")
async def get_live_tracking(token: str):
    """
    Tokenized public access endpoint for live patient tracking, ETA, hospital info, and doctor updates.
    """
    try:
        tracking = await family_tracking_service.get_tracking_by_token(token)
        if not tracking:
            raise HTTPException(status_code=404, detail="Invalid or expired tracking token")

        return SuccessResponse(data=tracking, message="Live patient tracking retrieved")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/consent")
async def update_family_consent(
    payload: Dict[str, Any] = Body(...)
):
    """
    Update patient privacy & notification consent preferences.
    """
    try:
        incident_id = payload.get("incident_id", "INC-1001")
        contact_id = payload.get("contact_id", "CONT-101")
        opt_in = payload.get("opt_in", True)
        privacy_level = payload.get("privacy_level")

        res = await family_contact_service.update_consent(
            incident_id=incident_id,
            contact_id=contact_id,
            opt_in=opt_in,
            privacy_level=privacy_level
        )

        if "error" in res:
            raise HTTPException(status_code=404, detail=res["error"])

        return SuccessResponse(data=res, message="Consent preferences updated")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{incident_id}")
async def get_notification_history(incident_id: str):
    """
    Get communication history log for an incident.
    """
    try:
        history = await family_notification_service.get_history(incident_id)
        return SuccessResponse(
            data={"history": history, "count": len(history)},
            message=f"Retrieved {len(history)} notification history entries"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/doctor-notes")
async def update_doctor_notes(
    payload: Dict[str, Any] = Body(...)
):
    """
    Update doctor notes and medical summary for family portal.
    """
    try:
        incident_id = payload.get("incident_id", "INC-1001")
        doctor_name = payload.get("doctor_name", "Dr. Aris Thorne")
        doctor_notes = payload.get("doctor_notes", "Patient is in stable condition after evaluation.")
        patient_status = payload.get("patient_status", "STABLE")
        room_number = payload.get("room_number")

        res = await family_tracking_service.update_doctor_notes(
            incident_id=incident_id,
            doctor_name=doctor_name,
            doctor_notes=doctor_notes,
            patient_status=patient_status,
            room_number=room_number
        )

        return SuccessResponse(data=res, message="Doctor notes updated for family portal")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

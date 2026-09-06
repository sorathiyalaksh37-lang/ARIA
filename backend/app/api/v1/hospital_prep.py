"""
Hospital Preparation Checklist API Endpoints
Provides pre-arrival checklist generation, staff check-off tracking,
readiness metric summary, and template access.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.response import SuccessResponse

from app.services.hospital import (
    hospital_prep_service,
    CHECKLIST_TEMPLATES
)

router = APIRouter(prefix="/hospital-prep", tags=["Hospital Preparation Checklist System"])


@router.post("/generate")
async def generate_hospital_prep_checklist(
    payload: Dict[str, Any] = Body(...)
):
    """
    Generate pre-arrival preparation checklist for an incoming emergency patient.
    Emergency categories: TRAUMA, CARDIAC, STROKE, BURN, OBSTETRIC, PEDIATRIC, MASS_CASUALTY.
    """
    try:
        incident_id = payload.get("incident_id", "INC-1001")
        emergency_category = payload.get("emergency_category", "TRAUMA")
        hospital_id = payload.get("hospital_id", "HOSP-01")
        hospital_name = payload.get("hospital_name", "General Trauma Center")
        patient_name = payload.get("patient_name", "Emergency Patient")
        eta_minutes = payload.get("eta_minutes", 10)

        prep = await hospital_prep_service.generate_checklist(
            incident_id=incident_id,
            emergency_category=emergency_category,
            hospital_id=hospital_id,
            hospital_name=hospital_name,
            patient_name=patient_name,
            eta_minutes=eta_minutes
        )

        return SuccessResponse(
            data=prep,
            message=f"Pre-arrival preparation checklist generated for incident {incident_id} ({emergency_category})"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/checklist/{incident_id}")
async def get_prep_checklist(incident_id: str):
    """
    Retrieve active hospital pre-arrival preparation checklist & progress metrics.
    """
    try:
        prep = await hospital_prep_service.get_checklist(incident_id)
        return SuccessResponse(data=prep, message=f"Pre-arrival checklist retrieved for incident {incident_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/check-item")
async def toggle_checklist_item(
    payload: Dict[str, Any] = Body(...)
):
    """
    Toggle item completion state with staff ID and timestamp logging.
    """
    try:
        incident_id = payload.get("incident_id", "INC-1001")
        item_id = payload.get("item_id", "TRM-01")
        completed = payload.get("completed", True)
        staff_id = payload.get("staff_id", "STF-902")

        updated_prep = await hospital_prep_service.toggle_item(
            incident_id=incident_id,
            item_id=item_id,
            completed=completed,
            staff_id=staff_id
        )

        return SuccessResponse(data=updated_prep, message=f"Checklist item '{item_id}' updated")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def list_checklist_templates():
    """
    List all 7 emergency pre-arrival checklist templates.
    """
    try:
        return SuccessResponse(
            data={"templates": list(CHECKLIST_TEMPLATES.values())},
            message=f"Retrieved {len(CHECKLIST_TEMPLATES)} preparation templates"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_hospital_prep_summary(
    hospital_id: str = Query("HOSP-01", description="Hospital ID")
):
    """
    Get readiness summary for all incoming emergency arrivals at hospital.
    """
    try:
        summary = await hospital_prep_service.get_hospital_summary(hospital_id=hospital_id)
        return SuccessResponse(data=summary, message="Hospital pre-arrival summary retrieved")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

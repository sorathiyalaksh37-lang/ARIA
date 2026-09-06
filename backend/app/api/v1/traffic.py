"""
Smart Traffic Light Integration API Endpoints
Provides Green Corridor activation, traffic light signal preemption control,
manual override commands, time savings calculation, and fallback route handling.
"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.response import SuccessResponse

from app.services.traffic import (
    city_traffic_service,
    green_corridor_service
)

router = APIRouter(prefix="/traffic", tags=["Smart Traffic Light Integration"])


@router.post("/corridor/create")
async def create_green_corridor(
    payload: Dict[str, Any] = Body(...)
):
    """
    Activate automatic Green Corridor signal preemption for an active ambulance route.
    """
    try:
        ambulance_id = payload.get("ambulance_id", "AMB-402")
        incident_id = payload.get("incident_id", "INC-1001")
        origin_lat = payload.get("origin_lat", 37.7749)
        origin_lng = payload.get("origin_lng", -122.4194)
        destination_hospital_id = payload.get("destination_hospital_id", "HOSP-01")

        corridor = await green_corridor_service.create_green_corridor(
            ambulance_id=ambulance_id,
            incident_id=incident_id,
            origin_lat=origin_lat,
            origin_lng=origin_lng,
            destination_hospital_id=destination_hospital_id
        )

        return SuccessResponse(
            data=corridor,
            message=f"Green Corridor activated for ambulance {ambulance_id}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/corridor/override")
async def toggle_manual_override(
    payload: Dict[str, Any] = Body(...)
):
    """
    Toggle manual coordinator override to force all traffic signals along route to GREEN.
    """
    try:
        enable_override = payload.get("enable_override", True)
        res = await green_corridor_service.set_manual_override(enable_override)
        return SuccessResponse(data=res, message=res["message"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/corridor/status")
async def get_corridor_status():
    """
    Get active Green Corridor status, traffic light signal node states, and preemption timer.
    """
    try:
        status = await green_corridor_service.get_corridor_status()
        return SuccessResponse(data=status, message="Retrieved Green Corridor live status")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/time-savings")
async def get_time_savings(
    distance_km: float = Query(7.8, description="Route distance in km"),
    normal_stops: int = Query(8, description="Number of normal traffic light stops")
):
    """
    Calculate travel time comparison between normal route and Green Corridor route.
    """
    try:
        savings = await green_corridor_service.calculate_time_savings(
            distance_km=distance_km,
            normal_light_stops=normal_stops
        )
        return SuccessResponse(data=savings, message="Calculated route time savings")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/fallback-route")
async def get_fallback_route():
    """
    Retrieve fallback route with fewest traffic lights if City ATCS API integration fails.
    """
    try:
        fallback = await city_traffic_service.trigger_fallback()
        return SuccessResponse(data=fallback, message="Fallback route retrieved")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/system-health")
async def get_traffic_system_health():
    """
    Check connection status with City Traffic Management System API.
    """
    try:
        health = await city_traffic_service.check_api_status()
        return SuccessResponse(data=health, message="City Traffic API health checked")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

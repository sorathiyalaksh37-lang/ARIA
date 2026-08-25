"""
ARIA Ambulance API Endpoints
Complete ambulance management with real-time GPS tracking and ML ETA prediction
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from geoalchemy2.functions import ST_Distance, ST_DWithin
from geoalchemy2.elements import WKTElement
from datetime import datetime

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.ambulance import Ambulance
from app.models.user import User
from app.schemas.response import StandardResponse
from app.services.ml_service import get_ml_service, MLService
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/ambulances", tags=["Ambulances"])


# ========== Schemas ==========

class LocationQuery(BaseModel):
    """Location for spatial queries."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class NearestAmbulancesRequest(BaseModel):
    """Request for nearest ambulances."""
    location: LocationQuery
    ambulance_type: Optional[str] = Field(None, regex="^(BASIC|ALS|CRITICAL_CARE)$")
    max_distance_km: float = Field(default=30.0, ge=1, le=100)
    severity: Optional[str] = Field(None, regex="^(LOW|MODERATE|CRITICAL)$")
    top_k: int = Field(default=5, ge=1, le=20)


class UpdateLocationRequest(BaseModel):
    """Update ambulance GPS location."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    speed: Optional[float] = Field(None, ge=0, le=200)  # km/h
    heading: Optional[float] = Field(None, ge=0, lt=360)  # degrees


class UpdateStatusRequest(BaseModel):
    """Update ambulance status."""
    status: str = Field(..., regex="^(AVAILABLE|EN_ROUTE|ON_SCENE|TRANSPORTING|AT_HOSPITAL|OFFLINE)$")
    incident_id: Optional[str] = None
    notes: Optional[str] = None


class AmbulanceResponse(BaseModel):
    """Ambulance response model."""
    ambulance_id: str
    registration_number: str
    ambulance_type: str
    status: str
    latitude: float
    longitude: float
    base_location: Optional[str]
    driver_name: Optional[str]
    driver_phone: Optional[str]
    equipment: List[str] = []
    distance_km: Optional[float] = None
    eta_minutes: Optional[float] = None
    
    class Config:
        from_attributes = True


# ========== Endpoints ==========

@router.get("", response_model=StandardResponse)
async def list_ambulances(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    ambulance_type: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all ambulances with filtering and pagination.
    
    - **page**: Page number (default: 1)
    - **page_size**: Results per page (default: 20, max: 100)
    - **ambulance_type**: Filter by type (BASIC, ALS, CRITICAL_CARE)
    - **status**: Filter by status (AVAILABLE, EN_ROUTE, etc.)
    """
    logger.info(f"Listing ambulances - page={page}, page_size={page_size}")
    
    # Build query
    query = select(Ambulance)
    
    # Apply filters
    filters = []
    if ambulance_type:
        filters.append(Ambulance.ambulance_type == ambulance_type)
    if status:
        filters.append(Ambulance.status == status)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Count total
    count_query = select(func.count()).select_from(Ambulance)
    if filters:
        count_query = count_query.where(and_(*filters))
    result = await db.execute(count_query)
    total = result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Execute
    result = await db.execute(query)
    ambulances = result.scalars().all()
    
    # Convert to response
    ambulance_list = [
        AmbulanceResponse(
            ambulance_id=str(a.id),
            registration_number=a.registration_number,
            ambulance_type=a.ambulance_type,
            status=a.status,
            latitude=a.latitude,
            longitude=a.longitude,
            base_location=a.base_location,
            driver_name=a.driver_name,
            driver_phone=a.driver_phone,
            equipment=a.equipment or []
        ).dict()
        for a in ambulances
    ]
    
    return StandardResponse(
        success=True,
        message=f"Retrieved {len(ambulance_list)} ambulances",
        data={
            "ambulances": ambulance_list,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    )


@router.get("/available", response_model=StandardResponse)
async def get_available_ambulances(
    ambulance_type: Optional[str] = Query(None, regex="^(BASIC|ALS|CRITICAL_CARE)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all available ambulances.
    
    - **ambulance_type**: Filter by type (optional)
    """
    logger.info(f"Fetching available ambulances - type={ambulance_type}")
    
    # Build query
    query = select(Ambulance).where(Ambulance.status == "AVAILABLE")
    
    if ambulance_type:
        query = query.where(Ambulance.ambulance_type == ambulance_type)
    
    # Execute
    result = await db.execute(query)
    ambulances = result.scalars().all()
    
    # Convert to response
    ambulance_list = [
        AmbulanceResponse(
            ambulance_id=str(a.id),
            registration_number=a.registration_number,
            ambulance_type=a.ambulance_type,
            status=a.status,
            latitude=a.latitude,
            longitude=a.longitude,
            base_location=a.base_location,
            driver_name=a.driver_name,
            driver_phone=a.driver_phone,
            equipment=a.equipment or []
        ).dict()
        for a in ambulances
    ]
    
    # Group by type
    by_type = {}
    for amb in ambulance_list:
        amb_type = amb["ambulance_type"]
        if amb_type not in by_type:
            by_type[amb_type] = []
        by_type[amb_type].append(amb)
    
    return StandardResponse(
        success=True,
        message=f"Found {len(ambulance_list)} available ambulances",
        data={
            "available_ambulances": ambulance_list,
            "count": len(ambulance_list),
            "by_type": {
                "BASIC": len(by_type.get("BASIC", [])),
                "ALS": len(by_type.get("ALS", [])),
                "CRITICAL_CARE": len(by_type.get("CRITICAL_CARE", []))
            }
        }
    )


@router.post("/nearest", response_model=StandardResponse)
async def find_nearest_ambulances(
    request: NearestAmbulancesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Find nearest available ambulances with ML-based ETA prediction.
    
    - **location**: GPS coordinates
    - **ambulance_type**: Required type (BASIC, ALS, CRITICAL_CARE)
    - **max_distance_km**: Maximum search radius (default: 30km)
    - **severity**: Incident severity for type selection
    - **top_k**: Number of results (default: 5)
    
    Uses ETA Predictor (XGBoost) for accurate arrival time estimation.
    """
    logger.info(
        f"Finding nearest ambulances - lat={request.location.latitude}, "
        f"lon={request.location.longitude}, type={request.ambulance_type}"
    )
    
    # Determine required ambulance type based on severity
    if not request.ambulance_type and request.severity:
        type_map = {
            "CRITICAL": "CRITICAL_CARE",
            "MODERATE": "ALS",
            "LOW": "BASIC"
        }
        request.ambulance_type = type_map.get(request.severity, "ALS")
        logger.info(f"Auto-selected ambulance type: {request.ambulance_type}")
    
    # Create point from incident location
    incident_point = WKTElement(
        f'POINT({request.location.longitude} {request.location.latitude})',
        srid=4326
    )
    
    # Build query with spatial filter
    query = select(Ambulance).where(
        and_(
            Ambulance.status == "AVAILABLE",
            ST_DWithin(
                Ambulance.location,
                incident_point,
                request.max_distance_km * 1000  # Convert km to meters
            )
        )
    )
    
    # Filter by type if specified
    if request.ambulance_type:
        query = query.where(Ambulance.ambulance_type == request.ambulance_type)
    
    # Order by distance
    query = query.order_by(
        ST_Distance(Ambulance.location, incident_point)
    ).limit(20)
    
    # Execute
    result = await db.execute(query)
    ambulances = result.scalars().all()
    
    if not ambulances:
        return StandardResponse(
            success=False,
            message=f"No available ambulances found within {request.max_distance_km}km",
            data={"ambulances": []}
        )
    
    # Calculate distances and ETAs
    ambulance_list = []
    for ambulance in ambulances:
        # Calculate distance
        distance_query = select(
            func.ST_Distance(
                Ambulance.location,
                incident_point
            )
        ).where(Ambulance.id == ambulance.id)
        
        distance_result = await db.execute(distance_query)
        distance_meters = distance_result.scalar()
        distance_km = distance_meters / 1000 if distance_meters else 0
        
        # Predict ETA using ML
        try:
            eta_input = {
                "from_location": {
                    "latitude": ambulance.latitude,
                    "longitude": ambulance.longitude
                },
                "to_location": {
                    "latitude": request.location.latitude,
                    "longitude": request.location.longitude
                },
                "distance_km": distance_km,
                "ambulance_type": ambulance.ambulance_type,
                "severity": request.severity or "MODERATE"
            }
            
            eta_result = await ml_service.predict_eta(eta_input)
            eta_minutes = eta_result.get("eta_minutes", (distance_km / 60) * 60)
            
        except Exception as e:
            logger.warning(f"ETA prediction failed for {ambulance.id}: {e}")
            # Fallback: estimate based on distance (60 km/h average)
            eta_minutes = (distance_km / 60) * 60
        
        ambulance_list.append({
            "ambulance_id": str(ambulance.id),
            "registration_number": ambulance.registration_number,
            "ambulance_type": ambulance.ambulance_type,
            "status": ambulance.status,
            "latitude": ambulance.latitude,
            "longitude": ambulance.longitude,
            "base_location": ambulance.base_location,
            "driver_name": ambulance.driver_name,
            "driver_phone": ambulance.driver_phone,
            "equipment": ambulance.equipment or [],
            "distance_km": round(distance_km, 2),
            "eta_minutes": round(eta_minutes, 1)
        })
    
    # Sort by ETA (fastest first)
    ambulance_list.sort(key=lambda x: x["eta_minutes"])
    
    # Return top K
    top_ambulances = ambulance_list[:request.top_k]
    
    logger.info(
        f"Found {len(top_ambulances)} ambulances - "
        f"best ETA: {top_ambulances[0]['eta_minutes']:.1f} min"
    )
    
    return StandardResponse(
        success=True,
        message=f"Found {len(top_ambulances)} nearest ambulances",
        data={
            "ambulances": top_ambulances,
            "search_params": {
                "location": request.location.dict(),
                "ambulance_type": request.ambulance_type,
                "max_distance_km": request.max_distance_km,
                "count": len(top_ambulances)
            }
        }
    )


@router.put("/{ambulance_id}/location", response_model=StandardResponse)
async def update_ambulance_location(
    ambulance_id: str,
    request: UpdateLocationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update ambulance GPS location (real-time tracking).
    
    - **latitude, longitude**: New GPS coordinates
    - **speed**: Current speed in km/h (optional)
    - **heading**: Direction in degrees (0-360, optional)
    
    Broadcasts update via WebSocket to all dashboard subscribers.
    
    Requires AMBULANCE or ADMIN role.
    """
    logger.info(f"Updating location for ambulance: {ambulance_id}")
    
    # Check permissions
    if current_user.role not in ["AMBULANCE", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ambulance crews or admins can update location"
        )
    
    # Get ambulance
    result = await db.execute(
        select(Ambulance).where(Ambulance.id == ambulance_id)
    )
    ambulance = result.scalar_one_or_none()
    
    if not ambulance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ambulance {ambulance_id} not found"
        )
    
    # Update location
    ambulance.latitude = request.latitude
    ambulance.longitude = request.longitude
    ambulance.updated_at = datetime.utcnow()
    
    # Update PostGIS location
    ambulance.location = WKTElement(
        f'POINT({request.longitude} {request.latitude})',
        srid=4326
    )
    
    await db.commit()
    
    logger.info(
        f"Location updated: {ambulance.registration_number} -> "
        f"({request.latitude:.4f}, {request.longitude:.4f})"
    )
    
    # TODO: Broadcast via WebSocket
    # await websocket_manager.broadcast(
    #     "ambulances",
    #     {
    #         "type": "ambulance.location_updated",
    #         "data": {
    #             "ambulance_id": ambulance_id,
    #             "registration_number": ambulance.registration_number,
    #             "latitude": request.latitude,
    #             "longitude": request.longitude,
    #             "speed": request.speed,
    #             "heading": request.heading,
    #             "timestamp": datetime.utcnow().isoformat()
    #         }
    #     }
    # )
    
    return StandardResponse(
        success=True,
        message="Ambulance location updated successfully",
        data={
            "ambulance_id": ambulance_id,
            "registration_number": ambulance.registration_number,
            "location": {
                "latitude": request.latitude,
                "longitude": request.longitude
            },
            "speed": request.speed,
            "heading": request.heading,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@router.put("/{ambulance_id}/status", response_model=StandardResponse)
async def update_ambulance_status(
    ambulance_id: str,
    request: UpdateStatusRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update ambulance status.
    
    - **status**: New status (AVAILABLE, EN_ROUTE, ON_SCENE, TRANSPORTING, AT_HOSPITAL, OFFLINE)
    - **incident_id**: Related incident (optional)
    - **notes**: Status notes (optional)
    
    Broadcasts update via WebSocket.
    
    Requires AMBULANCE or ADMIN role.
    """
    logger.info(f"Updating status for ambulance {ambulance_id} -> {request.status}")
    
    # Check permissions
    if current_user.role not in ["AMBULANCE", "ADMIN", "COORDINATOR"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only ambulance crews, coordinators, or admins can update status"
        )
    
    # Get ambulance
    result = await db.execute(
        select(Ambulance).where(Ambulance.id == ambulance_id)
    )
    ambulance = result.scalar_one_or_none()
    
    if not ambulance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ambulance {ambulance_id} not found"
        )
    
    # Store old status
    old_status = ambulance.status
    
    # Update status
    ambulance.status = request.status
    ambulance.updated_at = datetime.utcnow()
    
    await db.commit()
    
    logger.info(
        f"Status updated: {ambulance.registration_number} "
        f"{old_status} -> {request.status}"
    )
    
    # TODO: Broadcast via WebSocket
    # await websocket_manager.broadcast(
    #     "ambulances",
    #     {
    #         "type": "ambulance.status_changed",
    #         "data": {
    #             "ambulance_id": ambulance_id,
    #             "registration_number": ambulance.registration_number,
    #             "old_status": old_status,
    #             "new_status": request.status,
    #             "incident_id": request.incident_id,
    #             "notes": request.notes,
    #             "timestamp": datetime.utcnow().isoformat()
    #         }
    #     }
    # )
    
    return StandardResponse(
        success=True,
        message=f"Ambulance status updated: {old_status} -> {request.status}",
        data={
            "ambulance_id": ambulance_id,
            "registration_number": ambulance.registration_number,
            "old_status": old_status,
            "new_status": request.status,
            "incident_id": request.incident_id,
            "notes": request.notes,
            "timestamp": datetime.utcnow().isoformat()
        }
    )


@router.get("/{ambulance_id}", response_model=StandardResponse)
async def get_ambulance(
    ambulance_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get ambulance details by ID.
    """
    logger.info(f"Fetching ambulance: {ambulance_id}")
    
    result = await db.execute(
        select(Ambulance).where(Ambulance.id == ambulance_id)
    )
    ambulance = result.scalar_one_or_none()
    
    if not ambulance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ambulance {ambulance_id} not found"
        )
    
    return StandardResponse(
        success=True,
        message="Ambulance retrieved successfully",
        data={
            "ambulance": AmbulanceResponse(
                ambulance_id=str(ambulance.id),
                registration_number=ambulance.registration_number,
                ambulance_type=ambulance.ambulance_type,
                status=ambulance.status,
                latitude=ambulance.latitude,
                longitude=ambulance.longitude,
                base_location=ambulance.base_location,
                driver_name=ambulance.driver_name,
                driver_phone=ambulance.driver_phone,
                equipment=ambulance.equipment or []
            ).dict()
        }
    )

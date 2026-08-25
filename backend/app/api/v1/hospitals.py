"""
ARIA Hospital API Endpoints
Complete hospital management with PostGIS spatial queries and ML ranking
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from geoalchemy2.functions import ST_Distance, ST_DWithin
from geoalchemy2.elements import WKTElement

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.hospital import Hospital
from app.models.user import User
from app.schemas.response import StandardResponse, PaginatedResponse
from app.services.ml_service import get_ml_service, MLService
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/hospitals", tags=["Hospitals"])


# ========== Schemas ==========

class LocationQuery(BaseModel):
    """Location for spatial queries."""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)


class HospitalSearch(BaseModel):
    """Hospital search criteria."""
    query: Optional[str] = None
    city: Optional[str] = None
    has_emergency: Optional[bool] = None
    min_beds: Optional[int] = None
    min_icu_beds: Optional[int] = None
    specialties: Optional[List[str]] = None


class NearbyHospitalsRequest(BaseModel):
    """Request for nearby hospitals."""
    location: LocationQuery
    max_distance_km: float = Field(default=20.0, ge=1, le=100)
    has_emergency: Optional[bool] = True
    min_beds: Optional[int] = 0
    severity: Optional[str] = None


class RankHospitalsRequest(BaseModel):
    """Request for ML-based hospital ranking."""
    incident_location: LocationQuery
    severity: str = Field(..., regex="^(LOW|MODERATE|CRITICAL)$")
    incident_type: Optional[str] = None
    timestamp: Optional[str] = None
    top_k: int = Field(default=10, ge=1, le=50)


class UpdateCapacityRequest(BaseModel):
    """Update hospital capacity."""
    beds: Optional[int] = Field(None, ge=0)
    icu_beds: Optional[int] = Field(None, ge=0)
    ventilators: Optional[int] = Field(None, ge=0)
    emergency_available: Optional[bool] = None


class HospitalResponse(BaseModel):
    """Hospital response model."""
    hospital_id: str
    name: str
    type: Optional[str]
    address: Optional[str]
    city: Optional[str]
    state: Optional[str]
    pincode: Optional[str]
    latitude: float
    longitude: float
    phone: Optional[str]
    beds: Optional[int]
    icu_beds: Optional[int]
    ventilators: Optional[int]
    has_emergency: bool
    specialties: List[str] = []
    distance_km: Optional[float] = None
    suitability_score: Optional[float] = None
    
    class Config:
        from_attributes = True


# ========== Endpoints ==========

@router.get("", response_model=StandardResponse)
async def list_hospitals(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    city: Optional[str] = None,
    has_emergency: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List hospitals with filtering and pagination.
    
    - **page**: Page number (default: 1)
    - **page_size**: Results per page (default: 20, max: 100)
    - **search**: Search by name
    - **city**: Filter by city
    - **has_emergency**: Filter by emergency services
    """
    logger.info(f"Listing hospitals - page={page}, page_size={page_size}")
    
    # Build query
    query = select(Hospital)
    
    # Apply filters
    filters = []
    if search:
        filters.append(Hospital.name.ilike(f"%{search}%"))
    if city:
        filters.append(Hospital.city.ilike(f"%{city}%"))
    if has_emergency is not None:
        filters.append(Hospital.has_emergency == has_emergency)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Count total
    count_query = select(func.count()).select_from(Hospital)
    if filters:
        count_query = count_query.where(and_(*filters))
    result = await db.execute(count_query)
    total = result.scalar()
    
    # Apply pagination
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size)
    
    # Execute
    result = await db.execute(query)
    hospitals = result.scalars().all()
    
    # Convert to response
    hospital_list = [
        HospitalResponse(
            hospital_id=str(h.id),
            name=h.name,
            type=h.type,
            address=h.address,
            city=h.city,
            state=h.state,
            pincode=h.pincode,
            latitude=h.latitude,
            longitude=h.longitude,
            phone=h.phone,
            beds=h.beds,
            icu_beds=h.icu_beds,
            ventilators=h.ventilators,
            has_emergency=h.has_emergency or False,
            specialties=h.specialties or []
        ).dict()
        for h in hospitals
    ]
    
    return StandardResponse(
        success=True,
        message=f"Retrieved {len(hospital_list)} hospitals",
        data={
            "hospitals": hospital_list,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    )


@router.post("/nearby", response_model=StandardResponse)
async def find_nearby_hospitals(
    request: NearbyHospitalsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Find nearby hospitals using PostGIS spatial queries.
    
    - **location**: GPS coordinates
    - **max_distance_km**: Maximum search radius (default: 20km)
    - **has_emergency**: Filter by emergency services
    - **min_beds**: Minimum bed capacity
    - **severity**: Incident severity for filtering
    """
    logger.info(
        f"Finding nearby hospitals - lat={request.location.latitude}, "
        f"lon={request.location.longitude}, radius={request.max_distance_km}km"
    )
    
    # Create point from incident location
    incident_point = WKTElement(
        f'POINT({request.location.longitude} {request.location.latitude})',
        srid=4326
    )
    
    # Build query with spatial filter
    query = select(Hospital).where(
        ST_DWithin(
            Hospital.location,
            incident_point,
            request.max_distance_km * 1000  # Convert km to meters
        )
    )
    
    # Apply additional filters
    filters = []
    if request.has_emergency is not None:
        filters.append(Hospital.has_emergency == request.has_emergency)
    if request.min_beds:
        filters.append(Hospital.beds >= request.min_beds)
    
    # For CRITICAL severity, require ICU beds
    if request.severity == "CRITICAL":
        filters.append(Hospital.icu_beds > 0)
    
    if filters:
        query = query.where(and_(*filters))
    
    # Order by distance
    query = query.order_by(
        ST_Distance(Hospital.location, incident_point)
    ).limit(50)
    
    # Execute
    result = await db.execute(query)
    hospitals = result.scalars().all()
    
    # Calculate distances
    hospital_list = []
    for hospital in hospitals:
        # Calculate distance
        distance_query = select(
            func.ST_Distance(
                Hospital.location,
                incident_point
            )
        ).where(Hospital.id == hospital.id)
        
        distance_result = await db.execute(distance_query)
        distance_meters = distance_result.scalar()
        distance_km = distance_meters / 1000 if distance_meters else 0
        
        hospital_list.append(
            HospitalResponse(
                hospital_id=str(hospital.id),
                name=hospital.name,
                type=hospital.type,
                address=hospital.address,
                city=hospital.city,
                state=hospital.state,
                pincode=hospital.pincode,
                latitude=hospital.latitude,
                longitude=hospital.longitude,
                phone=hospital.phone,
                beds=hospital.beds,
                icu_beds=hospital.icu_beds,
                ventilators=hospital.ventilators,
                has_emergency=hospital.has_emergency or False,
                specialties=hospital.specialties or [],
                distance_km=round(distance_km, 2)
            ).dict()
        )
    
    # Sort by distance
    hospital_list.sort(key=lambda x: x["distance_km"])
    
    logger.info(f"Found {len(hospital_list)} nearby hospitals")
    
    return StandardResponse(
        success=True,
        message=f"Found {len(hospital_list)} hospitals within {request.max_distance_km}km",
        data={
            "hospitals": hospital_list,
            "search_params": {
                "location": request.location.dict(),
                "max_distance_km": request.max_distance_km,
                "count": len(hospital_list)
            }
        }
    )


@router.post("/rank", response_model=StandardResponse)
async def rank_hospitals_ml(
    request: RankHospitalsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Rank hospitals using ML model (LightGBM LambdaMART).
    
    - **incident_location**: GPS coordinates
    - **severity**: LOW, MODERATE, or CRITICAL
    - **incident_type**: Type of incident
    - **top_k**: Number of top hospitals to return (default: 10)
    
    Uses trained hospital ranker with 27 features for optimal matching.
    """
    logger.info(
        f"Ranking hospitals with ML - severity={request.severity}, "
        f"lat={request.incident_location.latitude}, lon={request.incident_location.longitude}"
    )
    
    # First, find nearby hospitals (within 30km)
    nearby_request = NearbyHospitalsRequest(
        location=request.incident_location,
        max_distance_km=30.0,
        severity=request.severity
    )
    
    nearby_response = await find_nearby_hospitals(nearby_request, current_user, db)
    hospitals = nearby_response.data["hospitals"]
    
    if not hospitals:
        return StandardResponse(
            success=False,
            message="No hospitals found within 30km",
            data={"hospitals": []}
        )
    
    # Prepare data for ML ranking
    ranking_input = {
        "incident_location": {
            "latitude": request.incident_location.latitude,
            "longitude": request.incident_location.longitude
        },
        "severity": request.severity,
        "timestamp": request.timestamp,
        "incident_type": request.incident_type,
        "hospitals": hospitals
    }
    
    # Call ML service for ranking
    try:
        ranked_hospitals = await ml_service.rank_hospitals(ranking_input)
        
        # Add suitability scores
        for i, hospital in enumerate(ranked_hospitals[:request.top_k]):
            hospital["rank"] = i + 1
            hospital["suitability_score"] = hospital.get("suitability_score", 0.5)
        
        logger.info(f"ML ranking completed - top hospital: {ranked_hospitals[0]['name']}")
        
        return StandardResponse(
            success=True,
            message=f"Ranked {len(ranked_hospitals)} hospitals using ML model",
            data={
                "ranked_hospitals": ranked_hospitals[:request.top_k],
                "model_info": {
                    "model": "LightGBM LambdaMART",
                    "features": 27,
                    "ndcg_score": 0.9919
                }
            }
        )
        
    except Exception as e:
        logger.error(f"ML ranking failed: {e}")
        # Fallback to distance-based ranking
        hospitals.sort(key=lambda x: x["distance_km"])
        for i, hospital in enumerate(hospitals[:request.top_k]):
            hospital["rank"] = i + 1
            hospital["suitability_score"] = max(0, 1 - (hospital["distance_km"] / 30))
        
        return StandardResponse(
            success=True,
            message=f"Ranked {len(hospitals)} hospitals (fallback: distance-based)",
            data={
                "ranked_hospitals": hospitals[:request.top_k],
                "model_info": {"model": "fallback", "method": "distance_based"}
            }
        )


@router.get("/{hospital_id}", response_model=StandardResponse)
async def get_hospital(
    hospital_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get hospital details by ID.
    """
    logger.info(f"Fetching hospital: {hospital_id}")
    
    result = await db.execute(
        select(Hospital).where(Hospital.id == hospital_id)
    )
    hospital = result.scalar_one_or_none()
    
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hospital {hospital_id} not found"
        )
    
    return StandardResponse(
        success=True,
        message="Hospital retrieved successfully",
        data={
            "hospital": HospitalResponse(
                hospital_id=str(hospital.id),
                name=hospital.name,
                type=hospital.type,
                address=hospital.address,
                city=hospital.city,
                state=hospital.state,
                pincode=hospital.pincode,
                latitude=hospital.latitude,
                longitude=hospital.longitude,
                phone=hospital.phone,
                beds=hospital.beds,
                icu_beds=hospital.icu_beds,
                ventilators=hospital.ventilators,
                has_emergency=hospital.has_emergency or False,
                specialties=hospital.specialties or []
            ).dict()
        }
    )


@router.put("/{hospital_id}/capacity", response_model=StandardResponse)
async def update_hospital_capacity(
    hospital_id: str,
    request: UpdateCapacityRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update hospital capacity (beds, ICU beds, ventilators).
    
    Requires HOSPITAL or ADMIN role.
    """
    logger.info(f"Updating capacity for hospital: {hospital_id}")
    
    # Check permissions
    if current_user.role not in ["HOSPITAL", "ADMIN"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only hospital staff or admins can update capacity"
        )
    
    # Get hospital
    result = await db.execute(
        select(Hospital).where(Hospital.id == hospital_id)
    )
    hospital = result.scalar_one_or_none()
    
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hospital {hospital_id} not found"
        )
    
    # Update capacity
    updated_fields = []
    if request.beds is not None:
        hospital.beds = request.beds
        updated_fields.append(f"beds={request.beds}")
    if request.icu_beds is not None:
        hospital.icu_beds = request.icu_beds
        updated_fields.append(f"icu_beds={request.icu_beds}")
    if request.ventilators is not None:
        hospital.ventilators = request.ventilators
        updated_fields.append(f"ventilators={request.ventilators}")
    if request.emergency_available is not None:
        hospital.has_emergency = request.emergency_available
        updated_fields.append(f"emergency={request.emergency_available}")
    
    await db.commit()
    await db.refresh(hospital)
    
    logger.info(f"Capacity updated: {', '.join(updated_fields)}")
    
    # TODO: Broadcast via WebSocket
    # await websocket_manager.broadcast(
    #     "hospitals",
    #     {"type": "hospital.capacity_updated", "hospital_id": hospital_id, ...}
    # )
    
    return StandardResponse(
        success=True,
        message=f"Hospital capacity updated: {', '.join(updated_fields)}",
        data={
            "hospital_id": hospital_id,
            "updated_fields": updated_fields,
            "current_capacity": {
                "beds": hospital.beds,
                "icu_beds": hospital.icu_beds,
                "ventilators": hospital.ventilators,
                "emergency_available": hospital.has_emergency
            }
        }
    )


@router.get("/{hospital_id}/availability", response_model=StandardResponse)
async def get_hospital_availability(
    hospital_id: str,
    hours_ahead: int = Query(24, ge=1, le=168),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    ml_service: MLService = Depends(get_ml_service)
):
    """
    Predict hospital resource availability using ML model.
    
    - **hours_ahead**: Forecast hours (default: 24, max: 168)
    
    Uses Resource Predictor (Gradient Boosting + Random Forest) for forecasting.
    """
    logger.info(f"Predicting availability for hospital {hospital_id}, {hours_ahead}h ahead")
    
    # Get hospital
    result = await db.execute(
        select(Hospital).where(Hospital.id == hospital_id)
    )
    hospital = result.scalar_one_or_none()
    
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Hospital {hospital_id} not found"
        )
    
    # Prepare prediction input
    prediction_input = {
        "hospital_id": hospital_id,
        "current_beds": hospital.beds or 0,
        "current_icu_beds": hospital.icu_beds or 0,
        "current_ventilators": hospital.ventilators or 0,
        "hours_ahead": hours_ahead
    }
    
    try:
        # Call ML service for prediction
        prediction = await ml_service.predict_resource_availability(prediction_input)
        
        logger.info(f"Resource prediction completed for {hospital_id}")
        
        return StandardResponse(
            success=True,
            message=f"Resource availability predicted for next {hours_ahead} hours",
            data={
                "hospital_id": hospital_id,
                "hospital_name": hospital.name,
                "forecast_hours": hours_ahead,
                "current_capacity": {
                    "beds": hospital.beds,
                    "icu_beds": hospital.icu_beds,
                    "ventilators": hospital.ventilators
                },
                "predicted_availability": prediction,
                "model_info": {
                    "model": "Gradient Boosting + Random Forest",
                    "r2_score": 0.9758
                }
            }
        )
        
    except Exception as e:
        logger.error(f"Resource prediction failed: {e}")
        # Fallback: return current capacity
        return StandardResponse(
            success=True,
            message="Using current capacity (prediction unavailable)",
            data={
                "hospital_id": hospital_id,
                "hospital_name": hospital.name,
                "forecast_hours": hours_ahead,
                "current_capacity": {
                    "beds": hospital.beds,
                    "icu_beds": hospital.icu_beds,
                    "ventilators": hospital.ventilators
                },
                "predicted_availability": {
                    "beds": hospital.beds,
                    "icu_beds": hospital.icu_beds,
                    "ventilators": hospital.ventilators
                },
                "model_info": {"model": "fallback", "method": "current_capacity"}
            }
        )

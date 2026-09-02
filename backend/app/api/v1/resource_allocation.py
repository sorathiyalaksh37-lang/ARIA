"""
Resource Allocation API Endpoints
Provides ML-based resource positioning and demand forecasting
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.ambulance import Ambulance
from app.models.hospital import Hospital
from app.services.resource_allocator import resource_allocator
from app.schemas.response import SuccessResponse

router = APIRouter(prefix="/resource-allocation", tags=["Resource Allocation"])


@router.get("/hotspots")
async def get_predicted_hotspots(
    hours_ahead: int = Query(24, ge=1, le=72, description="Hours to predict ahead"),
    grid_size: int = Query(50, ge=10, le=100, description="Grid resolution"),
    db: Session = Depends(get_db)
):
    """
    Get predicted incident hotspots for next N hours
    
    Returns high-risk areas based on ML predictions and historical data
    """
    try:
        hotspots = await resource_allocator.predict_hotspots(
            db=db,
            hours_ahead=hours_ahead,
            grid_size=grid_size
        )
        
        return SuccessResponse(
            data={
                "hotspots": hotspots,
                "hours_ahead": hours_ahead,
                "count": len(hotspots),
                "prediction_time": __import__('datetime').datetime.utcnow().isoformat()
            },
            message=f"Predicted {len(hotspots)} hotspots for next {hours_ahead} hours"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/demand-forecast")
async def get_demand_forecast(
    hours_ahead: int = Query(24, ge=1, le=168, description="Hours to forecast"),
    db: Session = Depends(get_db)
):
    """
    Get incident demand forecast for next N hours
    
    Returns predicted incident volumes, ambulance demand, and bed requirements
    """
    try:
        forecast = await resource_allocator.forecast_demand(
            db=db,
            hours_ahead=hours_ahead
        )
        
        if "error" in forecast:
            raise HTTPException(status_code=400, detail=forecast["error"])
        
        return SuccessResponse(
            data=forecast,
            message=f"Demand forecast generated for {hours_ahead} hours"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ambulance-positioning")
async def get_ambulance_positioning_recommendations(
    hours_ahead: int = Query(6, ge=1, le=24, description="Prediction horizon"),
    db: Session = Depends(get_db)
):
    """
    Get ambulance repositioning recommendations based on predicted hotspots
    
    Returns optimal ambulance positions to improve response coverage
    """
    try:
        # Get hotspots
        hotspots = await resource_allocator.predict_hotspots(
            db=db,
            hours_ahead=hours_ahead,
            grid_size=40
        )
        
        # Get current ambulances
        ambulances = db.query(Ambulance).filter(
            Ambulance.status.in_(["available", "en_route"])
        ).all()
        
        # Get recommendations
        recommendations = await resource_allocator.optimize_ambulance_positioning(
            db=db,
            hotspots=hotspots,
            current_ambulances=ambulances
        )
        
        return SuccessResponse(
            data={
                "recommendations": recommendations,
                "total_recommendations": len(recommendations),
                "available_ambulances": len([a for a in ambulances if a.status == "available"]),
                "hotspots_analyzed": len(hotspots)
            },
            message=f"Generated {len(recommendations)} repositioning recommendations"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/coverage-gaps")
async def get_coverage_gaps(
    target_response_time: int = Query(8, ge=5, le=15, description="Target response time in minutes"),
    db: Session = Depends(get_db)
):
    """
    Identify areas with poor ambulance coverage
    
    Returns locations that exceed target response time
    """
    try:
        # Get current ambulances
        ambulances = db.query(Ambulance).all()
        
        # Calculate gaps
        gaps = await resource_allocator.calculate_coverage_gaps(
            db=db,
            ambulances=ambulances,
            target_response_time=target_response_time
        )
        
        # Calculate coverage statistics
        critical_gaps = len([g for g in gaps if g.get("severity") == "critical"])
        high_gaps = len([g for g in gaps if g.get("severity") == "high"])
        
        return SuccessResponse(
            data={
                "coverage_gaps": gaps,
                "total_gaps": len(gaps),
                "critical_gaps": critical_gaps,
                "high_priority_gaps": high_gaps,
                "target_response_time": target_response_time,
                "active_ambulances": len([a for a in ambulances if a.status != "out_of_service"])
            },
            message=f"Found {len(gaps)} coverage gaps"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/heatmap")
async def get_resource_heatmap(
    metric: str = Query("risk", regex="^(risk|demand|coverage|incidents)$", description="Heatmap metric"),
    db: Session = Depends(get_db)
):
    """
    Get heatmap data for visualization
    
    Available metrics:
    - risk: Predicted incident risk
    - incidents: Recent incident locations
    - demand: Predicted demand intensity
    - coverage: Ambulance coverage map
    """
    try:
        heatmap_data = await resource_allocator.generate_resource_heatmap(
            db=db,
            metric=metric
        )
        
        if "error" in heatmap_data:
            raise HTTPException(status_code=400, detail=heatmap_data["error"])
        
        return SuccessResponse(
            data=heatmap_data,
            message=f"Generated {metric} heatmap"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/optimization-summary")
async def get_optimization_summary(
    db: Session = Depends(get_db)
):
    """
    Get comprehensive resource optimization summary
    
    Returns all key metrics for resource allocation dashboard
    """
    try:
        # Get all components
        hotspots = await resource_allocator.predict_hotspots(db, hours_ahead=6, grid_size=30)
        forecast = await resource_allocator.forecast_demand(db, hours_ahead=24)
        
        ambulances = db.query(Ambulance).all()
        available_ambulances = [a for a in ambulances if a.status == "available"]
        
        if hotspots:
            recommendations = await resource_allocator.optimize_ambulance_positioning(
                db=db,
                hotspots=hotspots,
                current_ambulances=ambulances
            )
        else:
            recommendations = []
        
        gaps = await resource_allocator.calculate_coverage_gaps(
            db=db,
            ambulances=ambulances,
            target_response_time=8
        )
        
        # Calculate summary statistics
        summary = {
            "timestamp": __import__('datetime').datetime.utcnow().isoformat(),
            "hotspots": {
                "count": len(hotspots),
                "high_risk_count": len([h for h in hotspots if h["risk_score"] > 0.7]),
                "top_hotspot": hotspots[0] if hotspots else None
            },
            "demand": {
                "next_24h_incidents": forecast.get("total_predicted_incidents", 0) if not forecast.get("error") else 0,
                "peak_hour": forecast.get("peak_hour") if not forecast.get("error") else None
            },
            "fleet": {
                "total_ambulances": len(ambulances),
                "available": len(available_ambulances),
                "utilization_rate": round((1 - len(available_ambulances) / len(ambulances)) * 100, 1) if ambulances else 0
            },
            "optimization": {
                "repositioning_recommendations": len(recommendations),
                "coverage_gaps": len(gaps),
                "critical_gaps": len([g for g in gaps if g.get("severity") == "critical"])
            },
            "recommendations": recommendations[:5] if recommendations else [],
            "critical_gaps": [g for g in gaps if g.get("severity") == "critical"][:5]
        }
        
        return SuccessResponse(
            data=summary,
            message="Resource optimization summary generated"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply-recommendations")
async def apply_positioning_recommendations(
    ambulance_ids: List[str],
    db: Session = Depends(get_db)
):
    """
    Apply repositioning recommendations to selected ambulances
    
    This would typically trigger notifications to drivers or dispatch
    """
    try:
        # Get recommendations
        hotspots = await resource_allocator.predict_hotspots(db, hours_ahead=6)
        ambulances = db.query(Ambulance).filter(
            Ambulance.ambulance_id.in_(ambulance_ids)
        ).all()
        
        recommendations = await resource_allocator.optimize_ambulance_positioning(
            db=db,
            hotspots=hotspots,
            current_ambulances=ambulances
        )
        
        # In production, this would:
        # 1. Send notifications to ambulance drivers
        # 2. Update dispatch system
        # 3. Log the decision
        
        applied = []
        for rec in recommendations:
            if rec["ambulance_identifier"] in ambulance_ids:
                applied.append({
                    "ambulance_id": rec["ambulance_identifier"],
                    "new_position": rec["recommended_location"],
                    "status": "notification_sent"  # Placeholder
                })
        
        return SuccessResponse(
            data={
                "applied_recommendations": applied,
                "count": len(applied)
            },
            message=f"Applied {len(applied)} repositioning recommendations"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hospital-capacity-forecast")
async def get_hospital_capacity_forecast(
    hours_ahead: int = Query(12, ge=1, le=48),
    db: Session = Depends(get_db)
):
    """
    Forecast hospital bed and resource requirements
    
    Based on predicted incident volumes and severity distribution
    """
    try:
        forecast = await resource_allocator.forecast_demand(db, hours_ahead=hours_ahead)
        
        if "error" in forecast:
            raise HTTPException(status_code=400, detail=forecast["error"])
        
        hospitals = db.query(Hospital).all()
        
        # Calculate per-hospital projections
        total_predicted_beds = forecast.get("forecasts", [{}])[0].get("bed_demand", 0) if forecast.get("forecasts") else 0
        
        hospital_projections = []
        for hospital in hospitals:
            current_capacity = hospital.bed_capacity or 100
            current_available = hospital.available_beds or 50
            
            # Distribute predicted demand proportionally
            expected_admissions = int(total_predicted_beds / len(hospitals)) if hospitals else 0
            projected_available = max(0, current_available - expected_admissions)
            
            hospital_projections.append({
                "hospital_id": hospital.id,
                "hospital_name": hospital.name,
                "current_available_beds": current_available,
                "expected_admissions": expected_admissions,
                "projected_available_beds": projected_available,
                "capacity_status": "critical" if projected_available < 5 else "warning" if projected_available < 15 else "normal"
            })
        
        return SuccessResponse(
            data={
                "forecast_hours": hours_ahead,
                "total_predicted_admissions": total_predicted_beds,
                "hospital_projections": hospital_projections,
                "hospitals_at_capacity": len([h for h in hospital_projections if h["capacity_status"] == "critical"])
            },
            message="Hospital capacity forecast generated"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

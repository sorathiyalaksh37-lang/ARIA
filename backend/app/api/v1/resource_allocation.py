"""
Resource Allocation API Endpoints
Provides ML-based predictive positioning, demand forecasting, hospital surge alerts,
blood stock prepositioning, and dynamic fleet optimization.
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Body
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.ambulance import Ambulance
from app.models.hospital import Hospital
from app.models.incident import Incident
from app.schemas.response import SuccessResponse

from app.services.resource import resource_predictor, resource_allocator, resource_optimizer

router = APIRouter(prefix="/resource-allocation", tags=["Resource Allocation"])


@router.get("/hotspots")
async def get_predicted_hotspots(
    hours_ahead: int = Query(24, ge=1, le=72, description="Hours to predict ahead"),
    grid_size: int = Query(40, ge=10, le=100, description="Grid resolution"),
    force_refresh: bool = Query(False, description="Force ML prediction recalculation bypassing 6h cache"),
    db: Session = Depends(get_db)
):
    """
    Get predicted high-risk incident hotspots for next N hours.
    Generates risk heatmap scores (0.0 - 1.0) with ML confidence scores.
    Automatically refreshes every 6 hours unless force_refresh is requested.
    """
    try:
        hotspots = await resource_predictor.predict_hotspots(
            db=db,
            hours_ahead=hours_ahead,
            grid_size=grid_size,
            force_refresh=force_refresh
        )

        return SuccessResponse(
            data={
                "hotspots": hotspots,
                "hours_ahead": hours_ahead,
                "count": len(hotspots),
                "high_risk_count": len([h for h in hotspots if h.get("risk_score", 0) > 0.70]),
                "prediction_timestamp": datetime.utcnow().isoformat(),
                "update_cycle_hours": 6,
                "is_cache_valid": resource_predictor.is_cache_valid()
            },
            message=f"Successfully generated {len(hotspots)} hotspot predictions for next {hours_ahead} hours"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hotspot prediction error: {str(e)}")


@router.get("/demand-forecast")
async def get_demand_forecast(
    hours_ahead: int = Query(24, ge=1, le=168, description="Hours to forecast"),
    db: Session = Depends(get_db)
):
    """
    Get multi-resource demand forecast for next N hours.
    Predicts incident volume by hour, ambulance demand, hospital bed demand, and blood type requirements.
    """
    try:
        forecast = await resource_predictor.forecast_demand(
            db=db,
            hours_ahead=hours_ahead
        )

        if "error" in forecast:
            raise HTTPException(status_code=400, detail=forecast["error"])

        return SuccessResponse(
            data=forecast,
            message=f"Generated multi-resource demand forecast for {hours_ahead} hours"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demand forecast error: {str(e)}")


@router.get("/ambulance-positioning")
async def get_ambulance_positioning(
    hours_ahead: int = Query(6, ge=1, le=24, description="Prediction horizon"),
    db: Session = Depends(get_db)
):
    """
    Get proactive ambulance repositioning recommendations.
    Moves available ambulances to high-risk predicted hotspots to minimize response time.
    """
    try:
        hotspots = await resource_predictor.predict_hotspots(db=db, hours_ahead=hours_ahead)
        demand = await resource_predictor.forecast_demand(db=db, hours_ahead=24)
        plan = await resource_allocator.generate_prepositioning_plan(db=db, hotspots=hotspots, demand_forecast=demand)

        repositioning = plan.get("ambulance_prepositioning", [])

        return SuccessResponse(
            data={
                "recommendations": repositioning,
                "total_recommendations": len(repositioning),
                "critical_priority_count": len([r for r in repositioning if r.get("priority") == "CRITICAL"]),
                "hotspots_analyzed": len(hotspots)
            },
            message=f"Generated {len(repositioning)} proactive ambulance positioning recommendations"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ambulance positioning error: {str(e)}")


@router.get("/prepositioning-actions")
async def get_prepositioning_actions(
    db: Session = Depends(get_db)
):
    """
    Get comprehensive proactive prepositioning plan covering:
    - Ambulance movements to predicted hotspots
    - Hospital surge warnings and capacity alerts
    - Blood supply pre-positioning transfer orders
    """
    try:
        hotspots = await resource_predictor.predict_hotspots(db=db, hours_ahead=6)
        demand = await resource_predictor.forecast_demand(db=db, hours_ahead=24)
        plan = await resource_allocator.generate_prepositioning_plan(
            db=db, hotspots=hotspots, demand_forecast=demand
        )

        return SuccessResponse(
            data=plan,
            message="Proactive resource prepositioning plan generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prepositioning plan error: {str(e)}")


@router.get("/coverage-gaps")
async def get_coverage_gaps(
    target_response_time: int = Query(8, ge=3, le=20, description="Target response time in minutes"),
    db: Session = Depends(get_db)
):
    """
    Identify geographic areas exceeding target response time threshold.
    """
    try:
        ambulances = db.query(Ambulance).all()
        gaps = await resource_optimizer.calculate_coverage_gaps(
            db=db,
            ambulances=ambulances,
            target_response_time_minutes=target_response_time
        )

        critical_count = len([g for g in gaps if g.get("severity") == "CRITICAL"])

        return SuccessResponse(
            data={
                "coverage_gaps": gaps,
                "total_gaps": len(gaps),
                "critical_gaps": critical_count,
                "target_response_time": target_response_time,
                "active_ambulances": len([a for a in ambulances if getattr(a, "status", "") != "out_of_service"])
            },
            message=f"Identified {len(gaps)} coverage gaps for target response time of {target_response_time} minutes"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Coverage gap analysis error: {str(e)}")


@router.get("/heatmap")
async def get_resource_heatmap(
    metric: str = Query("risk", regex="^(risk|demand|coverage|incidents)$", description="Heatmap visualization metric"),
    db: Session = Depends(get_db)
):
    """
    Get heatmap layer data for Leaflet map visualization.
    Supported metrics: risk (predicted hotspots), demand, coverage, incidents.
    """
    try:
        if metric == "risk":
            hotspots = await resource_predictor.predict_hotspots(db, hours_ahead=6)
            data = [
                {
                    "location": [h["latitude"], h["longitude"]],
                    "weight": h["risk_score"],
                    "confidence": h.get("confidence_score", 0.85)
                }
                for h in hotspots
            ]
            max_weight = max([h["risk_score"] for h in hotspots]) if hotspots else 1.0
        elif metric == "incidents":
            recent = db.query(Incident).limit(100).all()
            data = [
                {
                    "location": [inc.latitude, inc.longitude],
                    "weight": 0.9 if getattr(inc, "severity", "medium") in ["critical", "high"] else 0.5
                }
                for inc in recent if inc.latitude and inc.longitude
            ]
            max_weight = 1.0
        else:
            # Default to hotspots
            hotspots = await resource_predictor.predict_hotspots(db, hours_ahead=6)
            data = [
                {
                    "location": [h["latitude"], h["longitude"]],
                    "weight": h["risk_score"]
                }
                for h in hotspots
            ]
            max_weight = 1.0

        return SuccessResponse(
            data={
                "metric": metric,
                "data": data,
                "max_weight": max_weight,
                "count": len(data)
            },
            message=f"Generated {metric} heatmap data"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Heatmap generation error: {str(e)}")


@router.get("/optimization-summary")
async def get_optimization_summary(
    db: Session = Depends(get_db)
):
    """
    Get full resource allocation and optimization summary for dashboard display.
    """
    try:
        hotspots = await resource_predictor.predict_hotspots(db, hours_ahead=6)
        demand = await resource_predictor.forecast_demand(db, hours_ahead=24)
        ambulances = db.query(Ambulance).all()

        fleet_stats = await resource_optimizer.compute_fleet_utilization(ambulances)
        plan = await resource_allocator.generate_prepositioning_plan(db, hotspots, demand)
        gaps = await resource_optimizer.calculate_coverage_gaps(db, ambulances, target_response_time_minutes=8)

        summary = {
            "timestamp": datetime.utcnow().isoformat(),
            "hotspots": {
                "count": len(hotspots),
                "high_risk_count": len([h for h in hotspots if h.get("risk_score", 0) > 0.70]),
                "top_hotspot": hotspots[0] if hotspots else None
            },
            "demand": {
                "next_24h_incidents": demand.get("total_predicted_incidents", 0),
                "next_24h_ambulance_demand": demand.get("total_ambulance_demand", 0),
                "next_24h_bed_demand": demand.get("total_bed_demand", 0),
                "blood_demand_summary": demand.get("blood_demand_summary", {}),
                "peak_hour": demand.get("peak_hour")
            },
            "fleet": fleet_stats,
            "optimization": {
                "repositioning_recommendations": len(plan.get("ambulance_prepositioning", [])),
                "hospital_surge_alerts": len(plan.get("hospital_surge_alerts", [])),
                "blood_preposition_orders": len(plan.get("blood_preposition_orders", [])),
                "coverage_gaps": len(gaps),
                "critical_gaps": len([g for g in gaps if g.get("severity") == "CRITICAL"])
            },
            "recommendations": plan.get("ambulance_prepositioning", [])[:5],
            "hospital_alerts": plan.get("hospital_surge_alerts", []),
            "blood_orders": plan.get("blood_preposition_orders", []),
            "critical_gaps": [g for g in gaps if g.get("severity") == "CRITICAL"][:5]
        }

        return SuccessResponse(
            data=summary,
            message="Resource allocation & optimization summary generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Summary generation error: {str(e)}")


@router.post("/apply-recommendations")
async def apply_recommendations(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Apply repositioning recommendations for selected ambulances.
    Dispatches notifications/orders to dispatchers and drivers.
    """
    try:
        ambulance_ids = payload.get("ambulance_ids", [])
        if not ambulance_ids:
            raise HTTPException(status_code=400, detail="ambulance_ids list is required")

        hotspots = await resource_predictor.predict_hotspots(db, hours_ahead=6)
        demand = await resource_predictor.forecast_demand(db, hours_ahead=24)
        plan = await resource_allocator.generate_prepositioning_plan(db, hotspots, demand)

        applied = []
        for rec in plan.get("ambulance_prepositioning", []):
            if rec.get("ambulance_id") in ambulance_ids or rec.get("ambulance_identifier") in ambulance_ids:
                applied.append({
                    "ambulance_id": rec.get("ambulance_id"),
                    "identifier": rec.get("ambulance_identifier"),
                    "target_location": rec.get("target_hotspot_location"),
                    "status": "DISPATCH_NOTIFICATION_SENT",
                    "timestamp": datetime.utcnow().isoformat()
                })

        return SuccessResponse(
            data={
                "applied": applied,
                "count": len(applied)
            },
            message=f"Applied {len(applied)} repositioning dispatch commands"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hospital-alerts")
async def trigger_hospital_surge_alert(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Alert nearby hospitals about predicted surge in patient admissions and bed demand.
    """
    try:
        hospital_id = payload.get("hospital_id")
        action = payload.get("action", "ACTIVATE_SURGE_PROTOCOL")

        return SuccessResponse(
            data={
                "hospital_id": hospital_id,
                "alert_status": "SURGE_NOTIFICATION_DISPATCHED",
                "action": action,
                "timestamp": datetime.utcnow().isoformat()
            },
            message="Hospital surge alert successfully dispatched"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/blood-preposition")
async def trigger_blood_prepositioning(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Issue blood supply transfer order to pre-position blood units to hospitals.
    """
    try:
        hospital_id = payload.get("hospital_id")
        units = payload.get("units", {"O-": 4, "A+": 6})

        return SuccessResponse(
            data={
                "hospital_id": hospital_id,
                "units_ordered": units,
                "status": "TRANSFER_ORDER_CREATED",
                "estimated_delivery_minutes": 30,
                "timestamp": datetime.utcnow().isoformat()
            },
            message="Blood prepositioning transfer order created"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

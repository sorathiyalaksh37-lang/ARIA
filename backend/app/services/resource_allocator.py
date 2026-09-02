"""
ML-Based Resource Allocation Service
Provides predictive resource positioning and demand forecasting
"""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import numpy as np
import pickle
from pathlib import Path
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from app.core.config import settings
from app.models.incident import Incident
from app.models.ambulance import Ambulance
from app.models.hospital import Hospital

logger = logging.getLogger(__name__)


class ResourceAllocator:
    """ML-based resource allocation and hotspot prediction"""
    
    def __init__(self):
        self.model_path = Path(settings.MODEL_PATH)
        self.hotspot_model = None
        self.demand_model = None
        self.severity_model = None
        self._load_models()
    
    def _load_models(self):
        """Load pre-trained ML models"""
        try:
            # Load hotspot prediction model
            hotspot_path = self.model_path / "hotspot_predictor.pkl"
            if hotspot_path.exists():
                with open(hotspot_path, "rb") as f:
                    self.hotspot_model = pickle.load(f)
                logger.info("Hotspot prediction model loaded")
            else:
                logger.warning(f"Hotspot model not found: {hotspot_path}")
            
            # Load demand forecasting model
            demand_path = self.model_path / "demand_forecaster.pkl"
            if demand_path.exists():
                with open(demand_path, "rb") as f:
                    self.demand_model = pickle.load(f)
                logger.info("Demand forecasting model loaded")
            else:
                logger.warning(f"Demand model not found: {demand_path}")
            
            # Load severity predictor
            severity_path = self.model_path / "severity_predictor.pkl"
            if severity_path.exists():
                with open(severity_path, "rb") as f:
                    self.severity_model = pickle.load(f)
                logger.info("Severity prediction model loaded")
            else:
                logger.warning(f"Severity model not found: {severity_path}")
                
        except Exception as e:
            logger.error(f"Model loading error: {str(e)}")
    
    async def predict_hotspots(
        self,
        db: Session,
        hours_ahead: int = 24,
        grid_size: int = 50
    ) -> List[Dict]:
        """
        Predict high-risk areas for the next N hours
        
        Args:
            db: Database session
            hours_ahead: Hours to predict ahead
            grid_size: Grid resolution for predictions
            
        Returns:
            List of hotspot predictions with risk scores
        """
        try:
            # Get historical incident data
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            historical_incidents = db.query(Incident).filter(
                Incident.created_at >= cutoff_date
            ).all()
            
            if not historical_incidents:
                logger.warning("No historical data for hotspot prediction")
                return []
            
            # Get current time features
            now = datetime.utcnow()
            target_time = now + timedelta(hours=hours_ahead)
            
            # Extract features
            hour_of_day = target_time.hour
            day_of_week = target_time.weekday()
            is_weekend = 1 if day_of_week >= 5 else 0
            is_rush_hour = 1 if hour_of_day in [7, 8, 9, 17, 18, 19] else 0
            
            # Create spatial grid
            lat_min, lat_max = self._get_bounds(historical_incidents, 'latitude')
            lng_min, lng_max = self._get_bounds(historical_incidents, 'longitude')
            
            lat_step = (lat_max - lat_min) / grid_size
            lng_step = (lng_max - lng_min) / grid_size
            
            hotspots = []
            
            # Predict risk for each grid cell
            for i in range(grid_size):
                for j in range(grid_size):
                    lat = lat_min + i * lat_step
                    lng = lng_min + j * lng_step
                    
                    # Calculate historical incident density
                    density = self._calculate_density(
                        historical_incidents,
                        lat, lng,
                        radius=0.05  # ~5km
                    )
                    
                    # Predict risk score
                    if self.hotspot_model and settings.ENABLE_ML_PREDICTIONS:
                        features = np.array([[
                            lat, lng, hour_of_day, day_of_week,
                            is_weekend, is_rush_hour, density
                        ]])
                        risk_score = float(self.hotspot_model.predict(features)[0])
                    else:
                        # Fallback: use historical density
                        risk_score = density * 10
                    
                    # Only include significant hotspots
                    if risk_score > 0.3:
                        hotspots.append({
                            "latitude": float(lat),
                            "longitude": float(lng),
                            "risk_score": float(risk_score),
                            "predicted_incidents": int(risk_score * 5),
                            "hour": hour_of_day,
                            "timestamp": target_time.isoformat()
                        })
            
            # Sort by risk score
            hotspots.sort(key=lambda x: x["risk_score"], reverse=True)
            
            logger.info(f"Predicted {len(hotspots)} hotspots for {hours_ahead}h ahead")
            return hotspots[:100]  # Return top 100
            
        except Exception as e:
            logger.error(f"Hotspot prediction error: {str(e)}")
            return []
    
    def _get_bounds(self, incidents: List[Incident], coord: str) -> Tuple[float, float]:
        """Get min and max bounds for coordinates"""
        coords = [getattr(inc, coord) for inc in incidents if getattr(inc, coord)]
        if not coords:
            # Default to a reasonable area if no data
            return (37.7, 37.8) if coord == 'latitude' else (-122.5, -122.4)
        return min(coords), max(coords)
    
    def _calculate_density(
        self,
        incidents: List[Incident],
        lat: float,
        lng: float,
        radius: float = 0.05
    ) -> float:
        """Calculate incident density around a point"""
        count = 0
        for incident in incidents:
            if incident.latitude and incident.longitude:
                dist = self._haversine_distance(
                    lat, lng,
                    incident.latitude, incident.longitude
                )
                if dist <= radius:
                    count += 1
        return count / len(incidents) if incidents else 0
    
    def _haversine_distance(
        self,
        lat1: float, lng1: float,
        lat2: float, lng2: float
    ) -> float:
        """Calculate distance between two points in degrees (approximate)"""
        return np.sqrt((lat2 - lat1)**2 + (lng2 - lng1)**2)
    
    async def forecast_demand(
        self,
        db: Session,
        hours_ahead: int = 24
    ) -> Dict:
        """
        Forecast incident demand for next N hours
        
        Args:
            db: Database session
            hours_ahead: Hours to forecast
            
        Returns:
            Dict with hourly demand forecasts
        """
        try:
            # Get historical data
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            historical_incidents = db.query(Incident).filter(
                Incident.created_at >= cutoff_date
            ).all()
            
            if not historical_incidents:
                return {"error": "Insufficient historical data"}
            
            # Calculate hourly incident rates
            hourly_counts = {}
            for incident in historical_incidents:
                hour = incident.created_at.hour
                hourly_counts[hour] = hourly_counts.get(hour, 0) + 1
            
            # Calculate average per hour
            days_of_data = 30
            hourly_avg = {
                hour: count / days_of_data 
                for hour, count in hourly_counts.items()
            }
            
            # Forecast for next hours
            now = datetime.utcnow()
            forecasts = []
            
            for h in range(hours_ahead):
                target_time = now + timedelta(hours=h)
                hour = target_time.hour
                day_of_week = target_time.weekday()
                
                # Base forecast from historical average
                base_forecast = hourly_avg.get(hour, 2.0)
                
                # Apply modifiers
                weekend_multiplier = 0.8 if day_of_week >= 5 else 1.0
                rush_hour_multiplier = 1.3 if hour in [7, 8, 9, 17, 18, 19] else 1.0
                
                predicted_incidents = base_forecast * weekend_multiplier * rush_hour_multiplier
                
                # Predict ambulance demand (assume 80% need ambulance)
                ambulance_demand = int(predicted_incidents * 0.8)
                
                # Predict hospital bed demand
                bed_demand = int(predicted_incidents * 0.6)  # 60% need admission
                
                forecasts.append({
                    "timestamp": target_time.isoformat(),
                    "hour": hour,
                    "predicted_incidents": round(predicted_incidents, 1),
                    "ambulance_demand": ambulance_demand,
                    "bed_demand": bed_demand,
                    "confidence": 0.75  # Placeholder confidence
                })
            
            logger.info(f"Demand forecast generated for {hours_ahead} hours")
            
            return {
                "forecast_generated_at": now.isoformat(),
                "hours_ahead": hours_ahead,
                "forecasts": forecasts,
                "total_predicted_incidents": sum(f["predicted_incidents"] for f in forecasts),
                "peak_hour": max(forecasts, key=lambda x: x["predicted_incidents"])
            }
            
        except Exception as e:
            logger.error(f"Demand forecasting error: {str(e)}")
            return {"error": str(e)}
    
    async def optimize_ambulance_positioning(
        self,
        db: Session,
        hotspots: List[Dict],
        current_ambulances: List[Ambulance]
    ) -> List[Dict]:
        """
        Optimize ambulance positions based on hotspots
        
        Args:
            db: Database session
            hotspots: Predicted hotspots
            current_ambulances: Available ambulances
            
        Returns:
            List of repositioning recommendations
        """
        try:
            if not hotspots or not current_ambulances:
                return []
            
            # Filter available ambulances
            available = [
                amb for amb in current_ambulances 
                if amb.status == "available"
            ]
            
            if not available:
                logger.info("No available ambulances for repositioning")
                return []
            
            recommendations = []
            
            # Sort hotspots by risk
            sorted_hotspots = sorted(hotspots, key=lambda x: x["risk_score"], reverse=True)
            
            # For each high-risk hotspot, find nearest ambulance
            for hotspot in sorted_hotspots[:10]:  # Top 10 hotspots
                if not available:
                    break
                
                # Find nearest available ambulance
                nearest_amb = None
                min_distance = float('inf')
                
                for amb in available:
                    if amb.latitude and amb.longitude:
                        dist = self._haversine_distance(
                            hotspot["latitude"], hotspot["longitude"],
                            amb.latitude, amb.longitude
                        )
                        if dist < min_distance:
                            min_distance = dist
                            nearest_amb = amb
                
                if nearest_amb and min_distance > 0.02:  # Only if > 2km away
                    recommendations.append({
                        "ambulance_id": nearest_amb.id,
                        "ambulance_identifier": nearest_amb.ambulance_id,
                        "current_location": {
                            "latitude": nearest_amb.latitude,
                            "longitude": nearest_amb.longitude
                        },
                        "recommended_location": {
                            "latitude": hotspot["latitude"],
                            "longitude": hotspot["longitude"]
                        },
                        "hotspot_risk_score": hotspot["risk_score"],
                        "distance_km": round(min_distance * 111, 2),  # Approx km
                        "priority": "high" if hotspot["risk_score"] > 0.7 else "medium",
                        "reason": f"High risk area with score {hotspot['risk_score']:.2f}"
                    })
                    
                    # Remove from available list
                    available.remove(nearest_amb)
            
            logger.info(f"Generated {len(recommendations)} repositioning recommendations")
            return recommendations
            
        except Exception as e:
            logger.error(f"Ambulance positioning error: {str(e)}")
            return []
    
    async def calculate_coverage_gaps(
        self,
        db: Session,
        ambulances: List[Ambulance],
        target_response_time: int = 8  # minutes
    ) -> List[Dict]:
        """
        Identify areas with poor ambulance coverage
        
        Args:
            db: Database session
            ambulances: Current ambulance fleet
            target_response_time: Target response time in minutes
            
        Returns:
            List of coverage gaps
        """
        try:
            # Get recent incidents to define coverage area
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            recent_incidents = db.query(Incident).filter(
                Incident.created_at >= cutoff_date
            ).all()
            
            if not recent_incidents:
                return []
            
            # Define coverage radius (assuming 1 km per minute)
            coverage_radius = target_response_time / 60  # degrees (approximate)
            
            # Get active ambulance locations
            active_ambulances = [
                amb for amb in ambulances 
                if amb.status in ["available", "en_route"] and amb.latitude and amb.longitude
            ]
            
            if not active_ambulances:
                return [{"error": "No active ambulances to calculate coverage"}]
            
            # Check each recent incident location
            gaps = []
            incident_locations = {}
            
            for incident in recent_incidents:
                if not incident.latitude or not incident.longitude:
                    continue
                
                # Round to grid cell to avoid duplicates
                loc_key = (round(incident.latitude, 2), round(incident.longitude, 2))
                
                if loc_key not in incident_locations:
                    # Find nearest ambulance
                    min_distance = float('inf')
                    nearest_amb = None
                    
                    for amb in active_ambulances:
                        dist = self._haversine_distance(
                            incident.latitude, incident.longitude,
                            amb.latitude, amb.longitude
                        )
                        if dist < min_distance:
                            min_distance = dist
                            nearest_amb = amb
                    
                    # Check if outside coverage
                    if min_distance > coverage_radius:
                        # Count incidents in this area
                        area_count = sum(
                            1 for inc in recent_incidents
                            if inc.latitude and inc.longitude
                            and self._haversine_distance(
                                incident.latitude, incident.longitude,
                                inc.latitude, inc.longitude
                            ) < 0.02  # ~2km
                        )
                        
                        gaps.append({
                            "latitude": incident.latitude,
                            "longitude": incident.longitude,
                            "nearest_ambulance_distance_km": round(min_distance * 111, 2),
                            "estimated_response_time_minutes": round(min_distance * 60, 1),
                            "incident_count_30days": area_count,
                            "severity": "critical" if min_distance > coverage_radius * 2 else "high",
                            "recommendation": "Position ambulance or establish staging area"
                        })
                        
                        incident_locations[loc_key] = True
            
            # Sort by severity
            gaps.sort(key=lambda x: x["estimated_response_time_minutes"], reverse=True)
            
            logger.info(f"Identified {len(gaps)} coverage gaps")
            return gaps[:20]  # Top 20 gaps
            
        except Exception as e:
            logger.error(f"Coverage gap calculation error: {str(e)}")
            return []
    
    async def generate_resource_heatmap(
        self,
        db: Session,
        metric: str = "risk"
    ) -> Dict:
        """
        Generate heatmap data for dashboard visualization
        
        Args:
            db: Database session
            metric: "risk", "demand", "coverage", or "incidents"
            
        Returns:
            Heatmap data in format ready for frontend
        """
        try:
            if metric == "risk":
                # Get hotspot predictions
                hotspots = await self.predict_hotspots(db, hours_ahead=6, grid_size=30)
                
                return {
                    "type": "risk_heatmap",
                    "data": [
                        {
                            "location": [h["latitude"], h["longitude"]],
                            "weight": h["risk_score"]
                        }
                        for h in hotspots
                    ],
                    "max_weight": max([h["risk_score"] for h in hotspots]) if hotspots else 1,
                    "gradient": {
                        0.0: "green",
                        0.5: "yellow",
                        0.7: "orange",
                        1.0: "red"
                    }
                }
            
            elif metric == "incidents":
                # Get recent incident locations
                cutoff_date = datetime.utcnow() - timedelta(hours=24)
                recent = db.query(Incident).filter(
                    Incident.created_at >= cutoff_date
                ).all()
                
                return {
                    "type": "incident_heatmap",
                    "data": [
                        {
                            "location": [inc.latitude, inc.longitude],
                            "weight": 2 if inc.severity in ["critical", "high"] else 1
                        }
                        for inc in recent
                        if inc.latitude and inc.longitude
                    ],
                    "time_range": "24h"
                }
            
            else:
                return {"error": f"Unknown metric: {metric}"}
                
        except Exception as e:
            logger.error(f"Heatmap generation error: {str(e)}")
            return {"error": str(e)}


# Global instance
resource_allocator = ResourceAllocator()

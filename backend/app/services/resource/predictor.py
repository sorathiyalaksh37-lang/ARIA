"""
Resource Predictor Module - Machine Learning Hotspot & Demand Forecasting
Provides ML-based high-risk hotspot prediction and multi-resource demand forecasting.
"""

import logging
import pickle
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.incident import Incident
from app.models.hospital import Hospital
from app.models.ambulance import Ambulance

logger = logging.getLogger(__name__)

# Blood type standard population and emergency trauma demand weights
DEFAULT_BLOOD_DISTRIBUTION = {
    "O+": 0.38,
    "A+": 0.34,
    "B+": 0.09,
    "O-": 0.07,  # Universal donor - high trauma usage
    "A-": 0.06,
    "AB+": 0.03,
    "B-": 0.02,
    "AB-": 0.01,
}

# Trauma severity blood requirement multipliers (units per admission)
TRAUMA_BLOOD_MULTIPLIER = {
    "critical": 3.5,  # High blood loss expectation
    "high": 1.8,
    "medium": 0.5,
    "low": 0.1
}


class ResourcePredictor:
    """
    ML-based predictor for incident hotspots, hourly incident volume,
    ambulance demand, hospital bed demand, and blood type requirements.
    """

    def __init__(self):
        self.model_dir = Path(getattr(settings, "MODEL_PATH", "models"))
        self.hotspot_model = None
        self.demand_model = None
        self.severity_model = None
        
        # 6-Hour Cache mechanism for predictions
        self._cached_hotspots: Optional[List[Dict[str, Any]]] = None
        self._last_prediction_time: Optional[datetime] = None
        self._cache_validity_hours: int = 6

        self._load_models()

    def _load_models(self):
        """Attempt to load trained ML models from disk"""
        try:
            hotspot_path = self.model_dir / "hotspot_predictor.pkl"
            if hotspot_path.exists():
                with open(hotspot_path, "rb") as f:
                    self.hotspot_model = pickle.load(f)
                logger.info("✅ ML Hotspot prediction model loaded successfully")

            demand_path = self.model_dir / "demand_forecaster.pkl"
            if demand_path.exists():
                with open(demand_path, "rb") as f:
                    self.demand_model = pickle.load(f)
                logger.info("✅ ML Demand forecasting model loaded successfully")

            severity_path = self.model_dir / "severity_predictor.pkl"
            if severity_path.exists():
                with open(severity_path, "rb") as f:
                    self.severity_model = pickle.load(f)
                logger.info("✅ ML Severity predictor model loaded successfully")

        except Exception as e:
            logger.warning(f"Failed to load trained ML model file: {e}. Using fallback predictor.")

    def is_cache_valid(self) -> bool:
        """Check if cached predictions are within the 6-hour window"""
        if self._cached_hotspots is None or self._last_prediction_time is None:
            return False
        elapsed = (datetime.utcnow() - self._last_prediction_time).total_seconds() / 3600.0
        return elapsed < self._cache_validity_hours

    async def predict_hotspots(
        self,
        db: Session,
        hours_ahead: int = 24,
        grid_size: int = 40,
        force_refresh: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Predict high-risk hotspot areas for the next N hours.
        Updates every 6 hours unless force_refresh is True.
        """
        # Return cached hotspots if valid and not forcing refresh
        if not force_refresh and self.is_cache_valid():
            logger.info("Returning cached hotspot predictions (6h refresh cycle active)")
            return self._cached_hotspots or []

        try:
            # Query historical incidents for spatial grid analysis
            cutoff_date = datetime.utcnow() - timedelta(days=90)
            historical_incidents = db.query(Incident).filter(
                Incident.created_at >= cutoff_date
            ).all()

            # Default coordinates around San Francisco / Metropolitan Area if dataset empty
            default_lat_center, default_lng_center = 37.7749, -122.4194

            if historical_incidents:
                lats = [inc.latitude for inc in historical_incidents if inc.latitude is not None]
                lngs = [inc.longitude for inc in historical_incidents if inc.longitude is not None]
                lat_min, lat_max = (min(lats), max(lats)) if lats else (default_lat_center - 0.1, default_lat_center + 0.1)
                lng_min, lng_max = (min(lngs), max(lngs)) if lngs else (default_lng_center - 0.1, default_lng_center + 0.1)
            else:
                lat_min, lat_max = default_lat_center - 0.1, default_lat_center + 0.1
                lng_min, lng_max = default_lng_center - 0.1, default_lng_center + 0.1

            # Ensure minimal bounding window
            if lat_max - lat_min < 0.05:
                lat_min -= 0.05
                lat_max += 0.05
            if lng_max - lng_min < 0.05:
                lng_min -= 0.05
                lng_max += 0.05

            now = datetime.utcnow()
            target_time = now + timedelta(hours=hours_ahead)
            hour_of_day = target_time.hour
            day_of_week = target_time.weekday()
            is_weekend = 1 if day_of_week >= 5 else 0
            is_rush_hour = 1 if hour_of_day in [7, 8, 9, 17, 18, 19] else 0

            lat_step = (lat_max - lat_min) / grid_size
            lng_step = (lng_max - lng_min) / grid_size

            hotspots = []
            total_incidents = len(historical_incidents) or 1

            for i in range(grid_size):
                for j in range(grid_size):
                    lat = lat_min + (i + 0.5) * lat_step
                    lng = lng_min + (j + 0.5) * lng_step

                    # Spatial density calculation
                    nearby_count = 0
                    severe_count = 0
                    for inc in historical_incidents:
                        if inc.latitude and inc.longitude:
                            dist = np.sqrt((inc.latitude - lat) ** 2 + (inc.longitude - lng) ** 2)
                            if dist <= 0.03:  # ~3km radius
                                nearby_count += 1
                                if getattr(inc, "severity", "medium") in ["critical", "high"]:
                                    severe_count += 1

                    density_ratio = nearby_count / total_incidents

                    if self.hotspot_model and getattr(settings, "ENABLE_ML_PREDICTIONS", True):
                        try:
                            features = np.array([[lat, lng, hour_of_day, day_of_week, is_weekend, is_rush_hour, density_ratio]])
                            pred_val = float(self.hotspot_model.predict(features)[0])
                            risk_score = float(np.clip(pred_val, 0.0, 1.0))
                            confidence = float(np.clip(0.85 + (density_ratio * 0.15), 0.70, 0.99))
                        except Exception:
                            risk_score = float(np.clip(density_ratio * 15.0 + (0.2 if is_rush_hour else 0.0), 0.0, 1.0))
                            confidence = float(np.clip(0.75 + (density_ratio * 0.20), 0.65, 0.95))
                    else:
                        # Statistical fallback model
                        base = density_ratio * 18.0
                        time_factor = 1.25 if is_rush_hour else (0.85 if is_weekend else 1.0)
                        risk_score = float(np.clip(base * time_factor, 0.05, 0.98))
                        confidence = float(np.clip(0.78 + (density_ratio * 0.18), 0.65, 0.96))

                    # Filter out non-significant risk areas
                    if risk_score >= 0.25:
                        predicted_volume = max(1, int(round(risk_score * 6)))
                        hotspots.append({
                            "latitude": float(round(lat, 5)),
                            "longitude": float(round(lng, 5)),
                            "risk_score": float(round(risk_score, 3)),
                            "confidence_score": float(round(confidence, 3)),
                            "predicted_incidents": predicted_volume,
                            "target_hour": hour_of_day,
                            "grid_x": i,
                            "grid_y": j,
                            "timestamp": target_time.isoformat()
                        })

            # Sort by risk score descending
            hotspots.sort(key=lambda x: x["risk_score"], reverse=True)
            result_hotspots = hotspots[:100]

            # Cache updating
            self._cached_hotspots = result_hotspots
            self._last_prediction_time = datetime.utcnow()

            logger.info(f"Generated {len(result_hotspots)} predicted hotspots for next {hours_ahead}h")
            return result_hotspots

        except Exception as e:
            logger.error(f"Error predicting hotspots: {str(e)}", exc_info=True)
            return []

    async def forecast_demand(
        self,
        db: Session,
        hours_ahead: int = 24
    ) -> Dict[str, Any]:
        """
        Forecast hourly incident volume, ambulance demand, hospital bed demand,
        and blood type requirements for the next N hours.
        """
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            recent_incidents = db.query(Incident).filter(
                Incident.created_at >= cutoff_date
            ).all()

            # Baseline statistics
            hourly_counts = {h: 0 for h in range(24)}
            total_incidents = len(recent_incidents)
            days_count = max(1, 30)

            for inc in recent_incidents:
                h = inc.created_at.hour
                hourly_counts[h] += 1

            hourly_avg = {h: max(1.5, counts / days_count) for h, counts in hourly_counts.items()}

            now = datetime.utcnow()
            forecasts = []
            total_predicted_incidents = 0.0
            total_ambulance_units = 0
            total_beds_needed = 0
            blood_demand_aggregate = {bt: 0.0 for bt in DEFAULT_BLOOD_DISTRIBUTION.keys()}

            for step in range(hours_ahead):
                target_time = now + timedelta(hours=step)
                hour = target_time.hour
                day_of_week = target_time.weekday()
                is_weekend = day_of_week >= 5
                is_rush = hour in [7, 8, 9, 17, 18, 19]

                base_val = hourly_avg.get(hour, 2.5)
                multiplier = (1.35 if is_rush else 1.0) * (0.85 if is_weekend else 1.0)
                
                predicted_incidents = round(float(base_val * multiplier), 1)
                total_predicted_incidents += predicted_incidents

                # Ambulance demand: 85% of predicted incidents require immediate dispatch
                ambulance_demand = int(np.ceil(predicted_incidents * 0.85))
                total_ambulance_units += ambulance_demand

                # Hospital bed demand: 60% expected admission rate
                bed_demand = int(np.ceil(predicted_incidents * 0.60))
                total_beds_needed += bed_demand

                # Blood type demand forecasting:
                # ~35% of emergency admissions require blood transfusions (average 1.5 units per transfusion)
                transfusion_cases = predicted_incidents * 0.35
                units_needed = transfusion_cases * 1.5

                hourly_blood = {}
                for btype, percentage in DEFAULT_BLOOD_DISTRIBUTION.items():
                    # Universal donor O- receives 50% boost during emergency trauma surges
                    weight = percentage * (1.5 if btype == "O-" else 1.0)
                    units_for_type = round(units_needed * weight, 1)
                    hourly_blood[btype] = units_for_type
                    blood_demand_aggregate[btype] += units_for_type

                forecasts.append({
                    "timestamp": target_time.isoformat(),
                    "hour": hour,
                    "predicted_incidents": predicted_incidents,
                    "ambulance_demand": ambulance_demand,
                    "bed_demand": bed_demand,
                    "blood_type_demand": hourly_blood,
                    "confidence": round(0.80 + (0.15 if not is_weekend else 0.10), 2)
                })

            peak_forecast = max(forecasts, key=lambda x: x["predicted_incidents"]) if forecasts else {}

            return {
                "forecast_generated_at": now.isoformat(),
                "hours_ahead": hours_ahead,
                "total_predicted_incidents": round(total_predicted_incidents, 1),
                "total_ambulance_demand": total_ambulance_units,
                "total_bed_demand": total_beds_needed,
                "peak_hour": {
                    "hour": peak_forecast.get("hour"),
                    "timestamp": peak_forecast.get("timestamp"),
                    "predicted_incidents": peak_forecast.get("predicted_incidents"),
                    "ambulance_demand": peak_forecast.get("ambulance_demand")
                },
                "blood_demand_summary": {
                    btype: round(units, 1) for btype, units in blood_demand_aggregate.items()
                },
                "forecasts": forecasts,
                "next_cache_update": (self._last_prediction_time + timedelta(hours=6)).isoformat() if self._last_prediction_time else (now + timedelta(hours=6)).isoformat()
            }

        except Exception as e:
            logger.error(f"Error forecasting demand: {str(e)}", exc_info=True)
            return {"error": str(e)}


# Singleton instance
resource_predictor = ResourcePredictor()

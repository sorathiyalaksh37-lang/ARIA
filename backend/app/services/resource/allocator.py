"""
Resource Allocator Module - Proactive Positioning & Dynamic Resource Allocation
Handles ambulance prepositioning, hospital surge alerts, blood supply distribution, and real-time resource matching.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from app.models.incident import Incident
from app.models.ambulance import Ambulance
from app.models.hospital import Hospital

logger = logging.getLogger(__name__)


class ResourceAllocator:
    """
    Allocates and preposition emergency assets based on ML predictions,
    real-time incidents, hospital surge status, and blood stock requirements.
    """

    def calculate_distance_km(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Haversine distance calculation in kilometers"""
        R = 6371.0  # Earth radius in kilometers
        dlat = np.radians(lat2 - lat1)
        dlng = np.radians(lng2 - lng1)
        a = (np.sin(dlat / 2) ** 2 +
             np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlng / 2) ** 2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        return float(R * c)

    async def generate_prepositioning_plan(
        self,
        db: Session,
        hotspots: List[Dict[str, Any]],
        demand_forecast: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate proactive prepositioning recommendations:
        1. Ambulance repositioning to high-risk hotspots
        2. Hospital surge alerts based on predicted bed capacity overflow
        3. Blood supply prepositioning orders for hospitals
        """
        try:
            # 1. Fetch available ambulances
            ambulances = db.query(Ambulance).filter(
                Ambulance.status.in_(["available", "idle", "stationed"])
            ).all()

            # Fallback if status enum is different or empty
            if not ambulances:
                ambulances = db.query(Ambulance).all()

            ambulance_recommendations = []
            available_pool = [a for a in ambulances if getattr(a, "status", "available") in ["available", "idle", "stationed"]]

            sorted_hotspots = sorted(hotspots, key=lambda x: x.get("risk_score", 0), reverse=True)

            for hs in sorted_hotspots[:12]:
                if not available_pool:
                    break

                hs_lat, hs_lng = hs["latitude"], hs["longitude"]
                risk = hs["risk_score"]

                # Find closest available ambulance
                best_amb = None
                best_dist = float('inf')

                for amb in available_pool:
                    if amb.latitude is not None and amb.longitude is not None:
                        dist = self.calculate_distance_km(amb.latitude, amb.longitude, hs_lat, hs_lng)
                        if dist < best_dist:
                            best_dist = dist
                            best_amb = amb

                # Only move if ambulance is not already stationed right there (> 1.5 km away)
                if best_amb and best_dist > 1.5:
                    eta_mins = max(2, int(round((best_dist / 40.0) * 60)))  # 40 km/h avg speed
                    ambulance_recommendations.append({
                        "ambulance_id": str(best_amb.id),
                        "ambulance_identifier": getattr(best_amb, "ambulance_id", f"AMB-{best_amb.id}"),
                        "current_location": {
                            "latitude": float(best_amb.latitude),
                            "longitude": float(best_amb.longitude)
                        },
                        "target_hotspot_location": {
                            "latitude": float(hs_lat),
                            "longitude": float(hs_lng)
                        },
                        "distance_km": round(best_dist, 2),
                        "estimated_travel_minutes": eta_mins,
                        "risk_score": float(risk),
                        "confidence_score": float(hs.get("confidence_score", 0.85)),
                        "priority": "CRITICAL" if risk > 0.75 else "HIGH" if risk > 0.55 else "MEDIUM",
                        "action": "Reposition to high-risk coverage zone"
                    })
                    available_pool.remove(best_amb)

            # 2. Hospital Surge Alerts
            hospitals = db.query(Hospital).all()
            hospital_alerts = []

            total_predicted_beds = demand_forecast.get("total_bed_demand", 25)
            hospitals_count = max(1, len(hospitals))

            for hosp in hospitals:
                capacity = getattr(hosp, "total_beds", getattr(hosp, "bed_capacity", 100)) or 100
                available_beds = getattr(hosp, "available_beds", 30) or 30
                
                # Proactively assign projected admissions proportionate to hospital capacity
                projected_admissions = int(round(total_predicted_beds * (capacity / (hospitals_count * 100))))
                projected_remaining_beds = available_beds - projected_admissions
                utilization_percentage = round(((capacity - max(0, projected_remaining_beds)) / capacity) * 100, 1)

                is_surge = projected_remaining_beds < 5 or utilization_percentage > 85.0
                if is_surge:
                    hospital_alerts.append({
                        "hospital_id": str(hosp.id),
                        "hospital_name": getattr(hosp, "name", f"Hospital #{hosp.id}"),
                        "current_available_beds": available_beds,
                        "projected_24h_admissions": projected_admissions,
                        "projected_available_beds": projected_remaining_beds,
                        "projected_utilization_rate": utilization_percentage,
                        "alert_level": "RED_SURGE_WARNING" if projected_remaining_beds < 3 else "YELLOW_SURGE_ADVISORY",
                        "recommended_action": "Activate surge capacity, prep trauma bays & offload delays"
                    })

            # 3. Blood Supply Pre-positioning
            blood_summary = demand_forecast.get("blood_demand_summary", {})
            blood_preposition_orders = []

            if blood_summary and hospitals:
                # Top 3 busiest hospitals based on capacity
                sorted_hospitals = sorted(hospitals, key=lambda h: getattr(h, "bed_capacity", 100) or 100, reverse=True)[:3]
                
                for hosp in sorted_hospitals:
                    hosp_name = getattr(hosp, "name", f"Hospital #{hosp.id}")
                    # Universal donor O- and A+ pre-positioning requirements
                    o_neg_units = int(np.ceil(blood_summary.get("O-", 5.0) / len(sorted_hospitals)))
                    a_pos_units = int(np.ceil(blood_summary.get("A+", 10.0) / len(sorted_hospitals)))

                    blood_preposition_orders.append({
                        "hospital_id": str(hosp.id),
                        "hospital_name": hosp_name,
                        "preposition_units": {
                            "O-": max(2, o_neg_units),
                            "A+": max(3, a_pos_units),
                            "B+": max(1, int(blood_summary.get("B+", 2.0) / len(sorted_hospitals))),
                            "O+": max(3, int(blood_summary.get("O+", 8.0) / len(sorted_hospitals)))
                        },
                        "source_bank": "Central Emergency Blood Depot",
                        "priority": "HIGH_PREPOSITION",
                        "reason": f"Anticipated 24h trauma demand based on ML hotspot forecast"
                    })

            return {
                "generated_at": datetime.utcnow().isoformat(),
                "ambulance_prepositioning": ambulance_recommendations,
                "hospital_surge_alerts": hospital_alerts,
                "blood_preposition_orders": blood_preposition_orders,
                "summary": {
                    "total_ambulance_moves": len(ambulance_recommendations),
                    "hospitals_on_surge_alert": len(hospital_alerts),
                    "blood_transfer_orders": len(blood_preposition_orders)
                }
            }

        except Exception as e:
            logger.error(f"Error generating prepositioning plan: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "ambulance_prepositioning": [],
                "hospital_surge_alerts": [],
                "blood_preposition_orders": []
            }

    async def redistribute_realtime_resources(
        self,
        db: Session,
        active_incidents: List[Incident],
        ambulances: List[Ambulance]
    ) -> List[Dict[str, Any]]:
        """
        Dynamic real-time redistribution of active resources based on
        current unassigned incidents and fleet utilization.
        """
        redistributions = []

        unassigned_incidents = [inc for inc in active_incidents if getattr(inc, "status", "") in ["pending", "unassigned", "open"]]
        available_ambulances = [amb for amb in ambulances if getattr(amb, "status", "") in ["available", "idle", "stationed"]]

        for inc in unassigned_incidents:
            if not available_ambulances:
                break
            
            if inc.latitude is None or inc.longitude is None:
                continue

            nearest_amb = None
            min_dist = float('inf')

            for amb in available_ambulances:
                if amb.latitude is not None and amb.longitude is not None:
                    d = self.calculate_distance_km(amb.latitude, amb.longitude, inc.latitude, inc.longitude)
                    if d < min_dist:
                        min_dist = d
                        nearest_amb = amb

            if nearest_amb:
                redistributions.append({
                    "incident_id": str(inc.id),
                    "incident_severity": getattr(inc, "severity", "medium"),
                    "ambulance_id": str(nearest_amb.id),
                    "ambulance_identifier": getattr(nearest_amb, "ambulance_id", f"AMB-{nearest_amb.id}"),
                    "distance_km": round(min_dist, 2),
                    "estimated_arrival_minutes": max(1, int(round((min_dist / 45.0) * 60))),
                    "status": "DISPATCH_RECOMMENDED"
                })
                available_ambulances.remove(nearest_amb)

        return redistributions


# Singleton instance
resource_allocator = ResourceAllocator()

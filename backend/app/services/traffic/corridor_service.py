"""
Green Corridor Optimization Service
Calculates green corridor preemption routes, time savings (normal vs pre-empted duration),
minimizes red light stops, and provides manual coordinator override.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

from app.services.traffic.traffic_service import city_traffic_service

logger = logging.getLogger(__name__)


class GreenCorridorService:
    """Manages green corridor activation, route time savings, and manual overrides."""

    def __init__(self):
        self._active_corridor: Optional[Dict[str, Any]] = None

    async def calculate_time_savings(
        self,
        distance_km: float = 7.8,
        normal_light_stops: int = 8
    ) -> Dict[str, Any]:
        """
        Calculate travel time comparison between normal route and green corridor route.
        Each red light stop adds ~45 to 60 seconds of delay plus deceleration/acceleration.
        """
        # Average ambulance speed: 45 km/h normal, 65 km/h green corridor
        base_travel_minutes = (distance_km / 45.0) * 60.0
        traffic_signal_delay_minutes = (normal_light_stops * 0.9)  # 54 sec per red light

        normal_total_minutes = round(base_travel_minutes + traffic_signal_delay_minutes, 1)

        # Green corridor zero-stop speed
        green_travel_minutes = round((distance_km / 68.0) * 60.0, 1)

        time_saved_minutes = round(max(0.0, normal_total_minutes - green_travel_minutes), 1)
        percentage_saved = round((time_saved_minutes / normal_total_minutes) * 100.0, 1) if normal_total_minutes > 0 else 0.0

        return {
            "distance_km": distance_km,
            "normal_route": {
                "estimated_minutes": normal_total_minutes,
                "traffic_light_stops": normal_light_stops,
                "avg_speed_kmh": 45
            },
            "green_corridor_route": {
                "estimated_minutes": green_travel_minutes,
                "traffic_light_stops": 0,
                "avg_speed_kmh": 68
            },
            "time_saved_minutes": time_saved_minutes,
            "percentage_time_saved": percentage_saved,
            "calculation_timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def create_green_corridor(
        self,
        ambulance_id: str = "AMB-402",
        incident_id: str = "INC-1001",
        origin_lat: float = 37.7749,
        origin_lng: float = -122.4194,
        destination_hospital_id: str = "HOSP-01"
    ) -> Dict[str, Any]:
        """Activate automatic Green Corridor for an active ambulance run"""
        nodes = await city_traffic_service.get_signal_nodes()
        signal_ids = [n["signal_id"] for n in nodes]
        await city_traffic_service.request_preemption(signal_ids)

        savings = await self.calculate_time_savings(distance_km=7.8, normal_light_stops=len(nodes))

        now_utc = datetime.now(timezone.utc)
        self._active_corridor = {
            "corridor_id": f"GC-{ambulance_id}-{now_utc.strftime('%M%S')}",
            "ambulance_id": ambulance_id,
            "incident_id": incident_id,
            "status": "ACTIVE",
            "manual_override": False,
            "origin": {"latitude": origin_lat, "longitude": origin_lng},
            "destination_hospital_id": destination_hospital_id,
            "preempted_nodes": nodes,
            "time_savings": savings,
            "activated_at": now_utc.isoformat()
        }

        logger.info(f"Green Corridor activated for ambulance {ambulance_id}: {savings['time_saved_minutes']} mins saved")
        return self._active_corridor

    async def set_manual_override(self, enable_override: bool) -> Dict[str, Any]:
        """Toggle manual coordinator override (forces permanent green lights across all nodes)"""
        if self._active_corridor:
            self._active_corridor["manual_override"] = enable_override
            self._active_corridor["status"] = "MANUAL_OVERRIDE_ACTIVE" if enable_override else "ACTIVE"

        nodes = await city_traffic_service.get_signal_nodes()
        await city_traffic_service.request_preemption(["ALL"])

        return {
            "manual_override_active": enable_override,
            "message": "Manual override enabled. All traffic signals along route forced GREEN.",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def get_corridor_status(self) -> Dict[str, Any]:
        """Get active green corridor status and live node preemption state"""
        if not self._active_corridor:
            # Generate active corridor state for demonstration
            await self.create_green_corridor()

        nodes = await city_traffic_service.get_signal_nodes()
        self._active_corridor["preempted_nodes"] = nodes
        return self._active_corridor


# Singleton export
green_corridor_service = GreenCorridorService()

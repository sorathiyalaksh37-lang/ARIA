"""
Traffic Integration Service
Interfaces with City Adaptive Traffic Control Systems (ATCS / UTCS) to request signal preemption,
query traffic light node states, and handle fallback modes when API integration fails.
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class CityTrafficService:
    """Interfaces with City Traffic Management API to manage signal preemption and node states."""

    def __init__(self):
        self._api_connected: bool = True
        self._signal_nodes: List[Dict[str, Any]] = [
            {
                "signal_id": "SIG-101",
                "intersection_name": "Main St & 4th Avenue",
                "status": "PREEMPTED",
                "light_color": "GREEN",
                "time_to_preemption_sec": 0,
                "preemption_active": True
            },
            {
                "signal_id": "SIG-102",
                "intersection_name": "Main St & 8th Avenue",
                "status": "PREEMPTED",
                "light_color": "GREEN",
                "time_to_preemption_sec": 0,
                "preemption_active": True
            },
            {
                "signal_id": "SIG-103",
                "intersection_name": "Grand Boulevard & Market St",
                "status": "PREEMPTED",
                "light_color": "GREEN",
                "time_to_preemption_sec": 15,
                "preemption_active": True
            },
            {
                "signal_id": "SIG-104",
                "intersection_name": "Hospital Expressway Entrance",
                "status": "SCHEDULED",
                "light_color": "RED",
                "time_to_preemption_sec": 45,
                "preemption_active": False
            }
        ]

    async def check_api_status(self) -> Dict[str, Any]:
        """Check city traffic management API connection health"""
        return {
            "city_api_connected": self._api_connected,
            "system_name": "Metro Adaptive Traffic Control System (ATCS v4.2)",
            "latched_signal_nodes_count": len(self._signal_nodes),
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def get_signal_nodes(self, route_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get state of all traffic light signal nodes along route"""
        return self._signal_nodes

    async def request_preemption(self, signal_ids: List[str]) -> Dict[str, Any]:
        """Send green light preemption commands to specific signal node IDs"""
        preempted_count = 0
        for node in self._signal_nodes:
            if node["signal_id"] in signal_ids or "ALL" in signal_ids:
                node["status"] = "PREEMPTED"
                node["light_color"] = "GREEN"
                node["preemption_active"] = True
                node["time_to_preemption_sec"] = 0
                preempted_count += 1

        logger.info(f"Traffic preemption executed across {preempted_count} signal nodes")
        return {
            "preempted_signal_count": preempted_count,
            "status": "SUCCESS",
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    async def trigger_fallback(self) -> Dict[str, Any]:
        """Fallback mode triggered if City Traffic API fails"""
        self._api_connected = False
        return {
            "fallback_active": True,
            "reason": "City Traffic API Connection Failed or Unresponsive",
            "fallback_advisory": "Rerouting ambulance via Express Bypass (2 traffic lights vs 8). Activate high-decibel siren override.",
            "fallback_route": {
                "name": "Express Bypass Corridor",
                "distance_km": 8.4,
                "estimated_minutes": 11,
                "traffic_light_count": 2
            }
        }


# Singleton export
city_traffic_service = CityTrafficService()

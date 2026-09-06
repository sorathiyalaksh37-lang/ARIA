"""
Bystander Location & Resource Finder Module
Locates nearby CPR-certified civilians, AED defibrillators, pharmacies, clinics,
and generates Google Maps turn-by-turn navigation links.
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class BystanderLocationService:
    """Location service for CPR civilians, AEDs, pharmacies, and clinics."""

    def calculate_distance_km(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Haversine distance formula in kilometers"""
        R = 6371.0
        dlat = np.radians(lat2 - lat1)
        dlng = np.radians(lng2 - lng1)
        a = (np.sin(dlat / 2) ** 2 +
             np.cos(np.radians(lat1)) * np.cos(np.radians(lat2)) * np.sin(dlng / 2) ** 2)
        c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
        return float(round(R * c, 2))

    def generate_google_maps_nav_url(
        self,
        origin_lat: float,
        origin_lng: float,
        dest_lat: float,
        dest_lng: float
    ) -> str:
        """Generate Google Maps turn-by-turn navigation URL"""
        return f"https://www.google.com/maps/dir/?api=1&origin={origin_lat},{origin_lng}&destination={dest_lat},{dest_lng}&travelmode=walking"

    async def find_nearby_resources(
        self,
        incident_lat: float,
        incident_lng: float,
        radius_km: float = 3.0
    ) -> Dict[str, Any]:
        """
        Locate nearby CPR-certified civilians, AED defibrillators, pharmacies, and clinics.
        """
        try:
            # Synthetic / Simulated active emergency network data centered around incident lat/lng
            # 1. Nearby CPR Certified Civilians
            civilians = [
                {
                    "civilian_id": "CIV-901",
                    "name": "Dr. Rajesh Kumar",
                    "certification": "AHA CPR & AED Certified",
                    "distance_km": self.calculate_distance_km(incident_lat, incident_lng, incident_lat + 0.003, incident_lng - 0.002),
                    "eta_minutes": 2,
                    "phone": "+91-9876543210",
                    "status": "active_responder_en_route",
                    "latitude": incident_lat + 0.003,
                    "longitude": incident_lng - 0.002
                },
                {
                    "civilian_id": "CIV-904",
                    "name": "Priya Sharma",
                    "certification": "Red Cross First Aid Specialist",
                    "distance_km": self.calculate_distance_km(incident_lat, incident_lng, incident_lat - 0.004, incident_lng + 0.005),
                    "eta_minutes": 4,
                    "phone": "+91-9876500112",
                    "status": "notified",
                    "latitude": incident_lat - 0.004,
                    "longitude": incident_lng + 0.005
                }
            ]

            # 2. Nearby AED Defibrillators
            aeds = [
                {
                    "aed_id": "AED-SF-104",
                    "building_name": "Metro Transit Station Entrance B",
                    "address": "Platform Level 1, Near Escalator",
                    "latitude": incident_lat + 0.002,
                    "longitude": incident_lng + 0.001,
                    "distance_km": self.calculate_distance_km(incident_lat, incident_lng, incident_lat + 0.002, incident_lng + 0.001),
                    "walking_eta_minutes": 2,
                    "status": "OPERATIONAL",
                    "access_code": "4412",
                    "navigation_url": self.generate_google_maps_nav_url(incident_lat, incident_lng, incident_lat + 0.002, incident_lng + 0.001)
                },
                {
                    "aed_id": "AED-SF-209",
                    "building_name": "Central Mall Security Desk",
                    "address": "Ground Floor, Information Counter",
                    "latitude": incident_lat - 0.005,
                    "longitude": incident_lng - 0.003,
                    "distance_km": self.calculate_distance_km(incident_lat, incident_lng, incident_lat - 0.005, incident_lng - 0.003),
                    "walking_eta_minutes": 5,
                    "status": "OPERATIONAL",
                    "access_code": "OPEN 24/7",
                    "navigation_url": self.generate_google_maps_nav_url(incident_lat, incident_lng, incident_lat - 0.005, incident_lng - 0.003)
                }
            ]

            # 3. Nearby Pharmacies
            pharmacies = [
                {
                    "pharmacy_id": "PHARM-301",
                    "name": "Apollo 24/7 Pharmacy",
                    "address": "Main Market Road #45",
                    "phone": "+91-11-23456789",
                    "distance_km": self.calculate_distance_km(incident_lat, incident_lng, incident_lat + 0.008, incident_lng + 0.004),
                    "open_24h": True,
                    "stock_status": "Tourniquets, Gauze, AED, Burn Dressings in stock",
                    "navigation_url": self.generate_google_maps_nav_url(incident_lat, incident_lng, incident_lat + 0.008, incident_lng + 0.004)
                }
            ]

            # 4. Nearby Emergency Clinics
            clinics = [
                {
                    "clinic_id": "CLINIC-502",
                    "name": "City Urgent Care & Trauma Clinic",
                    "address": "4th Cross Avenue",
                    "emergency_phone": "+91-11-99887766",
                    "distance_km": self.calculate_distance_km(incident_lat, incident_lng, incident_lat - 0.009, incident_lng - 0.007),
                    "trauma_ready": True,
                    "navigation_url": self.generate_google_maps_nav_url(incident_lat, incident_lng, incident_lat - 0.009, incident_lng - 0.007)
                }
            ]

            return {
                "incident_location": {"latitude": incident_lat, "longitude": incident_lng},
                "search_radius_km": radius_km,
                "cpr_civilians": civilians,
                "aed_locations": aeds,
                "pharmacies": pharmacies,
                "emergency_clinics": clinics,
                "timestamp": datetime.utcnow().isoformat()
            }

        except Exception as e:
            logger.error(f"Error finding nearby bystander resources: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "cpr_civilians": [],
                "aed_locations": [],
                "pharmacies": [],
                "emergency_clinics": []
            }


# Singleton export
bystander_location_service = BystanderLocationService()

"""
Unified Geocoding Service with fallbacks.
Tries Google Maps first, then falls back to Nominatim.
"""
import logging
from typing import Optional, Dict, List, Tuple
import httpx

from app.services.maps.google_maps_service import google_maps_service

logger = logging.getLogger(__name__)


class NominatimService:
    """OpenStreetMap Nominatim geocoding service."""
    
    def __init__(self):
        """Initialize Nominatim client."""
        self.base_url = "https://nominatim.openstreetmap.org"
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={"User-Agent": "ARIA-Emergency-Response/1.0"}
        )
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    async def geocode(self, address: str) -> Optional[Dict]:
        """
        Geocode an address.
        
        Args:
            address: Address string
            
        Returns:
            Geocoding result
        """
        try:
            url = f"{self.base_url}/search"
            params = {
                "q": address,
                "format": "json",
                "limit": 1,
                "addressdetails": 1
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                return None
            
            result = data[0]
            
            return {
                "lat": float(result["lat"]),
                "lng": float(result["lon"]),
                "formatted_address": result["display_name"],
                "place_id": result["place_id"],
                "address_components": result.get("address", {})
            }
            
        except Exception as e:
            logger.error(f"Nominatim geocoding error: {e}")
            return None
    
    async def reverse_geocode(self, lat: float, lng: float) -> Optional[Dict]:
        """
        Reverse geocode coordinates.
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            Reverse geocoding result
        """
        try:
            url = f"{self.base_url}/reverse"
            params = {
                "lat": lat,
                "lon": lng,
                "format": "json",
                "addressdetails": 1
            }
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            return {
                "formatted_address": data["display_name"],
                "place_id": data["place_id"],
                "address_components": data.get("address", {})
            }
            
        except Exception as e:
            logger.error(f"Nominatim reverse geocoding error: {e}")
            return None


class GeocodingService:
    """
    Unified geocoding service with automatic fallback.
    Tries Google Maps first, then Nominatim.
    """
    
    def __init__(self):
        """Initialize geocoding service."""
        self.nominatim = NominatimService()
    
    async def geocode_address(self, address: str) -> Optional[Dict]:
        """
        Geocode an address with automatic fallback.
        
        Args:
            address: Address string
            
        Returns:
            {
                "lat": float,
                "lng": float,
                "formatted_address": str,
                "place_id": str,
                "provider": str  # "google" or "nominatim"
            }
        """
        # Try Google Maps first
        if google_maps_service.is_available():
            result = await google_maps_service.geocode_address(address)
            if result:
                result["provider"] = "google"
                logger.info(f"Geocoded with Google Maps: {address}")
                return result
            logger.warning("Google Maps geocoding failed, trying Nominatim")
        
        # Fallback to Nominatim
        result = await self.nominatim.geocode(address)
        if result:
            result["provider"] = "nominatim"
            logger.info(f"Geocoded with Nominatim: {address}")
            return result
        
        logger.error(f"All geocoding services failed for: {address}")
        return None
    
    async def reverse_geocode(self, lat: float, lng: float) -> Optional[Dict]:
        """
        Reverse geocode coordinates with automatic fallback.
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            Reverse geocoding result with provider info
        """
        # Try Google Maps first
        if google_maps_service.is_available():
            result = await google_maps_service.reverse_geocode(lat, lng)
            if result:
                result["provider"] = "google"
                return result
        
        # Fallback to Nominatim
        result = await self.nominatim.reverse_geocode(lat, lng)
        if result:
            result["provider"] = "nominatim"
            return result
        
        return None
    
    async def batch_geocode(self, addresses: List[str]) -> List[Optional[Dict]]:
        """
        Geocode multiple addresses.
        
        Args:
            addresses: List of address strings
            
        Returns:
            List of geocoding results
        """
        results = []
        for address in addresses:
            result = await self.geocode_address(address)
            results.append(result)
        return results
    
    async def validate_coordinates(
        self,
        lat: float,
        lng: float
    ) -> bool:
        """
        Validate if coordinates are valid.
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            True if valid
        """
        return -90 <= lat <= 90 and -180 <= lng <= 180
    
    def calculate_distance(
        self,
        point1: Tuple[float, float],
        point2: Tuple[float, float]
    ) -> float:
        """
        Calculate great circle distance between two points (Haversine formula).
        
        Args:
            point1: (lat, lng) tuple
            point2: (lat, lng) tuple
            
        Returns:
            Distance in kilometers
        """
        from math import radians, sin, cos, sqrt, atan2
        
        lat1, lon1 = point1
        lat2, lon2 = point2
        
        # Convert to radians
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        # Earth radius in km
        r = 6371
        
        return r * c
    
    async def close(self):
        """Close all connections."""
        await self.nominatim.close()


# Global instance
geocoding_service = GeocodingService()

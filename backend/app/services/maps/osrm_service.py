"""
OSRM (Open Source Routing Machine) Service
Fallback routing service when Google Maps is unavailable.
"""
import logging
from typing import List, Dict, Tuple, Optional
import httpx
import polyline

logger = logging.getLogger(__name__)


class OSRMService:
    """OSRM routing service as fallback."""
    
    def __init__(self, base_url: str = "http://router.project-osrm.org"):
        """
        Initialize OSRM client.
        
        Args:
            base_url: OSRM server URL (default: public server)
        """
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
    
    # ============================================================================
    # ROUTING
    # ============================================================================
    
    async def get_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        waypoints: Optional[List[Tuple[float, float]]] = None
    ) -> Optional[Dict]:
        """
        Get route between origin and destination.
        
        Args:
            origin: (lat, lng) tuple
            destination: (lat, lng) tuple
            waypoints: Optional list of (lat, lng) waypoints
            
        Returns:
            {
                "distance": int (meters),
                "duration": int (seconds),
                "geometry": str (polyline),
                "steps": List[Dict]
            }
        """
        try:
            # Build coordinates string: lng,lat
            coords = []
            coords.append(f"{origin[1]},{origin[0]}")
            
            if waypoints:
                for wp in waypoints:
                    coords.append(f"{wp[1]},{wp[0]}")
            
            coords.append(f"{destination[1]},{destination[0]}")
            coords_str = ";".join(coords)
            
            # Build URL
            url = f"{self.base_url}/route/v1/driving/{coords_str}"
            params = {
                "overview": "full",
                "steps": "true",
                "geometries": "polyline"
            }
            
            # Make request
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data["code"] != "Ok":
                logger.error(f"OSRM error: {data.get('message')}")
                return None
            
            route = data["routes"][0]
            
            return {
                "distance": route["distance"],  # meters
                "duration": route["duration"],  # seconds
                "geometry": route["geometry"],  # polyline encoded
                "legs": route["legs"],
                "weight": route.get("weight")
            }
            
        except httpx.HTTPError as e:
            logger.error(f"OSRM HTTP error: {e}")
            return None
        except Exception as e:
            logger.error(f"OSRM routing error: {e}")
            return None
    
    async def get_distance_matrix(
        self,
        origins: List[Tuple[float, float]],
        destinations: List[Tuple[float, float]]
    ) -> Optional[Dict]:
        """
        Get distance matrix.
        
        Args:
            origins: List of (lat, lng) tuples
            destinations: List of (lat, lng) tuples
            
        Returns:
            Distance matrix
        """
        try:
            # Combine all points
            all_points = origins + destinations
            coords = [f"{lng},{lat}" for lat, lng in all_points]
            coords_str = ";".join(coords)
            
            # Build sources and destinations indices
            sources_idx = ";".join(str(i) for i in range(len(origins)))
            dest_idx = ";".join(str(i) for i in range(len(origins), len(all_points)))
            
            # Build URL
            url = f"{self.base_url}/table/v1/driving/{coords_str}"
            params = {
                "sources": sources_idx,
                "destinations": dest_idx
            }
            
            # Make request
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data["code"] != "Ok":
                return None
            
            return {
                "durations": data["durations"],  # 2D array in seconds
                "distances": data.get("distances")  # 2D array in meters (if available)
            }
            
        except Exception as e:
            logger.error(f"OSRM distance matrix error: {e}")
            return None
    
    async def get_nearest_road(
        self,
        location: Tuple[float, float],
        number: int = 1
    ) -> Optional[List[Dict]]:
        """
        Get nearest road(s) to a location.
        
        Args:
            location: (lat, lng) tuple
            number: Number of nearest roads to return
            
        Returns:
            List of nearest roads
        """
        try:
            url = f"{self.base_url}/nearest/v1/driving/{location[1]},{location[0]}"
            params = {"number": number}
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data["code"] != "Ok":
                return None
            
            return data["waypoints"]
            
        except Exception as e:
            logger.error(f"OSRM nearest road error: {e}")
            return None
    
    def decode_polyline(self, encoded: str) -> List[Tuple[float, float]]:
        """
        Decode polyline to list of coordinates.
        
        Args:
            encoded: Polyline encoded string
            
        Returns:
            List of (lat, lng) tuples
        """
        try:
            return polyline.decode(encoded)
        except Exception as e:
            logger.error(f"Polyline decode error: {e}")
            return []
    
    def encode_polyline(self, coords: List[Tuple[float, float]]) -> str:
        """
        Encode coordinates to polyline.
        
        Args:
            coords: List of (lat, lng) tuples
            
        Returns:
            Polyline encoded string
        """
        try:
            return polyline.encode(coords)
        except Exception as e:
            logger.error(f"Polyline encode error: {e}")
            return ""


# Global instance
osrm_service = OSRMService()

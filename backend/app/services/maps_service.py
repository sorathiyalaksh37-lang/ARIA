"""
Google Maps API Integration Service
Provides geocoding, routing, distance matrix, and places functionality
"""
import logging
from typing import Dict, List, Optional, Tuple
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class MapsService:
    """Google Maps API service with error handling and fallbacks"""
    
    def __init__(self):
        self.api_key = settings.GOOGLE_MAPS_API_KEY
        self.base_url = "https://maps.googleapis.com/maps/api"
        self.timeout = 10.0
        self.max_retries = 3
        
    async def geocode(self, address: str) -> Optional[Dict]:
        """
        Convert address to coordinates
        
        Args:
            address: Street address to geocode
            
        Returns:
            Dict with lat, lng, formatted_address or None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/geocode/json",
                    params={
                        "address": address,
                        "key": self.api_key
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Geocoding API error: {response.status_code}")
                    return None
                    
                data = response.json()
                
                if data.get("status") != "OK" or not data.get("results"):
                    logger.warning(f"Geocoding failed for address: {address}")
                    return None
                    
                result = data["results"][0]
                location = result["geometry"]["location"]
                
                return {
                    "latitude": location["lat"],
                    "longitude": location["lng"],
                    "formatted_address": result["formatted_address"],
                    "place_id": result.get("place_id")
                }
                
        except httpx.TimeoutException:
            logger.error(f"Geocoding timeout for address: {address}")
            return None
        except Exception as e:
            logger.error(f"Geocoding error: {str(e)}")
            return None
    
    async def reverse_geocode(self, latitude: float, longitude: float) -> Optional[str]:
        """
        Convert coordinates to address
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            
        Returns:
            Formatted address string or None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/geocode/json",
                    params={
                        "latlng": f"{latitude},{longitude}",
                        "key": self.api_key
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Reverse geocoding API error: {response.status_code}")
                    return None
                    
                data = response.json()
                
                if data.get("status") != "OK" or not data.get("results"):
                    logger.warning(f"Reverse geocoding failed for: {latitude}, {longitude}")
                    return None
                    
                return data["results"][0]["formatted_address"]
                
        except Exception as e:
            logger.error(f"Reverse geocoding error: {str(e)}")
            return None
    
    async def calculate_route(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        waypoints: Optional[List[Tuple[float, float]]] = None
    ) -> Optional[Dict]:
        """
        Calculate route with traffic-aware directions
        
        Args:
            origin: (latitude, longitude) tuple
            destination: (latitude, longitude) tuple
            waypoints: Optional list of waypoint coordinates
            
        Returns:
            Dict with duration, distance, polyline, steps
        """
        try:
            params = {
                "origin": f"{origin[0]},{origin[1]}",
                "destination": f"{destination[0]},{destination[1]}",
                "key": self.api_key,
                "departure_time": "now",
                "traffic_model": "best_guess",
                "mode": "driving"
            }
            
            if waypoints:
                waypoints_str = "|".join([f"{lat},{lng}" for lat, lng in waypoints])
                params["waypoints"] = f"optimize:true|{waypoints_str}"
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/directions/json",
                    params=params
                )
                
                if response.status_code != 200:
                    logger.error(f"Directions API error: {response.status_code}")
                    return None
                    
                data = response.json()
                
                if data.get("status") != "OK" or not data.get("routes"):
                    logger.warning(f"Route calculation failed: {data.get('status')}")
                    return None
                    
                route = data["routes"][0]
                leg = route["legs"][0]
                
                return {
                    "duration_seconds": leg["duration"]["value"],
                    "duration_text": leg["duration"]["text"],
                    "duration_in_traffic_seconds": leg.get("duration_in_traffic", {}).get("value"),
                    "duration_in_traffic_text": leg.get("duration_in_traffic", {}).get("text"),
                    "distance_meters": leg["distance"]["value"],
                    "distance_text": leg["distance"]["text"],
                    "polyline": route["overview_polyline"]["points"],
                    "start_address": leg["start_address"],
                    "end_address": leg["end_address"],
                    "steps": [
                        {
                            "instruction": step["html_instructions"],
                            "distance": step["distance"]["text"],
                            "duration": step["duration"]["text"]
                        }
                        for step in leg["steps"]
                    ]
                }
                
        except Exception as e:
            logger.error(f"Route calculation error: {str(e)}")
            return None
    
    async def get_distance_matrix(
        self,
        origins: List[Tuple[float, float]],
        destinations: List[Tuple[float, float]]
    ) -> Optional[List[List[Dict]]]:
        """
        Calculate distance and duration matrix between multiple points
        
        Args:
            origins: List of origin coordinates
            destinations: List of destination coordinates
            
        Returns:
            2D list of distance/duration data or None
        """
        try:
            origins_str = "|".join([f"{lat},{lng}" for lat, lng in origins])
            destinations_str = "|".join([f"{lat},{lng}" for lat, lng in destinations])
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/distancematrix/json",
                    params={
                        "origins": origins_str,
                        "destinations": destinations_str,
                        "key": self.api_key,
                        "departure_time": "now",
                        "traffic_model": "best_guess",
                        "mode": "driving"
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Distance Matrix API error: {response.status_code}")
                    return None
                    
                data = response.json()
                
                if data.get("status") != "OK":
                    logger.warning(f"Distance matrix failed: {data.get('status')}")
                    return None
                    
                result = []
                for row in data["rows"]:
                    row_data = []
                    for element in row["elements"]:
                        if element["status"] == "OK":
                            row_data.append({
                                "distance_meters": element["distance"]["value"],
                                "distance_text": element["distance"]["text"],
                                "duration_seconds": element["duration"]["value"],
                                "duration_text": element["duration"]["text"],
                                "duration_in_traffic_seconds": element.get("duration_in_traffic", {}).get("value"),
                                "duration_in_traffic_text": element.get("duration_in_traffic", {}).get("text")
                            })
                        else:
                            row_data.append(None)
                    result.append(row_data)
                    
                return result
                
        except Exception as e:
            logger.error(f"Distance matrix error: {str(e)}")
            return None
    
    async def find_nearby_places(
        self,
        latitude: float,
        longitude: float,
        place_type: str = "hospital",
        radius: int = 5000
    ) -> Optional[List[Dict]]:
        """
        Find nearby places of a specific type
        
        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            place_type: Type of place (hospital, pharmacy, etc.)
            radius: Search radius in meters (max 50000)
            
        Returns:
            List of places with details or None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/place/nearbysearch/json",
                    params={
                        "location": f"{latitude},{longitude}",
                        "radius": min(radius, 50000),
                        "type": place_type,
                        "key": self.api_key
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Places API error: {response.status_code}")
                    return None
                    
                data = response.json()
                
                if data.get("status") not in ["OK", "ZERO_RESULTS"]:
                    logger.warning(f"Places search failed: {data.get('status')}")
                    return None
                    
                places = []
                for result in data.get("results", []):
                    places.append({
                        "name": result["name"],
                        "address": result.get("vicinity"),
                        "latitude": result["geometry"]["location"]["lat"],
                        "longitude": result["geometry"]["location"]["lng"],
                        "place_id": result["place_id"],
                        "rating": result.get("rating"),
                        "open_now": result.get("opening_hours", {}).get("open_now")
                    })
                    
                return places
                
        except Exception as e:
            logger.error(f"Places search error: {str(e)}")
            return None
    
    async def get_place_details(self, place_id: str) -> Optional[Dict]:
        """
        Get detailed information about a place
        
        Args:
            place_id: Google Place ID
            
        Returns:
            Dict with place details or None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/place/details/json",
                    params={
                        "place_id": place_id,
                        "fields": "name,formatted_address,formatted_phone_number,opening_hours,rating,website",
                        "key": self.api_key
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Place Details API error: {response.status_code}")
                    return None
                    
                data = response.json()
                
                if data.get("status") != "OK":
                    logger.warning(f"Place details failed: {data.get('status')}")
                    return None
                    
                result = data["result"]
                return {
                    "name": result.get("name"),
                    "address": result.get("formatted_address"),
                    "phone": result.get("formatted_phone_number"),
                    "website": result.get("website"),
                    "rating": result.get("rating"),
                    "open_now": result.get("opening_hours", {}).get("open_now"),
                    "weekday_text": result.get("opening_hours", {}).get("weekday_text", [])
                }
                
        except Exception as e:
            logger.error(f"Place details error: {str(e)}")
            return None


# Global instance
maps_service = MapsService()

"""
Google Maps API Integration Service
Provides geocoding, routing, places, and traffic services.
"""
import logging
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import googlemaps
from googlemaps import exceptions as gmaps_exceptions

from app.core.config import settings

logger = logging.getLogger(__name__)


class GoogleMapsService:
    """Google Maps API service for geocoding, routing, and places."""
    
    def __init__(self):
        """Initialize Google Maps client."""
        self.client = None
        if settings.GOOGLE_MAPS_API_KEY:
            try:
                self.client = googlemaps.Client(key=settings.GOOGLE_MAPS_API_KEY)
                logger.info("✅ Google Maps client initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Google Maps: {e}")
        else:
            logger.warning("⚠️ Google Maps API key not configured")
    
    def is_available(self) -> bool:
        """Check if Google Maps service is available."""
        return self.client is not None
    
    # ============================================================================
    # GEOCODING
    # ============================================================================
    
    async def geocode_address(self, address: str) -> Optional[Dict]:
        """
        Convert address to GPS coordinates.
        
        Args:
            address: Address string
            
        Returns:
            {
                "lat": float,
                "lng": float,
                "formatted_address": str,
                "place_id": str,
                "address_components": List[Dict]
            }
        """
        if not self.is_available():
            logger.error("Google Maps service not available")
            return None
        
        try:
            results = self.client.geocode(address)
            
            if not results:
                logger.warning(f"No results for address: {address}")
                return None
            
            result = results[0]
            location = result["geometry"]["location"]
            
            return {
                "lat": location["lat"],
                "lng": location["lng"],
                "formatted_address": result["formatted_address"],
                "place_id": result["place_id"],
                "address_components": result.get("address_components", []),
                "location_type": result["geometry"]["location_type"]
            }
            
        except gmaps_exceptions.ApiError as e:
            logger.error(f"Google Maps API error: {e}")
            return None
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return None
    
    async def reverse_geocode(self, lat: float, lng: float) -> Optional[Dict]:
        """
        Convert GPS coordinates to address.
        
        Args:
            lat: Latitude
            lng: Longitude
            
        Returns:
            {
                "formatted_address": str,
                "place_id": str,
                "address_components": List[Dict]
            }
        """
        if not self.is_available():
            return None
        
        try:
            results = self.client.reverse_geocode((lat, lng))
            
            if not results:
                return None
            
            result = results[0]
            
            return {
                "formatted_address": result["formatted_address"],
                "place_id": result["place_id"],
                "address_components": result.get("address_components", [])
            }
            
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
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
    
    # ============================================================================
    # ROUTING
    # ============================================================================
    
    async def get_directions(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        waypoints: Optional[List[Tuple[float, float]]] = None,
        mode: str = "driving",
        traffic_model: str = "best_guess",
        departure_time: Optional[datetime] = None
    ) -> Optional[Dict]:
        """
        Get directions between origin and destination.
        
        Args:
            origin: (lat, lng) tuple
            destination: (lat, lng) tuple
            waypoints: Optional list of (lat, lng) waypoints
            mode: Transportation mode (driving, walking, bicycling, transit)
            traffic_model: Traffic model (best_guess, pessimistic, optimistic)
            departure_time: Departure time for traffic prediction
            
        Returns:
            {
                "distance": {"value": int (meters), "text": str},
                "duration": {"value": int (seconds), "text": str},
                "duration_in_traffic": {"value": int (seconds), "text": str},
                "polyline": str,
                "steps": List[Dict],
                "bounds": Dict,
                "warnings": List[str]
            }
        """
        if not self.is_available():
            return None
        
        try:
            # Format waypoints
            waypoints_str = None
            if waypoints:
                waypoints_str = [f"{lat},{lng}" for lat, lng in waypoints]
            
            # Set departure time for traffic
            if departure_time is None:
                departure_time = datetime.now()
            
            # Get directions
            results = self.client.directions(
                origin=f"{origin[0]},{origin[1]}",
                destination=f"{destination[0]},{destination[1]}",
                waypoints=waypoints_str,
                mode=mode,
                departure_time=departure_time,
                traffic_model=traffic_model,
                alternatives=False
            )
            
            if not results:
                return None
            
            route = results[0]
            leg = route["legs"][0]
            
            return {
                "distance": leg["distance"],
                "duration": leg["duration"],
                "duration_in_traffic": leg.get("duration_in_traffic", leg["duration"]),
                "polyline": route["overview_polyline"]["points"],
                "steps": leg["steps"],
                "start_address": leg["start_address"],
                "end_address": leg["end_address"],
                "bounds": route["bounds"],
                "warnings": route.get("warnings", []),
                "summary": route.get("summary", "")
            }
            
        except Exception as e:
            logger.error(f"Directions error: {e}")
            return None
    
    async def get_multiple_routes(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float]
    ) -> List[Dict]:
        """
        Get multiple alternative routes.
        
        Args:
            origin: (lat, lng) tuple
            destination: (lat, lng) tuple
            
        Returns:
            List of route dictionaries
        """
        if not self.is_available():
            return []
        
        try:
            results = self.client.directions(
                origin=f"{origin[0]},{origin[1]}",
                destination=f"{destination[0]},{destination[1]}",
                mode="driving",
                departure_time=datetime.now(),
                alternatives=True
            )
            
            routes = []
            for route in results:
                leg = route["legs"][0]
                routes.append({
                    "distance": leg["distance"],
                    "duration": leg["duration"],
                    "duration_in_traffic": leg.get("duration_in_traffic", leg["duration"]),
                    "polyline": route["overview_polyline"]["points"],
                    "summary": route.get("summary", ""),
                    "warnings": route.get("warnings", [])
                })
            
            return routes
            
        except Exception as e:
            logger.error(f"Multiple routes error: {e}")
            return []
    
    async def get_distance_matrix(
        self,
        origins: List[Tuple[float, float]],
        destinations: List[Tuple[float, float]],
        mode: str = "driving"
    ) -> Optional[Dict]:
        """
        Get distance and duration matrix for multiple origins and destinations.
        
        Args:
            origins: List of (lat, lng) tuples
            destinations: List of (lat, lng) tuples
            mode: Transportation mode
            
        Returns:
            {
                "rows": List[{
                    "elements": List[{
                        "distance": {"value": int, "text": str},
                        "duration": {"value": int, "text": str},
                        "status": str
                    }]
                }]
            }
        """
        if not self.is_available():
            return None
        
        try:
            origins_str = [f"{lat},{lng}" for lat, lng in origins]
            destinations_str = [f"{lat},{lng}" for lat, lng in destinations]
            
            result = self.client.distance_matrix(
                origins=origins_str,
                destinations=destinations_str,
                mode=mode,
                departure_time=datetime.now()
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Distance matrix error: {e}")
            return None
    
    async def optimize_waypoints(
        self,
        origin: Tuple[float, float],
        destination: Tuple[float, float],
        waypoints: List[Tuple[float, float]]
    ) -> Optional[Dict]:
        """
        Get optimized order of waypoints.
        
        Args:
            origin: Starting point
            destination: Ending point
            waypoints: List of intermediate points
            
        Returns:
            Optimized route with waypoint order
        """
        if not self.is_available():
            return None
        
        try:
            waypoints_str = [f"{lat},{lng}" for lat, lng in waypoints]
            
            results = self.client.directions(
                origin=f"{origin[0]},{origin[1]}",
                destination=f"{destination[0]},{destination[1]}",
                waypoints=waypoints_str,
                optimize_waypoints=True,
                mode="driving"
            )
            
            if not results:
                return None
            
            route = results[0]
            
            return {
                "waypoint_order": route.get("waypoint_order", []),
                "route": route
            }
            
        except Exception as e:
            logger.error(f"Waypoint optimization error: {e}")
            return None
    
    # ============================================================================
    # PLACES API
    # ============================================================================
    
    async def search_nearby(
        self,
        location: Tuple[float, float],
        keyword: str,
        radius: int = 5000,
        place_type: Optional[str] = None
    ) -> List[Dict]:
        """
        Search for places near a location.
        
        Args:
            location: (lat, lng) tuple
            keyword: Search keyword (e.g., "hospital", "blood bank")
            radius: Search radius in meters (max 50000)
            place_type: Place type filter (e.g., "hospital", "pharmacy")
            
        Returns:
            List of places with details
        """
        if not self.is_available():
            return []
        
        try:
            results = self.client.places_nearby(
                location=location,
                keyword=keyword,
                radius=radius,
                type=place_type
            )
            
            places = []
            for place in results.get("results", []):
                places.append({
                    "place_id": place["place_id"],
                    "name": place["name"],
                    "address": place.get("vicinity", ""),
                    "location": place["geometry"]["location"],
                    "rating": place.get("rating"),
                    "types": place.get("types", []),
                    "open_now": place.get("opening_hours", {}).get("open_now")
                })
            
            return places
            
        except Exception as e:
            logger.error(f"Nearby search error: {e}")
            return []
    
    async def autocomplete_address(
        self,
        input_text: str,
        location: Optional[Tuple[float, float]] = None,
        radius: int = 50000
    ) -> List[Dict]:
        """
        Get address autocomplete suggestions.
        
        Args:
            input_text: Partial address input
            location: Optional location bias
            radius: Radius for location bias
            
        Returns:
            List of autocomplete predictions
        """
        if not self.is_available():
            return []
        
        try:
            results = self.client.places_autocomplete(
                input_text=input_text,
                location=location,
                radius=radius
            )
            
            predictions = []
            for prediction in results:
                predictions.append({
                    "place_id": prediction["place_id"],
                    "description": prediction["description"],
                    "structured_formatting": prediction.get("structured_formatting", {}),
                    "types": prediction.get("types", [])
                })
            
            return predictions
            
        except Exception as e:
            logger.error(f"Autocomplete error: {e}")
            return []
    
    async def get_place_details(self, place_id: str) -> Optional[Dict]:
        """
        Get detailed information about a place.
        
        Args:
            place_id: Google Places ID
            
        Returns:
            Place details
        """
        if not self.is_available():
            return None
        
        try:
            result = self.client.place(place_id)
            
            if result.get("status") != "OK":
                return None
            
            place = result["result"]
            
            return {
                "place_id": place["place_id"],
                "name": place["name"],
                "address": place.get("formatted_address"),
                "location": place["geometry"]["location"],
                "phone": place.get("formatted_phone_number"),
                "website": place.get("website"),
                "rating": place.get("rating"),
                "reviews": place.get("reviews", []),
                "opening_hours": place.get("opening_hours", {}),
                "types": place.get("types", [])
            }
            
        except Exception as e:
            logger.error(f"Place details error: {e}")
            return None


# Global instance
google_maps_service = GoogleMapsService()

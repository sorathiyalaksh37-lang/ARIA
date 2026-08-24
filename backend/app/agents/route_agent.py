"""
ARIA Route Agent
Calculates optimal routes between locations
"""
from typing import Optional, List
import httpx
from geopy.distance import geodesic

from app.agents.base_agent import BaseAgent
from app.agents.state import AgentState, RouteInfo, Location
from app.core.config import settings


class RouteAgent(BaseAgent):
    """
    Route Agent: Calculates optimal routes for ambulances.
    Uses Google Maps API (or OSRM for open-source alternative).
    """
    
    def __init__(
        self,
        max_retries: int = 3,
        routing_api: str = "osrm"  # "osrm" or "google"
    ):
        """
        Initialize route agent.
        
        Args:
            max_retries: Maximum retries
            routing_api: Routing API to use
        """
        super().__init__(name="RouteAgent", max_retries=max_retries)
        self.routing_api = routing_api
        self.osrm_base_url = "http://router.project-osrm.org"
    
    async def run(self, state: AgentState) -> AgentState:
        """
        Calculate optimal route from ambulance to hospital.
        
        Args:
            state: Current agent state
            
        Returns:
            Updated state with route information
        """
        self._log_state_update(
            "Starting route calculation",
            routing_api=self.routing_api
        )
        
        # Validate required data
        if not state.ambulances:
            self.logger.warning("⚠️ No ambulances selected - skipping route calculation")
            return state
        
        if not state.hospitals:
            self.logger.warning("⚠️ No hospitals selected - skipping route calculation")
            return state
        
        # Get best ambulance and hospital from state
        best_ambulance = state.ambulances[0]
        best_hospital = state.hospitals[0]
        
        # Calculate route: Ambulance -> Incident -> Hospital
        self.logger.info(
            f"🗺️ Calculating route: "
            f"{best_ambulance.registration_number} -> Incident -> {best_hospital.name}"
        )
        
        # Route segment 1: Ambulance to Incident
        route_to_incident = await self._calculate_route_segment(
            best_ambulance.current_location,
            state.incident.location
        )
        
        # Route segment 2: Incident to Hospital
        route_to_hospital = await self._calculate_route_segment(
            state.incident.location,
            best_hospital.location
        )
        
        # Combine routes
        total_distance = route_to_incident["distance_km"] + route_to_hospital["distance_km"]
        total_eta = route_to_incident["eta_minutes"] + route_to_hospital["eta_minutes"]
        
        # Create combined waypoints
        waypoints = [
            best_ambulance.current_location,
            state.incident.location,
            best_hospital.location
        ]
        
        # Combine instructions
        instructions = [
            "Phase 1: Ambulance to Incident Location",
            *route_to_incident["instructions"],
            "Phase 2: Pick up patient and proceed to hospital",
            *route_to_hospital["instructions"]
        ]
        
        # Create route info
        route_info = RouteInfo(
            route_id=f"ROUTE-{state.incident.incident_id}",
            from_location=best_ambulance.current_location,
            to_location=best_hospital.location,
            distance_km=round(total_distance, 2),
            eta_minutes=round(total_eta, 1),
            traffic_level=route_to_incident.get("traffic_level", "MODERATE"),
            waypoints=waypoints,
            instructions=instructions
        )
        
        # Update state
        state.route = route_info
        
        # Store in context
        state.context["total_route_distance"] = total_distance
        state.context["total_route_eta"] = total_eta
        
        self._log_state_update(
            "Route calculation completed",
            total_distance=f"{total_distance:.2f} km",
            total_eta=f"{total_eta:.1f} min"
        )
        
        return state
    
    async def _calculate_route_segment(
        self,
        from_location: Location,
        to_location: Location
    ) -> dict:
        """
        Calculate route between two locations.
        
        Args:
            from_location: Starting location
            to_location: Destination location
            
        Returns:
            Route segment data
        """
        if self.routing_api == "google" and hasattr(settings, "GOOGLE_MAPS_API_KEY"):
            return await self._calculate_route_google(from_location, to_location)
        else:
            return await self._calculate_route_osrm(from_location, to_location)
    
    async def _calculate_route_osrm(
        self,
        from_location: Location,
        to_location: Location
    ) -> dict:
        """
        Calculate route using OSRM (Open Source Routing Machine).
        
        Args:
            from_location: Starting location
            to_location: Destination location
            
        Returns:
            Route data dictionary
        """
        try:
            # Build OSRM API URL
            url = (
                f"{self.osrm_base_url}/route/v1/driving/"
                f"{from_location.longitude},{from_location.latitude};"
                f"{to_location.longitude},{to_location.latitude}"
                f"?overview=full&steps=true"
            )
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                data = response.json()
            
            if data["code"] != "Ok":
                raise ValueError(f"OSRM error: {data.get('message', 'Unknown error')}")
            
            route = data["routes"][0]
            
            # Extract route information
            distance_meters = route["distance"]
            duration_seconds = route["duration"]
            
            # Extract turn-by-turn instructions
            instructions = []
            if "legs" in route:
                for leg in route["legs"]:
                    if "steps" in leg:
                        for step in leg["steps"]:
                            if "maneuver" in step:
                                instruction = step["maneuver"].get("instruction", "Continue")
                                distance = step.get("distance", 0)
                                instructions.append(
                                    f"{instruction} ({int(distance)}m)"
                                )
            
            return {
                "distance_km": distance_meters / 1000,
                "eta_minutes": duration_seconds / 60,
                "instructions": instructions[:10],  # Limit to 10 steps
                "traffic_level": "MODERATE"  # OSRM doesn't provide real-time traffic
            }
            
        except Exception as e:
            self.logger.warning(f"OSRM route calculation failed: {e}, using fallback")
            return self._calculate_route_fallback(from_location, to_location)
    
    async def _calculate_route_google(
        self,
        from_location: Location,
        to_location: Location
    ) -> dict:
        """
        Calculate route using Google Maps Directions API.
        
        Args:
            from_location: Starting location
            to_location: Destination location
            
        Returns:
            Route data dictionary
        """
        try:
            # Build Google Maps API URL
            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                "origin": f"{from_location.latitude},{from_location.longitude}",
                "destination": f"{to_location.latitude},{to_location.longitude}",
                "mode": "driving",
                "departure_time": "now",
                "traffic_model": "pessimistic",
                "key": settings.GOOGLE_MAPS_API_KEY
            }
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
            
            if data["status"] != "OK":
                raise ValueError(f"Google Maps error: {data.get('status')}")
            
            route = data["routes"][0]
            leg = route["legs"][0]
            
            # Extract route information
            distance_meters = leg["distance"]["value"]
            duration_seconds = leg["duration_in_traffic"]["value"] if "duration_in_traffic" in leg else leg["duration"]["value"]
            
            # Extract instructions
            instructions = []
            for step in leg["steps"][:10]:  # Limit to 10 steps
                instruction = step["html_instructions"].replace("<b>", "").replace("</b>", "")
                distance = step["distance"]["text"]
                instructions.append(f"{instruction} ({distance})")
            
            # Determine traffic level
            if "duration_in_traffic" in leg:
                normal_duration = leg["duration"]["value"]
                traffic_duration = leg["duration_in_traffic"]["value"]
                traffic_ratio = traffic_duration / normal_duration
                
                if traffic_ratio > 1.5:
                    traffic_level = "SEVERE"
                elif traffic_ratio > 1.2:
                    traffic_level = "HIGH"
                elif traffic_ratio > 1.0:
                    traffic_level = "MODERATE"
                else:
                    traffic_level = "LOW"
            else:
                traffic_level = "MODERATE"
            
            return {
                "distance_km": distance_meters / 1000,
                "eta_minutes": duration_seconds / 60,
                "instructions": instructions,
                "traffic_level": traffic_level
            }
            
        except Exception as e:
            self.logger.warning(f"Google Maps route calculation failed: {e}, using fallback")
            return self._calculate_route_fallback(from_location, to_location)
    
    def _calculate_route_fallback(
        self,
        from_location: Location,
        to_location: Location
    ) -> dict:
        """
        Fallback route calculation using straight-line distance.
        
        Args:
            from_location: Starting location
            to_location: Destination location
            
        Returns:
            Estimated route data
        """
        # Calculate straight-line distance
        from_coords = (from_location.latitude, from_location.longitude)
        to_coords = (to_location.latitude, to_location.longitude)
        distance_km = geodesic(from_coords, to_coords).kilometers
        
        # Estimate road distance (1.4x straight line for urban areas)
        road_distance_km = distance_km * 1.4
        
        # Estimate ETA (average speed 40 km/h in urban areas)
        eta_minutes = (road_distance_km / 40) * 60
        
        return {
            "distance_km": road_distance_km,
            "eta_minutes": eta_minutes,
            "instructions": [
                "Route calculated using fallback method",
                f"Proceed {road_distance_km:.1f}km to destination",
                "Follow fastest route suggested by navigation"
            ],
            "traffic_level": "MODERATE"
        }

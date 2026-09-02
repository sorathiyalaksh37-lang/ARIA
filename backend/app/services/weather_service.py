"""
OpenWeatherMap API Integration Service
Provides weather data, forecasts, and weather alerts
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class WeatherService:
    """OpenWeatherMap API service for weather data"""
    
    def __init__(self):
        self.api_key = settings.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5"
        self.timeout = 10.0
        
    async def get_current_weather(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[Dict]:
        """
        Get current weather conditions
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Dict with weather data or None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/weather",
                    params={
                        "lat": latitude,
                        "lon": longitude,
                        "appid": self.api_key,
                        "units": "metric"
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Weather API error: {response.status_code}")
                    return None
                    
                data = response.json()
                
                return {
                    "temperature": data["main"]["temp"],
                    "feels_like": data["main"]["feels_like"],
                    "humidity": data["main"]["humidity"],
                    "pressure": data["main"]["pressure"],
                    "wind_speed": data["wind"]["speed"],
                    "wind_direction": data["wind"].get("deg"),
                    "visibility": data.get("visibility", 0) / 1000,  # Convert to km
                    "clouds": data["clouds"]["all"],
                    "condition": data["weather"][0]["main"],
                    "description": data["weather"][0]["description"],
                    "icon": data["weather"][0]["icon"],
                    "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).isoformat(),
                    "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).isoformat(),
                    "timestamp": datetime.fromtimestamp(data["dt"]).isoformat()
                }
                
        except httpx.TimeoutException:
            logger.error("Weather API timeout")
            return None
        except Exception as e:
            logger.error(f"Weather API error: {str(e)}")
            return None
    
    async def get_forecast(
        self,
        latitude: float,
        longitude: float,
        hours: int = 24
    ) -> Optional[List[Dict]]:
        """
        Get weather forecast
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            hours: Number of hours to forecast (max 120)
            
        Returns:
            List of forecast data points or None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/forecast",
                    params={
                        "lat": latitude,
                        "lon": longitude,
                        "appid": self.api_key,
                        "units": "metric",
                        "cnt": min(hours // 3, 40)  # API returns 3-hour intervals
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Forecast API error: {response.status_code}")
                    return None
                    
                data = response.json()
                
                forecasts = []
                for item in data["list"]:
                    forecasts.append({
                        "timestamp": datetime.fromtimestamp(item["dt"]).isoformat(),
                        "temperature": item["main"]["temp"],
                        "feels_like": item["main"]["feels_like"],
                        "humidity": item["main"]["humidity"],
                        "wind_speed": item["wind"]["speed"],
                        "clouds": item["clouds"]["all"],
                        "condition": item["weather"][0]["main"],
                        "description": item["weather"][0]["description"],
                        "precipitation_probability": item.get("pop", 0) * 100,
                        "rain_volume": item.get("rain", {}).get("3h", 0),
                        "snow_volume": item.get("snow", {}).get("3h", 0)
                    })
                
                return forecasts
                
        except Exception as e:
            logger.error(f"Forecast API error: {str(e)}")
            return None
    
    async def get_weather_alerts(
        self,
        latitude: float,
        longitude: float
    ) -> Optional[List[Dict]]:
        """
        Get weather alerts for location
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            List of weather alerts or None
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/onecall",
                    params={
                        "lat": latitude,
                        "lon": longitude,
                        "appid": self.api_key,
                        "exclude": "minutely,hourly,daily"
                    }
                )
                
                if response.status_code != 200:
                    logger.error(f"Weather alerts API error: {response.status_code}")
                    return None
                    
                data = response.json()
                
                if "alerts" not in data:
                    return []
                
                alerts = []
                for alert in data["alerts"]:
                    alerts.append({
                        "event": alert["event"],
                        "sender": alert.get("sender_name", "Unknown"),
                        "description": alert["description"],
                        "start": datetime.fromtimestamp(alert["start"]).isoformat(),
                        "end": datetime.fromtimestamp(alert["end"]).isoformat(),
                        "tags": alert.get("tags", [])
                    })
                
                return alerts
                
        except Exception as e:
            logger.error(f"Weather alerts API error: {str(e)}")
            return None
    
    async def check_severe_weather(
        self,
        latitude: float,
        longitude: float
    ) -> Dict:
        """
        Check if there's severe weather affecting emergency response
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            
        Returns:
            Dict with severe_weather flag and impact assessment
        """
        weather = await self.get_current_weather(latitude, longitude)
        alerts = await self.get_weather_alerts(latitude, longitude)
        
        if not weather:
            return {
                "severe_weather": False,
                "impact": "unknown",
                "details": "Unable to fetch weather data"
            }
        
        severe_conditions = []
        impact_score = 0
        
        # Check for severe conditions
        if weather["visibility"] < 1.0:  # < 1 km visibility
            severe_conditions.append("Poor visibility")
            impact_score += 3
        
        if weather["wind_speed"] > 15:  # > 15 m/s (54 km/h)
            severe_conditions.append("High winds")
            impact_score += 2
        
        if weather["condition"] in ["Thunderstorm", "Snow", "Tornado"]:
            severe_conditions.append(weather["condition"])
            impact_score += 3
        
        if weather["condition"] == "Rain" and weather.get("precipitation_probability", 0) > 70:
            severe_conditions.append("Heavy rain")
            impact_score += 1
        
        # Check alerts
        if alerts:
            for alert in alerts:
                if any(keyword in alert["event"].lower() for keyword in ["severe", "warning", "watch"]):
                    severe_conditions.append(f"Alert: {alert['event']}")
                    impact_score += 2
        
        # Determine impact level
        if impact_score >= 5:
            impact = "critical"
        elif impact_score >= 3:
            impact = "high"
        elif impact_score >= 1:
            impact = "moderate"
        else:
            impact = "low"
        
        return {
            "severe_weather": impact_score > 0,
            "impact": impact,
            "impact_score": impact_score,
            "conditions": severe_conditions,
            "weather": weather,
            "alerts": alerts or [],
            "recommendations": self._get_weather_recommendations(impact_score, severe_conditions)
        }
    
    def _get_weather_recommendations(
        self,
        impact_score: int,
        conditions: List[str]
    ) -> List[str]:
        """Generate recommendations based on weather conditions"""
        recommendations = []
        
        if impact_score >= 5:
            recommendations.append("Consider delaying non-critical transports")
            recommendations.append("Increase ambulance response times in estimates")
            recommendations.append("Alert all units of severe weather conditions")
        
        if impact_score >= 3:
            recommendations.append("Monitor weather conditions closely")
            recommendations.append("Advise drivers to exercise extreme caution")
        
        if "Poor visibility" in conditions:
            recommendations.append("Reduce speed, increase following distance")
            recommendations.append("Use hazard lights when appropriate")
        
        if "High winds" in conditions:
            recommendations.append("Watch for debris on roads")
            recommendations.append("Be cautious when passing high-profile vehicles")
        
        if any("Snow" in c or "Ice" in c for c in conditions):
            recommendations.append("Check tire chains and winter equipment")
            recommendations.append("Allow extra travel time")
        
        return recommendations
    
    async def get_route_weather(
        self,
        waypoints: List[tuple[float, float]]
    ) -> List[Dict]:
        """
        Get weather conditions along a route
        
        Args:
            waypoints: List of (latitude, longitude) tuples
            
        Returns:
            List of weather data for each waypoint
        """
        route_weather = []
        
        for lat, lon in waypoints:
            weather = await self.get_current_weather(lat, lon)
            if weather:
                route_weather.append({
                    "location": {"latitude": lat, "longitude": lon},
                    "weather": weather
                })
        
        return route_weather


# Global instance
weather_service = WeatherService()

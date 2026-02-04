"""WeatherAPI.com tool for weather information."""

import os
from typing import Any

import httpx

from .base_tool import BaseTool, ToolResult


class WeatherTool(BaseTool):
    """Tool for fetching weather information using WeatherAPI.com (free tier available)."""

    name = "weather"
    description = "Get current weather information for a city including temperature, humidity, and conditions"

    def __init__(self):
        self.base_url = "http://api.weatherapi.com/v1"
        self.api_key = os.getenv("WEATHER_API_KEY")

    @property
    def parameters_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name to get weather for (e.g., 'London', 'New York', 'Kanpur')",
                },
                "units": {
                    "type": "string",
                    "enum": ["metric", "imperial"],
                    "description": "Temperature units: 'metric' (Celsius) or 'imperial' (Fahrenheit)",
                    "default": "metric",
                },
            },
            "required": ["city"],
        }

    async def execute(self, **kwargs) -> ToolResult:
        """Fetch weather data for a city."""
        city = kwargs.get("city")
        units = kwargs.get("units", "metric")

        if not city:
            return ToolResult(success=False, error="Missing required parameter: city")

        if not self.api_key:
            return ToolResult(
                success=False,
                error="WEATHER_API_KEY environment variable is not set. Get your free API key from https://www.weatherapi.com/signup.aspx",
            )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # WeatherAPI.com current weather endpoint
                url = f"{self.base_url}/current.json"
                params = {
                    "key": self.api_key,
                    "q": city,
                    "aqi": "no"  # Air quality data not needed for basic weather
                }

                response = await client.get(url, params=params)

                if response.status_code == 400:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", f"City '{city}' not found")
                    return ToolResult(success=False, error=error_msg)
                
                if response.status_code == 401:
                    return ToolResult(
                        success=False, 
                        error="Invalid API key. Please check your WEATHER_API_KEY in .env file"
                    )

                response.raise_for_status()
                data = response.json()

                location = data["location"]
                current = data["current"]

                # Use the appropriate temperature field based on units
                if units == "metric":
                    temp = current["temp_c"]
                    feels_like = current["feelslike_c"]
                    wind_speed = current["wind_kph"]
                    temp_unit = "°C"
                    speed_unit = "km/h"
                else:
                    temp = current["temp_f"]
                    feels_like = current["feelslike_f"]
                    wind_speed = current["wind_mph"]
                    temp_unit = "°F"
                    speed_unit = "mph"

                return ToolResult(
                    success=True,
                    data={
                        "city": location["name"],
                        "country": location["country"],
                        "temperature": f"{temp}{temp_unit}",
                        "feels_like": f"{feels_like}{temp_unit}",
                        "humidity": f"{current['humidity']}%",
                        "conditions": current["condition"]["text"],
                        "wind_speed": f"{wind_speed} {speed_unit}",
                        "visibility": f"{current['vis_km']} km" if units == "metric" else f"{current['vis_miles']} miles",
                    },
                )

        except httpx.TimeoutException:
            return ToolResult(success=False, error="Weather API request timed out")
        except httpx.HTTPStatusError as e:
            return ToolResult(success=False, error=f"Weather API HTTP error: {e.response.status_code}")
        except Exception as e:
            return ToolResult(success=False, error=f"Weather API error: {str(e)}")

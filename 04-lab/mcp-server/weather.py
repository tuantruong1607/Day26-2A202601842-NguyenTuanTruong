from typing import Any
import httpx
import logging
import os
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastMCP server
port = int(os.getenv("PORT", 8085))
mcp = FastMCP("weather", host="0.0.0.0", port=port)
logger = logging.getLogger(__name__)
# httpx logs full query strings at INFO, which would expose WEATHERAPI_KEY.
logging.getLogger("httpx").setLevel(logging.WARNING)

# Constants
WEATHERAPI_BASE = "https://api.weatherapi.com/v1"
USER_AGENT = "weather-app/1.0"

async def make_weather_request(endpoint: str, params: dict[str, str]) -> dict[str, Any] | None:
    """Make a request to the WeatherAPI with proper error handling."""
    api_key = os.getenv("WEATHERAPI_KEY")
    if not api_key:
        logger.warning("WEATHERAPI_KEY is not set; using local demo weather data")
        return None

    headers = {
        "User-Agent": USER_AGENT,
    }
    request_params = {**params, "key": api_key}

    url = f"{WEATHERAPI_BASE}/{endpoint}"

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                url,
                headers=headers,
                params=request_params,
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.warning(
                "WeatherAPI returned HTTP %s: %s",
                e.response.status_code,
                e.response.text,
            )
            return None
        except httpx.RequestError as e:
            logger.warning("WeatherAPI request failed (%s)", type(e).__name__)
            return None
        except (KeyError, TypeError, ValueError) as e:
            logger.warning("WeatherAPI returned an invalid response: %s", e)
            return None

_MOCK_WEATHER = {
    "hanoi": {
        "location": {"name": "Hanoi", "region": "Hanoi", "country": "Vietnam"},
        "current": {
            "temp_c": 29.0, "temp_f": 84.2,
            "feelslike_c": 32.0, "feelslike_f": 89.6,
            "condition": {"text": "Trời mưa nhẹ"},
            "humidity": 82,
            "wind_kph": 12.0, "wind_mph": 7.5, "wind_dir": "SE",
            "pressure_mb": 1008.0,
            "uv": 3.0,
            "vis_km": 10.0,
            "last_updated": "2026-08-28 15:30"
        },
        "forecast": {
            "forecastday": [
                {
                    "date": "2026-08-28",
                    "day": {
                        "maxtemp_c": 31.0, "maxtemp_f": 87.8,
                        "mintemp_c": 25.0, "mintemp_f": 77.0,
                        "condition": {"text": "Mưa rào nhẹ"},
                        "daily_chance_of_rain": 80,
                        "maxwind_kph": 15.0,
                        "uv": 4.0
                    }
                },
                {
                    "date": "2026-08-29",
                    "day": {
                        "maxtemp_c": 32.0, "maxtemp_f": 89.6,
                        "mintemp_c": 26.0, "mintemp_f": 78.8,
                        "condition": {"text": "Nhiều mây"},
                        "daily_chance_of_rain": 40,
                        "maxwind_kph": 12.0,
                        "uv": 6.0
                    }
                },
                {
                    "date": "2026-08-30",
                    "day": {
                        "maxtemp_c": 33.0, "maxtemp_f": 91.4,
                        "mintemp_c": 26.0, "mintemp_f": 78.8,
                        "condition": {"text": "Có nắng"},
                        "daily_chance_of_rain": 10,
                        "maxwind_kph": 10.0,
                        "uv": 8.0
                    }
                }
            ]
        }
    },
    "brisbane": {
        "location": {"name": "Brisbane", "region": "Queensland", "country": "Australia"},
        "current": {
            "temp_c": 21.0, "temp_f": 69.8,
            "feelslike_c": 21.0, "feelslike_f": 69.8,
            "condition": {"text": "Sunny"},
            "humidity": 60,
            "wind_kph": 15.0, "wind_mph": 9.3, "wind_dir": "NE",
            "pressure_mb": 1018.0,
            "uv": 5.0,
            "vis_km": 10.0,
            "last_updated": "2026-08-28 15:30"
        },
        "forecast": {
            "forecastday": [
                {
                    "date": "2026-08-28",
                    "day": {
                        "maxtemp_c": 22.0, "maxtemp_f": 71.6,
                        "mintemp_c": 12.0, "mintemp_f": 53.6,
                        "condition": {"text": "Sunny"},
                        "daily_chance_of_rain": 0,
                        "maxwind_kph": 18.0,
                        "uv": 6.0
                    }
                },
                {
                    "date": "2026-08-29",
                    "day": {
                        "maxtemp_c": 24.0, "maxtemp_f": 75.2,
                        "mintemp_c": 13.0, "mintemp_f": 55.4,
                        "condition": {"text": "Sunny"},
                        "daily_chance_of_rain": 0,
                        "maxwind_kph": 12.0,
                        "uv": 6.0
                    }
                },
                {
                    "date": "2026-08-30",
                    "day": {
                        "maxtemp_c": 25.0, "maxtemp_f": 77.0,
                        "mintemp_c": 14.0, "mintemp_f": 57.2,
                        "condition": {"text": "Partly Cloudy"},
                        "daily_chance_of_rain": 10,
                        "maxwind_kph": 10.0,
                        "uv": 5.0
                    }
                }
            ]
        }
    }
}

def get_mock_data(city: str) -> dict:
    city_lower = city.strip().casefold()
    if city_lower in _MOCK_WEATHER:
        return _MOCK_WEATHER[city_lower]
    return {
        "location": {"name": city.capitalize(), "region": "Local Region", "country": "World"},
        "current": {
            "temp_c": 25.0, "temp_f": 77.0,
            "feelslike_c": 26.0, "feelslike_f": 78.8,
            "condition": {"text": "Partly Cloudy"},
            "humidity": 70,
            "wind_kph": 10.0, "wind_mph": 6.2, "wind_dir": "N",
            "pressure_mb": 1013.0,
            "uv": 5.0,
            "vis_km": 10.0,
            "last_updated": "2026-08-28 15:30"
        },
        "forecast": {
            "forecastday": [
                {
                    "date": "2026-08-28",
                    "day": {
                        "maxtemp_c": 28.0, "maxtemp_f": 82.4,
                        "mintemp_c": 20.0, "mintemp_f": 68.0,
                        "condition": {"text": "Partly Cloudy"},
                        "daily_chance_of_rain": 20,
                        "maxwind_kph": 12.0,
                        "uv": 5.0
                    }
                },
                {
                    "date": "2026-08-29",
                    "day": {
                        "maxtemp_c": 29.0, "maxtemp_f": 84.2,
                        "mintemp_c": 21.0, "mintemp_f": 69.8,
                        "condition": {"text": "Cloudy"},
                        "daily_chance_of_rain": 40,
                        "maxwind_kph": 15.0,
                        "uv": 4.0
                    }
                },
                {
                    "date": "2026-08-30",
                    "day": {
                        "maxtemp_c": 27.0, "maxtemp_f": 80.6,
                        "mintemp_c": 19.0, "mintemp_f": 66.2,
                        "condition": {"text": "Rainy"},
                        "daily_chance_of_rain": 70,
                        "maxwind_kph": 18.0,
                        "uv": 3.0
                    }
                }
            ]
        }
    }


def format_location(location: dict[str, Any]) -> str:
    """Join non-empty location fields without duplicate separators."""
    parts = (location.get("name"), location.get("region"), location.get("country"))
    return ", ".join(str(part) for part in parts if part)

@mcp.tool()
async def get_current_weather(city: str) -> str:
    """Get current weather conditions for a city.

    Args:
        city: City name (e.g., "Hanoi", "Haiphong", "Danang", "Brisbane", "Sydney")
    """
    city = city.strip()
    if not city:
        raise ValueError("city must not be empty")

    params = {
        "q": city,
        "aqi": "no"
    }
    
    data = await make_weather_request("current.json", params)

    if not data:
        logger.info("Using local demo weather data for %s", city)
        data = get_mock_data(city)

    current = data["current"]
    location = data["location"]
    
    return f"""Current Weather for {format_location(location)}:

Temperature: {current['temp_c']}°C ({current['temp_f']}°F)
Feels like: {current['feelslike_c']}°C ({current['feelslike_f']}°F)
Condition: {current['condition']['text']}
Humidity: {current['humidity']}%
Wind: {current['wind_kph']} km/h ({current['wind_mph']} mph) {current['wind_dir']}
Pressure: {current['pressure_mb']} mb
UV Index: {current['uv']}
Visibility: {current['vis_km']} km

Last updated: {current['last_updated']}"""

@mcp.tool()
async def get_forecast(city: str, days: int = 3) -> str:
    """Get weather forecast for a city.

    Args:
        city: City name (e.g., "Hanoi", "Haiphong", "Danang", "Brisbane", "Sydney", "Melbourne")
        days: Number of days to forecast (1-3 for free tier, max 10 for paid)
    """
    city = city.strip()
    if not city:
        raise ValueError("city must not be empty")

    # WeatherAPI's free tier supports 1-3 days.
    days = max(1, min(days, 3))

    params = {
        "q": city,
        "days": str(days),
        "aqi": "no",
        "alerts": "no"
    }
    
    data = await make_weather_request("forecast.json", params)

    if not data:
        logger.info("Using local demo forecast data for %s", city)
        data = get_mock_data(city)

    location = data["location"]
    forecast_days = data["forecast"]["forecastday"][:days]
    
    forecasts = []
    forecasts.append(f"Weather Forecast for {format_location(location)}:")
    
    for day in forecast_days:
        day_data = day["day"]
        date = day["date"]
        
        forecast = f"""{date}:
High: {day_data['maxtemp_c']}°C ({day_data['maxtemp_f']}°F)
Low: {day_data['mintemp_c']}°C ({day_data['mintemp_f']}°F)
Condition: {day_data['condition']['text']}
Chance of Rain: {day_data['daily_chance_of_rain']}%
Max Wind: {day_data['maxwind_kph']} km/h
UV Index: {day_data['uv']}"""
        forecasts.append(forecast)

    return "\n---\n".join(forecasts)

@mcp.tool()
async def health_check() -> str:
    """Health check endpoint for deployment verification."""
    return "Weather MCP Server is running and ready to provide weather data."

if __name__ == "__main__":
    print(f"Starting Weather MCP server on http://0.0.0.0:{port}/mcp")
    mcp.run(transport="streamable-http")

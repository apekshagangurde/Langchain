import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather")

_GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

_WEATHER_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


@mcp.tool()
def get_weather(city: str) -> str:
    """Get the current weather (temperature, wind speed, condition) for a city.

    Uses the free Open-Meteo API (no API key required) — first geocodes the
    city name to coordinates, then fetches the current weather for that spot.

    Args:
        city: Name of the city to look up, e.g. "Mumbai" or "New York".
    """
    try:
        with httpx.Client(timeout=10, follow_redirects=True) as client:
            geo_response = client.get(_GEOCODE_URL, params={"name": city, "count": 1})
            geo_response.raise_for_status()
            geo_results = geo_response.json().get("results")
            if not geo_results:
                return f"Could not find a location matching '{city}'."

            place = geo_results[0]
            latitude, longitude = place["latitude"], place["longitude"]

            weather_response = client.get(
                _FORECAST_URL,
                params={
                    "latitude": latitude,
                    "longitude": longitude,
                    "current_weather": "true",
                },
            )
            weather_response.raise_for_status()
            current = weather_response.json()["current_weather"]

        condition = _WEATHER_CODES.get(current["weathercode"], "Unknown")
        location_label = f"{place['name']}, {place.get('country', '')}".strip(", ")
        return (
            f"Weather in {location_label}: {condition}, "
            f"{current['temperature']}°C, wind {current['windspeed']} km/h."
        )
    except Exception as exc:
        return f"Error fetching weather: {exc}"


if __name__ == "__main__":
    mcp.run(transport="stdio")

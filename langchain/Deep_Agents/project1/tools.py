"""
Tools for TripMate
==================

Built one tool at a time. Each new tool is added here, wired into agent.py,
and tested before the next one.

    Tool            Status
    --------------  ---------------------------------------------
    get_weather     ✅ step 7 — real forecast via Open-Meteo (free, no API key)
    search_places   ✅ step 6 — real web search via Tavily

search_places needs TAVILY_API_KEY in project1/.env (pip install langchain-tavily).
"""

import httpx
from langchain.tools import tool
from langchain_tavily import TavilySearch

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather codes used by Open-Meteo -> plain words.
WEATHER_CODES = {
    0: "clear sky", 1: "mainly clear", 2: "partly cloudy", 3: "overcast",
    45: "fog", 48: "freezing fog",
    51: "light drizzle", 53: "drizzle", 55: "heavy drizzle",
    56: "freezing drizzle", 57: "heavy freezing drizzle",
    61: "light rain", 63: "rain", 65: "heavy rain",
    66: "freezing rain", 67: "heavy freezing rain",
    71: "light snow", 73: "snow", 75: "heavy snow", 77: "snow grains",
    80: "light showers", 81: "showers", 82: "violent showers",
    85: "snow showers", 86: "heavy snow showers",
    95: "thunderstorm", 96: "thunderstorm with hail", 99: "severe thunderstorm with hail",
}


@tool
def get_weather(city: str, days: int = 3, country_code: str = "") -> str:
    """Get the real daily weather forecast for a city (up to 16 days ahead).

    Args:
        city: City or town name, e.g. "Mahabaleshwar".
        days: Number of days to forecast, starting today (1-16).
        country_code: Optional 2-letter country code to pick the right place,
            e.g. "IN" for India. Use it when the city name is ambiguous.
    """
    days = max(1, min(int(days), 16))
    try:
        # 1. City name -> latitude/longitude
        params = {"name": city, "count": 1, "language": "en", "format": "json"}
        if country_code:
            params["countryCode"] = country_code.upper()
        geo = httpx.get(GEOCODE_URL, params=params, timeout=15).json()
        if not geo.get("results"):
            return (
                f"Could not find a place called {city}. "
                f"Ask the user to check the spelling and give the correct town name."
            )
        place = geo["results"][0]

        # 2. Latitude/longitude -> daily forecast
        forecast = httpx.get(
            FORECAST_URL,
            params={
                "latitude": place["latitude"],
                "longitude": place["longitude"],
                "timezone": "auto",
                "forecast_days": days,
                "daily": "weather_code,temperature_2m_max,temperature_2m_min,"
                "precipitation_probability_max,precipitation_sum,wind_speed_10m_max",
            },
            timeout=15,
        ).json()
    except httpx.HTTPError as e:
        return f"Weather lookup failed for {city}: {e}"

    daily = forecast.get("daily")
    if not daily:
        return f"No forecast available for {city}: {forecast.get('reason', 'unknown error')}"

    where = ", ".join(p for p in (place.get("name"), place.get("admin1"), place.get("country")) if p)
    lines = [f"Forecast for {where}:"]
    for i, date in enumerate(daily["time"]):
        sky = WEATHER_CODES.get(daily["weather_code"][i], "unknown")
        lines.append(
            f"- {date}: {sky}, {daily['temperature_2m_min'][i]}–{daily['temperature_2m_max'][i]}°C, "
            f"rain chance {daily['precipitation_probability_max'][i]}% "
            f"({daily['precipitation_sum'][i]} mm), wind up to {daily['wind_speed_10m_max'][i]} km/h"
        )
    return "\n".join(lines)


_tavily = None


def _get_tavily() -> TavilySearch:
    """Create the Tavily client on first use (after .env is loaded), then reuse it."""
    global _tavily
    if _tavily is None:
        _tavily = TavilySearch(
            max_results=6,
            search_depth="advanced",  # better quality results for travel queries
            include_answer=True,  # short summary written by Tavily
        )
    return _tavily


@tool
def search_places(city: str, interests: str = "") -> str:
    """Search the web for the best places to visit in a city.

    Args:
        city: City or town to search, e.g. "Mahabaleshwar".
        interests: Optional focus, e.g. "nature viewpoints", "historic forts",
            "vegetarian food", "kid friendly". Leave empty for top attractions.
    """
    query = f"best places to visit in {city}"
    if interests:
        query += f" for {interests}"
    query += " tourist attractions travel guide"

    try:
        data = _get_tavily().invoke({"query": query})
    except Exception as e:  # network / key / quota problems
        return f"Place search failed for {city}: {e}"

    results = data.get("results", []) if isinstance(data, dict) else []
    if not results:
        return f"No places found for {city}."

    # Keep the output short so it doesn't flood the agent's context.
    lines = [f"Search: {query}"]
    if data.get("answer"):
        lines.append(f"Summary: {data['answer']}")
    lines.append("Sources:")
    for r in results:
        snippet = " ".join(r.get("content", "").split())[:300]
        lines.append(f"- {r.get('title', '')} ({r.get('url', '')})\n  {snippet}")
    return "\n".join(lines)

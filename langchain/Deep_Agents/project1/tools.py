"""
Tools for TripMate
==================

Built one tool at a time. Each new tool is added here, wired into agent.py,
and tested before the next one.

    Tool            Status
    --------------  ---------------------------
    get_weather     ✅ added (step 2)
    get_places      ⏳ next
    get_trip_cost   ⏳
    book_hotel      ⏳ (later: human approval)

Data is fake and hard-coded so the focus stays on the agent.
"""

from langchain.tools import tool

WEATHER = {
    "lonavala": "24°C, misty with light drizzle",
    "mahabaleshwar": "19°C, cool and clear",
    "goa": "30°C, sunny and humid",
}


@tool
def get_weather(city: str) -> str:
    """Return this weekend's weather forecast for a city."""
    return WEATHER.get(city.lower(), f"No weather data for {city}.")

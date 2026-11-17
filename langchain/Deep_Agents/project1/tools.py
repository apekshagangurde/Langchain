"""
Tools for TripMate
==================

Built one tool at a time. Each new tool is added here, wired into agent.py,
and tested before the next one.

    Tool            Status
    --------------  ---------------------------
    get_weather     ✅ added (step 2)
    get_places      ✅ added (step 3)

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


PLACES = {
    "lonavala": ["Tiger Point", "Bhushi Dam", "Karla Caves", "Della Adventure Park"],
    "mahabaleshwar": ["Venna Lake", "Arthur's Seat", "Mapro Garden", "Pratapgad Fort"],
    "goa": ["Baga Beach", "Fort Aguada", "Old Goa Churches", "Dudhsagar Falls"],
}


@tool
def get_places(city: str) -> str:
    """Return the top tourist places to visit in a city."""
    places = PLACES.get(city.lower())
    return ", ".join(places) if places else f"No places data for {city}."

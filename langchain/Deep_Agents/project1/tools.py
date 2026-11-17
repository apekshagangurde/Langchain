"""
Tools for TripMate
==================

Built one tool at a time. Each new tool is added here, wired into agent.py,
and tested before the next one.

    Tool            Status
    --------------  ---------------------------------------------
    get_weather     ✅ added (step 2) — fake data for now
    search_places   ✅ added (step 6) — real web search via Tavily

search_places needs TAVILY_API_KEY in project1/.env (pip install langchain-tavily).
"""

from langchain.tools import tool
from langchain_tavily import TavilySearch

WEATHER = {
    "lonavala": "24°C, misty with light drizzle",
    "mahabaleshwar": "19°C, cool and clear",
    "goa": "30°C, sunny and humid",
}


@tool
def get_weather(city: str) -> str:
    """Return this weekend's weather forecast for a city."""
    return WEATHER.get(city.lower(), f"No weather data for {city}.")


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

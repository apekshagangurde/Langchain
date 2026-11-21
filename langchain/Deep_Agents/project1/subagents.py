"""
TripMate — subagents
====================

Each subagent is a dict spec passed to create_deep_agent(subagents=[...]).
The main agent delegates to one with the built-in `task` tool:

    task(subagent_type="weather-agent", description="Weather in Lonavala this weekend")

The subagent runs in its own context (it sees only that task description),
uses its own tools, and returns one final message to the main agent.

Fields (deepagents SubAgent):
    name          -> what the main agent passes as subagent_type
    description   -> how the main agent decides WHEN to delegate
    system_prompt -> the subagent's own instructions
    tools         -> only these tools (otherwise it inherits the main agent's)
"""

from tools import get_weather

WEATHER_AGENT = {
    "name": "weather-agent",
    "description": (
        "Checks the weather forecast for one or more cities for the trip dates "
        "and says whether it suits outdoor sightseeing. Use it for any weather "
        "question or when comparing destinations by weather."
    ),
    "system_prompt": """\
You are TripMate's weather checker.

- Call `get_weather` once per city in the task.
- Reply in at most 5 short lines: per city, the conditions, temperature range
  in °C, and rain chance for the trip days.
- End with one line: which city is better for outdoor sightseeing and why.
- Return only this summary — no raw tool output, no itinerary.
""",
    "tools": [get_weather],
}

SUBAGENTS = [WEATHER_AGENT]

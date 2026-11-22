"""
TripMate — subagents
====================

Each subagent is a dict spec passed to create_deep_agent(subagents=[...]).
The main agent delegates to one with the built-in `task` tool:

    task(subagent_type="weather-agent", description="Weather in Lonavala this weekend")

By default a subagent is ISOLATED: it sees only that task description, uses
its own tools, and returns one final message to the main agent.
A FORK (mode="fork") instead continues the main agent's conversation: it sees
the whole chat + the main system prompt, then the task. (Experimental.)

Fields (deepagents SubAgent):
    name          -> what the main agent passes as subagent_type
    description   -> how the main agent decides WHEN to delegate
    system_prompt -> the subagent's own instructions
    tools         -> only these tools ([] = none; omitted = inherits the main agent's)
    mode          -> "isolated" (default) or "fork"

    weather-agent  get_weather     forecast + "better for sightseeing" verdict
    places-agent   search_places   short list of places to visit
    budget-agent   (none)          cost split via the budget-planner skill
    critic-agent   (none, fork)    reviews the draft against the whole chat -> "ok" or fixes
"""

from tools import get_weather, search_places

WEATHER_AGENT = {
    "name": "weather-agent",
    "description": (
        "Checks the weather forecast for one or more cities for the trip dates "
        "and says whether it suits outdoor sightseeing. Use it for any weather "
        "question or when comparing destinations by weather."
    ),
    "system_prompt": """\
You are TripMate's weather checker.

- Call `get_weather` once per city in the task (pass `country_code`, e.g. "IN").
- Check the returned place name is the right town. If a city is not found,
  say so for that city — do NOT guess another spelling.
- Reply in at most 5 short lines: per city, the conditions, temperature range
  in °C, and rain chance for the trip days.
- End with one line: which city is better for outdoor sightseeing and why.
- Return only this summary — no raw tool output, no itinerary.
""",
    "tools": [get_weather],
}

PLACES_AGENT = {
    "name": "places-agent",
    "description": (
        "Finds places to visit in ONE city, optionally matching the user's "
        "interests (e.g. forts, viewpoints, food). Use it once the destination "
        "is chosen. Include the city and any interests in the task."
    ),
    "system_prompt": """\
You are TripMate's places finder.

- Call `search_places` for the city in the task, passing the interests if given.
- Only list places that appear in the search results — never invent one.
- Reply with at most 8 bullets: `- <place> — <one-line why it's worth it>`.
- If the results are empty or unclear, say so in one line.
- Return only this list — no raw tool output, no itinerary.
""",
    "tools": [search_places],
}

BUDGET_AGENT = {
    "name": "budget-agent",
    "description": (
        "Estimates trip cost for a city, number of days, home city, people and "
        "budget, split into travel / stay / food / buffer, and says whether it "
        "fits. Use it after the destination is chosen and before writing the plan."
    ),
    "system_prompt": """\
You are TripMate's budget estimator. You have no search tools.

- FIRST read the `budget-planner` skill and follow it (split, prices, output).
- Read from the task: home city, destination, days, people, total budget.
  Use any prices given in the task; otherwise the skill's typical ranges.
- Return only the skill's budget table, verdict and assumptions.
""",
    "tools": [],
    # Isolated subagents don't inherit the main agent's skills.
    "skills": ["/skills/"],
}

CRITIC_AGENT = {
    "name": "critic-agent",
    "description": (
        "Reviews a DRAFT itinerary before it is shown to the user, against "
        "everything said in this chat. Pass the full draft in the task. "
        "Returns 'ok' or a short fix list."
    ),
    # G4: fork mode — the critic sees the whole conversation (what the user asked,
    # their preferences, the weather/places/budget results), not just the task text.
    # Under fork, this system_prompt is ADDED after the main agent's prompt.
    # Fork subagents can't set `skills` (they inherit the main agent's).
    "mode": "fork",
    "system_prompt": """\
## You are now TripMate's critic (reviewer)
You are not planning or delegating any more — only reviewing. The draft to
review is in the task. Check it against what the user said in the
conversation above and the subagent results there (weather, places, budget):
- days and budget match; travel from the home city is realistic
- no late-night travel; each day has a sensible pace
- the user's likes/dislikes and diet are respected
- nothing looks invented (places or prices with no source)

If everything is fine, reply exactly: ok
Otherwise reply with at most 5 bullets, each one concrete fix.
""",
    "tools": [],
}

SUBAGENTS = [WEATHER_AGENT, PLACES_AGENT, BUDGET_AGENT, CRITIC_AGENT]

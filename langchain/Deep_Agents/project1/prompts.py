"""
Step 1 — System prompt for TripMate (starter version)
=====================================================

WHY START WITH THE SYSTEM PROMPT?
---------------------------------
In a deep agent the system prompt is the "job description". The harness gives
the agent its tools, but the prompt tells the agent WHEN and HOW to use them.

This is only the STARTER prompt: who the agent is, what its job is, and basic
rules. Each time we add a concept to the project, we add one section here so
the prompt always matches what the agent can actually do.

HOW THE PROMPT WILL GROW
------------------------
    Step we build            Section to add here
    -----------------------  -------------------------------
    todo list                ## Planning
    subagents                ## Subagents
    skills                   ## Skills
    backends / files         ## Files
    memory                   ## Memory
    permissions              ## Permissions
    runtime context          ## Run context
    structured output        ## Output (replace the plain one)
    human-in-the-loop        ## Human approval
    async subagent           ## Background jobs

NOTE: deepagents adds its own tool descriptions automatically. This prompt only
adds the TripMate-specific rules on top (the "USER" part, placed first:
USER -> BASE -> SUFFIX).
"""

TRIPMATE_SYSTEM_PROMPT = """\
You are TripMate, a weekend-trip planner for users living in Pune, India.
Your job: turn a request like "Plan a 2-day trip, budget ₹8,000" into a
simple day-by-day itinerary.

## Planning
- For any request with more than one step, FIRST call `write_todos` with one
  todo per step (e.g. check weather -> pick city -> find places -> write plan).
- Mark one todo `in_progress` at a time and mark it `completed` as soon as it
  is done.

## Skills
- Before writing the itinerary, read the `itinerary-writer` skill and follow it.
- Only open a skill when the current step needs it.

## Rules
- Only suggest cities you have data for; never invent prices or weather.
- If no city fits the budget, say so and suggest the cheapest option.

## Output
- Write the itinerary in the format from the `itinerary-writer` skill.
"""


if __name__ == "__main__":
    print(TRIPMATE_SYSTEM_PROMPT)

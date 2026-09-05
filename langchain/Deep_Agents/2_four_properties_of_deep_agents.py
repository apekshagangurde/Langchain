"""
The 4 Important Properties of a Deep Agent
==========================================
A deep agent is not a different loop from a shallow agent — it is the same loop
plus four properties. Remove any one of them and it degrades back toward shallow.

`create_deep_agent()` from the `deepagents` package gives you three of the four
out of the box; planning you add with one middleware. Each property below is
labelled with the argument that supplies it.


PROPERTY 1 — PLANNING                          middleware=[TodoListMiddleware()]
---------------------
The agent writes an explicit to-do list before working, then updates it as it goes.

  why it matters   The plan lives in STATE, not in the model's head. Even after
                   50 steps the agent can re-read what it set out to do, what is
                   done, and what is left. This is what stops it drifting off the
                   goal, stopping early, or redoing finished work.
  how              `TodoListMiddleware` adds a `write_todos` tool. NOT included by
                   default in deepagents 0.7.x — pass it in `middleware=[...]`.
                   The list ends up in `result["todos"]`.


PROPERTY 2 — SUB-AGENTS (CONTEXT ISOLATION)               subagents=[...]
-------------------------------------------
Instead of doing everything itself, the main agent hands a subtask to a fresh
agent that has its OWN clean context window, and gets back only the conclusion.

  why it matters   The sub-agent can burn 50,000 tokens reading and searching,
                   then return a 200-token answer. The main agent's context never
                   sees the 50,000. This is the single biggest difference from a
                   shallow agent — one context window becomes many.
  bonus            Each sub-agent gets its own prompt and its own tools, so the
                   researcher's instructions never leak into the writer's.
  how              Declare `SubAgent` dicts in `subagents=[...]`. The main agent
                   delegates through a built-in `task` tool. Default mode is
                   "isolated" (sees only the delegated task); "fork" instead
                   continues the parent's conversation.


PROPERTY 3 — PERSISTENT MEMORY / FILE SYSTEM              built in
--------------------------------------------
Findings are written to files instead of being carried in the message history.
The agent reads back only the file it needs, when it needs it.

  why it matters   Message history is volatile — summarisation deletes it, a
                   restart wipes it. A file survives all of that. It also keeps
                   the context small: a filename is 5 tokens, its contents 5,000.
  how              Always on. `create_deep_agent` ships `ls`, `read_file`,
                   `write_file`, `edit_file`, `glob` and `grep`. By default these
                   write to a VIRTUAL filesystem held in `result["files"]`, not
                   to your disk — pass a `backend=` to change that.


PROPERTY 4 — A DETAILED SYSTEM PROMPT                     system_prompt="..."
-------------------------------------
Shallow agents get one sentence. Deep agents get a page: how to plan, when to
delegate, what "done" means, how to verify before finishing.

  why it matters   Properties 1-3 give the agent capabilities; the prompt is what
                   actually makes it use them. Given `write_todos` and no
                   instruction to plan, a model will mostly ignore the tool.
  how              `create_deep_agent` already has a long built-in prompt covering
                   the tools. Yours is ADDED to it, so describe only the job.


All four are assembled below.
"""

from deepagents import SubAgent, create_deep_agent
from dotenv import load_dotenv
from langchain.agents.middleware import TodoListMiddleware
from langchain.tools import tool
from langchain_groq import ChatGroq

load_dotenv()

# The main agent plans, delegates and writes files at once, so it gets the larger
# model. Small models degenerate when asked to emit long free-text tool arguments
# (the file contents), which surfaces as a Groq "tool_use_failed" error.
model = ChatGroq(model="openai/gpt-oss-120b")


@tool
def lookup_city(city: str) -> str:
    """Returns raw facts about a city."""
    data = {
        "pune": "population 7.4M; IT and auto hub; cost index 38; 1BHK rent Rs 12-20k",
        "mumbai": "population 21.7M; finance and film capital; cost index 62; 1BHK rent Rs 30-45k",
    }
    return data.get(city.lower(), f"no data for {city}")


# ---------------------------------------------------------------------------
# PROPERTY 2 — a sub-agent, declared as a plain dict.
# It runs in its OWN context window with its OWN prompt and tools; the main
# agent calls it through the built-in `task` tool and sees only what it returns.
# ---------------------------------------------------------------------------
city_researcher: SubAgent = {
    "name": "city-researcher",
    # The MAIN agent reads this to decide when to delegate — make it action-first.
    "description": "Researches one city's cost of living, job market and lifestyle.",
    "system_prompt": "You research one city. Reply with 3 short bullet points, nothing else.",
    "tools": [lookup_city],
}


# ---------------------------------------------------------------------------
# PROPERTY 4 — the prompt. Note how short it can be: the built-in deep-agent
# prompt already explains the file and delegation tools, so this only has to
# describe THIS job and the house rules.
# ---------------------------------------------------------------------------
DEEP_AGENT_PROMPT = """You are a relocation research assistant.

## Planning
Call `write_todos` first to break the request into concrete steps, and mark each
one completed as you finish it. Do not batch completions.

## Delegating
Research each city with the `city-researcher` subagent. Do not reason about
cities yourself.

## Memory
Save each city's findings with `write_file` (e.g. `pune.md`, `mumbai.md`), under
300 characters each — they are notes, not essays. Read them back with `read_file`
when you write the comparison.

## Finishing
Done means: every todo completed, both files written, and a short comparison
paragraph as your final answer.
"""


# ---------------------------------------------------------------------------
# All four properties in one call.
# ---------------------------------------------------------------------------
deep_agent = create_deep_agent(
    model=model,
    tools=[lookup_city],
    subagents=[city_researcher],          # property 2
    middleware=[TodoListMiddleware()],    # property 1
    system_prompt=DEEP_AGENT_PROMPT,      # property 4
    # property 3 (the file system) needs no argument — it is always on
)

result = deep_agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Compare Pune and Mumbai for someone relocating for an IT job.",
            }
        ]
    }
)

print("--- final answer ---")
print(result["messages"][-1].text)

print("\n--- property 1: the plan the agent wrote ---")
for todo in result.get("todos", []) or []:
    print(f"  [{todo.get('status')}] {todo.get('content')}")

print("\n--- property 3: the virtual file system it built ---")
for name, content in (result.get("files") or {}).items():
    print(f"  {name}: {str(content)[:70]}...")

print(f"\n--- property 2: {len(result['messages'])} messages in the MAIN context ---")
print("The subagent's research turns happened elsewhere and never entered it.")

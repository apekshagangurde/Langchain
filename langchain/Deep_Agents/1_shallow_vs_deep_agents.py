"""
Shallow Agents vs Deep Agents
=============================

WHAT IS A SHALLOW AGENT?
------------------------
A shallow agent is the basic agent loop: a model, a set of tools, and a while-loop.

    user message -> MODEL -> tool call -> tool result -> MODEL -> ... -> final answer

That's it. `create_agent(model, tools)` gives you one. The model sees the whole
message history on every turn and decides the single next step.

Characteristics:
  - one model, one context window, one flat message history
  - reactive: it plans nothing ahead, it just picks the next tool
  - all intermediate work (every tool result) piles up in the message history
  - great for short tasks: 1-10 steps, one clear goal

Examples of shallow-agent work: "what's the weather in Pune", "convert this CSV
column to JSON", "look up this customer and summarise their plan".


DISADVANTAGES OF A SHALLOW AGENT
--------------------------------
1. COMPLEX QUERIES ARE NOT HANDLED WELL
   A shallow agent only ever decides the NEXT tool call. It never breaks a task
   into sub-tasks, never sequences them, and never checks its own work. So a
   query like "research three competitors, compare their pricing, and write a
   report with sources" typically goes wrong in one of these ways:
     - it answers only the first part of the request and stops early
     - it drifts off the original goal halfway through
     - it repeats a step it already completed, because nothing tracks progress
     - it produces a shallow answer where the question needed several passes
   There is no plan to fall back on, so there is nothing keeping it on course.

2. LIMITED CONTEXT RETENTION
   Everything the agent knows lives in one message history inside one context
   window. That single window is the memory, and it is finite:
     - once the history exceeds the window, older messages must be dropped or
       summarised, and the agent genuinely forgets earlier steps and decisions
     - it cannot recall anything from a previous run; a restart starts from zero
     - a single fat tool result (a 5000-line file, a full web page, a big API
       response) eats the window and crowds out everything else — "context rot"
     - accuracy degrades as the window fills, even before the hard limit
   Because there is no external memory (no files, no per-sub-agent context),
   there is nowhere to put information except the conversation itself.

3. NO SEPARATION OF CONCERNS
   Research, writing and verification all share one prompt and one history.
   Instructions for one phase leak into the others, and noise from research
   pollutes the writing step.

4. NO COST CONTROL ON CONTEXT
   Every turn resends the entire growing history to the model, so token cost
   climbs with each step even when only the last two messages matter.

Each of these maps onto one deep-agent capability: planning fixes (1),
sub-agents and a file system fix (2) and (4), and sub-agent prompts fix (3).


WHAT IS A DEEP AGENT?
---------------------
A deep agent is the same loop plus an architecture for handling long, multi-step
work without losing the thread. Four capabilities are what make it "deep":

  1. PLANNING
     The agent writes an explicit to-do list, then works through it and revises it
     as it learns. The plan lives in state, not in the model's head, so the goal
     survives a long run. (In LangChain: `TodoListMiddleware` / `write_todos`.)

  2. SUB-AGENTS (context isolation)
     Instead of doing everything itself, the main agent delegates a subtask to a
     fresh agent with its OWN clean context window. The sub-agent burns 50k tokens
     researching and hands back a 200-token answer. The main agent's context stays
     clean. This is the single biggest difference from a shallow agent.

  3. PERSISTENT MEMORY / FILE SYSTEM
     Findings get written to files (real or virtual) instead of being carried in
     the message history. The agent reads back only what it needs, when it needs
     it. Work therefore survives summarisation — and even a restart.

  4. A DETAILED SYSTEM PROMPT
     Shallow agents get a one-liner. Deep agents get long, explicit instructions:
     how to plan, when to delegate, what "done" looks like, how to verify.

Examples of deep-agent work: "research this market and write a report with
sources", "migrate this codebase off library X", "audit these 40 files for bugs".


SIDE BY SIDE
------------
                    shallow agent              deep agent
  planning          none, reactive              explicit to-do list in state
  context           one shared history          isolated per sub-agent
  memory            message history only        files + state that outlive the loop
  prompt            a sentence                  a page
  good for          1-10 steps                  50-500 steps
  cost              low                         high (many model calls)
  failure mode      forgets / repeats itself    over-engineers a simple task

Rule of thumb: start shallow. Go deep only when the task genuinely needs planning
and context isolation — a deep agent on a simple question is slower, pricier, and
no more correct.


BOTH, SIDE BY SIDE, IN CODE
---------------------------
Below are the two agents doing the SAME task, so the difference is visible rather
than theoretical.

    shallow   create_agent(...)        from langchain.agents
    deep      create_deep_agent(...)   from deepagents   (pip install deepagents)

`create_deep_agent` is a wrapper around `create_agent` that pre-installs most of
the deep-agent properties — sub-agents, a file system and a long built-in prompt —
so you configure them instead of building them. Planning is the exception: in
deepagents 0.7.x you still add `TodoListMiddleware()` yourself.

File 2 covers the four properties in detail; file 3 covers when they are worth
the cost.
"""

from deepagents import SubAgent, create_deep_agent
from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware
from langchain.tools import tool
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_groq import ChatGroq

load_dotenv()


@tool
def get_population(city: str) -> str:
    """Returns the population of a city."""
    data = {"pune": "7.4 million", "mumbai": "21.7 million", "delhi": "32.9 million"}
    return data.get(city.lower(), f"No population data for {city}")


# Deep agents are token-hungry: the built-in prompt plus the growing history is
# resent on every turn, and each subagent is a full agent loop of its own. On
# Groq's free tier (8,000 tokens/minute) that hits a 429 within a few steps, so
# the model is paced to roughly one request every 25 seconds.
# Drop the rate limiter if you are on a paid tier.
model = ChatGroq(
    model="openai/gpt-oss-120b",
    rate_limiter=InMemoryRateLimiter(requests_per_second=0.04, check_every_n_seconds=0.5),
)

TASK = "Compare Pune and Mumbai for someone relocating, and recommend one."


# ===========================================================================
# 1. THE SHALLOW AGENT — model + tools + a one-line prompt.
#    No planning, no delegation, no memory beyond the message history.
# ===========================================================================
shallow_agent = create_agent(
    model=model,
    tools=[get_population],
    system_prompt="You are a helpful assistant. Answer in one sentence.",
)

shallow_result = shallow_agent.invoke({"messages": [{"role": "user", "content": TASK}]})

print("--- shallow agent ---")
print(shallow_result["messages"][-1].text)
print(f"\n{len(shallow_result['messages'])} messages, one flat history, no plan")


# ===========================================================================
# 2. THE DEEP AGENT — use `create_deep_agent()` from the `deepagents` package.
#
#    You do NOT hand-build this out of create_agent. Out of the box it gives you:
#      - sub-agents -> a `task` tool, driven by the `subagents=[...]` argument
#      - filesystem -> ls / read_file / write_file / edit_file / glob / grep
#      - prompting  -> a detailed built-in prompt, prepended to yours
#
#    Planning is NOT on by default in deepagents 0.7.x — add it yourself with
#    `middleware=[TodoListMiddleware()]`, which supplies the `write_todos` tool.
#
#    Install with:  pip install deepagents
# ===========================================================================
research_subagent: SubAgent = {
    "name": "city-researcher",
    # The MAIN agent reads this description to decide when to delegate,
    # so write it action-first.
    "description": "Researches one city: cost of living, jobs, climate, commute.",
    # The sub-agent's own instructions. The main agent's prompt never reaches it.
    "system_prompt": "You research one city. Reply with 3 short bullet points, nothing else.",
    "tools": [get_population],
    # mode defaults to "isolated": it sees only the delegated task, in its OWN
    # context window, and returns only its conclusion. That is context isolation.
}

deep_agent = create_deep_agent(
    model=model,
    tools=[get_population],
    subagents=[research_subagent],
    middleware=[TodoListMiddleware()],  # adds planning (`write_todos`)
    # Your prompt is ADDED to the built-in deep-agent prompt, so you only need
    # to describe the job — not re-explain how to delegate or use the files.
    system_prompt=(
        "You are a relocation researcher.\n"
        "Start by calling `write_todos` to plan the steps.\n"
        "Delegate each city to the city-researcher subagent rather than "
        "reasoning about cities yourself.\n"
        "Finish with a short recommendation paragraph."
    ),
)

deep_result = deep_agent.invoke({"messages": [{"role": "user", "content": TASK}]})

print("\n--- deep agent ---")
print(deep_result["messages"][-1].text)

print("\nthe plan it wrote for itself (property 1: planning):")
for todo in deep_result.get("todos", []) or []:
    print(f"  [{todo.get('status')}] {todo.get('content')}")

print(f"\n{len(deep_result['messages'])} messages in the MAIN context — the subagent's")
print("research turns happened in a separate context and never entered it.")

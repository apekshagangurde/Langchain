"""
TripMate — the deep agent
=========================

Deep agent with:
- two tools: get_weather (Open-Meteo forecast), search_places (Tavily web search)
- a todo list (TodoListMiddleware -> write_todos) for planning
- skills from project1/skills/ (e.g. itinerary-writer), read only when needed
- build_agent(checkpointer=..., store=...) for short- and long-term memory (used by app.py)
- long-term memory: files under /memories/ are saved in the store, shared across threads
- memory/AGENTS.md: TripMate defaults for all users, loaded on every run
  (per-user details like home city live in /memories/user_preferences.md)

    python agent.py
"""

from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import (
    CompositeBackend,
    FilesystemBackend,
    StateBackend,
    StoreBackend,
)
from dotenv import load_dotenv
from langchain.agents.middleware import TodoListMiddleware

from llm import get_model
from prompts import TRIPMATE_SYSTEM_PROMPT
from tools import get_weather, search_places

PROJECT_DIR = Path(__file__).parent
load_dotenv(PROJECT_DIR / ".env")  # API keys + TRIPMATE_MODEL

# Model comes from TRIPMATE_MODEL in .env (default: Groq gpt-oss-120b).
# To switch to Claude: TRIPMATE_MODEL=anthropic:claude-opus-5-5
model = get_model()


backend = CompositeBackend(
    default=StateBackend(),
    routes={
        "/skills/": FilesystemBackend(
            root_dir=PROJECT_DIR / "skills", virtual_mode=True
        ),
        # Long-term memory: files under /memories/ go to the LangGraph store,
        # so they survive across threads (new chats). Everything else stays per-thread.
        # One shared namespace for now; per-user comes with runtime context (E2).
        "/memories/": StoreBackend(namespace=lambda _rt: ("tripmate", "memories")),
        # Shared defaults: project1/memory/AGENTS.md on disk (you edit it, the agent reads it).
        "/memory/": FilesystemBackend(
            root_dir=PROJECT_DIR / "memory", virtual_mode=True
        ),
    },
)


def build_agent(checkpointer=None, store=None):
    """Build TripMate.

    checkpointer -> short-term memory (one chat thread)
    store        -> long-term memory (/memories/, shared across threads)
    """
    return create_deep_agent(
        model=model,
        tools=[get_weather, search_places],
        middleware=[
            TodoListMiddleware()
        ],  # adds the write_todos tool (not default in deepagents 0.7.x)
        backend=backend,
        skills=["/skills/"],
        memory=["/memory/AGENTS.md"],  # always loaded into the system prompt
        system_prompt=TRIPMATE_SYSTEM_PROMPT,
        checkpointer=checkpointer,
        store=store,
    )


# For LangGraph Studio (langgraph.json -> agent.py:agent).
# No checkpointer or store here: `langgraph dev` adds its own and errors if we pass one.
agent = build_agent()


if __name__ == "__main__":
    # Test: get_weather for both cities, pick one, then search_places for it.
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Compare this weekend's weather in Lonavala and Mahabaleshwar, "
                    "pick the better one for sightseeing, and tell me what places to visit there.",
                }
            ]
        }
    )

    # Show which tools were called, then the final answer.
    for msg in result["messages"]:
        for call in getattr(msg, "tool_calls", None) or []:
            print(f"tool call -> {call['name']}({call['args']})")
    print("\nTripMate:", result["messages"][-1].content)

    print("\nTodo list:")
    for todo in result.get("todos", []):
        print(f"  [{todo['status']}] {todo['content']}")

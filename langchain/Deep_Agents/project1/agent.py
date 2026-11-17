"""
TripMate — the deep agent
=========================

Deep agent with two tools (get_weather, get_places) and a todo list
(TodoListMiddleware -> write_todos) for planning.

    python agent.py
"""

from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.agents.middleware import TodoListMiddleware
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_groq import ChatGroq

from prompts import TRIPMATE_SYSTEM_PROMPT
from tools import get_places, get_weather

load_dotenv(Path(__file__).parent / ".env")  # project1/.env with GROQ_API_KEY

# Groq for now (Anthropic key not working yet).
# Rate limiter keeps us under Groq's free-tier tokens/minute cap.
model = ChatGroq(
    model="openai/gpt-oss-120b",
    rate_limiter=InMemoryRateLimiter(
        requests_per_second=0.04, check_every_n_seconds=0.5
    ),
)

agent = create_deep_agent(
    model=model,
    tools=[get_weather, get_places],
    middleware=[
        TodoListMiddleware()
    ],  # adds the write_todos tool (not default in deepagents 0.7.x)
    system_prompt=TRIPMATE_SYSTEM_PROMPT,
)


if __name__ == "__main__":
    # Test: get_weather for both cities, pick one, then get_places for it.
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

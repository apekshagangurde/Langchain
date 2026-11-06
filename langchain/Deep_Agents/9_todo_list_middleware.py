"""
TodoListMiddleware
==================

Middleware            Simple explanation
--------------------  ---------------------------------------------------------
TodoListMiddleware    Gives the agent a `write_todos` tool to maintain a task list.

HOW IT WORKS
------------
- Adds a `write_todos` tool, plus a short prompt telling the agent when to use it.
- Each todo has `content` (the task) and `status`: pending -> in_progress -> completed.
- Every call to `write_todos` REPLACES the whole list, so the agent rewrites it
  as it makes progress.
- The list is kept in the agent's state, so after the run you can read it from
  `result["todos"]`.

Why it helps: the plan lives in state, not in the model's head, so on long
tasks the agent keeps track of what is done and what is left, and doesn't
stop early or repeat steps.

NOTE: in deepagents 0.7.x this middleware is NOT added by default. Pass it in
with `create_deep_agent(middleware=[TodoListMiddleware()])`.
"""

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.agents.middleware import TodoListMiddleware
from langchain.tools import tool
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_groq import ChatGroq

load_dotenv()

# Rate limiter keeps us under Groq's free-tier tokens/minute cap.
model = ChatGroq(
    model="openai/gpt-oss-120b",
    rate_limiter=InMemoryRateLimiter(requests_per_second=0.04, check_every_n_seconds=0.5),
)


@tool
def get_weather(city: str) -> str:
    """Returns today's weather for a city."""
    data = {
        "pune": "28°C, partly cloudy",
        "mumbai": "31°C, humid with light rain",
        "delhi": "22°C, hazy",
    }
    return data.get(city.lower(), f"no weather data for {city}")


agent = create_deep_agent(
    model=model,
    tools=[get_weather],
    middleware=[TodoListMiddleware()],  # adds the write_todos tool
    system_prompt=(
        "You are a travel weather assistant. For multi-step requests, first call "
        "`write_todos` to plan one todo per step, then mark each todo completed "
        "as soon as you finish it."
    ),
)

if __name__ == "__main__":
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "Check the weather in Pune, Mumbai and Delhi, then tell me "
                    "which city is best for a walk today.",
                }
            ]
        }
    )

    print("Agent reply:", result["messages"][-1].content)

    # The final task list, kept in the agent's state by TodoListMiddleware.
    print("\nTodo list:")
    for todo in result.get("todos", []):
        print(f"  [{todo['status']}] {todo['content']}")

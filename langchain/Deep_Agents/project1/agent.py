"""
TripMate — the deep agent
=========================

Smallest working version: one deep agent + one tool (get_weather).
Run it, check the answer, then add the next tool.

    python agent.py
"""

from pathlib import Path

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_groq import ChatGroq

from prompts import TRIPMATE_SYSTEM_PROMPT
from tools import get_weather

load_dotenv(Path(__file__).parent / ".env")  # project1/.env with GROQ_API_KEY

# Groq for now (Anthropic key not working yet).
# Rate limiter keeps us under Groq's free-tier tokens/minute cap.
model = ChatGroq(
    model="openai/gpt-oss-120b",
    rate_limiter=InMemoryRateLimiter(requests_per_second=0.04, check_every_n_seconds=0.5),
)

agent = create_deep_agent(
    model=model,
    tools=[get_weather],
    system_prompt=TRIPMATE_SYSTEM_PROMPT,
)


if __name__ == "__main__":
    # Test: the agent should call get_weather for each city and compare.
    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": "What's the weather this weekend in Lonavala and Mahabaleshwar? "
                    "Which one is better for sightseeing?",
                }
            ]
        }
    )

    # Show which tools were called, then the final answer.
    for msg in result["messages"]:
        for call in getattr(msg, "tool_calls", None) or []:
            print(f"tool call -> {call['name']}({call['args']})")
    print("\nTripMate:", result["messages"][-1].content)

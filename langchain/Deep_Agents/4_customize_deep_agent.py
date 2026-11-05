"""
Customize a Deep Agent (simple)
A minimal deep agent customized with our own model, one custom tool and a custom system prompt.
Planning (write_todos) and the virtual file system come built in, so we only describe the job.
"""

from deepagents import create_deep_agent
from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_groq import ChatGroq

load_dotenv()

# Custom model: Groq, rate-limited to stay under the free-tier tokens/minute cap.
model = ChatGroq(
    model="openai/gpt-oss-120b",
    rate_limiter=InMemoryRateLimiter(requests_per_second=0.04, check_every_n_seconds=0.5),
)


# Custom tool.
@tool
def get_weather(city: str) -> str:
    """Returns today's weather for a city."""
    data = {
        "pune": "28°C, partly cloudy",
        "mumbai": "31°C, humid with light rain",
    }
    return data.get(city.lower(), f"no weather data for {city}")


# Custom system prompt.
SYSTEM_PROMPT = """You are a friendly travel weather assistant.
Use `get_weather` for each city the user asks about, then give a short,
one-line packing tip per city."""


agent = create_deep_agent(
    model=model,
    tools=[get_weather],
    system_prompt=SYSTEM_PROMPT,
)

if __name__ == "__main__":
    result = agent.invoke(
        {"messages": [{"role": "user", "content": "I'm visiting Pune and Mumbai today. What should I pack?"}]}
    )
    print(result["messages"][-1].content)

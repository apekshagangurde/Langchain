"""
Claude Agent SDK - Custom Tool + Structured Output (Pydantic)

Combines two earlier examples:
- A custom tool (get_temperature) that calls a real API
- output_format constrained to a Pydantic model, so the final
  ResultMessage.structured_output can be validated straight into a
  typed WeatherResult instance.
"""

import asyncio
from typing import Any
import httpx
from pydantic import BaseModel
from claude_agent_sdk import (
    query,
    tool,
    create_sdk_mcp_server,
    ClaudeAgentOptions,
    ResultMessage,
)


class WeatherResult(BaseModel):
    location: str
    temperature_fahrenheit: float


@tool(
    "get_temperature",
    "Get the current temperature at a location",
    {"latitude": float, "longitude": float},
)
async def get_temperature(args: dict[str, Any]) -> dict[str, Any]:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": args["latitude"],
                "longitude": args["longitude"],
                "current": "temperature_2m",
                "temperature_unit": "fahrenheit",
            },
        )
        data = response.json()

    return {
        "content": [
            {
                "type": "text",
                "text": f"Temperature: {data['current']['temperature_2m']}°F",
            }
        ]
    }


weather_server = create_sdk_mcp_server(
    name="weather",
    version="1.0.0",
    tools=[get_temperature],
)


async def main():
    options = ClaudeAgentOptions(
        mcp_servers={"weather": weather_server},
        allowed_tools=["mcp__weather__get_temperature"],
        output_format={
            "type": "json_schema",
            "schema": WeatherResult.model_json_schema(),
        },
    )

    async for message in query(
        prompt="What's the temperature in San Francisco?", options=options
    ):
        if isinstance(message, ResultMessage) and message.subtype == "success":
            result = WeatherResult.model_validate(message.structured_output)
            print(result)
            print(result.location, result.temperature_fahrenheit)


if __name__ == "__main__":
    asyncio.run(main())

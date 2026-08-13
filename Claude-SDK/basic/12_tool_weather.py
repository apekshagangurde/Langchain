"""
Claude Agent SDK - Custom Tool that calls a real API (weather)

Same 4-part anatomy as before (name, description, input_schema, handler),
but the handler here actually calls an external API (Open-Meteo) instead
of doing plain math. Wrapped in an MCP server and used with query()
exactly like the calculator example.

Official docs: https://code.claude.com/docs/en/agent-sdk/custom-tools
"""

import asyncio
from typing import Any
import httpx
from claude_agent_sdk import (
    query,
    tool,
    create_sdk_mcp_server,
    ClaudeAgentOptions,
    AssistantMessage,
    ToolUseBlock,
    ResultMessage,
)


# 1. name: "get_temperature"
# 2. description: tells Claude what it does
# 3. input_schema: {"latitude": float, "longitude": float}
# 4. handler: the function below, which calls the Open-Meteo API
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

    # Return a content array - Claude sees this as the tool result
    return {
        "content": [
            {
                "type": "text",
                "text": f"Temperature: {data['current']['temperature_2m']}°F",
            }
        ]
    }


# Wrap the tool in an in-process MCP server
weather_server = create_sdk_mcp_server(
    name="weather",
    version="1.0.0",
    tools=[get_temperature],
)


async def main():
    options = ClaudeAgentOptions(
        mcp_servers={"weather": weather_server},
        allowed_tools=["mcp__weather__get_temperature"],
    )

    async for message in query(
        prompt="What's the temperature in San Francisco?", options=options
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"[tool call] {block.name}({block.input})")
        elif isinstance(message, ResultMessage) and message.subtype == "success":
            print(f"Answer: {message.result}")


if __name__ == "__main__":
    asyncio.run(main())

"""
Claude Agent SDK - Custom Tool Call

Define a custom in-process tool with @tool, wrap it in an MCP server with
create_sdk_mcp_server(), then register it via mcp_servers + allowed_tools
so Claude can call it.

Tool names must be referenced in allowed_tools as:
    mcp__{server_name}__{tool_name}

Official docs: https://code.claude.com/docs/en/agent-sdk/custom-tools
"""

import asyncio
from typing import Any
from claude_agent_sdk import (
    query,
    tool,
    create_sdk_mcp_server,
    ClaudeAgentOptions,
    AssistantMessage,
    ToolUseBlock,
    ResultMessage,
)


# Define a tool: name, description, input schema, handler
@tool("add", "Add two numbers", {"a": float, "b": float})
async def add(args: dict[str, Any]) -> dict[str, Any]:
    result = args["a"] + args["b"]
    return {"content": [{"type": "text", "text": f"Sum: {result}"}]}


# Wrap it in an in-process MCP server
calculator_server = create_sdk_mcp_server(
    name="calculator",
    version="1.0.0",
    tools=[add],
)


async def main():
    options = ClaudeAgentOptions(
        mcp_servers={"calculator": calculator_server},
        allowed_tools=["mcp__calculator__add"],
    )

    async for message in query(prompt="What is 12 plus 30?", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"[tool call] {block.name}({block.input})")
        elif isinstance(message, ResultMessage) and message.subtype == "success":
            print(f"Answer: {message.result}")


if __name__ == "__main__":
    asyncio.run(main())

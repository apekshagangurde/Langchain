"""
Claude Agent SDK - Basic Usage Example

Build production AI agents with Claude Code as a library

Official docs: https://code.claude.com/docs/en/agent-sdk/python

Install:
    uv init
    uv add claude-agent-sdk

    (or: pip install claude-agent-sdk)

Setup:
    export ANTHROPIC_API_KEY=your-api-key

Note: The SDK bundles a native Claude Code binary, so no separate
CLI install is required on most platforms.
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage


async def main():
    # query() drives the agentic loop and returns an async iterator of messages
    async for message in query(
        prompt="What is 2 + 2?",
        options=ClaudeAgentOptions(
            allowed_tools=["Read", "Edit", "Glob"],
            permission_mode="acceptEdits",
        ),
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)  # Claude's reasoning/response
                elif hasattr(block, "name"):
                    print(f"Tool: {block.name}")  # Tool being called
        elif isinstance(message, ResultMessage):
            print(f"Done: {message.subtype}")  # Final result


if __name__ == "__main__":
    asyncio.run(main())

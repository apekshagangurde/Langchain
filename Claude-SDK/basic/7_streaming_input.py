"""
Claude Agent SDK - Streaming Input Mode

Instead of a single string prompt, you can pass an async generator that
yields user message dicts one at a time. This keeps one persistent
session alive so you can send follow-up messages (based on timers, user
input, tool results, etc.) while the agent is running.

Official docs: https://code.claude.com/docs/en/agent-sdk/streaming-vs-single-mode
"""

import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    AssistantMessage,
    TextBlock,
)


async def message_generator():
    # First message
    yield {
        "type": "user",
        "message": {
            "role": "user",
            "content": "My favorite color is blue.",
        },
    }

    # Simulate waiting on something (a timer, a tool result, user input, etc.)
    await asyncio.sleep(2)

    # Follow-up message, sent on the same persistent session
    yield {
        "type": "user",
        "message": {
            "role": "user",
            "content": "What is my favorite color?",
        },
    }


async def main():
    options = ClaudeAgentOptions(max_turns=10)

    async with ClaudeSDKClient(options) as client:
        await client.query(message_generator())

        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(block.text)


if __name__ == "__main__":
    asyncio.run(main())

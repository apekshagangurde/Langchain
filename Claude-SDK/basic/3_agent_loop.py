"""
Claude Agent SDK - The Agent Loop Explained

Official docs: https://code.claude.com/docs/en/agent-sdk/python
"""

import asyncio
from claude_agent_sdk import query, AssistantMessage, ResultMessage


async def main():
    async for message in query(prompt="Summarize this project"):
        if isinstance(message, AssistantMessage):
            print(f"Turn completed: {len(message.content)} content blocks")

        if isinstance(message, ResultMessage):
            if message.subtype == "success":
                print(message.result)
            else:
                print(f"Stopped: {message.subtype}")


if __name__ == "__main__":
    asyncio.run(main())

"""
Claude Agent SDK - Hello World

Official docs: https://code.claude.com/docs/en/agent-sdk/python
"""

import asyncio
from claude_agent_sdk import query, AssistantMessage


async def main():
    async for message in query(prompt="Say hello world"):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)


if __name__ == "__main__":
    asyncio.run(main())

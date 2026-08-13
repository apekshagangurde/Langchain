"""
Claude Agent SDK - Hello World (v2)

Official docs: https://code.claude.com/docs/en/agent-sdk/python
"""

import asyncio
from claude_agent_sdk import query


async def main():
    response = query(prompt="Hey, How are you? My name is Apeksha")

    async for message in response:
        print(f"Response: {message}")


if __name__ == "__main__":
    asyncio.run(main())

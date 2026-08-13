"""
Claude Agent SDK - State / Continuing a Conversation

`continue_conversation=True` on ClaudeAgentOptions continues the most
recent session, so the second query() call remembers what was said
in the first one.

Official docs: https://code.claude.com/docs/en/agent-sdk/python
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage


def print_text(message):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if hasattr(block, "text"):
                print(block.text)


async def main():
    print("=== First query ===")
    async for message in query(
        prompt="My name is Apeksha.",
        options=ClaudeAgentOptions(),
    ):
        print_text(message)

    print("\n=== Second query (continue=True) ===")
    async for message in query(
        prompt="What is my name?",
        options=ClaudeAgentOptions(continue_conversation=True),
    ):
        print_text(message)


if __name__ == "__main__":
    asyncio.run(main())

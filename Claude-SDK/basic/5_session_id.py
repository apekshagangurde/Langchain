"""
Claude Agent SDK - Capture and Resume by Session ID

`ResultMessage.session_id` gives you the ID of the session you just ran.
Pass it to `ClaudeAgentOptions(resume=session_id)` on a later query() call
to resume that exact session (instead of just "the most recent one",
which is what `continue_conversation=True` does).

Official docs: https://code.claude.com/docs/en/agent-sdk/sessions
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, ResultMessage


def print_text(message):
    if isinstance(message, AssistantMessage):
        for block in message.content:
            if hasattr(block, "text"):
                print(block.text)


async def main():
    session_id = None

    print("=== First query ===")
    async for message in query(
        prompt="My name is Apeksha.",
        options=ClaudeAgentOptions(),
    ):
        print_text(message)
        if isinstance(message, ResultMessage):
            session_id = message.session_id
            print(f"Session ID: {session_id}")

    print("\n=== Second query (resume=session_id) ===")
    async for message in query(
        prompt="What is my name?",
        options=ClaudeAgentOptions(resume=session_id),
    ):
        print_text(message)


if __name__ == "__main__":
    asyncio.run(main())

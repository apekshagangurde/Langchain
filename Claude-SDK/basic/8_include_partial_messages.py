"""
Claude Agent SDK - include_partial_messages

By default you only get whole messages once a turn finishes. Setting
`include_partial_messages=True` also yields `StreamEvent` messages as
the response is generated, letting you print text token-by-token.

`StreamEvent` fields (from claude_agent_sdk.types):
- uuid: str
- session_id: str
- event: dict  -> the raw Anthropic API stream event
                  (e.g. {"type": "content_block_delta",
                         "delta": {"type": "text_delta", "text": "..."}})
- parent_tool_use_id: str | None

Official docs: https://code.claude.com/docs/en/agent-sdk/python
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, StreamEvent


async def main():
    options = ClaudeAgentOptions(include_partial_messages=True)

    async for message in query(prompt="write long story", options=options):
        if isinstance(message, StreamEvent):
            event = message.event
            if event.get("type") == "content_block_delta":
                delta = event.get("delta", {})
                if delta.get("type") == "text_delta":
                    print(delta.get("text", ""), end="", flush=True)


if __name__ == "__main__":
    asyncio.run(main())

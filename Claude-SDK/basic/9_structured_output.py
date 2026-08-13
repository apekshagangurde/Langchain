"""
Claude Agent SDK - Structured Output

`output_format` on ClaudeAgentOptions constrains the agent's final answer
to a JSON schema (same shape as the Messages API's output_config.format:
{"type": "json_schema", "schema": {...}}). The parsed result shows up on
`ResultMessage.structured_output`.

Verified against the installed claude_agent_sdk package
(claude_agent_sdk/types.py): ClaudeAgentOptions.output_format and
ResultMessage.structured_output.
"""

import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage

SCHEMA = {
    "type": "json_schema",
    "schema": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "age": {"type": "integer"},
            "hobbies": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["name", "age", "hobbies"],
        "additionalProperties": False,
    },
}


async def main():
    options = ClaudeAgentOptions(output_format=SCHEMA)

    async for message in query(
        prompt="Generate a profile for a fictional person named Alex who is 30 and loves hiking and chess.",
        options=options,
    ):
        if isinstance(message, ResultMessage):
            print(message.structured_output)


if __name__ == "__main__":
    asyncio.run(main())

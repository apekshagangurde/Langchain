"""
Claude Agent SDK - Structured Output with a Pydantic Model

The SDK's `output_format` just takes a raw JSON schema dict
({"type": "json_schema", "schema": {...}}) — there's no built-in
Pydantic integration. So define a Pydantic model, generate its schema
with `.model_json_schema()`, and validate the result back into the
model with `.model_validate()`.
"""

import asyncio
from pydantic import BaseModel
from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


class Profile(BaseModel):
    name: str
    age: int
    hobbies: list[str]


async def main():
    options = ClaudeAgentOptions(
        output_format={
            "type": "json_schema",
            "schema": Profile.model_json_schema(),
        }
    )

    async for message in query(
        prompt="Generate a profile for a fictional person named Alex who is 30 and loves hiking and chess.",
        options=options,
    ):
        if isinstance(message, ResultMessage):
            profile = Profile.model_validate(message.structured_output)
            print(profile)
            print(profile.name, profile.age, profile.hobbies)


if __name__ == "__main__":
    asyncio.run(main())

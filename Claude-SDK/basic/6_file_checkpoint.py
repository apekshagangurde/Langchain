"""
Claude Agent SDK - File Checkpointing

File checkpointing tracks changes made through Write/Edit/NotebookEdit
tools, and lets you rewind files back to an earlier point without losing
conversation history.

Requirements:
- enable_file_checkpointing=True on ClaudeAgentOptions
- extra_args={"replay-user-messages": None} — required to get a `uuid`
  on UserMessage objects in the response stream (that uuid IS the
  checkpoint id)
- rewind_files() can't be called after a response stream has fully
  finished — call it during the loop, or resume the session with an
  empty prompt to open a fresh connection first

Official docs: https://code.claude.com/docs/en/agent-sdk/file-checkpointing
"""

import asyncio
from claude_agent_sdk import (
    ClaudeSDKClient,
    ClaudeAgentOptions,
    UserMessage,
    ResultMessage,
)

OPTIONS = ClaudeAgentOptions(
    enable_file_checkpointing=True,
    permission_mode="acceptEdits",  # auto-accept file edits without prompting
    extra_args={"replay-user-messages": None},  # required for checkpoint uuids
)


async def main():
    checkpoint_id = None
    session_id = None

    async with ClaudeSDKClient(OPTIONS) as client:
        # Turn 1: create the file
        await client.query("Create a file named config.txt with the text 'v1'")
        async for message in client.receive_response():
            if isinstance(message, UserMessage) and message.uuid and not checkpoint_id:
                checkpoint_id = message.uuid  # restore point: state after turn 1
            if isinstance(message, ResultMessage):
                session_id = message.session_id

        # Turn 2: modify the file
        await client.query("Change config.txt to say 'v2' instead")
        async for message in client.receive_response():
            pass

    print(f"Checkpoint captured: {checkpoint_id}")

    # Rewind: resume the session with an empty prompt to open a fresh
    # connection, then rewind files back to the turn-1 checkpoint.
    if checkpoint_id and session_id:
        async with ClaudeSDKClient(
            ClaudeAgentOptions(enable_file_checkpointing=True, resume=session_id)
        ) as client:
            await client.query("")  # empty prompt just opens the connection
            async for message in client.receive_response():
                await client.rewind_files(checkpoint_id)
                break

        print(f"Rewound to checkpoint: {checkpoint_id} (config.txt back to 'v1')")


if __name__ == "__main__":
    asyncio.run(main())

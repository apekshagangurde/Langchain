"""
Claude Agent SDK - Hooks (PreToolUse)

Hooks let your code intercept an agent's tool calls before/after they run,
without the model being aware of the interception — unlike `can_use_tool`
(one global callback checked on every tool call), hooks are registered per
event ("PreToolUse", "PostToolUse", ...) and per tool via a HookMatcher, so
you can attach different logic to different tools.

This example registers a PreToolUse hook on the Bash tool that inspects the
command Claude is about to run and denies it outright if it matches a
destructive pattern (e.g. `rm -rf`) — before the shell ever executes it.

Official docs: https://code.claude.com/docs/en/agent-sdk/python
"""

import asyncio
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    HookMatcher,
    HookContext,
    PreToolUseHookInput,
    AssistantMessage,
    ResultMessage,
)

DANGEROUS_SUBSTRINGS = ("rm -rf", "sudo ", ":(){:|:&};:")


async def block_dangerous_bash(
    input_data: PreToolUseHookInput, tool_use_id: str | None, context: HookContext
):
    command = input_data["tool_input"].get("command", "")

    if any(pattern in command for pattern in DANGEROUS_SUBSTRINGS):
        print(f"[hook] blocked: {command}")
        return {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": "deny",
                "permissionDecisionReason": f"Command matched a blocked pattern: {command}",
            }
        }

    print(f"[hook] allowed: {command}")
    return {}


async def main():
    options = ClaudeAgentOptions(
        allowed_tools=["Bash"],
        hooks={
            "PreToolUse": [HookMatcher(matcher="Bash", hooks=[block_dangerous_bash])]
        },
    )

    async for message in query(
        prompt="Run `ls` in the current directory, then try running `rm -rf /tmp/should-be-blocked`.",
        options=options,
    ):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if hasattr(block, "text"):
                    print(block.text)

        if isinstance(message, ResultMessage):
            print("\n--- Done ---")
            if message.subtype == "success":
                print(message.result)
            else:
                print(f"Stopped: {message.subtype}")


if __name__ == "__main__":
    asyncio.run(main())

"""
Debug-and-PR Agent — GitHub MCP server over HTTP

Same as agent.py, but connects to GitHub's hosted remote MCP server over
HTTP/Streamable-HTTP instead of running the server locally via Docker/stdio.
No Docker required — auth is a Bearer token sent as a request header instead
of an env var passed into a container.

Setup:
  uv add python-dotenv          # if not already installed

.env variables required (see .env.example):
  ANTHROPIC_API_KEY
  GITHUB_PERSONAL_ACCESS_TOKEN   # needs repo + pull_request scopes
  REPO_PATH                      # absolute path to the local git repo to debug
  BUG_DESCRIPTION                # what's broken / what to fix
"""

import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from claude_agent_sdk import (
    query,
    ClaudeAgentOptions,
    AssistantMessage,
    ToolUseBlock,
    ResultMessage,
    PermissionResultAllow,
    PermissionResultDeny,
)

load_dotenv()

GITHUB_TOKEN = os.environ["GITHUB_PERSONAL_ACCESS_TOKEN"]
REPO_PATH = os.environ["REPO_PATH"]
BUG_DESCRIPTION = os.environ.get(
    "BUG_DESCRIPTION",
    "There is a bug somewhere in this codebase. Find it, fix it, and verify with tests.",
)

# Substrings that mark a GitHub MCP tool call as read-only / safe to auto-approve
SAFE_PREFIXES = ("get_", "list_", "search_")
# Substrings that mark a GitHub MCP tool call as destructive / needs confirmation
DESTRUCTIVE_SUBSTRINGS = ("create", "push", "merge", "delete", "close", "update")


# GitHub's hosted remote MCP server — Streamable HTTP transport, no local
# Docker container to run. Auth is a Bearer token in the Authorization header
# instead of an env var injected into a container.
github_server = {
    "type": "http",
    "url": "https://api.githubcopilot.com/mcp/",
    "headers": {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
    },
}


async def can_use_tool(tool_name, tool_input, context) -> PermissionResultAllow | PermissionResultDeny:
    # Only the GitHub MCP tools reach this callback — local file/bash tools
    # are in `allowed_tools` below and never hit this function.
    if tool_name.startswith("mcp__github__") and any(
        s in tool_name for s in DESTRUCTIVE_SUBSTRINGS
    ):
        print(f"\n[permission] Claude wants to call: {tool_name}")
        print(f"[permission] input: {tool_input}")

        if not sys.stdin.isatty():
            # No live terminal to answer y/n (e.g. run by an automated
            # process). Refuse destructive GitHub actions rather than
            # hang on input() or silently allow a real push/PR.
            print("[permission] No interactive terminal detected — denying by default (dry run).")
            return PermissionResultDeny(
                message="Denied: not running interactively, so this destructive "
                "action can't be confirmed. Report what you would have done instead."
            )

        answer = input("[permission] Allow this? (y/n): ").strip().lower()
        if answer == "y":
            return PermissionResultAllow()
        return PermissionResultDeny(message="User denied this action.")

    return PermissionResultAllow()


SYSTEM_PROMPT = """\
You are a debugging agent working in a local git repository. Follow this
workflow exactly:

1. Reproduce: read the relevant files and understand the bug described
   by the user.
2. Locate: find the root cause. Don't guess — trace through the code.
3. Fix: apply the smallest correct fix. Don't refactor unrelated code.
4. Verify: if the repo has a test suite, run it with Bash and do not
   proceed until tests pass. If there is no test suite, verify manually
   with Bash instead (e.g. compile/run the affected file against a
   couple of sample inputs) and show that output as your evidence.
5. Ship: once verified, use the GitHub MCP tools to:
   - create a new branch (e.g. fix/<short-description>)
   - commit the fix with a clear commit message
   - push the branch
   - open a pull request with a description covering: what was broken,
     what you changed, and how you verified it (include test output)

Report the pull request URL in your final response.
"""


async def prompt_stream():
    # can_use_tool requires streaming input mode (an async iterable prompt),
    # not a plain string.
    yield {
        "type": "user",
        "message": {"role": "user", "content": BUG_DESCRIPTION},
    }


async def main():
    options = ClaudeAgentOptions(
        cwd=Path(REPO_PATH),
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={"github": github_server},
        allowed_tools=["Read", "Grep", "Glob", "Edit", "Bash"],
        can_use_tool=can_use_tool,
        max_turns=40,
    )

    async for message in query(prompt=prompt_stream(), options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, ToolUseBlock):
                    print(f"[tool call] {block.name}({block.input})")
                elif hasattr(block, "text"):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print("\n--- Done ---")
            if message.subtype == "success":
                print(message.result)
            else:
                print(f"Stopped: {message.subtype}")


if __name__ == "__main__":
    asyncio.run(main())

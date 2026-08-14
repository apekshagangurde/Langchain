"""
Debug-and-PR Agent

An agent that:
  1. Reads/greps/greps a local repo to find and fix a described bug
  2. Runs tests to verify the fix
  3. Uses the GitHub MCP server to create a branch, commit, push, and
     open a pull request

Local file/bash tools are auto-approved via `allowed_tools`. GitHub MCP
tools are gated through a `can_use_tool` callback: read-only calls
(get/list/search) are auto-approved, anything that looks destructive
(create/push/merge/delete/close) asks for a y/n confirmation in the
terminal before running.

Setup:
  uv add python-dotenv          # if not already installed
  Docker Desktop must be running (the GitHub MCP server runs via
  `docker run ...`) — see https://github.com/github/github-mcp-server

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


github_server = {
    "type": "stdio",
    "command": "docker",
    "args": [
        "run",
        "-i",
        "--rm",
        "-e",
        "GITHUB_PERSONAL_ACCESS_TOKEN",
        "-e",
        "GITHUB_TOOLSETS=repos,issues,pull_requests",
        "ghcr.io/github/github-mcp-server",
    ],
    "env": {"GITHUB_PERSONAL_ACCESS_TOKEN": GITHUB_TOKEN},
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

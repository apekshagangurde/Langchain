# PermissionMode

Permission modes for controlling tool execution. Set via `ClaudeAgentOptions.permission_mode`, or changed mid-session with `ClaudeSDKClient.set_permission_mode()`. See `ClaudeAgentOptions`.

```python
PermissionMode = Literal[
    "default",           # Standard permission behavior
    "acceptEdits",        # Auto-accept file edits
    "plan",                # Planning mode - explore without editing
    "dontAsk",             # Deny anything not pre-approved instead of prompting
    "bypassPermissions",   # Bypass permission checks; explicit ask rules still prompt (use with caution)
    "auto",                # Model classifier approves or denies permission prompts
]
```

| Mode | Description |
|---|---|
| `default` | Standard permission behavior. Tool calls not covered by `allowed_tools`, allow rules, or `can_use_tool` fall through to a permission prompt |
| `acceptEdits` | Auto-accepts file edit tool calls (e.g. `Edit`, `Write`); other tools still follow normal permission flow |
| `plan` | Planning mode — Claude can explore and read but cannot make edits or take other mutating actions |
| `dontAsk` | Instead of prompting for anything not pre-approved, denies it outright. `AskUserQuestion`, connector tools set to ask, and MCP tools marked `requiresUserInteraction` are denied here too, since they would otherwise reach a prompt. See `can_use_tool` |
| `bypassPermissions` | Bypasses permission checks entirely. Explicit ask rules (e.g. deny rules scoped with a pattern) still prompt. Use with caution — this skips the safety net for auto-approved actions |
| `auto` | A model classifier decides whether to approve or deny permission prompts instead of asking the user |

```python
from claude_agent_sdk import ClaudeAgentOptions, ClaudeSDKClient

options = ClaudeAgentOptions(permission_mode="acceptEdits")

async with ClaudeSDKClient(options=options) as client:
    await client.query("Refactor this file")
    # Switch modes mid-session
    await client.set_permission_mode("plan")
```

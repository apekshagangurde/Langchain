# EffortLevel

Effort levels for guiding thinking depth. Set via `ClaudeAgentOptions.effort`. Works together with adaptive thinking to control how much reasoning Claude does before responding. See `ClaudeAgentOptions`.

```python
EffortLevel = Literal[
    "low",     # Minimal thinking, fastest responses
    "medium",  # Moderate thinking
    "high",    # Deep reasoning
    "xhigh",   # Extended reasoning; falls back to "high" on models that don't support it
    "max",     # Maximum effort
]
```

| Level | Description |
|---|---|
| `low` | Minimal thinking, fastest responses |
| `medium` | Moderate thinking |
| `high` | Deep reasoning (default) |
| `xhigh` | Extended reasoning depth (supported on select models, e.g. Opus 4.7+); falls back to `"high"` on models that don't support it |
| `max` | Maximum effort |

```python
from claude_agent_sdk import ClaudeAgentOptions, query

options = ClaudeAgentOptions(effort="high")

async for message in query(prompt="Explain this algorithm's complexity", options=options):
    print(message)
```

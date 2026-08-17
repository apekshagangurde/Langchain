# ToolAnnotations

Re-exported from `mcp.types` (also available as
`from claude_agent_sdk import ToolAnnotations`). All fields are optional
hints; clients should not rely on them for security decisions.

| Field | Type | Default | Description |
|---|---|---|---|
| `title` | `str \| None` | `None` | Human-readable title for the tool |
| `readOnlyHint` | `bool \| None` | `False` | If `True`, the tool does not modify its environment |
| `destructiveHint` | `bool \| None` | `True` | If `True`, the tool may perform destructive updates (only meaningful when `readOnlyHint` is `False`) |
| `idempotentHint` | `bool \| None` | `False` | If `True`, repeated calls with the same arguments have no additional effect (only meaningful when `readOnlyHint` is `False`) |
| `openWorldHint` | `bool \| None` | `True` | If `True`, the tool interacts with external entities (for example, web search). If `False`, the tool's domain is closed (for example, a memory tool) |

```python
from claude_agent_sdk import tool, ToolAnnotations
from typing import Any


@tool(
    "search",
    "Search the web",
    {"query": str},
    annotations=ToolAnnotations(readOnlyHint=True, openWorldHint=True),
)
async def search(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Results for: {args['query']}"}]}
```

# tool()

Decorator for defining MCP tools with type safety.

```python
def tool(
    name: str,
    description: str,
    input_schema: type | dict[str, Any],
    annotations: ToolAnnotations | None = None
) -> Callable[[Callable[[Any], Awaitable[dict[str, Any]]]], SdkMcpTool[Any]]
```

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `name` | `str` | Unique identifier for the tool |
| `description` | `str` | Human-readable description of what the tool does |
| `input_schema` | `type \| dict[str, Any]` | Schema defining the tool's input parameters (see below) |
| `annotations` | `ToolAnnotations \| None` | Optional MCP tool annotations providing behavioral hints to clients |

---

## Breaking it down, piece by piece

### 1. What is `tool()`?

The documentation says: "Decorator for defining MCP tools with type safety."

In simple English: `tool()` lets you turn a normal Python function into a
tool that Claude can call.

### 2. Why is this called a decorator?

Python decorators allow you to modify/wrap a function. Similarly:

```python
@tool(...)
async def calculate(...):
    ...
```

means: "Take this Python function and turn/register it as an MCP tool."

### 3. What does "returns a decorator function" mean?

The documentation says:

> A decorator function that wraps the tool implementation and returns an
> `SdkMcpTool` instance.

In simple English: `tool(name, description, input_schema)` itself doesn't
directly turn your function into a tool — it first builds and hands back
*another* function (the actual decorator), and that returned function is
what does the wrapping. That's why you call it with parentheses right above
your `async def`, like `@tool("greet", "Greet a user", {"name": str})`
rather than just `@tool`.

So there are two steps happening, even though it looks like one:

1. `tool("greet", "Greet a user", {"name": str})` runs first and returns a
   decorator (a function waiting for your `greet` function).
2. That returned decorator is then applied to `async def greet(...)`,
   producing an `SdkMcpTool` object — the thing your MCP server actually
   registers, not your original plain `async def` function.

### 4. `name`

```python
name: str
```

This is the name of your tool.

### 5. `description`

```python
description: str
```

This explains what the tool does.

Example:

```python
description="Adds two numbers together"
```

### 6. `input_schema`

This is probably the most important parameter.

```python
input_schema: type | dict[str, Any]
```

It tells Claude: "What inputs does my tool require?"

**Input schema options**

Simple type mapping (recommended):

```python
{"text": str, "count": int, "enabled": bool}
```

JSON Schema format (for complex validation):

```python
{
    "type": "object",
    "properties": {
        "text": {"type": "string"},
        "count": {"type": "integer", "minimum": 0},
    },
    "required": ["text"],
}
```

### Returns

A decorator function that wraps the tool implementation and returns an
`SdkMcpTool` instance.

### Example

```python
from claude_agent_sdk import tool
from typing import Any


@tool("greet", "Greet a user", {"name": str})
async def greet(args: dict[str, Any]) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": f"Hello, {args['name']}!"}]}
```

### 13. Now see why `create_sdk_mcp_server()` exists

This is the next important connection.

You can create multiple tools:

```python
@tool("greet", "Greet a user", {"name": str})
async def greet(args):
    ...


@tool("add", "Add two numbers", {"a": int, "b": int})
async def add(args):
    ...
```

Now you have:

```
SdkMcpTool
   │
   ├── greet
   │
   └── add
```

Then you put them into an MCP server:

```python
calculator = create_sdk_mcp_server(
    name="my_server",
    tools=[greet, add]
)
```

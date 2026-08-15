# Functions

Signature blocks and bare `async for` / `async with` fragments on this page
are illustrative. To run them, wrap the body in `async def main(): ...` and
call `asyncio.run(main())`.

## query()

Creates a new session for each interaction with Claude Code by default.
Returns an async iterator that yields messages as they arrive. Each call to
`query()` starts fresh with no memory of previous interactions unless you
pass `continue_conversation=True` or `resume` in `ClaudeAgentOptions`. See
Sessions.

```python
async def query(
    *,
    prompt: str | AsyncIterable[dict[str, Any]],
    options: ClaudeAgentOptions | None = None,
    transport: Transport | None = None
) -> AsyncIterator[Message]
```

### Parameters

| Parameter | Type | Description |
|---|---|---|
| `prompt` | `str \| AsyncIterable[dict]` | The input prompt as a string or async iterable for streaming mode |
| `options` | `ClaudeAgentOptions \| None` | Optional configuration object (defaults to `ClaudeAgentOptions()` if `None`) |
| `transport` | `Transport \| None` | Optional custom transport for communicating with the CLI process |

### Returns

Returns an `AsyncIterator[Message]` that yields messages from the
conversation.

### Example — with options

```python
import asyncio
from claude_agent_sdk import query, ClaudeAgentOptions


async def main():
    options = ClaudeAgentOptions(
        system_prompt="You are an expert Python developer",
        permission_mode="acceptEdits",
    )

    async for message in query(prompt="Create a Python web server", options=options):
        print(message)


asyncio.run(main())
```

`query()` starts an interaction with Claude and gives you the messages
Claude produces as it works.

```python
async for message in query(
    prompt="Find the bug in this repository"
):
    print(message)
```

---

## Breaking the signature down, piece by piece

### Why do we need `async def`?

This is Python's asynchronous programming. Don't worry about the advanced
meaning yet. For now, think: Claude takes time to respond, and your program
shouldn't be treated like everything happens instantly.

### `async for message in query(...)`

**Message** — a message is something Claude sends back. For example, it
could represent:

- assistant message
- tool use
- tool result
- result
- etc.

**Iterator** — an iterator means "you can get items one after another." For
example:

- Item 1
- Item 2
- Item 3
- Item 4

**AsyncIterator** — same idea, except the next item may arrive
asynchronously.

### The `*`

You see:

```python
async def query(
    *,
    prompt=...,
    options=...,
    transport=...
)
```

The `*` means these parameters are keyword-only. So you should write:

```python
query(
    prompt="Hello",
    options=options
)
```

rather than:

```python
query(
    "Hello",
    options
)
```

### Shape of the call

```
query()
   │
   ├── prompt
   │
   └── options
          │
          ├── system_prompt
          ├── permission_mode
          ├── allowed_tools
          ├── mcp_servers
          ├── hooks
          └── other configuration
```

### `transport`

The third parameter:

```python
transport: Transport | None = None
```

This is more advanced. It controls how the SDK communicates with the Claude
Code process.

### The return type

The end of the signature says:

```python
-> AsyncIterator[Message]
```

This means: `query()` gives you an asynchronous stream/iterator of `Message`
objects.

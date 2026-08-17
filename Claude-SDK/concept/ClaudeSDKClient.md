# Classes

## ClaudeSDKClient

Maintains a conversation session across multiple exchanges. This is the
Python equivalent of how the TypeScript SDK's `query()` function works
internally — it creates a client object that can continue conversations.
See the comparison with [`query()`](query_vs_ClaudeSDKClient.md).

```python
class ClaudeSDKClient:
    def __init__(self, options: ClaudeAgentOptions | None = None, transport: Transport | None = None)
    async def connect(self, prompt: str | AsyncIterable[dict] | None = None) -> None
    async def query(self, prompt: str | AsyncIterable[dict], session_id: str = "default") -> None
    async def receive_messages(self) -> AsyncIterator[Message]
    async def receive_response(self) -> AsyncIterator[Message]
    async def interrupt(self) -> None
    async def set_permission_mode(self, mode: str) -> None
    async def set_model(self, model: str | None = None) -> None
    async def rewind_files(self, user_message_id: str) -> None
    async def get_mcp_status(self) -> McpStatusResponse
    async def reconnect_mcp_server(self, server_name: str) -> None
    async def toggle_mcp_server(self, server_name: str, enabled: bool) -> None
    async def stop_task(self, task_id: str) -> None
    async def get_server_info(self) -> dict[str, Any] | None
    async def disconnect(self) -> None
```

### Methods

| Method | Description |
|---|---|
| `__init__(options)` | Initialize the client with optional configuration |
| `connect(prompt)` | Connect to Claude with an optional initial prompt or message stream |
| `query(prompt, session_id)` | Send a new request in streaming mode |
| `receive_messages()` | Receive all messages from Claude as an async iterator |
| `receive_response()` | Receive messages until and including a `ResultMessage` |
| `interrupt()` | Send interrupt signal (only works in streaming mode) |
| `set_permission_mode(mode)` | Change the permission mode for the current session |
| `set_model(model)` | Change the model for the current session. Pass `None` to reset to default |
| `rewind_files(user_message_id)` | Restore files to their state at the specified user message. Requires `enable_file_checkpointing=True`. See File checkpointing |
| `get_mcp_status()` | Get the status of all configured MCP servers. Returns `McpStatusResponse` |
| `reconnect_mcp_server(server_name)` | Retry connecting to an MCP server that failed or was disconnected |
| `toggle_mcp_server(server_name, enabled)` | Enable or disable an MCP server mid-session. Disabling removes its tools |
| `stop_task(task_id)` | Stop a running background task. A `TaskNotificationMessage` with status `"stopped"` follows in the message stream |
| `get_server_info()` | Get server information including session ID and capabilities |
| `disconnect()` | Disconnect from Claude |

### Shape of the client

```
ClaudeSDKClient
│
├── connect()
│      └── Start the session
│
├── query()
│      └── Send a new request
│
├── receive_messages()
│      └── Receive the message stream
│
├── receive_response()
│      └── Receive until request finishes
│
├── interrupt()
│      └── Stop current work
│
├── set_permission_mode()
│      └── Change permissions
│
├── set_model()
│      └── Change model
│
├── rewind_files()
│      └── Restore checkpointed files
│
├── get_mcp_status()
│      └── Check MCP servers
│
├── reconnect_mcp_server()
│      └── Retry MCP connection
│
├── toggle_mcp_server()
│      └── Enable/disable MCP
│
├── stop_task()
│      └── Stop background task
│
├── get_server_info()
│      └── Get session/server info
│
└── disconnect()
       └── End the session
```

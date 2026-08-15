# Choosing between query() and ClaudeSDKClient

The Python SDK provides two ways to interact with Claude Code:

- **`query()`** is a single async function: you give it a prompt (and
  options), it opens a connection, streams back messages, and closes the
  connection when done. It's unidirectional and stateless — you can't send a
  follow-up mid-run, and each call starts a fresh session with no memory of a
  previous `query()` call unless you explicitly resume one via
  `continue_conversation`/`resume`. This is what `basic/1_hello.py` through
  `basic/3_agent_loop.py`, and both `task/agent.py` / `task/agent2.py`, use —
  a fixed task, run start to finish, done.

- **`ClaudeSDKClient`** is a class you instantiate and hold onto: you call
  `.connect()`, then can call `.query()` multiple times against the *same*
  session, `.receive_response()` to read messages, and `.interrupt()` to stop
  Claude mid-turn. It's bidirectional and stateful — the conversation history
  persists across calls automatically, and you decide when the connection
  opens and closes. This is the right choice for anything that looks like a
  chat: a REPL, a long-running assistant, or a workflow where what you send
  next depends on what Claude just said.

**Rule of thumb:** if you know the whole prompt upfront and just want an
answer or a completed task, use `query()`. If the interaction is ongoing —
multiple turns, needs to react to intermediate output, or might need to be
interrupted — use `ClaudeSDKClient`.

| Feature | `query()` | `ClaudeSDKClient` |
|---|---|---|
| Session | Creates a new session by default | Reuses same session |
| Conversation | Single exchange | Multiple exchanges in same context |
| Connection | Managed automatically | Manual control |
| Streaming Input | ✅ Supported | ✅ Supported |
| Interrupts | ❌ Not supported | ✅ Supported |
| Hooks | ✅ Supported | ✅ Supported |
| Custom Tools | ✅ Supported | ✅ Supported |
| Continue Chat | Manual via `continue_conversation` or `resume` | ✅ Automatic |
| Use Case | One-off tasks | Continuous conversations |

## Row-by-row

- **Session / Conversation** — `query()` spins up a brand-new session on
  every call; anything from a prior call is gone unless you pass
  `continue_conversation=True` or `resume=<session_id>` in options.
  `ClaudeSDKClient` keeps one session alive across as many `.query()` calls
  as you make on the same instance, so message history just accumulates.

- **Connection** — `query()` opens and tears down the transport connection
  for you, inside the call. `ClaudeSDKClient` requires you to call
  `.connect()` (and eventually disconnect, e.g. via `async with`), giving you
  the window to send multiple messages or interrupt before closing it.

- **Streaming Input** — both accept an `AsyncIterable` of message dicts as
  the prompt instead of a plain string (this is what `can_use_tool` requires
  in `task/agent.py`/`agent2.py` — see `prompt_stream()` in those files).

- **Interrupts** — only `ClaudeSDKClient` exposes `.interrupt()`, which stops
  Claude mid-turn. `query()` has no handle to call anything on once it's
  running — you either let it finish or cancel the whole async task.

- **Hooks / Custom Tools** — both take the same `ClaudeAgentOptions`
  (`hooks=...`, `mcp_servers=...`), so anything demonstrated in
  `basic/14_hooks.py` or the custom-tool examples works identically under
  either.

- **Continue Chat** — with `query()` you have to explicitly say "continue
  this" (`continue_conversation` / `resume`) on the next call, or it starts
  fresh. `ClaudeSDKClient` continues automatically because the session is
  just kept open on the object.

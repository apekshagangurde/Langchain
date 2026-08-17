# Session Management Functions

Utility functions for listing, reading, renaming, and tagging past sessions.
All of these are synchronous (they return immediately — no `await`), unlike
`query()` / `ClaudeSDKClient`.

```
list_sessions()
        ↓
find sessions

get_session_info()
        ↓
get information about ONE session

get_session_messages()
        ↓
read messages inside a session

rename_session()
        ↓
give a session a custom name

tag_session()
        ↓
attach a tag to a session
```

## list_sessions()

Lists past sessions with metadata. Filter by project directory or list
sessions across all projects. Synchronous; returns immediately.

```python
def list_sessions(
    directory: str | None = None,
    limit: int | None = None,
    offset: int = 0,
    include_worktrees: bool = True
) -> list[SDKSessionInfo]
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `directory` | `str \| None` | `None` | Directory to list sessions for. When omitted, returns sessions across all projects |
| `limit` | `int \| None` | `None` | Maximum number of sessions to return |
| `offset` | `int` | `0` | Number of sessions to skip from the start of the sorted results. Use with `limit` for pagination |
| `include_worktrees` | `bool` | `True` | When `directory` is inside a git repository, include sessions from all worktree paths |

### Return type: `SDKSessionInfo`

| Property | Type | Description |
|---|---|---|
| `session_id` | `str` | Unique session identifier |
| `summary` | `str` | Display title: custom title, auto-generated summary, or first prompt |
| `last_modified` | `int` | Last modified time in milliseconds since epoch |
| `file_size` | `int \| None` | Session file size in bytes (`None` for remote storage backends) |
| `custom_title` | `str \| None` | User-set session title |
| `first_prompt` | `str \| None` | First meaningful user prompt in the session |
| `git_branch` | `str \| None` | Git branch at the end of the session |
| `cwd` | `str \| None` | Working directory for the session |
| `tag` | `str \| None` | User-set session tag (see `tag_session()`) |
| `created_at` | `int \| None` | Session creation time in milliseconds since epoch |

### Example

Print the 10 most recent sessions for a project. Results are sorted by
`last_modified` descending, so the first item is the newest. Omit
`directory` to search across all projects.

```python
from claude_agent_sdk import list_sessions

for session in list_sessions(directory="/path/to/project", limit=10):
    print(f"{session.summary} ({session.session_id})")
```

---

## get_session_messages()

Retrieves messages from a past session. Synchronous; returns immediately.

```python
def get_session_messages(
    session_id: str,
    directory: str | None = None,
    limit: int | None = None,
    offset: int = 0
) -> list[SessionMessage]
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `session_id` | `str` | required | The session ID to retrieve messages for |
| `directory` | `str \| None` | `None` | Project directory to look in. When omitted, searches all projects |
| `limit` | `int \| None` | `None` | Maximum number of messages to return |
| `offset` | `int` | `0` | Number of messages to skip from the start |

### Return type: `SessionMessage`

| Property | Type | Description |
|---|---|---|
| `type` | `Literal["user", "assistant"]` | Message role |
| `uuid` | `str` | Unique message identifier |
| `session_id` | `str` | Session identifier |
| `message` | `Any` | Raw message content |
| `parent_tool_use_id` | `None` | Reserved for future use |

### Example

```python
from claude_agent_sdk import list_sessions, get_session_messages

sessions = list_sessions(limit=1)
if sessions:
    messages = get_session_messages(sessions[0].session_id)
    for msg in messages:
        print(f"[{msg.type}] {msg.uuid}")
```

---

## get_session_info()

Reads metadata for a single session by ID without scanning the full project
directory. Synchronous; returns immediately.

```python
def get_session_info(
    session_id: str,
    directory: str | None = None,
) -> SDKSessionInfo | None
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `session_id` | `str` | required | UUID of the session to look up |
| `directory` | `str \| None` | `None` | Project directory path. When omitted, searches all project directories |

Returns `SDKSessionInfo`, or `None` if the session is not found.

### Example

Look up a single session's metadata without scanning the project directory.
Useful when you already have a session ID from a previous run.

```python
from claude_agent_sdk import get_session_info

info = get_session_info("550e8400-e29b-41d4-a716-446655440000")
if info:
    print(f"{info.summary} (branch: {info.git_branch}, tag: {info.tag})")
```

---

## rename_session()

Renames a session by appending a custom-title entry. Repeated calls are
safe; the most recent title wins. Synchronous.

```python
def rename_session(
    session_id: str,
    title: str,
    directory: str | None = None,
) -> None
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `session_id` | `str` | required | UUID of the session to rename |
| `title` | `str` | required | New title. Must be non-empty after stripping whitespace |
| `directory` | `str \| None` | `None` | Project directory path. When omitted, searches all project directories |

Raises `ValueError` if `session_id` is not a valid UUID or `title` is empty;
`FileNotFoundError` if the session cannot be found.

### Example

Rename the most recent session so it's easier to find later. The new title
appears in `SDKSessionInfo.custom_title` on subsequent reads.

```python
from claude_agent_sdk import list_sessions, rename_session

sessions = list_sessions(directory="/path/to/project", limit=1)
if sessions:
    rename_session(sessions[0].session_id, "Refactor auth module")
```

---

## tag_session()

Tags a session. Pass `None` to clear the tag. Repeated calls are safe; the
most recent tag wins. Synchronous.

```python
def tag_session(
    session_id: str,
    tag: str | None,
    directory: str | None = None,
) -> None
```

### Parameters

| Parameter | Type | Default | Description |
|---|---|---|---|
| `session_id` | `str` | required | UUID of the session to tag |
| `tag` | `str \| None` | required | Tag string, or `None` to clear. Unicode-sanitized before storing |
| `directory` | `str \| None` | `None` | Project directory path. When omitted, searches all project directories |

Raises `ValueError` if `session_id` is not a valid UUID or `tag` is empty
after sanitization; `FileNotFoundError` if the session cannot be found.

### Example

Tag a session, then filter by that tag on a later read. Pass `None` to
clear an existing tag.

```python
from claude_agent_sdk import list_sessions, tag_session

# Tag the most recent session
sessions = list_sessions(directory="/path/to/project", limit=1)
if sessions:
    tag_session(sessions[0].session_id, "needs-review")

# Later: find all sessions with that tag
for session in list_sessions(directory="/path/to/project"):
    if session.tag == "needs-review":
        print(session.summary)
```

# ClaudeAgentOptions

Configuration dataclass for Claude Code queries.

```python
@dataclass
class ClaudeAgentOptions:
    tools: list[str] | ToolsPreset | None = None
    allowed_tools: list[str] = field(default_factory=list)
    system_prompt: str | SystemPromptPreset | SystemPromptFile | None = None
    mcp_servers: dict[str, McpServerConfig] | str | Path = field(default_factory=dict)
    strict_mcp_config: bool = False
    permission_mode: PermissionMode | None = None
    continue_conversation: bool = False
    resume: str | None = None
    session_id: str | None = None
    max_turns: int | None = None
    max_budget_usd: float | None = None
    disallowed_tools: list[str] = field(default_factory=list)
    model: str | None = None
    fallback_model: str | None = None
    betas: list[SdkBeta] = field(default_factory=list)
    output_format: dict[str, Any] | None = None
    permission_prompt_tool_name: str | None = None
    cwd: str | Path | None = None
    cli_path: str | Path | None = None
    settings: str | None = None
    add_dirs: list[str | Path] = field(default_factory=list)
    env: dict[str, str] = field(default_factory=dict)
    extra_args: dict[str, str | None] = field(default_factory=dict)
    max_buffer_size: int | None = None
    debug_stderr: Any = sys.stderr  # Deprecated
    stderr: Callable[[str], None] | None = None
    can_use_tool: CanUseTool | None = None
    hooks: dict[HookEvent, list[HookMatcher]] | None = None
    user: str | None = None
    include_partial_messages: bool = False
    include_hook_events: bool = False
    fork_session: bool = False
    resume_session_at: str | None = None
    resume_drops_turn: str | None = None
    agents: dict[str, AgentDefinition] | None = None
    setting_sources: list[SettingSource] | None = None
    skills: list[str] | Literal["all"] | None = None
    sandbox: SandboxSettings | None = None
    plugins: list[SdkPluginConfig] = field(default_factory=list)
    max_thinking_tokens: int | None = None  # Deprecated: use thinking instead
    thinking: ThinkingConfig | None = None
    effort: EffortLevel | None = None
    enable_file_checkpointing: bool = False
    session_store: SessionStore | None = None
    session_store_flush: SessionStoreFlushMode = "batched"
    load_timeout_ms: int = 60_000
    task_budget: TaskBudget | None = None
```

### Properties

| Property | Type | Default | Description |
|---|---|---|---|
| `tools` | `list[str] \| ToolsPreset \| None` | `None` | Tools configuration. Use `{"type": "preset", "preset": "claude_code"}` for Claude Code's default tools |
| `allowed_tools` | `list[str]` | `[]` | Tools to auto-approve without prompting. This does not restrict Claude to only these tools. If you name one of the task-tracking tools here, Claude Code also opts the session in. Other unlisted tools fall through to `permission_mode` and `can_use_tool`. Use `disallowed_tools` to block tools. See Permissions |
| `system_prompt` | `str \| SystemPromptPreset \| SystemPromptFile \| None` | `None` | System prompt configuration. Pass a string for a custom prompt, `{"type": "preset", "preset": "claude_code"}` for Claude Code's system prompt with optional `"append"`, or `{"type": "file", "path": "..."}` to load a large prompt from disk. See `SystemPromptPreset` and `SystemPromptFile` |
| `mcp_servers` | `dict[str, McpServerConfig] \| str \| Path` | `{}` | MCP server configurations or path to config file |
| `strict_mcp_config` | `bool` | `False` | When `True`, use only the servers passed in `mcp_servers` and ignore project `.mcp.json`, user settings, plugin-provided MCP servers, and claude.ai connectors. Maps to the CLI `--strict-mcp-config` flag |
| `permission_mode` | `PermissionMode \| None` | `None` | Permission mode for tool usage |
| `continue_conversation` | `bool` | `False` | Continue the most recent conversation |
| `resume` | `str \| None` | `None` | Session ID to resume |
| `session_id` | `str \| None` | `None` | Use a specific session ID instead of an auto-generated one. Must be a valid UUID. Can't be combined with `continue_conversation` or `resume` unless `fork_session` is also set |
| `max_turns` | `int \| None` | `None` | Maximum agentic turns (tool-use round trips) |
| `max_budget_usd` | `float \| None` | `None` | Stop the query when the client-side cost estimate reaches this USD value. Compared against the same estimate as `total_cost_usd`; see Track cost and usage for accuracy caveats |
| `disallowed_tools` | `list[str]` | `[]` | Tools to deny. A bare name such as `"Bash"` removes the tool from Claude's context. A scoped rule such as `"Bash(rm *)"` leaves the tool available and denies matching calls in every permission mode, including `bypassPermissions`. See Permissions |
| `enable_file_checkpointing` | `bool` | `False` | Enable file change tracking for rewinding. See File checkpointing |
| `model` | `str \| None` | `None` | Claude model alias or full model name. See accepted values and provider-specific IDs |
| `fallback_model` | `str \| None` | `None` | Fallback model to use if the primary model fails |
| `betas` | `list[SdkBeta]` | `[]` | Beta features to enable. See `SdkBeta` for available options |
| `output_format` | `dict[str, Any] \| None` | `None` | Output format for structured responses (e.g., `{"type": "json_schema", "schema": {...}}`). See Structured outputs for details |
| `permission_prompt_tool_name` | `str \| None` | `None` | MCP tool name for permission prompts |
| `cwd` | `str \| Path \| None` | `None` | Current working directory |
| `cli_path` | `str \| Path \| None` | `None` | Custom path to the Claude Code CLI executable |
| `settings` | `str \| None` | `None` | Path to settings file |
| `add_dirs` | `list[str \| Path]` | `[]` | Additional directories Claude can access |
| `env` | `dict[str, str]` | `{}` | Environment variables merged on top of the inherited process environment. See Environment variables for variables the underlying CLI reads, and [Handle slow or stalled API responses](#handle-slow-or-stalled-api-responses) for timeout-related variables |
| `extra_args` | `dict[str, str \| None]` | `{}` | Additional CLI arguments to pass directly to the CLI |
| `max_buffer_size` | `int \| None` | `None` | Maximum bytes when buffering CLI stdout |
| `debug_stderr` | `Any` | `sys.stderr` | Deprecated — File-like object for debug output. Use `stderr` callback instead |
| `stderr` | `Callable[[str], None] \| None` | `None` | Callback function for stderr output from CLI |
| `can_use_tool` | `CanUseTool \| None` | `None` | Tool permission callback, invoked only when the permission flow falls through to a prompt. Not invoked for calls auto-approved by `allowed_tools`, allow rules, or `permission_mode`. `AskUserQuestion`, connector tools your organization set to ask, and MCP tools marked `requiresUserInteraction` reach it even if you've allowed them; in `dontAsk` mode these are denied instead. See `CanUseTool` for details |
| `hooks` | `dict[HookEvent, list[HookMatcher]] \| None` | `None` | Hook configurations for intercepting events |
| `user` | `str \| None` | `None` | User identifier |
| `include_partial_messages` | `bool` | `False` | Include partial message streaming events. When enabled, `StreamEvent` messages are yielded |
| `include_hook_events` | `bool` | `False` | Include hook lifecycle events in the message stream as `HookEventMessage` objects |
| `fork_session` | `bool` | `False` | When resuming with `resume`, fork to a new session ID instead of continuing the original session |
| `resume_session_at` | `str \| None` | `None` | When resuming, load the conversation only up to and including the message with this UUID. Use with `resume`, and usually `fork_session`, to branch from an earlier point |
| `resume_drops_turn` | `str \| None` | `None` | UUID of the user prompt whose turn a `resume_session_at` truncation discards. When set, the CLI refuses the resume if the discarded range holds entries not attributable to that turn. Requires Claude Code v2.1.223 or later; the bundled CLI satisfies this |
| `agents` | `dict[str, AgentDefinition] \| None` | `None` | Programmatically defined subagents |
| `plugins` | `list[SdkPluginConfig]` | `[]` | Load custom plugins from local paths. See Plugins for details |
| `sandbox` | `SandboxSettings \| None` | `None` | Configure sandbox behavior programmatically. See Sandbox settings for details |
| `setting_sources` | `list[SettingSource] \| None` | `None` (CLI defaults: all sources) | Control which filesystem settings to load. Pass `[]` to disable user, project, and local settings. Endpoint-managed policy loads regardless; server-managed settings are fetched when the session authenticates with an organization credential on an eligible configuration. See Use Claude Code features |
| `skills` | `list[str] \| Literal["all"] \| None` | `None` | Skills available to the session. Pass `"all"` to enable every discovered skill, or a list of skill names. Pass exact names only. The SDK rejects malformed and wildcard-form names with a `ValueError` before starting the Claude Code process. When set, the SDK adds the `Skill` tool to `allowed_tools` automatically. If you also pass `tools`, include `"Skill"` in that list. See Skills |
| `max_thinking_tokens` | `int \| None` | `None` | Deprecated — Maximum tokens for thinking blocks. Use `thinking` instead |
| `thinking` | `ThinkingConfig \| None` | `None` | Controls extended thinking behavior. Takes precedence over `max_thinking_tokens` |
| `effort` | `EffortLevel \| None` | `None` | Effort level for thinking depth. See adjust the effort level |
| `session_store` | `SessionStore \| None` | `None` | Mirror session transcripts to an external backend so another host can resume them. See Persist sessions to external storage |
| `session_store_flush` | `Literal["batched", "eager"]` | `"batched"` | When to flush mirrored transcript entries to `session_store`. `"batched"` flushes once per turn or when the buffer fills; `"eager"` triggers a background flush after every frame. Ignored when `session_store` is `None` |
| `load_timeout_ms` | `int` | `60000` | Per-call timeout for `session_store.load()` and `list_subkeys()` during resume materialization, in milliseconds |
| `task_budget` | `TaskBudget \| None` | `None` | API-side token budget. Sent as `output_config.task_budget` with the `task-budgets-2026-03-13` beta header. Pass `{"total": <int>}` |

## Handle slow or stalled API responses

The CLI subprocess reads several environment variables that control API
timeouts and stall detection. Pass them through `ClaudeAgentOptions.env`:

```python
from claude_agent_sdk import ClaudeAgentOptions

options = ClaudeAgentOptions(
    env={
        "API_TIMEOUT_MS": "120000",
        "CLAUDE_CODE_MAX_RETRIES": "2",
        "CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS": "120000",
    },
)
```

- **`API_TIMEOUT_MS`** — per-request timeout on the Anthropic client, in
  milliseconds. Default `600000`. Applies to the main loop and all
  subagents.
- **`CLAUDE_CODE_MAX_RETRIES`** — maximum API retries. Default `10`, capped
  at `15`. Each retry gets its own `API_TIMEOUT_MS` window, so worst-case
  wall time is roughly `API_TIMEOUT_MS × (CLAUDE_CODE_MAX_RETRIES + 1)` plus
  backoff. For unattended runs that need to wait through longer outages, set
  `CLAUDE_CODE_RETRY_WATCHDOG=1`: it retries capacity errors indefinitely,
  and as of Claude Code v2.1.199 raises the default for other transient
  errors to `300` and removes the cap on this variable.
- **`CLAUDE_ASYNC_AGENT_STALL_TIMEOUT_MS`** — stall watchdog for subagents
  launched with `run_in_background`. Default `600000`. Resets on each stream
  event; on stall it aborts the subagent, marks the task failed, and
  surfaces the error to the parent with any partial result. Does not apply
  to synchronous subagents.
- **`CLAUDE_ENABLE_STREAM_WATCHDOG`** with **`CLAUDE_STREAM_IDLE_TIMEOUT_MS`**
  — aborts the request when headers have arrived but the response body
  stops streaming. The watchdog is on by default for all providers; set
  `CLAUDE_ENABLE_STREAM_WATCHDOG=0` to disable it.
  `CLAUDE_STREAM_IDLE_TIMEOUT_MS` defaults to `300000` and is clamped to
  that minimum. After the abort, Automatic retries covers what Claude Code
  does, based on how far the response had progressed.

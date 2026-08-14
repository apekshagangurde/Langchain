# Plan: Debug-and-PR Agent

Goal: an agent that finds/fixes a bug in a local repo, verifies with tests,
and opens a PR via the GitHub MCP server.

## Phase 0 — Environment setup
- [ ] `uv add python-dotenv claude-agent-sdk` (if not already installed)
- [ ] Docker Desktop running (GitHub MCP server runs via `docker run`)
- [ ] Fill `.env`: `ANTHROPIC_API_KEY`, `GITHUB_PERSONAL_ACCESS_TOKEN` (repo + pull_request scopes), `REPO_PATH`, `BUG_DESCRIPTION`
- [ ] Confirm `.env` is gitignored

## Phase 1 — Bare agent loop (no MCP, no bug-fixing yet)
- [ ] Wire up `query()` + `ClaudeAgentOptions` with just `allowed_tools=["Read"]`
- [ ] Print `AssistantMessage` text and `ResultMessage` to confirm the loop runs end to end
- [ ] Sanity check: point it at a repo and ask it to summarize a file

## Phase 2 — Local debugging capability
- [ ] Add `Grep`, `Glob`, `Edit`, `Bash` to `allowed_tools`
- [ ] Write the system prompt for steps: reproduce → locate → fix (no test/PR steps yet)
- [ ] Test against `test-repos/` with a known bug — confirm it finds and edits the right file

## Phase 3 — Test verification gate
- [ ] Extend system prompt: after fixing, run the test suite with `Bash`
- [ ] Require it to show passing test output before considering the fix "done"
- [ ] Test against a repo with a real test suite — confirm it won't stop until tests pass

## Phase 4 — GitHub MCP server wiring (read-only first)
- [ ] Add `github_server` stdio config (`docker run ... ghcr.io/github/github-mcp-server`)
- [ ] Register it in `mcp_servers`, but only allow `get_*`/`list_*`/`search_*` tools
- [ ] Confirm the agent can read repo/issue info through MCP before trusting it with writes

## Phase 5 — Permission gating for destructive actions
- [ ] Implement `can_use_tool` callback: auto-allow safe prefixes, gate `create/push/merge/delete/close/update`
- [ ] Add the y/n terminal confirmation path
- [ ] Add the non-interactive (`sys.stdin.isatty()` false) deny-by-default path so automated runs never silently push/PR

## Phase 6 — Full ship workflow
- [ ] Extend system prompt: branch → commit → push → open PR with description (what broke, what changed, how verified)
- [ ] Switch prompt to `prompt_stream()` (streaming input mode) since `can_use_tool` requires it
- [ ] Set `max_turns` high enough for the full workflow

## Phase 7 — End-to-end verification
- [ ] Run against a `test-repos/` sandbox repo with a seeded bug
- [ ] Confirm: bug found → fixed → tests pass → branch created → PR opened
- [ ] Confirm PR URL is printed from the final `ResultMessage`
- [ ] Confirm destructive-action prompts actually block until approved (and deny cleanly when non-interactive)

## Phase 8 — Hardening (stretch)
- [ ] Handle `ResultMessage.subtype != "success"` (report what stopped it, don't crash)
- [ ] Guard against missing/invalid env vars with clear error messages
- [ ] Optional: dry-run mode that stops right before the destructive GitHub calls

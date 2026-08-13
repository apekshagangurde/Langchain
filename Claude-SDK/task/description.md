# Task

An agent that debugs code and raises a PR using the GitHub MCP server.

## Learning Plan — what to learn before implementing

1. **Claude Agent SDK fundamentals** (done in `basic/`)
   - `query()`, `ClaudeAgentOptions`
   - Message types: `AssistantMessage`, `ResultMessage`, tool-use blocks
   - The agent loop (turns, when a run finishes)

2. **MCP (Model Context Protocol) basics**
   - What an MCP server is and how it exposes tools to the agent
   - How to register an MCP server in `ClaudeAgentOptions` (`mcp_servers` config)
   - Difference between local/stdio MCP servers and remote/URL-based ones

3. **GitHub MCP server**
   - Official GitHub MCP server: what tools it exposes (create branch, commit, push, open PR, read issues, etc.)
   - How to run/connect it (command, or hosted URL)
   - Authenticating it with a GitHub Personal Access Token (repo + pull-request scopes)

4. **Tool permissions & safety**
   - `allowed_tools` / `permission_mode` in `ClaudeAgentOptions`
   - Which tools the agent needs enabled: file read/edit, Bash (to run tests), and the GitHub MCP tools
   - Gating destructive/irreversible actions (pushing, opening a PR) behind explicit approval

5. **Debugging workflow design**
   - How to point the agent at a repo/codebase
   - Prompting it to: reproduce the bug → locate the cause → propose/apply a fix → run tests to verify
   - Deciding what "done" looks like (tests pass) before it's allowed to commit

6. **Git + PR workflow**
   - Creating a new branch, committing the fix, pushing
   - Opening a PR with a clear title/description (what was broken, what changed, how it was verified)

7. **Environment & config**
   - `.env` variables needed: `ANTHROPIC_API_KEY`, `GITHUB_PERSONAL_ACCESS_TOKEN` (or similar)
   - Keeping secrets out of git (already have `.env` gitignored)

8. **Putting it together**
   - System prompt that encodes the debug → fix → verify → PR workflow
   - Reading the final `ResultMessage` to confirm success/failure and surface the PR link

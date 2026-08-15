# Web Search Options for the Claude Agent SDK

Reference notes only — no code here. Two ways to give an agent web search:
a built-in tool (zero setup) or an MCP server (more control, needs its own API key).

## 1. Built-in tools (simplest — just add to `allowed_tools`)

The Claude Agent SDK ships the same built-in tools as Claude Code, including:

- **`WebSearch`** — runs a web search and returns results with citations. No
  extra config, no API key of your own — it's covered by your Claude
  subscription/API usage.
- **`WebFetch`** — fetches a specific URL and returns its content (e.g. as
  markdown). Good for "read this page" once you already have a link (from a
  search result, or given directly by the user).

Add either (or both) to `ClaudeAgentOptions(allowed_tools=[...])` and Claude
decides when to call them — no MCP server, no separate credentials.

**When this is enough:** general-purpose search/lookup where you don't need
control over the search provider, ranking, or result format.

## 2. MCP servers (more control, needs your own API key)

Use an MCP server instead when you want a specific search provider, a
paid/higher-quality API, or search results shaped differently than the
built-in tool provides (e.g. semantic search, scraped full-page content,
domain-restricted search).

| MCP server | What it's for | Needs |
|---|---|---|
| **Brave Search** | General web search via Brave's Search API | Brave Search API key |
| **Tavily** | Search API built specifically for LLM agents (concise, structured results) | Tavily API key |
| **Exa** | Neural/semantic search — finds pages by meaning, not just keywords | Exa API key |
| **Perplexity (Sonar/Ask)** | Search-augmented Q&A — returns an answer with sources, not just links | Perplexity API key |
| **Firecrawl** | Search + full-page scraping/crawling (turns a page into clean markdown) | Firecrawl API key |
| **SerpAPI** | Structured Google (or other engine) search results | SerpAPI key |
| **DuckDuckGo** | Community MCP server, no API key required, but rate-limited | None (or self-hosted) |
| **Fetch** (reference server) | Not search itself — fetches a URL and converts to markdown; often paired with one of the above for "search, then read the top result" | None |

Most of these are listed in the official Model Context Protocol servers
directory (`github.com/modelcontextprotocol/servers`) or as standalone MCP
packages on npm/PyPI from each provider — check there for the current
package name and exact setup steps before wiring one in, since these change
over time.

## How to wire an MCP one in (once you pick one)

Same pattern as `task/agent.py`'s GitHub MCP server or `task/agent2.py`'s
HTTP variant: add an entry to `ClaudeAgentOptions(mcp_servers={...})` —
`{"type": "stdio", "command": ..., "args": ..., "env": {...}}` for a
locally-run server (e.g. via `npx`), or `{"type": "http", "url": ...,
"headers": {...}}` for a hosted one — then add its tool name(s) (e.g.
`mcp__brave-search__brave_web_search`) to `allowed_tools`.

# TripMate — Build Plan (part 2)

> Working plan (committed). Tick boxes as steps are done.

Part 1 (the basics) is done. Part 2 is about learning the more advanced
deepagents features, one small step at a time.

Per step: write the code → add a one-line entry to `CHANGELOG.md` → tick the box here.
Status: `[ ]` todo · `[x]` done · **needs: X** = do X first.

Installed: `deepagents 0.7.13`.

---

## Done (part 1)

- [x] Tools: `get_weather`, `search_places`, `book_hotel` (fake)
- [x] Todo-list planning, `itinerary-writer` + `budget-planner` skills
- [x] Memory: checkpointer (chat), store `/memories/` (long-term), `memory/AGENTS.md`
- [x] Subagents: weather, places, budget, critic (critic in **fork** mode)
- [x] Human-in-the-loop: approve / reject booking in Streamlit
- [x] Streamlit UI, LangGraph Studio, LangSmith tracing

---

## 1. Async subagents ⭐ (next)

Normal subagents **block**: the main agent waits until the subagent finishes.
Async subagents run **in the background on a LangGraph server**. The main agent
gets a task id at once, keeps chatting, and checks back later.
It gets 5 tools: `start_async_task`, `check_async_task`, `update_async_task`,
`cancel_async_task`, `list_async_tasks`.

Docs: https://docs.langchain.com/oss/python/deepagents/async-subagents

- [ ] **1.1 `train_finder.py` — a separate small agent**
  Its own `create_deep_agent` (or `create_agent`) with `search_places`-style
  web search for trains/buses from home city → destination.
  Export `train_finder = ...` at module level.

- [ ] **1.2 Register it in `langgraph.json`** — needs: 1.1
  Add a second graph: `"train_finder": "./train_finder.py:train_finder"`.
  *Done when:* Studio shows two graphs (`agent`, `train_finder`).

- [ ] **1.3 `AsyncSubAgent` spec** — needs: 1.2
  In `subagents.py`:
  `{"name": "train-finder", "description": ..., "graph_id": "train_finder", "url": "http://127.0.0.1:2024"}`
  and add it to `SUBAGENTS`.
  (`url` is needed because Streamlit uses sync `invoke`; `langgraph dev` must be running.)

- [ ] **1.4 `## Background jobs` in `prompts.py`** — needs: 1.3
  Start `train-finder` early, keep planning, check it before writing the final
  plan; don't poll in a loop.

- [ ] **1.5 Try it** — needs: 1.4
  In Studio: ask for a trip → see `start_async_task` → ask "any trains yet?"
  → see `check_async_task`. Look at both runs in LangSmith.

- [ ] **1.6 Sidebar: background tasks** — needs: 1.3
  Show the async tasks (from state) with their status in the Streamlit sidebar.

## 2. Live streaming (see subagents while they work)

- [ ] **2.1 `agent.stream(..., subgraphs=True)` in `app.py`**
  Show each tool call / subagent step as it happens instead of a spinner.
  *Done when:* you see "weather-agent → get_weather(...)" appear live.

## 3. Agent shape (stash: "TripMate E1–E5 agent shape (WIP)")

Already written — `git stash apply`, then go through it one piece at a time.

- [ ] **3.1 Structured output** — `TripSummary` + `response_format`
- [ ] **3.2 Runtime context** — `TripContext(user_id, budget)`, per-user `/memories/`
- [ ] **3.3 Custom state** — `chosen_city` via a `Command(update=...)` tool
- [ ] **3.4 Permissions** — `FilesystemPermission`: read-only `/skills/`, `/memory/`
- [ ] **3.5 Summarization / big-result eviction** — read & note in README
- [ ] **3.6 TripSummary card in Streamlit** — needs: 3.1

## 4. Self-check with `RubricMiddleware` (new in 0.7)

The agent grades its own answer against a rubric and retries until it passes.
Compare it with the `critic-agent` you already have.

- [ ] **4.1 Add `RubricMiddleware(model=...)`** to `middleware=[...]`
- [ ] **4.2 Pass a rubric on invoke** — `{"messages": [...], "rubric": "- each day has a time plan\n- total within budget\n- ..."}`
- [ ] **4.3 Compare** — critic (subagent) vs rubric (middleware): which catches more? Note it in README.

## 5. Evals with LangSmith

- [ ] **5.1 Dataset** — 5 test prompts (normal, over budget, unknown city, booking, vegetarian)
- [ ] **5.2 Evaluator** — LLM-as-judge: fits budget? uses only real places? asks for home city?
- [ ] **5.3 Run the eval** and look at the scores in LangSmith

## 6. MCP tools (optional)

- [ ] **6.1** Load one public MCP server via `langchain-mcp-adapters` and give it to `places-agent`.

## 7. Learn from other projects (read, don't copy)

For each: read the code, write 3 things you learned in `plan/notes.md`.

- [ ] **7.1 `deep_research`** (langchain-ai/deepagents → `examples/deep_research`)
  — research subagent + `think` tool + citations.
- [ ] **7.2 `content-builder-agent`** (`examples/content-builder-agent`)
  — AGENTS.md memory + several skills, very close to TripMate's setup.
- [ ] **7.3 `async-subagent-server`** (`examples/async-subagent-server`)
  — read before step 1. ⚠ Older API (`async_subagents=`); TripMate uses `subagents=`.
- [ ] **7.4 `deep-agents-ui`** (langchain-ai/deep-agents-ui) — a ready UI for
  any deep agent; try it against `langgraph dev`.

## 8. Extras (later)

- [ ] **8.1 `patterns.py`** — one tiny function per pattern (chaining, routing,
  parallel, orchestrator-workers, evaluator-optimizer).
- [ ] **8.2 Switch to Claude** — `TRIPMATE_MODEL=anthropic:claude-...` and compare to Groq.
- [ ] **8.3 Studio screenshot in README.**

---

## Links

- [Deep Agents docs: Async subagents](https://docs.langchain.com/oss/python/deepagents/async-subagents)
- [LangChain blog: Running subagents in the background](https://www.langchain.com/blog/running-subagents-in-the-background)
- [Testing LangChain's async subagents (third-party write-up)](https://levelup.gitconnected.com/your-agent-can-talk-while-it-works-testing-langchains-async-subagents-474ab1c85882)
- [deepagents examples overview (DeepWiki)](https://deepwiki.com/langchain-ai/deepagents/8-examples-and-use-cases)
- [Deep Agents docs: Content builder](https://docs.langchain.com/oss/python/deepagents/content-builder)
- [async-subagent-server example (mirror)](https://gitcode.com/xiaoyifan/deepagents/tree/main/examples/async-subagent-server)

---

## Suggested order

7.3 → 1.1 → 1.2 → 1.3 → 1.4 → 1.5 → 2.1 → 1.6 → 4.1–4.3 → 3.x → 5.x → 7.1, 7.2, 7.4 → 6 → 8

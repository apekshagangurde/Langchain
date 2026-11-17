# Project 1 — "TripMate": a Deep Agent Weekend-Trip Planner

A small, end-to-end project that uses **every deep agent concept** from the notes
in `../1_*.py` … `../9_*.py` in one place.

---

## Problem statement

> A user says: *"Plan a 2-day weekend trip from Pune for me. My budget is ₹8,000."*
>
> **TripMate** must:
> 1. **Plan** the work as a todo list (pick city → check weather → find places → check budget → write itinerary).
> 2. **Delegate** research to specialist **subagents** (weather, places, budget) so the main agent's context stays clean.
> 3. Follow **skills** (house rules for *how* to write an itinerary and *how* to check a budget), loaded only when needed.
> 4. **Remember** the user:
>    - inside one chat (short-term memory),
>    - across chats, e.g. "I am vegetarian" (long-term memory in `/memories/`),
>    - always-on profile facts in `AGENTS.md`.
> 5. **Write files** — save the final plan to `/trip_plan.md`.
> 6. Ask a **human for approval** before booking a hotel (human-in-the-loop).
>
> Finally, the same problem is solved again using each of the **six common
> orchestration patterns**, so you can compare them side by side.

All tools use **fake, hard-coded data** (no web calls), so the focus stays on
the agent architecture.

---

## Concept map — where each concept lives

| # | Deep agent concept            | Where in this project                                              |
|---|-------------------------------|--------------------------------------------------------------------|
| 1 | Planning (todo list)          | `TodoListMiddleware` in `agent.py` → `write_todos` tool            |
| 2 | File system / backends        | `CompositeBackend` in `agent.py` (State + Filesystem + Store)       |
| 3 | Subagents (context isolation) | `subagents.py` → weather / places / budget / critic, via `task`     |
| 4 | Skills (progressive disclosure)| `skills/itinerary-writer/SKILL.md`, `skills/budget-planner/SKILL.md` |
| 5 | Short-term memory             | `checkpointer=InMemorySaver()` + `thread_id`                       |
| 6 | Long-term memory              | `/memories/` routed to `StoreBackend`                              |
| 7 | AGENTS.md memory              | `memory/AGENTS.md` → `memory=["/memory/AGENTS.md"]`                |
| 8 | Human-in-the-loop             | `interrupt_on={"book_hotel": True}`                                |
| 9 | Context engineering           | detailed system prompt + subagents return short summaries only     |
| 10| Six orchestration patterns    | `patterns.py`                                                      |
| 11| Permissions                   | `permissions=[...]` — skills/ and memory/AGENTS.md read-only except for allowed edits; deny writes outside `/trip_plan.md`, `/notes/`, `/memories/` |
| 12| Structured output             | `response_format=TripSummary` (city, total_cost, fits_budget, critic_verdict) on the main agent; `response_format` on `budget-agent` so it returns JSON |
| 13| Runtime context               | `context_schema=TripContext` (user_id, budget) passed with `invoke(..., context=...)`; subagents inherit it; `user_id` scopes the `/memories/` namespace |
| 14| Custom state                  | `state_schema` subclassing `DeepAgentState` with e.g. `chosen_city`, shown in the UI |
| 15| Summarization & offloading    | built-in `SummarizationMiddleware` (long chats) + large tool results offloaded to files |
| 16| Event streaming               | `agent.stream(...)` / `stream_events` with `subgraphs=True` → live steps in Streamlit, incl. subagent progress |
| 17| Async subagents               | `AsyncSubAgent` "train-finder" that runs in the background (launch / check / cancel) |
| 18| Fork-mode subagent            | `critic-agent` with `mode="fork"` so it sees the whole conversation (experimental) |
| 19| Observability (LangSmith)     | `LANGSMITH_TRACING=true`; filter runs by `lc_agent_name` per subagent |
| 20| MCP tools (optional)          | load a public MCP server (e.g. maps) with `langchain-mcp-adapters` |

### ✅ Must use in this project (added after reviewing the Deep Agents docs)

These concepts come from the official docs (overview, subagents, context
engineering) and **have to be built into TripMate**, on top of rows 1–10.

**Core — required:**

| #  | Concept                      | How TripMate uses it                                                                                     |
|----|------------------------------|----------------------------------------------------------------------------------------------------------|
| 11 | Permissions                  | Agent can read but not overwrite `skills/` and `AGENTS.md`; may only write to `/trip_plan.md`, `/notes/` and `/memories/` |
| 12 | Structured output            | Agent returns fixed fields (city, total cost, fits budget, critic verdict) instead of free text — makes the Streamlit UI easier |
| 13 | Runtime context              | Pass `user_id` and budget into each run; subagents receive them too, and `user_id` keeps each user's `/memories/` separate |
| 14 | Custom state                 | Keep values like `chosen_city` in the agent's state so the UI can show them                              |
| 15 | Summarization and offloading | Built in: long chats are summarized and very large tool results are saved to files                       |
| 16 | Event streaming              | Show live steps, including subagent progress, in the Streamlit UI                                        |

**Extras — also to be used:**

| #  | Concept            | How TripMate uses it                                                    |
|----|--------------------|-------------------------------------------------------------------------|
| 17 | Async subagents    | A background "train-finder" job you can start, check on or cancel       |
| 18 | Fork-mode subagent | The critic sees the whole conversation (experimental in the docs)       |
| 19 | LangSmith tracing  | View runs and filter them by subagent                                   |
| 20 | MCP tools          | Optional: load tools from an MCP server                                 |

> Note: the "six orchestration patterns" above follow Anthropic's
> *Building effective agents* list; they are not listed on the Deep Agents
> overview, subagents or context-engineering pages.

### From the docs but intentionally *not* used

| Concept                      | Why skipped                                                        |
|------------------------------|--------------------------------------------------------------------|
| Sandboxes / `execute` tool   | TripMate doesn't need to run shell code                            |
| Interpreters / dynamic subagents | beta; overkill for a learning project                           |
| Multimodal                   | no images/audio in a trip planner (could add "upload a photo of a place" later) |
| Harness profiles             | only needed to tweak per-model defaults                            |
| Prompt caching middleware    | no-op for Groq models                                              |
| Managed Deep Agents / Agent Server / ACP | deployment topics, not agent design                     |

---

## The six common orchestration patterns

(Following Anthropic's *"Building effective agents"* taxonomy — 5 workflows + 1 agent.)

| # | Pattern               | Idea                                                   | TripMate example in `patterns.py`                       |
|---|-----------------------|--------------------------------------------------------|---------------------------------------------------------|
| 1 | Prompt chaining       | Fixed steps; output of step N is input of step N+1     | pick city → list activities → write itinerary           |
| 2 | Routing               | Classify the request, send it to a specialist           | "weather?" / "budget?" / "places?" → right handler     |
| 3 | Parallelization       | Run independent sub-tasks at the same time, then merge  | weather + places + budget for a city in one `batch`     |
| 4 | Orchestrator–workers  | A lead LLM decides the sub-tasks and delegates them     | the deep agent + `task` tool + subagents               |
| 5 | Evaluator–optimizer   | Generator writes, evaluator critiques, loop until good  | draft itinerary ↔ critic, max 2 rounds                  |
| 6 | Autonomous agent      | LLM loops with tools on its own until done              | `create_deep_agent` with tools, no fixed steps         |

Deep agents are mostly **#4 + #6** combined: an autonomous loop that plans,
and an orchestrator that hands work to subagents.

---

## Planned folder structure (to be built step by step)

```
project1/
├── README.md                ← you are here
├── prompts.py               ← step 1: TripMate system prompt (all concepts)
├── tools.py                 ← fake tools: weather, places, costs, book_hotel
├── subagents.py             ← subagent specs (weather, places, budget, critic)
├── agent.py                 ← the main TripMate deep agent (all concepts)
├── patterns.py              ← the six orchestration patterns
├── app.py                   ← Streamlit UI for TripMate
├── skills/
│   ├── itinerary-writer/SKILL.md
│   └── budget-planner/SKILL.md
└── memory/
    └── AGENTS.md            ← always-loaded user profile
```

---

## How to run

```bash
# from the repo root, with the venv active and GROQ_API_KEY in .env
cd langchain/Deep_Agents/project1
python agent.py      # full deep agent demo (memory, subagents, skills, HITL)
python patterns.py   # the six orchestration patterns one by one
streamlit run app.py # chat UI in the browser (http://localhost:8501)
```

Model: `ChatGroq(model="openai/gpt-oss-120b")` with a rate limiter to stay
under Groq's free-tier tokens/minute limit. Runs are slow on purpose.

---

## Streamlit UI (`app.py`)

A simple browser UI so you can *see* every deep agent concept while it runs.

```
┌──────────────── Sidebar ────────────────┐ ┌────────────────── Main area ──────────────────┐
│ 🧳 TripMate                              │ │ 💬 Chat                                        │
│ Thread id: [ thread-1   ] [New chat]     │ │   user: Plan a 2-day trip, budget ₹8,000       │
│ Budget (₹): [ 8000 ]                     │ │   TripMate: Lonavala fits your budget ...      │
│                                          │ │                                                │
│ 📋 Todo list        (write_todos)        │ │ ▸ Agent steps (expander)                       │
│   ✅ Check weather                        │ │     task → weather-agent  : "Lonavala 24°C…"   │
│   🔄 Check budget                         │ │     task → budget-agent   : "₹5,700 fits"      │
│   ⏳ Write itinerary                      │ │     read_file /skills/itinerary-writer/SKILL.md│
│                                          │ │                                                │
│ 📁 Files            (backend)            │ │ ⚠️ Approval needed: book_hotel(Lonavala, 1)     │
│   /trip_plan.md  [view]                  │ │     [ Approve ]   [ Reject ]                   │
│                                          │ │                                                │
│ 🧠 Long-term memory (/memories/)         │ │ 📄 /trip_plan.md (rendered markdown)            │
│ 👤 AGENTS.md        (profile)            │ │                                                │
└──────────────────────────────────────────┘ └────────────────────────────────────────────────┘
```

| UI part                    | Deep agent concept it shows                     | How                                                       |
|----------------------------|-------------------------------------------------|-----------------------------------------------------------|
| Chat box + history         | Short-term memory                               | same `thread_id` + checkpointer across messages           |
| "New chat" button          | Long-term memory                                | new `thread_id`; `/memories/` is still remembered          |
| Todo list panel            | Planning                                        | read `state["todos"]` after each run                       |
| Agent steps expander       | Subagents, skills, tool calls                   | `agent.stream(..., stream_mode="updates")`                |
| Files panel                | File system / backends                          | read `state["files"]` (e.g. `/trip_plan.md`)              |
| Memory + AGENTS.md panels  | Long-term + AGENTS.md memory                    | `store.search(("memories",))` and `memory/AGENTS.md`       |
| Approve / Reject buttons   | Human-in-the-loop                               | on `__interrupt__`, resume with `Command(resume=...)`     |
| Pattern selector (optional)| Six orchestration patterns                      | dropdown that runs the matching function in `patterns.py` |

Notes:
- Keep the agent, store and checkpointer in `st.session_state` (or
  `@st.cache_resource`) so they are not re-created on every Streamlit rerun.
- Install with `pip install streamlit`.

---

## Ideas to extend

- Swap `InMemoryStore` for `PostgresStore` so long-term memory survives restarts.
- Add an `AsyncSubAgent` for a slow "find cheapest train" job.
- Add a third skill, e.g. `packing-list`.
- Replace fake tools with real APIs (OpenWeather, Google Places).

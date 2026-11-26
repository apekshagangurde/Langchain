# TripMate → Personal Travel Assistant — Plan (part 3)

> Roadmap for the next phase (part 3). Part 2 is `PLAN.md`.

Goal: turn TripMate from "a chat that plans a trip" into **an assistant that knows each user, remembers their trips, works in the background, acts through real apps (calendar, email, expenses), and reaches out first** when something matters.

Per step: write the code → one-line `CHANGELOG.md` entry → tick the box here.
Status: `[ ]` todo · `[x]` done · **needs: X** = do X first.

Installed now: `deepagents 0.7.13`, `langchain 1.4`, `langgraph 1.2`, `langgraph-sdk 0.4` (has `auth`, `crons`), `langchain-mcp-adapters 0.3`.
Not installed yet: `langmem`, a Postgres checkpointer/store, an embeddings model (Groq has none → use HuggingFace embeddings).

---

## Big picture

```
            channels: Streamlit · Telegram/WhatsApp · Email · Slack
                               │  (each message carries a user_id)
                               ▼
   ┌──────────────── LangGraph server (langgraph dev → deployment) ────────────────┐
   │  auth  → user_id                                                              │
   │  tripmate (main agent) ── subagents (weather, places, budget, critic)          │
   │        │                └─ async subagents (train-finder, memory-curator)      │
   │        ├─ tools: calendar (MCP) · email · expenses   (HITL before any send)    │
   │        └─ /memories/<user>/…  ←→  store (+ embedding index)                    │
   │  checkpointer (Postgres) · task queue + workers · crons (heartbeat, reminders) │
   └────────────────────────────────────────────────────────────────────────────────┘
```

Build order: **A → B → C → D → E → F → G → H** (each section mostly needs the one before).

---

## A. Identity: who is talking

Everything later (memory, calendar, email) is per user, so this comes first.

- [ ] **A1. Apply the E-stash pieces we need** — `git stash apply` "TripMate E1–E5"; keep `TripContext(user_id, …)` and `context_schema`.
  *Done when:* `agent.invoke(..., context=TripContext(user_id="u1"))` works.
- [ ] **A2. Stable user id in Streamlit** — a simple sign-in (name + password from a local test users file, or Streamlit's built-in OIDC login). Save `user_id` in `st.session_state`; pass it as `context` on every call.
  *Done when:* two users in two browsers get different ids, and the same user gets the same id after refresh.
- [ ] **A3. LangGraph server auth** — `auth.py` with `langgraph_sdk.Auth` (`@auth.authenticate` returns the user identity); register it under `"auth"` in `langgraph.json`. Studio / API calls then carry the user automatically.
  *Done when:* a request without a valid token is rejected; a valid one shows the user id in the run.
- [ ] **A4. Threads belong to users** — `@auth.on` handler that adds `owner = user_id` metadata to threads and filters by it.
  *Done when:* user B can't open user A's chat thread.

## B. Memory layout: what we remember, per user

Move `/memories/` from one shared namespace to **one namespace per user**: `("tripmate", user_id, "memories")` (the `StoreBackend` namespace lambda reads `runtime.context.user_id`). — **needs: A1**

| File (per user) | What goes in | Who writes it |
|---|---|---|
| `/memories/profile.md` | home city, diet, budget habits, likes/dislikes | agent, when the user states a lasting preference |
| `/memories/trips/<trip-id>.md` | one ongoing/upcoming trip: dates, city, bookings, status | agent, during planning |
| `/memories/facts.md` | long-term facts ("travels with 2 kids", "has a car") | memory-curator (C) |
| `/memories/decisions.md` | important decisions + why ("chose Lonavala over Mahabaleshwar: rain") | memory-curator (C) |
| `/memories/daily/YYYY-MM-DD.md` | short log of today's chats and actions | agent appends one line per finished task |
| `/memories/recent.md` | last ~10 activities, newest first (quick context) | memory-curator (C) |

- [ ] **B1. Per-user namespace** — change the `/memories/` route; update the Memory section of `prompts.py` to the table above.
  *Done when:* user A's `profile.md` is not visible to user B.
- [ ] **B2. Trip files** — prompt rule: every new trip gets `/memories/trips/<city>-<date>.md`; update its status (`planning → booked → done`).
- [ ] **B3. Daily log** — prompt rule: after finishing a task, append one line to today's daily file.
- [ ] **B4. Read on start** — prompt rule: at the start of a request, read `profile.md`, `recent.md` and any trip still `planning`/`booked`.
  *Done when:* a new chat says "your Lonavala trip on the 28th is still unbooked" without being told.

## C. Background memory curator (not during the chat)

Writing memory while chatting slows replies and saves noise. Instead, a **separate background job** reviews conversations later and keeps only what's worth keeping. — **needs: B1**

- [ ] **C1. `memory_curator.py`** — a small deep agent: input = a finished thread's messages + current memory files; output = updates to `facts.md`, `decisions.md`, `recent.md` (merge, de-duplicate, drop one-off details).
- [ ] **C2. Register as a second graph** in `langgraph.json` (`"memory_curator": "./memory_curator.py:graph"`).
- [ ] **C3. Trigger it in the background** — after a chat goes quiet, start a background run (`client.runs.create(..., graph "memory_curator")`), or call it as an **async subagent** so the main agent never waits.
  *Alternative to study:* `langmem` (`create_memory_store_manager` + `ReflectionExecutor` delays processing until the chat is idle).
- [ ] **C4. Nightly review** — a cron (see G) runs the curator once a day over that day's `daily/` file.
  *Done when:* after chatting "I'm vegetarian, and we went with Lonavala because of rain", the next day `facts.md` and `decisions.md` contain one clean line each, and nothing was written during the chat itself.

## D. Memory retrieval with embeddings

Reading whole files works while memory is small. Later, search it by meaning. — **needs: B1**

- [ ] **D1. Embeddings model** — HuggingFace (e.g. a small sentence-transformers model) via `langchain-huggingface`; note the vector size (`dims`).
- [ ] **D2. Indexed store** — `InMemoryStore(index={"embed": embeddings, "dims": N})` in `app.py`; for the server, set `"store": {"index": {...}}` in `langgraph.json`.
- [ ] **D3. `search_memory(query)` tool** — `store.search(("tripmate", user_id, "memories"), query=..., limit=5)`; return short snippets with their file path.
- [ ] **D4. Prompt rule** — use `search_memory` for questions like "where did I go last monsoon?" instead of reading every file.
  *Done when:* "what did I decide about Mahabaleshwar?" finds the line in `decisions.md`.

## E. Acting in real apps: connectors, OAuth, MCP, skills

Every action that leaves the app (calendar event, email, expense message) goes through **human approval** (we already have `interrupt_on`). — **needs: A2**

- [ ] **E1. OAuth per user** — a "Connect Google" button in Streamlit; store each user's tokens **server-side, encrypted, keyed by user_id**. Never put tokens in agent state, memory files or prompts.
- [ ] **E2. Calendar via MCP** — load a Google Calendar MCP server with `langchain-mcp-adapters` (`MultiServerMCPClient`), passing the user's token. Give its tools to a new `calendar-agent` subagent.
  *Done when:* "add my Lonavala plan to my calendar" creates one event per itinerary block, at the right times.
- [ ] **E3. `share-plan` email** — Gmail send tool (API or MCP) with `interrupt_on`: the user sees recipient + subject + body and approves.
  *Done when:* the plan arrives in a friend's inbox only after Approve.
- [ ] **E4. Expense messages** — after a trip, a `split_expenses` tool computes who owes whom and **drafts** messages (email / Splitwise API via OAuth). Only messages; **no money is moved by the agent**.
- [ ] **E5. Skills for each workflow** — `skills/calendar-sync/`, `skills/share-plan/`, `skills/trip-expenses/`: when to use, required inputs, what to confirm, message templates.
- [ ] **E6. Prompt + safety rules** — never send without approval; never invent email addresses (ask or read from `profile.md` contacts); one action per approval.

## F. Execution environment: long, reliable tasks

Planning + booking + calendar + emails is a long task. It must survive restarts and failures. — **needs: A3**

- [ ] **F1. Durable checkpointer** — swap `InMemorySaver` for SQLite now (`langgraph-checkpoint-sqlite` is installed), Postgres later. Every step is saved, so a crash resumes from the last step.
  *Done when:* kill Streamlit mid-plan, restart, send "continue" → it picks up where it stopped.
- [ ] **F2. Task progress record** — keep using `write_todos`, plus a `status` block in the trip file: steps done, results so far (links, ids), steps left.
- [ ] **F3. Background runs + task queue** — long jobs (full trip planning, train search) run as background runs on the LangGraph server; its built-in queue and workers handle them (`--n-jobs-per-worker`). The UI shows status instead of blocking.
- [ ] **F4. Timeouts + retries** — `ToolRetryMiddleware` / `ModelRetryMiddleware` (installed in `langchain 1.4`) with backoff; `ModelFallbackMiddleware` (Groq → Claude) when the main model fails; `ToolCallLimitMiddleware` / `ModelCallLimitMiddleware` to stop runaway loops; a timeout on every HTTP call in `tools.py`.
- [ ] **F5. Idempotency** — every side-effect tool (`book_hotel`, send email, create event) takes an `idempotency_key` (e.g. `trip-id + action + date`); keep a per-user `done_actions` record and skip repeats. A retry must never send the email twice.
  *Done when:* forcing a retry after "send email" still produces exactly one email.
- [ ] **F6. Async subagents for long work** — `train-finder` (from PLAN.md section 1) and `memory-curator` as `AsyncSubAgent`s.

## G. Proactivity: the assistant reaches out first

— **needs: F1, E2/E3 for actions**

- [ ] **G1. Scheduled jobs (crons)** — `client.crons.create(...)` on the LangGraph server:
  - daily 8 AM: check each user's upcoming trips (weather change? unbooked hotel?);
  - nightly: run the memory curator (C4).
- [ ] **G2. Heartbeat** — a short periodic run that reads `trips/*` and decides "anything worth telling the user?"; if not, it does nothing (no message).
- [ ] **G3. Event triggers** — start a run when something happens: a calendar event changes, a booking confirmation email arrives, or a trip is 2 days away. (Webhook → `client.runs.create`.)
- [ ] **G4. Notification rules** — at most N messages a day, quiet hours, and only for things the user said they care about (stored in `profile.md`).
  *Done when:* 2 days before a trip, the user gets one message: "Rain expected Saturday in Lonavala; want me to swap Day 1 and Day 2?"

## H. Multi-channel: same assistant everywhere

— **needs: A2, B1**

- [ ] **H1. Channel → user mapping** — a table `(channel, channel_user_id) → user_id`, so the Telegram user and the Streamlit user are the same person with the same memory.
- [ ] **H2. Thread per channel conversation** — `thread_id = f"{user_id}:{channel}:{chat_id}"`; memory is shared, chat history is per channel.
- [ ] **H3. Telegram bot** (simplest first) — webhook → LangGraph run → reply. Approvals via inline Approve/Reject buttons (maps to our `resume()`).
- [ ] **H4. Email in/out** — reply to the assistant's email to continue the conversation.
- [ ] **H5. Proactive messages use the user's preferred channel** (stored in `profile.md`).

---

## Suggested order

A1 → A2 → B1 → B2 → B3 → B4 → F1 → C1 → C2 → C3 → D1–D4 → E1 → E2 → E3 → F2 → F4 → F5 → F3 → F6 → G1 → G2 → C4 → E4 → E5 → E6 → G3 → G4 → H1 → H2 → H3 → H4 → H5 → A3 → A4

(A3/A4 matter once TripMate runs on a shared server; locally, A2 is enough to start.)

## Watch out

- **Secrets:** OAuth tokens and API keys never go into prompts, memory files, state or a sandbox.
- **Approval on every outward action** (email, calendar, expense message); money is never moved by the agent.
- **Groq limits:** background jobs + crons multiply model calls. Rate-limit them and keep the curator on a cheap model.
- **Privacy:** per-user namespaces from B1 onward; a "forget me" command that deletes the user's namespace.

## Links

- [LangGraph: authentication & access control](https://docs.langchain.com/langsmith/auth)
- [LangGraph: cron jobs](https://docs.langchain.com/langsmith/cron-jobs)
- [LangGraph: semantic search in the store](https://docs.langchain.com/oss/python/langgraph/add-memory)
- [LangMem (background memory manager)](https://langchain-ai.github.io/langmem/)
- [LangChain MCP adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
- [Deep Agents docs: Async subagents](https://docs.langchain.com/oss/python/deepagents/async-subagents)

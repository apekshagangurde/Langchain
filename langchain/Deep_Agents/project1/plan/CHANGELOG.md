# TripMate — Changelog

Newest first. One entry per step / commit: what changed, which files, and why.

---

## 2026-11-17 — Step 6: Tavily place search

**Branch:** `deep-agents-project1` · **Status:** committed

- Added `search_places` (Tavily web search) to `tools.py`; removed `get_places`.
- Switched the agent in `agent.py` to `search_places`.
- Added a `search_places` rule to the prompt in `prompts.py`.
- Installed `langchain-tavily`; `TAVILY_API_KEY` goes in `project1/.env`.

## 2026-11-17 — Step 5: skills

**Branch:** `deep-agents-project1` · **Status:** committed

- Added `skills/itinerary-writer/SKILL.md`.
- Added a `CompositeBackend` and `skills=["/skills/"]` to the agent in `agent.py`.
- Added a `## Skills` section to the prompt in `prompts.py`; `## Output` now uses the skill's format.

## 2026-11-17 — Step 4: planning (todo list)

**Branch:** `deep-agents-project1` · **Status:** committed

- Added `TodoListMiddleware` to the agent in `agent.py`; it prints the final todo list.
- Added a `## Planning` section to the prompt in `prompts.py`.

## 2026-11-17 — Step 3: second tool

**Branch:** `deep-agents-project1` · **Status:** committed

- Added `get_places` to `tools.py`.
- Added `get_places` to the agent in `agent.py`.

## 2026-11-17 — Step 2: smallest working agent + first tool

**Branch:** `deep-agents-project1` · **Status:** committed

- Added `tools.py` with `get_weather`.
- Added `agent.py`: deep agent with Groq (`openai/gpt-oss-120b`) and `get_weather`.
- Added `project1/.env` (git-ignored) for API keys.

## 2026-11-17 — Step 1: system prompt + tracking folder

**Branch:** `deep-agents-project1` · **Status:** committed

- Added `prompts.py` with a **starter** `TRIPMATE_SYSTEM_PROMPT`: role, job,
  Rules and a plain Output section only.
- Added `plan/CHANGELOG.md` (this file) to track changes step by step.

## 2026-11-17 — Step 0: README

**Branch:** `deep-agents-project1` · **Commit:** `fa7e534`

- Added `README.md`: problem statement, concept map (rows 1–20), six
  orchestration patterns, planned folder structure, Streamlit UI design,
  "Must use in this project" section after reviewing the Deep Agents docs,
  and the list of concepts intentionally not used.

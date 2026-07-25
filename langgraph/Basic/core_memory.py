"""
========================================================
     How Different LLMs Store the GOAL in Core Memory
========================================================

------------------------------------------------------------
 WHAT IS "CORE MEMORY"?
------------------------------------------------------------

Core Memory:
  A small, always-visible block of memory that is kept
  INSIDE the model's context window at every single step.
  It is not searched or retrieved — it is just always there,
  like a sticky note pinned to the top of the conversation.

  The GOAL (what the agent is ultimately trying to achieve)
  is usually the most important thing kept in core memory,
  because if the agent forgets the goal, it starts drifting
  and doing random or irrelevant actions.

  Think of it like a whiteboard header in an office that says
  "PROJECT GOAL: Launch product by Friday" — everyone glances
  at it before doing any task so they don't lose focus.

------------------------------------------------------------
 WHY THE GOAL CAN'T JUST LIVE IN NORMAL CHAT HISTORY
------------------------------------------------------------

- Chat history gets long and gets TRUNCATED or SUMMARIZED as
  the conversation grows — the original goal can get pushed
  out or watered down.

- In a long multi-step agent loop, the goal stated in message
  #1 is "far away" from the model's attention by message #50.

- Core memory solves this by re-inserting the goal into the
  prompt EVERY time, regardless of how long the conversation gets.

------------------------------------------------------------
 HOW DIFFERENT SYSTEMS STORE THE GOAL
------------------------------------------------------------

1. Plain LLM API calls (no framework)
   - No real core memory — the goal is just the first message.
   - Developer must manually re-inject it into the system
     prompt on every call, or it silently gets lost.

2. System Prompt Pinning (most common approach)
   - The goal is written once into the SYSTEM PROMPT.
   - Every single LLM call includes the system prompt, so the
     goal is technically always "in view" of the model.
   - Simple, but static — the goal text doesn't update as the
     agent learns more about the task.

3. MemGPT / Letta style "Core Memory Blocks"
   - Splits memory into labeled blocks, e.g.:
       <persona>  → who the agent is
       <human>    → who the user is
       <goal/task> → what must be achieved
   - These blocks are ALWAYS included in context (like core
     memory), but the agent itself can EDIT them using a tool
     call (e.g. "update_core_memory") as it learns more.
   - This makes the goal block dynamic — the agent can refine
     or narrow the goal over time without losing the original intent.

4. LangGraph style "State Object"
   - The goal is stored as a field inside a typed State
     (e.g. state["goal"]), not inside free-text chat history.
   - Every node in the graph receives the full state, so the
     goal travels with the run automatically — no re-prompting needed.
   - Because state is explicit data (not just text), other
     nodes (like a guardrail node) can check progress against
     the goal directly, instead of re-reading the conversation.

5. AutoGPT / BabyAGI style Agents
   - The goal is stored as a persistent variable outside the
     LLM entirely (in the surrounding Python program).
   - On every loop iteration, the orchestrator re-feeds the
     goal + the latest progress back into a fresh prompt.
   - The LLM itself has no "memory" — the outer program is
     what remembers the goal and keeps the agent aligned.

------------------------------------------------------------
 CORE MEMORY vs OTHER MEMORY TYPES (QUICK CONTRAST)
------------------------------------------------------------

| Memory Type     | What it holds                | Always in context? |
|------------------|------------------------------|---------------------|
| Core Memory      | Goal, persona, key facts     | Yes, every step      |
| Working Memory   | Current step's scratch notes | Only during that step|
| Recall Memory    | Full raw conversation log    | No (searched on demand)|
| Archival Memory  | Long-term facts, documents   | No (retrieved via search)|

------------------------------------------------------------
 KEY TAKEAWAY
------------------------------------------------------------

  No matter the framework, the pattern is the same:
  the GOAL is treated as a special, protected piece of
  memory that is re-inserted into every prompt — either
  automatically (system prompt, state object) or manually
  (editable core memory blocks) — so the agent never
  "forgets" what it's supposed to be doing.

========================================================
"""

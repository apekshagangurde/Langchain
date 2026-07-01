"""
Claude Code - Agents
=====================

What is an Agent?
------------------
An agent is an AI that can autonomously plan, act, and complete
multi-step tasks using tools — without you guiding every step.

In Claude Code, agents can be spawned to handle work in the background
while you continue chatting, or to isolate complex sub-tasks.

---

How Agents Work in Claude Code:
---------------------------------
1. You give a task
2. Claude spins up an agent (fresh or fork)
3. Agent uses tools (read, write, bash, search, etc.)
4. Agent returns a result back to you

---

Types of Agents:
-----------------

1. Fork Agent
   - Copies YOUR current conversation context
   - Runs in background, keeps its tool output out of your context
   - Great for: research, long searches, multi-step work you don't want
     cluttering your main conversation
   - Example: "summarize all files in this repo" → fork handles it

2. Fresh Agent (General Purpose)
   - Starts with zero context — blank slate
   - You must brief it fully in the prompt
   - Great for: independent tasks, second opinions, isolated work
   - Example: "review this migration for safety"

3. Specialized Agents (Built-in Types):
   ┌──────────────────────┬────────────────────────────────────────────┐
   │ Agent Type           │ Best For                                   │
   ├──────────────────────┼────────────────────────────────────────────┤
   │ claude               │ General catch-all tasks                    │
   │ Explore             │ Fast read-only code search                  │
   │ Plan                │ Design implementation plans                 │
   │ claude-code-guide    │ Questions about Claude Code / API / SDK    │
   │ general-purpose      │ Complex multi-step research or tasks       │
   └──────────────────────┴────────────────────────────────────────────┘

---

Fork vs Fresh Agent:
---------------------
| Feature           | Fork Agent          | Fresh Agent          |
|-------------------|---------------------|----------------------|
| Has your context  | Yes (inherited)     | No (blank slate)     |
| Speed             | Fast (cached)       | Slower (cold start)  |
| Use for           | Background research | Independent tasks    |
| Tool noise in ctx | No (isolated)       | No (isolated)        |

---

When to Use Agents:
--------------------
- Task is too long and would fill your context
- You want parallel work (launch multiple agents at once)
- You need an independent second opinion (fresh agent)
- Background research while you keep chatting (fork)

---

Running Agents in Parallel:
-----------------------------
- You can spawn multiple agents in one message
- They run simultaneously — saves time on independent tasks
- Example: one agent searches files, another checks tests, both at once

---

Key Rule:
----------
- Fork   → use when task is open-ended or research-heavy
- Fresh  → use when task needs a clean, unbiased perspective
- Never re-delegate inside a fork — execute directly

---

Worktree Mode — claude -w <name>
----------------------------------
- Launches Claude in an isolated git worktree
- Claude works on a separate branch/copy of the repo — your main code is untouched
- Run: claude -w <name>   → creates a worktree named <name> and starts Claude in it

  How it works:
  1. Git creates a new worktree (separate folder, same repo)
  2. Claude makes all changes inside that worktree
  3. Your main working directory stays clean
  4. When done — merge, discard, or review the worktree branch

  Example:
  claude -w feature-login
  → Claude works in an isolated copy called "feature-login"
  → You review and merge when satisfied

Why use Worktree:
  - Safe experimentation — main branch never touched
  - Run multiple Claude sessions on the same repo in parallel
  - Each worktree is its own branch — easy to diff and merge
  - Auto-cleaned if Claude makes no changes

| Mode          | Isolation        | Use For                        |
|---------------|------------------|--------------------------------|
| Normal        | None             | Regular tasks                  |
| -w <name>     | Git worktree     | Risky changes, parallel work   |
| Fork agent    | Context only     | Background research            |
"""

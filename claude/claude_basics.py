"""
Claude Code - Basics
=====================

1. /btw
--------
- Use it to give Claude extra context mid-conversation without making it a direct command
- Example: "/btw I'm using Python 3.11 and FastAPI"
- Claude notes it silently and uses it going forward

2. /memory
-----------
- Lets you view, edit, or delete what Claude has saved about you
- Claude stores preferences, project info, and feedback across sessions
- Example: "/memory" → opens your memory file to review or update it

3. Auto Memory
---------------
- Claude automatically saves useful info during the conversation
- Things like your role, preferences, project goals, or corrections you give
- You don't need to ask — it happens in the background
- Saved under: ~/.claude/projects/<project>/memory/

4. Double Esc (Esc Esc)
-------------------------
- Press Esc once  → interrupts Claude mid-response (stops generation)
- Press Esc twice → clears the current input and resets the prompt
- Useful when you typed something wrong or want to start fresh quickly

5. /context
------------
- Shows how much of Claude's context window is currently being used
- Helps you understand token usage before hitting limits
- Run: /context        → compact summary
- Run: /context all    → full expanded breakdown

Snapshot (taken during session):
  Model   : claude-sonnet-4-6
  Tokens  : 25.7k / 200k  (13% used)

  Breakdown:
  ┌─────────────────────┬────────┬──────────┐
  │ Category            │ Tokens │ % of 200k│
  ├─────────────────────┼────────┼──────────┤
  │ System prompt       │  6.7k  │   3.3%   │
  │ System tools        │  7.7k  │   3.9%   │
  │ Skills              │  2.5k  │   1.2%   │
  │ Messages            │  8.9k  │   4.4%   │
  │ Free space          │ 141.3k │  70.6%   │
  │ Autocompact buffer  │  33k   │  16.5%   │
  └─────────────────────┴────────┴──────────┘

  MCP Tools loaded : 24 tools (Gmail, Google Calendar, Drive, Figma)
  Skills loaded    : 24 skills (figma, code-review, run, claude-api, etc.)

  Auto-compact kicks in when context fills up — Claude summarizes old turns
  to free space, so the conversation can continue without losing context.

6. /compact
------------
- Manually triggers context compression — summarizes the conversation so far
- Frees up token space without starting a new chat
- Use it when context is getting heavy (e.g. 60-70%+ used)
- Run: /compact                → compresses with default summary
- Run: /compact <instruction>  → compresses with your custom focus
- Example: "/compact focus on the LangGraph changes only"
- After compact: old messages are replaced with a summary, Claude still
  remembers the key context but uses far fewer tokens

7. /clear
----------
- Wipes the entire conversation history and starts completely fresh
- Unlike /compact (which summarizes), /clear removes everything
- Tokens drop back to near zero after clearing
- Run: /clear → full reset, blank slate
- Use when: switching to a totally different task, or context is too messy
- Note: Claude will NOT remember anything from before the clear

8. /model
----------
- Switch the Claude model being used in the current session
- Run: /model              → shows current model
- Run: /model <model-id>  → switches to that model

  Available Models:
  ┌──────────────────────────┬──────────────────────────────────────┐
  │ Model                    │ Best For                             │
  ├──────────────────────────┼──────────────────────────────────────┤
  │ claude-sonnet-4-6        │ Balanced — speed + quality (default) │
  │ claude-opus-4-8          │ Most powerful, complex reasoning      │
  │ claude-haiku-4-5         │ Fastest, lightweight tasks            │
  │ claude-fable-5           │ Latest flagship model                 │
  └──────────────────────────┴──────────────────────────────────────┘

- Example: "/model claude-opus-4-8" → switches to Opus for heavy tasks
- Switch back anytime — model change applies only to current session

9. /plan
---------
- Puts Claude into Plan Mode — Claude thinks and proposes a plan BEFORE writing any code
- Claude will NOT make changes until you approve the plan
- Great for large or risky tasks where you want to review the approach first

  How it works:
  1. You describe the task
  2. Claude drafts a step-by-step plan
  3. You review, adjust, or approve
  4. Claude executes only after approval

- Run: /plan → enters plan mode for the next task
- Use when: adding a feature, refactoring, or anything multi-step
- Prevents Claude from diving in and making unwanted changes

10. /diff
----------
- Shows all file changes Claude made in the current session
- Like `git diff` but scoped to what Claude touched
- Run: /diff → displays added/removed lines across all edited files
- Use it to review Claude's changes before committing

11. /effort
------------
- Controls how hard Claude tries on a task (thinking depth)
- Higher effort = slower but more thorough reasoning
- Run: /effort low    → quick, surface-level response
- Run: /effort medium → balanced (default)
- Run: /effort high   → deep reasoning, best for complex problems
- Use high effort for: debugging hard bugs, architecture decisions, code review

12. /rewind
------------
- Steps back to a previous point in the conversation
- Undoes Claude's last action(s) and lets you try a different approach
- Run: /rewind → goes back one turn
- Use when: Claude did something wrong and you want to retry differently
- Does NOT undo file changes automatically — pair with git to be safe

13. /resume
------------
- Resumes a previous Claude Code session
- Useful when you closed the terminal and want to pick up where you left off
- Run: /resume           → lists recent sessions to choose from
- Run: /resume <id>      → jumps directly into that session
- Claude reloads the conversation context from that session

14. /doctor
------------
- Runs a health check on your Claude Code setup
- Checks if everything is configured and working correctly
- Run: /doctor → scans your environment and reports any issues

  What it checks:
  - API key is valid and set correctly
  - Claude Code version is up to date
  - Node.js / shell environment is compatible
  - MCP servers are connected and healthy
  - Permissions and settings are properly configured

- Use when: something feels broken, MCP tools missing, or after install
"""

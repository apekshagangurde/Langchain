"""
Context Engineering in Deep Agents
==================================

1. INPUT CONTEXT — what goes into the agent's prompt at the start
-----------------------------------------------------------------
Before the agent takes its first step, deep agents builds the system prompt
the model sees. Three things go into it:

a) SYSTEM PROMPT
   Your own instructions, passed with `create_deep_agent(system_prompt=...)`.
   They go FIRST, followed by the built-in deep-agent instructions that explain
   the planning, file and subagent tools. So yours only needs to describe the
   job and the house rules.

b) MEMORY
   AGENTS.md files passed with `create_deep_agent(memory=["/memory/AGENTS.md"])`.
   They are loaded when the agent starts and their FULL text is added to the
   system prompt. Use them for things the agent should always know: user
   preferences, project conventions, past lessons.

c) SKILLS
   Skill folders passed with `create_deep_agent(skills=["/skills/"])`. Each skill
   is a folder with a SKILL.md file (YAML frontmatter + instructions).
   Only each skill's NAME and DESCRIPTION go into the prompt at the start
   (progressive disclosure). The agent reads the full SKILL.md with
   `read_file` only when a task needs that skill, so many skills cost very
   little context.

Memory and skill paths are read through the agent's backend: with
FilesystemBackend they are real files under `root_dir`; with StateBackend
(default) you pass them in with `agent.invoke({"messages": [...], "files": {...}})`.

    Memory  = always in the prompt (full text)
    Skills  = always listed (name + description), loaded on demand


2. RUNTIME CONTEXT — data the agent's code can use, but the model never sees
---------------------------------------------------------------------------
Runtime context is information for a single run that your TOOLS and middleware
need, but that does not belong in the prompt: user ID, API keys, DB
connections, feature flags.

  - Define its shape with `create_deep_agent(context_schema=MyContext)`.
  - Pass the values on each call: `agent.invoke({...}, context=MyContext(user_id="u1"))`.
  - Read it inside a tool via `runtime.context.user_id` (`ToolRuntime` argument).

It is read-only for the run and costs ZERO prompt tokens: the model only sees
what a tool chooses to return. That also keeps secrets out of the prompt.


3. CONTEXT COMPRESSION — keeping a long run inside the context window
---------------------------------------------------------------------
Deep agents run for many steps, and every tool result piles up in the message
history. Two things are built in to stop it from overflowing:

a) OFFLOADING LARGE TOOL RESULTS
   When a tool result is too big (about 20,000 tokens by default), it is saved
   to a file under `/large_tool_results/` and the message history keeps only a
   short preview plus the file path. The agent can `read_file` or `grep` it
   later if it needs the details.

b) SUMMARIZATION
   When the conversation gets close to the model's context limit, older
   messages are replaced with an LLM-written summary. The full original
   history is saved to the backend, so nothing is truly lost.

Your part: tell the agent (in the system prompt) to save findings to files
with `write_file` instead of keeping everything in chat. Files are context
the agent can reload on demand.


4. CONTEXT ISOLATION — subagents get their own clean context window
--------------------------------------------------------------------
When the main agent delegates with the `task` tool, the subagent starts with a
FRESH context: only its own system prompt, its tools, and the task
description. It does all its messy work (searches, tool calls, retries) in
that separate window, and only its FINAL answer comes back to the main agent.

Why it matters:
  - the main agent's context stays small and focused on the overall plan
  - one subtask's noise cannot confuse another subtask
  - each subagent can have a narrow prompt and only the tools it needs

    Main agent:  plan -> task("research Pune") -> gets back 3 bullet points
    Subagent:    10 tool calls, 5,000 tokens of raw results  (never seen by main)
"""

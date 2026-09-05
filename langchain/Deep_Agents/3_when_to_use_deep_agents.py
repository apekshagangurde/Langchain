"""
When To Use Deep Agents
=======================
Theory only — no code in this file. Files 1 and 2 covered what a deep agent IS.
This one covers when it is the right choice, and when it is the wrong one.


THE CORE TRADE-OFF
------------------
A deep agent buys reliability on long tasks by spending tokens, latency and
complexity. That is a good trade only when the task is actually long.

    shallow agent   1 model call per step, 1 context, seconds, cents
    deep agent      many model calls per step (planning + sub-agents + reads),
                    many contexts, minutes, dollars

So the question is never "which is better" — it is "is this task long enough to
pay for the overhead".


USE A DEEP AGENT WHEN...
------------------------
1. THE TASK NEEDS MORE THAN ~10 STEPS
   If you cannot picture the whole task fitting in one context window, the agent
   cannot either. Planning and file-based memory exist precisely for this.

2. THE TASK HAS SEPARABLE SUB-TASKS
   "Research three competitors" is three independent jobs. Independent jobs are
   what sub-agents are for — each gets a clean context and its own prompt.

3. INTERMEDIATE RESULTS ARE LARGE BUT THE ANSWER IS SMALL
   Reading 40 files to write one paragraph. A sub-agent absorbs the 40 files and
   returns the paragraph; the main context never sees the bulk.

4. THE PHASES NEED DIFFERENT INSTRUCTIONS
   Researching, writing and fact-checking want different prompts and different
   tools. One shared prompt makes each phase worse.

5. THE WORK MUST SURVIVE INTERRUPTION
   Long runs get summarised, crash, or need resuming tomorrow. A plan in state
   and findings in files survive that; a message history does not.

6. YOU NEED TO SEE THE AGENT'S REASONING AS IT WORKS
   The to-do list is a live progress report — valuable when a human is
   supervising a long-running job.


DO NOT USE A DEEP AGENT WHEN...
-------------------------------
1. THE TASK IS 1-5 STEPS
   A deep agent will write a to-do list for "what's the weather in Pune", spawn a
   sub-agent to answer it, and save it to a file. Slower, pricier, no more correct.

2. LATENCY MATTERS
   Planning and delegation multiply model calls. Anything user-facing and
   interactive usually cannot afford it.

3. THE STEPS ARE FIXED AND KNOWN IN ADVANCE
   If you already know the sequence, write a chain or a LangGraph graph. Letting
   a model rediscover a pipeline you could hardcode is expensive and less
   reliable. Agents are for when the path is genuinely unknown.

4. THE TASK IS ONE TOOL CALL WRAPPED IN TEXT
   Lookups, conversions, formatting, classification — a shallow agent, or often
   just a model with one tool, is the right size.

5. YOU HAVEN'T TRIED SHALLOW YET
   Most "we need a deep agent" problems are actually a bad prompt, a missing
   tool, or a tool returning too much text. Fix those first — they are cheaper
   fixes and they help the deep agent too, if you still end up needing one.


THE ESCALATION LADDER
---------------------
Work up this list and stop at the first rung that solves your problem:

    1. a plain model call                        no tools needed
    2. a model + one tool                        one clear action
    3. a chain / LangGraph graph                 steps known in advance
    4. a shallow agent (create_agent)            path unknown, few steps
    5. a shallow agent + middleware              add summarisation, limits,
                                                 retries, human approval
    6. a deep agent                              long, open-ended, many sub-tasks

Rung 5 is where most production agents live. Middleware fixes a surprising number
of the problems people reach for deep agents to solve: `SummarizationMiddleware`
for context overflow, `ToolCallLimitMiddleware` for runaway loops,
`HumanInTheLoopMiddleware` for risky actions.


A QUICK TEST
------------
Ask three questions about the task:

    Can I list the steps in advance?          yes -> use a graph, not an agent
    Will it take more than ~10 steps?         no  -> shallow agent
    Do sub-tasks produce a lot of text
      that the final answer doesn't need?     yes -> deep agent

Two "no"s and a "yes" on the last is the clearest deep-agent signal there is:
that is exactly the context-isolation problem sub-agents solve.


CLASSIC DEEP-AGENT USE CASES
----------------------------
  research reports        many sources in, one document out
  codebase migrations     dozens of files, one consistent change, verification
  deep code review        many files reviewed independently, findings merged
  competitive analysis    parallel research per competitor, then synthesis
  data investigations     explore, hypothesise, check, repeat until an answer

What these share: unknown path, many steps, large intermediate volume, small
final output. That combination is the deep-agent shape.


COST AND FAILURE NOTES
----------------------
  - cost scales with sub-agents, not steps: each one is a full agent loop
  - a deep agent can fail by OVER-planning — 12 todos for a 2-step task; the
    prompt must say when planning is unnecessary
  - sub-agents cannot see each other's work, only what they return; anything two
    sub-agents both need must go through files or the main agent
  - more moving parts means more to debug; trace runs with LangSmith
"""

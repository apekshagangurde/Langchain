"""
========================================================
            LangChain vs LangGraph — Quick Guide
========================================================

------------------------------------------------------------
 DEFINITIONS
------------------------------------------------------------

LangChain:
  A framework for building LLM apps by CHAINING steps together
  in a straight line: prompt → LLM → parser → next step.
  Great for pipelines where the order of steps is fixed and
  known in advance.

  Example: Load a PDF → split into chunks → embed → store in
           a vector DB → retrieve → answer (a linear RAG chain).

LangGraph:
  A framework (built by the LangChain team) for building LLM
  apps as a GRAPH instead of a straight line: nodes = steps,
  edges = the flow between them. Supports loops, branches,
  conditional routing, and explicit state — things a simple
  chain can't easily do.

  Example: An agent that plans → acts → checks the result →
           loops back to plan again if the result isn't good
           enough, and only stops when the goal is reached.

------------------------------------------------------------
 KEY DIFFERENCES
------------------------------------------------------------

| Feature            | LangChain                        | LangGraph                              |
|--------------------|-----------------------------------|-----------------------------------------|
| Structure          | Linear chain (A → B → C)          | Graph (nodes + edges, any shape)         |
| Loops / cycles      | Hard / not natural                | Native support (loop back to any node)   |
| Branching logic     | Limited                           | Conditional edges built in               |
| State management    | Manual, passed through the chain  | Explicit shared State object per run     |
| Human-in-the-loop    | Difficult to pause mid-chain      | Easy — add a "wait for input" node       |
| Multi-agent setups   | Awkward to coordinate             | Natural fit (Supervisor + sub-agents)    |
| Best for            | Simple pipelines, RAG, Q&A        | Agentic workflows, multi-step reasoning  |

------------------------------------------------------------
 HOW THEY RELATE (NOT COMPETITORS)
------------------------------------------------------------

  LangGraph is NOT a replacement for LangChain — it's built
  ON TOP of LangChain's building blocks (LLM wrappers, tools,
  prompts, retrievers) and adds a graph-based orchestration
  layer around them.

  - LangChain  → gives you the LEGO BRICKS (LLM calls, tools,
                 prompts, memory, retrievers).
  - LangGraph  → gives you the BLUEPRINT for how those bricks
                 connect, loop, and make decisions together.

  Many real projects use LangChain components INSIDE
  LangGraph nodes — e.g. a node that calls a LangChain
  retriever, or a node that runs a LangChain tool.

------------------------------------------------------------
 WHEN TO USE WHICH
------------------------------------------------------------

Use LangChain when:
  - The task is a simple, fixed sequence of steps.
  - You don't need loops, retries, or complex branching.
  - Example: "Summarize this document" or basic RAG Q&A.

Use LangGraph when:
  - The task needs the agent to plan, act, check, and repeat.
  - You need explicit control over state across many steps.
  - You need to pause for human approval mid-task.
  - You're coordinating multiple agents together.
  - Example: An autonomous research agent, a multi-agent
             customer support system, or any workflow where
             the number of steps isn't known in advance.

------------------------------------------------------------
 VIDEO NOTES :-
------------------------------------------------------------

 CHALLENGES IN LANGCHAIN WHEN IMPLEMENTING COMPLEX WORKFLOWS
------------------------------------------------------------

1) Control Flow Complexity

   - Real workflows aren't always a straight line — they need
     CONDITIONALS ("if this, do that"), BRANCHES ("split into
     multiple possible paths"), LOOPS ("repeat until done"),
     and JUMPS ("go back to an earlier step").

   - Example (from video): an agent checks its own output
     against some criteria — if the criteria is NOT satisfied,
     it needs to JUMP BACK to an earlier step and try again,
     instead of just moving forward blindly.

   - LangChain's chains are built to run in one direction,
     step 1 → step 2 → step 3. They don't naturally support
     "go back to step 1 if this check fails." Loops and jumps
     like this are NOT something LangChain gives you out of
     the box.

   - Because of this gap, the developer ends up writing a lot
     of extra custom code just to force this looping/branching
     behavior on top of LangChain — this extra code is what's
     referred to as GLUE CODE.

   Glue Code (definition):
     Custom code that YOU have to write, that doesn't do any
     real "work" for the app itself, but exists only to connect
     pieces together, handle control flow (loops/conditionals/
     retries), and pass data between steps that the framework
     doesn't handle natively.

     In other words — it's the "duct tape" code that holds a
     workflow together when the framework's built-in structure
     isn't flexible enough to express the logic directly.

     Problem with relying on glue code:
       - It's manual, repetitive, and easy to get wrong.
       - It's not reusable — every complex workflow needs its
         own custom glue code written from scratch.
       - It makes the codebase harder to read/maintain, since
         the "real" logic gets buried inside plumbing code.

   - This is exactly the gap LangGraph is designed to close:
     loops, branches, and jumps become native parts of the
     GRAPH structure (conditional edges, cycles back to any
     node) — so you don't need to hand-write glue code just
     to make the workflow loop or branch.

2) State Handling

   - In any workflow, there are certain data points/values
     that keep CHANGING as you move forward from one step to
     the next (e.g. the user's input, intermediate results,
     a counter, a flag showing pass/fail). This evolving data
     is called the STATE of the workflow.

   - State is naturally a set of KEY-VALUE pairs — e.g.
     {"input": "...", "output": "...", "steps": 2}.

   - LangChain has no built-in way to store and manage this
     kind of state. There's no native memory object that
     automatically carries key-value data forward through a
     chain. LangChain is essentially STATELESS by default.

   - Because of this, the developer has to manually write
     extra code to create a dictionary, pass it between steps,
     and update its values at every step. As the workflow gets
     more complex (more steps, more branches, more data points
     to track), this hand-written state-management code also
     becomes more complex — it turns into more glue code.

   - LangGraph solves this natively: every graph run has a
     single shared STATE OBJECT. Every node automatically gets
     access to this state, can READ values from it, and can
     EDIT/UPDATE values in it. As execution moves from node to
     node, the updated state just flows along automatically —
     no manual dictionary-passing or glue code required.

   Quick summary:
     LangChain → STATELESS  (you build state-passing yourself)
     LangGraph → STATEFUL   (state object is built in, shared
                             across all nodes, and auto-updated
                             as the workflow moves forward)

3) Event-Driven Execution

   - A workflow can run in two different ways:

     a) Sequential  → Runs straight through, step after step,
                       without stopping anywhere. Nothing
                       pauses it midway.

     b) Event-Driven → The workflow PAUSES at some point and
                        WAITS for an external event/factor to
                        happen before it continues. It only
                        moves to the next step once that event
                        actually gets triggered.

   - Example (from video): You send an offer letter to a
     candidate. The workflow should trigger the "next step"
     only when the candidate ACCEPTS the offer letter — it has
     to sit and wait for that external trigger before moving on.

   - LangChain does not have this "wait for an external event"
     feature built in. To achieve this, you'd need to build it
     yourself — e.g. write TWO separate chains (one that sends
     the offer, one that runs after acceptance) plus extra glue
     code in between to check whether the candidate has
     accepted or not, and manually decide when to call the
     second chain.

   - LangGraph supports this naturally because it's stateful —
     it can pause a run at a node, persist the state, and only
     resume/continue once the expected trigger/event actually
     occurs, without needing separate chains stitched together
     with manual glue code.

4) Fault Tolerance

   Fault Tolerance (definition):
     The ability of a system to keep working correctly, or to
     recover gracefully, even when something goes wrong (like
     a crash, a server outage, or a network failure) — instead
     of losing all progress and failing completely.

   - Example : You have a chain of 5 steps. If the
     server goes down while on step 3, what happens to the
     progress already made in steps 1 and 2, and what happens
     to steps 4 and 5?

   - LangChain does NOT have built-in fault tolerance. If a
     step fails or the server goes down mid-chain, there's no
     native mechanism to retry it or pick back up where it left
     off — you'd have to build that handling yourself.

   - LangGraph supports fault tolerance built in, mainly
     through two things:

     a) Retry Logic → For short/temporary failures, LangGraph
                       can automatically RETRY the failed step
                       instead of the whole run dying.

     b) Recovery via Checkpoints → If the workflow fails partway
                       through, you can RECOVER from that exact
                       point instead of starting over from step 1.
                       This works because LangGraph uses a
                       PERSISTENCE LAYER that saves a SNAPSHOT of
                       the state after every step (a "checkpoint").
                       When resuming, LangGraph checks the last
                       saved state/checkpoint and continues the
                       workflow from there.

   Quick summary:
     LangChain → No built-in fault tolerance (failure = lost
                 progress, must be handled manually).
     LangGraph → Built-in fault tolerance via retry logic +
                 checkpoint-based recovery (persistence layer
                 snapshots state after every step).

5) Human-in-the-Loop

   - Many real workflows need a HUMAN to step in and give a
     response/approval before the workflow can continue (e.g.
     approving a request, reviewing an output, confirming an
     action) — this is called HUMAN-IN-THE-LOOP.

   - In LangChain, building human-in-the-loop is hard, because
     LangChain is not designed to sit and wait for a long time
     for a human's approval. A chain expects to run start-to-
     finish, not pause indefinitely mid-way for someone to
     respond.

   - To fake this in LangChain, you again need TWO separate
     chains: run the first chain, then write extra code outside
     the chain to capture the human's input/response, and only
     then trigger the second chain with that input — essentially
     more manual glue code stitching the two halves together.

   - LangGraph supports human-in-the-loop naturally, because it
     is STATEFUL and CHECKPOINT-based: it can save the workflow's
     progress at the exact point a human response is needed, and
     then simply RESUME the run from that saved checkpoint once
     the human's review/input is received — no separate chains
     or manual stitching required.

6) Nested Workflows (Subgraphs) — this is a FEATURE, not a challenge

   - LangGraph lets you build SUBGRAPHS — a subgraph is a graph
     that is itself used as a single NODE inside a bigger, outer
     graph. This means you can build complex systems out of
     smaller graphs nested inside one another.

   - This is what makes MULTI-AGENT systems possible: each
     "agent" can be its own self-contained subgraph (with its
     own nodes, state, and logic), and a top-level graph simply
     coordinates/calls these agent-subgraphs as nodes.

     Example: A "Research Agent" subgraph (search → summarize →
     verify) and a "Writing Agent" subgraph (outline → draft →
     edit) can both be plugged in as nodes inside one top-level
     "Content Pipeline" graph that decides when to call each one.

     Example: A customer support system where a "Billing Agent"
     subgraph and a "Technical Support Agent" subgraph are both
     nodes inside a top-level "Supervisor" graph that routes the
     user's query to whichever subgraph fits.

   - Subgraphs also give you REUSABILITY — once you've built a
     subgraph for a common piece of logic (e.g. a "validate and
     retry" subgraph, or a "human approval" subgraph), you can
     plug that SAME subgraph as a node into many different
     bigger graphs, instead of rebuilding that logic every time.
     This turns a workflow into a reusable, shareable building
     block instead of one-off code.

7) Observability

   Observability (definition):
     The ability to understand WHAT is happening inside a
     running system — and WHY — by looking at the data it
     produces (logs, traces, prompts, outputs) while it runs,
     rather than only seeing pass/fail at the end.

   - In production, things go wrong in many different ways, and
     observability is what lets you find the REASONS behind
     those failures — it's what actually helps with DEBUGGING
     when something breaks in a live system.

   - LangChain has LangSmith for observability — it records
     prompts, LLM calls, and other run details so you can trace
     what happened.

   - The issue: LangSmith only records/traces the parts that go
     through LangChain's own code. It does NOT capture the
     custom GLUE CODE you wrote yourself (the manual loops,
     retries, dict-passing, etc. from the earlier challenges).
     So in LangChain, observability ends up PARTIAL — you can
     see inside the LangChain steps, but the glue code around
     them stays invisible.

   - In LangGraph, since the loops, branches, state, retries,
     and human-in-the-loop pauses are all NATIVE parts of the
     graph (not hand-written glue code), LangSmith can track
     EVERY part of the run for LangGraph — including things
     like human responses, checkpoint resumes, and retries —
     giving FULL observability instead of a partial view.

------------------------------------------------------------
 WHEN TO USE WHAT (RECAP)
------------------------------------------------------------

   - Simple workflow (fixed, linear, no loops, no waiting on
     anything external) → Use LANGCHAIN.

   - Complex workflow (needs loops/jumps, branching, shared
     state, event-driven waits, fault tolerance, human-in-the-
     loop, or multi-agent subgraphs) → Use LANGGRAPH.

========================================================
"""

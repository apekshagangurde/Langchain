"""
========================================================
              LLM Core Concept — LLM Workflows
========================================================

------------------------------------------------------------
 DEFINITION
------------------------------------------------------------

LLM Workflow:
  A step-by-step process, built using one or more LLM calls,
  that lets you go from a simple single prompt-response
  interaction to building COMPLEX LLM applications.

  Instead of relying on a single LLM call to do everything,
  a workflow breaks the problem into smaller steps — where
  each step is an LLM call (or a decision, or several LLM
  calls at once) — and defines exactly how those steps
  connect together.

  These workflow patterns are the common, reusable "shapes"
  that show up again and again when building real LLM-based
  applications.

------------------------------------------------------------
 COMMON LLM WORKFLOWS
------------------------------------------------------------

1) Prompt Chaining

   - The simplest workflow: you talk to the LLM in a CHAIN —
     the output of one LLM call becomes the input to the next
     LLM call, and so on.
   - Each step in the chain focuses on one smaller sub-task,
     instead of asking one giant prompt to do everything at once.

   Example: Step 1 → LLM extracts key points from a document.
            Step 2 → LLM turns those key points into a summary.
            Step 3 → LLM translates that summary into another
                     language.

2) Routing

   - Adds a DECISION-MAKING step before the actual work happens.
   - Based on the input, a decision is made about WHICH LLM (or
     which specific prompt/path) should handle this particular
     request, and the input is then routed there.
   - Useful when different types of inputs need very different
     handling (different prompts, different models, different
     specialized logic).

   Example: A support query first goes through a router step
            that decides: "Is this a billing question or a
            technical question?" → routes to the Billing LLM
            path or the Technical Support LLM path accordingly.

3) Parallelization

   - Instead of running LLM calls one after another, this
     workflow RUNS MULTIPLE LLM calls IN PARALLEL (at the same
     time), and then MERGES/combines their responses together
     into one final result.
   - Useful when a task can be split into independent sub-parts
     that don't depend on each other's output.

   Example: Three LLM calls run at once — one checks grammar,
            one checks factual accuracy, one checks tone — and
            their three results are merged into one final review.

4) Orchestrator-Worker(s) Workflow

   - Similar in shape to the Parallelization workflow (multiple
     LLM calls happening around a central flow), but the key
     difference is: the ORCHESTRATOR does not know the internal
     working/details of each individual worker LLM — it only
     knows how to break the task down, assign pieces of it to
     the right workers, and combine their results at the end.
   - The orchestrator manages the "what needs to be done and who
     does it," while each worker LLM independently handles its
     own piece without the orchestrator needing to know HOW.

   Example: An orchestrator breaks "write a research report"
            into sub-tasks and hands them off to separate worker
            LLMs (one for gathering data, one for writing intro,
            one for writing conclusion) — the orchestrator just
            collects and assembles their outputs.

5) Evaluator-Optimizer

   - Built around an ITERATION loop, with two roles:
       - Generator LLM  → produces an attempt/output.
       - Evaluator LLM  → reviews that output and judges whether
                           it's good enough (and gives feedback).
   - If the Evaluator is not satisfied, the Generator tries
     again — often using the Evaluator's feedback — and this
     loop repeats until the output meets the required quality,
     instead of just accepting the first attempt.

   Example: A Generator LLM writes a piece of code → an
            Evaluator LLM checks it against requirements/tests →
            if it fails, the Generator LLM revises the code based
            on the feedback, and this repeats until it passes.

------------------------------------------------------------
 GRAPHS, NODES & EDGES (HOW LANGGRAPH BUILDS THESE WORKFLOWS)
------------------------------------------------------------

Graph:
  The overall structure used to represent a workflow — made up
  of NODES (the steps/tasks) connected by EDGES (the flow/
  order between those steps). All the workflow patterns above
  (prompt chaining, routing, parallelization, etc.) can be
  represented as different shapes of a graph.

Node:
  Represents a single TASK/step in the workflow.
  - A node is nothing more than a PYTHON FUNCTION.
  - It takes the current state as input, does some work
    (e.g. calls an LLM, runs some logic), and returns an
    update to the state.
  - So at the end of the day, an entire graph is really just a
    SET OF PYTHON FUNCTIONS, wired together, that get executed
    in a particular order.

Edge:
  Represents the CONNECTION/FLOW between nodes — it decides
  which node runs next after the current one finishes.
  - A normal edge always goes to the same next node.
  - A conditional edge picks the next node dynamically, based
    on the current state (this is what enables routing,
    branching, and loops).

State:
  A shared data structure that represents the CURRENT SNAPSHOT
  of the workflow at any point in time — it holds all the
  values/data points that the graph is working with (e.g.
  user input, intermediate results, flags, counters).

  - It is typically a set of KEY-VALUE pairs.
  - Every NODE (python function) receives the state as input,
    can READ from it, and returns an UPDATE to it.
  - As execution moves from node to node along the edges, the
    state travels along and gets updated at each step — so it
    always reflects everything that has happened SO FAR in
    the run.
  - This is what allows nodes to share information with each
    other without needing to pass data around manually.

Reducer:
  A rule that decides HOW a node's returned update should be
  COMBINED with the existing value already in the state for
  that key — instead of just always overwriting it.

  - By default, when a node returns a value for a state key,
    it simply REPLACES/OVERWRITES the old value with the new one.
  - This isn't always what you want. Example: if "messages" is
    a state key holding the conversation history, you don't
    want each new message to overwrite/erase the old ones — you
    want the new message APPENDED to the existing list.
  - A reducer defines exactly this merge behavior for a given
    state key — e.g. "overwrite," "append to list," "add the
    numbers together," etc.
  - This way, each state field can have its own custom logic
    for how updates from nodes get merged in, instead of every
    field being forced to just overwrite on every update.

------------------------------------------------------------
 LANGGRAPH EXECUTION MODEL
------------------------------------------------------------

  Building and running a graph in LangGraph happens in three
  phases:

1) Graph Definition

   - This is where you DEFINE the shape of the graph:
     - Add all the NODES (the python functions representing
       each task/step).
     - Add all the EDGES (how those nodes connect to each
       other, including any conditional edges).
   - At this point, the graph is just a definition/blueprint —
     it hasn't run yet, it's simply describing what nodes exist
     and how they're wired together.

2) Compilation

   - The defined graph is COMPILED before it can be run.
   - Compilation takes the graph definition (nodes + edges) and
     turns it into an actual EXECUTABLE object that is ready to
     be invoked — it validates the structure and prepares it
     to be run.

3) Invocation (the Execution Phase)

   - This is where the graph actually RUNS. You INVOKE the
     compiled graph by passing in an INITIAL STATE.
   - That initial state is passed to the FIRST node → this
     "activates" that node, meaning the python function behind
     that node gets executed.
   - Once that node finishes, its returned update to the state
     travels ALONG THE EDGE to the next node — this handing off
     of state from one node to another is called MESSAGE PASSING.
   - Receiving this state then ACTIVATES the next node (its
     python function runs), and this continues node after node,
     following the edges, until there's nothing left to run.

   Superstep:
     One round of execution where all the nodes that are
     currently active run (in parallel, if more than one is
     active at the same time) and pass their resulting messages/
     state updates onward. The whole run of a graph is really a
     sequence of these supersteps, one after another.

   Halting Condition:
     The graph run STOPS when there is nothing left to execute —
     specifically: NO nodes are currently active, AND NO
     messages/state updates are currently in transit between
     nodes. Once both of these are true, the run is considered
     complete.

========================================================
"""

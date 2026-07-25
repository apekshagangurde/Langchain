"""
========================================================
           Gen AI vs Agentic AI — Quick Guide
========================================================

------------------------------------------------------------
 DEFINITIONS
------------------------------------------------------------

Gen AI (Generative AI):
  You give it a question → it gives you an answer → done.
  It does NOT remember what you asked before, it does NOT
  take any action, it just generates text/code/images.
  Think of it like a very smart calculator — input in, output out.

  Example: You ask ChatGPT "What is Python?" → it replies → stops.

Agentic AI:
  You give it a GOAL → it figures out the steps on its own →
  takes actions (search web, run code, call APIs) → checks results →
  adjusts if needed → keeps going until the goal is complete.
  Think of it like hiring an assistant who works independently.

  Example: You say "Book me a flight to Mumbai for tomorrow" →
           it searches flights, compares prices, picks the best,
           and books it — all by itself.

------------------------------------------------------------
 GEN AI vs AGENTIC AI — KEY DIFFERENCES
------------------------------------------------------------

| Feature          | Gen AI                  | Agentic AI                    |
|------------------|-------------------------|-------------------------------|
| How it works     | One question, one answer| Plan → Act → Check → Repeat   |
| Uses tools?      | No                      | Yes (search, code, APIs, DB)  |
| Has memory?      | No (forgets each time)  | Yes (remembers past steps)    |
| Makes decisions? | No                      | Yes (plans and adapts)        |
| Best for         | Q&A, writing, summarize | Autonomous multi-step tasks   |

------------------------------------------------------------
 KEY CHARACTERISTICS OF AGENTIC AI
------------------------------------------------------------

- Autonomous       → Works on its own. You set the goal, it handles the rest
                     without you approving every single step.

- Goal-Oriented    → Always focused on completing the final goal,
                     not just answering one question at a time.

- Planning         → Before acting, it breaks the big task into smaller steps.
                     Like making a to-do list before starting work.

- Reasoning        → It thinks: "What is the best action right now?"
                     and picks the most suitable option at each step.

- Context Awareness→ Remembers what it already did so it doesn't repeat steps
                     or lose track of the task mid-way.

- Adaptability     → If one approach fails, it tries a different one.
                     It doesn't just stop — it adjusts and continues.

------------------------------------------------------------
 5 MAIN COMPONENTS OF AGENTIC AI
------------------------------------------------------------

1. Brain (LLM)    → The AI model (like Claude/GPT) that does all the thinking,
                    understanding, and decision-making.

2. Orchestrator   → The manager that decides: what step to run next,
                    which tool to call, and when to stop.

3. Tools          → The agent's hands — search the web, run Python code,
                    read files, call APIs, query databases, send emails.

4. Memory         → Keeps track of what has happened so far.
                    Short-term: current task steps.
                    Long-term: info saved across sessions.

5. Supervisor     → Oversees multiple agents working together.
                    Assigns tasks, catches errors, and coordinates the team.

------------------------------------------------------------
 WORKFLOW vs AGENT
------------------------------------------------------------

Workflow:
  A fixed set of steps defined in advance.
  Always runs the same way, no matter what happens.
  Like a recipe — step 1, step 2, step 3, done.
  Good when the process never changes.

Agent:
  A dynamic system that decides its own steps.
  It reacts to what it finds along the way and changes its plan.
  Like a chef who improvises based on available ingredients.
  Good when the task changes or is unpredictable.

------------------------------------------------------------
 WHY NOT LANGCHAIN? → WHY LANGGRAPH?
------------------------------------------------------------

LangChain Challenges:
  - Agents in LangChain run in a straight line — no loops or cycles.
    Once a step is done, you can't easily go back or repeat it.
  - Tracking "what has happened so far" (state) is complicated.
  - Pausing an agent mid-task for human review is very hard to set up.
  - Running multiple agents together and coordinating them gets messy.
  - You have very little control over how the agent flows step-by-step.

Why LangGraph Solves This:
  - Represents your agent as a GRAPH (nodes = steps, edges = flow).
    So you can have loops, branches, and decisions built right in.
  - State (everything the agent knows so far) is tracked automatically
    and passed cleanly between every node.
  - You can add a "pause here and wait for human input" node easily.
  - Multiple agents (like a team) can be wired together with a Supervisor.
  - You decide exactly what runs, when, and under what condition.

========================================================
"""

from langgraph.graph import StateGraph, END
from typing import TypedDict


class State(TypedDict):
    input: str
    output: str
    steps: int


# --- Gen AI style: single pass, no reasoning loop ---
def gen_ai_node(state: State) -> State:
    # Simulates a simple one-shot LLM response
    response = f"[Gen AI] Direct answer to: '{state['input']}'"
    return {"output": response, "steps": 1}


# --- Agentic AI style: think → act → observe loop ---
def think_node(state: State) -> State:
    thought = f"[Agent] Planning how to handle: '{state['input']}'"
    print(thought)
    return {"steps": state["steps"] + 1}


def act_node(state: State) -> State:
    action = f"[Agent] Executing action for: '{state['input']}'"
    print(action)
    return {"steps": state["steps"] + 1}


def observe_node(state: State) -> State:
    result = f"[Agent] Final answer after {state['steps']} steps for: '{state['input']}'"
    return {"output": result, "steps": state["steps"] + 1}


def should_continue(state: State) -> str:
    # After 2 reasoning steps, finish
    return END if state["steps"] >= 2 else "think"


# Build Gen AI graph (single node, no loop)
gen_ai_graph = StateGraph(State)
gen_ai_graph.add_node("respond", gen_ai_node)
gen_ai_graph.set_entry_point("respond")
gen_ai_graph.add_edge("respond", END)
gen_ai_app = gen_ai_graph.compile()

# Build Agentic AI graph (think → act → observe loop)
agentic_graph = StateGraph(State)
agentic_graph.add_node("think", think_node)
agentic_graph.add_node("act", act_node)
agentic_graph.add_node("observe", observe_node)
agentic_graph.set_entry_point("think")
agentic_graph.add_edge("think", "act")
agentic_graph.add_edge("act", "observe")
agentic_graph.add_conditional_edges("observe", should_continue)
agentic_app = agentic_graph.compile()


if __name__ == "__main__":
    user_input = "What is the capital of France?"
    initial_state = {"input": user_input, "output": "", "steps": 0}

    print("=" * 50)
    print("GEN AI (single pass)")
    print("=" * 50)
    result = gen_ai_app.invoke(initial_state)
    print(result["output"])

    print()
    print("=" * 50)
    print("AGENTIC AI (multi-step loop)")
    print("=" * 50)
    result = agentic_app.invoke(initial_state)
    print(result["output"])

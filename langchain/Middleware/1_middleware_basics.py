"""
Agent Middleware Basics
=======================
Middleware lets you hook into an agent's run loop without rewriting the agent.
`create_agent()` builds a graph roughly like:

    START -> before_agent -> before_model -> MODEL -> after_model -> TOOLS -> ... -> after_agent -> END

Middleware plugs into that loop at six points:

  before_agent      runs once, before the loop starts        (load memory, validate input)
  before_model      runs before every model call             (trim messages, inject context)
  wrap_model_call   wraps the model call itself              (retry, fallback, swap model)
  after_model       runs after every model call              (guardrails, logging)
  wrap_tool_call    wraps every tool call                    (cache, block, rewrite result)
  after_agent       runs once, when the loop finishes        (persist results, cleanup)

Two ways to write one:

  1. Decorators  — @before_model, @after_model, @wrap_model_call, ... on a plain function.
                   Quick, one hook per middleware.
  2. Subclass    — class MyMiddleware(AgentMiddleware) with the hook methods you need.
                   Use when one middleware needs several hooks or its own state.

Ordering: middleware run in list order on the way in, reverse order on the way out.
So middleware=[A, B] means A.before_model -> B.before_model -> MODEL -> B.after_model -> A.after_model.
"""

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import AgentState, Runtime, after_model, before_model
from langchain.tools import tool
from langchain_groq import ChatGroq

load_dotenv()


@tool
def word_count(text: str) -> int:
    """Counts the number of words in a piece of text."""
    return len(text.split())


# ---------------------------------------------------------------------------
# Hook 1: before_model — runs just before every model call.
# Return a dict to update agent state, or None to leave state untouched.
# ---------------------------------------------------------------------------
@before_model
def log_before_model(state: AgentState, runtime: Runtime) -> None:
    print(f"[before_model] messages in state: {len(state['messages'])}")
    return None


# ---------------------------------------------------------------------------
# Hook 2: after_model — runs right after every model call.
# The model's reply is the last message in state.
# ---------------------------------------------------------------------------
@after_model
def log_after_model(state: AgentState, runtime: Runtime) -> None:
    last = state["messages"][-1]
    tool_calls = getattr(last, "tool_calls", []) or []
    if tool_calls:
        print(f"[after_model]  model asked for tools: {[c['name'] for c in tool_calls]}")
    else:
        print(f"[after_model]  model answered with text ({len(last.text)} chars)")
    return None


model = ChatGroq(model="openai/gpt-oss-20b")

agent = create_agent(
    model=model,
    tools=[word_count],
    system_prompt="You are a concise assistant. Use tools when they help.",
    middleware=[log_before_model, log_after_model],
)

result = agent.invoke(
    {"messages": [{"role": "user", "content": "How many words are in 'the quick brown fox jumps'?"}]}
)

print("\n--- Final answer ---")
print(result["messages"][-1].text)

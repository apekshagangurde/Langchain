"""
HumanInTheLoopMiddleware
========================
Some tools shouldn't run unsupervised — sending email, refunding money, deleting
files. `HumanInTheLoopMiddleware` pauses the agent right before those tools run
and waits for a human decision.

    HumanInTheLoopMiddleware(interrupt_on={"send_email": True})

    tool needs approval -> agent PAUSES (raises an interrupt)
    you send a decision -> agent RESUMES from exactly where it stopped

`interrupt_on` maps tool name -> what's allowed:
    True                                        pause; all four decisions allowed
    False                                       auto-approve, never pause
    {"allowed_decisions": ["approve", ...]}     pause; only these decisions allowed

Tools not listed at all are auto-approved.

The four decisions you can send back:
    {"type": "approve"}                                    run the tool as-is
    {"type": "reject", "message": "..."}                   don't run it; tell the model why
    {"type": "edit", "edited_action": {"name": ..., "args": {...}}}   run it with fixed args
    {"type": "respond", "message": "..."}                  skip the tool; you answer for it

TWO THINGS ARE REQUIRED for pausing to work:
  1. a checkpointer  — the paused run has to be saved somewhere
  2. a thread_id     — so resuming knows which paused run to continue
"""

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langchain.tools import tool
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

load_dotenv()


@tool
def send_email(to: str, subject: str, body: str) -> str:
    """Sends an email to a recipient."""
    print(f"    >>> EMAIL ACTUALLY SENT to {to}")
    return f"Email sent to {to} with subject {subject!r}"


@tool
def get_weather(city: str) -> str:
    """Returns the current weather for a city."""
    return f"It is 28 C and sunny in {city}."


agent = create_agent(
    model=ChatGroq(model="openai/gpt-oss-20b"),
    tools=[send_email, get_weather],
    system_prompt="You are an assistant. Use tools when asked.",
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "send_email": True,   # pause and ask before every email
                "get_weather": False,  # harmless, let it run
            },
            description_prefix="Approve this action?",
        )
    ],
    checkpointer=InMemorySaver(),  # required: stores the paused run
)

request = {
    "messages": [
        {
            "role": "user",
            "content": "Email riya@example.com with subject 'Standup' and body 'Moved to 10am'.",
        }
    ]
}


# ---------------------------------------------------------------------------
# Run 1 — approve the email.
# ---------------------------------------------------------------------------
print("=== Run 1: approve ===")
config = {"configurable": {"thread_id": "run-1"}}

result = agent.invoke(request, config)

# The agent stopped instead of finishing. The pending request is in __interrupt__.
interrupt = result["__interrupt__"][0]
action = interrupt.value["action_requests"][0]
print(f"PAUSED -> tool={action['name']} args={action['args']}")

# Resume by passing the decisions back on the SAME thread_id.
result = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config)
print(result["messages"][-1].text)


# ---------------------------------------------------------------------------
# Run 2 — reject it instead. The tool never executes; the model is told why.
# ---------------------------------------------------------------------------
print("\n=== Run 2: reject ===")
config = {"configurable": {"thread_id": "run-2"}}

result = agent.invoke(request, config)
print(f"PAUSED -> tool={result['__interrupt__'][0].value['action_requests'][0]['name']}")

result = agent.invoke(
    Command(
        resume={
            "decisions": [
                {"type": "reject", "message": "Do not email this person without checking first."}
            ]
        }
    ),
    config,
)
print(result["messages"][-1].text)


# ---------------------------------------------------------------------------
# Run 3 — no pause at all, because get_weather is set to False.
# ---------------------------------------------------------------------------
print("\n=== Run 3: auto-approved tool ===")
result = agent.invoke(
    {"messages": [{"role": "user", "content": "What's the weather in Pune?"}]},
    {"configurable": {"thread_id": "run-3"}},
)
print(result["messages"][-1].text)

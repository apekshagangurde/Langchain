"""
Human In The Loop — Simple Working Code
=======================================
The runnable companion to technique 2 in file 5.

The whole idea in four lines:

    1. list the tools that need approval    -> interrupt_on={"send_email": True}
    2. give the agent a checkpointer        -> so a paused run can be saved
    3. invoke with a thread_id              -> so you can find the paused run
    4. invoke again with a decision         -> the agent resumes where it stopped

Steps 2 and 3 are not optional. Without a checkpointer there is nowhere to save
the pause; without a thread_id there is no way to say which pause to resume.
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
def send_email(to: str, subject: str) -> str:
    """Sends an email to a recipient."""
    print("    >>> the email really went out")
    return f"Email sent to {to}"


agent = create_agent(
    model=ChatGroq(model="openai/gpt-oss-20b"),
    tools=[send_email],
    system_prompt="You are an assistant. Use the tools you are given.",
    middleware=[
        HumanInTheLoopMiddleware(
            # True = pause and ask. False = let it run. Tools not listed run freely.
            interrupt_on={"send_email": True}
        )
    ],
    checkpointer=InMemorySaver(),  # step 2: where a paused run is stored
)

QUESTION = {
    "messages": [{"role": "user", "content": "Email riya@example.com with subject 'Standup'."}]
}


# ---------------------------------------------------------------------------
# RUN 1 — approve it.
# ---------------------------------------------------------------------------
print("=== approve ===")
config = {"configurable": {"thread_id": "chat-1"}}  # step 3: names this conversation

result = agent.invoke(QUESTION, config)

# The agent did NOT finish. It stopped and handed back the pending action.
action = result["__interrupt__"][0].value["action_requests"][0]
print(f"  paused before: {action['name']}({action['args']})")

# Step 4: resume on the SAME thread_id, carrying the decision.
result = agent.invoke(Command(resume={"decisions": [{"type": "approve"}]}), config)
print(f"  {result['messages'][-1].text}")


# ---------------------------------------------------------------------------
# RUN 2 — reject it. The tool never runs, and the model is told why.
# A new thread_id, because this is a separate conversation.
# ---------------------------------------------------------------------------
print("\n=== reject ===")
config = {"configurable": {"thread_id": "chat-2"}}

result = agent.invoke(QUESTION, config)
print(f"  paused before: {result['__interrupt__'][0].value['action_requests'][0]['name']}")

result = agent.invoke(
    Command(resume={"decisions": [{"type": "reject", "message": "Check with me first."}]}),
    config,
)
print(f"  {result['messages'][-1].text}")


# ---------------------------------------------------------------------------
# The other two decisions, same shape:
#
#   edit     run it, but with corrected arguments
#     {"type": "edit",
#      "edited_action": {"name": "send_email",
#                        "args": {"to": "team@example.com", "subject": "Standup"}}}
#
#   respond  skip the tool; you supply the result yourself
#     {"type": "respond", "message": "Already sent it manually."}
# ---------------------------------------------------------------------------

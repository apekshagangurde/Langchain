"""
Memory in Deep Agents
=====================

WHAT IS MEMORY?
---------------
Memory is what the agent remembers beyond the current model call. Deep agents
have two kinds, and both are built on the agent's FILE SYSTEM (its backend):

    Short-term memory  -> lasts for ONE conversation (thread)
    Long-term memory   -> lasts ACROSS conversations (threads)


1. SHORT-TERM MEMORY — within one conversation
---------------------------------------------
  - The message history, plus any files the agent writes with the default
    StateBackend (todos, notes, drafts).
  - Lives in the agent's state, so it is gone when the conversation ends.
  - To continue the SAME conversation across several `invoke` calls, give the
    agent a checkpointer and reuse a thread_id:

        agent = create_deep_agent(model=model, checkpointer=InMemorySaver())
        config = {"configurable": {"thread_id": "chat-1"}}
        agent.invoke({"messages": [...]}, config=config)   # turn 1
        agent.invoke({"messages": [...]}, config=config)   # turn 2 remembers turn 1


2. LONG-TERM MEMORY — across conversations
------------------------------------------
  - Files written to a StoreBackend survive after the conversation ends, and a
    brand-new conversation (new thread_id) can read them again.
  - The usual setup is a CompositeBackend: only the `/memories/` folder is
    long-term, everything else stays short-term scratch space.

        backend = CompositeBackend(
            default=StateBackend(),                      # scratch, per conversation
            routes={"/memories/": StoreBackend(          # kept across conversations
                store=store, namespace=lambda _rt: ("memories",))},
        )

  - Then tell the agent in its system prompt: "Save user preferences and
    lessons to /memories/ so you remember them next time."
  - Use a database-backed store (e.g. PostgresStore) in production;
    InMemoryStore is lost when the program stops.


3. AGENTS.md MEMORY — always loaded into the prompt
---------------------------------------------------
  - Pass memory files with `create_deep_agent(memory=["/memories/AGENTS.md"])`.
  - Their FULL text is added to the system prompt every time the agent starts,
    so the agent always knows them without having to read a file.
  - The agent is also told it can update this file with `edit_file` when it
    learns something from the user (a correction, a preference). So it can
    improve itself over time.
  - Keep it short: everything in AGENTS.md costs prompt tokens on every call.


QUICK SUMMARY
-------------
    Type          Where it lives                     How long it lasts
    -----------   --------------------------------   -------------------------
    Short-term    messages + StateBackend files      one conversation (thread)
    Long-term     StoreBackend (e.g. /memories/)     across conversations
    AGENTS.md     memory=[...] -> system prompt      always loaded at start
"""


# ---------------------------------------------------------------------------
# SIMPLE EXAMPLE: short-term + long-term memory in one agent
#   - checkpointer + thread_id  -> short-term (remembers the chat in a thread)
#   - CompositeBackend routing /memories/ to StoreBackend -> long-term
#     (files there survive into a brand-new thread)
# ---------------------------------------------------------------------------
from pathlib import Path

from deepagents import create_deep_agent
from deepagents.backends import CompositeBackend, FilesystemBackend, StateBackend, StoreBackend
from dotenv import load_dotenv
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

load_dotenv()

# Rate limiter keeps us under Groq's free-tier tokens/minute cap.
model = ChatGroq(
    model="openai/gpt-oss-120b",
    rate_limiter=InMemoryRateLimiter(requests_per_second=0.04, check_every_n_seconds=0.5),
)

store = InMemoryStore()  # long-term memory lives here (RAM; use PostgresStore in production)

agent = create_deep_agent(
    model=model,
    checkpointer=InMemorySaver(),  # short-term: saves each thread's messages
    backend=CompositeBackend(
        default=StateBackend(),  # normal files: scratch space for one thread
        routes={"/memories/": StoreBackend(store=store, namespace=lambda _rt: ("memories",))},
    ),
    system_prompt=(
        "You are a personal assistant. Save anything the user wants remembered "
        "long-term to /memories/preferences.md. When asked about the user, check "
        "/memories/ first."
    ),
)


# ---------------------------------------------------------------------------
# SIMPLE EXAMPLE: AGENTS.md memory
# A real AGENTS.md file on disk is loaded into the system prompt at startup,
# so the agent follows it without being told. With FilesystemBackend the agent
# can also update the file with `edit_file`, so what it learns is still there
# next time you run the script.
# ---------------------------------------------------------------------------
MEMORY_DIR = Path(__file__).parent / "agent_memory"
MEMORY_DIR.mkdir(exist_ok=True)
AGENTS_MD = MEMORY_DIR / "AGENTS.md"

if not AGENTS_MD.exists():
    AGENTS_MD.write_text(
        "# About the user\n"
        "- Lives in Pune, India.\n"
        "- Prefers short answers in bullet points.\n"
    )

agents_md_agent = create_deep_agent(
    model=model,
    backend=FilesystemBackend(root_dir=MEMORY_DIR, virtual_mode=True),
    memory=["/AGENTS.md"],  # path inside root_dir; full text goes into the system prompt
)


def ask(question: str, thread_id: str) -> str:
    """Send one message on a thread and return the agent's reply."""
    result = agent.invoke(
        {"messages": [{"role": "user", "content": question}]},
        config={"configurable": {"thread_id": thread_id}},
    )
    return result["messages"][-1].content


if __name__ == "__main__":
    # Thread 1, turn 1: tell the agent something and ask it to remember it.
    print("[thread-1]", ask("My favourite city is Pune. Remember it for the future.", "thread-1"))

    # Thread 1, turn 2: SHORT-TERM memory. Same thread, so it still has the chat history.
    print("[thread-1]", ask("What did I just tell you?", "thread-1"))

    # Thread 2: LONG-TERM memory. New thread, no chat history, but /memories/ survives.
    print("[thread-2]", ask("What is my favourite city?", "thread-2"))

    # What is actually stored long-term.
    print("\nLong-term memory in the store:")
    for item in store.search(("memories",)):
        print(f"--- {item.key} ---")
        print(item.value["content"])

    # AGENTS.md: the agent already knows the user's city and answer style
    # from the file, without being told in the chat.
    print("\n[AGENTS.md]", agents_md_agent.invoke(
        {"messages": [{"role": "user", "content": "Suggest a weekend trip for me."}]}
    )["messages"][-1].content)

    # Teach it something new; it should save this to AGENTS.md with edit_file.
    agents_md_agent.invoke(
        {"messages": [{"role": "user", "content": "Remember that I am vegetarian."}]}
    )
    print("\nAGENTS.md after the agent updated it:")
    print(AGENTS_MD.read_text())

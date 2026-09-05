"""
SummarizationMiddleware
=======================
A long conversation eventually blows past the model's context window.
`SummarizationMiddleware` watches the message history on every `before_model` hook
and, once a threshold is crossed, replaces the older messages with an LLM-written
summary — keeping the most recent messages verbatim.

    [msg1 ... msg40]  ->  [SUMMARY of msg1..msg36] + [msg37 ... msg40]

Two knobs control it:

  trigger = WHEN to summarize
      ("messages", 12)   summarize once the history reaches 12 messages
      ("tokens", 600)    summarize once the history reaches 600 tokens
      ("fraction", 0.8)  summarize at 80% of the model's max input tokens
                         (needs model profile data; Groq models expose it)

  keep    = WHAT to leave untouched after the summary (same three units)
      ("messages", 4)    keep the last 4 messages verbatim
      ("tokens", 500)    keep roughly the last 500 tokens
      ("fraction", 0.3)  keep roughly the last 30% of the context window

You can also pass a dict for AND semantics — {"tokens": 4000, "messages": 10} only
fires when BOTH are met — or a list of dicts for OR semantics.

AI/Tool message pairs are never split across the cut, so tool calls stay valid.
"""

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware
from langchain_groq import ChatGroq

load_dotenv()

model = ChatGroq(model="openai/gpt-oss-20b")


def build_history(turns: int = 8) -> list[dict[str, str]]:
    """Fakes a long conversation so the trigger actually fires in this demo."""
    topics = [
        "Kerala backwaters",
        "Rajasthan forts",
        "Goa beaches",
        "Ladakh road trip",
        "Meghalaya living root bridges",
        "Hampi ruins",
        "Andaman islands",
        "Spiti valley",
    ]
    history: list[dict[str, str]] = []
    for topic in topics[:turns]:
        history.append({"role": "user", "content": f"Tell me one thing about {topic}."})
        history.append(
            {
                "role": "assistant",
                "content": (
                    f"{topic} is a well known destination in India. Travellers usually visit "
                    f"between October and March, when the weather is pleasant and the routes "
                    f"are open. Budget roughly three to four days for {topic}."
                ),
            }
        )
    return history


def run(label: str, middleware: SummarizationMiddleware) -> None:
    agent = create_agent(
        model=model,
        system_prompt="You are a travel assistant. Answer in one short sentence.",
        middleware=[middleware],
    )

    history = build_history()
    history.append({"role": "user", "content": "Which of these did we discuss first?"})

    print(f"\n=== {label} ===")
    print(f"messages sent in : {len(history)}")

    result = agent.invoke({"messages": history})
    kept = result["messages"]

    # After summarization the history is collapsed into a summary + recent messages,
    # so the returned message list is shorter than what we sent in.
    summarized = len(kept) <= len(history)
    print(f"messages after   : {len(kept)}  -> summarization {'ran' if summarized else 'did not run'}")
    print(f"answer           : {kept[-1].text}")


# ---------------------------------------------------------------------------
# 1. MESSAGES trigger — simplest to reason about. Count messages, not tokens.
#    Good default when turns are roughly uniform in size.
# ---------------------------------------------------------------------------
run(
    "trigger=('messages', 12) / keep=('messages', 4)",
    SummarizationMiddleware(
        model=model,
        trigger=("messages", 12),   # summarize once history hits 12 messages
        keep=("messages", 4),       # keep the last 4 messages verbatim
    ),
)

# ---------------------------------------------------------------------------
# 2. TOKENS trigger — an absolute token budget. Use when messages vary wildly in
#    size (a 5-line reply and a 3000-token tool result both count as "1 message").
# ---------------------------------------------------------------------------
run(
    "trigger=('tokens', 600) / keep=('tokens', 300)",
    SummarizationMiddleware(
        model=model,
        trigger=("tokens", 600),    # summarize once history hits ~600 tokens
        keep=("tokens", 300),       # keep roughly the last 300 tokens verbatim
    ),
)

# ---------------------------------------------------------------------------
# 3. FRACTION trigger — a share of the model's own context window. Portable:
#    swap the model and the threshold rescales itself.
#    openai/gpt-oss-20b has a 131,072-token window, so 0.8 would be ~105k tokens.
#    A tiny fraction is used here only so the demo actually triggers.
# ---------------------------------------------------------------------------
run(
    "trigger=('fraction', 0.002) / keep=('fraction', 0.001)",
    SummarizationMiddleware(
        model=model,
        trigger=("fraction", 0.002),  # in production use ~0.8
        keep=("fraction", 0.001),     # in production use ~0.3
    ),
)

# ---------------------------------------------------------------------------
# Bonus: AND / OR conditions
#
#   trigger={"tokens": 4000, "messages": 10}          -> fires when BOTH are met
#   trigger=[{"tokens": 5000}, {"messages": 30}]      -> fires when EITHER is met
# ---------------------------------------------------------------------------

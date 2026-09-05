"""
PIIMiddleware — Working Code
============================
The runnable companion to file 4 (which is the theory).

Part 1 runs the middleware directly on fake messages, so you can see exactly
what each strategy does to each PII type — no model call, no cost.
Part 2 wires it into a real agent, including the tool-results switch that
people most often forget to turn on.
"""

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.agents.middleware import PIIDetectionError, PIIMiddleware
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq

load_dotenv()


# ===========================================================================
# PART 1 — the four strategies, side by side. No agent, no model, no cost.
#
# `before_model` is just a function: hand it a state dict and read what comes
# back. This is also how you unit-test a guardrail.
# ===========================================================================
SAMPLES = {
    "email": "contact riya.sharma@example.com now",
    "credit_card": "card 4111 1111 1111 1111 ok",
    "ip": "server 192.168.1.42 up",
    "mac_address": "mac 00:1A:2B:3C:4D:5E",
    "url": "see https://internal.corp/x?t=1",
}

print("=== PART 1: strategies ===\n")
for pii_type, text in SAMPLES.items():
    print(f"{pii_type}  (original: {text})")
    for strategy in ("redact", "mask", "hash"):
        guard = PIIMiddleware(pii_type, strategy=strategy)
        out = guard.before_model({"messages": [HumanMessage(content=text)]}, None)
        # The hook returns None when nothing matched, or a state update whose
        # message has the SAME id as the original — that is what overwrites it.
        result = out["messages"][-1].text if out else text
        print(f"    {strategy:7} -> {result}")
    print()

# Note what each strategy preserves:
#   redact  nothing survives                     -> [REDACTED_EMAIL]
#   mask    a recognisable fragment survives     -> **** **** **** 1111
#   hash    a STABLE fingerprint survives, so the same value always produces
#           the same hash and repeats stay correlatable without being readable


# ===========================================================================
# The fourth strategy: BLOCK. It does not transform anything — it raises,
# which is the only strategy that gives a hard guarantee.
# ===========================================================================
print("=== block strategy ===")
blocker = PIIMiddleware("api_key", detector=r"sk-[A-Za-z0-9]{8,}", strategy="block")
try:
    blocker.before_model(
        {"messages": [HumanMessage(content="my key is sk-abcd1234efgh5678")]}, None
    )
    print("  no PII found")
except PIIDetectionError as exc:
    print(f"  raised PIIDetectionError: {exc}")
print()


# ===========================================================================
# PART 2 — in a real agent.
#
# The three switches are independent, so each rule below guards a different
# point in the run.
# ===========================================================================
@tool
def lookup_customer(customer_id: str) -> str:
    """Looks up a customer record by id."""
    # A realistic tool result: real customer data, straight from a database.
    # Without apply_to_tool_results this lands in the context untouched and is
    # resent on every following turn.
    return (
        f"Customer {customer_id}: Riya Sharma, "
        "email riya.sharma@example.com, card 4111 1111 1111 1111, "
        "last login from 192.168.1.42"
    )


agent = create_agent(
    model=ChatGroq(model="openai/gpt-oss-20b"),
    tools=[lookup_customer],
    system_prompt="You are a support assistant. Answer in one short sentence.",
    middleware=[
        # Each instance handles ONE type with ONE strategy, so real policies stack.
        #
        # Email: redact everywhere. The model never needs the actual address.
        PIIMiddleware(
            "email",
            strategy="redact",
            apply_to_input=True,          # before the model sees the user message
            apply_to_tool_results=True,   # before the model sees the DB record
            apply_to_output=True,         # before the user sees the reply
        ),
        # Card: mask, not redact — support agents need "the card ending 1111"
        # to confirm which card is meant.
        PIIMiddleware("credit_card", strategy="mask", apply_to_tool_results=True),
        # IP: hash. The value stays correlatable across the conversation
        # (same IP -> same hash) without ever being readable.
        PIIMiddleware("ip", strategy="hash", apply_to_tool_results=True),
        # Custom type. A detector regex plus a name of your choosing behaves
        # exactly like a built-in type. Blocking here because an API key in a
        # chat is an incident, not something to tidy up.
        PIIMiddleware("api_key", detector=r"sk-[A-Za-z0-9]{8,}", strategy="block"),
    ],
)

print("=== PART 2: inside an agent ===\n")

result = agent.invoke(
    {"messages": [{"role": "user", "content": "Look up customer C-1042 and summarise it."}]}
)

print("what the model saw after the tool returned:")
for msg in result["messages"]:
    if msg.type == "tool":
        print(f"    {msg.text}")

print(f"\nfinal answer: {result['messages'][-1].text}")

# The block rule fires on the whole run, so this one never reaches the model.
print("\n=== block rule in the agent ===")
try:
    agent.invoke({"messages": [{"role": "user", "content": "is sk-abcd1234efgh5678 valid?"}]})
except PIIDetectionError as exc:
    print(f"  run stopped: {exc}")

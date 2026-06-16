"""
RunnablePassthrough — Passing Input Through Unchanged
===========================================================

What is RunnablePassthrough?
  A Runnable that does NOTHING to its input — it just hands it back exactly
  as it received it. Think of it as a mirror: whatever goes in, the same
  thing comes out.

Why would you need a step that does nothing?
  Because chains transform data as it flows through them, and once a step
  changes the data, the ORIGINAL input is gone — unless something kept a
  copy of it. RunnablePassthrough is that "keep a copy" step.

  This matters most inside RunnableParallel, where you often want:
    - one branch to PROCESS the input (e.g. summarize it)
    - another branch to PRESERVE the original input untouched
  so the final result has both.

How is it created?
    RunnablePassthrough()

Data flow (this is the whole idea):

    input  ──────────────────────►  same input, unchanged
           RunnablePassthrough()

  Inside a RunnableParallel:

                     {"topic": "Python"}
                            │
            ┌───────────────┴───────────────┐
            │                                │
      RunnablePassthrough()              notes_chain
            │                                │
            ▼                                ▼
    {"topic": "Python"}              "- point 1\\n- point 2"
            │                                │
            └───────────────┬────────────────┘
                             ▼
        {"original": {"topic": "Python"}, "notes": "..."}

Rules to remember:
  1. RunnablePassthrough never looks at or modifies the input.
  2. On its own, .invoke(x) just returns x — not very useful by itself.
  3. It becomes useful inside RunnableParallel, where it sits alongside
     other branches that DO transform the input.
  4. RunnablePassthrough.assign(...) is a variant that keeps the original
     input AND adds new computed keys to it — shown below.
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")
parser = StrOutputParser()


# ── STEP 1: see RunnablePassthrough on its own ────────────────────────────────
# By itself it just echoes back whatever you give it. Not impressive alone,
# but this is the entire behaviour — no surprises.

print("=" * 60)
print("STEP 1 — RunnablePassthrough on its own")
print("=" * 60)

passthrough = RunnablePassthrough()

echoed = passthrough.invoke({"topic": "Python lists"})
print("Input : {'topic': 'Python lists'}")
print(f"Output: {echoed}")
print(f"Same object content: {echoed == {'topic': 'Python lists'}}")
print()


# ── STEP 2: build a chain that transforms the input ──────────────────────────
# Once this chain runs, the original {"topic": ...} dict is gone — all that's
# left is the generated notes string. We'll fix that with RunnablePassthrough.

notes_prompt = ChatPromptTemplate.from_template(
    "Write short study notes (2 bullet points) about {topic}."
)
notes_chain = notes_prompt | llm | parser


# ── METHOD A: keep the original input next to the transformed result ────────

print("=" * 60)
print("METHOD A — RunnablePassthrough alongside a transforming chain")
print("=" * 60)

parallel_chain = RunnableParallel(
    original=RunnablePassthrough(),   # keeps {"topic": "Python lists"} as-is
    notes=notes_chain,                # transforms input into generated notes
)

result = parallel_chain.invoke({"topic": "Python lists"})

print(f"Result type     : {type(result)}")        # dict
print(f"original (as-is): {result['original']}")  # {"topic": "Python lists"}
print(f"notes (generated): {result['notes']}")
print()


# ── METHOD B: RunnablePassthrough.assign() — keep input AND add new keys ────
# .assign() is a convenience variant: it keeps every key from the original
# input dict, and ADDS whatever new keys you give it — no need for a separate
# "original" key, the input keys are merged straight into the output dict.

print("=" * 60)
print("METHOD B — RunnablePassthrough.assign() merges new keys into input")
print("=" * 60)

assign_chain = RunnablePassthrough.assign(notes=notes_chain)

result_b = assign_chain.invoke({"topic": "Python lists"})

print(f"Result type: {type(result_b)}")   # dict
print(f"Keys       : {list(result_b.keys())}")   # ['topic', 'notes']
print(f"topic (kept from input): {result_b['topic']}")
print(f"notes (added by assign): {result_b['notes']}")

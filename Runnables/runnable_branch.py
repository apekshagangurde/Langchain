"""
RunnableBranch — if/elif/else Logic Inside a Chain
========================================================

What is RunnableBranch?
  A Runnable that picks ONE chain to run out of several options, based on
  conditions you define. It behaves exactly like an if/elif/else statement,
  except the branches are chains instead of plain code blocks.

How is it created?
    RunnableBranch(
        (condition_fn_1, chain_if_true_1),
        (condition_fn_2, chain_if_true_2),
        default_chain,        ← runs if NONE of the conditions matched
    )

  - Each condition_fn receives the chain's input and returns True/False.
  - Conditions are checked IN ORDER, top to bottom.
  - The FIRST condition that returns True has its chain run — the rest are
    skipped entirely (not run "just in case").
  - If no condition matches, the final default_chain runs.

Why use it?
  Sometimes a single prompt can't handle every case well. For example, you
  might want a different prompt style for Python questions vs Java questions
  vs everything else. RunnableBranch lets you route the input to the right
  chain automatically, inside the chain itself.

Data flow (this is the whole idea):

                       input
                         │
              ┌──────────┼──────────┐
              ▼          ▼          ▼
        condition_1  condition_2  (none matched)
         True?         True?
           │             │
           ▼             ▼
        chain_1       chain_2     default_chain
           │             │             │
           └─────────────┴─────────────┘
                         ▼
                      output

Rules to remember:
  1. Conditions are checked top to bottom — order matters.
  2. Only ONE branch ever runs per call — never more, never zero (the
     default guarantees something always runs).
  3. The default branch is REQUIRED — always include one as the last
     argument, with no condition attached to it.
  4. Each branch is a full chain — it can be as simple as a single prompt
     or as complex as prompt | llm | parser | RunnableLambda(...).
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableBranch
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")
parser = StrOutputParser()


# ── STEP 1: build one chain per category ──────────────────────────────────────
# Each of these is a normal RunnableSequence — nothing special yet.

python_prompt = ChatPromptTemplate.from_template(
    "Answer this Python question like a Python expert: {question}"
)
python_chain = python_prompt | llm | parser

java_prompt = ChatPromptTemplate.from_template(
    "Answer this Java question like a Java expert: {question}"
)
java_chain = java_prompt | llm | parser

general_prompt = ChatPromptTemplate.from_template(
    "Answer this general programming question: {question}"
)
general_chain = general_prompt | llm | parser


# ── METHOD A: RunnableBranch with condition functions ─────────────────────────
# Conditions receive the SAME input dict the branch will eventually run with,
# so they can inspect it however they like (here, just checking the topic).

print("=" * 60)
print("METHOD A — routing input to the right chain with RunnableBranch")
print("=" * 60)

branch_chain = RunnableBranch(
    (lambda x: "python" in x["question"].lower(), python_chain),
    (lambda x: "java" in x["question"].lower(), java_chain),
    general_chain,   # default — runs if neither condition matched
)

print(f"Type of branch_chain: {type(branch_chain)}")   # RunnableBranch

result_python = branch_chain.invoke({"question": "What is a Python decorator?"})
print(f"Python question  → {result_python}")
print()

result_java = branch_chain.invoke({"question": "What is a Java interface?"})
print(f"Java question    → {result_java}")
print()

result_default = branch_chain.invoke({"question": "What is Big-O notation?"})
print(f"Unmatched topic  → {result_default}")
print()


# ── BONUS: see which branch fires, without calling the LLM ──────────────────
# Conditions are plain functions, so you can test the routing logic on its
# own — useful for confirming the right branch is picked before paying for
# an LLM call.

print("=" * 60)
print("BONUS — testing the routing logic in isolation")
print("=" * 60)

is_python = lambda x: "python" in x["question"].lower()
is_java = lambda x: "java" in x["question"].lower()

for q in ["Explain Python generators", "Explain Java generics", "Explain recursion"]:
    if is_python({"question": q}):
        route = "python_chain"
    elif is_java({"question": q}):
        route = "java_chain"
    else:
        route = "general_chain (default)"
    print(f"'{q}' → {route}")

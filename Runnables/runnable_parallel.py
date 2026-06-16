"""
RunnableParallel — Running Multiple Chains at the Same Time
===============================================================

What is RunnableParallel?
  A Runnable that takes ONE input and sends a COPY of it to MULTIPLE chains
  at once. Each chain runs independently (in parallel threads), and the
  results are collected into a single dict — one key per chain.

How is it created?
  You pass named chains as keyword arguments:

    chain = RunnableParallel(
        key1 = chain1,
        key2 = chain2,
    )

  Every branch (chain1, chain2, ...) receives the EXACT SAME input.
  The final output is a dict: {"key1": result1, "key2": result2}.

Why use it?
  Without RunnableParallel you would have to call each chain one after
  another and wait for each to finish before starting the next. With
  RunnableParallel, all branches start at roughly the same time, so the
  total time is closer to the SLOWEST branch, not the SUM of all branches.

Data flow (this is the whole idea):

                     input
                       │
            ┌──────────┴──────────┐
            │                     │
         chain1                chain2     ← both run at the same time
            │                     │
            └──────────┬──────────┘
                        ▼
            {"key1": result1, "key2": result2}

Rules to remember:
  1. Every branch is independent — branches CANNOT see each other's output.
  2. Every branch gets the SAME input (the original input to the parallel
     block), not the output of another branch.
  3. The output is always a dict, with one entry per named branch.
  4. RunnablePassthrough() is often used as one of the branches when you
     want to keep the original input alongside the other results.
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")
parser = StrOutputParser()


# ── STEP 1: build two independent chains ─────────────────────────────────────
# Both chains will receive the SAME input ({"topic": "..."}) once they are
# placed inside a RunnableParallel — neither chain knows the other exists.

notes_prompt = ChatPromptTemplate.from_template(
    "Write short study notes (3 bullet points) about {topic}."
)
notes_chain = notes_prompt | llm | parser

quiz_prompt = ChatPromptTemplate.from_template(
    "Write 2 quiz questions (no answers) about {topic}."
)
quiz_chain = quiz_prompt | llm | parser


# ── METHOD A: the normal way — RunnableParallel(key=chain, ...) ──────────────

print("=" * 60)
print("METHOD A — notes and quiz generated in parallel")
print("=" * 60)

parallel_chain = RunnableParallel(
    notes=notes_chain,
    quiz=quiz_chain,
)

print(f"Type of parallel_chain: {type(parallel_chain)}")   # RunnableParallel

result = parallel_chain.invoke({"topic": "Python lists"})

print(f"Result type: {type(result)}")   # dict
print(f"Notes:\n{result['notes']}")
print(f"Quiz:\n{result['quiz']}")
print()


# ── METHOD B: same thing using a plain dict (LangChain auto-converts it) ────
# A plain Python dict of Runnables gets automatically treated as a
# RunnableParallel when placed inside a chain with |. Shown here only to
# prove RunnableParallel(...) and {} are interchangeable in this position.

print("=" * 60)
print("METHOD B — same result, built with a plain dict")
print("=" * 60)

dict_chain = {
    "notes": notes_chain,
    "quiz": quiz_chain,
}

result_b = RunnableParallel(dict_chain).invoke({"topic": "Python lists"})
print(f"Result type: {type(result_b)}")   # dict
print(f"Keys: {list(result_b.keys())}")
print()


# ── BONUS: RunnablePassthrough to keep the original input too ───────────────
# Add a third branch that just returns the input unchanged, so the final
# output also contains the original topic alongside notes and quiz.

print("=" * 60)
print("BONUS — keeping the original input with RunnablePassthrough")
print("=" * 60)

full_chain = RunnableParallel(
    original=RunnablePassthrough(),
    notes=notes_chain,
    quiz=quiz_chain,
)

final_result = full_chain.invoke({"topic": "Python lists"})

print(f"Original input preserved: {final_result['original']}")
print(f"Notes:\n{final_result['notes']}")
print(f"Quiz:\n{final_result['quiz']}")

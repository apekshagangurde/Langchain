"""
RunnableSequence — Chaining Steps One After Another
=======================================================

What is RunnableSequence?
  A Runnable that connects multiple steps so the OUTPUT of one step becomes
  the INPUT of the next step, in order. It is the most basic and most used
  Runnable in LangChain — almost every chain you build is a RunnableSequence
  under the hood.

How is it created?
  You almost never write RunnableSequence(...) yourself. Instead, you use the
  pipe operator | between Runnables, and LangChain creates the RunnableSequence
  for you automatically.

    chain = prompt | model | parser

  is exactly the same as writing:

    chain = RunnableSequence(prompt, model, parser)

Why does this matter?
  Because | is just sugar — understanding that it builds a RunnableSequence
  explains WHY data flows the way it does: strictly left to right, one step
  feeding the next, with no branching and no parallel work.

Data flow (this is the whole idea):

    input
      │
      ▼
   step 1  →  output of step 1
      │
      ▼
   step 2  →  output of step 2  (this is the input to step 2)
      │
      ▼
   step 3  →  final output

Rules to remember:
  1. Every step must be a Runnable (have .invoke()).
  2. The output type of step N must match the input type step N+1 expects.
     e.g. a prompt outputs messages → a chat model expects messages. OK.
          a chat model outputs an AIMessage → a parser expects an AIMessage. OK.
  3. .invoke() on the whole sequence just calls .invoke() on each step in turn,
     passing the result along — that's it, no magic.
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")


# ── STEP 1: build the individual Runnables ───────────────────────────────────
# Each of these on its own already has .invoke() — that makes it a Runnable.

prompt = ChatPromptTemplate.from_template(
    "Explain the topic {topic} in 2 simple lines for a complete beginner."
)
parser = StrOutputParser()


# ── METHOD A: the normal way — using the | operator ──────────────────────────
# This is what you will use 99% of the time. LangChain builds the
# RunnableSequence behind the scenes when it sees |.

print("=" * 60)
print("METHOD A — built using the | operator")
print("=" * 60)

pipe_chain = prompt | llm | parser

print(f"Type of pipe_chain: {type(pipe_chain)}")   # RunnableSequence

result_a = pipe_chain.invoke({"topic": "recursion"})
print(f"Result: {result_a}")
print()


# ── METHOD B: the explicit way — calling RunnableSequence() directly ─────────
# This produces the SAME chain as Method A. Shown here only to prove that |
# is just a shortcut for RunnableSequence(step1, step2, step3, ...).

print("=" * 60)
print("METHOD B — built explicitly with RunnableSequence(...)")
print("=" * 60)

explicit_chain = RunnableSequence(prompt, llm, parser)

print(f"Type of explicit_chain: {type(explicit_chain)}")   # RunnableSequence

result_b = explicit_chain.invoke({"topic": "recursion"})
print(f"Result: {result_b}")
print()

print(f"Both methods give the same kind of chain: {type(pipe_chain) is type(explicit_chain)}")


# ── BONUS: each step's output becomes the next step's input ─────────────────
# Run each step by hand to SEE the data change shape as it moves through
# the sequence — this is exactly what RunnableSequence automates for you.

print("=" * 60)
print("BONUS — watching data change shape at every step")
print("=" * 60)

step1_output = prompt.invoke({"topic": "recursion"})
print(f"After prompt → type: {type(step1_output).__name__}")   # ChatPromptValue

step2_output = llm.invoke(step1_output)
print(f"After llm    → type: {type(step2_output).__name__}")   # AIMessage

step3_output = parser.invoke(step2_output)
print(f"After parser → type: {type(step3_output).__name__}")   # str
print(f"Final text   : {step3_output}")

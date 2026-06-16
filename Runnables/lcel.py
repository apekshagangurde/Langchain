"""
LCEL — LangChain Expression Language
==========================================

What is LCEL?
  LCEL is the | (pipe) syntax used to build chains in LangChain. It is NOT
  a separate Runnable type — it is the LANGUAGE that connects Runnables
  together. Every primitive Runnable you've seen (RunnableSequence,
  RunnableParallel, RunnablePassthrough, RunnableLambda, RunnableBranch) is
  something LCEL lets you build with simple, readable syntax instead of
  verbose constructor calls.

Why does LCEL exist?
  Without it, building a chain means nesting constructors:

    RunnableSequence(
        prompt,
        RunnableParallel(notes=notes_chain, quiz=quiz_chain),
        llm,
        parser,
    )

  With LCEL, the same chain reads left to right, like a pipeline:

    chain = prompt | {"notes": notes_chain, "quiz": quiz_chain} | llm | parser

  LCEL is just operator overloading: every Runnable implements __or__, so
  writing `a | b` actually calls a.__or__(b), which builds a RunnableSequence
  (or merges into an existing one) behind the scenes.

What LCEL gives you, beyond just convenience:
  1. Automatic parallelism   — every step exposes both .invoke() (sync) and
                                 .ainvoke() (async) without you writing it.
  2. Streaming for free      — .stream() yields output piece by piece, even
                                 through multiple chained steps.
  3. Batching for free       — .batch([...]) runs the same chain over many
                                 inputs, in parallel, with one call.
  4. Consistent interface    — every Runnable in a chain, no matter how
                                 different internally, exposes the SAME
                                 methods: invoke / ainvoke / stream / batch.

LCEL building blocks recap (all pieced together with |):

  ┌───────────────────────┬────────────────────────────────────────────┐
  │ Syntax                │ What it builds                             │
  ├───────────────────────┼────────────────────────────────────────────┤
  │ a | b | c              │ RunnableSequence(a, b, c)                  │
  │ {"k1": a, "k2": b}     │ RunnableParallel(k1=a, k2=b)  (auto-cast)  │
  │ RunnablePassthrough()  │ pass input through unchanged                │
  │ lambda x: ...          │ RunnableLambda(...)           (auto-cast)  │
  │ RunnableBranch(...)    │ if/elif/else routing between chains        │
  └───────────────────────┴────────────────────────────────────────────┘
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableSequence
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")
parser = StrOutputParser()


# ── STEP 1: the building blocks ──────────────────────────────────────────────

notes_prompt = ChatPromptTemplate.from_template(
    "Write 2 short bullet-point notes about {topic}."
)
notes_chain = notes_prompt | llm | parser

quiz_prompt = ChatPromptTemplate.from_template(
    "Write 1 quiz question (no answer) about {topic}."
)
quiz_chain = quiz_prompt | llm | parser


# ── METHOD A: pure LCEL — read it left to right like a pipeline ─────────────
# Notice {"notes": ..., "quiz": ...} is a plain dict — LCEL auto-casts it
# into a RunnableParallel because it appears next to |.

print("=" * 60)
print("METHOD A — one LCEL pipeline: parallel branches, then a summary step")
print("=" * 60)

summary_prompt = ChatPromptTemplate.from_template(
    "Combine these into one short paragraph:\nNotes: {notes}\nQuiz: {quiz}"
)

lcel_chain = (
    {
        "notes": notes_chain,
        "quiz": quiz_chain,
    }
    | summary_prompt
    | llm
    | parser
)

print(f"Type of lcel_chain: {type(lcel_chain)}")   # RunnableSequence

result = lcel_chain.invoke({"topic": "Python dictionaries"})
print(f"Result:\n{result}")
print()


# ── METHOD B: the SAME chain, written the verbose way (no LCEL) ─────────────
# Shown only to prove LCEL is sugar — this does exactly what Method A does,
# just spelled out longhand with explicit constructors.

print("=" * 60)
print("METHOD B — the same chain built without | syntax")
print("=" * 60)

verbose_chain = RunnableSequence(
    RunnableParallel(notes=notes_chain, quiz=quiz_chain),
    summary_prompt,
    llm,
    parser,
)

result_b = verbose_chain.invoke({"topic": "Python dictionaries"})
print(f"Result:\n{result_b}")
print()


# ── BONUS: LCEL gives you streaming and batching for free ──────────────────
# These methods exist on ANY chain built with |, no extra code needed.

print("=" * 60)
print("BONUS — same chain, used three different LCEL-provided ways")
print("=" * 60)

simple_chain = notes_prompt | llm | parser

print("invoke() — single call, single result:")
print(simple_chain.invoke({"topic": "Python tuples"}))
print()

print("stream() — same chain, yields pieces as they arrive:")
for chunk in simple_chain.stream({"topic": "Python sets"}):
    print(chunk, end="", flush=True)
print("\n")

print("batch() — same chain, runs multiple inputs in parallel:")
batch_results = simple_chain.batch(
    [{"topic": "Python strings"}, {"topic": "Python loops"}]
)
for i, r in enumerate(batch_results, start=1):
    print(f"Result {i}: {r}")

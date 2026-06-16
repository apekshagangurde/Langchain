"""
RunnableLambda — Plugging a Plain Python Function into a Chain
====================================================================

What is RunnableLambda?
  A wrapper that turns an ordinary Python function into a Runnable, so it
  can be used with the | operator just like a prompt, model, or parser.

Why do you need it?
  The | operator only works between Runnables (objects with .invoke()).
  A plain Python function like `def shout(text): return text.upper()` does
  NOT have .invoke() — so you can't pipe it directly. RunnableLambda fixes
  that by wrapping the function so it behaves like any other chain step.

How is it created?
    RunnableLambda(my_function)

  Once wrapped, calling .invoke(x) on it just calls my_function(x) for you.

Shortcut:
  LangChain auto-wraps a bare lambda when it sees one next to | in a chain,
  so you often don't even need to write RunnableLambda explicitly:

    chain = prompt | llm | parser | (lambda x: x.upper())

  is the same as:

    chain = prompt | llm | parser | RunnableLambda(lambda x: x.upper())

Data flow (this is the whole idea):

    input  →  your_function(input)  →  output
                      │
              RunnableLambda just
              calls this for you

Rules to remember:
  1. The function takes ONE argument (the output of the previous step) and
     returns ONE value (passed to the next step).
  2. Use RunnableLambda for ANY custom logic that prompts/models/parsers
     don't already cover — cleaning text, reshaping a dict, simple math, etc.
  3. A plain `lambda x: ...` inline is fine for short logic; use a named
     function + RunnableLambda(fn) when the logic needs a name or is longer.
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")
parser = StrOutputParser()


# ── STEP 1: a plain Python function — NOT a Runnable on its own ──────────────
# This function has no .invoke() method, so prompt | llm | parser | shout
# would fail without wrapping it first.

def shout(text: str) -> str:
    return text.upper() + "!!!"


# ── METHOD A: wrap it explicitly with RunnableLambda ─────────────────────────

print("=" * 60)
print("METHOD A — RunnableLambda(shout) used explicitly in a chain")
print("=" * 60)

joke_prompt = ChatPromptTemplate.from_template("Tell me a one-line joke about {topic}.")

explicit_chain = joke_prompt | llm | parser | RunnableLambda(shout)

print(f"Type of wrapped step: {type(RunnableLambda(shout))}")   # RunnableLambda

result_a = explicit_chain.invoke({"topic": "cats"})
print(f"Result: {result_a}")
print()


# ── METHOD B: the shortcut — a bare lambda, auto-wrapped by LangChain ───────
# Same effect as Method A, just shorter. Useful for small one-off logic.

print("=" * 60)
print("METHOD B — bare lambda, auto-wrapped when piped with |")
print("=" * 60)

shortcut_chain = joke_prompt | llm | parser | (lambda text: text.upper() + "!!!")

result_b = shortcut_chain.invoke({"topic": "dogs"})
print(f"Result: {result_b}")
print()


# ── BONUS: reshaping a dict between steps ────────────────────────────────────
# RunnableLambda isn't just for strings — it's commonly used to pick out or
# rename fields from a dict before passing them to the next prompt.

print("=" * 60)
print("BONUS — using RunnableLambda to reshape data between steps")
print("=" * 60)


def extract_word_count(text: str) -> dict:
    return {"joke": text, "word_count": len(text.split())}


reshape_chain = joke_prompt | llm | parser | RunnableLambda(extract_word_count)

result_c = reshape_chain.invoke({"topic": "robots"})
print(f"Result type: {type(result_c)}")   # dict
print(f"Joke       : {result_c['joke']}")
print(f"Word count : {result_c['word_count']}")

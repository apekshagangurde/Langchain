# ==============================================================
# RunnableLambda and RunnablePassthrough — DEEP DIVE
# ==============================================================
#
# ── RunnableLambda ──────────────────────────────────────────
#
# PROBLEM:
#   Chains connect Runnables. But what if you want to run a
#   plain Python function inside a chain?
#   Normal functions are NOT Runnables.
#
# SOLUTION: RunnableLambda
#   Wraps any Python function and makes it a Runnable.
#   Now you can plug it into a chain with |
#
# SYNTAX:
#   RunnableLambda(my_function)
#   OR the shortcut: just use a lambda directly after a |
#
# EXAMPLE:
#   chain = prompt | model | parser | RunnableLambda(make_uppercase)
#
# ── RunnablePassthrough ─────────────────────────────────────
#
# PROBLEM:
#   When a chain runs, the original input gets replaced by
#   each step's output. You can't access the original input later.
#
# SOLUTION: RunnablePassthrough
#   TWO uses:
#   1. RunnablePassthrough()          → pass input through unchanged
#   2. RunnablePassthrough.assign(k=chain) → keep input AND add new key
#
# ANALOGY for assign():
#   Input = {"name": "Apeksha"}
#   After assign(greeting=chain):
#   Output = {"name": "Apeksha", "greeting": "Hello Apeksha!"}
#   ← original key is kept, new key is added
#
# ==============================================================

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()
model = ChatGroq(model="llama-3.1-8b-instant")
parser = StrOutputParser()


# ==============================================================
# RUNNABLELAMBDA — Basic
# ==============================================================
print("=" * 55)
print("RunnableLambda — basic transformation")
print("=" * 55)

# A plain Python function
def make_uppercase(text: str) -> str:
    return text.upper()

def add_border(text: str) -> str:
    line = "=" * 40
    return f"{line}\n{text}\n{line}"

chain = (
    ChatPromptTemplate.from_messages([("human", "What is {topic}? One sentence.")])
    | model
    | parser
    | RunnableLambda(make_uppercase)   # transform output
    | RunnableLambda(add_border)       # transform again
)

print(chain.invoke({"topic": "deep learning"}))


# ==============================================================
# RUNNABLELAMBDA — Transform dict shape for next step
# ==============================================================
print("\n" + "=" * 55)
print("RunnableLambda — reshape dict between chains")
print("=" * 55)
#
# VERY COMMON use case:
#   Chain 1 returns a string.
#   Chain 2 prompt expects {"summary": "..."}.
#   You need to reshape: string → {"summary": string}

chain1 = (
    ChatPromptTemplate.from_messages([
        ("human", "Write a 50-word paragraph about {topic}.")
    ])
    | model | parser
)

chain2 = (
    ChatPromptTemplate.from_messages([
        ("human", "How many words are approximately in this text?\n\n{text}")
    ])
    | model | parser
)

# Bridge function: reshape output of chain1 for chain2
def wrap_as_text(s: str) -> dict:
    return {"text": s}

full = chain1 | RunnableLambda(wrap_as_text) | chain2
print(full.invoke({"topic": "the solar system"}))


# ==============================================================
# RUNNABLELAMBDA — Add logging/debugging to a chain
# ==============================================================
print("\n" + "=" * 55)
print("RunnableLambda — debug logger inside chain")
print("=" * 55)

def log_and_pass(data):
    print(f"  [DEBUG] Data flowing through: {str(data)[:80]}...")
    return data   # pass unchanged

debug_chain = (
    ChatPromptTemplate.from_messages([("human", "Name 3 planets.")])
    | RunnableLambda(log_and_pass)   # log after prompt step
    | model
    | RunnableLambda(log_and_pass)   # log after model step
    | parser
    | RunnableLambda(log_and_pass)   # log after parser step
)

result = debug_chain.invoke({})
print("\nFinal:", result)


# ==============================================================
# RUNNABLEPASSTHROUGH — Pass input unchanged
# ==============================================================
print("\n" + "=" * 55)
print("RunnablePassthrough — pass input unchanged")
print("=" * 55)

# When a chain step is RunnablePassthrough(), it just
# forwards whatever it received to the next step.
# Useful when you want to "skip" transformation.

identity_chain = (
    RunnablePassthrough()   # does nothing, passes {"topic": "..."} through
    | ChatPromptTemplate.from_messages([("human", "Define {topic} briefly.")])
    | model
    | parser
)

print(identity_chain.invoke({"topic": "API"}))


# ==============================================================
# RUNNABLEPASSTHROUGH.assign() — Keep input, ADD new key
# ==============================================================
print("\n" + "=" * 55)
print("RunnablePassthrough.assign() — extend the dict")
print("=" * 55)
#
# Input:  {"question": "What is Python?"}
# After assign(answer=answer_chain):
# Output: {"question": "What is Python?", "answer": "Python is..."}
#
# Now BOTH question and answer are available in the next step!

answer_chain = (
    ChatPromptTemplate.from_messages([("human", "{question}")])
    | model | parser
)

final_chain = (
    RunnablePassthrough.assign(answer=answer_chain)
    | ChatPromptTemplate.from_messages([
        ("human",
         "Question: {question}\n"
         "Answer: {answer}\n\n"
         "Is this answer correct and complete? Reply Yes/No and why.")
    ])
    | model | parser
)

print(final_chain.invoke({"question": "What is the speed of light?"}))


# ==============================================================
# COMBINED — Lambda + Passthrough together
# ==============================================================
print("\n" + "=" * 55)
print("COMBINED: assign + lambda together")
print("=" * 55)

def count_words(text: str) -> int:
    return len(text.split())

pipeline = (
    RunnablePassthrough.assign(
        answer     = answer_chain,
        word_count = RunnableLambda(lambda d: count_words(d["question"]))
    )
    | RunnableLambda(lambda d: (
        f"Question ({d['word_count']} words): {d['question']}\n"
        f"Answer: {d['answer']}"
    ))
)

print(pipeline.invoke({"question": "What are neural networks used for in practice?"}))

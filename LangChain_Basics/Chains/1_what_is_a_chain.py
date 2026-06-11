# ==============================================================
# WHAT IS A CHAIN IN LANGCHAIN?
# ==============================================================
#
# SIMPLE DEFINITION:
#   A Chain is a sequence of steps where the OUTPUT of one step
#   becomes the INPUT of the next step.
#
# REAL LIFE ANALOGY — Assembly Line in a factory:
#
#   Raw material → Machine 1 → Machine 2 → Machine 3 → Final Product
#
#   In LangChain:
#   User Input → Prompt → LLM Model → Output Parser → Final Answer
#
# WITHOUT CHAINS (old way — manual, messy):
#
#   step1 = prompt.format(topic="Python")      # format the prompt
#   step2 = model.invoke(step1)                # call the model
#   step3 = parser.parse(step2)                # parse the output
#   final = step3
#
#   Problem: 3 separate lines, easy to make mistakes, hard to reuse
#
# WITH CHAINS (new way — clean, powerful):
#
#   chain = prompt | model | parser
#   final = chain.invoke({"topic": "Python"})
#
#   The | symbol is called "pipe" — just like Linux command pipe
#   It connects steps together.
#
# THE | PIPE OPERATOR:
#   prompt | model | parser
#     ↑         ↑       ↑
#   Step 1   Step 2   Step 3
#
#   Step 1 output → feeds into Step 2 input
#   Step 2 output → feeds into Step 3 input
#   Step 3 output → your final result
#
# This system is called LCEL = LangChain Expression Language
#
# EVERY STEP IS A "RUNNABLE":
#   A Runnable is anything that has a .invoke() method.
#   Prompt    → Runnable ✓
#   Model     → Runnable ✓
#   Parser    → Runnable ✓
#   Your own function (wrapped) → Runnable ✓
#   So you can connect ANYTHING with |
#
# KEY METHODS of a chain:
#   chain.invoke(input)         → run once, get result
#   chain.batch([i1, i2, i3])   → run on a list, get list of results
#   chain.stream(input)         → get output word by word (streaming)
# ==============================================================

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()
model = ChatGroq(model="llama-3.1-8b-instant")

# ==============================================================
# STEP 1 — Without chain (manual, old way)
# ==============================================================
print("=" * 55)
print("WITHOUT CHAIN (manual steps)")
print("=" * 55)

prompt = ChatPromptTemplate.from_messages([
    ("human", "What is {topic}? Answer in 1 sentence.")
])

# Step 1: format prompt manually
messages = prompt.format_messages(topic="Python")

# Step 2: call model manually
response = model.invoke(messages)

# Step 3: extract text manually
text = response.content

print(text)


# ==============================================================
# STEP 2 — With chain (clean, new way)
# ==============================================================
print("\n" + "=" * 55)
print("WITH CHAIN (pipe | operator)")
print("=" * 55)

chain = prompt | model | StrOutputParser()

# One line does everything
result = chain.invoke({"topic": "Python"})
print(result)

# Both produce the SAME result. Chain is just cleaner!


# ==============================================================
# STEP 3 — invoke vs batch vs stream
# ==============================================================

print("\n" + "=" * 55)
print("invoke() — single input")
print("=" * 55)
r = chain.invoke({"topic": "JavaScript"})
print(r)

print("\n" + "=" * 55)
print("batch() — multiple inputs at once")
print("=" * 55)
results = chain.batch([
    {"topic": "AI"},
    {"topic": "Blockchain"},
    {"topic": "Cloud computing"},
])
for res in results:
    print("-", res)

print("\n" + "=" * 55)
print("stream() — word by word output")
print("=" * 55)
print("Answer: ", end="", flush=True)
for chunk in chain.stream({"topic": "Machine Learning"}):
    print(chunk, end="", flush=True)
print()

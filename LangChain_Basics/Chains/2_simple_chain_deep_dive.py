# ==============================================================
# SIMPLE CHAIN — DEEP DIVE
# ==============================================================
#
# A simple chain has exactly 3 steps:
#
#   ┌──────────┐    ┌───────┐    ┌────────┐
#   │  PROMPT  │ →  │ MODEL │ →  │ PARSER │
#   └──────────┘    └───────┘    └────────┘
#
# Let's understand WHAT each step does with the DATA:
#
# INPUT:  {"topic": "Python"}        ← you give this
#
# STEP 1 — Prompt:
#   Takes: {"topic": "Python"}
#   Does:  Fills the template with the variable
#   Gives: [SystemMessage("..."), HumanMessage("What is Python?")]
#
# STEP 2 — Model:
#   Takes: [SystemMessage, HumanMessage]
#   Does:  Sends to LLM, gets response
#   Gives: AIMessage(content="Python is a programming language...")
#
# STEP 3 — Parser:
#   Takes: AIMessage(content="Python is...")
#   Does:  Extracts just the text from the AIMessage
#   Gives: "Python is a programming language..."   ← plain string
#
# OUTPUT: "Python is a programming language..."    ← you get this
#
# WHY USE A PARSER?
#   Without parser: you get  AIMessage(content="...", metadata={...})
#   With parser:    you get  "..."   (just the clean text)
#   Always add a parser unless you need the full AIMessage object.
# ==============================================================

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()
model = ChatGroq(model="llama-3.1-8b-instant")

# ==============================================================
# SEE WHAT EACH STEP PRODUCES
# ==============================================================
print("=" * 55)
print("What each step produces (data transformation)")
print("=" * 55)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful teacher."),
    ("human", "Explain {topic} in one sentence.")
])

# After prompt step
messages = prompt.invoke({"topic": "recursion"})
print("\nAfter PROMPT step:")
print("Type:", type(messages))
print("Content:", messages)

# After model step
ai_response = model.invoke(messages)
print("\nAfter MODEL step:")
print("Type:", type(ai_response))
print("Content:", ai_response)

# After parser step
parser = StrOutputParser()
final = parser.invoke(ai_response)
print("\nAfter PARSER step:")
print("Type:", type(final))
print("Content:", final)


# ==============================================================
# BUILD THE CHAIN — same thing in 1 line
# ==============================================================
print("\n" + "=" * 55)
print("Full chain — 1 clean line")
print("=" * 55)

chain = prompt | model | parser
result = chain.invoke({"topic": "recursion"})
print(result)


# ==============================================================
# CHAINS WITH DIFFERENT PARSER TYPES
# ==============================================================
print("\n" + "=" * 55)
print("StrOutputParser — plain text")
print("=" * 55)

str_chain = (
    ChatPromptTemplate.from_messages([("human", "Capital of {country}?")])
    | model
    | StrOutputParser()    # returns a string
)
print(str_chain.invoke({"country": "Japan"}))
print("Type:", type(str_chain.invoke({"country": "Japan"})))


from langchain_core.output_parsers import JsonOutputParser

print("\n" + "=" * 55)
print("JsonOutputParser — Python dict")
print("=" * 55)

json_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "Return ONLY valid JSON. No explanation, no markdown."),
        ("human", "Give me name, population, continent for country: {country}")
    ])
    | model
    | JsonOutputParser()   # returns a dict
)
result = json_chain.invoke({"country": "Brazil"})
print(result)
print("Type:", type(result))
print("Population:", result.get("population"))


# ==============================================================
# CHAIN INSPECTION — see the steps inside
# ==============================================================
print("\n" + "=" * 55)
print("Chain inspection")
print("=" * 55)

chain = prompt | model | StrOutputParser()
print("Chain steps:")
print(chain)

"""
With vs Without StrOutputParser
=================================

What is StrOutputParser?
  A simple parser that extracts the text content from an LLM's AIMessage
  and returns it as a plain Python string. Nothing fancy — just unwraps the object.

What is AIMessage?
  When you call an LLM in LangChain, it doesn't return a plain string.
  It returns an AIMessage object that looks like:
    AIMessage(content="Python is great!", response_metadata={...}, ...)
  To get the actual text you need:  response.content

Flow in this file:
  Template 1  →  "Give a tagline for Python"
  Template 2  →  "Translate that tagline to Marathi"
  Template 2 needs the OUTPUT of Template 1 as its input.

WITHOUT StrOutputParser:
  - LLM returns AIMessage object, not a plain string
  - You must manually extract .content before passing to next template
  - Chain breaks — you handle each step separately
  - Easy to forget .content and get a type error

  template1 | llm  →  AIMessage(content="...")   ← object, not string
  response.content                               ← manual unwrap
  template2 | llm  →  AIMessage(content="...")   ← object again
  response.content                               ← manual unwrap again

WITH StrOutputParser:
  - Sits between llm and the next step in the chain
  - Automatically converts AIMessage → plain string
  - Chain everything with  |  in one go, no manual .content needed

  template1 | llm | StrOutputParser()            →  "Python tagline..."  (plain string)
  | (lambda text: {"text": text})                →  {"text": "Python tagline..."}
  | template2 | llm | StrOutputParser()          →  "Marathi translation"

  Note: the lambda is needed because template2 expects a dict {"text": ...},
  not a raw string — so we wrap the string into the right key.
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")

template1 = ChatPromptTemplate.from_template("Give a one-line tagline for {topic}.")
template2 = ChatPromptTemplate.from_template("Translate this to Marathi: {text}")


# ── WITHOUT StrOutputParser ───────────────────────────────────────────────────
# Every step is done manually — format prompt, call llm, extract .content

# Step 1: format template1 into a list of messages
messages1 = template1.format_messages(topic="Python programming")

# Step 2: pass messages to LLM → returns AIMessage object (not a string)
ai_message1 = llm.invoke(messages1)

# Step 3: manually extract the text from AIMessage
raw_text = ai_message1.content

# Step 4: format template2 using the extracted text
messages2 = template2.format_messages(text=raw_text)

# Step 5: pass to LLM again → returns another AIMessage
ai_message2 = llm.invoke(messages2)

# Step 6: manually extract the final text
final = ai_message2.content

print("WITHOUT parser:", final)


# ── WITH StrOutputParser ──────────────────────────────────────────────────────
# StrOutputParser converts AIMessage → str automatically
# So template2 receives a plain string directly — no manual .content needed
parser = StrOutputParser()
chain = (
    template1
    | llm
    | parser                           # AIMessage → str
    | (lambda text: {"text": text})    # map str to next template input
    | template2
    | llm
    | parser
)

result = chain.invoke({"topic": "Python programming"})
print("WITH parser:   ", result)

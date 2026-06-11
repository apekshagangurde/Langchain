from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(model="llama-3.1-8b-instant")
parser = StrOutputParser()

# --- 1. Simple Chain: prompt | model | parser ---
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a travel guide."),
    ("human", "Give me 3 must-visit places in {country}.")
])

chain = prompt | model | parser

print("=== Simple Chain ===")
result = chain.invoke({"country": "Japan"})
print(result)

# --- 2. Chaining two prompts (sequential chain) ---
summarize_prompt = ChatPromptTemplate.from_messages([
    ("human", "Summarize this in one sentence:\n{text}")
])

sequential_chain = prompt | model | parser | (lambda text: {"text": text}) | summarize_prompt | model | parser

print("\n=== Sequential Chain (places → one-line summary) ===")
summary = sequential_chain.invoke({"country": "Japan"})
print(summary)

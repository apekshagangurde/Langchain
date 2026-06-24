"""
Output Parsers in LangChain
=============================
Output parsers take the raw text response from an LLM and convert it
into a structured Python object (list, dict, Pydantic model, etc.)

Why use them?
  - LLM returns a string → parser turns it into usable data
  - Works great in chains (prompt → llm → parser)

Common parsers:
  1. StrOutputParser    — plain string (default, no transformation)
  2. JsonOutputParser   — parses JSON string → Python dict
  3. PydanticOutputParser — parses into a Pydantic model with validation
  4. CommaSeparatedListOutputParser — splits "a, b, c" → ["a", "b", "c"]
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import (
    CommaSeparatedListOutputParser,
    JsonOutputParser,
    PydanticOutputParser,
    StrOutputParser,
)
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")


# ── 1. StrOutputParser ────────────────────────────────────────────────────────
# Just returns the LLM reply as a clean string

parser = StrOutputParser()
chain  = llm | parser

result = chain.invoke("What is Python in one line?")
print(result)  # "Python is a high-level, interpreted programming language."


# ── 2. CommaSeparatedListOutputParser ────────────────────────────────────────
# Splits a comma-separated reply into a Python list

list_parser = CommaSeparatedListOutputParser()
chain2 = llm | list_parser

result2 = chain2.invoke("Name 4 popular programming languages, comma separated.")
print(result2)  # ['Python', 'JavaScript', 'Java', 'C++']


# ── 3. JsonOutputParser ───────────────────────────────────────────────────────
# Parses JSON string → Python dict

json_parser = JsonOutputParser()
prompt = ChatPromptTemplate.from_template(
    "Return a JSON with keys: name, age, city for a fictional person. {format_instructions}"
)
chain3 = prompt | llm | json_parser

result3 = chain3.invoke({"format_instructions": json_parser.get_format_instructions()})
print(result3)         # {'name': 'Alice', 'age': 28, 'city': 'Paris'}
print(result3["name"]) # Alice


# ── 4. PydanticOutputParser ───────────────────────────────────────────────────
# Parses LLM output directly into a typed Pydantic object

from langchain_core.output_parsers import PydanticOutputParser

class Movie(BaseModel):
    title: str         = Field(description="Movie title")
    genre: str         = Field(description="Movie genre")
    release_year: int  = Field(description="Year of release")

pydantic_parser = PydanticOutputParser(pydantic_object=Movie)

prompt2 = ChatPromptTemplate.from_template(
    "Give details about the movie Inception.\n{format_instructions}"
)
chain4 = prompt2 | llm | pydantic_parser

result4 = chain4.invoke({"format_instructions": pydantic_parser.get_format_instructions()})
print(result4)               # title='Inception' genre='Sci-Fi' release_year=2010
print(result4.title)         # Inception
print(result4.release_year)  # 2010

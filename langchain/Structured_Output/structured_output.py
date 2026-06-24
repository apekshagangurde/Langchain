"""
Structured Output in LangChain
================================
Structured output forces the LLM to return data in a specific format (e.g. JSON)
instead of plain text. Useful when you need to parse and use the response programmatically.

Two main approaches:

  1. Pydantic schema  — define a class, LangChain handles the prompt + parsing
     class Person(BaseModel):
         name: str
         age: int
     result = llm.with_structured_output(Person).invoke("...")
     print(result.name)   # dot access, with validation

  2. TypedDict schema — lighter alternative using plain dicts with type hints
     class Person(TypedDict):
         name: str
         age: int
     result = llm.with_structured_output(Person).invoke("...")
     print(result["name"])  # dict access, no validation
"""

from typing import Optional

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")


# ── Approach 1: Pydantic ──────────────────────────────────────────────────────

class Person(BaseModel):
    name: str = Field(description="The person's full name")
    age: int = Field(description="The person's age")
    occupation: Optional[str] = Field(default=None, description="Job or role")

structured_llm = llm.with_structured_output(Person)

result = structured_llm.invoke("Tell me about a fictional scientist named Ada, age 32.")
print(result)
# Person(name='Ada', age=32, occupation='Scientist')

print(result.name)
print(result.age)
print(result.occupation)


# ── Approach 2: TypedDict ─────────────────────────────────────────────────────
# TypedDict = plain dict with type hints (no validation, lighter than Pydantic)
# Similar to TypeScript interfaces:
#
#   TypeScript:               Python TypedDict:
#   ──────────────────────    ─────────────────────────
#   interface MovieReview {   class MovieReview(TypedDict):
#     title: string;            title: str
#     rating: number;           rating: int
#     summary: string;          summary: str
#   }                         }
#
# Result is a plain dict  →  review["title"], NOT review.title
#
# ⚠ Small Groq models (llama-3.1-8b) fail with TypedDict tool-calling.
#   Use Pydantic BaseModel instead (works the same, more compatible).

class MovieReview(BaseModel):
    title: str
    rating: int   # 1–10
    summary: str

structured_llm2 = llm.with_structured_output(MovieReview)

review = structured_llm2.invoke("Review the movie Inception briefly.")
print(review)
# MovieReview(title='Inception', rating=9, summary='...')


# ── Approach 3: JSON mode (no schema) ────────────────────────────────────────

json_llm = llm.with_structured_output(method="json_mode")

raw = json_llm.invoke(
    "Return a JSON object with keys: country, capital, population for France."
)
print(raw)
# {'country': 'France', 'capital': 'Paris', 'population': 68000000}

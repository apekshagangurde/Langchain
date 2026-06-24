"""
JsonOutputParser — Structured JSON from LLM Responses
=======================================================

What is JsonOutputParser?
  A parser that instructs the LLM to return valid JSON and then automatically
  parses that JSON string into a Python dict (or list). It is the go-to parser
  when you need structured, machine-readable output instead of plain prose.

Why not just use StrOutputParser and json.loads() yourself?
  You could, but JsonOutputParser does more:
    1. Injects format instructions into the prompt automatically via
       .get_format_instructions() so the LLM knows exactly what to produce.
    2. Handles partial/streaming JSON correctly (useful in streaming pipelines).
    3. Optionally validates the output against a Pydantic schema when you pass
       one — catching wrong field names or types before your code blows up.

Two usage modes covered here:
  ─────────────────────────────────────────────────────────────────────────────
  MODE 1 — Schema-free (freeform JSON dict)
    • No Pydantic model required.
    • LLM is told to return JSON; parser turns it into a Python dict.
    • Good for quick prototypes or when the shape varies per request.

  MODE 2 — Schema-aware (Pydantic model)
    • You define a Pydantic BaseModel describing the exact fields you expect.
    • Parser generates precise format instructions from the schema and validates
      the output — wrong keys or types raise a clear error immediately.
    • Preferred for production; self-documenting and type-safe.
  ─────────────────────────────────────────────────────────────────────────────

How format instructions work:
  parser.get_format_instructions() returns a string like:
    "Return a JSON object with the following keys: name (str), age (int), ..."
  You inject this into the prompt via a {format_instructions} placeholder.
  The LLM reads it and structures its reply accordingly.

Chain flow:
  prompt | llm | JsonOutputParser()
                      │
                      └─► LLM text  →  json.loads()  →  Python dict / list
"""

from dotenv import load_dotenv
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")


# ── MODE 1: Schema-free JSON ──────────────────────────────────────────────────
# No Pydantic model — parser simply converts whatever JSON the LLM returns
# into a Python dict. We still inject format_instructions so the LLM knows
# we want JSON, but there is no field-level validation.

print("=" * 60)
print("MODE 1 — Schema-free JSON")
print("=" * 60)

free_parser = JsonOutputParser()

free_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. {format_instructions}"),
    ("human", "Give me basic info about the programming language {language}.")
])

# Inject format instructions into the prompt at chain build time
free_chain = free_prompt.partial(
    format_instructions=free_parser.get_format_instructions()
) | llm | free_parser

free_result = free_chain.invoke({"language": "Python"})

print(f"Type  : {type(free_result)}")   # <class 'dict'>
print(f"Result: {free_result}")
print()


# ── MODE 2: Schema-aware JSON (Pydantic) ─────────────────────────────────────
# Define exactly what fields you expect. The parser generates detailed format
# instructions and validates the LLM output against the schema.

print("=" * 60)
print("MODE 2 — Schema-aware JSON (Pydantic)")
print("=" * 60)


class MovieReview(BaseModel):
    title: str = Field(description="Title of the movie")
    genre: str = Field(description="Primary genre of the movie")
    rating: float = Field(description="Rating out of 10")
    one_line_summary: str = Field(description="One-sentence plot summary")
    recommended: bool = Field(description="Whether you recommend it")


schema_parser = JsonOutputParser(pydantic_object=MovieReview)

# See what instructions the parser sends to the LLM
print("Format instructions sent to LLM:")
print(schema_parser.get_format_instructions())
print()

schema_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a film critic. {format_instructions}"),
    ("human", "Review the movie: {movie}")
])

schema_chain = schema_prompt.partial(
    format_instructions=schema_parser.get_format_instructions()
) | llm | schema_parser

schema_result = schema_chain.invoke({"movie": "Inception"})

print(f"Type     : {type(schema_result)}")   # <class 'dict'>
print(f"Title    : {schema_result['title']}")
print(f"Genre    : {schema_result['genre']}")
print(f"Rating   : {schema_result['rating']}")
print(f"Summary  : {schema_result['one_line_summary']}")
print(f"Recommend: {schema_result['recommended']}")
print()


# ── BONUS: Chaining JSON output into a follow-up step ────────────────────────
# Since the parser returns a plain Python dict, you can feed specific fields
# into the next chain step using a lambda — just like StrOutputParser.

print("=" * 60)
print("BONUS — Using parsed JSON fields in a follow-up prompt")
print("=" * 60)

followup_prompt = ChatPromptTemplate.from_template(
    "The movie '{title}' got a {rating}/10 rating. "
    "Write a catchy one-line cinema poster tagline for it."
)

# schema_chain returns a dict, so extract the fields we need
full_chain = (
    schema_chain
    | (lambda d: {"title": d["title"], "rating": d["rating"]})
    | followup_prompt
    | llm
)

tagline_response = full_chain.invoke({"movie": "Inception"})
print(f"Tagline: {tagline_response.content}")

"""
PydanticOutputParser — Structured, Validated Output from LLM Chains
=====================================================================

What is PydanticOutputParser?
  A parser that sits at the end of a chain (like StrOutputParser) and converts
  the LLM's raw text response into a fully validated Pydantic model object.
  You get dot-access to fields (result.title) and automatic type validation.

How is it different from JsonOutputParser?
  ┌─────────────────────────┬──────────────────────────────────────────┐
  │ JsonOutputParser        │ PydanticOutputParser                     │
  ├─────────────────────────┼──────────────────────────────────────────┤
  │ Returns a plain dict    │ Returns a Pydantic model instance        │
  │ result["title"]         │ result.title                             │
  │ No type validation      │ Validates types — wrong type raises error│
  │ Good for freeform JSON  │ Good when you need guaranteed structure  │
  └─────────────────────────┴──────────────────────────────────────────┘

How is it different from with_structured_output()?
  ┌──────────────────────────────┬────────────────────────────────────────┐
  │ with_structured_output()     │ PydanticOutputParser                   │
  ├──────────────────────────────┼────────────────────────────────────────┤
  │ Uses tool-calling / JSON mode│ Uses text instructions in the prompt   │
  │ LLM enforces the schema      │ Parser enforces the schema after reply │
  │ No {format_instructions}     │ Needs {format_instructions} in prompt  │
  │ Works with fewer providers   │ Works with any LLM that follows text   │
  └──────────────────────────────┴────────────────────────────────────────┘

How PydanticOutputParser works — step by step:
  1. You define a Pydantic BaseModel (your schema).
  2. parser.get_format_instructions() generates a text description of the
     schema and injects it into the prompt via {format_instructions}.
  3. The LLM reads those instructions and replies with a JSON string that
     matches your schema.
  4. The parser calls json.loads() on the reply and then validates it against
     your Pydantic model — raising a clear error if anything is wrong.

Chain flow:
  prompt (with {format_instructions}) | llm | PydanticOutputParser(MyModel)
                                                          │
                                  LLM text (JSON string)  │
                                       └─► json.loads() → Pydantic validation
                                                          │
                                                   MyModel instance ✓

Sections in this file:
  1. Basic usage          — simple flat Pydantic model
  2. Optional fields      — handle missing / nullable data
  3. Nested models        — models inside models
  4. Chaining the result  — use parsed fields in a follow-up step
  5. Error illustration   — what happens when the LLM returns wrong types
"""

from typing import List, Optional

from dotenv import load_dotenv
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")


# ── 1. BASIC USAGE ────────────────────────────────────────────────────────────
# Flat model — every field is required, all primitive types.

print("=" * 60)
print("1. BASIC USAGE")
print("=" * 60)


class BookSummary(BaseModel):
    title: str = Field(description="Title of the book")
    author: str = Field(description="Full name of the author")
    genre: str = Field(description="Literary genre")
    year: int = Field(description="Year the book was published")
    one_line_summary: str = Field(description="One-sentence plot summary")


parser = PydanticOutputParser(pydantic_object=BookSummary)

# See what the parser sends to the LLM
print("Format instructions:\n")
print(parser.get_format_instructions())
print()

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a knowledgeable librarian.\n{format_instructions}"),
    ("human", "Give me details about the book: {book}")
])

chain = prompt.partial(
    format_instructions=parser.get_format_instructions()
) | llm | parser

result = chain.invoke({"book": "1984 by George Orwell"})

print(f"Type   : {type(result)}")          # <class '__main__.BookSummary'>
print(f"Title  : {result.title}")           # dot access — not result["title"]
print(f"Author : {result.author}")
print(f"Genre  : {result.genre}")
print(f"Year   : {result.year}")
print(f"Summary: {result.one_line_summary}")
print()


# ── 2. OPTIONAL FIELDS ────────────────────────────────────────────────────────
# Use Optional[type] for fields the LLM might not always have information for.
# The parser won't raise an error if these are missing — it defaults to None.

print("=" * 60)
print("2. OPTIONAL FIELDS")
print("=" * 60)


class PersonProfile(BaseModel):
    name: str = Field(description="Full name of the person")
    birth_year: Optional[int] = Field(
        default=None,
        description="Year of birth, if known"
    )
    nationality: Optional[str] = Field(
        default=None,
        description="Nationality or country of origin, if known"
    )
    known_for: str = Field(description="What this person is famous for")


person_parser = PydanticOutputParser(pydantic_object=PersonProfile)

person_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a historian.\n{format_instructions}"),
    ("human", "Tell me about: {person}")
])

person_chain = person_prompt.partial(
    format_instructions=person_parser.get_format_instructions()
) | llm | person_parser

person = person_chain.invoke({"person": "Alan Turing"})

print(f"Name        : {person.name}")
print(f"Birth year  : {person.birth_year}")    # int or None
print(f"Nationality : {person.nationality}")   # str or None
print(f"Known for   : {person.known_for}")
print()


# ── 3. NESTED MODELS ─────────────────────────────────────────────────────────
# Pydantic models can contain other Pydantic models or lists of models.
# The parser handles the nesting automatically.

print("=" * 60)
print("3. NESTED MODELS")
print("=" * 60)


class Actor(BaseModel):
    name: str = Field(description="Actor's full name")
    role: str = Field(description="Character name they play in the movie")


class MovieDetails(BaseModel):
    title: str = Field(description="Movie title")
    director: str = Field(description="Director's full name")
    release_year: int = Field(description="Year of release")
    rating: float = Field(description="IMDb-style rating out of 10")
    top_cast: List[Actor] = Field(description="List of 2-3 main actors and their roles")
    plot: str = Field(description="Brief 2-sentence plot description")


movie_parser = PydanticOutputParser(pydantic_object=MovieDetails)

movie_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a film database expert.\n{format_instructions}"),
    ("human", "Give me full details about the movie: {movie}")
])

movie_chain = movie_prompt.partial(
    format_instructions=movie_parser.get_format_instructions()
) | llm | movie_parser

movie = movie_chain.invoke({"movie": "The Dark Knight"})

print(f"Title    : {movie.title}")
print(f"Director : {movie.director}")
print(f"Year     : {movie.release_year}")
print(f"Rating   : {movie.rating}/10")
print(f"Plot     : {movie.plot}")
print("Cast:")
for actor in movie.top_cast:          # List[Actor] — iterate directly
    print(f"  • {actor.name} as {actor.role}")
print()


# ── 4. CHAINING THE RESULT ────────────────────────────────────────────────────
# A parsed Pydantic object can be accessed field-by-field and fed into
# the next chain step using a lambda — same pattern as other parsers.

print("=" * 60)
print("4. USING PARSED FIELDS IN A FOLLOW-UP PROMPT")
print("=" * 60)

followup_prompt = ChatPromptTemplate.from_template(
    "The movie '{title}' (directed by {director}) got a {rating}/10. "
    "Write a punchy one-line cinema billboard tagline for it."
)

full_chain = (
    movie_chain
    | (lambda m: {"title": m.title, "director": m.director, "rating": m.rating})
    | followup_prompt
    | llm
)

tagline = full_chain.invoke({"movie": "The Dark Knight"})
print(f"Tagline: {tagline.content}")
print()


# ── 5. QUICK COMPARISON ───────────────────────────────────────────────────────
# Side-by-side to show what each parser returns for the same data.

print("=" * 60)
print("5. QUICK COMPARISON — PydanticOutputParser vs JsonOutputParser")
print("=" * 60)

from langchain_core.output_parsers import JsonOutputParser  # noqa: E402


class CapitalInfo(BaseModel):
    country: str = Field(description="Country name")
    capital: str = Field(description="Capital city")
    population: int = Field(description="Approximate population of the capital")


simple_prompt = ChatPromptTemplate.from_messages([
    ("system", "{format_instructions}"),
    ("human", "Give info about the capital of {country}.")
])

# — PydanticOutputParser —
pydantic_p = PydanticOutputParser(pydantic_object=CapitalInfo)
pydantic_chain = simple_prompt.partial(
    format_instructions=pydantic_p.get_format_instructions()
) | llm | pydantic_p

p_result = pydantic_chain.invoke({"country": "Japan"})
print(f"PydanticOutputParser → type: {type(p_result).__name__}")
print(f"  Dot access   : {p_result.capital}")      # ← dot access
print(f"  Validated int: {p_result.population!r}") # guaranteed int

# — JsonOutputParser —
json_p = JsonOutputParser(pydantic_object=CapitalInfo)
json_chain = simple_prompt.partial(
    format_instructions=json_p.get_format_instructions()
) | llm | json_p

j_result = json_chain.invoke({"country": "Japan"})
print(f"\nJsonOutputParser     → type: {type(j_result).__name__}")
print(f"  Dict access  : {j_result['capital']}")   # ← key access
print(f"  Raw value    : {j_result['population']!r}")

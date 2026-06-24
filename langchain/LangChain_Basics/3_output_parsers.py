from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
from langchain_core.pydantic_v1 import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(model="llama-3.1-8b-instant")

# --- 1. StrOutputParser — plain text ---
str_chain = (
    ChatPromptTemplate.from_messages([("human", "Name the capital of {country}.")])
    | model
    | StrOutputParser()
)
print("=== StrOutputParser ===")
print(str_chain.invoke({"country": "France"}))

# --- 2. JsonOutputParser — structured JSON output ---
json_prompt = ChatPromptTemplate.from_messages([
    ("system", "Return only valid JSON, no markdown."),
    ("human", "Give info about {animal}: name, habitat, diet. Return as JSON keys: name, habitat, diet.")
])

json_chain = json_prompt | model | JsonOutputParser()

print("\n=== JsonOutputParser ===")
result = json_chain.invoke({"animal": "snow leopard"})
print(result)
print(type(result))  # dict

# --- 3. Pydantic output parser — typed Python object ---
class Movie(BaseModel):
    title: str = Field(description="Movie title")
    year: int = Field(description="Release year")
    genre: str = Field(description="Main genre")

pydantic_prompt = ChatPromptTemplate.from_messages([
    ("system", "Return only valid JSON matching the schema: title, year, genre. No markdown."),
    ("human", "Give details about the movie: {movie_name}")
])

pydantic_chain = pydantic_prompt | model | JsonOutputParser()

print("\n=== Pydantic-style Structured Output ===")
movie = pydantic_chain.invoke({"movie_name": "Inception"})
print(movie)

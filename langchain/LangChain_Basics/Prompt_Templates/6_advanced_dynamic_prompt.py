# ==============================================================
# ADVANCED: DYNAMIC PROMPT BUILDING
# ==============================================================
#
# REAL WORLD SCENARIO:
#   You're building an AI tutor app.
#   → Beginner students  → simple language, no jargon
#   → Advanced students  → technical depth, use terms
#   → The system prompt must CHANGE based on the student level
#
# You can't hardcode this. You need to BUILD the prompt
# dynamically at runtime based on user input.
#
# TECHNIQUES COVERED HERE:
#   1. Choose prompt based on a condition (if/else)
#   2. Build prompts dynamically with a factory function
#   3. RunnableLambda to pick prompt at runtime inside a chain
# ==============================================================

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()
model = ChatGroq(model="llama-3.1-8b-instant")
parser = StrOutputParser()

# ---- TECHNIQUE 1: Prompt factory function ----
# Build different prompts based on input

def get_prompt_for_level(level: str) -> ChatPromptTemplate:
    if level == "beginner":
        return ChatPromptTemplate.from_messages([
            ("system", "You are a teacher for 10-year-olds. Use very simple words, no jargon. Use analogies."),
            ("human", "Explain: {topic}")
        ])
    elif level == "intermediate":
        return ChatPromptTemplate.from_messages([
            ("system", "You are a college professor. Be clear and structured. Use some technical terms."),
            ("human", "Explain: {topic}")
        ])
    else:  # advanced
        return ChatPromptTemplate.from_messages([
            ("system", "You are an expert researcher. Use full technical depth and assume strong prior knowledge."),
            ("human", "Explain: {topic}")
        ])

print("=== Same topic, 3 different levels ===\n")

topic = "how neural networks learn"

for level in ["beginner", "intermediate", "advanced"]:
    prompt = get_prompt_for_level(level)
    chain = prompt | model | parser
    result = chain.invoke({"topic": topic})
    print(f"--- {level.upper()} ---")
    print(result[:300])   # print first 300 chars to keep output short
    print()

# ---- TECHNIQUE 2: Dynamic prompt INSIDE a chain ----
# RunnableLambda lets you run a Python function as a step in the chain

def build_prompt(inputs: dict) -> list:
    level = inputs["level"]
    topic = inputs["topic"]
    prompt = get_prompt_for_level(level)
    return prompt.format_messages(topic=topic)

dynamic_chain = RunnableLambda(build_prompt) | model | parser

print("=== Dynamic chain (level chosen at runtime) ===\n")

result = dynamic_chain.invoke({"level": "beginner", "topic": "recursion in programming"})
print("BEGINNER explanation of recursion:")
print(result[:400])

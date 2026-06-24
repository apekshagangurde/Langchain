# ==============================================================
# BRANCHING / CONDITIONAL CHAIN
# ==============================================================
#
# WHAT IS IT?
#   Sometimes you don't want ONE fixed chain.
#   You want DIFFERENT chains to run based on the input.
#
# ANALOGY — Hospital triage:
#   Patient arrives → Nurse checks severity
#     If CRITICAL  → send to ICU chain
#     If MODERATE  → send to general ward chain
#     If MINOR     → send to outpatient chain
#
# IN LANGCHAIN:
#   Input arrives → classifier decides which chain to use
#   → Route to chain A, B, or C based on the classification
#
# HOW TO BUILD IT:
#   1. Classifier chain → classifies the input (e.g. "math"/"code"/"general")
#   2. Router function  → picks the right chain based on classification
#   3. RunnableLambda   → runs the router as a step in the main chain
#
# THIS IS CALLED "Routing" in LangChain.
# ==============================================================

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()
model = ChatGroq(model="llama-3.1-8b-instant")
parser = StrOutputParser()


# ==============================================================
# EXAMPLE 1 — Simple if/else routing
# ==============================================================
print("=" * 55)
print("EXAMPLE 1: Route by language (Python vs JavaScript)")
print("=" * 55)

python_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "You are a Python expert. Only use Python examples."),
        ("human", "{question}")
    ])
    | model | parser
)

js_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "You are a JavaScript expert. Only use JS examples."),
        ("human", "{question}")
    ])
    | model | parser
)

general_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "You are a helpful coding assistant."),
        ("human", "{question}")
    ])
    | model | parser
)

def route_by_language(inputs: dict) -> str:
    lang = inputs.get("language", "").lower()
    if lang == "python":
        return python_chain.invoke(inputs)
    elif lang == "javascript":
        return js_chain.invoke(inputs)
    else:
        return general_chain.invoke(inputs)

# The main chain just routes
routing_chain = RunnableLambda(route_by_language)

print("\n[Python route]")
print(routing_chain.invoke({
    "language": "python",
    "question": "How do I loop through a list?"
}))

print("\n[JavaScript route]")
print(routing_chain.invoke({
    "language": "javascript",
    "question": "How do I loop through a list?"
}))


# ==============================================================
# EXAMPLE 2 — Auto-classify then route (no manual tag needed)
# ==============================================================
print("\n" + "=" * 55)
print("EXAMPLE 2: AI classifies input, then routes automatically")
print("=" * 55)
#
# User just sends a question — no tag.
# Step 1: Classifier chain → labels it "math", "code", or "general"
# Step 2: Router  → picks the right expert chain based on label
# Step 3: Expert chain → answers the question
#
# Input:  {"question": "What is the derivative of x^2?"}
# After classifier: "math"
# After router: uses math_chain
# Final: expert math answer

# Step 1: Classifier
classifier_chain = (
    ChatPromptTemplate.from_messages([
        ("system",
         "Classify the question into exactly one category: math, code, or general.\n"
         "Reply with ONLY the category word. Nothing else."),
        ("human", "{question}")
    ])
    | model | parser
)

# Step 2: Expert chains
math_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "You are a math professor. Solve step by step."),
        ("human", "{question}")
    ])
    | model | parser
)

code_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "You are a senior programmer. Provide code with explanation."),
        ("human", "{question}")
    ])
    | model | parser
)

general_chain2 = (
    ChatPromptTemplate.from_messages([
        ("system", "You are a knowledgeable assistant."),
        ("human", "{question}")
    ])
    | model | parser
)

# Step 3: Router function
def route_by_classifier(inputs: dict) -> str:
    category = classifier_chain.invoke(inputs).strip().lower()
    print(f"  [Classified as: {category}]")

    if "math" in category:
        return math_chain.invoke(inputs)
    elif "code" in category:
        return code_chain.invoke(inputs)
    else:
        return general_chain2.invoke(inputs)

auto_router = RunnableLambda(route_by_classifier)

questions = [
    "What is the integral of sin(x)?",
    "How do I reverse a string in Python?",
    "Who invented the telephone?",
]

for q in questions:
    print(f"\nQuestion: {q}")
    answer = auto_router.invoke({"question": q})
    print("Answer:", answer[:200])


# ==============================================================
# EXAMPLE 3 — Fallback chain (try chain A, if fails use chain B)
# ==============================================================
print("\n" + "=" * 55)
print("EXAMPLE 3: Fallback — if main chain fails, use backup")
print("=" * 55)
#
# .with_fallbacks([backup_chain]) makes a chain that:
#   1. Tries the main chain
#   2. If it throws an error → automatically tries backup chain
#
# REAL USE: main = expensive GPT-4, backup = cheaper model

# Simulate a chain that fails for certain inputs
def strict_chain_fn(inputs: dict) -> str:
    question = inputs.get("question", "")
    if "secret" in question.lower():
        raise ValueError("I cannot answer questions about secrets!")
    return model.invoke(question).content

main_chain   = RunnableLambda(strict_chain_fn)
backup_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "If you can't answer directly, give a helpful redirect."),
        ("human", "{question}")
    ])
    | model | parser
)

safe_chain = main_chain.with_fallbacks([backup_chain])

print("\nNormal question:")
print(safe_chain.invoke({"question": "What is gravity?"}))

print("\nTriggered fallback question:")
print(safe_chain.invoke({"question": "Tell me about secret government projects"}))

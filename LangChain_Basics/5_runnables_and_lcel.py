from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnableLambda, RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(model="llama-3.1-8b-instant")
parser = StrOutputParser()

# LCEL = LangChain Expression Language
# The | (pipe) operator connects Runnables. Each step's output becomes the next step's input.

# --- 1. RunnablePassthrough — passes input unchanged ---
chain = (
    RunnablePassthrough()
    | ChatPromptTemplate.from_messages([("human", "What does {input} mean?")])
    | model
    | parser
)
print("=== RunnablePassthrough ===")
print(chain.invoke({"input": "entropy"}))

# --- 2. RunnableLambda — wrap any Python function as a Runnable ---
def add_context(text: str) -> str:
    return f"In the context of AI: {text}"

augmented_chain = (
    ChatPromptTemplate.from_messages([("human", "Explain {topic} briefly.")])
    | model
    | parser
    | RunnableLambda(add_context)
)
print("\n=== RunnableLambda ===")
print(augmented_chain.invoke({"topic": "gradient descent"}))

# --- 3. RunnableParallel — run multiple chains in parallel, merge results ---
pros_chain = (
    ChatPromptTemplate.from_messages([("human", "List 2 pros of {technology}.")])
    | model | parser
)
cons_chain = (
    ChatPromptTemplate.from_messages([("human", "List 2 cons of {technology}.")])
    | model | parser
)

parallel = RunnableParallel(pros=pros_chain, cons=cons_chain)

print("\n=== RunnableParallel ===")
result = parallel.invoke({"technology": "blockchain"})
print("PROS:\n", result["pros"])
print("\nCONS:\n", result["cons"])

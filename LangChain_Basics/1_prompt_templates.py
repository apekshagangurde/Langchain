from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(model="llama-3.1-8b-instant")

# --- 1. PromptTemplate (plain string, for LLMs) ---
prompt = PromptTemplate(
    input_variables=["topic"],
    template="Explain {topic} in simple words in 3 sentences."
)

formatted = prompt.format(topic="machine learning")
print("=== PromptTemplate Output ===")
print(formatted)

# --- 2. ChatPromptTemplate (for chat models) ---
chat_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful teacher who explains things simply."),
    ("human", "Explain {topic} to a {level} student.")
])

messages = chat_prompt.format_messages(topic="neural networks", level="beginner")
print("\n=== ChatPromptTemplate Messages ===")
for msg in messages:
    print(f"{msg.type}: {msg.content}")

# --- 3. Send ChatPromptTemplate directly to the model ---
result = model.invoke(messages)
print("\n=== Model Response ===")
print(result.content)

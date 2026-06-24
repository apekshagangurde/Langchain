# ==============================================================
# CHAT PROMPT TEMPLATE
# ==============================================================
#
# Chat models (like Groq/ChatGPT) don't just take a single string.
# They take a CONVERSATION — a list of messages with ROLES.
#
# 3 ROLES:
#   "system"  → Background instruction to the AI
#                (who it is, how it should behave)
#   "human"   → What the user says
#   "ai"      → What the AI said previously (used in history)
#
# THINK OF IT LIKE THIS:
#   system = "You are a chef"          ← sets the personality
#   human  = "How do I boil an egg?"  ← user's question
#   ai     = model's answer
#
# ChatPromptTemplate combines all these roles into one template.
# ==============================================================

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()
model = ChatGroq(model="llama-3.1-8b-instant")

# ---- BASIC: system + human ----
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant who speaks like a pirate."),
    ("human",  "Tell me about {topic}")
])

# .format_messages() → returns a list of message objects
messages = prompt.format_messages(topic="the ocean")

print("=== Messages sent to model ===")
for msg in messages:
    print(f"  [{msg.type.upper()}]: {msg.content}")

# Send to model
result = model.invoke(messages)
print("\n=== Model Response ===")
print(result.content)

# ---- VARIABLES IN BOTH system AND human ----
flexible_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a {role}. Always answer in {language}."),
    ("human",  "{question}")
])

print("\n\n=== Flexible Prompt (role + language + question) ===")
messages2 = flexible_prompt.format_messages(
    role="doctor",
    language="simple English",
    question="What causes headaches?"
)
result2 = model.invoke(messages2)
print(result2.content)

# ---- USING THE PIPE | (chain style — cleaner code) ----
chain = flexible_prompt | model

print("\n\n=== Same thing using | chain ===")
result3 = chain.invoke({
    "role": "fitness trainer",
    "language": "motivating tone",
    "question": "How do I build abs?"
})
print(result3.content)

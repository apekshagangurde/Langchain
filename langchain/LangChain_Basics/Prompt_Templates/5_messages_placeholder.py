# ==============================================================
# MESSAGES PLACEHOLDER — For Chat History / Memory
# ==============================================================
#
# PROBLEM:
#   In a chatbot, the user sends multiple messages back and forth.
#   How do you inject the entire conversation history into the prompt?
#
# WRONG WAY:
#   Manually hardcode every past message → impossible for dynamic chats
#
# RIGHT WAY: MessagesPlaceholder
#   It's a "slot" in your ChatPromptTemplate that says:
#   "Put the entire conversation history HERE"
#
# THINK OF IT LIKE:
#   Template: [system] + {chat_history_goes_here} + [latest human msg]
#   At runtime: fill the slot with the actual history list
#
# This is the FOUNDATION of how chatbots remember context!
# ==============================================================

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv

load_dotenv()
model = ChatGroq(model="llama-3.1-8b-instant")

# ---- BUILD THE TEMPLATE WITH A PLACEHOLDER ----
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a friendly assistant. Keep answers short."),
    MessagesPlaceholder(variable_name="history"),   # ← slot for past messages
    ("human", "{user_input}")                        # ← current message
])

# ---- SIMULATE A MULTI-TURN CONVERSATION ----
chat_history = []   # starts empty

def chat(user_input: str) -> str:
    # Build the full message list by filling the template
    messages = prompt.format_messages(
        history=chat_history,
        user_input=user_input
    )

    response = model.invoke(messages)
    answer = response.content

    # Save this turn into history for next time
    chat_history.append(HumanMessage(content=user_input))
    chat_history.append(AIMessage(content=answer))

    return answer

print("=== Multi-turn Chat using MessagesPlaceholder ===\n")

print("You: My name is Apeksha.")
print("Bot:", chat("My name is Apeksha."))

print("\nYou: What is AI?")
print("Bot:", chat("What is AI?"))

print("\nYou: Can you remind me what my name is?")  # tests memory
print("Bot:", chat("Can you remind me what my name is?"))

print("\nYou: Give me one real world use case of what you just explained.")
print("Bot:", chat("Give me one real world use case of what you just explained."))

print("\n\n=== Chat History Stored ===")
for i, msg in enumerate(chat_history):
    role = "You " if isinstance(msg, HumanMessage) else "Bot"
    print(f"  [{role}]: {msg.content[:80]}...")

from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv

load_dotenv()

model = ChatGroq(model="llama-3.1-8b-instant")

# LangChain manages memory by passing the full conversation history
# as a list of messages on every call. You maintain the list yourself.

chat_history = [
    SystemMessage(content="You are a helpful assistant. Keep answers brief.")
]

def chat(user_input: str) -> str:
    chat_history.append(HumanMessage(content=user_input))
    response = model.invoke(chat_history)
    chat_history.append(AIMessage(content=response.content))
    return response.content

print("=== Multi-turn Conversation with Memory ===\n")

print("You: What is photosynthesis?")
print("Bot:", chat("What is photosynthesis?"))

print("\nYou: Give me an example of it.")
print("Bot:", chat("Give me an example of it."))  # "it" refers to photosynthesis

print("\nYou: How many steps are involved?")
print("Bot:", chat("How many steps are involved?"))

print("\n=== Full Chat History ===")
for msg in chat_history:
    role = msg.__class__.__name__.replace("Message", "")
    print(f"[{role}]: {msg.content}")

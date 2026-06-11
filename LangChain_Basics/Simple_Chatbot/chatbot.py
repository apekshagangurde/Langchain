# ================================================================
#                        THEORY
# ================================================================
#
# WHAT IS A CHATBOT?
#   A chatbot is a program that takes a user's text message,
#   sends it to an AI model, and prints the reply.
#   Then it waits for the next message. This repeats forever
#   until the user says "exit".
#
# ── HOW A BASIC CHATBOT WORKS (step by step) ──────────────────
#
#   1. User types a message  →  "What is Python?"
#   2. Program sends it to the AI model
#   3. AI model replies      →  "Python is a programming language..."
#   4. Program prints reply
#   5. Go back to step 1 and wait again
#   6. If user types "exit"  →  stop the program
#
# ── WHAT IS CHAT HISTORY / MEMORY? ───────────────────────────
#
#   Problem:
#     Every time you send a message to the AI, it forgets the
#     previous messages. It has no memory by default.
#
#   Example of NO memory (bad):
#     You:  "My name is Apeksha"
#     Bot:  "Nice to meet you, Apeksha!"
#     You:  "What is my name?"
#     Bot:  "I don't know your name."   ← FORGOT!
#
#   Solution — Chat History:
#     Keep a list of all past messages.
#     Every time you send a new message, ALSO send the full list
#     of past messages along with it.
#     Now the AI can "see" the whole conversation.
#
#   Example WITH memory (good):
#     You:  "My name is Apeksha"
#     Bot:  "Nice to meet you, Apeksha!"
#     You:  "What is my name?"
#     Bot:  "Your name is Apeksha."     ← REMEMBERED!
#
# ── WHAT ARE HumanMessage AND AIMessage? ─────────────────────
#
#   LangChain stores chat history as a list of message objects.
#   Each message has a TYPE (who said it) and CONTENT (what was said).
#
#   HumanMessage  →  something the user said
#   AIMessage     →  something the AI replied
#
#   chat_history = [
#       HumanMessage(content="My name is Apeksha"),
#       AIMessage(content="Nice to meet you, Apeksha!"),
#       HumanMessage(content="What is my name?"),
#       ...
#   ]
#
# ── WHAT IS MessagesPlaceholder? ────────────────────────────
#
#   It is a "slot" inside the prompt template.
#   When you call the chain, all messages from chat_history
#   get inserted into that slot automatically.
#
#   Template looks like:
#     [system message]
#     [---- all past messages go here ----]   ← MessagesPlaceholder
#     [latest human message]
#
# ── WHAT IS while True? ──────────────────────────────────────
#
#   while True means "loop forever".
#   The only way to stop it is with a "break" statement.
#   We break when the user types "exit".
#
#   while True:
#       input = get_user_input()
#       if input == "exit":
#           break           ← stops the loop
#       else:
#           reply to user   ← keeps going
#
# ── COMPONENTS USED ──────────────────────────────────────────
#
#   ChatGroq               → the AI model (free, fast)
#   ChatPromptTemplate     → structures the conversation with roles
#   MessagesPlaceholder    → slot for injecting chat history
#   HumanMessage           → stores what user said in history
#   AIMessage              → stores what AI replied in history
#   StrOutputParser        → extracts plain text from AI response
#
# ================================================================


# ================================================================
#                        IMPORTS
# ================================================================

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

load_dotenv()


# ================================================================
#                        SETUP
# ================================================================

model = ChatGroq(model="llama-3.1-8b-instant")

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant. Keep answers concise."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

chain = prompt | model | StrOutputParser()

chat_history = []


# ================================================================
#                        CHATBOT LOOP
# ================================================================

print("Chatbot ready! Type 'exit' to quit.\n")

while True:
    user_input = input("You: ").strip()

    if user_input.lower() == "exit":
        print("Goodbye!")
        break

    if not user_input:
        continue

    response = chain.invoke({"input": user_input, "history": chat_history})

    chat_history.append(HumanMessage(content=user_input))
    chat_history.append(AIMessage(content=response))

    print(f"Bot: {response}\n")


# ================================================================
#                     CODE EXPLANATION
# ================================================================
#
# ── LINE BY LINE ─────────────────────────────────────────────
#
#   from langchain_groq import ChatGroq
#     → Imports the Groq AI model class.
#       Groq runs Llama 3 and is free to use.
#
#   from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
#     → ChatPromptTemplate  : builds the full prompt with roles (system/human)
#     → MessagesPlaceholder : a slot in the prompt for inserting chat history
#
#   from langchain_core.messages import HumanMessage, AIMessage
#     → HumanMessage : wraps what the user said, for storing in history
#     → AIMessage    : wraps what the AI said, for storing in history
#
#   from langchain_core.output_parsers import StrOutputParser
#     → The AI model returns an AIMessage object.
#       StrOutputParser extracts just the text (string) from it.
#
#   from dotenv import load_dotenv
#     → Reads your .env file so GROQ_API_KEY is available to the program.
#
#   load_dotenv()
#     → Actually loads the .env file into environment variables.
#       Without this, the API key would not be found.
#
# ─────────────────────────────────────────────────────────────
#
#   model = ChatGroq(model="llama-3.1-8b-instant")
#     → Creates the AI model object.
#       "llama-3.1-8b-instant" is the model name — fast and free on Groq.
#
# ─────────────────────────────────────────────────────────────
#
#   prompt = ChatPromptTemplate.from_messages([...])
#     → Builds the prompt structure. It has 3 parts:
#
#       ("system", "You are a helpful assistant...")
#         → Gives the AI its personality/instructions.
#           The AI will always follow this rule.
#
#       MessagesPlaceholder(variable_name="history")
#         → This is the slot where all past messages will be inserted.
#           At runtime, the "history" key fills this slot.
#
#       ("human", "{input}")
#         → The current message from the user.
#           {input} gets replaced with what the user just typed.
#
# ─────────────────────────────────────────────────────────────
#
#   chain = prompt | model | StrOutputParser()
#     → Connects all steps with the pipe | operator.
#       prompt  → formats the messages
#       model   → sends to AI, gets AIMessage back
#       parser  → extracts plain text from AIMessage
#
# ─────────────────────────────────────────────────────────────
#
#   chat_history = []
#     → Starts as an empty list.
#       After each conversation turn, we add 2 items:
#         - HumanMessage (what user said)
#         - AIMessage    (what bot replied)
#       So after 3 turns it looks like:
#         [HumanMessage, AIMessage, HumanMessage, AIMessage, ...]
#
# ─────────────────────────────────────────────────────────────
#
#   print("Chatbot ready! Type 'exit' to quit.\n")
#     → Just a welcome message shown once at the start.
#
# ─────────────────────────────────────────────────────────────
#
#   while True:
#     → Infinite loop — keeps running until we call break.
#
#   user_input = input("You: ").strip()
#     → input("You: ")  : prints "You: " and waits for the user to type
#     → .strip()        : removes extra spaces from start and end
#                         e.g. "  hello  " → "hello"
#
#   if user_input.lower() == "exit":
#       print("Goodbye!")
#       break
#     → .lower() converts input to lowercase so "EXIT", "Exit", "exit"
#       all work the same way.
#     → break stops the while True loop and exits the program.
#
#   if not user_input:
#       continue
#     → If the user pressed Enter without typing anything,
#       user_input is "" (empty string).
#       "not user_input" is True when it's empty.
#       continue skips the rest of the loop and asks for input again.
#       This prevents sending empty messages to the AI.
#
#   response = chain.invoke({"input": user_input, "history": chat_history})
#     → Runs the full chain (prompt → model → parser).
#     → Passes two things:
#         "input"   : the current message the user just typed
#         "history" : the full list of past messages (memory)
#     → Returns a plain string (thanks to StrOutputParser).
#
#   chat_history.append(HumanMessage(content=user_input))
#   chat_history.append(AIMessage(content=response))
#     → Saves this turn into history so the next message remembers it.
#     → We append AFTER getting the response (not before).
#
#   print(f"Bot: {response}\n")
#     → Prints the AI's reply with "Bot: " prefix.
#     → \n adds a blank line after each reply for readability.
#
# ── FLOW DIAGRAM ──────────────────────────────────────────────
#
#   START
#     │
#     ▼
#   print welcome message
#     │
#     ▼
#   ┌─────────────────────────────────────┐
#   │           while True                │
#   │                                     │
#   │  user_input = input("You: ")        │
#   │         │                           │
#   │   "exit"? ──YES──► print "Goodbye!" │
#   │         │              └──► BREAK   │
#   │         NO                          │
#   │         │                           │
#   │   empty? ──YES──► continue (skip)   │
#   │         │                           │
#   │         NO                          │
#   │         │                           │
#   │  chain.invoke(input + history)      │
#   │         │                           │
#   │  append to chat_history             │
#   │         │                           │
#   │  print Bot: response                │
#   │         │                           │
#   │         └──────────────────────────►│ (loop again)
#   └─────────────────────────────────────┘
#     │
#   END
#
# ================================================================

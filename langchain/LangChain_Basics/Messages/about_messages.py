# ================================================================
#                   WHAT ARE MESSAGES IN LANGCHAIN?
# ================================================================
#
# When you talk to an AI model, you don't just send one plain text.
# You send a LIST of messages, and each message has a ROLE.
# The role tells the AI — who is speaking this line?
#
#
# LangChain has 3 types of messages for these 3 roles.
#
# ================================================================
#
#
# ── 1. SystemMessage ─────────────────────────────────────────
#
#   WHO    : The developer (you) — written before the conversation starts
#   PURPOSE: Give the AI its personality, role, and rules
#
#   Think of it as:
#     The instruction manual you give to an employee before they
#     start their job. The employee (AI) always follows these rules
#     throughout the entire conversation.
#
#   Examples of what you write in a SystemMessage:
#     → "You are a helpful customer service agent for Amazon."
#     → "Always answer in bullet points."
#     → "You are a doctor. Never give medical prescriptions."
#     → "Reply only in Hindi."
#
#   Key points:
#     → The user NEVER sees the SystemMessage
#     → It is set ONCE and applies to the whole conversation
#     → It shapes HOW the AI behaves, not WHAT it answers
#
#
# ── 2. HumanMessage ──────────────────────────────────────────
#
#   WHO    : The user — the person using your app
#   PURPOSE: The actual question or message from the user
#
#   Think of it as:
#     What the customer types in a chat box.
#     Every time the user sends a message, it becomes a HumanMessage.
#
#   Examples:
#     → "What is machine learning?"
#     → "My order has not arrived yet."
#     → "Give me a recipe for pasta."
#     → "Explain that in simpler words."
#
#   Key points:
#     → This is the input that changes every conversation turn
#     → Every message the user types = one HumanMessage
#     → The AI reads this and decides what to reply
#
#
# ── 3. AIMessage ─────────────────────────────────────────────
#
#   WHO    : The AI model — the chatbot
#   PURPOSE: The reply that the AI gave in a previous turn
#
#   Think of it as:
#     The AI's previous answers, stored so the AI can remember
#     what it already said earlier in the conversation.
#
#   Examples:
#     → "Machine learning is a type of AI that learns from data."
#     → "I'm sorry to hear that. Can you share your order ID?"
#     → "Here is a simple pasta recipe: ..."
#
#   Key points:
#     → You don't write AIMessage yourself — the AI produces it
#     → You SAVE it into chat history after each reply
#     → It gives the AI memory of its own previous responses
#
#
# ================================================================
#               HOW ALL 3 WORK TOGETHER
# ================================================================
#
#   A full conversation sent to the AI looks like this:
#
#   ┌─────────────────────────────────────────────────────────┐
#   │  SystemMessage  → "You are a travel guide."             │
#   │  HumanMessage   → "Suggest a place to visit in India."  │
#   │  AIMessage      → "You should visit Rajasthan..."       │
#   │  HumanMessage   → "Tell me more about it."              │
#   │  AIMessage      → "Rajasthan is known for..."           │
#   │  HumanMessage   → "What is the best time to go?"  ←new  │
#   └─────────────────────────────────────────────────────────┘
#
#   The AI sees ALL of the above every time.
#   That is why it knows "it" refers to Rajasthan.
#   That is memory.
#
#
# ================================================================
#               SIMPLE SUMMARY TABLE
# ================================================================
#
#   Type            Who writes it      When                  Purpose
#   ─────────────   ──────────────     ────────────────────  ──────────────────────
#   SystemMessage   Developer (you)    Once at the start     Set AI personality/rules
#   HumanMessage    The user           Every conversation    User's question/message
#   AIMessage       The AI model       After each reply      AI's previous response
#
#
# ================================================================

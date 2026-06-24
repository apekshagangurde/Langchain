# ==============================================================
# REAL WORLD CHAIN — Complete End-to-End Example
# ==============================================================
#
# PROJECT: "Smart Study Assistant"
#
# Given a topic, it:
#   1. Generates a short lesson
#   2. Simultaneously creates a quiz AND a summary (parallel)
#   3. Evaluates if the quiz is good quality
#   4. Returns everything in one structured output
#
# CHAIN ARCHITECTURE:
#
#   User Input: {"topic": "Python functions"}
#        │
#        ▼
#   [lesson_chain]  ← generates lesson text
#        │
#        ▼ lesson text
#   [RunnablePassthrough.assign]
#        ├── quiz_chain    (parallel)
#        └── summary_chain (parallel)
#        │
#        ▼ {topic, lesson, quiz, summary}
#   [quality_check_chain] ← rates the quiz quality
#        │
#        ▼
#   [format_chain] ← formats everything nicely
#        │
#        ▼
#   Final structured output
#
# This shows ALL chain types working together:
#   Simple chain + Sequential + Parallel + Lambda + Passthrough
# ==============================================================

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda, RunnablePassthrough, RunnableParallel
from dotenv import load_dotenv

load_dotenv()
model = ChatGroq(model="llama-3.1-8b-instant")
parser = StrOutputParser()


# ── Individual chains ─────────────────────────────────────────

lesson_chain = (
    ChatPromptTemplate.from_messages([
        ("system", "You are a teacher. Write clearly and simply."),
        ("human",  "Write a short lesson (80 words) about: {topic}")
    ])
    | model | parser
)

# These take {topic} AND {lesson} as input
quiz_chain = (
    ChatPromptTemplate.from_messages([
        ("human",
         "Based on this lesson about {topic}:\n\n{lesson}\n\n"
         "Create 2 multiple choice questions (A/B/C/D) with answers.")
    ])
    | model | parser
)

summary_chain = (
    ChatPromptTemplate.from_messages([
        ("human",
         "Summarize this lesson in ONE sentence:\n\n{lesson}")
    ])
    | model | parser
)

quality_chain = (
    ChatPromptTemplate.from_messages([
        ("human",
         "Rate this quiz from 1-5 for educational quality:\n\n{quiz}\n\n"
         "Reply with just: Rating: X/5 — one reason why.")
    ])
    | model | parser
)


# ── Final formatter ───────────────────────────────────────────

def format_output(data: dict) -> str:
    return f"""
╔══════════════════════════════════════════════╗
   STUDY ASSISTANT — Topic: {data['topic']}
╚══════════════════════════════════════════════╝

📖 LESSON:
{data['lesson']}

💡 ONE-LINE SUMMARY:
{data['summary']}

📝 QUIZ:
{data['quiz']}

⭐ QUIZ QUALITY:
{data['quality']}
"""


# ── Full chain assembly ───────────────────────────────────────

full_chain = (
    # Step 1: Keep topic + generate lesson
    RunnablePassthrough.assign(lesson=lesson_chain)

    # Step 2: Keep topic+lesson, generate quiz and summary in PARALLEL
    | RunnablePassthrough.assign(
        quiz    = quiz_chain,
        summary = summary_chain,
    )

    # Step 3: Keep everything, add quality check on the quiz
    | RunnablePassthrough.assign(quality=quality_chain)

    # Step 4: Format everything into a nice readable output
    | RunnableLambda(format_output)
)


# ── Run it ────────────────────────────────────────────────────

print("Running Smart Study Assistant...\n")
output = full_chain.invoke({"topic": "Python list comprehensions"})
print(output)

# ── Try another topic ─────────────────────────────────────────
print("\nRunning on second topic...\n")
output2 = full_chain.invoke({"topic": "What are APIs"})
print(output2)

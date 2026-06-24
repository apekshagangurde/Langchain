# ==============================================================
# PARTIAL PROMPT TEMPLATES
# ==============================================================
#
# PROBLEM:
#   Sometimes you know SOME variables now, but others come later.
#
# REAL LIFE EXAMPLE:
#   You're building a customer service bot.
#   → Company name is FIXED (you know it now)
#   → Customer question changes every time (you get it later)
#
# SOLUTION: "Partial" the template → fix some variables now,
#            leave others for later.
#
# TWO WAYS to partial:
#   1. With a fixed value  → partial(company="TechCorp")
#   2. With a function     → partial(date=get_today)  ← auto-called!
# ==============================================================

from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_groq import ChatGroq
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
model = ChatGroq(model="llama-3.1-8b-instant")

# ---- METHOD 1: Partial with a fixed value ----
full_template = PromptTemplate.from_template(
    "You work at {company}. Answer this customer question: {question}"
)

# Fix the company name now — it never changes
company_bot = full_template.partial(company="Amazon")

# Later, only pass the question
prompt1 = company_bot.format(question="Where is my order?")
prompt2 = company_bot.format(question="How do I return an item?")

print("=== Partial with fixed value ===")
print(prompt1)
print(prompt2)

# ---- METHOD 2: Partial with a FUNCTION (auto-called each time) ----
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")   # e.g. "June 11, 2025"

date_template = PromptTemplate.from_template(
    "Today is {date}. Answer this question: {question}"
)

# Pass the function (not the result) — LangChain calls it automatically
auto_date_template = date_template.partial(date=get_current_date)

print("\n=== Partial with auto function (date is always today) ===")
print(auto_date_template.format(question="What day is it?"))
print(auto_date_template.format(question="Is today a weekday?"))

# ---- ChatPromptTemplate partial ----
chat_template = ChatPromptTemplate.from_messages([
    ("system", "You are a {subject} teacher. Teach in {style} style."),
    ("human",  "{question}")
])

# Fix subject now
math_teacher = chat_template.partial(subject="math", style="simple and visual")

print("\n=== ChatPromptTemplate partial ===")
chain = math_teacher | model
result = chain.invoke({"question": "What is a fraction?"})
print(result.content)

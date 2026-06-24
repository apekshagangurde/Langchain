# ==============================================================
# WHAT IS A PROMPT TEMPLATE?
# ==============================================================
#
# SIMPLE DEFINITION:
#   A Prompt Template is like a "fill-in-the-blank" sentence.
#
# EXAMPLE IN REAL LIFE:
#   "Dear {name}, your order {order_id} has been shipped."
#    → Fill name="Apeksha", order_id="1234"
#    → "Dear Apeksha, your order 1234 has been shipped."
#
# WHY DO WE NEED IT?
#   Without template:
#     prompt1 = "Explain Python to a beginner"
#     prompt2 = "Explain JavaScript to a beginner"
#     prompt3 = "Explain Java to a beginner"
#     → You rewrite the same sentence 100 times. BAD!
#
#   With template:
#     template = "Explain {language} to a beginner"
#     → Change just the variable. GOOD!
#
# IN LANGCHAIN there are 2 main types:
#   1. PromptTemplate       → simple text (one block of text)
#   2. ChatPromptTemplate   → chat style (system + human + ai roles)
# ==============================================================

from langchain_core.prompts import PromptTemplate

# ---- BASIC: Create a template with ONE variable ----
template = PromptTemplate(
    input_variables=["language"],
    template="Explain {language} to a 10 year old in 2 sentences."
)

# Fill the blank → this gives you the final string
prompt1 = template.format(language="Python")
prompt2 = template.format(language="JavaScript")
prompt3 = template.format(language="Machine Learning")

print("=== Prompt 1 ===")
print(prompt1)

print("\n=== Prompt 2 ===")
print(prompt2)

print("\n=== Prompt 3 ===")
print(prompt3)

# ---- SHORTCUT: from_template (most common way) ----
# You don't need to list input_variables separately
short_template = PromptTemplate.from_template(
    "What is the capital of {country}? Answer in one word."
)

print("\n=== Shortcut Style ===")
print(short_template.format(country="India"))
print(short_template.format(country="France"))

# ---- MULTIPLE VARIABLES ----
multi_template = PromptTemplate.from_template(
    "Write a {tone} email to {person} about {topic}."
)

print("\n=== Multiple Variables ===")
print(multi_template.format(tone="formal", person="the manager", topic="project delay"))
print(multi_template.format(tone="friendly", person="my colleague", topic="team lunch"))

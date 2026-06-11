# ==============================================================
# FEW-SHOT PROMPT TEMPLATES
# ==============================================================
#
# WHAT IS FEW-SHOT PROMPTING?
#   You show the AI a few EXAMPLES before asking your real question.
#   The AI learns the pattern from examples and follows it.
#
# ANALOGY:
#   Teacher: "Convert to past tense. Example: run → ran, eat → ate"
#   Student: "Now do: swim → ?"
#   Student answers: "swam"  ← learned from examples!
#
# WHEN TO USE IT?
#   → When you want output in a VERY SPECIFIC format
#   → When the AI keeps getting the format wrong
#   → When you want consistent style every time
#
# FewShotPromptTemplate has 3 parts:
#   1. examples      → list of input/output pairs to show
#   2. example_prompt → how to format each example
#   3. suffix        → the actual question at the end
# ==============================================================

from langchain_core.prompts import FewShotPromptTemplate, PromptTemplate
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
model = ChatGroq(model="llama-3.1-8b-instant")

# ---- EXAMPLE 1: Sentiment Analysis with consistent format ----

examples = [
    {"review": "This phone is amazing! Best purchase ever.",  "sentiment": "POSITIVE"},
    {"review": "The battery died after 2 hours. Terrible.",   "sentiment": "NEGATIVE"},
    {"review": "It's okay. Nothing special.",                  "sentiment": "NEUTRAL"},
]

# How to display each example to the model
example_format = PromptTemplate.from_template(
    "Review: {review}\nSentiment: {sentiment}"
)

# Full few-shot template
few_shot = FewShotPromptTemplate(
    examples=examples,
    example_prompt=example_format,
    prefix="Classify the sentiment of reviews. Use only: POSITIVE, NEGATIVE, or NEUTRAL.\n",
    suffix="Review: {review}\nSentiment:",
    input_variables=["review"]
)

print("=== Generated Prompt (what model actually sees) ===")
print(few_shot.format(review="The screen cracked on the first day."))

print("\n=== Model Answer ===")
result = model.invoke(few_shot.format(review="The screen cracked on the first day."))
print(result.content)

result2 = model.invoke(few_shot.format(review="Absolutely love this product! 10/10"))
print(result2.content)

# ---- EXAMPLE 2: Format conversion — JSON output ----

json_examples = [
    {"sentence": "John is 25 years old and lives in Paris.",
     "output": '{{"name": "John", "age": 25, "city": "Paris"}}'},
    {"sentence": "Maria is 30 years old and lives in Tokyo.",
     "output": '{{"name": "Maria", "age": 30, "city": "Tokyo"}}'},
]

json_format = PromptTemplate.from_template(
    "Sentence: {sentence}\nJSON: {output}"
)

json_few_shot = FewShotPromptTemplate(
    examples=json_examples,
    example_prompt=json_format,
    prefix="Extract person info from sentences and return as JSON.\n",
    suffix="Sentence: {sentence}\nJSON:",
    input_variables=["sentence"]
)

print("\n\n=== JSON Extraction Few-Shot ===")
result3 = model.invoke(json_few_shot.format(sentence="Alex is 22 years old and lives in London."))
print(result3.content)

# ==============================================================
# SAVING & LOADING PROMPT TEMPLATES
# ==============================================================
#
# WHAT IS IT?
#   LangChain lets you SAVE a prompt template to a JSON file
#   and LOAD it back later — without rewriting Python code.
#
# WHY IS THIS USEFUL?
#
#   PROBLEM without save/load:
#     Prompts are hardcoded inside Python files.
#     → Want to change wording? Edit code → redeploy. BAD!
#
#   SOLUTION with save/load:
#     Store prompt in a .json file.
#     → Want to change wording? Edit the .json only. GOOD!
#
# REAL WORLD USE CASES:
#   1. Non-technical team edits prompts without touching Python
#   2. You have 50 different prompts → each gets its own .json
#   3. Different prompts per customer / language / product
#   4. Version-control prompts like config files
#   5. Share a prompt with a colleague — just send the .json
#
# MODERN API (LangChain 1.x+):
#   Old (deprecated): template.save() / load_prompt()
#   New (current):    dumps() / loads() from langchain_core.load
# ==============================================================

import os
import json
from langchain_core.prompts import PromptTemplate
from langchain_core.load import dumps, loads      # modern serialize/deserialize
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()
model = ChatGroq(model="llama-3.1-8b-instant")

os.makedirs("saved_prompts", exist_ok=True)


# ==============================================================
# PART 1: Save and load a basic PromptTemplate
# ==============================================================

print("=" * 55)
print("PART 1: Basic save & load")
print("=" * 55)

# Step 1: Create template
explain_template = PromptTemplate.from_template(
    "Explain {topic} to a {audience} in 3 bullet points."
)

# Step 2: Serialize to JSON string using dumps()
json_string = dumps(explain_template)

# Step 3: Save that JSON string to a file
with open("saved_prompts/explain_template.json", "w") as f:
    f.write(json_string)

print("Saved: saved_prompts/explain_template.json")

# Step 4: See what the file looks like
print("\nJSON file content:")
print(json.dumps(json.loads(json_string), indent=2))

# Step 5: Load it back using loads()
with open("saved_prompts/explain_template.json") as f:
    loaded_template = loads(f.read(), allowed_objects="all")

print("\nLoaded back successfully!")
print("Type:", type(loaded_template))

# Step 6: Use it exactly like the original
prompt_text = loaded_template.format(topic="blockchain", audience="school student")
result = model.invoke(prompt_text)
print("\nModel response:")
print(result.content)


# ==============================================================
# PART 2: Save a partially-filled template
# ==============================================================

print("\n" + "=" * 55)
print("PART 2: Save a partial template (some vars pre-filled)")
print("=" * 55)

# Pre-fill "audience" permanently → now only "topic" is needed
beginner_template = explain_template.partial(audience="complete beginner")

json_string2 = dumps(beginner_template)
with open("saved_prompts/explain_beginner.json", "w") as f:
    f.write(json_string2)

print("Saved: saved_prompts/explain_beginner.json")

with open("saved_prompts/explain_beginner.json") as f:
    loaded_beginner = loads(f.read(), allowed_objects="all")

# Only pass "topic" — audience is already baked in
result2 = model.invoke(loaded_beginner.format(topic="cloud computing"))
print("\nResponse (audience pre-filled as 'complete beginner'):")
print(result2.content)


# ==============================================================
# PART 3: Real-world pattern — a prompt library
# ==============================================================

print("\n" + "=" * 55)
print("PART 3: Prompt library — load by task name")
print("=" * 55)

# Save multiple prompts for different tasks
task_templates = {
    "summarize": PromptTemplate.from_template(
        "Summarize the following text in {num_sentences} sentences:\n\n{text}"
    ),
    "translate": PromptTemplate.from_template(
        "Translate the following text to {language}:\n\n{text}"
    ),
    "quiz": PromptTemplate.from_template(
        "Create {num_questions} quiz questions about: {topic}"
    ),
}

for task_name, tmpl in task_templates.items():
    path = f"saved_prompts/{task_name}.json"
    with open(path, "w") as f:
        f.write(dumps(tmpl))
    print(f"Saved: {path}")

# App function: load prompt by name and run it
def run_task(task_name: str, inputs: dict) -> str:
    with open(f"saved_prompts/{task_name}.json") as f:
        template = loads(f.read(), allowed_objects="all")
    return model.invoke(template.format(**inputs)).content

print("\nRunning 'quiz' task loaded from file:")
print(run_task("quiz", {"num_questions": "3", "topic": "Python lists"}))


# ==============================================================
# PART 4: Edit the JSON by hand (no Python needed!)
# ==============================================================

print("\n" + "=" * 55)
print("PART 4: Hand-edit the JSON file → different output")
print("=" * 55)

# Load the saved quiz.json and change it manually in Python
# (simulating what a non-technical person would do in a text editor)

with open("saved_prompts/quiz.json") as f:
    raw = json.load(f)

# Change the template text directly in the JSON dict
old_template = raw["kwargs"]["template"]
new_template = old_template.replace(
    "Create {num_questions} quiz questions about: {topic}",
    "Create {num_questions} MULTIPLE CHOICE quiz questions about: {topic}. "
    "Add 4 options (A/B/C/D) and mark the correct answer."
)
raw["kwargs"]["template"] = new_template

with open("saved_prompts/quiz_mcq.json", "w") as f:
    json.dump(raw, f, indent=2)

print("Hand-edited and saved: saved_prompts/quiz_mcq.json")

with open("saved_prompts/quiz_mcq.json") as f:
    mcq_template = loads(f.read(), allowed_objects="all")

result3 = model.invoke(mcq_template.format(num_questions="2", topic="LangChain"))
print("\nMCQ output after hand-editing JSON:")
print(result3.content)


# ==============================================================
# SUMMARY
# ==============================================================

print("\n" + "=" * 55)
print("SUMMARY — What's inside the JSON file?")
print("=" * 55)
print("""
A saved PromptTemplate JSON looks like:

{
  "lc": 1,
  "type": "constructor",
  "id": ["langchain_core", "prompts", "prompt", "PromptTemplate"],
  "kwargs": {
    "input_variables": ["topic", "audience"],
    "template": "Explain {topic} to a {audience}..."
  }
}

KEY POINT:
  "template" is just a plain string inside the JSON.
  Anyone can open the file and change the wording.
  Your Python code stays the same — it just loads the file.
""")

# ==============================================================
# SEQUENTIAL CHAIN
# ==============================================================
#
# WHAT IS IT?
#   A sequential chain runs steps ONE AFTER ANOTHER.
#   The output of Chain 1 becomes the input of Chain 2.
#
# ANALOGY — Cooking process:
#   Buy groceries → Chop vegetables → Cook → Serve
#   Each step uses the result of the previous step.
#
# IN LANGCHAIN:
#   chain1 = prompt1 | model | parser      → produces some text
#   chain2 = prompt2 | model | parser      → takes that text
#
#   To connect: chain1 | transform_fn | chain2
#
# THE CHALLENGE:
#   Chain 1 output is a string.
#   Chain 2 prompt expects a dict like {"key": "value"}.
#   So you need a small bridge function to convert string → dict.
#
#   chain1 → "some text"
#            ↓
#          lambda text: {"key": text}   ← bridge function
#            ↓
#   chain2 → uses {"key": "some text"}
#
# REAL WORLD EXAMPLE:
#   Step 1: Generate a blog post about {topic}
#   Step 2: Summarize that blog post in 2 sentences
#   → Output of step 1 (full blog) feeds into step 2 (summary)
# ==============================================================

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda
from dotenv import load_dotenv

load_dotenv()
model = ChatGroq(model="llama-3.1-8b-instant")
parser = StrOutputParser()


# ==============================================================
# EXAMPLE 1 — Blog → Summary
# ==============================================================
print("=" * 55)
print("EXAMPLE 1: Blog post → Summary")
print("=" * 55)

# Chain 1: Write a blog post
blog_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a tech blogger."),
    ("human",  "Write a short blog post (100 words) about: {topic}")
])

# Chain 2: Summarize it
summary_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an editor. Summarize text concisely."),
    ("human",  "Summarize this in 1 sentence:\n\n{blog_text}")
])

# Build each chain separately
blog_chain    = blog_prompt    | model | parser
summary_chain = summary_prompt | model | parser

# Connect them — bridge the string output to a dict input
full_chain = (
    blog_chain
    | RunnableLambda(lambda text: {"blog_text": text})  # bridge
    | summary_chain
)

result = full_chain.invoke({"topic": "Python decorators"})
print("Final Summary:")
print(result)


# ==============================================================
# EXAMPLE 2 — 3-step chain: Question → Answer → Simplify
# ==============================================================
print("\n" + "=" * 55)
print("EXAMPLE 2: Question → Detailed Answer → Simple Version")
print("=" * 55)

# Step 1: Get a detailed answer
answer_prompt = ChatPromptTemplate.from_messages([
    ("human", "Answer this question in detail: {question}")
])

# Step 2: Simplify it for a child
simplify_prompt = ChatPromptTemplate.from_messages([
    ("human", "Rewrite this for a 10-year-old child:\n\n{detailed_answer}")
])

# Step 3: Convert to bullet points
bullet_prompt = ChatPromptTemplate.from_messages([
    ("human", "Convert this into 3 bullet points:\n\n{simple_text}")
])

three_step_chain = (
    (answer_prompt | model | parser)
    | RunnableLambda(lambda x: {"detailed_answer": x})
    | (simplify_prompt | model | parser)
    | RunnableLambda(lambda x: {"simple_text": x})
    | (bullet_prompt | model | parser)
)

result2 = three_step_chain.invoke({"question": "How does the internet work?"})
print(result2)


# ==============================================================
# EXAMPLE 3 — Using RunnablePassthrough to keep original input
# ==============================================================
print("\n" + "=" * 55)
print("EXAMPLE 3: Keep original question + add answer")
print("=" * 55)
#
# PROBLEM:
#   After chain1 runs, you lose the original "question".
#   What if chain2 needs BOTH the original question AND chain1's output?
#
# SOLUTION: RunnablePassthrough.assign()
#   It keeps everything from input AND adds new keys.
#
#   Input:  {"question": "What is AI?"}
#   After assign(answer=chain):
#           {"question": "What is AI?", "answer": "AI is..."}
#   Now both question and answer are available for next step!

from langchain_core.runnables import RunnablePassthrough

qa_chain = answer_prompt | model | parser

combined_chain = (
    RunnablePassthrough.assign(answer=qa_chain)   # adds "answer" key
    | ChatPromptTemplate.from_messages([
        ("human",
         "Question: {question}\nAnswer: {answer}\n\n"
         "Now rate the quality of this answer from 1-10 and explain why.")
    ])
    | model
    | parser
)

result3 = combined_chain.invoke({"question": "What is machine learning?"})
print(result3)

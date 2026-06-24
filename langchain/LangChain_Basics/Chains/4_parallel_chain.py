# ==============================================================
# PARALLEL CHAIN — RunnableParallel
# ==============================================================
#
# WHAT IS IT?
#   Run MULTIPLE chains at the SAME TIME on the SAME input.
#   All chains run simultaneously → results collected into a dict.
#
# ANALOGY — Restaurant kitchen:
#   One order comes in: "Give me a meal"
#   Chef 1 makes the starter  (runs in parallel)
#   Chef 2 makes the main     (runs in parallel)
#   Chef 3 makes the dessert  (runs in parallel)
#   All done → serve together on one plate
#
# WITHOUT PARALLEL (sequential — slow):
#   pros   = pros_chain.invoke(input)     # wait 2 seconds
#   cons   = cons_chain.invoke(input)     # wait 2 seconds
#   Total: 4 seconds
#
# WITH PARALLEL (simultaneous — fast):
#   result = parallel_chain.invoke(input) # both run at same time
#   Total: 2 seconds  ← FASTER!
#
# STRUCTURE:
#   RunnableParallel(
#       key1 = chain_1,
#       key2 = chain_2,
#       key3 = chain_3,
#   )
#   → returns {"key1": result1, "key2": result2, "key3": result3}
#
# WHEN TO USE:
#   → When you need multiple perspectives on the same input
#   → When steps are INDEPENDENT (don't need each other's output)
#   → When speed matters
# ==============================================================

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
import time
from dotenv import load_dotenv

load_dotenv()
model = ChatGroq(model="llama-3.1-8b-instant")
parser = StrOutputParser()


# ==============================================================
# NOTES + QUIZ → MERGE  (parallel then combine)
# ==============================================================
#
# CHAIN STRUCTURE:
#
#          topic
#            ↓
#   ┌────────────────────┐
#   │   RunnableParallel │
#   │  ┌──────────────┐  │
#   │  │ notes_chain  │  │  ← prompt1 | model | parser
#   │  └──────────────┘  │
#   │  ┌──────────────┐  │
#   │  │  quiz_chain  │  │  ← prompt2 | model | parser
#   │  └──────────────┘  │
#   └────────────────────┘
#            ↓
#   {"notes": "...", "quiz": "..."}
#            ↓
#      merge_prompt        ← prompt3: combine notes + quiz
#            ↓
#          model
#            ↓
#          parser
#            ↓
#      final study guide
#
# ==============================================================

print("=" * 55)
print("NOTES + QUIZ → MERGE (parallel chains)")
print("=" * 55)

# Prompt 1 — short notes on a topic
notes_prompt = ChatPromptTemplate.from_template(
    "Create simple and short notes on the topic: {topic}\n"
    "Use at most 5 bullet points. Keep each point one sentence."
)
notes_chain = notes_prompt | model | parser

# Prompt 2 — 5 short Q&A on the topic
quiz_prompt = ChatPromptTemplate.from_template(
    "Generate exactly 5 short question and answer pairs on: {topic}\n"
    "Format each as:\nQ: ...\nA: ..."
)
quiz_chain = quiz_prompt | model | parser

# Prompt 3 — merge notes and quiz into one study guide
merge_prompt = ChatPromptTemplate.from_template(
    "Merge the following notes and quiz into one clean study guide.\n\n"
    "NOTES:\n{notes}\n\n"
    "QUIZ:\n{quiz}\n\n"
    "Produce a single well-organised document with both sections."
)

# Run notes_chain and quiz_chain in PARALLEL, then pipe into merge
full_chain = (
    RunnableParallel(
        notes=notes_chain,
        quiz=quiz_chain,
    )
    | merge_prompt
    | model
    | parser
)

study_guide = full_chain.invoke({"topic": "Python decorators"})
print(study_guide)


# ==============================================================
# EXAMPLE 1 — Pros and Cons simultaneously
# ==============================================================
print("=" * 55)
print("EXAMPLE 1: Pros & Cons in parallel")
print("=" * 55)

pros_chain = (
    ChatPromptTemplate.from_messages([
        ("human", "List 3 pros of {technology} in bullet points.")
    ])
    | model | parser
)

cons_chain = (
    ChatPromptTemplate.from_messages([
        ("human", "List 3 cons of {technology} in bullet points.")
    ])
    | model | parser
)

parallel = RunnableParallel(pros=pros_chain, cons=cons_chain)

start = time.time()
result = parallel.invoke({"technology": "Artificial Intelligence"})
elapsed = time.time() - start

print(f"(Ran in {elapsed:.1f}s)\n")
print("PROS:")
print(result["pros"])
print("\nCONS:")
print(result["cons"])


# ==============================================================
# EXAMPLE 2 — Multi-perspective analysis
# ==============================================================
print("\n" + "=" * 55)
print("EXAMPLE 2: Same topic, 3 expert perspectives")
print("=" * 55)

def make_expert_chain(expert_role: str) -> object:
    return (
        ChatPromptTemplate.from_messages([
            ("system", f"You are a {expert_role}. Give your expert view."),
            ("human", "What do you think about {topic}? Answer in 2 sentences.")
        ])
        | model | parser
    )

multi_perspective = RunnableParallel(
    developer  = make_expert_chain("senior software developer"),
    ethicist   = make_expert_chain("AI ethics researcher"),
    economist  = make_expert_chain("economist"),
)

results = multi_perspective.invoke({"topic": "AI replacing human jobs"})

for role, opinion in results.items():
    print(f"\n[{role.upper()}]")
    print(opinion)


# ==============================================================
# EXAMPLE 3 — Parallel + merge results into one final output
# ==============================================================
print("\n" + "=" * 55)
print("EXAMPLE 3: Parallel → merge → final answer")
print("=" * 55)
#
# Pattern:
#   Input
#     ↓
#   [Parallel: get pros + cons]
#     ↓  returns {"pros": "...", "cons": "..."}
#   [Merge prompt: write a balanced verdict using both]
#     ↓
#   Final verdict

merge_prompt = ChatPromptTemplate.from_messages([
    ("human",
     "Based on these pros and cons, write a 2-sentence balanced verdict.\n\n"
     "PROS:\n{pros}\n\nCONS:\n{cons}")
])

full_analysis_chain = (
    RunnableParallel(pros=pros_chain, cons=cons_chain)
    | merge_prompt
    | model
    | parser
)

verdict = full_analysis_chain.invoke({"technology": "Social Media"})
print("Balanced Verdict:")
print(verdict)


# ==============================================================
# EXAMPLE 4 — Parallel with RunnablePassthrough (keep original input)
# ==============================================================
print("\n" + "=" * 55)
print("EXAMPLE 4: Keep original input + add parallel results")
print("=" * 55)
#
# RunnablePassthrough() → passes the original input dict unchanged
# Combined with parallel, you can keep the original question too.

enriched_chain = RunnableParallel(
    original   = RunnablePassthrough(),     # keeps original input as-is
    pros       = pros_chain,
    cons       = cons_chain,
)

enriched = enriched_chain.invoke({"technology": "Blockchain"})

print("Original input was:", enriched["original"])
print("\nPros (first 100 chars):", enriched["pros"][:100])
print("\nCons (first 100 chars):", enriched["cons"][:100])

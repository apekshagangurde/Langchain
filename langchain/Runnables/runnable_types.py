# ==============================================================
# RUNNABLES IN LANGCHAIN — Complete Theory
# ==============================================================
#
# WHAT IS A RUNNABLE?
#   A Runnable is anything that has a .invoke() method.
#   It takes an input, does something with it, and returns output.
#   Every step you connect with the | pipe operator MUST be a Runnable.
#
#   prompt | model | parser
#     ↑         ↑       ↑
#  Runnable  Runnable  Runnable
#
# There are TWO categories of Runnables in LangChain:
#
#   1. PRIMITIVE RUNNABLES   — control HOW data flows in a chain
#   2. TASK-SPECIFIC RUNNABLES — perform actual AI / NLP work
#
# ==============================================================


# ==============================================================
# CATEGORY 1 — PRIMITIVE RUNNABLES
# ==============================================================
#
# These are low-level building blocks.
# They do NOT know anything about LLMs, prompts, or AI.
# Their ONLY job is to control how data moves through the chain.
# Think of them as PLUMBING — pipes, splitters, valves.
#
# Imported from:  langchain_core.runnables
#
# ┌──────────────────────┬─────────────────────────────────────────────────────┐
# │ Primitive Runnable   │ What it does                                        │
# ├──────────────────────┼─────────────────────────────────────────────────────┤
# │ RunnableSequence     │ Connects steps one after another (created by |)     │
# │                      │ Output of step 1 → Input of step 2 → ...           │
# │                      │ You never write it directly — | creates it for you  │
# ├──────────────────────┼─────────────────────────────────────────────────────┤
# │ RunnableParallel     │ Runs multiple chains AT THE SAME TIME               │
# │                      │ All branches get the SAME input                     │
# │                      │ Returns a dict: {"key1": result1, "key2": result2} │
# ├──────────────────────┼─────────────────────────────────────────────────────┤
# │ RunnablePassthrough  │ Passes the input through UNCHANGED                  │
# │                      │ Used to keep the original input alongside new data  │
# │                      │ Acts like a mirror — input goes in, same input out  │
# ├──────────────────────┼─────────────────────────────────────────────────────┤
# │ RunnableLambda       │ Wraps a plain Python function into a Runnable       │
# │                      │ Lets you plug any custom logic into a chain         │
# │                      │ RunnableLambda(my_func)  or just  lambda x: ...    │
# ├──────────────────────┼─────────────────────────────────────────────────────┤
# │ RunnableBranch       │ Picks ONE branch to run based on a condition        │
# │                      │ Like an if/elif/else inside a chain                 │
# │                      │ RunnableBranch((condition, chain), ..., default)    │
# └──────────────────────┴─────────────────────────────────────────────────────┘
#
#
# DETAILED BREAKDOWN — PRIMITIVE RUNNABLES
# ─────────────────────────────────────────
#
# ── RunnableSequence ─────────────────────────────────────────
#
#   WHAT:  Chains steps together so output of one feeds the next.
#   HOW:   Created automatically when you use the | operator.
#   USE:   Every single chain you write uses RunnableSequence.
#
#   EXAMPLE:
#     chain = prompt | model | parser
#     # This is actually: RunnableSequence(prompt, model, parser)
#     # You never need to write RunnableSequence(...) manually
#
#
# ── RunnableParallel ─────────────────────────────────────────
#
#   WHAT:  Splits one input into multiple branches and runs them
#          all at the SAME TIME (in parallel threads).
#   HOW:   RunnableParallel(key1=chain1, key2=chain2)
#   USE:   When you need multiple results from the same input
#          without waiting for each one to finish before starting
#          the next.
#
#   INPUT:   {"topic": "Python"}
#   OUTPUT:  {"notes": "...", "quiz": "..."}
#
#   VISUAL:
#             input
#               ↓
#       ┌───────┴────────┐
#       │                │
#     chain1           chain2      ← both run at same time
#       │                │
#       └───────┬────────┘
#               ↓
#        {"key1": ..., "key2": ...}
#
#
# ── RunnablePassthrough ──────────────────────────────────────
#
#   WHAT:  Copies the input and passes it forward without change.
#   HOW:   RunnablePassthrough()
#   USE 1: Inside RunnableParallel to keep original input alongside
#          results from other branches.
#   USE 2: In a chain where a later step needs the original input
#          but earlier steps already changed it.
#
#   INPUT:   {"topic": "Python"}
#   OUTPUT:  {"topic": "Python"}   ← exactly the same, unchanged
#
#   EXAMPLE:
#     RunnableParallel(
#         original = RunnablePassthrough(),   # ← keeps {"topic": "Python"}
#         summary  = summary_chain,           # ← adds the summary
#     )
#     OUTPUT: {"original": {"topic": "Python"}, "summary": "..."}
#
#
# ── RunnableLambda ───────────────────────────────────────────
#
#   WHAT:  Wraps any regular Python function into a Runnable.
#   WHY:   Plain Python functions are NOT Runnables, so you can't
#          use them directly in a chain with |.
#          RunnableLambda fixes that.
#   HOW:   RunnableLambda(my_function)
#
#   EXAMPLE:
#     def shout(text):
#         return text.upper() + "!!!"
#
#     chain = prompt | model | parser | RunnableLambda(shout)
#
#   SHORTCUT: you can often just write a lambda inline:
#     chain = prompt | model | parser | (lambda x: x.upper())
#
#
# ── RunnableBranch ───────────────────────────────────────────
#
#   WHAT:  Chooses ONE chain to run based on a condition.
#          Like if/elif/else but inside a chain.
#   HOW:   RunnableBranch(
#              (condition_fn, chain_if_true),
#              (condition_fn, chain_if_true),
#              default_chain,           ← runs if no condition matched
#          )
#
#   EXAMPLE:
#     RunnableBranch(
#         (lambda x: "python" in x["topic"].lower(), python_chain),
#         (lambda x: "java"   in x["topic"].lower(), java_chain),
#         general_chain,      ← default
#     )
#
# ==============================================================


# ==============================================================
# CATEGORY 2 — TASK-SPECIFIC RUNNABLES
# ==============================================================
#
# These are HIGH-LEVEL components that do the actual AI work.
# They are domain-aware — they understand prompts, LLMs, parsers.
# Under the hood they extend BaseRunnable, so you can pipe them
# with | just like primitive runnables.
# Think of them as WORKERS — each one has a specific job.
#
# Sub-categories:
#
# ── A. PROMPT RUNNABLES ──────────────────────────────────────
#
#   Imported from: langchain_core.prompts
#
#   ┌─────────────────────────┬────────────────────────────────────────────────┐
#   │ Runnable                │ What it does                                   │
#   ├─────────────────────────┼────────────────────────────────────────────────┤
#   │ PromptTemplate          │ Simple string template with {variable} slots   │
#   │                         │ Input: dict  →  Output: formatted string       │
#   ├─────────────────────────┼────────────────────────────────────────────────┤
#   │ ChatPromptTemplate      │ Multi-role prompt (system + human + AI turns)  │
#   │                         │ Input: dict  →  Output: list of messages       │
#   ├─────────────────────────┼────────────────────────────────────────────────┤
#   │ MessagesPlaceholder     │ Inserts a list of past messages (chat history) │
#   │                         │ into the prompt at a specific position         │
#   └─────────────────────────┴────────────────────────────────────────────────┘
#
#
# ── B. MODEL RUNNABLES ───────────────────────────────────────
#
#   Imported from: langchain_groq / langchain_openai / langchain_anthropic etc.
#
#   ┌─────────────────────────┬────────────────────────────────────────────────┐
#   │ Runnable                │ What it does                                   │
#   ├─────────────────────────┼────────────────────────────────────────────────┤
#   │ ChatGroq                │ Calls Groq-hosted models (llama, mixtral, etc) │
#   │ ChatOpenAI              │ Calls OpenAI models (GPT-4o, GPT-3.5, etc)    │
#   │ ChatAnthropic           │ Calls Anthropic Claude models                  │
#   │ ChatGoogleGenerativeAI  │ Calls Google Gemini models                     │
#   │ HuggingFaceEndpoint     │ Calls HuggingFace hosted or local models       │
#   ├─────────────────────────┼────────────────────────────────────────────────┤
#   │ ALL of the above:       │ Input: list of messages                        │
#   │                         │ Output: AIMessage object                       │
#   └─────────────────────────┴────────────────────────────────────────────────┘
#
#
# ── C. OUTPUT PARSER RUNNABLES ───────────────────────────────
#
#   Imported from: langchain_core.output_parsers
#
#   ┌──────────────────────────────┬─────────────────────────────────────────────┐
#   │ Runnable                     │ What it does                                │
#   ├──────────────────────────────┼─────────────────────────────────────────────┤
#   │ StrOutputParser              │ AIMessage  →  plain Python string           │
#   ├──────────────────────────────┼─────────────────────────────────────────────┤
#   │ JsonOutputParser             │ LLM JSON text  →  Python dict               │
#   ├──────────────────────────────┼─────────────────────────────────────────────┤
#   │ PydanticOutputParser         │ LLM JSON text  →  validated Pydantic object │
#   ├──────────────────────────────┼─────────────────────────────────────────────┤
#   │ CommaSeparatedListOutputParser│ "a, b, c"  →  ["a", "b", "c"]             │
#   ├──────────────────────────────┼─────────────────────────────────────────────┤
#   │ XMLOutputParser              │ LLM XML text  →  Python dict                │
#   └──────────────────────────────┴─────────────────────────────────────────────┘
#
# ==============================================================


# ==============================================================
# SIDE-BY-SIDE COMPARISON
# ==============================================================
#
#  ┌──────────────────────┬──────────────────────────────────────────────────┐
#  │                      │  PRIMITIVE RUNNABLES                             │
#  ├──────────────────────┼──────────────────────────────────────────────────┤
#  │ Purpose              │ Control data flow — sequence, split, merge,      │
#  │                      │ branch, pass-through, transform                  │
#  ├──────────────────────┼──────────────────────────────────────────────────┤
#  │ Domain knowledge     │ None — they don't know about LLMs or prompts     │
#  ├──────────────────────┼──────────────────────────────────────────────────┤
#  │ Examples             │ RunnableParallel, RunnablePassthrough,           │
#  │                      │ RunnableLambda, RunnableBranch                   │
#  ├──────────────────────┼──────────────────────────────────────────────────┤
#  │ Imported from        │ langchain_core.runnables                         │
#  ├──────────────────────┼──────────────────────────────────────────────────┤
#  │ Analogy              │ Plumbing — pipes, valves, splitters              │
#  └──────────────────────┴──────────────────────────────────────────────────┘
#
#  ┌──────────────────────┬──────────────────────────────────────────────────┐
#  │                      │  TASK-SPECIFIC RUNNABLES                         │
#  ├──────────────────────┼──────────────────────────────────────────────────┤
#  │ Purpose              │ Do real AI work — format prompts, call LLMs,    │
#  │                      │ parse structured output                          │
#  ├──────────────────────┼──────────────────────────────────────────────────┤
#  │ Domain knowledge     │ Full — they understand messages, tokens, schemas │
#  ├──────────────────────┼──────────────────────────────────────────────────┤
#  │ Examples             │ ChatPromptTemplate, ChatGroq, StrOutputParser,   │
#  │                      │ JsonOutputParser, PydanticOutputParser           │
#  ├──────────────────────┼──────────────────────────────────────────────────┤
#  │ Imported from        │ langchain_core.prompts / langchain_groq /        │
#  │                      │ langchain_openai / langchain_core.output_parsers │
#  ├──────────────────────┼──────────────────────────────────────────────────┤
#  │ Analogy              │ Workers — each one has a specialised job         │
#  └──────────────────────┴──────────────────────────────────────────────────┘
#
# ==============================================================


# ==============================================================
# HOW THEY WORK TOGETHER — THE BIG PICTURE
# ==============================================================
#
#  A real chain uses BOTH types together:
#
#  prompt | model | parser
#    ↑         ↑       ↑
#  Task      Task    Task       ← Task-Specific Runnables do the AI work
#
#  RunnableParallel(
#      notes = prompt1 | model | parser,    ← Task-Specific inside
#      quiz  = prompt2 | model | parser,    ← Task-Specific inside
#  )
#  ↑
#  Primitive                               ← Primitive controls the flow
#
#  RULE OF THUMB:
#    Task-Specific  →  fills the SLOTS in a chain (what each step does)
#    Primitive      →  controls the SHAPE of the chain (how steps connect)
#
# ==============================================================


# ==============================================================
# QUICK REFERENCE — WHAT TO IMPORT AND WHEN
# ==============================================================
#
#  Need to...                             Import
#  ─────────────────────────────────────  ────────────────────────────────────
#  Run two chains at the same time        RunnableParallel  (langchain_core.runnables)
#  Keep original input in a parallel      RunnablePassthrough (langchain_core.runnables)
#  Put a Python function in a chain       RunnableLambda    (langchain_core.runnables)
#  Add if/else logic in a chain           RunnableBranch    (langchain_core.runnables)
#
#  Format a prompt with variables         ChatPromptTemplate (langchain_core.prompts)
#  Call an LLM (Groq)                     ChatGroq           (langchain_groq)
#  Call an LLM (OpenAI)                   ChatOpenAI         (langchain_openai)
#  Get a plain string from LLM            StrOutputParser    (langchain_core.output_parsers)
#  Get a dict (JSON) from LLM             JsonOutputParser   (langchain_core.output_parsers)
#  Get a validated object from LLM        PydanticOutputParser (langchain_core.output_parsers)
#
# ==============================================================

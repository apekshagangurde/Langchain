# 🌸 LangChain Learning Path — Beginner to Intermediate

A hands-on, step-by-step guide to learning LangChain with Python.
Every folder builds on the one before it — follow the order below and you will
go from "what is an LLM?" to building structured AI pipelines.

---

## 🌱 Setup — Do This First

```bash
# 1. Create a virtual environment
python -m venv venv
source venv/bin/activate        # macOS / Linux
# venv\Scripts\activate         # Windows

# 2. Install all dependencies
pip install -r requirements.txt

# 3. Add your API keys
cp .env.example .env            # then open .env and fill in your keys
```

Your `.env` file should contain the keys for the providers you want to use:

```
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
GROQ_API_KEY=...
HUGGINGFACEHUB_API_TOKEN=...
```

> You don't need all keys to get started — **Groq is free** and used in most
> examples. Sign up at [console.groq.com](https://console.groq.com) to get a
> free API key in 2 minutes.

---

## 🌻 Learning Path — Follow This Order

```
🌸 Step 1 → LLMs/
🌼 Step 2 → ChatModels/
🌺 Step 3 → LangChain_Basics/
               ├── Messages/
               ├── Prompt_Templates/
               ├── Chains/
               └── Simple_Chatbot/
🌷 Step 4 → Embedded_Models/
🌹 Step 5 → Output_Parsers/
🌟 Step 6 → Structured_Output/
```

---

## 🌸 Step 1 — `LLMs/`

**What you learn:** What an LLM is and how to call one directly.

| File | What it teaches |
|------|----------------|
| `1_llm_demo.py` | Call a basic LLM, understand input → output |

> This is the foundation. An LLM takes text in and gives text back.
> Everything else in this repo builds on this idea.

---

## 🌼 Step 2 — `ChatModels/`

**What you learn:** The difference between a raw LLM and a Chat Model.
Chat models understand conversation roles (system, human, AI).

| File | What it teaches |
|------|----------------|
| `1_chatmodel_openai.py` | ChatGPT via OpenAI API |
| `2_chatmodel_anthropic.py` | Claude via Anthropic API |
| `3_chatmodel_google.py` | Gemini via Google API |
| `4_chatmodle_hf_api.py` | HuggingFace models via cloud API |
| `5_chatmodel_hf_local.py` | Run a HuggingFace model on your own machine |

> **Tip for beginners:** Start with `1_chatmodel_openai.py` or
> `3_chatmodel_google.py` — both have generous free tiers.

---

## 🌺 Step 3 — `LangChain_Basics/`

The core of this repo. Work through the sub-folders **in order**.

### 📂 `Messages/`

**What you learn:** The three message types LangChain uses — SystemMessage,
HumanMessage, AIMessage — and why roles matter in a conversation.

| File | What it teaches |
|------|----------------|
| `about_messages.py` | Message types, how to construct and use them |

---

### 📂 `Prompt_Templates/`

**What you learn:** How to build reusable, dynamic prompts instead of
hardcoding strings.

| File | What it teaches |
|------|----------------|
| `1_what_is_prompt_template.py` | Basic PromptTemplate — fill in variables |
| `2_chat_prompt_template.py` | ChatPromptTemplate for multi-turn prompts |
| `3_partial_templates.py` | Pre-fill some variables, leave others open |
| `4_few_shot_prompting.py` | Give the LLM examples to follow |
| `5_messages_placeholder.py` | Inject conversation history into a prompt |
| `6_advanced_dynamic_prompt.py` | Build prompts that change based on logic |
| `7_save_and_load_template.py` | Save a prompt to a file and reload it |

---

### 📂 `Chains/`

**What you learn:** How to connect prompts, models, and parsers together into
a pipeline using the `|` operator (LCEL — LangChain Expression Language).

| File | What it teaches |
|------|----------------|
| `1_what_is_a_chain.py` | What a chain is — the core idea |
| `2_simple_chain_deep_dive.py` | Deep dive into how one chain step works |
| `3_sequential_chain.py` | Run steps one after another |
| `4_parallel_chain.py` | Run multiple steps at the same time |
| `5_runnable_lambda_passthrough.py` | Transform data mid-chain |
| `6_branching_conditional_chain.py` | Branch the chain based on input |
| `7_real_world_chain.py` | A realistic end-to-end example |

---

### 📂 `Simple_Chatbot/`

**What you learn:** Put everything together — build an interactive chatbot
that remembers the conversation history.

| File | What it teaches |
|------|----------------|
| `chatbot.py` | A full chatbot loop with memory |

---

## 🌷 Step 4 — `Embedded_Models/`

**What you learn:** How to turn text into numbers (vectors/embeddings).
This is the foundation for search, similarity, and RAG (Retrieval-Augmented
Generation).

| File | What it teaches |
|------|----------------|
| `1_embedding_openai_query.py` | Generate embeddings with OpenAI |
| `2.emdedding_hf_local.py` | Generate embeddings locally with HuggingFace |

---

## 🌹 Step 5 — `Output_Parsers/`

**What you learn:** How to control and parse the LLM's output — from raw
strings to structured Python objects.

| File | What it teaches |
|------|----------------|
| `output_parsers.py` | Overview of all parser types |
| `str_parser_compare.py` | `StrOutputParser` — with vs without it |
| `json_parser.py` | `JsonOutputParser` — get structured dicts from the LLM |
| `pydantic_parser.py` | `PydanticOutputParser` — validated Pydantic objects from LLM chains |

---

## 🌟 Step 6 — `Structured_Output/`

**What you learn:** How to make the LLM return output that exactly matches a
Pydantic schema — the most reliable way to get structured data.

| File | What it teaches |
|------|----------------|
| `structured_output.py` | `.with_structured_output()` — schema-enforced replies |

---

## 🗂️ Reference — `saved_prompts/`

Pre-built prompt templates saved as JSON files. These are ready to load and
reuse in your own projects. See `7_save_and_load_template.py` in
`Prompt_Templates/` for how to load them.

| File | Purpose |
|------|---------|
| `explain_beginner.json` | Explain a concept to a beginner |
| `explain_template.json` | General explanation template |
| `quiz.json` | Generate quiz questions |
| `quiz_mcq.json` | Generate multiple-choice quiz questions |
| `summarize.json` | Summarize a piece of text |
| `translate.json` | Translate text to another language |

---

## 📦 Project Structure

```
LangChain models/
│
├── 🌸 LLMs/                    ← Step 1: Raw LLM basics
├── 🌼 ChatModels/              ← Step 2: Chat models (OpenAI, Anthropic, etc.)
├── 🌺 LangChain_Basics/        ← Step 3: Core LangChain concepts
│   ├── Messages/               │   Message types (System, Human, AI)
│   ├── Prompt_Templates/       │   Dynamic reusable prompts
│   ├── Chains/                 │   Pipelines with |  operator (LCEL)
│   └── Simple_Chatbot/         │   Full chatbot with memory
├── 🌷 Embedded_Models/         ← Step 4: Text embeddings / vectors
├── 🌹 Output_Parsers/          ← Step 5: Parse LLM output (str, JSON)
├── 🌟 Structured_Output/       ← Step 6: Schema-enforced structured output
│
├── saved_prompts/              ← Reusable JSON prompt templates
├── requirements.txt            ← All Python dependencies
└── .env                        ← Your API keys (never commit this!)
```

---

## 💡 Tips for Beginners

- **Run each file on its own** — `python filename.py` — and read the output carefully.
- **Read the docstring at the top** of every file before running it. Each file
  explains the concept in plain English before showing the code.
- **Files are numbered** inside each folder — always start from `1_`.
- If a file fails, check your `.env` has the right API key for that provider.
- `Groq` is used in most examples — it's free and fast.

---

## 🚀 Quick Start (TL;DR)

```bash
# 1. Install
pip install -r requirements.txt

# 2. Add Groq API key to .env
echo "GROQ_API_KEY=your_key_here" >> .env

# 3. Run your first file
python LLMs/1_llm_demo.py
```

Then follow the learning path from Step 1 to Step 6. Happy learning! 🌸

# ==============================================================
# RAG (RETRIEVAL-AUGMENTED GENERATION) — Theory
# ==============================================================
#
# WHAT IS RAG?
#   RAG is a technique that lets an LLM answer questions using YOUR OWN
#   data (PDFs, docs, notes, a website, a database) instead of relying only
#   on what it memorized during training.
#
#   The core idea in one line:
#     "Find the relevant pieces of YOUR data, then hand them to the LLM
#      as context, and let it answer using that context."
#
# WHY DO WE NEED RAG?
#   LLMs have two big limitations on their own:
#     1. Knowledge cutoff — they don't know about your private documents,
#        recent events, or anything created after their training data.
#     2. Hallucination — when they don't know something, they may
#        confidently make up a wrong answer instead of saying "I don't know".
#
#   RAG fixes both by GROUNDING the LLM's answer in real text retrieved
#   from your own data at the moment the question is asked.
#
# ==============================================================


# ==============================================================
# THE RAG PIPELINE — STEP BY STEP
# ==============================================================
#
#   There are two phases: INDEXING (done once, ahead of time) and
#   RETRIEVAL + GENERATION (done every time a user asks a question).
#
#  ── PHASE 1: INDEXING (build the searchable knowledge base) ──
#
#   1. LOAD       Read raw data from its source.
#                 (a .txt file, PDF, webpage, database, etc.)
#                 Tool: DocumentLoaders (e.g. TextLoader, PyPDFLoader)
#
#   2. SPLIT      Break long documents into small chunks.
#                 LLMs and embeddings work best on small, focused pieces —
#                 not one giant wall of text.
#                 Tool: RecursiveCharacterTextSplitter
#
#   3. EMBED      Convert each text chunk into a vector (a list of numbers)
#                 that captures its MEANING. Similar meaning → similar vector.
#                 Tool: OpenAIEmbeddings, HuggingFaceEmbeddings, etc.
#
#   4. STORE      Save all those vectors in a Vector Store (a database
#                 built for fast similarity search over vectors).
#                 Tool: InMemoryVectorStore, FAISS, Chroma, Pinecone, etc.
#
#  ── PHASE 2: RETRIEVAL + GENERATION (runs per user question) ──
#
#   5. RETRIEVE   Embed the user's QUESTION the same way, then search the
#                 vector store for the chunks whose vectors are CLOSEST in
#                 meaning to the question. These are the "relevant docs".
#                 Tool: retriever = vector_store.as_retriever()
#
#   6. AUGMENT    Insert the retrieved chunks into the prompt as "context",
#                 alongside the original question.
#                 e.g. "Context: {retrieved chunks}\nQuestion: {question}"
#
#   7. GENERATE   Send the augmented prompt to the LLM. It answers using
#                 the provided context instead of guessing from memory.
#                 Tool: any chat model (ChatGroq, ChatOpenAI, etc.)
#
# ==============================================================


# ==============================================================
# VISUAL — THE WHOLE FLOW
# ==============================================================
#
#  INDEXING (once, offline)
#  ─────────────────────────
#    raw documents
#         │  LOAD
#         ▼
#    full documents
#         │  SPLIT
#         ▼
#    small chunks
#         │  EMBED
#         ▼
#    vectors  ──STORE──►  [ Vector Store ]
#
#
#  RETRIEVAL + GENERATION (every question)
#  ──────────────────────────────────────────
#    user question
#         │  EMBED question
#         ▼
#    question vector
#         │  search [ Vector Store ] for closest chunk vectors
#         ▼
#    relevant chunks  ──AUGMENT──►  prompt = context + question
#                                          │
#                                          ▼
#                                       LLM  ──GENERATE──►  final answer
#
# ==============================================================


# ==============================================================
# KEY TERMS — QUICK REFERENCE
# ==============================================================
#
#  ┌───────────────────┬────────────────────────────────────────────────┐
#  │ Term               │ Meaning                                        │
#  ├───────────────────┼────────────────────────────────────────────────┤
#  │ Document            │ A piece of text + metadata (e.g. source file)  │
#  ├───────────────────┼────────────────────────────────────────────────┤
#  │ Chunk                │ A small slice of a document after splitting  │
#  ├───────────────────┼────────────────────────────────────────────────┤
#  │ Embedding            │ A vector of numbers representing meaning      │
#  ├───────────────────┼────────────────────────────────────────────────┤
#  │ Vector Store         │ A database optimized for similarity search    │
#  │                      │ over embeddings                               │
#  ├───────────────────┼────────────────────────────────────────────────┤
#  │ Retriever            │ A Runnable that takes a query string and      │
#  │                      │ returns the most relevant chunks               │
#  ├───────────────────┼────────────────────────────────────────────────┤
#  │ Context              │ The retrieved chunks, inserted into the       │
#  │                      │ prompt so the LLM can use them                 │
#  ├───────────────────┼────────────────────────────────────────────────┤
#  │ Grounding             │ Making the LLM base its answer on real,      │
#  │                      │ retrieved text instead of guessing            │
#  └───────────────────┴────────────────────────────────────────────────┘
#
# ==============================================================


# ==============================================================
# WHY RETRIEVERS ARE RUNNABLES
# ==============================================================
#
#   A LangChain retriever has .invoke() just like everything else, so it
#   plugs straight into an LCEL chain using | and RunnableParallel —
#   no special-casing needed.
#
#     retriever = vector_store.as_retriever()
#
#     rag_chain = (
#         {"context": retriever, "question": RunnablePassthrough()}
#         | prompt
#         | llm
#         | parser
#     )
#
#   Read left to right:
#     - retriever runs on the question → relevant chunks
#     - RunnablePassthrough() keeps the original question untouched
#     - both get merged into {"context": ..., "question": ...}
#     - that dict fills the {context} and {question} slots in the prompt
#     - the LLM generates the final answer, grounded in the context
#
#   See rag_basic.py in this folder for a full working example.
#
# ==============================================================

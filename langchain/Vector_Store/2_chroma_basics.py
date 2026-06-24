# ==============================================================
# CHROMA VECTOR STORE — Basics
# ==============================================================
#
# WHAT IS CHROMA?
#   Chroma is an open-source vector database designed for AI apps.
#   It stores embeddings and lets you search by meaning.
#   It's one of the easiest vector stores to get started with.
#
# WHY CHROMA?
#   - Free and open source
#   - Works locally (no cloud setup needed)
#   - Supports persistent storage (saves data to disk)
#   - Built-in metadata filtering
#   - Easy integration with LangChain
#
# TWO MODES:
#   1. In-memory   → data lives in RAM, lost when app stops
#   2. Persistent   → data saved to a folder on disk, survives restarts
#
# INSTALL:
#   pip install langchain-chroma
#
# ==============================================================
#
#
# ==============================================================
# HOW CHROMA WORKS IN LANGCHAIN
# ==============================================================
#
#   1. Load & split your documents
#   2. Pick an embedding model
#   3. Create a Chroma vector store from the documents
#   4. Search or use as a retriever
#
# BASIC FLOW:
#
#   Documents ──► Chroma.from_documents(docs, embeddings)
#                        │
#                        ▼
#                  [ Chroma DB ]
#                        │
#       similarity_search("query") or .as_retriever()
#                        │
#                        ▼
#                  Matching chunks
#
# ==============================================================
#
#
# ==============================================================
# KEY CHROMA METHODS
# ==============================================================
#
#  ┌──────────────────────────┬──────────────────────────────────┐
#  │ Method                   │ What it does                     │
#  ├──────────────────────────┼──────────────────────────────────┤
#  │ Chroma.from_documents()  │ Create store from Documents      │
#  ├──────────────────────────┼──────────────────────────────────┤
#  │ Chroma.from_texts()      │ Create store from plain strings  │
#  ├──────────────────────────┼──────────────────────────────────┤
#  │ .add_documents()         │ Add more docs to existing store  │
#  ├──────────────────────────┼──────────────────────────────────┤
#  │ .similarity_search()     │ Find closest chunks to a query   │
#  ├──────────────────────────┼──────────────────────────────────┤
#  │ .similarity_search_with_ │ Same as above but also returns   │
#  │  score()                 │ the similarity score             │
#  ├──────────────────────────┼──────────────────────────────────┤
#  │ .as_retriever()          │ Convert to Retriever for chains  │
#  ├──────────────────────────┼──────────────────────────────────┤
#  │ .delete()                │ Remove documents by ID           │
#  └──────────────────────────┴──────────────────────────────────┘
#
# ==============================================================

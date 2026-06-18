# ==============================================================
# VECTOR STORE — Basics
# ==============================================================
#
# WHAT IS A VECTOR STORE?
#   A vector store is a database that stores text as vectors
#   (lists of numbers called embeddings) and lets you search
#   by MEANING instead of exact keywords.
#
# HOW IT WORKS:
#   1. Text chunks are converted into vectors using an embedding model.
#   2. These vectors are stored in the vector store.
#   3. When you ask a question, it is also converted into a vector.
#   4. The store finds the closest matching vectors (most similar meaning).
#
# WHY USE IT?
#   - Normal search matches exact words ("Python" finds "Python").
#   - Vector search matches meaning ("coding language" also finds "Python").
#
# WHERE IT FITS IN RAG:
#   LOAD → SPLIT → EMBED → STORE (you are here) → RETRIEVE → GENERATE
#
# POPULAR VECTOR STORES:
#   - FAISS         (Facebook, runs locally, fast)
#   - Chroma        (open source, easy to use)
#   - Pinecone      (cloud-based, managed service)
#   - InMemoryVectorStore (LangChain built-in, good for testing)
#
# ==============================================================
#
#
# ==============================================================
# VECTOR STORE vs VECTOR DATABASE
# ==============================================================
#
#  ┌────────────────────┬──────────────────────────┬──────────────────────────┐
#  │ Feature            │ Vector Store             │ Vector Database          │
#  ├────────────────────┼──────────────────────────┼──────────────────────────┤
#  │ Storage            │ In-memory (RAM)          │ On disk (persistent)     │
#  ├────────────────────┼──────────────────────────┼──────────────────────────┤
#  │ Data persists?     │ No — lost when app stops │ Yes — saved permanently  │
#  ├────────────────────┼──────────────────────────┼──────────────────────────┤
#  │ Speed              │ Very fast                │ Fast                     │
#  ├────────────────────┼──────────────────────────┼──────────────────────────┤
#  │ Scalability        │ Limited by RAM           │ Handles large datasets   │
#  ├────────────────────┼──────────────────────────┼──────────────────────────┤
#  │ Use case           │ Testing, prototyping,    │ Production apps,         │
#  │                    │ small datasets           │ large-scale RAG          │
#  ├────────────────────┼──────────────────────────┼──────────────────────────┤
#  │ CRUD operations    │ Basic (add, search)      │ Full (add, update,       │
#  │                    │                          │ delete, search)          │
#  ├────────────────────┼──────────────────────────┼──────────────────────────┤
#  │ Filtering          │ Limited                  │ Advanced metadata        │
#  │                    │                          │ filtering                │
#  ├────────────────────┼──────────────────────────┼──────────────────────────┤
#  │ Examples           │ FAISS,                   │ Pinecone, Weaviate,      │
#  │                    │ InMemoryVectorStore      │ Chroma, Milvus           │
#  └────────────────────┴──────────────────────────┴──────────────────────────┘
#
# In short:
#   Vector Store    = simple, temporary, good for learning & testing
#   Vector Database = full-featured, persistent, good for production
#
# ==============================================================
#
#
# ==============================================================
# VECTOR STORE IN LANGCHAIN
# ==============================================================
#
# LangChain provides a unified interface to work with any vector store.
# No matter which store you pick, the workflow is the same:
#
#   1. Create embeddings:
#        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
#
#   2. Build the vector store from documents:
#        vector_store = FAISS.from_documents(documents, embeddings)
#
#   3. Search (similarity search):
#        results = vector_store.similarity_search("your query", k=3)
#
#   4. Use as a retriever (for RAG chains):
#        retriever = vector_store.as_retriever()
#
# KEY METHODS:
#   .from_documents()     → create store from Document objects
#   .from_texts()         → create store from plain strings
#   .add_documents()      → add more documents to existing store
#   .similarity_search()  → find most similar chunks to a query
#   .as_retriever()       → convert to a Retriever for use in chains
#
# The biggest advantage: you can swap vector stores (FAISS → Chroma
# → Pinecone) by changing ONE line — the rest of your code stays the same.
#
# ==============================================================

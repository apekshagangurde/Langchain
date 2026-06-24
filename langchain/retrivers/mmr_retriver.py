"""
Maximal Marginal Relevance (MMR) Retriever
============================================
MMR is a retrieval strategy that balances relevance and diversity.
Instead of returning the most similar documents (which may be redundant),
MMR selects documents that are both relevant to the query AND different
from each other.

How it works:
1. Find documents similar to the query (relevance).
2. Among those, pick documents that are diverse from each other.
3. This avoids returning repetitive or overlapping results.

Formula:
  MMR = lambda * Similarity(query, doc) - (1 - lambda) * Max_Similarity(doc, selected_docs)

  - lambda close to 1 → more relevant results
  - lambda close to 0 → more diverse results

Flow:
------
  Query → Find Similar Docs → Re-rank for Diversity → Return Balanced Results
"""

# pip install faiss-cpu langchain-community langchain-huggingface

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Step 1: Create sample documents (some are intentionally similar)
docs = [
    Document(page_content="Machine learning is a branch of artificial intelligence."),
    Document(page_content="Machine learning uses data to train models."),
    Document(page_content="Deep learning is a type of machine learning."),
    Document(page_content="Python is used for web development."),
    Document(page_content="LangChain is a framework for building LLM apps."),
]

# Step 2: Create embeddings and vector store
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = FAISS.from_documents(docs, embeddings)

query = "What is machine learning?"

# --- Normal Similarity Search ---
print("=== Normal Similarity Search ===")
retriever_normal = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})
results = retriever_normal.invoke(query)
for i, doc in enumerate(results):
    print(f"Result {i+1}: {doc.page_content}")

# --- MMR Search (Relevance + Diversity) ---
print("\n=== MMR Search (Relevance + Diversity) ===")
retriever_mmr = vector_store.as_retriever(search_type="mmr", search_kwargs={"k": 3})
results = retriever_mmr.invoke(query)
for i, doc in enumerate(results):
    print(f"Result {i+1}: {doc.page_content}")

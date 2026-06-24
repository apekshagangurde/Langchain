"""
Vector Store Retriever
=======================
A Vector Store Retriever searches for similar documents by comparing
vector embeddings. It converts text into numerical vectors (embeddings)
and finds the closest matching documents using similarity search.

How it works:
1. Documents are split into chunks.
2. Each chunk is converted into a vector embedding.
3. Embeddings are stored in a vector store (e.g., FAISS, Chroma).
4. When a query comes in, it is also converted into an embedding.
5. The vector store finds the most similar document embeddings.
6. The matching documents are returned as results.

Flow:
------
  Documents → Split into Chunks → Convert to Embeddings → Store in Vector DB
  Query → Convert to Embedding → Search Vector DB → Return Similar Documents
"""

# pip install faiss-cpu langchain-community langchain-huggingface

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Step 1: Create sample documents
docs = [
    Document(page_content="Python is a popular programming language."),
    Document(page_content="Machine learning is a subset of AI."),
    Document(page_content="LangChain helps build LLM applications."),
    Document(page_content="FAISS is a library for similarity search."),
]

# Step 2: Create embeddings and vector store
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = FAISS.from_documents(docs, embeddings)

# Step 3: Create retriever from vector store
retriever = vector_store.as_retriever()

# Step 4: Query the retriever
query = "What is machine learning?"
results = retriever.invoke(query)

print(f"Query: {query}")
print(f"Number of results: {len(results)}")
for i, doc in enumerate(results):
    print(f"\nResult {i+1}: {doc.page_content}")

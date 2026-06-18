"""
Contextual Compression Retriever
==================================
The Contextual Compression Retriever takes retrieved documents and
compresses them to keep only the relevant parts based on the query.
Instead of returning full documents, it extracts or filters the
content that actually answers the user's question.

Why use it:
- Retrieved documents often contain irrelevant information.
- Compression reduces noise and keeps only useful content.
- This leads to better answers from the LLM.

How it works:
1. User provides a query.
2. Base retriever fetches matching documents.
3. A compressor filters or extracts relevant parts from each document.
4. Only the compressed, relevant content is returned.

Flow:
------
  Query → Base Retriever → Full Documents → Compressor → Compressed Documents
                                              ↓
                                   Removes irrelevant content
                                   Keeps only query-related parts
"""

# pip install faiss-cpu langchain-community langchain-huggingface langchain

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_classic.retrievers.document_compressors import EmbeddingsFilter
from langchain_classic.retrievers import ContextualCompressionRetriever

# Step 1: Create sample documents (with mixed content)
docs = [
    Document(page_content="Python was created by Guido van Rossum. It is great for data science and machine learning."),
    Document(page_content="JavaScript is used for web development. React and Angular are popular JS frameworks."),
    Document(page_content="Machine learning is a subset of AI. It uses algorithms to learn from data."),
    Document(page_content="The weather today is sunny. Deep learning uses neural networks."),
    Document(page_content="LangChain helps build applications powered by large language models."),
]

# Step 2: Create vector store and base retriever
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = FAISS.from_documents(docs, embeddings)
base_retriever = vector_store.as_retriever(search_kwargs={"k": 3})

query = "What is machine learning?"

# --- Without Compression ---
print("=== Without Compression (Full Documents) ===")
results = base_retriever.invoke(query)
for i, doc in enumerate(results):
    print(f"\nResult {i+1}: {doc.page_content}")

# --- With Contextual Compression ---
print("\n=== With Contextual Compression (Filtered) ===")
embeddings_filter = EmbeddingsFilter(embeddings=embeddings, similarity_threshold=0.5)

compression_retriever = ContextualCompressionRetriever(
    base_compressor=embeddings_filter,
    base_retriever=base_retriever,
)

compressed_results = compression_retriever.invoke(query)
for i, doc in enumerate(compressed_results):
    print(f"\nResult {i+1}: {doc.page_content}")

print(f"\nBefore compression: {len(results)} docs")
print(f"After compression: {len(compressed_results)} docs")

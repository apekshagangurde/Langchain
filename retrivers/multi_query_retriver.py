"""
Multi Query Retriever
======================
The Multi Query Retriever improves retrieval by generating multiple
variations of the user's query. Each variation is used to search
the vector store, and all results are combined and deduplicated.

Why use it:
- A single query may miss relevant documents due to wording.
- By rephrasing the query in different ways, we cast a wider net
  and retrieve more relevant results.

How it works:
1. User provides a single query.
2. Multiple variations of that query are generated.
3. Each variation is used to search the vector store.
4. Results from all searches are combined and duplicates are removed.
5. The final unique set of documents is returned.

Flow:
------
  User Query → Generate 3 query variations
       ↓
  Variation 1 → Search → Results
  Variation 2 → Search → Results  → Combine & Deduplicate → Final Documents
  Variation 3 → Search → Results
"""

# pip install faiss-cpu langchain-community langchain-huggingface

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# Step 1: Create sample documents
docs = [
    Document(page_content="Python is a popular programming language for data science."),
    Document(page_content="Machine learning models learn patterns from data."),
    Document(page_content="Deep learning uses neural networks with many layers."),
    Document(page_content="AI is transforming healthcare and finance industries."),
    Document(page_content="Natural language processing helps computers understand text."),
]

# Step 2: Create vector store
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = FAISS.from_documents(docs, embeddings)
retriever = vector_store.as_retriever(search_kwargs={"k": 2})

# Step 3: Define multiple query variations (in real use, an LLM generates these)
original_query = "Tell me about deep learning"
query_variations = [
    "Tell me about deep learning",
    "What are neural networks?",
    "How does AI use layers to learn?",
]

# Step 4: Search with each variation and combine results
all_results = []
seen_contents = set()

print(f"Original Query: {original_query}\n")

for i, query in enumerate(query_variations):
    results = retriever.invoke(query)
    print(f"Variation {i+1}: '{query}'")
    for doc in results:
        print(f"  → {doc.page_content}")
        if doc.page_content not in seen_contents:
            all_results.append(doc)
            seen_contents.add(doc.page_content)
    print()

# Step 5: Final deduplicated results
print(f"=== Final Combined Results (Deduplicated) ===")
print(f"Total unique documents: {len(all_results)}")
for i, doc in enumerate(all_results):
    print(f"\nResult {i+1}: {doc.page_content}")

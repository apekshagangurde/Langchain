# ==============================================================
# CHROMA VECTOR STORE — Full Operations
# ==============================================================

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document

# --- Setup Embeddings ---
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")


# ==============================================================
# 1. Create Document Objects
# ==============================================================

docs = [
    Document(
        page_content="Python is a popular programming language.",
        metadata={"source": "notes", "topic": "python"},
    ),
    Document(
        page_content="JavaScript is used for web development.",
        metadata={"source": "notes", "topic": "javascript"},
    ),
    Document(
        page_content="Machine learning is a branch of AI.",
        metadata={"source": "articles", "topic": "ml"},
    ),
    Document(
        page_content="React is a JavaScript library for building UIs.",
        metadata={"source": "articles", "topic": "javascript"},
    ),
    Document(
        page_content="Django is a Python web framework.",
        metadata={"source": "notes", "topic": "python"},
    ),
]

print("=== Created 5 Document Objects ===")
for i, doc in enumerate(docs):
    print(f"  {i + 1}. {doc.page_content} | metadata: {doc.metadata}")
print()


# ==============================================================
# 2. Create Vector Store with Collection Name & Persistent Storage
# ==============================================================

vector_store = Chroma.from_documents(
    documents=docs,
    embedding=embeddings,
    collection_name="my_collection",
    persist_directory="Vector_Store/chroma_db",
)

print("=== Vector Store Created ===")
print("  Collection: my_collection")
print("  Stored at: Vector_Store/chroma_db")
print()


# ==============================================================
# 3. Add More Documents using add_documents()
# ==============================================================

new_docs = [
    Document(
        page_content="Flask is a lightweight Python web framework.",
        metadata={"source": "notes", "topic": "python"},
    ),
    Document(
        page_content="TensorFlow is a popular ML framework by Google.",
        metadata={"source": "articles", "topic": "ml"},
    ),
]

new_ids = vector_store.add_documents(new_docs)

print("=== Added 2 New Documents ===")
print(f"  New document IDs: {new_ids}")
print()


# ==============================================================
# 4. View All Documents
# ==============================================================

all_docs = vector_store.get()

print("=== All Documents in Store ===")
print(f"  Total documents: {len(all_docs['ids'])}")
for i, (doc_id, content) in enumerate(zip(all_docs["ids"], all_docs["documents"])):
    print(f"  {i + 1}. ID: {doc_id[:8]}... | Content: {content}")
print()


# ==============================================================
# 5. Similarity Search (k=2)
# ==============================================================

results = vector_store.similarity_search("web framework", k=2)

print("=== Similarity Search: 'web framework' (k=2) ===")
for i, doc in enumerate(results):
    print(f"  {i + 1}. {doc.page_content}")
print()


# ==============================================================
# 6. Similarity Search with Score
# ==============================================================

results_with_score = vector_store.similarity_search_with_score("Python programming", k=2)

print("=== Similarity Search with Score: 'Python programming' (k=2) ===")
for i, (doc, score) in enumerate(results_with_score):
    print(f"  {i + 1}. {doc.page_content} | Score: {score:.4f}")
print()


# ==============================================================
# 7. Metadata Filtering
# ==============================================================

filtered_results = vector_store.similarity_search(
    "programming",
    k=3,
    filter={"topic": "python"},
)

print("=== Metadata Filtering: topic='python' ===")
for i, doc in enumerate(filtered_results):
    print(f"  {i + 1}. {doc.page_content} | metadata: {doc.metadata}")
print()


# ==============================================================
# 8. Update Document
# ==============================================================

updated_doc = Document(
    page_content="Python is the most popular programming language in 2026.",
    metadata={"source": "notes", "topic": "python"},
)

first_id = all_docs["ids"][0]
vector_store.update_document(document_id=first_id, document=updated_doc)

print("=== Updated Document ===")
print(f"  ID: {first_id[:8]}...")
print(f"  New content: {updated_doc.page_content}")
print()


# ==============================================================
# 9. Delete Document
# ==============================================================

delete_id = all_docs["ids"][1]
print(f"=== Deleting Document ===")
print(f"  ID: {delete_id[:8]}...")
print(f"  Content was: {all_docs['documents'][1]}")

vector_store.delete(ids=[delete_id])

remaining = vector_store.get()
print(f"  Documents remaining: {len(remaining['ids'])}")
print()

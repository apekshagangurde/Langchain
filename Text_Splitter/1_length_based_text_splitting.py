# ==============================================================
# LENGTH-BASED TEXT SPLITTING
# ==============================================================
#
# The simplest way to split text — cut it based on character count.
# You set a chunk_size (max characters per chunk) and an optional
# chunk_overlap (characters shared between chunks so context isn't lost).
#
# When to use:
#   When you just need quick, straightforward splitting and don't
#   care about preserving paragraph or sentence boundaries.
#
# ==============================================================

from langchain_text_splitters import CharacterTextSplitter

# Sample text
text = """Python is a popular programming language.
It is used for web development, data science, and AI.
Python is easy to learn and has a simple syntax.
Many developers love Python for its readability.
It has a large community and many useful libraries."""

# Create a length-based splitter
splitter = CharacterTextSplitter(chunk_size=100, chunk_overlap=20, separator="\n")

# Split the text
chunks = splitter.split_text(text)

# Print the chunks
for i, chunk in enumerate(chunks):
    print(f"--- Chunk {i + 1} ---")
    print(chunk)
    print()


# ==============================================================
# Example 2: Using split_documents()
# ==============================================================
# split_documents() works with Document objects instead of raw text.
# It keeps the metadata (like source file name) attached to each chunk.

from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("Loader/sample.pdf")
docs = loader.load()

split_docs = splitter.split_documents(docs)

for i, doc in enumerate(split_docs):
    print(f"--- Document Chunk {i + 1} ---")
    print(f"Content: {doc.page_content}")
    print(f"Metadata: {doc.metadata}")
    print()

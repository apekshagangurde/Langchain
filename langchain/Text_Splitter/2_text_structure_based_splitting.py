# ==============================================================
# TEXT STRUCTURE-BASED SPLITTING
# ==============================================================
#
# Instead of cutting text by character count, this approach splits
# based on the STRUCTURE of the text — paragraphs, sentences, etc.
# It uses RecursiveCharacterTextSplitter which tries separators
# in priority order: paragraphs → lines → words → characters.
#
# This preserves natural text boundaries and produces more
# meaningful chunks compared to simple length-based splitting.
#
# ==============================================================

from langchain_text_splitters import RecursiveCharacterTextSplitter

# Sample text with clear paragraph structure
text = """Python is a high-level programming language.
It was created by Guido van Rossum and released in 1991.

Python is widely used in web development.
Frameworks like Django and Flask make it easy to build web apps.

Python is also popular in data science.
Libraries like Pandas and NumPy are used for data analysis.

Machine learning is another major use of Python.
TensorFlow and PyTorch are two popular ML frameworks."""

# Create a recursive splitter
splitter = RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=20,
    separators=["\n\n", "\n", " ", ""]
)

chunks = splitter.split_text(text)

for i, chunk in enumerate(chunks):
    print(f"--- Chunk {i + 1} ---")
    print(chunk)
    print()


# ==============================================================
# Example 2: Using split_documents() with a PDF
# ==============================================================

from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("Loader/sample.pdf")
docs = loader.load()

split_docs = splitter.split_documents(docs)

for i, doc in enumerate(split_docs):
    print(f"--- Document Chunk {i + 1} ---")
    print(f"Content: {doc.page_content}")
    print(f"Metadata: {doc.metadata}")
    print()

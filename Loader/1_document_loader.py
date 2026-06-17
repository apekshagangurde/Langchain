"""
Document Loader — Reading Raw Data into LangChain Documents
==================================================================

What is a Document Loader?
  A component that reads data from a source (a .txt file, PDF, webpage,
  CSV, database, etc.) and converts it into LangChain Document objects.

What is a Document?
  A simple object with two parts:
    - page_content : the actual text
    - metadata      : extra info about it (e.g. source file path)

Why use a loader instead of just open(file).read()?
  Loaders give you a CONSISTENT output (a list of Document objects) no
  matter what the source is, so the rest of a RAG pipeline (splitter,
  embeddings, vector store) can work the same way regardless of where
  the data came from.

Common loaders (all imported from langchain_community.document_loaders):
  TextLoader        → loads a single .txt file
  PyPDFLoader        → loads a PDF, one Document per page
  CSVLoader          → loads a CSV, one Document per row
  WebBaseLoader      → loads and parses a webpage URL
"""

import os

from langchain_community.document_loaders import TextLoader

sample_path = os.path.join(os.path.dirname(__file__), "sample.txt")
loader = TextLoader(sample_path)
documents = loader.load()

print(f"Type        : {type(documents)}")        # list
print(f"Num documents: {len(documents)}")
print(f"page_content : {documents[0].page_content!r}")
print(f"metadata     : {documents[0].metadata}")

"""
TextLoader — Loading a Single .txt File
=============================================

What is TextLoader?
  A Document Loader that reads ONE plain text (.txt) file and returns it
  as a single LangChain Document.

When to use it:
  - Your source data is already a plain .txt file (notes, transcripts,
    exported chat logs, README files, etc.)
  - You just need the whole file as one Document — no per-page or
    per-row splitting like PyPDFLoader or CSVLoader do.
"""

import os

from langchain_community.document_loaders import TextLoader

sample_path = os.path.join(os.path.dirname(__file__), "sample.txt")
loader = TextLoader(sample_path)
documents = loader.load()

print(f"Num documents: {len(documents)}")          # 1 — whole file as one Document
print(f"page_content : {documents[0].page_content!r}")
print(f"metadata     : {documents[0].metadata}")    # {'source': 'sample.txt'}

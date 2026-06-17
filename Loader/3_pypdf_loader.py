"""
PyPDFLoader — Loading a PDF File
======================================

What is PyPDFLoader?
  A Document Loader that reads a PDF file and returns ONE Document PER
  PAGE (unlike TextLoader, which returns the whole file as a single
  Document).

When to use it:
  - Your source data is a PDF (reports, manuals, research papers, etc.)
  - You want page-level Documents, so each chunk later keeps track of
    which page it came from (useful for citing "page 3" in an answer).
"""

import os

from langchain_community.document_loaders import PyPDFLoader

sample_path = os.path.join(os.path.dirname(__file__), "sample.pdf")
loader = PyPDFLoader(sample_path)
documents = loader.load()

print(f"Num documents: {len(documents)}")          # 1 per page
for i, doc in enumerate(documents, start=1):
    print(f"Page {i} content : {doc.page_content!r}")
    print(f"Page {i} metadata: {doc.metadata}")      # includes 'page' number

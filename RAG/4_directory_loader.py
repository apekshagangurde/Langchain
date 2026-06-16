"""
DirectoryLoader — Loading Every File in a Folder
======================================================

What is DirectoryLoader?
  A Document Loader that loads ALL matching files inside a folder at
  once, instead of pointing a loader at one file at a time.

When to use it:
  - Your source data is a whole folder of files (e.g. a docs/ directory
    of .txt or .pdf files) and you want them all loaded with one call.
  - glob picks which files to include (e.g. "*.txt" for only text files).
  - loader_cls tells it WHICH loader to use for each matched file
    (TextLoader, PyPDFLoader, etc.) — DirectoryLoader itself doesn't
    read file content, it just finds files and delegates to that loader.

Common glob patterns:
  "*.txt"        → only .txt files directly inside the folder
  "*.pdf"        → only .pdf files directly inside the folder
  "**/*.txt"     → .txt files in the folder AND all subfolders (recursive)
  "*"            → every file directly inside the folder, any extension
  "**/*"         → every file in the folder and all subfolders (recursive)

load() vs lazy_load():
  Issue / limitation with load():
    loader.load() reads EVERY matching file right away and builds the
    FULL list of Documents in memory before returning. With a folder of
    thousands of files (or huge PDFs), this means waiting for all of them
    to finish AND holding all of them in memory at once — even if you
    only needed the first few.

  Difference with lazy_load():
    loader.lazy_load() returns a generator instead of a list. Each
    Document is only read from disk the moment you actually iterate to
    it, not all upfront. This keeps memory usage low and lets you start
    processing the first Document immediately instead of waiting for
    every file to load.

    for doc in loader.lazy_load():   # reads one file at a time, on demand
        ...
"""

import os

from langchain_community.document_loaders import DirectoryLoader, TextLoader

docs_path = os.path.join(os.path.dirname(__file__), "docs")
loader = DirectoryLoader(docs_path, glob="*.txt", loader_cls=TextLoader)
documents = loader.load()

print(f"Num documents: {len(documents)}")          # 1 per file
for i, doc in enumerate(documents, start=1):
    print(f"File {i} content : {doc.page_content!r}")
    print(f"File {i} metadata: {doc.metadata}")      # includes 'source' file path

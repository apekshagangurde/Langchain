# ==============================================================
# DOCUMENT-BASED TEXT SPLITTING
# ==============================================================
#
# Splits text based on the document format — HTML, Markdown, JSON,
# or Code. These splitters understand the structure of the document
# and cut at meaningful boundaries (headings, tags, functions, etc.)
# instead of blindly splitting by character count.
#
# ==============================================================


# ==============================================================
# Example 1: HTML Splitting
# ==============================================================

from langchain_text_splitters import HTMLSectionSplitter

html = """
<h1>Python</h1>
<p>Python is a popular programming language.</p>
<h2>Web Development</h2>
<p>Django and Flask are popular web frameworks.</p>
<h2>Data Science</h2>
<p>Pandas and NumPy are used for data analysis.</p>
"""

html_splitter = HTMLSectionSplitter(
    headers_to_split_on=[
        ("h1", "Header 1"),
        ("h2", "Header 2"),
    ]
)

html_docs = html_splitter.split_text(html)

print("=== HTML Splitting ===")
for i, doc in enumerate(html_docs):
    print(f"--- Chunk {i + 1} ---")
    print(f"Content: {doc.page_content}")
    print(f"Metadata: {doc.metadata}")
    print()


# ==============================================================
# Example 2: Markdown Splitting
# ==============================================================

from langchain_text_splitters import MarkdownHeaderTextSplitter

markdown = """# Python
Python is a popular programming language.

## Web Development
Django and Flask are popular web frameworks.

## Data Science
Pandas and NumPy are used for data analysis.
"""

md_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[
        ("#", "Header 1"),
        ("##", "Header 2"),
    ]
)

md_docs = md_splitter.split_text(markdown)

print("=== Markdown Splitting ===")
for i, doc in enumerate(md_docs):
    print(f"--- Chunk {i + 1} ---")
    print(f"Content: {doc.page_content}")
    print(f"Metadata: {doc.metadata}")
    print()


# ==============================================================
# Example 3: Code Splitting (Python)
# ==============================================================

from langchain_text_splitters import RecursiveCharacterTextSplitter, Language

python_code = """
def greet(name):
    print(f"Hello, {name}!")

class Calculator:
    def add(self, a, b):
        return a + b

    def subtract(self, a, b):
        return a - b
"""

code_splitter = RecursiveCharacterTextSplitter.from_language(
    language=Language.PYTHON,
    chunk_size=100,
    chunk_overlap=0,
)

code_chunks = code_splitter.split_text(python_code)

print("=== Code Splitting (Python) ===")
for i, chunk in enumerate(code_chunks):
    print(f"--- Chunk {i + 1} ---")
    print(chunk)
    print()

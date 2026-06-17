# ==============================================================
# TEXT SPLITTING — Theory
# ==============================================================
#
# WHAT IS TEXT SPLITTING?
#   Text splitting is the process of breaking large documents into
#   smaller, meaningful chunks so that LLMs and embedding models
#   can work with them effectively.
#
#   The core idea in one line:
#     "Cut big text into small, overlapping pieces that each carry
#      enough context to be useful on their own."
#
# WHY DO WE NEED TEXT SPLITTING?
#   1. LLMs have a limited context window — you can't feed an entire
#      book into a single prompt.
#   2. Embedding models produce better vectors for short, focused
#      passages than for huge walls of text.
#   3. Retrieval accuracy improves when chunks are small and topical —
#      a search returns the RIGHT paragraph, not a 50-page chapter.
#   4. Cost & speed — smaller chunks mean fewer tokens per LLM call.
#
# ==============================================================


# ==============================================================
# KEY CONCEPTS
# ==============================================================
#
# CHUNK SIZE
#   The maximum number of characters (or tokens) each piece can have.
#   - Too large  → chunks lose focus, retrieval becomes noisy.
#   - Too small  → chunks lose context, answers become fragmented.
#   - Sweet spot → typically 500–1000 characters for most use cases.
#
# CHUNK OVERLAP
#   The number of characters shared between consecutive chunks.
#   Overlap ensures that sentences sitting at a boundary don't get
#   cut in half and lose meaning.
#
#   Example (chunk_size=10, chunk_overlap=3):
#     Text:    "ABCDEFGHIJKLMNOP"
#     Chunk 1: "ABCDEFGHIJ"
#     Chunk 2: "HIJKLMNOP"      ← "HIJ" overlaps with Chunk 1
#
# SEPARATORS
#   The characters or patterns the splitter uses to decide WHERE to
#   cut. Common separators (in priority order):
#     "\n\n"  →  paragraph break  (best — preserves full paragraphs)
#     "\n"    →  line break
#     " "     →  space            (word boundary)
#     ""      →  character        (last resort)
#
# ==============================================================


# ==============================================================
# TYPES OF TEXT SPLITTERS IN LANGCHAIN
# ==============================================================
#
#  ┌──────────────────────────────────┬───────────────────────────────────────┐
#  │ Splitter                          │ Best For                              │
#  ├──────────────────────────────────┼───────────────────────────────────────┤
#  │ CharacterTextSplitter             │ Simple splitting by a single          │
#  │                                   │ separator (e.g. "\n\n")               │
#  ├──────────────────────────────────┼───────────────────────────────────────┤
#  │ RecursiveCharacterTextSplitter    │ General-purpose — tries multiple      │
#  │                                   │ separators in order; the DEFAULT      │
#  │                                   │ choice for most use cases             │
#  ├──────────────────────────────────┼───────────────────────────────────────┤
#  │ TokenTextSplitter                 │ Splitting by token count instead of   │
#  │                                   │ character count (important when you   │
#  │                                   │ care about exact token limits)        │
#  ├──────────────────────────────────┼───────────────────────────────────────┤
#  │ HTMLTextSplitter /                │ Structure-aware splitting for         │
#  │ MarkdownTextSplitter             │ HTML or Markdown documents            │
#  ├──────────────────────────────────┼───────────────────────────────────────┤
#  │ RecursiveJsonSplitter             │ Splitting large JSON objects while    │
#  │                                   │ keeping valid JSON structure          │
#  ├──────────────────────────────────┼───────────────────────────────────────┤
#  │ CodeTextSplitter /                │ Language-aware splitting for source   │
#  │ Language (enum)                   │ code (Python, JS, etc.)               │
#  └──────────────────────────────────┴───────────────────────────────────────┘
#
# ==============================================================


# ==============================================================
# HOW RecursiveCharacterTextSplitter WORKS
# ==============================================================
#
#   This is the RECOMMENDED default splitter. Here's its algorithm:
#
#   1. Start with the first separator in the list (e.g. "\n\n").
#   2. Split the text on that separator.
#   3. For each piece:
#        - If it fits within chunk_size → keep it as a chunk.
#        - If it's still too big → recurse with the NEXT separator
#          (e.g. "\n", then " ", then "").
#   4. After all chunks are formed, add overlap from the previous
#      chunk to the beginning of each new chunk.
#
#   This "recursive" approach preserves the most natural boundaries
#   (paragraphs first, then sentences, then words) instead of cutting
#   blindly at a fixed character count.
#
#   Default separators: ["\n\n", "\n", " ", ""]
#
# ==============================================================


# ==============================================================
# VISUAL — SPLITTING FLOW
# ==============================================================
#
#   Full Document
#        │
#        │  Try separator "\n\n" (paragraphs)
#        ▼
#   ┌──────────┐  ┌──────────┐  ┌────────────────────┐
#   │ Para 1   │  │ Para 2   │  │ Para 3 (too long)  │
#   │ (fits)   │  │ (fits)   │  │                    │
#   └──────────┘  └──────────┘  └────────┬───────────┘
#                                        │
#                           Try separator "\n" (lines)
#                                        ▼
#                               ┌──────────┐  ┌──────────┐
#                               │ Lines A  │  │ Lines B  │
#                               │ (fits)   │  │ (fits)   │
#                               └──────────┘  └──────────┘
#
#   Final chunks: [Para 1] [Para 2] [Lines A] [Lines B]
#                  ← overlap →  ← overlap →  ← overlap →
#
# ==============================================================


# ==============================================================
# BASIC USAGE EXAMPLE
# ==============================================================
#
#   from langchain.text_splitter import RecursiveCharacterTextSplitter
#
#   # 1. Create the splitter
#   splitter = RecursiveCharacterTextSplitter(
#       chunk_size=500,       # max characters per chunk
#       chunk_overlap=50,     # characters shared between chunks
#       separators=["\n\n", "\n", " ", ""]
#   )
#
#   # 2. Split raw text
#   text = "Your long document text here..."
#   chunks = splitter.split_text(text)
#   # Returns: ["chunk 1 text", "chunk 2 text", ...]
#
#   # 3. Or split LangChain Document objects (preserves metadata)
#   from langchain.schema import Document
#   docs = [Document(page_content=text, metadata={"source": "notes.txt"})]
#   split_docs = splitter.split_documents(docs)
#   # Returns: [Document(page_content="chunk 1", metadata={...}), ...]
#
# ==============================================================


# ==============================================================
# CHOOSING THE RIGHT chunk_size AND chunk_overlap
# ==============================================================
#
#   There's no one-size-fits-all answer. Here are practical guidelines:
#
#   ┌────────────────────┬──────────────┬───────────────┐
#   │ Use Case           │ chunk_size   │ chunk_overlap  │
#   ├────────────────────┼──────────────┼───────────────┤
#   │ Q&A / RAG          │ 500 – 1000   │ 50 – 100      │
#   ├────────────────────┼──────────────┼───────────────┤
#   │ Summarization      │ 1000 – 2000  │ 100 – 200     │
#   ├────────────────────┼──────────────┼───────────────┤
#   │ Code analysis      │ 1000 – 1500  │ 100 – 150     │
#   ├────────────────────┼──────────────┼───────────────┤
#   │ Chat / Dialogue    │ 200 – 500    │ 20 – 50       │
#   └────────────────────┴──────────────┴───────────────┘
#
#   Rule of thumb:
#     - chunk_overlap ≈ 10–20% of chunk_size
#     - Start with 500/50, test retrieval quality, then adjust
#
# ==============================================================


# ==============================================================
# WHERE TEXT SPLITTING FITS IN THE RAG PIPELINE
# ==============================================================
#
#   LOAD  ──►  SPLIT  ──►  EMBED  ──►  STORE
#                 ▲
#            YOU ARE HERE
#
#   Text splitting is Step 2 of the indexing phase.
#   It sits between loading raw documents and embedding them
#   into vectors for the vector store.
#
# ==============================================================


# ==============================================================
# KEY TERMS — QUICK REFERENCE
# ==============================================================
#
#  ┌───────────────────┬────────────────────────────────────────────────┐
#  │ Term               │ Meaning                                        │
#  ├───────────────────┼────────────────────────────────────────────────┤
#  │ Chunk              │ A small piece of text after splitting           │
#  ├───────────────────┼────────────────────────────────────────────────┤
#  │ Chunk Size         │ Max characters (or tokens) per chunk            │
#  ├───────────────────┼────────────────────────────────────────────────┤
#  │ Chunk Overlap      │ Characters shared between consecutive chunks   │
#  ├───────────────────┼────────────────────────────────────────────────┤
#  │ Separator          │ Pattern used to decide where to cut text       │
#  ├───────────────────┼────────────────────────────────────────────────┤
#  │ Recursive Splitting│ Trying multiple separators in priority order   │
#  │                    │ to preserve natural text boundaries            │
#  ├───────────────────┼────────────────────────────────────────────────┤
#  │ split_text()       │ Returns a list of strings                      │
#  ├───────────────────┼────────────────────────────────────────────────┤
#  │ split_documents()  │ Returns a list of Document objects with        │
#  │                    │ metadata preserved                             │
#  └───────────────────┴────────────────────────────────────────────────┘
#
# ==============================================================

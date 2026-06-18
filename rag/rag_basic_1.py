"""
RAG (Retrieval Augmented Generation) - Basics
===============================================
RAG is a technique that combines information retrieval with text generation.
Instead of relying only on the LLM's training data, RAG fetches relevant
documents from an external knowledge source and passes them as context
to the LLM for generating accurate, up-to-date answers.

Why use RAG:
- LLMs have a knowledge cutoff and can hallucinate.
- RAG grounds the LLM's response in real, retrieved data.
- No need to retrain the model — just update the knowledge source.

How it works:
1. Load documents from a source (PDF, web, database, etc.).
2. Split documents into smaller chunks.
3. Convert chunks into vector embeddings and store in a vector store.
4. User asks a question.
5. Retrieve relevant chunks from the vector store.
6. Pass the question + retrieved chunks to the LLM.
7. LLM generates an answer based on the provided context.

RAG Pipeline:
--------------

  +------------+     +-----------+     +------------+     +--------------+
  | Load Docs  +---->+ Split into+---->+ Create     +---->+ Store in     |
  | (PDF, Web) |     | Chunks    |     | Embeddings |     | Vector Store |
  +------------+     +-----------+     +------------+     +------+-------+
                                                                 |
                                                                 v
  +------------+     +-----------+     +------------+     +------+-------+
  | LLM Answer |<----+ Pass to   |<----+ Retrieve   |<----+ User Query  |
  | (Response) |     | LLM       |     | Relevant   |     | (Question)  |
  +------------+     +-----------+     | Chunks     |     +--------------+
                                       +------------+


In-Context Learning (ICL)
==========================
In-Context Learning is the ability of an LLM to learn and perform tasks
from examples provided directly in the prompt, without any fine-tuning
or retraining.

How it works:
- You provide a few examples (input-output pairs) inside the prompt.
- The LLM recognizes the pattern from these examples.
- It applies the same pattern to generate the answer for a new input.

Types of In-Context Learning:
1. Zero-shot:  No examples given, just the instruction.
   e.g., "Translate to French: Hello" → "Bonjour"

2. One-shot:   One example given before the actual query.
   e.g., "Happy → Positive. Sad → ?"  → "Negative"

3. Few-shot:   Multiple examples given before the query.
   e.g., "Cat → Animal. Rose → Plant. Car → ?" → "Vehicle"

RAG vs In-Context Learning:
-----------------------------
- ICL relies on examples in the prompt to guide the LLM.
- RAG retrieves external knowledge to provide factual context.
- Both inject information into the prompt, but RAG fetches it
  dynamically while ICL uses fixed examples.
"""

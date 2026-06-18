"""
Retrievers in LangChain are interfaces that return relevant documents based on a query.
They take a string query as input and return a list of matching Documents.
Retrievers are commonly used in RAG pipelines to fetch context from vector stores,
databases, or other data sources before passing it to an LLM for answer generation.

Retriever Flow Diagram:
========================

  +-------------+        +-------------+        +----------------+
  |   User      |        |  Retriever  |        |   Database /   |
  |   Query     +------->+  Interface  +------->+  Vector Store  |
  | (string)    |        |             |        |                |
  +-------------+        +------+------+        +-------+--------+
                                |                       |
                                |    Searches &         |
                                |    Matches            |
                                |                       |
                         +------v------+        +-------v--------+
                         |  Relevant   |<-------+   Stored       |
                         |  Documents  |        |   Documents    |
                         |  (List)     |        |                |
                         +------+------+        +----------------+
                                |
                                v
                         +-------------+
                         |    LLM      |
                         |  (Answer    |
                         | Generation) |
                         +-------------+


Wikipedia Retriever:
=====================
The Wikipedia Retriever in LangChain allows you to query Wikipedia articles
and retrieve relevant documents based on a search query. It uses the Wikipedia
API to search for articles matching the query and returns them as LangChain
Document objects.

How it works:
1. User provides a search query (e.g., "Machine Learning").
2. The retriever sends the query to the Wikipedia API.
3. Wikipedia returns matching articles based on relevance.
4. The retriever converts each article into a LangChain Document object
   containing the page content and metadata (title, source URL, etc.).
5. The retrieved documents can then be passed to an LLM for summarization
   or question answering.

Wikipedia Retriever Flow:
--------------------------

  +-----------+       +-------------------+       +----------------+
  |  User     +------>+ WikipediaRetriever+------>+ Wikipedia API  |
  |  Query    |       |  .get_relevant_   |       | (Search)       |
  | (string)  |       |   documents()     |       +-------+--------+
  +-----------+       +--------+----------+               |
                               |                          |
                               v                          v
                      +--------+----------+     +---------+--------+
                      | List of LangChain |<----+ Matching Articles|
                      | Documents         |     | (page content,   |
                      | (ready for LLM)   |     |  metadata)       |
                      +-------------------+     +------------------+

"""

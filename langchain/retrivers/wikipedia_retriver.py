"""
Wikipedia Retriever - Code Example
====================================
The WikipediaRetriever fetches relevant Wikipedia articles
based on a user query and returns them as LangChain Documents.
"""

# pip install wikipedia langchain-community

from langchain_community.retrievers import WikipediaRetriever

retriever = WikipediaRetriever(top_k_results=1)

docs = retriever.invoke("Machine Learning")

print(f"Number of documents retrieved: {len(docs)}")
print(f"Title: {docs[0].metadata['title']}")
print(f"Content preview: {docs[0].page_content[:300]}")

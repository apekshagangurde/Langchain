"""
WebBaseLoader — Loading a Webpage
=======================================

What is WebBaseLoader?
  A Document Loader that fetches a URL over HTTP, strips out the HTML
  tags using BeautifulSoup, and returns the visible page text as a
  Document (one Document per URL).

When to use it:
  - Your source data is a public webpage (blog post, docs page, article)
    and you want its text content pulled into a RAG pipeline.
  - You only need the rendered TEXT, not styling, scripts, or layout.

Limitations:
  - Only fetches static HTML — it does NOT run JavaScript, so content
    rendered client-side (common in single-page apps) will be missing.
  - Output is the raw scraped text, including menus, footers, ads, etc.
    unless you pass bs_kwargs to target a specific HTML tag/class.
  - Subject to the page's access rules — logins, paywalls, or robots.txt
    blocks will cause it to fail or return incomplete content.
  - Network-dependent — slow or unreachable sites mean failed/slow loads.
  - Requires the `beautifulsoup4` package, and setting a USER_AGENT is
    recommended (some sites reject requests without one).
"""

import os

from langchain_community.document_loaders import WebBaseLoader

os.environ.setdefault("USER_AGENT", "LangChainDemo/1.0")

loader = WebBaseLoader("https://sashakt-platform.github.io/docs/")
documents = loader.load()

print(f"Num documents: {len(documents)}")  # 1 per URL
print(f"page_content : {documents[0].page_content!r}")
print(f"metadata     : {documents[0].metadata}")  # includes 'source', 'title'

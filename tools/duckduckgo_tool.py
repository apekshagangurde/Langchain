"""
DuckDuckGo Search Tool
======================
A built-in LangChain tool that searches the web using DuckDuckGo.
No API key required — free and easy to use.
"""

from langchain_community.tools import DuckDuckGoSearchRun

search_tool = DuckDuckGoSearchRun()

print(f"Tool Name: {search_tool.name}")
print(f"Description: {search_tool.description}")

query = "ipl news "
result = search_tool.run(query)

print(f"\nSearch Query: {query}")
print(f"Result:\n{result}")

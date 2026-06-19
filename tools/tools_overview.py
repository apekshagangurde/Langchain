"""
LangChain Tools Overview
========================

Built-in Tools:
    Pre-made tools provided by LangChain that are ready to use out of the box.
    Examples: Wikipedia, DuckDuckGo Search, Python REPL, Arxiv, Shell, etc.
    They require minimal setup — just import and use.

Custom Tools:
    User-defined tools created to perform specific tasks tailored to your needs.
    You define the tool name, description, and the function it executes.
    Created using the @tool decorator or by subclassing BaseTool.
"""

# ============================================================
# 1. Built-in Tool Example (Wikipedia)
# ============================================================

from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

wiki_tool = WikipediaQueryRun(api_wrapper=WikipediaAPIWrapper())

print("=== Built-in Tool ===")
print(f"Name: {wiki_tool.name}")
print(f"Description: {wiki_tool.description}")
print(f"Result: {wiki_tool.run('LangChain')}")


# ============================================================
# 2. Custom Tool Example (using @tool decorator)
# ============================================================

from langchain.tools import tool

@tool
def word_count(text: str) -> int:
    """Counts the number of words in the given text."""
    return len(text.split())

print("\n=== Custom Tool ===")
print(f"Name: {word_count.name}")
print(f"Description: {word_count.description}")
print(f"Result: {word_count.run('LangChain makes building AI apps easy')}")

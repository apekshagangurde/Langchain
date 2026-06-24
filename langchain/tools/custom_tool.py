"""
Custom Tool Example
===================
Creating a custom tool using the @tool decorator for multiplication.
"""

from langchain.tools import tool


@tool
def multiply(a: int, b: int) -> int:
    """Multiplies two integers and returns the result."""
    return a * b


print(f"Tool Name: {multiply.name}")
print(f"Description: {multiply.description}")
print(f"Args: {multiply.args}")

result = multiply.invoke({"a": 5, "b": 3})
print(f"\nResult of 5 x 3 = {result}")

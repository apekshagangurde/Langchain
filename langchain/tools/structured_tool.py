"""
Structured Tool with Pydantic
==============================
Using Pydantic BaseModel to define input schema for a custom tool.
This gives more control over argument validation and descriptions.
"""

from pydantic import BaseModel, Field
from langchain.tools import StructuredTool


class MultiplyInput(BaseModel):
    a: int = Field(description="First number")
    b: int = Field(description="Second number")


def multiply(a: int, b: int) -> int:
    """Multiplies two integers and returns the result."""
    return a * b


multiply_tool = StructuredTool.from_function(
    func=multiply,
    name="multiply",
    description="Multiplies two numbers together",
    args_schema=MultiplyInput,
)

print(f"Tool Name: {multiply_tool.name}")
print(f"Description: {multiply_tool.description}")
print(f"Args: {multiply_tool.args}")

result = multiply_tool.invoke({"a": 4, "b": 7})
print(f"\nResult of 4 x 7 = {result}")

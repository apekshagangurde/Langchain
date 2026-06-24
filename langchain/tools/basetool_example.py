"""
BaseTool Class Example
======================
Creating a custom tool by subclassing BaseTool with Pydantic input schema.
"""

from typing import Type

from pydantic import BaseModel, Field
from langchain.tools import BaseTool


class MultiplyInput(BaseModel):
    a: int = Field(description="First number")
    b: int = Field(description="Second number")


class MultiplyTool(BaseTool):
    name: str = "multiply"
    description: str = "Multiplies two numbers using BaseTool class"
    args_schema: Type[BaseModel] = MultiplyInput

    def _run(self, a: int, b: int) -> int:
        return a * b


tool = MultiplyTool()

print(f"Tool Name: {tool.name}")
print(f"Description: {tool.description}")
print(f"Args: {tool.args}")

result = tool.invoke({"a": 6, "b": 9})
print(f"\nResult of 6 x 9 = {result}")

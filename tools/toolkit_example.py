"""
Toolkit Example
================
Creating a custom toolkit with multiple tools (add and multiply).
A Toolkit is a collection of related tools grouped together.
"""

from typing import List, Type

from pydantic import BaseModel, Field
from langchain.tools import BaseTool, BaseToolkit


class MathInput(BaseModel):
    a: int = Field(description="First number")
    b: int = Field(description="Second number")


class AddTool(BaseTool):
    name: str = "add"
    description: str = "Adds two numbers together"
    args_schema: Type[BaseModel] = MathInput

    def _run(self, a: int, b: int) -> int:
        return a + b


class MultiplyTool(BaseTool):
    name: str = "multiply"
    description: str = "Multiplies two numbers together"
    args_schema: Type[BaseModel] = MathInput

    def _run(self, a: int, b: int) -> int:
        return a * b


class MathToolkit(BaseToolkit):
    def get_tools(self) -> List[BaseTool]:
        return [AddTool(), MultiplyTool()]


toolkit = MathToolkit()
tools = toolkit.get_tools()

print("=== Math Toolkit ===")
for tool in tools:
    print(f"\nTool Name: {tool.name}")
    print(f"Description: {tool.description}")
    print(f"Args: {tool.args}")

print("\n=== Results ===")
add_tool = tools[0]
multiply_tool = tools[1]

print(f"3 + 5 = {add_tool.invoke({'a': 3, 'b': 5})}")
print(f"3 x 5 = {multiply_tool.invoke({'a': 3, 'b': 5})}")

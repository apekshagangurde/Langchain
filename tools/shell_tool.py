"""
Shell Tool
==========
A built-in LangChain tool that runs shell commands directly from Python.
Useful for executing system-level operations like listing files, checking disk usage, etc.
"""

from langchain_community.tools import ShellTool

shell_tool = ShellTool()

print(f"Tool Name: {shell_tool.name}")
print(f"Description: {shell_tool.description}")

result = shell_tool.run("echo Hello from LangChain Shell Tool!")
print(f"\nResult:\n{result}")

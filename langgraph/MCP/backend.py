import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import TypedDict, Annotated

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

_search = DuckDuckGoSearchRun()


@tool
async def duckduckgo_search(query: str) -> str:
    """Search the web using DuckDuckGo and return a summary of top results.

    Use this when you need up-to-date information that is not in your training data.

    Args:
        query: The search query string.
    """
    return await _search.arun(query)


@tool
async def get_current_time(timezone_offset_hours: float = 0) -> str:
    """Get the current date and time as a formatted string.

    Args:
        timezone_offset_hours: Hours to offset from UTC (e.g. 5 for UTC+5, 5.5 for UTC+5:30 / India). Defaults to 0 (UTC).
    """
    now = datetime.now(timezone.utc) + timedelta(hours=timezone_offset_hours)
    sign = "+" if timezone_offset_hours >= 0 else "-"
    return now.strftime("%Y-%m-%d %H:%M:%S") + f" (UTC{sign}{abs(timezone_offset_hours):g})"


mcp_client = MultiServerMCPClient(
    {
        "calculator": {
            "command": "python",
            "args": [str(Path(__file__).parent / "mcp_server.py")],
            "transport": "stdio",
        },
        "weather": {
            "command": "python",
            "args": [str(Path(__file__).parent / "weather_mcp_server.py")],
            "transport": "stdio",
        },
        "unit_converter": {
            "command": "python",
            "args": [str(Path(__file__).parent / "unit_converter_mcp_server.py")],
            "transport": "stdio",
        },
        "currency_converter": {
            "command": "python",
            "args": [str(Path(__file__).parent / "currency_mcp_server.py")],
            "transport": "stdio",
        },
        "text_utils": {
            "command": "python",
            "args": [str(Path(__file__).parent / "text_utils_mcp_server.py")],
            "transport": "stdio",
        },
    }
)

llm = ChatGroq(model="llama-3.3-70b-versatile")


class ChatState(TypedDict):
    """Graph state — a running list of chat messages, merged via `add_messages`."""

    messages: Annotated[list[BaseMessage], add_messages]


async def build_workflow():
    """Fetch the calculator tool from the MCP server and compile the LangGraph agent."""
    mcp_tools = await mcp_client.get_tools()
    tools = [duckduckgo_search, get_current_time, *mcp_tools]
    llm_with_tools = llm.bind_tools(tools)

    async def chat_node(state: ChatState) -> ChatState:
        messages = state["messages"]
        response = await llm_with_tools.ainvoke(messages)
        return {"messages": [response]}

    tool_node = ToolNode(tools)

    graph = StateGraph(ChatState)

    graph.add_node("chat_node", chat_node)
    graph.add_node("tools", tool_node)

    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition)
    graph.add_edge("tools", "chat_node")

    return graph.compile()


async def main():
    workflow = await build_workflow()
    response = await workflow.ainvoke(
        {"messages": [HumanMessage(content="Count the words in: the quick brown fox")]}
    )
    for message in response["messages"]:
        message.pretty_print()


if __name__ == "__main__":
    asyncio.run(main())

import ast
import operator
from datetime import datetime, timedelta, timezone
from typing import TypedDict, Annotated

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage
from langchain_core.tools import tool
from langchain_community.tools import DuckDuckGoSearchRun
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

load_dotenv()

_ALLOWED_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
    ast.USub: operator.neg,
    ast.UAdd: operator.pos,
    ast.Mod: operator.mod,
}


def _safe_eval(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](
            _safe_eval(node.left), _safe_eval(node.right)
        )
    if isinstance(node, ast.UnaryOp) and type(node.op) in _ALLOWED_OPS:
        return _ALLOWED_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")


@tool
def calculator(expression: str) -> str:
    """Evaluate a basic arithmetic expression and return the result.

    Supports +, -, *, /, **, % and parentheses. Example input: "(4 + 5) * 2".

    Args:
        expression: The arithmetic expression to evaluate, as a string.
    """
    try:
        tree = ast.parse(expression, mode="eval")
        result = _safe_eval(tree.body)
        return str(result)
    except Exception as exc:
        return f"Error evaluating expression: {exc}"


_search = DuckDuckGoSearchRun()


@tool
def duckduckgo_search(query: str) -> str:
    """Search the web using DuckDuckGo and return a summary of top results.

    Use this when you need up-to-date information that is not in your training data.

    Args:
        query: The search query string.
    """
    return _search.run(query)


@tool
def get_current_time(timezone_offset_hours: float = 0) -> str:
    """Get the current date and time as a formatted string.

    Args:
        timezone_offset_hours: Hours to offset from UTC (e.g. 5 for UTC+5, 5.5 for UTC+5:30 / India). Defaults to 0 (UTC).
    """
    now = datetime.now(timezone.utc) + timedelta(hours=timezone_offset_hours)
    sign = "+" if timezone_offset_hours >= 0 else "-"
    return now.strftime("%Y-%m-%d %H:%M:%S") + f" (UTC{sign}{abs(timezone_offset_hours):g})"


tools = [calculator, duckduckgo_search, get_current_time]

llm = ChatGroq(model="llama-3.1-8b-instant")
llm_with_tools = llm.bind_tools(tools)


class ChatState(TypedDict):
    """Graph state — a running list of chat messages, merged via `add_messages`."""

    messages: Annotated[list[BaseMessage], add_messages]


def chat_node(state: ChatState) -> ChatState:
    """Call the tool-bound Groq LLM with the current message history.

    Args:
        state: The current graph state containing the message list.
    """
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


tool_node = ToolNode(tools)

graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)
graph.add_node("tools", tool_node)

graph.add_edge(START, "chat_node")
graph.add_conditional_edges("chat_node", tools_condition)
graph.add_edge("tools", "chat_node")

workflow = graph.compile()

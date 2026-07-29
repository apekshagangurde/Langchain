import asyncio

import streamlit as st
from langchain_core.messages import HumanMessage, ToolMessage

from backend import build_workflow

st.title("LangGraph MCP Agent")


@st.cache_resource
def get_workflow():
    return asyncio.run(build_workflow())


workflow = get_workflow()

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state["messages"]:
    if isinstance(message, ToolMessage):
        continue
    role = "user" if message.type == "human" else "assistant"
    with st.chat_message(role):
        st.text(message.content)

user_input = st.chat_input(
    "Ask for math, weather, currency, unit conversion, text stats, or a web search..."
)

if user_input:
    with st.chat_message("user"):
        st.text(user_input)

    st.session_state["messages"].append(HumanMessage(content=user_input))
    num_before = len(st.session_state["messages"])

    with st.chat_message("assistant"):
        with st.status("Thinking...", expanded=True) as status:
            response = asyncio.run(
                workflow.ainvoke({"messages": st.session_state["messages"]})
            )

            new_tool_messages = [
                m for m in response["messages"][num_before:] if isinstance(m, ToolMessage)
            ]
            for tool_message in new_tool_messages:
                status.write(f"✅ Tool `{tool_message.name}` finished")

            status.update(
                label="Tool run complete" if new_tool_messages else "Done",
                state="complete",
            )

        st.session_state["messages"] = response["messages"]
        ai_message = response["messages"][-1].content
        st.text(ai_message)

import streamlit as st
from langchain_core.messages import HumanMessage

from Langgraph_backend import workflow

CONFIG = {"configurable": {"thread_id": "1"}}

st.title("LangGraph Chatbot (Streaming)")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.text(message["content"])

user_input = st.chat_input("Type your message here")


def stream_response(user_message):
    for message_chunk, metadata in workflow.stream(
        {"messages": [HumanMessage(content=user_message)]},
        config=CONFIG,
        stream_mode="messages",
    ):
        yield message_chunk.content


if user_input:
    st.session_state["messages"].append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.text(user_input)

    with st.chat_message("assistant"):
        ai_message = st.write_stream(stream_response(user_input))

    st.session_state["messages"].append({"role": "assistant", "content": ai_message})

import uuid

import streamlit as st
from langchain_core.messages import HumanMessage

from langgraph_sqlite_backend import workflow, retrieve_all_threads


def new_thread_id():
    return str(uuid.uuid4())


if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = new_thread_id()

if "chat_threads" not in st.session_state:
    st.session_state["chat_threads"] = retrieve_all_threads()

if st.session_state["thread_id"] not in st.session_state["chat_threads"]:
    st.session_state["chat_threads"].append(st.session_state["thread_id"])


def load_conversation(thread_id):
    state = workflow.get_state({"configurable": {"thread_id": thread_id}})
    return state.values.get("messages", [])


st.sidebar.title("LangGraph Chatbot (SQLite)")

if st.sidebar.button("New Chat"):
    st.session_state["thread_id"] = new_thread_id()
    st.session_state["chat_threads"].append(st.session_state["thread_id"])

st.sidebar.header("Conversations")
for thread_id in st.session_state["chat_threads"][::-1]:
    if st.sidebar.button(thread_id, key=thread_id):
        st.session_state["thread_id"] = thread_id

st.title("LangGraph Chatbot (SQLite persistence)")

CONFIG = {"configurable": {"thread_id": st.session_state["thread_id"]}}

# resume — load this thread's past messages straight from the sqlite checkpointer
messages = load_conversation(st.session_state["thread_id"])
for message in messages:
    role = "user" if message.type == "human" else "assistant"
    with st.chat_message(role):
        st.text(message.content)

user_input = st.chat_input("Type your message here")

if user_input:
    with st.chat_message("user"):
        st.text(user_input)

    response = workflow.invoke(
        {"messages": [HumanMessage(content=user_input)]}, config=CONFIG
    )
    ai_message = response["messages"][-1].content

    with st.chat_message("assistant"):
        st.text(ai_message)

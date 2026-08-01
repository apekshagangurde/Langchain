import uuid

import streamlit as st
from langgraph.types import Command

from backend import workflow


def new_thread_id():
    return str(uuid.uuid4())


if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = new_thread_id()

if "stage" not in st.session_state:
    st.session_state["stage"] = "topic"  # topic -> review -> done


st.title("Social Media Post Generator (HITL)")

CONFIG = {"configurable": {"thread_id": st.session_state["thread_id"]}}

if st.sidebar.button("New Post"):
    st.session_state["thread_id"] = new_thread_id()
    st.session_state["stage"] = "topic"
    st.rerun()

if st.session_state["stage"] == "topic":
    topic = st.text_input("Enter Topic", value="GenAI")

    if st.button("Submit"):
        workflow.invoke({"topic": topic}, config=CONFIG)
        st.session_state["stage"] = "review"
        st.rerun()

elif st.session_state["stage"] == "review":
    interrupt_payload = workflow.get_state(CONFIG).tasks[0].interrupts[0].value

    st.subheader("Draft post — pending approval")
    edited = st.text_area("Review / edit before approving", value=interrupt_payload["draft"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Approve"):
            workflow.invoke(Command(resume="approve"), config=CONFIG)
            st.session_state["stage"] = "done"
            st.rerun()
    with col2:
        if st.button("Approve edited version"):
            workflow.invoke(Command(resume=edited), config=CONFIG)
            st.session_state["stage"] = "done"
            st.rerun()

elif st.session_state["stage"] == "done":
    final_state = workflow.get_state(CONFIG).values
    st.success("Posted to X")
    st.write(final_state["draft"])

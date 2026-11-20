"""
TripMate — small Streamlit chat UI
==================================

    streamlit run app.py

Type a prompt, get TripMate's answer. Each reply also shows the tool calls
the agent made and its todo list.

Memory: the agent has a checkpointer, so it remembers the chat by thread_id.
We only send the new message; "New chat" starts a new thread_id.
Long-term facts saved under /memories/ are kept across chats (until restart).
"""

import uuid

import streamlit as st
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

from agent import build_agent


@st.cache_resource
def get_agent():
    # Built once and kept across Streamlit reruns, so saved chats and memories survive.
    # InMemorySaver = per-chat history; InMemoryStore = /memories/ shared by all chats.
    return build_agent(checkpointer=InMemorySaver(), store=InMemoryStore())


agent = get_agent()

st.set_page_config(page_title="TripMate", page_icon="🧳")
st.title("🧳 TripMate")
st.caption("Weekend-trip planner — a deep agent with real weather and place search.")

if "messages" not in st.session_state:
    st.session_state.messages = []  # only for showing the chat on screen
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if st.sidebar.button("New chat"):
    st.session_state.messages = []
    st.session_state.thread_id = str(uuid.uuid4())  # fresh memory
    st.rerun()

st.sidebar.caption(f"Thread: `{st.session_state.thread_id[:8]}`")

# Show the conversation so far.
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("e.g. Plan a 2-day trip from Pune to Mahabaleshwar, budget ₹8,000")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Planning... (rate-limited, can take a minute)"):
                # Send only the new message; the checkpointer remembers earlier turns.
                config = {"configurable": {"thread_id": st.session_state.thread_id}}
                result = agent.invoke(
                    {"messages": [{"role": "user", "content": prompt}]}, config=config
                )
        except Exception as e:  # bad API key, network, rate limit, ...
            st.error(f"Agent failed: {e}")
            st.stop()

        answer = result["messages"][-1].content
        st.markdown(answer)

        # What happened behind the scenes — this turn only.
        # result["messages"] holds the whole thread, so start after the last user message.
        msgs = result["messages"]
        last_user = max(i for i, m in enumerate(msgs) if m.type == "human")
        tool_calls = [
            call
            for m in msgs[last_user + 1 :]
            for call in (getattr(m, "tool_calls", None) or [])
        ]
        with st.expander(f"Tool calls ({len(tool_calls)})"):
            for call in tool_calls:
                st.code(f"{call['name']}({call['args']})", language="python")

        todos = result.get("todos", [])
        if todos:
            with st.expander("Todo list"):
                icons = {"completed": "✅", "in_progress": "🔄", "pending": "⏳"}
                for todo in todos:
                    st.write(f"{icons.get(todo['status'], '•')} {todo['content']}")

    st.session_state.messages.append({"role": "assistant", "content": answer})

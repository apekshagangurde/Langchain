"""
TripMate — small Streamlit chat UI
==================================

    streamlit run app.py

Type a prompt, get TripMate's answer. Each reply also shows the tool calls
the agent made and its todo list.
"""

import streamlit as st

from agent import agent

st.set_page_config(page_title="TripMate", page_icon="🧳")
st.title("🧳 TripMate")
st.caption("Weekend-trip planner — a deep agent with real weather and place search.")

if "messages" not in st.session_state:
    st.session_state.messages = []  # [{"role": "user"|"assistant", "content": str}]

if st.sidebar.button("New chat"):
    st.session_state.messages = []
    st.rerun()

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
                # Send the whole chat so the agent remembers earlier turns.
                result = agent.invoke({"messages": st.session_state.messages})
        except Exception as e:  # bad API key, network, rate limit, ...
            st.error(f"Agent failed: {e}")
            st.stop()

        answer = result["messages"][-1].content
        st.markdown(answer)

        # What happened behind the scenes.
        tool_calls = [
            call
            for m in result["messages"]
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

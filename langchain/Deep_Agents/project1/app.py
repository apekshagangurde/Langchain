"""
TripMate — small Streamlit chat UI
==================================

    streamlit run app.py

Type a prompt, get TripMate's answer. Each reply also shows the tool calls
the agent made and its todo list.

Memory: the agent has a checkpointer, so it remembers the chat by thread_id.
We only send the new message; "New chat" starts a new thread_id.
Long-term facts saved under /memories/ are kept across chats (until restart).

Human-in-the-loop: when the agent calls book_hotel, the run pauses. The pending
booking is shown with Approve / Reject buttons; clicking one resumes the run.
"""

import uuid

import streamlit as st
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

from agent import build_agent, pending_booking, resume


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
if "pending" not in st.session_state:
    st.session_state.pending = []  # bookings waiting for Approve / Reject

if st.sidebar.button("New chat"):
    st.session_state.messages = []
    st.session_state.pending = []
    st.session_state.thread_id = str(uuid.uuid4())  # fresh memory
    st.rerun()

st.sidebar.caption(f"Thread: `{st.session_state.thread_id[:8]}`")
config = {"configurable": {"thread_id": st.session_state.thread_id}}


def show_result(result):
    """Show the answer (or the paused booking) plus tool calls and todos for this turn."""
    msgs = result["messages"]
    pending = pending_booking(result)
    st.session_state.pending = pending

    if pending:
        st.info("Waiting for your approval before booking — see below.")
    else:
        answer = msgs[-1].content
        st.markdown(answer)
        st.session_state.messages.append({"role": "assistant", "content": answer})

    # What happened behind the scenes — this turn only.
    # result["messages"] holds the whole thread, so start after the last user message.
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


def run(step, *args, **kwargs):
    """Call the agent with a spinner; show errors instead of crashing."""
    try:
        with st.spinner("Planning... (rate-limited, can take a minute)"):
            return step(*args, **kwargs)
    except Exception as e:  # bad API key, network, rate limit, ...
        st.error(f"Agent failed: {e}")
        st.stop()


# Show the conversation so far.
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Human-in-the-loop: a booking is paused, waiting for the user's decision.
if st.session_state.pending:
    with st.chat_message("assistant"):
        st.markdown("**🏨 Booking needs your approval**")
        for req in st.session_state.pending:
            st.markdown(f"- {req.get('description') or req['args']}")
        reason = st.text_input("Reason if rejecting (optional)", key="reject_reason")
        approve_col, reject_col = st.columns(2)
        approve = approve_col.button("✅ Approve", type="primary", use_container_width=True)
        reject = reject_col.button("❌ Reject", use_container_width=True)

    if approve or reject:
        n = len(st.session_state.pending)
        label = "✅ Approved booking" if approve else f"❌ Rejected booking{': ' + reason if reason else ''}"
        st.session_state.messages.append({"role": "user", "content": label})
        st.session_state.pending = []
        with st.chat_message("assistant"):
            result = run(resume, agent, config, approve=approve, n_actions=n, reason=reason)
            show_result(result)
        st.rerun()

prompt = st.chat_input(
    "e.g. Plan a 2-day trip from Pune to Mahabaleshwar, budget ₹8,000",
    disabled=bool(st.session_state.pending),  # decide on the booking first
)
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        # Send only the new message; the checkpointer remembers earlier turns.
        result = run(
            agent.invoke, {"messages": [{"role": "user", "content": prompt}]}, config=config
        )
        show_result(result)
    if st.session_state.pending:
        st.rerun()  # redraw so the Approve / Reject buttons appear

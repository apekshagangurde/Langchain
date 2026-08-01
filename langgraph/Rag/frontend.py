import uuid

import streamlit as st

from backend import build_rag_workflow, save_uploaded_pdf

st.title("RAG with LangGraph")

with st.sidebar:
    st.header("Upload a PDF")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

    if uploaded_file is not None and st.session_state.get("uploaded_filename") != uploaded_file.name:
        with st.spinner("Indexing PDF..."):
            pdf_path = save_uploaded_pdf(uploaded_file)
            collection_name = f"pdf_{uuid.uuid4().hex}"
            workflow, num_chunks = build_rag_workflow(pdf_path, collection_name)

        st.session_state["workflow"] = workflow
        st.session_state["uploaded_filename"] = uploaded_file.name
        st.session_state["messages"] = []
        st.success(f"Indexed {num_chunks} chunks from {uploaded_file.name}")
    elif uploaded_file is not None:
        st.info(f"Using indexed file: {uploaded_file.name}")

if "messages" not in st.session_state:
    st.session_state["messages"] = []

for role, content in st.session_state["messages"]:
    with st.chat_message(role):
        st.write(content)

if "workflow" not in st.session_state:
    st.info("Upload a PDF from the sidebar to get started.")
else:
    user_input = st.chat_input("Ask a question about the uploaded PDF...")

    if user_input:
        st.session_state["messages"].append(("user", user_input))
        with st.chat_message("user"):
            st.write(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = st.session_state["workflow"].invoke({"question": user_input})
                answer = result["answer"]

            st.write(answer)
            with st.expander("Sources"):
                for doc in result["context"]:
                    st.markdown(f"**Page {doc.metadata.get('page')}**")
                    st.text(doc.page_content[:300] + "...")

        st.session_state["messages"].append(("assistant", answer))

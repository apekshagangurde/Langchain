import tempfile
from pathlib import Path
from typing import TypedDict

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from langgraph.graph import StateGraph, START, END

load_dotenv()

embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
llm = ChatGroq(model="llama-3.3-70b-versatile")


class RAGState(TypedDict):
    """Graph state — the user's question, the retrieved chunks, and the final answer."""

    question: str
    context: list[Document]
    answer: str


def save_uploaded_pdf(uploaded_file) -> str:
    """Persist a Streamlit-uploaded PDF to a temp file and return its path.

    Args:
        uploaded_file: A Streamlit `UploadedFile` object from `st.file_uploader`.
    """
    tmp_path = Path(tempfile.gettempdir()) / f"rag_upload_{uploaded_file.name}"
    tmp_path.write_bytes(uploaded_file.getbuffer())
    return str(tmp_path)


def load_and_split_pdf(pdf_path: str) -> list[Document]:
    """Load a PDF from disk and split it into overlapping chunks for retrieval.

    Args:
        pdf_path: Path to the PDF file.
    """
    loader = PyPDFLoader(pdf_path)
    pages = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    return splitter.split_documents(pages)


def build_rag_workflow(pdf_path: str, collection_name: str):
    """Index a PDF into an in-memory Chroma store and compile the retrieve -> generate graph.

    Args:
        pdf_path: Path to the PDF file to index.
        collection_name: Unique Chroma collection name for this upload (avoids
            mixing chunks from different PDFs across sessions).
    """
    chunks = load_and_split_pdf(pdf_path)

    vector_store = Chroma.from_documents(
        chunks, embedding=embeddings, collection_name=collection_name
    )
    retriever = vector_store.as_retriever(search_kwargs={"k": 4})

    def retrieve(state: RAGState) -> RAGState:
        docs = retriever.invoke(state["question"])
        return {"context": docs}

    def generate(state: RAGState) -> RAGState:
        context_text = "\n\n".join(doc.page_content for doc in state["context"])
        prompt = (
            "Answer the question using ONLY the context below. "
            "If the answer isn't in the context, say you don't know.\n\n"
            f"Context:\n{context_text}\n\n"
            f"Question: {state['question']}"
        )
        response = llm.invoke(prompt)
        return {"answer": response.content}

    graph = StateGraph(RAGState)

    graph.add_node("retrieve", retrieve)
    graph.add_node("generate", generate)

    graph.add_edge(START, "retrieve")
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

    return graph.compile(), len(chunks)

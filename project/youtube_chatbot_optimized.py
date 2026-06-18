from dotenv import load_dotenv

load_dotenv()

from youtube_transcript_api import YouTubeTranscriptApi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain_groq import ChatGroq

# Step 1: Fetch YouTube transcript
video_id = "Gfr50f6ZBvo"

ytt_api = YouTubeTranscriptApi()
transcript = ytt_api.fetch(video_id, languages=["en"])

full_script = " ".join([entry.text for entry in transcript])

print("=== Step 1: YouTube Video Transcript ===")
print(f"Video ID: {video_id}")
print(f"Total segments: {len(transcript)}")

# Step 2: Split text using RecursiveCharacterTextSplitter
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
documents = splitter.create_documents([full_script])

# Step 3: Store documents in FAISS vector store
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = FAISS.from_documents(documents, embeddings)
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

print(f"\n=== Step 3: FAISS Vector Store ===")
print(f"Total vectors stored: {vector_store.index.ntotal}")

# Step 4: Create LLM and Prompt Template
llm = ChatGroq(model="llama-3.3-70b-versatile")

prompt = ChatPromptTemplate.from_template(
    """You are a helpful assistant. Answer the question based only on the provided transcript context.
If the context is insufficient to answer the question, say "I don't know".

Context:
{context}

Question: {question}

Answer:"""
)

# Step 5: Build optimized chain using RunnableParallel and RunnablePassthrough
parallel_chain = RunnableParallel(
    context=retriever | (lambda docs: "\n\n".join([doc.page_content for doc in docs])),
    question=RunnablePassthrough(),
)

chain = parallel_chain | prompt | llm

# Step 6: Invoke the chain
query = "What is AlphaFold?"
response = chain.invoke(query)

print(f"\n=== Optimized Chain Output ===")
print(f"Question: {query}")
print(f"Answer: {response.content}")


"""
=============================================================
IMPROVEMENT SECTION - What We Can Improve in This Project
=============================================================

1. UI Enhancement (Streamlit)
   - Streamlit is a Python framework to build interactive web apps quickly.
   - Add a text input for YouTube URL, a chat interface for questions,
     and display answers in a clean UI with st.chat_message().

2. Evaluation - RAGs with LangSmith
   - LangSmith helps trace, monitor, and evaluate RAG pipelines.
   - Track retrieval quality, LLM responses, latency, and token usage.
   - Create evaluation datasets to measure accuracy over time.

3. Pre-Retrieval Improvements
   - Query rewriting: rephrase user query for better search results.
   - Query expansion: generate multiple query variations (Multi Query Retriever).
   - HyDE: generate a hypothetical answer, then use it to search.

4. During Retrieval Improvements
   - Use MMR (Maximal Marginal Relevance) for diverse results.
   - Re-ranking: reorder retrieved docs by relevance score.
   - Hybrid search: combine keyword search + vector search.

5. Post-Retrieval Augmentation
   - Contextual compression: remove irrelevant parts from retrieved docs.
   - Document summarization: summarize long chunks before passing to LLM.
   - Filtering: remove low-relevance documents based on threshold.

6. Prompt Template Optimization
   - Add role-specific system prompts for better responses.
   - Use few-shot examples in prompts for consistent output format.
   - Chain-of-thought prompting for complex reasoning questions.

7. Answer Grounding
   - Ensure LLM answers are strictly based on retrieved context.
   - Add verification step to check if answer is supported by sources.
   - Reduce hallucination by constraining output to provided context.

8. Context Window Optimization
   - Smart chunking: adjust chunk size based on content type.
   - Token-aware splitting: ensure chunks fit within LLM context limits.
   - Prioritize most relevant chunks when context window is limited.

9. Generation - Answer with Citation
   - Return source chunk references alongside the answer.
   - Show which part of the transcript supports the answer.
   - Add timestamps from transcript for video navigation.

10. Guardrailing
    - Input validation: filter harmful or irrelevant queries.
    - Output validation: ensure responses are safe and appropriate.
    - Topic restriction: limit answers to transcript content only.

11. System Design
    - Add caching layer to avoid re-fetching same transcripts.
    - Persistent vector store: save FAISS index to disk for reuse.
    - API endpoint: wrap chatbot as a REST API with FastAPI.

12. Multi-Modal
    - Process video frames alongside transcript for visual context.
    - Support image-based questions about video content.
    - Combine audio, text, and visual features for richer answers.

13. Agentic RAG
    - Use LangChain agents to decide when to retrieve vs answer directly.
    - Tool-based approach: agent picks retriever, summarizer, or calculator.
    - Self-reflective RAG: agent evaluates its own answer quality.

14. Memory-Based
    - Add conversation memory to support follow-up questions.
    - Use ConversationBufferMemory or ConversationSummaryMemory.
    - Remember user preferences and previous interactions.
"""

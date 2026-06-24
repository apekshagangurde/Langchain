from dotenv import load_dotenv

load_dotenv()

from youtube_transcript_api import YouTubeTranscriptApi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
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
chunks = splitter.split_text(full_script)

# print("\n=== Step 2: Text Splitting ===")
# print(f"Total chunks: {len(chunks)}")
# print(f"\nFirst Chunk:\n{chunks[0]}")

# Step 3: Store documents in FAISS vector store using from_documents
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
vector_store = FAISS.from_documents(documents, embeddings)

print("\n=== Step 3: FAISS Vector Store ===")
print(f"Total vectors stored: {vector_store.index.ntotal}")

# Step 4: Create retriever with similarity search, k=4
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

query = "What is AlphaFold?"
results = retriever.invoke(query)

# print("\n=== Step 4: Retrieval (Similarity Search, k=4) ===")
# print(f"Query: {query}")
# for i, doc in enumerate(results):
#     print(f"\nResult {i+1}: {doc.page_content[:200]}...")

# Step 5: Create LLM and Prompt Template
llm = ChatGroq(model="llama-3.3-70b-versatile")

prompt = ChatPromptTemplate.from_template(
    """You are a helpful assistant. Answer the question based only on the provided transcript context.
If the context is insufficient to answer the question, say "I don't know".

Context:
{context}

Question: {question}

Answer:"""
)

# Step 6: Retrieve, join page content, and invoke
retrieved_docs = retriever.invoke(query)
context = "\n\n".join([doc.page_content for doc in retrieved_docs])

chain = prompt | llm
response = chain.invoke({"context": context, "question": query})

print("\n=== Step 5 & 6: LLM Answer ===")
print(f"Question: {query}")
print(f"Answer: {response.content}")

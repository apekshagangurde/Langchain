from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_ollama import ChatOllama

load_dotenv()

# ---- Google Gemini ----
gemini_model = ChatGoogleGenerativeAI(model="gemini-2.0-flash")
gemini_response = gemini_model.invoke("What is LangGraph in one sentence?")
print("Gemini:", gemini_response.content)

# ---- Groq (fast inference for open-source models) ----
groq_model = ChatGroq(model="llama-3.3-70b-versatile")
groq_response = groq_model.invoke("What is LangGraph in one sentence?")
print("Groq (LLaMA 3.3):", groq_response.content)

# ---- Ollama (local LLMs - make sure Ollama is running) ----
ollama_model = ChatOllama(model="llama3.2")
ollama_response = ollama_model.invoke("What is LangGraph in one sentence?")
print("Ollama (LLaMA 3.2):", ollama_response.content)

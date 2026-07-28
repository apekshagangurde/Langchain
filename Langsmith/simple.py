"""
LangSmith
=========
LangSmith is LangChain's observability and evaluation platform for LLM
applications. You point an app at it (via env vars, no code changes needed
for LangChain/LangGraph components) and every run gets logged to a
dashboard where you can inspect, debug, and evaluate it.

What LangSmith traces (per run):
- Every LLM call — the exact prompt/messages sent, the raw response,
  token usage, latency, and model parameters.
- The run hierarchy — parent/child spans showing the order nodes, chains,
  or graph steps executed in (e.g. which node called which).
- Tool calls — which tool was invoked, with what input, and what it
  returned.
- Errors — full stack trace and the exact step where a run failed.
- Custom metadata/tags you attach (e.g. thread_id, run name) so runs can
  be filtered and grouped in the LangSmith UI.

Enabling it only requires these env vars (set in .env, then load_dotenv()
picks them up automatically):
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_API_KEY=<your langsmith api key>
    LANGCHAIN_PROJECT=<project name shown in the LangSmith dashboard>
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()

model = ChatGroq(model="llama-3.1-8b-instant")

response = model.invoke("What is LangSmith used for? Answer in one sentence.")

print(response.content)

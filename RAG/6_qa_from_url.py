"""
Simple Q&A from a URL
==========================

Loads a webpage's content with WebBaseLoader, then builds the simplest
possible chain — prompt | model | parser — and sends the whole page
content plus your question to it in one invoke() call. No splitting,
no embeddings, no vector store.
"""

import os

from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

load_dotenv()
os.environ.setdefault("USER_AGENT", "LangChainDemo/1.0")

URL = "https://sashakt-platform.github.io/docs/"
page_content = WebBaseLoader(URL).load()[0].page_content

prompt = ChatPromptTemplate.from_template(
    """Answer the question using only the content below.

Content:
{content}

Question: {question}"""
)
llm = ChatGroq(model="llama-3.1-8b-instant")
parser = StrOutputParser()

chain = prompt | llm | parser

print("Ask a question (type 'exit' to quit)\n")

while True:
    question = input("You: ")
    if question.strip().lower() in ("exit", "quit"):
        break
    answer = chain.invoke({"content": page_content, "question": question})
    print(f"Answer: {answer}\n")

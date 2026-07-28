from langchain_groq import ChatGroq
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
import os

os.environ["LANGCHAIN_PROJECT"] = "sequetial llm app"

load_dotenv()

prompt1 = PromptTemplate(
    template="Generate a detailed report on {topic}", input_variables=["topic"]
)

prompt2 = PromptTemplate(
    template="Generate a 5 pointer summary from the following text \n {text}",
    input_variables=["text"],
)

model = ChatGroq(model="llama-3.1-8b-instant", temperature=0.5)

parser = StrOutputParser()

chain = prompt1 | model | parser | prompt2 | model | parser
config = {
    "run_name": "sequential_chain",
    "tags": ["llm app", "report generation", "summarization"],
    "metadata": {"model": "llama-3.1-8b-instant", "model_temperature": 0.5},
}

result = chain.invoke({"topic": "Unemployment in India"}, config=config)

print(result)

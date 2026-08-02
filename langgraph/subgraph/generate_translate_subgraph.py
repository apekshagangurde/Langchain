from typing import TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph

load_dotenv()

model = ChatGroq(model="llama-3.1-8b-instant")


# --- subgraph: START -> translate -> END -----------------------------
# shares the "generated"/"translated" keys with the parent's state, so
# the compiled subgraph can be added directly as a node below.
class TranslateState(TypedDict):
    generated: str
    translated: str


def translate_node(state: TranslateState) -> TranslateState:
    prompt = f"Translate the following text from English to Hindi:\n\n{state['generated']}"
    translated = model.invoke(prompt).content
    return {"translated": translated}


translate_builder = StateGraph(TranslateState)

translate_builder.add_node("translate", translate_node)

translate_builder.add_edge(START, "translate")
translate_builder.add_edge("translate", END)

translate_subgraph = translate_builder.compile()


# --- parent graph: START -> generate -> translate (subgraph) -> END --
class TextState(TypedDict):
    topic: str
    generated: str
    translated: str


def generate_node(state: TextState) -> TextState:
    prompt = f"Write a short paragraph about: {state['topic']}"
    generated = model.invoke(prompt).content
    return {"generated": generated}


graph = StateGraph(TextState)

graph.add_node("generate", generate_node)
graph.add_node("translate", translate_subgraph)

graph.add_edge(START, "generate")
graph.add_edge("generate", "translate")
graph.add_edge("translate", END)

workflow = graph.compile()


if __name__ == "__main__":
    result = workflow.invoke({"topic": "the ocean"})
    print(result)

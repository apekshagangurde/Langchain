from typing import TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph

load_dotenv()

model = ChatGroq(model="llama-3.1-8b-instant")


# --- subgraph: START -> translate -> END -----------------------------
# no keys in common with the parent's state ("text"/"hindi_text" here
# vs "generated"/"translated" below), so it CANNOT be added directly
# as a node — the parent needs a wrapper node to translate state in/out.
class TranslateState(TypedDict):
    text: str
    hindi_text: str


def translate_node(state: TranslateState) -> TranslateState:
    prompt = f"Translate the following text from English to Hindi:\n\n{state['text']}"
    hindi_text = model.invoke(prompt).content
    return {"hindi_text": hindi_text}


translate_builder = StateGraph(TranslateState)

translate_builder.add_node("translate", translate_node)

translate_builder.add_edge(START, "translate")
translate_builder.add_edge("translate", END)

translate_subgraph = translate_builder.compile()


# --- parent graph: START -> generate -> translate (wrapper) -> END ---
class TextState(TypedDict):
    topic: str
    generated: str
    translated: str


def generate_node(state: TextState) -> TextState:
    prompt = f"Write a short paragraph about: {state['topic']}"
    generated = model.invoke(prompt).content
    return {"generated": generated}


def translate_wrapper_node(state: TextState) -> TextState:
    # map parent state -> subgraph's input schema
    subgraph_result = translate_subgraph.invoke({"text": state["generated"]})
    # map subgraph output -> parent's state
    return {"translated": subgraph_result["hindi_text"]}


graph = StateGraph(TextState)

graph.add_node("generate", generate_node)
graph.add_node("translate", translate_wrapper_node)

graph.add_edge(START, "generate")
graph.add_edge("generate", "translate")
graph.add_edge("translate", END)

workflow = graph.compile()


if __name__ == "__main__":
    result = workflow.invoke({"topic": "the ocean"})
    print(result)

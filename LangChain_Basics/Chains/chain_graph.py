# ==============================================================
# CHAIN + get_graph() IN LANGCHAIN
# ==============================================================
#
# WHAT IS A CHAIN?
#   A Chain connects steps using the | (pipe) operator.
#   Output of one step flows into the input of the next.
#
#   prompt | llm | parser
#     ↓         ↓       ↓
#   Step 1   Step 2   Step 3
#
# ONE SIMPLE EXAMPLE:
#   User asks a question → LLM answers → return clean string
#
# WHAT IS get_graph()?
#   Every chain has a .get_graph() method.
#   It returns a Graph object that describes the structure of
#   your chain — what nodes (steps) exist and how they connect.
#
#   chain.get_graph()              → Graph object
#   chain.get_graph().print_ascii()→ draws chain in the terminal
#   chain.get_graph().draw_mermaid()→ returns Mermaid diagram code
#   chain.get_graph().nodes        → dict of all steps
#   chain.get_graph().edges        → list of connections between steps
#   chain.get_graph().first_node() → the entry point of the chain
#   chain.get_graph().last_node()  → the exit point of the chain
#   chain.get_graph().to_json()    → full graph as a Python dict
#
# WHY IS get_graph() USEFUL?
#   - Debug: instantly see what steps your chain has
#   - Visualize: paste draw_mermaid() output into mermaid.live
#   - Inspect: count nodes, check edges, verify order
#
# REQUIREMENTS:
#   pip install grandalf   ← needed for print_ascii() only
# ==============================================================

from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")


# ==============================================================
# THE CHAIN — one simple example
# ==============================================================

prompt = ChatPromptTemplate.from_template(
    "Answer this question in one sentence: {question}"
)
parser = StrOutputParser()

chain = prompt | llm | parser

result = chain.invoke({"question": "What is LangChain?"})
print("Chain result:", result)


# ==============================================================
# get_graph() — EVERYTHING YOU CAN DO WITH IT
# ==============================================================

graph = chain.get_graph()

print("\n" + "=" * 55)
print("1. print_ascii() — draw the chain in the terminal")
print("=" * 55)
# Requires: pip install grandalf
graph.print_ascii()


print("=" * 55)
print("2. draw_mermaid() — Mermaid diagram code")
print("   Paste this at https://mermaid.live to see a diagram")
print("=" * 55)
print(graph.draw_mermaid())


print("=" * 55)
print("3. nodes — every step in the chain")
print("=" * 55)
# nodes is a dict: { node_id: Node(id, name, data, metadata) }
for node_id, node in graph.nodes.items():
    print(f"  Step : {node.name}")
    print(f"  ID   : {node_id}")
    print()


print("=" * 55)
print("4. edges — connections between steps")
print("=" * 55)
# edges is a list of Edge(source_id, target_id, data)
for i, edge in enumerate(graph.edges, start=1):
    source_name = graph.nodes[edge.source].name
    target_name = graph.nodes[edge.target].name
    print(f"  Edge {i}: {source_name}  →  {target_name}")
print()


print("=" * 55)
print("5. first_node() and last_node()")
print("=" * 55)
first = graph.first_node()
last  = graph.last_node()
print(f"  Entry point : {first.name}")
print(f"  Exit point  : {last.name}")
print()


print("=" * 55)
print("6. to_json() — full graph as a Python dict")
print("=" * 55)
data = graph.to_json()
print(f"  Keys in JSON : {list(data.keys())}")
print(f"  Total nodes  : {len(data['nodes'])}")
print(f"  Total edges  : {len(data['edges'])}")
print()
# print full json if you want to inspect
import json
print(json.dumps(data, indent=2, default=str))

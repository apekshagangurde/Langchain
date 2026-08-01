from typing import TypedDict

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.types import interrupt

load_dotenv()

model = ChatGroq(model="llama-3.1-8b-instant")


class PostState(TypedDict):
    topic: str
    research: str
    draft: str
    approved: bool
    posted: bool


def research_node(state: PostState) -> PostState:
    prompt = (
        f"List 3-4 key points worth mentioning in a social media post about: "
        f"{state['topic']}"
    )
    research = model.invoke(prompt).content
    return {"research": research}


def post_node(state: PostState) -> PostState:
    prompt = (
        f"Using this research, write a short punchy tweet (under 280 characters) "
        f"about '{state['topic']}':\n\n{state['research']}"
    )
    draft = model.invoke(prompt).content
    return {"draft": draft}


def human_review_node(state: PostState) -> PostState:
    # pauses the graph — the social media manager reviews the draft
    # before it goes out to X (Twitter)
    decision = interrupt(
        {
            "question": "Approve this post, or send edited text to rewrite it.",
            "draft": state["draft"],
        }
    )

    if decision == "approve":
        return {"approved": True, "posted": True}

    # anything else is the manager's rewritten post
    return {"draft": decision, "approved": True, "posted": True}


checkpointer = MemorySaver()

graph = StateGraph(PostState)

graph.add_node("research", research_node)
graph.add_node("post", post_node)
graph.add_node("human_review", human_review_node)

graph.add_edge(START, "research")
graph.add_edge("research", "post")
graph.add_edge("post", "human_review")
graph.add_edge("human_review", END)

workflow = graph.compile(checkpointer=checkpointer)

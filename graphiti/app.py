"""Streamlit UI for searching the graph built by add_episodes.py.

    docker compose up -d
    streamlit run app.py

Same three search approaches as search.py, just with a text box instead of
argv. The search logic is imported rather than duplicated.
"""

import asyncio
import threading

import streamlit as st

# Imported for side effects too: loads .env and pins EMBEDDING_DIM before
# graphiti_core is imported.
from add_episodes import make_graphiti
from search import RECIPES, answer_from_facts, find_focal_node

st.set_page_config(page_title="Graphiti search", page_icon="🔎")


@st.cache_resource
def get_client():
    """Build Graphiti once per session, not once per keystroke.

    Streamlit re-runs this whole script on every interaction, and
    make_graphiti() loads two sentence-transformers models (~100MB) and opens
    a FalkorDB connection. cache_resource keeps one instance across re-runs.

    The event loop is cached alongside it, because the driver's async
    connections bind to the loop that created them -- a fresh asyncio.run()
    per re-run would close the loop out from under them.

    The loop gets its own thread and is never driven from the script thread.
    Streamlit starts a new script run as soon as you touch a widget, without
    waiting for the previous run to finish, so two runs share this one cached
    loop. Calling loop.run_until_complete() from the second run while the
    first is still inside it raises "RuntimeError: this event loop is already
    running". Owning the loop in a separate thread and submitting work with
    run_coroutine_threadsafe() makes overlapping runs safe.
    """
    loop = asyncio.new_event_loop()
    threading.Thread(
        target=loop.run_forever, daemon=True, name="graphiti-eventloop"
    ).start()
    return loop, make_graphiti()


def run(coro):
    """Run a coroutine on the cached loop from Streamlit's script thread."""
    loop, _ = get_client()
    return asyncio.run_coroutine_threadsafe(coro, loop).result()


loop, graphiti = get_client()

st.title("🔎 Graphiti search")
st.caption("Searches the knowledge graph in FalkorDB. Run `add_episodes.py` first.")

with st.sidebar:
    st.header("Options")
    recipe = st.selectbox(
        "Search mode",
        ["facts", *RECIPES],
        help=(
            "**facts** - graphiti.search(): BM25 + cosine, merged with "
            "Reciprocal Rank Fusion. The only mode that supports node "
            "distance reranking.\n\n"
            "**edges** - same, via the configurable search_().\n\n"
            "**edges_diverse** - MMR reranking: trades relevance for variety, "
            "so it can return fewer results than you asked for.\n\n"
            "**edges_accurate** - cross-encoder reranking. Most accurate, "
            "slowest.\n\n"
            "**edges_popular** - favours facts mentioned in many episodes.\n\n"
            "**nodes** - entities instead of facts.\n\n"
            "**all** - facts, entities and communities together."
        ),
    )
    limit = st.slider("Max results", 1, 25, 10)

    narrate = st.toggle(
        "Answer in natural language",
        value=True,
        help=(
            "Sends the retrieved facts to Groq and shows a written answer, "
            "with the raw facts underneath. Turn off to see only the facts."
        ),
    )

    focus = st.text_input(
        "Focal entity (optional)",
        placeholder="e.g. Arjun",
        help=(
            "Reranks results by graph distance to this entity, pulling its own "
            "facts to the top. Only applies in **facts** mode."
        ),
    )
    if focus and recipe != "facts":
        st.info("Node distance reranking only applies in **facts** mode.")

query = st.text_input("Query", placeholder="who works at Dalgo?")
go = st.button("Search", type="primary")

if go or query:
    if not query.strip():
        st.warning("Type a query first.")
        st.stop()

    center_uuid = None
    if focus.strip():
        with st.spinner(f'Looking up "{focus}"...'):
            node, by_name = run(find_focal_node(graphiti, focus.strip()))
        if node is None:
            st.warning("The graph has no entities. Run `add_episodes.py` first.")
        elif by_name:
            center_uuid = node.uuid
            st.success(f"Focal node: **{node.name}**")
        else:
            # Hybrid search always returns nearest neighbours, so an unknown
            # name yields a loose match rather than nothing. Say so.
            center_uuid = node.uuid
            st.warning(
                f'No entity named "{focus}" — closest is **{node.name}**, using that.'
            )

    with st.spinner("Searching..."):
        if recipe == "facts":
            edges = run(
                graphiti.search(
                    query=query, center_node_uuid=center_uuid, num_results=limit
                )
            )
            results = None
        else:
            config = RECIPES[recipe].model_copy(deep=True)
            config.limit = limit
            results = run(graphiti.search_(query=query, config=config))
            edges = results.edges

    # What the LLM is allowed to use. Node summaries count as context in
    # nodes mode, where the search returns no edges at all.
    # citation[n] is the number the answer will cite this item as, so the
    # numbering shown below matches the [1]/[2] markers in the prose.
    context = [edge.fact for edge in edges]
    citation: dict[str, int] = {}
    if results is not None:
        for node in results.nodes:
            summary = (node.summary or "").strip()
            if summary:
                context.append(f"{node.name}: {summary}")
                citation[node.uuid] = len(context)

    if not context:
        st.info("No results found. Try a broader query, or run `add_episodes.py`.")
        st.stop()

    if narrate:
        with st.spinner("Writing an answer..."):
            answer = run(answer_from_facts(query, context))
        st.subheader("Answer")
        st.write(answer)
        st.caption(
            f"Grounded in the {len(context)} retrieved item(s) below — "
            "the model was given nothing else."
        )
        st.divider()

    if edges:
        # Numbered to match the [1]/[2] citations in the answer above.
        st.subheader(f"Facts ({len(edges)})")
        for i, edge in enumerate(edges, start=1):
            st.markdown(f"{i}. {edge.fact}")

    if results is not None:
        if results.nodes:
            st.subheader(f"Entities ({len(results.nodes)})")
            for node in results.nodes:
                n = citation.get(node.uuid)
                with st.expander(f"{n}. {node.name}" if n else node.name):
                    st.write((node.summary or "_no summary_").strip())
        if results.communities:
            st.subheader(f"Communities ({len(results.communities)})")
            for community in results.communities:
                st.markdown(f"- {community.name}")

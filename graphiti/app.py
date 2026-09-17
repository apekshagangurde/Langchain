"""Streamlit UI for searching the graph built by add_episodes.py.

    docker compose up -d
    streamlit run app.py

Same three search approaches as search.py, just with a text box instead of
argv. The search logic is imported rather than duplicated.
"""

import asyncio

import streamlit as st

# Imported for side effects too: loads .env and pins EMBEDDING_DIM before
# graphiti_core is imported.
from add_episodes import make_graphiti
from search import RECIPES, find_focal_node

st.set_page_config(page_title="Graphiti search", page_icon="🔎")


@st.cache_resource
def get_client():
    """Build Graphiti once per session, not once per keystroke.

    Streamlit re-runs this whole script on every interaction, and
    make_graphiti() loads two sentence-transformers models (~100MB) and opens
    a FalkorDB connection. cache_resource keeps one instance across re-runs.

    The event loop is cached alongside it: the driver's async connections bind
    to the loop that created them, so a fresh asyncio.run() per re-run would
    close the loop out from under them and break the next query.
    """
    loop = asyncio.new_event_loop()
    return loop, make_graphiti()


def run(coro):
    loop, _ = get_client()
    return loop.run_until_complete(coro)


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

    if edges:
        st.subheader(f"Facts ({len(edges)})")
        for edge in edges:
            st.markdown(f"- {edge.fact}")

    if results is not None:
        if results.nodes:
            st.subheader(f"Entities ({len(results.nodes)})")
            for node in results.nodes:
                with st.expander(node.name):
                    st.write((node.summary or "_no summary_").strip())
        if results.communities:
            st.subheader(f"Communities ({len(results.communities)})")
            for community in results.communities:
                st.markdown(f"- {community.name}")

        if not (results.edges or results.nodes or results.communities):
            st.info("No results found.")
    elif not edges:
        st.info("No facts found.")

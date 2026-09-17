"""Streamlit UI for searching the graph built by add_episodes.py.

    docker compose up -d
    streamlit run app.py

Same three search approaches as search.py, just with a text box instead of
argv. The search logic is imported rather than duplicated.
"""

import asyncio
import os
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

DEFAULT_GRAPH = os.getenv("FALKORDB_DATABASE", "graphiti")


@st.cache_data(ttl=30)
def list_graphs() -> list[tuple[str, int]]:
    """(graph name, entity count) for every graph, biggest first.

    ingest_markdown.py --group-id writes to a graph of that name, so this is
    the list of ingested documents plus the default graph.

    The counts are the point: querying a deleted FalkorDB graph recreates it
    as an empty shell, so the list alone will happily offer you a graph with
    nothing in it. Cached briefly so a running ingest shows up.
    """

    async def fetch() -> list[tuple[str, int]]:
        client = graphiti.driver.client
        # default_db is FalkorDB's own bookkeeping graph, not one of ours.
        names = [n for n in await client.list_graphs() if n != "default_db"]
        out = []
        for name in names:
            try:
                result = await client.select_graph(name).query(
                    "MATCH (e:Entity) RETURN count(e)"
                )
                out.append((name, int(result.result_set[0][0])))
            except Exception:
                out.append((name, 0))
        return out

    try:
        graphs = run(fetch())
    except Exception:
        return [(DEFAULT_GRAPH, 0)]

    if not graphs:
        return [(DEFAULT_GRAPH, 0)]
    # Biggest first, so the graph you just filled is at the top.
    return sorted(graphs, key=lambda pair: (-pair[1], pair[0]))

st.title("🔎 Graphiti search")
caption = st.empty()  # filled in once the graph is chosen, below

with st.sidebar:
    st.header("Options")

    graphs = list_graphs()
    counts = dict(graphs)
    labels = [f"{name}  ({count} entities)" for name, count in graphs]

    # Open on the fullest graph. FALKORDB_DATABASE is not a useful default
    # here: it points at the starter graph from add_episodes.py, so an
    # ingested document would sit unsearched while the app answered from
    # three toy episodes.
    choice = st.selectbox(
        "Graph",
        labels,
        index=0,
        help=(
            "On FalkorDB each group_id is a separate graph, so an ingest run "
            "with `--group-id kabil` is only searchable here by picking "
            "`kabil`. Searching a different graph finds nothing from it."
        ),
    )
    group = graphs[labels.index(choice)][0]

    if not counts.get(group):
        st.warning(f"`{group}` is empty. Nothing to search in it yet.")
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

caption.caption(
    f"Searching the **{group}** graph in FalkorDB "
    f"({counts.get(group, 0)} entities)."
)

query = st.text_input("Query", placeholder="what do you know about KABIL?")
go = st.button("Search", type="primary")

if go or query:
    if not query.strip():
        st.warning("Type a query first.")
        st.stop()

    # None for the driver's own default graph; a one-element list otherwise.
    group_ids = None if group == DEFAULT_GRAPH else [group]

    center_uuid = None
    if focus.strip():
        with st.spinner(f'Looking up "{focus}"...'):
            node, by_name = run(find_focal_node(graphiti, focus.strip(), group_ids))
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
                    query=query,
                    center_node_uuid=center_uuid,
                    num_results=limit,
                    group_ids=group_ids,
                )
            )
            results = None
        else:
            config = RECIPES[recipe].model_copy(deep=True)
            config.limit = limit
            results = run(
                graphiti.search_(query=query, config=config, group_ids=group_ids)
            )
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
        st.info(
            f"No results in the **{group}** graph. "
            "If your data was ingested under a different --group-id, pick it above."
        )
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

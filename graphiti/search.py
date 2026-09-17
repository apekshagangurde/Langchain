"""Step 3: search the graph built by add_episodes.py.

    docker compose up -d
    python search.py                          # interactive prompt
    python search.py "who works at Dalgo?"    # one-shot
    python search.py "wool runners" --focus Jane
    python search.py "Dalgo" --nodes          # entities instead of facts

Three search approaches are shown:

1. Hybrid search -- graphiti.search(query)
   BM25 + cosine similarity, merged with Reciprocal Rank Fusion. Broad recall.

2. Node distance reranking -- graphiti.search(query, center_node_uuid=...)
   Same hybrid search, then reweighted by graph proximity to a focal entity.
   Use it for entity-specific questions: --focus Jane pulls up Jane's own
   facts ahead of generally-relevant ones.

3. Configurable search -- graphiti.search_(query, config=<recipe>)
   The low-level method. Returns nodes/edges/communities instead of a flat
   fact list, and takes a SearchConfig recipe (see RECIPES below).
   Note: graphiti._search() is the deprecated name for the same thing.
"""

import argparse
import asyncio

# Imported for its side effects too: loads .env and pins EMBEDDING_DIM before
# graphiti_core is imported. make_graphiti() wires up Groq + the local
# embedder and reranker, so no search path reaches OpenAI.
from add_episodes import make_graphiti

from graphiti_core.search.search_config_recipes import (
    COMBINED_HYBRID_SEARCH_RRF,
    EDGE_HYBRID_SEARCH_CROSS_ENCODER,
    EDGE_HYBRID_SEARCH_EPISODE_MENTIONS,
    EDGE_HYBRID_SEARCH_MMR,
    EDGE_HYBRID_SEARCH_RRF,
    NODE_HYBRID_SEARCH_RRF,
)

# The recipes worth reaching for here. The full set of 16 lives in
# graphiti_core/search/search_config_recipes.py.
RECIPES = {
    "edges": EDGE_HYBRID_SEARCH_RRF,
    # MMR trades some relevance for diversity -- less redundant results
    "edges_diverse": EDGE_HYBRID_SEARCH_MMR,
    # Cross-encoder scores query+fact jointly. Most accurate, slowest:
    # LocalReranker runs ms-marco-MiniLM on every candidate.
    "edges_accurate": EDGE_HYBRID_SEARCH_CROSS_ENCODER,
    # Favours facts mentioned across many episodes
    "edges_popular": EDGE_HYBRID_SEARCH_EPISODE_MENTIONS,
    "nodes": NODE_HYBRID_SEARCH_RRF,
    "all": COMBINED_HYBRID_SEARCH_RRF,
}


async def find_focal_node(graphiti, name: str):
    """Resolve a name like "Jane" to an entity node, for center_node_uuid.

    search() takes a uuid, not a name, so this is the lookup step. Returns
    None if nothing matches.

    A name match is preferred over the top semantic hit: hybrid node search
    scores summaries too, so "Arjun" otherwise resolves to Priya Sharma
    because her summary says she mentors him.

    Returns (node, matched_by_name). matched_by_name is False when the name
    hit nothing and this fell back to the nearest semantic neighbour.
    """
    results = await graphiti.search_(query=name, config=NODE_HYBRID_SEARCH_RRF)
    if not results.nodes:
        return None, False

    target = name.casefold()
    for node in results.nodes:
        if node.name.casefold() == target:
            return node, True
    for node in results.nodes:
        # "Arjun" -> "Arjun Rao". Split on words so a partial like "Ar"
        # doesn't win over a genuinely better semantic match.
        if target in node.name.casefold().split():
            return node, True

    # Hybrid search always returns its nearest neighbours, so there is no
    # "not found" -- an unknown name lands here on a loose semantic match.
    return results.nodes[0], False


async def run_search(graphiti, query: str, focus: str | None, recipe: str, limit: int):
    center_uuid = None
    if focus:
        node, by_name = await find_focal_node(graphiti, focus)
        if node is None:
            print('  graph has no entities -- searching without a focal node')
        elif by_name:
            center_uuid = node.uuid
            print(f"  focal node: {node.name} ({node.uuid})")
        else:
            center_uuid = node.uuid
            print(f'  no entity named "{focus}" -- closest is {node.name}, using that')

    # The plain fact list: enough for most questions, and the only path that
    # applies node distance reranking.
    if recipe == "facts":
        edges = await graphiti.search(
            query=query, center_node_uuid=center_uuid, num_results=limit
        )
        if not edges:
            print("  no facts found")
            return
        for edge in edges:
            print(f"  - {edge.fact}")
        return

    # The configurable path.
    config = RECIPES[recipe].model_copy(deep=True)
    config.limit = limit
    results = await graphiti.search_(
        query=query, config=config, center_node_uuid=center_uuid
    )

    if results.edges:
        print("  facts:")
        for edge in results.edges:
            print(f"    - {edge.fact}")
    if results.nodes:
        print("  entities:")
        for node in results.nodes:
            summary = (node.summary or "").strip().replace("\n", " ")
            if len(summary) > 100:
                summary = summary[:100] + "..."
            print(f"    - {node.name}" + (f" -- {summary}" if summary else ""))
    if results.communities:
        print("  communities:")
        for community in results.communities:
            print(f"    - {community.name}")
    if not (results.edges or results.nodes or results.communities):
        print("  no results found")


async def interactive(graphiti, recipe: str, limit: int):
    """Prompt loop -- keeps the embedder and reranker models in memory between
    queries instead of reloading them per run."""
    print("\nType a query, or 'quit' to exit.")
    print("  prefix with @Name to rerank by distance to that entity")
    print(f"  :recipe <name> to switch mode ({', '.join(['facts', *RECIPES])})\n")

    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return

        if not line:
            continue
        if line.lower() in {"quit", "exit", "q"}:
            return

        if line.startswith(":recipe "):
            choice = line.split(maxsplit=1)[1].strip()
            if choice in RECIPES or choice == "facts":
                recipe = choice
                print(f"  recipe = {recipe}")
            else:
                print(f"  unknown recipe. Choices: {['facts', *RECIPES]}")
            continue

        # "@Jane can she wear wool?" -> focus="Jane", query="can she wear wool?"
        focus = None
        if line.startswith("@"):
            focus, _, rest = line[1:].partition(" ")
            line = rest.strip() or focus

        await run_search(graphiti, line, focus, recipe, limit)
        print()


async def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("query", nargs="?", help="omit to get an interactive prompt")
    parser.add_argument("--focus", help="entity name to rerank by graph distance")
    parser.add_argument(
        "--recipe",
        default="facts",
        choices=["facts", *RECIPES],
        help="facts (default) uses graphiti.search(); the rest use search_()",
    )
    parser.add_argument("--nodes", action="store_true", help="shorthand for --recipe nodes")
    parser.add_argument("-n", "--limit", type=int, default=10)
    args = parser.parse_args()

    recipe = "nodes" if args.nodes else args.recipe

    graphiti = make_graphiti()
    try:
        if args.query:
            print(f'\nquery: "{args.query}"  (recipe: {recipe})')
            await run_search(graphiti, args.query, args.focus, recipe, args.limit)
        else:
            await interactive(graphiti, recipe, args.limit)
    finally:
        await graphiti.close()


if __name__ == "__main__":
    asyncio.run(main())

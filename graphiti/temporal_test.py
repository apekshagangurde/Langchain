"""Step 5: does Graphiti actually record when a fact stopped being true?

    docker compose up -d
    python temporal_test.py            # add the episodes, then show the edges
    python temporal_test.py --show     # show the edges only, no LLM calls

Writes to the default graph (the Priya/Dalgo starter data), not to any
--group-id graph, so it cannot disturb the ingested documents.

The test is two contradictory statements given different reference_times:

    Jan 2023   Priya works out of the Pune office.
    Jul 2024   Priya moved from Pune to the Bengaluru office.

A plain store would overwrite Pune with Bengaluru. Graphiti should instead
keep both edges and mark the first one as no longer valid, so that "where is
Priya now?" and "where was Priya in 2023?" have different answers.

Four timestamps are involved, and they mean different things:
    valid_at    when the fact started being true in the world
    invalid_at  when it stopped being true in the world
    created_at  when Graphiti first wrote the fact down
    expired_at  when Graphiti learned the fact was superseded
"""

import argparse
import asyncio
from datetime import datetime, timezone

from add_episodes import make_graphiti

from graphiti_core.nodes import EpisodeType  # noqa: E402

# Deliberately small bodies. Graphiti's own prompt is ~7,500 tokens against an
# 8,000 TPM free-tier ceiling, so only short episodes get through.
EPISODES = [
    (
        "priya_office_2023",
        "Priya Sharma works out of the Dalgo Pune office as of January 2023.",
        datetime(2023, 1, 15, tzinfo=timezone.utc),
    ),
    (
        "priya_office_2024",
        "Priya Sharma moved from the Dalgo Pune office to the Dalgo Bengaluru "
        "office on 1 July 2024.",
        datetime(2024, 7, 1, tzinfo=timezone.utc),
    ),
]

# r.name is the relationship the model invented; the Cypher type is always
# RELATES_TO, so filtering on the type alone would return every fact.
EDGE_QUERY = """
MATCH (a:Entity)-[r:RELATES_TO]->(b:Entity)
WHERE a.name CONTAINS 'Priya' OR b.name CONTAINS 'Priya'
RETURN a.name AS src, r.name AS rel, b.name AS dst, r.fact AS fact,
       r.valid_at AS valid_at, r.invalid_at AS invalid_at,
       r.created_at AS created_at, r.expired_at AS expired_at
ORDER BY r.valid_at
"""


def short(value) -> str:
    """Dates as YYYY-MM-DD; anything unset as a visible dash."""
    if value in (None, "", "null"):
        return "—"
    text = str(value)
    return text[:10] if len(text) >= 10 and text[4] == "-" else text


async def show_edges(graphiti) -> None:
    records, *_ = await graphiti.driver.execute_query(EDGE_QUERY)
    rows = records or []

    if not rows:
        print("no Priya edges found — run without --show first")
        return

    print(f"\n{len(rows)} edge(s) mentioning Priya:\n")
    header = f"{'relationship':<22}{'target':<18}{'valid_at':<12}{'invalid_at':<12}{'expired_at':<12}"
    print(header)
    print("-" * len(header))
    for row in rows:
        get = row.get if isinstance(row, dict) else lambda k: row[k]
        print(
            f"{str(get('rel'))[:21]:<22}"
            f"{str(get('dst'))[:17]:<18}"
            f"{short(get('valid_at')):<12}"
            f"{short(get('invalid_at')):<12}"
            f"{short(get('expired_at')):<12}"
        )

    print("\nfacts in full:")
    for row in rows:
        get = row.get if isinstance(row, dict) else lambda k: row[k]
        mark = " [SUPERSEDED]" if get("invalid_at") or get("expired_at") else ""
        print(f"  - {get('fact')}{mark}")


async def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument(
        "--show", action="store_true", help="only print the edges, no LLM calls"
    )
    args = parser.parse_args()

    graphiti = make_graphiti()  # default graph, no group_id
    try:
        if not args.show:
            await graphiti.build_indices_and_constraints()

            for name, body, reference_time in EPISODES:
                print(f"\n[{name}] {reference_time.date()}  {body}")
                result = await graphiti.add_episode(
                    name=name,
                    episode_body=body,
                    source=EpisodeType.text,
                    source_description="temporal behaviour test",
                    # The event's own date, not now() -- this is what Graphiti
                    # reasons over when deciding which fact came first.
                    reference_time=reference_time,
                )
                print(f"  entities: {[n.name for n in result.nodes]}")
                for edge in result.edges:
                    print(f"    - {edge.fact}")

        await show_edges(graphiti)
    finally:
        await graphiti.close()


if __name__ == "__main__":
    asyncio.run(main())

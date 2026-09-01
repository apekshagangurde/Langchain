"""
Named, reusable GDELT queries for tracking CSOs, FCRA actions, and funders
in North East India.

Query text is copied verbatim from the source doc. The `keyword=` parameter
on gdeltdoc's Filters class can only build a single OR group, so queries that
need (OR group) AND (OR group) are built as raw query text and injected
straight into Filters.query_params instead of going through `keyword=`.

Usage:
    python3 named_queries.py                  # run every query, timespan=1d
    python3 named_queries.py cso_ngo_activity  # run just one query
"""

import os
import sys
import time

import pandas as pd

from gdeltdoc import GdeltDoc, Filters
from gdeltdoc.errors import RateLimitError

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")

# Note: the source doc warns that boolean strings with five or six ORs get
# unreliable. cso_ngo_activity and fcra_actions exceed that here because
# they're copied as-is from the doc -- trim the OR list if results look thin.
QUERIES = {
    "cso_ngo_activity": (
        '("North East India" OR Assam OR Meghalaya OR Nagaland OR Manipur OR '
        'Tripura OR "Arunachal Pradesh" OR Mizoram OR Sikkim) '
        '(NGO OR "civil society" OR "non-profit" OR "voluntary organisation")'
    ),
    "fcra_actions": (
        'FCRA ("registration cancelled" OR "licence cancelled" OR '
        '"licence suspended" OR "FCRA renewal" OR "prior permission" OR '
        '"show cause notice")'
    ),
    "fcra_policy": (
        '("FCRA amendment" OR "Foreign Contribution Regulation Rules")'
    ),
    "funders_grants": (
        '("grant" OR "funding announcement" OR "awarded a grant" OR '
        '"philanthropic support") (Assam OR "North East India" OR Nagaland OR '
        'Meghalaya)'
    ),
}


def run_query(name: str, timespan: str = "1d", retries: int = 6):
    """Run one of the named queries above and return the articles DataFrame.

    Retries with increasing backoff on GDELT's 429 rate limit rather than
    failing outright -- the API allows only ~1 request every 5 seconds and
    seems to extend the cooldown after repeated hits.
    """
    if name not in QUERIES:
        raise ValueError(f"Unknown query '{name}'. Choices: {list(QUERIES)}")

    f = Filters(timespan=timespan)
    f.query_params.insert(0, QUERIES[name])

    gd = GdeltDoc()

    delay = 20
    for attempt in range(retries):
        try:
            return gd.article_search(f)
        except RateLimitError:
            if attempt == retries - 1:
                raise
            print(f"  rate limited, waiting {delay}s before retry...")
            time.sleep(delay)
            delay *= 2


def save_results(name: str, df: pd.DataFrame) -> int:
    """
    Append new articles to data/<name>.csv, deduplicated by url.
    Does not re-pull or overwrite history -- only new rows are added.

    Returns the number of genuinely new rows written.
    """
    os.makedirs(DATA_DIR, exist_ok=True)
    path = os.path.join(DATA_DIR, f"{name}.csv")

    if len(df) == 0:
        return 0

    if os.path.exists(path):
        existing = pd.read_csv(path)
        new_rows = df[~df["url"].isin(existing["url"])]
        combined = pd.concat([existing, new_rows], ignore_index=True)
    else:
        new_rows = df
        combined = df

    combined.to_csv(path, index=False)
    return len(new_rows)


if __name__ == "__main__":
    names = sys.argv[1:] or list(QUERIES)

    for i, name in enumerate(names):
        if i > 0:
            time.sleep(10)  # avoid GDELT's rate limit on back-to-back calls

        df = run_query(name)
        new_count = save_results(name, df)
        print(
            f"\n=== {name}: {len(df)} articles fetched, "
            f"{new_count} new, saved to data/{name}.csv ==="
        )
        if len(df):
            print(df[["title", "domain", "seendate"]].head())

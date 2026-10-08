"""HTTP API over the graph, for hosting (Step 5).

    uvicorn api:app --reload             # local, against whatever .env points at
    curl localhost:8000/health

Same client as the scripts: make_graphiti() wires up Claude plus the local
embedder and reranker, so nothing here reaches OpenAI. The backend is
GRAPH_BACKEND, as everywhere else.

Every route but /health needs an `x-api-key` header matching GRAPHITI_API_KEY.
The server refuses to start without one: it holds the Anthropic key, so an
open /episodes would let anyone spend it.

Large ingests stay on ingest_markdown.py -- a document takes minutes of Claude
calls, longer than an HTTP request should live.
"""

import os
import secrets
from contextlib import asynccontextmanager

# Imported for side effects too: loads .env and pins EMBEDDING_DIM before
# graphiti_core is imported.
from add_episodes import (
    DEFAULT_BACKEND,
    add_episode,
    groups_are_graphs,
    make_graphiti,
)
from fastapi import Depends, FastAPI, Header, HTTPException  # noqa: E402
from pydantic import BaseModel, Field  # noqa: E402

API_KEY = os.environ.get("GRAPHITI_API_KEY", "")
if not API_KEY:
    raise RuntimeError("GRAPHITI_API_KEY is not set -- see .env.example.")

GROUP_PATTERN = r"^[a-zA-Z0-9_-]+$"  # graphiti's validate_group_id

# One client per FalkorDB graph; on Neo4j every group shares the one client,
# because `database` is ignored there.
_clients = {}


def client_for(group_id: str | None):
    key = group_id if groups_are_graphs(DEFAULT_BACKEND) else None
    if key not in _clients:
        _clients[key] = make_graphiti(database=key, backend=DEFAULT_BACKEND)
    return _clients[key]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Build the default client up front so the first request does not pay for
    # loading the embedding and reranker models.
    client_for(None)
    yield
    for client in _clients.values():
        await client.close()


app = FastAPI(title="Graphiti", lifespan=lifespan)


def require_key(x_api_key: str = Header(default="")):
    if not secrets.compare_digest(x_api_key, API_KEY):
        raise HTTPException(status_code=401, detail="bad or missing x-api-key")


class SearchIn(BaseModel):
    query: str = Field(min_length=1)
    group_id: str | None = Field(default=None, pattern=GROUP_PATTERN)
    limit: int = Field(default=10, ge=1, le=50)


class EpisodeIn(BaseModel):
    text: str = Field(min_length=1)
    name: str = "api-episode"
    source_description: str = "added via api.py"
    group_id: str | None = Field(default=None, pattern=GROUP_PATTERN)


@app.get("/health")
async def health():
    await client_for(None).driver.health_check()
    return {"ok": True, "backend": DEFAULT_BACKEND}


@app.post("/search", dependencies=[Depends(require_key)])
async def search(body: SearchIn):
    graphiti = client_for(body.group_id)
    edges = await graphiti.search(
        query=body.query,
        num_results=body.limit,
        group_ids=[body.group_id] if body.group_id else None,
    )
    facts = [
        {
            "fact": e.fact,
            "valid_at": e.valid_at,
            "invalid_at": e.invalid_at,
            "uuid": e.uuid,
        }
        for e in edges
    ]
    # Straight from the graph -- no Claude call on the read path.
    return {"query": body.query, "facts": facts}


@app.post("/episodes", dependencies=[Depends(require_key)])
async def episodes(body: EpisodeIn):
    result = await add_episode(
        client_for(body.group_id),
        body.text,
        name=body.name,
        source_description=body.source_description,
        group_id=body.group_id,
    )
    return {
        "entities": [n.name for n in result.nodes],
        "facts": [e.fact for e in result.edges],
    }

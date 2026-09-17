"""Step 2: add a few small episodes and let Graphiti build the graph.

    docker compose up -d
    python add_episodes.py

Re-running adds the episodes again. To start clean:
    docker exec graphiti-falkordb redis-cli GRAPH.DELETE graphiti
"""

import asyncio
import os

from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

# Must be set before importing graphiti_core: it reads EMBEDDING_DIM at import time.
# 384 = sentence-transformers/all-MiniLM-L6-v2
os.environ.setdefault("EMBEDDING_DIM", "384")

from graphiti_core import Graphiti  # noqa: E402
from graphiti_core.cross_encoder.client import CrossEncoderClient  # noqa: E402
from graphiti_core.driver.falkordb_driver import FalkorDriver  # noqa: E402
from graphiti_core.embedder.client import EmbedderClient, EmbedderConfig  # noqa: E402
from graphiti_core.llm_client.config import LLMConfig  # noqa: E402
from graphiti_core.llm_client.groq_client import GroqClient  # noqa: E402
from graphiti_core.nodes import EpisodeType  # noqa: E402

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
RERANKER_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class LocalEmbedder(EmbedderClient):
    """Graphiti ships only API-backed embedders and Groq has no embeddings
    endpoint, so embeddings run locally via sentence-transformers."""

    def __init__(self):
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(EMBEDDING_MODEL)
        dim = self.model.get_embedding_dimension()
        if dim != int(os.environ["EMBEDDING_DIM"]):
            raise ValueError(f"set EMBEDDING_DIM={dim} to match {EMBEDDING_MODEL}")
        self.config = EmbedderConfig(embedding_dim=dim)

    async def create(self, input_data) -> list[float]:
        text = input_data if isinstance(input_data, str) else str(input_data)
        return (await self.create_batch([text]))[0]

    async def create_batch(self, input_data_list: list[str]) -> list[list[float]]:
        if not input_data_list:
            return []
        loop = asyncio.get_running_loop()
        vectors = await loop.run_in_executor(
            None,
            lambda: self.model.encode(input_data_list, normalize_embeddings=True),
        )
        return [[float(x) for x in v] for v in vectors]


class LocalReranker(CrossEncoderClient):
    """Local reranker so search doesn't fall back to OpenAI either."""

    def __init__(self):
        from sentence_transformers import CrossEncoder

        self.model = CrossEncoder(RERANKER_MODEL)

    async def rank(self, query: str, passages: list[str]) -> list[tuple[str, float]]:
        if not passages:
            return []
        loop = asyncio.get_running_loop()
        scores = await loop.run_in_executor(
            None, self.model.predict, [[query, p] for p in passages]
        )
        return sorted(
            ((p, float(s)) for p, s in zip(passages, scores, strict=False)),
            key=lambda pair: pair[1],
            reverse=True,
        )


def make_graphiti() -> Graphiti:
    return Graphiti(
        graph_driver=FalkorDriver(
            host=os.getenv("FALKORDB_HOST", "localhost"),
            port=int(os.getenv("FALKORDB_PORT", "6379")),
            database=os.getenv("FALKORDB_DATABASE", "graphiti"),
        ),
        llm_client=GroqClient(
            config=LLMConfig(
                api_key=os.environ["GROQ_API_KEY"],
                model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"),
            )
        ),
        embedder=LocalEmbedder(),
        cross_encoder=LocalReranker(),
    )


# Small and deliberately connected, so the extracted graph has edges to look at.
EPISODES = [
    "Priya Sharma is a data engineer at Dalgo. She joined in March 2023.",
    "Dalgo is a data platform built by Project Tech4Dev for non-profits.",
    "Priya mentors Arjun Rao, a junior analyst who joined Dalgo in 2024.",
]


async def main():
    graphiti = make_graphiti()
    try:
        # Creates indices and constraints. Safe to run repeatedly.
        await graphiti.build_indices_and_constraints()

        for i, text in enumerate(EPISODES, start=1):
            result = await graphiti.add_episode(
                name=f"episode-{i}",
                episode_body=text,
                source=EpisodeType.text,
                source_description="step 2 starter episodes",
                reference_time=datetime.now(timezone.utc),
            )
            print(f"\nepisode-{i}: {text}")
            print(f"  entities ({len(result.nodes)}): {[n.name for n in result.nodes]}")
            print(f"  facts    ({len(result.edges)}):")
            for edge in result.edges:
                print(f"    - {edge.fact}")
    finally:
        await graphiti.close()


if __name__ == "__main__":
    asyncio.run(main())

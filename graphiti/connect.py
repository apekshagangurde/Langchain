"""Step 1: connect to FalkorDB through Graphiti and confirm it works.

    docker compose up -d
    python connect.py
"""

import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # graphiti/.env
# Falls back to the shared key in "Langchain models/.env" (does not override the local one)
load_dotenv(Path(__file__).resolve().parent.parent / '.env')

# Must be set before importing graphiti_core: it reads EMBEDDING_DIM at import time.
# 384 = sentence-transformers/all-MiniLM-L6-v2
os.environ.setdefault('EMBEDDING_DIM', '384')

from graphiti_core import Graphiti  # noqa: E402
from graphiti_core.driver.falkordb_driver import FalkorDriver  # noqa: E402
from graphiti_core.llm_client.config import LLMConfig  # noqa: E402
from graphiti_core.llm_client.groq_client import GroqClient  # noqa: E402

FALKOR_HOST = os.getenv('FALKORDB_HOST', 'localhost')
FALKOR_PORT = int(os.getenv('FALKORDB_PORT', '6379'))


async def main():
    graphiti = Graphiti(
        # FalkorDB is passed as a driver; uri/user/password are Neo4j-only
        graph_driver=FalkorDriver(
            host=FALKOR_HOST,
            port=FALKOR_PORT,
            database=os.getenv('FALKORDB_DATABASE', 'graphiti'),
        ),
        # Without this, Graphiti defaults to OpenAI and fails on a missing OPENAI_API_KEY
        llm_client=GroqClient(
            config=LLMConfig(
                api_key=os.environ['GROQ_API_KEY'],
                model=os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b'),
            )
        ),
    )

    try:
        await graphiti.driver.health_check()
        print(f'Connected to FalkorDB at {FALKOR_HOST}:{FALKOR_PORT}')
    finally:
        await graphiti.close()


if __name__ == '__main__':
    asyncio.run(main())

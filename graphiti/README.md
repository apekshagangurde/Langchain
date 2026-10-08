# Graphiti on Vercel

Official `zepai/graphiti` server wrapped for Vercel, pointing at Neo4j Aura.

Entrypoint (verified from the current image): `graph_service.main:app` in `/app`.

## Env vars (read by `graph_service/config.py`)

| Var | Value |
|---|---|
| `NEO4J_URI` | `neo4j+s://xxxxx.databases.neo4j.io` |
| `NEO4J_USER` | `neo4j` |
| `NEO4J_PASSWORD` | Aura password |
| `OPENAI_API_KEY` | required |
| `OPENAI_BASE_URL`, `MODEL_NAME`, `EMBEDDING_MODEL_NAME` | optional |

## Test locally

```bash
docker build -f Dockerfile.vercel -t graphiti-vercel .
docker run --rm -p 8000:8000 --env-file .env graphiti-vercel
curl localhost:8000/healthcheck
```

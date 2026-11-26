"""
TripMate — model setup (provider-agnostic)
==========================================

Pick the model with one string, "provider:model-name", in project1/.env:

    TRIPMATE_MODEL=groq:openai/gpt-oss-120b      # default
    TRIPMATE_MODEL=anthropic:claude-opus-5-5     # switch to Claude

The matching API key must be in .env too (GROQ_API_KEY or ANTHROPIC_API_KEY).
Any provider that `init_chat_model` supports works, as long as its
langchain-<provider> package is installed.
"""

import os

from langchain.chat_models import init_chat_model
from langchain_core.rate_limiters import InMemoryRateLimiter

DEFAULT_MODEL = "groq:openai/gpt-oss-120b"

# Only providers listed here get a rate limiter.
# Groq free tier has a low tokens/minute cap, so we slow requests down.
RATE_LIMITS = {
    "groq": InMemoryRateLimiter(requests_per_second=0.04, check_every_n_seconds=0.5),
}


def get_model(model: str | None = None):
    """Return a chat model for "provider:model-name" (default: TRIPMATE_MODEL env var)."""
    model = model or os.getenv("TRIPMATE_MODEL", DEFAULT_MODEL)
    provider = model.split(":", 1)[0]

    kwargs = {}
    if provider in RATE_LIMITS:
        kwargs["rate_limiter"] = RATE_LIMITS[provider]
    # No temperature: Claude Opus 5.5 rejects it.

    return init_chat_model(model, **kwargs)

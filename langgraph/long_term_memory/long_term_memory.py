# Long-term memory: information that persists ACROSS threads/sessions —
# stored outside any single conversation (e.g. in a database/store) and
# deliberately recalled into the context window when relevant, instead
# of being replayed every time like short-term memory.

# Types of long-term memory:
#
# 1. Semantic memory: facts and knowledge — things the system knows to
#    be true (e.g. "the user prefers Hindi translations", "the user is
#    a backend developer").
# 2. Episodic memory: past experiences/events — specific things that
#    happened before (e.g. a prior conversation, a past example of how
#    a task was handled successfully) that can be recalled as a
#    reference for similar situations.
# 3. Procedural memory: how to do things — rules, instructions, or
#    learned procedures for behavior (e.g. a system prompt, a preferred
#    workflow/style) rather than a fact or a specific past event.

# How long-term memory works:
#
# 1. Creation: decide what's worth remembering from the current
#    conversation/thread (often an LLM call that extracts a fact,
#    event, or preference worth keeping) and shape it into a memory
#    record.
# 2. Storage: write that record into a persistent store outside the
#    thread (e.g. a database or vector store), usually keyed/embedded
#    so it can be found again later — this is what makes it survive
#    past the current session.
# 3. Retrieval: given a new conversation/query, search the store for
#    memories relevant to it (e.g. similarity search, filters by user/
#    namespace) instead of loading everything that was ever stored.
# 4. Ingestion: inject the retrieved memories back into the prompt/
#    context window for the current call, so the model actually uses
#    them when generating its response.

# Challenges:
#
# 1. Deciding what's worth remembering: there's no clean rule for which
#    parts of a conversation deserve to become a memory — save too much
#    and the store fills up with noise/trivia that hurts retrieval
#    quality; save too little and genuinely useful facts/preferences
#    never get captured. Usually left to an LLM judgment call, which
#    means it can be inconsistent across conversations.
# 2. Retrieving the right info at the right time: even with good
#    memories stored, pulling back the ones actually relevant to the
#    current conversation (and not irrelevant/stale ones) at the moment
#    they're needed is hard — poor retrieval means the right memory
#    exists but never makes it into context when it matters.
# 3. Orchestrating the entire system: creation, storage, retrieval, and
#    ingestion all have to work together as one pipeline — deciding
#    when each step runs (e.g. write memories mid-conversation vs. after
#    it ends, retrieve before every call vs. only when needed) adds
#    real system complexity on top of getting each step right in
#    isolation.

# LangMem — https://langchain-ai.github.io/langmem/
# LangChain's SDK that implements this creation/storage/retrieval/
# ingestion pipeline for you: a storage-agnostic memory API, built-in
# agent tools to save/search memories during a live conversation, and
# native integration with LangGraph's long-term memory store — instead
# of hand-rolling all four stages above yourself.

# Mem0 — https://docs.mem0.ai/
# A universal, framework-agnostic memory layer for AI agents/apps —
# handles the same creation/storage/retrieval pipeline as a hosted or
# self-hosted service (SDK + API), so agents built on any stack
# (LangChain, AutoGen, LlamaIndex, etc.) get persistent memory across
# sessions without being tied to LangGraph specifically.

# Supermemory — https://supermemory.ai/docs/intro
# A memory/context API for agents that goes beyond simple recall —
# provides building blocks like Memory, Retrieval, Profiles, Connectors,
# and Extractors, aiming to cover both short-term and long-term memory
# infrastructure through one REST API.

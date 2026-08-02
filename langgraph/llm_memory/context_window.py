# Context window: the maximum number of tokens (input + output combined)
# an LLM can "see" and reason over in a single call — anything beyond
# that limit gets truncated or must be dropped/summarized before the
# next call, which is exactly the problem memory strategies solve for.

# In-context learning: an LLM picking up a task/pattern just from
# examples or instructions given in the prompt itself (within its
# context window), with no retraining or fine-tuning — the model
# "learns" only for the duration of that single call.

# Short-term memory: the running conversation history (messages so far
# in the current thread/session) that gets passed back into the
# context window on every call, so the model stays consistent with
# what was just said — lost once the session/thread ends unless it's
# persisted (e.g. via a checkpointer) or summarized into long-term memory.

# Problems with short-term memory:
#
# 1. Fragile: it lives only in memory/process state for that thread —
#    a restart, crash, or missing checkpointer wipes it out, and
#    nothing about the conversation survives unless it was explicitly
#    persisted.
# 2. Context window limit: the full message history is replayed into
#    the model on every call, so a long-running conversation eventually
#    exceeds the context window — older messages must be truncated or
#    summarized, and whatever gets dropped is lost to the model.
# 3. Thread-scoped: short-term memory is tied to a single thread/session
#    (e.g. one thread_id) — nothing carries over to a different thread,
#    so the model has no memory of the user across separate
#    conversations unless that's promoted to long-term memory.

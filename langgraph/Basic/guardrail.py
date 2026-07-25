"""
========================================================
                Guardrails — Quick Guide
========================================================

------------------------------------------------------------
 DEFINITION
------------------------------------------------------------

Guardrail:
  A safety check that sits around an LLM or agent to control
  what goes IN (user input) and what comes OUT (model output).
  It does NOT change how the model thinks — it just blocks,
  filters, or corrects anything that breaks the rules you set.

  Think of it like a bumper lane in bowling — the AI can still
  move freely, but it can't go completely off track.

  Example: A user tries to ask the AI how to build a weapon →
           the guardrail detects this and blocks the request
           before it ever reaches the model.

------------------------------------------------------------
 WHY GUARDRAILS ARE NEEDED
------------------------------------------------------------

- LLMs can be tricked (prompt injection, jailbreaks) into
  saying or doing things they shouldn't.

- Agentic AI can take real actions (call APIs, run code,
  spend money, send emails) — a mistake here is much more
  costly than a bad text answer.

- Businesses need outputs to stay on-topic, safe, accurate,
  and compliant with policy/legal requirements.

- Without guardrails, one bad input or one hallucinated
  output can cascade into a bigger failure in a multi-step
  agent loop.

------------------------------------------------------------
 TYPES OF GUARDRAILS
------------------------------------------------------------

1. Input Guardrails (before the LLM sees it)
   - Blocks harmful, off-topic, or malicious user prompts.
   - Catches prompt injection / jailbreak attempts.
   - Example: Rejecting requests unrelated to the product's purpose.

2. Output Guardrails (before the user sees it)
   - Checks the model's response before it is returned.
   - Filters toxic language, PII leaks, or policy violations.
   - Example: Redacting a phone number the model accidentally revealed.

3. Tool / Action Guardrails (before the agent acts)
   - Validates that a tool call is safe and intended.
   - Example: Requiring human approval before an agent sends
     a real email or deletes a database record.

4. Structural / Format Guardrails
   - Forces output into a required shape (JSON schema, word
     limit, specific format) so downstream systems don't break.

5. Topical / Relevance Guardrails
   - Keeps the conversation focused on the intended domain.
   - Example: A banking assistant refusing to give medical advice.

------------------------------------------------------------
 HOW GUARDRAILS WORK (CONCEPTUALLY)
------------------------------------------------------------

  User Input → [ INPUT GUARDRAIL ] → LLM / Agent
                                        |
                                        v
                              [ TOOL GUARDRAIL ] (if using tools)
                                        |
                                        v
  Final Answer ← [ OUTPUT GUARDRAIL ] ← LLM Response

  At each checkpoint, the guardrail can:
  - ALLOW   → pass through unchanged.
  - BLOCK   → stop it completely and return a safe fallback.
  - MODIFY  → clean/redact/rewrite before passing it on.

------------------------------------------------------------
 GUARDRAILS IN LANGGRAPH
------------------------------------------------------------

  In LangGraph, a guardrail is usually just another NODE in
  the graph — placed before or after the LLM node.

  - It can inspect state and decide whether to route the
    flow forward, back to the user, or to an END/error node.
  - Conditional edges are what make this possible: the
    guardrail node's output decides which node runs next
    (e.g. "safe" → continue, "unsafe" → stop / ask again).
  - Because LangGraph tracks state explicitly, the guardrail
    can also look at the full conversation/action history —
    not just the latest message — before making a decision.

========================================================
"""

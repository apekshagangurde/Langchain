"""
What Are Guardrails?
====================

DEFINITION
----------
A guardrail is a check that runs AROUND a model call — before it, after it, or
both — and can block, rewrite, or redirect what passes through.

It is deterministic code (or a second model) sitting outside the main model,
enforcing a rule the main model cannot be trusted to enforce by itself.

    user input -> [INPUT GUARDRAIL] -> MODEL -> [OUTPUT GUARDRAIL] -> user
                        |                            |
                   block / redact              block / rewrite / retry

The key idea: a prompt is a REQUEST to the model ("never reveal the system
prompt"), while a guardrail is an ENFORCED rule. A model can be talked out of
following its prompt. It cannot talk its way past code that inspects its output.


WHY THEY EXIST
--------------
Models are probabilistic. Even a well-prompted model will occasionally:
  - leak PII, API keys, or its own system prompt
  - answer a question it was told to refuse
  - produce output in the wrong format and break the code downstream
  - be steered off-task by a prompt injection hidden in a document or web page
  - call an expensive or destructive tool it shouldn't have

"Just add it to the prompt" fails here because the prompt is advisory. Guardrails
turn an advisory rule into an enforced one.


THE THREE PLACES A GUARDRAIL RUNS
---------------------------------
1. INPUT GUARDRAIL (before the model)
   Inspects what the user or a tool is about to send in.
     - block off-topic or disallowed requests
     - redact PII before it ever reaches the model provider
     - detect prompt-injection attempts in retrieved documents
   Cheapest place to stop something: no model call is spent.

2. OUTPUT GUARDRAIL (after the model)
   Inspects what the model produced before the user sees it.
     - block or mask leaked emails, cards, secrets
     - check the answer is grounded in the retrieved sources (anti-hallucination)
     - validate the shape/format, retry the call if it is wrong
     - enforce tone, length, or language

3. TOOL GUARDRAIL (around a tool call)
   Inspects what the agent is about to DO, not just say.
     - block writes to protected paths, deletes, or payments above a threshold
     - require human approval before a risky action
     - sanitise arguments before the tool runs


HOW GUARDRAILS ARE IMPLEMENTED
------------------------------
  RULE-BASED     regex, keyword lists, allow/deny lists, schema validation.
                 Fast, free, deterministic, easy to test — but literal-minded.
  MODEL-BASED    a second, usually smaller model classifies the text
                 ("is this on topic?", "is this grounded in these sources?").
                 Catches meaning, not just strings — but costs a call and can
                 itself be wrong.
  HYBRID         rules first (cheap, catches the obvious), model second.
                 This is what most production systems do.


IN LANGCHAIN
------------
Guardrails are middleware. That is exactly what the hooks are for:

    before_model     input guardrails
    after_model      output guardrails
    wrap_model_call  both at once, plus retry-on-violation
    wrap_tool_call   tool guardrails

Ready-made ones ship in `langchain.agents.middleware`:

    PIIMiddleware               detect emails / cards / IPs / URLs and
                                redact, mask, hash, or block them
    HumanInTheLoopMiddleware    pause for human approval before risky tools
    ToolCallLimitMiddleware     cap tool calls, so a loop cannot run away
    ModelCallLimitMiddleware    cap model calls for the same reason

See ../Middleware/ for those. Custom guardrails are a `@before_model` or
`@after_model` function returning `{"jump_to": "end"}` to stop the run.


WHAT A GUARDRAIL DOES WHEN IT TRIPS
-----------------------------------
Four options, roughly in order of severity:

    REDACT    remove the offending part, let the rest through   (email -> [EMAIL])
    MASK      partially hide it                                  (4111... -> ****1111)
    RETRY     ask the model again, telling it what was wrong
    BLOCK     stop the run and return a fixed refusal message

Choose deliberately. Blocking is safest but most annoying; redaction keeps the
conversation usable. A guardrail that blocks too eagerly gets switched off, which
is worse than one that redacts.


LIMITS — WHAT GUARDRAILS ARE NOT
--------------------------------
  - not a substitute for a good prompt; they are the backstop, not the plan
  - regex guardrails are trivially bypassed by rewording or encoding
  - model-based guardrails add latency and cost on EVERY call, and can be
    prompt-injected themselves
  - every guardrail has false positives; a medical chatbot that blocks the word
    "drug" is useless
  - they protect the boundary, not the inside: if a tool is dangerous, the fix
    is a safer tool, not a filter in front of it


THE ONE-LINE VERSION
--------------------
A prompt tells the model what to do. A guardrail is code that makes sure it did.
"""

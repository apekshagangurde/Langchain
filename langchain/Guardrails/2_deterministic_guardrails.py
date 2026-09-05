"""
Deterministic (Rule-Based) Guardrails
=====================================
Theory only — no code in this file.


DEFINITION
----------
A deterministic guardrail is a check written as plain code: regular expressions,
keyword lists, allow/deny lists, length limits, schema validation. No model is
involved in the decision.

Because it is ordinary code, the same input always produces the same verdict.
That is the whole point of the word "deterministic": you can unit-test it, you
can explain exactly why it fired, and it behaves identically today and next month.


HOW IT DECIDES
--------------
It matches STRINGS AND STRUCTURE, never meaning. Typical forms:

  DENY LIST        block if the text contains any banned term
  ALLOW LIST       block unless the text matches something permitted
  PATTERN MATCH    regex for emails, cards, API keys, phone numbers, URLs
  SCHEMA CHECK     reject output that is not valid JSON / fails a Pydantic model
  NUMERIC LIMIT    refund above 10,000; more than 5 tool calls; message over 4k chars
  PATH / SCOPE     block file writes outside an allowed directory


STRENGTHS
---------
  FREE           no model call, so no token cost
  INSTANT        microseconds, versus a second or more for a judge model
  TESTABLE       write a table of inputs and expected verdicts; it stays true
  AUDITABLE      "it fired because it matched this pattern" — a real answer for
                 a compliance reviewer, which "the judge model felt uneasy" is not
  UNBREAKABLE    a regex cannot be prompt-injected. No wording of a user message
                 will convince `re.search` to change its mind. This is the single
                 biggest advantage over model-based guardrails.


WEAKNESSES
----------
  LITERAL-MINDED     it matches the words you listed and nothing else
  FALSE NEGATIVES    "medical advice" is blocked; "my head hurts, what should I
                     take?" sails straight through. Every deny list is a list of
                     the phrasings you happened to think of
  FALSE POSITIVES    blocking the word "drug" breaks a pharmacy chatbot; blocking
                     "kill" breaks "kill the background process"
  TRIVIALLY EVADED   spacing, unicode look-alikes, base64, another language, or
                     simply asking the same thing a different way
  MAINTENANCE        the list grows forever, and nobody dares delete an entry


WHERE EACH KIND RUNS
--------------------
  INPUT (before the model)
      redact API keys and PII before the text leaves your machine
      block obviously out-of-scope requests without paying for a model call
      cap input length so one huge paste cannot blow the context window

  OUTPUT (after the model)
      mask card numbers and emails the model produced
      validate the format before downstream code parses it
      catch a leaked internal string (a code name, an internal URL) by exact match

  TOOL (around a tool call)
      block writes outside an allowed directory
      block deletes entirely
      cap a refund or transfer amount
      these are the highest-value deterministic guardrails, because the damage a
      tool does is real, and the rule is usually genuinely simple


THE FOUR RESPONSES WHEN A RULE TRIPS
------------------------------------
  REDACT   replace the match, let the rest through   sk-abc123 -> [REDACTED]
  MASK     partially hide it                          4111...1111 -> ****1111
  RETRY    call the model again saying what was wrong (mostly for schema failures)
  BLOCK    stop and return a fixed message

Deterministic guardrails suit REDACT and MASK especially well, because the rule
knows exactly which characters are the problem. A model-based guardrail can only
say "this reply is bad", not "characters 40-56 are the bad part".


IN LANGCHAIN
------------
They are middleware hooks:

  before_model      the input guardrail
  after_model       the output guardrail
  wrap_tool_call    the tool guardrail

Ready-made deterministic guardrails ship in `langchain.agents.middleware`:

  PIIMiddleware              regex detectors for email, credit_card, ip,
                             mac_address and url, with redact / mask / hash /
                             block strategies
  ToolCallLimitMiddleware    a hard numeric cap on tool calls
  ModelCallLimitMiddleware   a hard numeric cap on model calls

The limit middlewares are pure deterministic guardrails, and they are the ones
most often missing from a broken agent: without them, one bad loop runs until
the bill or the context window stops it.


WHEN TO REACH FOR A DETERMINISTIC GUARDRAIL
-------------------------------------------
Use one when ALL of these are true:
  - the rule can be stated exactly ("no card numbers in the output")
  - a false positive is cheap (a redaction, not a refusal)
  - the check runs on every request, so cost and latency matter
  - you need to prove to somebody why it fired

Reach for a model-based guardrail instead (file 3) when the rule is about
INTENT — "is the user asking for medical advice", "is this answer supported by
the sources" — because no list of strings expresses that.


THE ONE-LINE VERSION
--------------------
A deterministic guardrail is cheap, certain, and unbypassable — about exactly the
strings you thought to list, and nothing else.
"""

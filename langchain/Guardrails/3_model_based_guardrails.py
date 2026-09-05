"""
Model-Based Guardrails (LLM-as-Judge)
=====================================
Theory only — no code in this file.


DEFINITION
----------
A model-based guardrail asks a SECOND model to judge the text before it goes in,
or after it comes out. That judge model is given a policy and returns a verdict.

It is called LLM-as-judge: one model produces, another evaluates.


THE DIFFERENCE FROM A DETERMINISTIC GUARDRAIL
---------------------------------------------
A deterministic guardrail asks a question about STRINGS.
A model-based guardrail asks a question about MEANING.

    deterministic     "does this text contain the phrase 'medical advice'?"
    model-based       "is this person asking for medical advice?"

The second question catches "my head has been pounding all morning, what should
I take?" — which contains none of the banned words and would pass every keyword
list you could write. That gap is the entire reason model-based guardrails exist.

It cuts the other way too: a deny list containing "drug" blocks "what drug
interactions should the pharmacist check?" A judge understands that is a
legitimate pharmacy question and lets it through. Fewer false positives, not just
fewer false negatives.


HOW ONE IS BUILT
----------------
1. WRITE A POLICY, not a word list. State what is allowed, what is blocked, and
   what to do in ambiguous cases. The policy is a prompt, so it can be as
   nuanced as prose allows.

2. DEMAND STRUCTURED OUTPUT. The judge must return a typed object — a boolean
   verdict plus a short reason — not free text. Parsing "I think this is
   probably fine..." with string matching reintroduces every fragility you
   adopted the judge to avoid.

3. USE A SMALL, FAST MODEL. Judging is a far easier task than answering.
   The judge runs on EVERY request, so its latency and cost are paid every
   single time; a small model keeps that bearable.

4. RUN IT AT THE RIGHT POINT. Same three positions as any guardrail — before the
   model, after it, or around a tool call.


WHAT A JUDGE CAN CHECK THAT CODE CANNOT
---------------------------------------
  INTENT             is the user actually asking for something off-limits,
                     however they phrased it
  TOPICALITY         is this within the assistant's remit at all
  PROMPT INJECTION   is this text trying to override the system instructions,
                     including injections hidden inside a retrieved document
  GROUNDEDNESS       is every claim in the answer supported by the sources that
                     were retrieved — the standard anti-hallucination check
                     for RAG, and impossible to express as a regex
  TONE AND SAFETY    is this reply rude, alarming, or overconfident
  COMPLETENESS       did the answer actually address the question asked


STRENGTHS
---------
  UNDERSTANDS PARAPHRASE   one policy replaces a hundred regexes and still
                           catches wordings nobody anticipated
  CONTEXT-AWARE            judges the sentence in context, not the word alone,
                           so far fewer false positives on innocent text
  EASY TO EVOLVE           tightening the policy is an edit to a prompt, not a
                           new pattern bolted onto a growing list
  HANDLES OPEN QUESTIONS   groundedness and completeness have no rule-based form


WEAKNESSES
----------
  COSTS A CALL          on every request; an input judge plus an output judge
                        means three model calls where you used to make one
  ADDS LATENCY          the user waits for the judge before seeing anything
  PROBABILISTIC         the guardrail can be wrong, and its mistakes are not
                        reproducible the way a regex's are
  ITSELF INJECTABLE     the judge reads attacker-influenced text, so a message
                        can try to talk the JUDGE into approving it. Keep the
                        policy in the system prompt, clearly separate the text
                        being judged, and never let the judged text look like
                        instructions to the judge
  HARDER TO AUDIT       "the judge said no" satisfies no compliance reviewer
  NEEDS ITS OWN TESTS   a guardrail whose accuracy you have not measured is a
                        guess; build a small labelled set and score it


THE HYBRID PATTERN — WHAT PRODUCTION ACTUALLY DOES
--------------------------------------------------
Neither kind wins outright. They are layered, cheapest first:

    1. deterministic checks   free, instant, catch the obvious and the literal
    2. model-based judge      only on what survives layer 1
    3. human approval         only for genuinely risky actions

Layer 1 filters most traffic for nothing, so you pay for layer 2 rarely. Layer 2
catches what layer 1 is blind to. Layer 3 exists because neither layer is
trustworthy enough for an irreversible action — which is what
`HumanInTheLoopMiddleware` is for.

The layering also matters for a subtler reason: a deterministic check cannot be
argued with, so it makes a good OUTER shell around a judge that can be.


CHOOSING BETWEEN THEM
---------------------
  Can the rule be stated as an exact pattern?           -> deterministic
  Is a false positive cheap (redact, not refuse)?       -> deterministic
  Does the rule depend on intent or meaning?            -> model-based
  Must the check justify itself to an auditor?          -> deterministic
  Does the answer need checking against sources?        -> model-based
  Is the action irreversible?                           -> human approval

A useful default: deterministic guardrails on the way IN (cheap, protective),
a judge on the way OUT (where meaning matters most), and human approval on any
tool that spends money or destroys data.


THE ONE-LINE VERSION
--------------------
A model-based guardrail understands what a deterministic one can only match —
and you pay for that understanding on every single request.
"""

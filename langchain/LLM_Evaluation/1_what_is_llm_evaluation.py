"""
What Is LLM Evaluation?
=======================
Theory only — no code in this file.


DEFINITION
----------
LLM evaluation is measuring whether your LLM application produces good output —
systematically, on a fixed set of examples, in a way that gives you a number you
can compare across versions.

The emphasis is on "compare across versions". The point of an eval is not to
learn that your app is 84% correct. It is to know whether the prompt you just
changed made it better or worse.


WHY IT IS HARD
--------------
Traditional software has one correct output per input, so a test is `==`.
LLM output has MANY acceptable outputs and no exact match to compare against:

    "Mumbai is bigger than Pune."
    "Pune has 7.4M people; Mumbai has 21.7M, so Mumbai is larger."
    "Mumbai."

All three are correct. None are string-equal. So evaluation cannot be assertion —
it has to be measurement, and measurement of something fuzzy.

Three more properties make it harder:
  NON-DETERMINISM   the same input gives different output run to run, so a
                    single passing run proves very little
  NO GROUND TRUTH   for summarisation, writing, or advice there often IS no
                    single right answer to compare against
  SILENT REGRESSION a prompt tweak that fixes one case quietly breaks four
                    others, and nothing crashes to tell you


THE ANATOMY OF AN EVAL
----------------------
Every evaluation, however simple, has four parts:

  1. DATASET      the examples you run against. Inputs, and — if you have them —
                  reference outputs. This is the part that decides whether your
                  eval is worth anything.
  2. APPLICATION  the thing under test: a prompt, a chain, an agent. Whatever
                  you will later change and want to re-measure.
  3. EVALUATOR    the function that scores one output. Rule-based, model-based,
                  or human.
  4. AGGREGATION  turning per-example scores into one number you can track,
                  plus the ability to look at which examples failed.

Change one of these and the numbers stop being comparable, so version them all.


THE THREE KINDS OF EVALUATOR
----------------------------
RULE-BASED (deterministic)
    exact match, contains, regex, JSON-schema validity, length, latency, cost.
    Free, instant, perfectly reproducible. Only works when correctness has a
    crisp form — classification labels, extracted fields, structured output.

MODEL-BASED (LLM-as-judge)
    a second model scores the output against a rubric. Handles open-ended text
    where no rule can. Costs a call per example and is itself fallible.
    Covered in file 2.

HUMAN
    the ground truth all others are approximations of. Slow and expensive, so
    it is used to build the dataset, to calibrate the judge, and to audit
    disagreements — not to run every time.

Real practice is layered: rules for what they can catch, a judge for the rest,
humans to check the judge is honest.


REFERENCE-BASED VS REFERENCE-FREE
---------------------------------
REFERENCE-BASED   you have an expected answer, and score the output against it.
                  Stronger signal, but somebody must write every reference.

REFERENCE-FREE    you score the output against a rubric alone — "is this
                  grounded in the sources", "is this a helpful answer". No
                  reference needed, so it scales to any input, but the score is
                  softer and more subjective.

RAG evaluation leans reference-free because the retrieved documents ARE the
reference: groundedness asks whether every claim traces back to them.


OFFLINE VS ONLINE
-----------------
OFFLINE   run against a fixed dataset, before you ship. This is the regression
          test: same examples, same evaluator, compare to last run. It answers
          "did my change break anything".

ONLINE    run against real production traffic, after you ship. Sampled, since
          judging everything is expensive. It answers "is it actually working
          for real users" — and surfaces the inputs you never thought to put
          in your dataset.

You need both. Offline catches regressions in what you anticipated; online tells
you what you failed to anticipate, which then becomes new offline examples.


WHAT TO MEASURE
---------------
Pick metrics that match what failure actually looks like for YOUR app:

  CORRECTNESS       is the answer factually right (needs a reference)
  GROUNDEDNESS      is every claim supported by the retrieved context — the
                    standard hallucination metric for RAG
  RELEVANCE         does it answer the question that was asked
  COMPLETENESS      did it cover everything the question required
  FORMAT            valid JSON, required fields, correct schema
  SAFETY / TONE     policy compliance, no leaks, appropriate register
  COST AND LATENCY  tokens and seconds per request — real constraints, and the
                    easiest metrics to collect, so there is no excuse not to

Two or three metrics tracked honestly beat ten tracked carelessly.


BUILDING THE DATASET — THE PART THAT ACTUALLY MATTERS
-----------------------------------------------------
A mediocre evaluator on a good dataset beats a brilliant evaluator on a bad one.

  - 20 well-chosen examples are worth more than 500 generated ones
  - include the failures you have actually seen in production; every bug you fix
    should leave an example behind
  - include the edge cases: empty input, hostile input, ambiguous questions,
    questions the app SHOULD refuse
  - keep the distribution honest — if 30% of real traffic is one question type,
    do not build a dataset that is 3% that type
  - never let the dataset leak into the prompt; an app tuned on its own eval set
    scores well and generalises badly


READING THE RESULTS
-------------------
  - a single number hides everything; always look at the failing examples
  - because output is non-deterministic, small score changes are noise — decide
    up front how big a difference counts as real
  - a metric that never moves is not measuring anything; drop it
  - when the score is high and users still complain, the dataset is wrong, not
    the users


THE ONE-LINE VERSION
--------------------
Evaluation replaces "it seems better" with a number, measured on examples you
chose in advance — so you can tell improvement from coincidence.
"""

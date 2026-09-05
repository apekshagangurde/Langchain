"""
LLM-as-Judge
============
Theory only — no code in this file. File 3 is the runnable version.


DEFINITION
----------
LLM-as-judge is using a second model to score the output of the first, against a
written rubric.

It exists because most useful LLM output cannot be checked with `==`. A summary,
an explanation, an answer phrased three different ways — none of these can be
string-matched against a reference, but a model can read both and say whether
they agree.

The same technique appears in two roles, and it helps to keep them distinct:
    as a GUARDRAIL   judges live traffic and blocks it        (Guardrails/file 3)
    as an EVALUATOR  judges a fixed dataset and scores it     (this file)
Same mechanism, different purpose: one gates, the other measures.


THE THREE FORMS
---------------
1. REFERENCE-BASED SCORING
   Judge sees: question, expected answer, actual answer.
   Asks: does the actual answer agree with the expected one?
   The strongest signal, because the judge has something concrete to compare
   against and cannot simply be charmed by fluent prose. Needs a reference for
   every example.

2. REFERENCE-FREE SCORING (rubric only)
   Judge sees: question, actual answer, (optionally the retrieved context).
   Asks: is this grounded / relevant / complete / safe?
   Scales to any input because nobody has to write references. Softer signal,
   and more prone to rewarding confident-sounding answers.

3. PAIRWISE COMPARISON
   Judge sees: question, answer A, answer B.
   Asks: which is better?
   Far more reliable than absolute scoring, because "is B better than A" is an
   easier judgement than "is this a 4 or a 5". This is the right form when
   comparing two prompt versions — which is the most common thing you actually
   want to know.


DESIGNING THE RUBRIC
--------------------
The rubric is the eval. A vague rubric produces vague numbers that drift between
runs and mean nothing.

  DEFINE EVERY POINT ON THE SCALE
      Not "rate 1-5". Say what a 1 is, what a 3 is, what a 5 is, in concrete
      terms. Otherwise the judge invents its own scale, differently each time.

  PREFER SMALL SCALES
      Binary (pass/fail) or 1-3 is far more stable than 1-10. Judges cannot
      reliably distinguish a 7 from an 8, and the extra resolution is noise
      that looks like signal.

  ONE CRITERION PER JUDGE CALL
      Ask for correctness OR groundedness OR tone — not all three at once.
      A judge asked for a combined score silently weights the criteria itself,
      and you cannot tell which one moved when the number changes.

  DEMAND STRUCTURED OUTPUT
      A typed object — score plus a one-line reason — never free text. The
      reason matters: it is what lets you audit a suspicious score, and it is
      the first thing to read when the eval disagrees with your intuition.

  ASK FOR THE REASON BEFORE THE SCORE
      Having the judge state its reasoning first, then commit to a score,
      produces more consistent results than the reverse. Field order in the
      schema is enough to enforce this.


KNOWN BIASES — WHAT JUDGES GET WRONG
------------------------------------
A judge is a model, so it fails like one. The documented, reproducible biases:

  POSITION BIAS      in pairwise comparison it favours whichever answer came
                     first. Mitigation: run both orderings and average, or
                     count a result only when both orderings agree.
  VERBOSITY BIAS     longer answers score higher, regardless of quality.
                     Mitigation: say so explicitly in the rubric; watch whether
                     score correlates with length.
  SELF-PREFERENCE    a model rates its own family's output higher. Mitigation:
                     judge with a different model family than you generate with,
                     where you can.
  LENIENCY           absolute scores drift upward; almost everything is a 4.
                     Mitigation: smaller scales, sharper rubrics, pairwise.
  FORMATTING         markdown, headers, and bullet points read as "thorough".

None of these disqualify the technique. They mean the judge must itself be
validated before you trust its numbers.


VALIDATING THE JUDGE
--------------------
An unvalidated judge is a random number generator with a plausible manner.

  1. Hand-label 20-30 examples yourself. This is the ground truth.
  2. Run the judge on the same examples.
  3. Measure agreement with your labels.
  4. If agreement is poor, fix the RUBRIC — that is almost always the problem,
     not the model.
  5. Re-check periodically, and whenever you change the judge model.

Agreement roughly in line with how often two humans agree is the realistic
target. Perfect agreement usually means the task was trivial.


CHOOSING THE JUDGE MODEL
------------------------
  - judging is easier than generating, so a smaller model is often enough,
    and it runs on every example in the dataset
  - keep the judge FIXED while you iterate on the app; changing the ruler and
    the thing being measured at the same time makes the numbers meaningless
  - when you do change the judge, re-run the whole dataset so old and new
    numbers are never compared directly
  - temperature 0 for reproducibility


WHEN NOT TO USE A JUDGE
-----------------------
Reach for something cheaper if it will do:
  - exact match / regex, for classification labels and extracted fields
  - schema validation, for structured output
  - retrieval metrics computed from ids, for whether the right doc was fetched
  - latency and cost, which are simply measured

Every one of those is free, instant and exactly reproducible. Spend the judge on
what genuinely needs reading.


THE ONE-LINE VERSION
--------------------
A judge model turns unscoreable text into a number — reliable only to the extent
that its rubric is sharp and its agreement with humans has been measured.
"""

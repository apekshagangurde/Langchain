"""
Running an Evaluation — Working Code
===================================
A complete, minimal eval harness. The four parts from file 1, in order:

    DATASET      -> examples with reference answers
    APPLICATION  -> the prompt under test
    EVALUATORS   -> one rule-based, one LLM-as-judge
    AGGREGATION  -> per-example scores plus one number to track

Run it, change PROMPT_UNDER_TEST, run it again, compare the numbers. That loop
is the entire point of evaluation.
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

load_dotenv()


# ===========================================================================
# 1. DATASET
# Small and hand-written beats large and generated. Note the last two: an
# edge case and a question the app should refuse. A dataset of only easy
# questions reports a great score and tells you nothing.
# ===========================================================================
DATASET = [
    {
        "question": "What is the capital of Maharashtra?",
        "reference": "Mumbai",
    },
    {
        "question": "Which is larger by population, Pune or Mumbai?",
        "reference": "Mumbai, which has about 21.7 million people to Pune's 7.4 million.",
    },
    {
        "question": "In one word, what river runs through Pune?",
        "reference": "Mula-Mutha",
    },
    {
        "question": "What will the Sensex close at next Friday?",
        "reference": "It is not possible to know; this cannot be predicted.",
    },
]


# ===========================================================================
# 2. THE APPLICATION UNDER TEST
# This is the thing you will change between runs. Keep everything else fixed
# so the score difference is attributable to this.
# ===========================================================================
PROMPT_UNDER_TEST = "Answer the question in one short sentence. If it cannot be known, say so."

app_model = ChatGroq(model="openai/gpt-oss-20b", temperature=0)


def run_app(question: str) -> str:
    """The application: one prompt, one model call."""
    reply = app_model.invoke(
        [
            {"role": "system", "content": PROMPT_UNDER_TEST},
            {"role": "user", "content": question},
        ]
    )
    return reply.text.strip()


# ===========================================================================
# 3a. EVALUATOR — RULE-BASED
# Free, instant, perfectly reproducible. Use it wherever correctness has a
# crisp form. Here: did the reference keyword survive into the answer.
# ===========================================================================
def evaluate_contains(output: str, reference: str) -> bool:
    """True if the answer contains the key term from the reference."""
    key = reference.split(",")[0].split(";")[0].strip()
    return key.lower() in output.lower()


# ===========================================================================
# 3b. EVALUATOR — LLM-AS-JUDGE (reference-based)
# For everything a rule cannot check. Note the rubric design from file 2:
#   - every point on the scale is defined, not just "rate 1-3"
#   - a SMALL scale, because judges cannot reliably tell a 7 from an 8
#   - ONE criterion only (correctness), so a moving score has one cause
#   - reason BEFORE score in the schema, so it reasons then commits
# ===========================================================================
class Judgement(BaseModel):
    """A judge's verdict on one answer."""

    reason: str = Field(description="One short sentence justifying the score")
    score: int = Field(description="1, 2 or 3 — how well the answer matches the reference")


JUDGE_RUBRIC = """You are grading a question-answering system against a reference answer.

Score ONLY factual agreement with the reference. Ignore wording, length and style.

3 = fully agrees with the reference
2 = partly right, or right but missing something the reference states
1 = contradicts the reference, or fails to answer

Give your reason first, then the score."""

# Temperature 0 and a fixed model: the ruler must not move while you measure.
judge_model = ChatGroq(model="openai/gpt-oss-20b", temperature=0).with_structured_output(
    Judgement, method="function_calling"
)


def evaluate_with_judge(question: str, reference: str, output: str) -> Judgement:
    return judge_model.invoke(
        [
            {"role": "system", "content": JUDGE_RUBRIC},
            {
                "role": "user",
                "content": (
                    f"Question: {question}\n"
                    f"Reference answer: {reference}\n"
                    f"System answer: {output}"
                ),
            },
        ]
    )


# ===========================================================================
# 4. THE EVAL LOOP + AGGREGATION
# ===========================================================================
print(f"prompt under test: {PROMPT_UNDER_TEST!r}\n")

rows = []
for example in DATASET:
    answer = run_app(example["question"])
    passed = evaluate_contains(answer, example["reference"])
    verdict = evaluate_with_judge(example["question"], example["reference"], answer)

    rows.append({"passed": passed, "score": verdict.score})

    print(f"Q: {example['question']}")
    print(f"   answer   : {answer}")
    print(f"   contains : {'PASS' if passed else 'FAIL'}")
    print(f"   judge    : {verdict.score}/3 — {verdict.reason}\n")


# One number to track across runs, and the failures to actually read.
n = len(rows)
contains_rate = sum(r["passed"] for r in rows) / n
mean_score = sum(r["score"] for r in rows) / n

print("=" * 60)
print(f"contains pass rate : {contains_rate:.0%}  ({sum(r['passed'] for r in rows)}/{n})")
print(f"mean judge score   : {mean_score:.2f} / 3")
print("=" * 60)
print()
print("Notice the two evaluators disagree on some rows. That is the lesson:")
print("the rule-based check is exact but literal — it fails a correct answer")
print("that used different words. The judge reads meaning but costs a call.")
print("Neither is 'the' score; you track both, and you read the failures.")

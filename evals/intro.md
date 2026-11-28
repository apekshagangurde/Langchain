# Why we need evaluation for LLMs

LLM outputs are non-deterministic, so the same prompt can give a different answer each time. You can't just eyeball one run and call it working.
A small change to a prompt, model, or tool can quietly break behaviour that used to work.
Evals give you a repeatable test set and scores (correctness, tool use, cost, latency), so you can measure quality instead of guessing.
That lets you compare versions, catch regressions before users do, and ship changes with confidence.

## Curriculum

1. LLM Evals
2. LLM Evals Landscape
3. LLM Evaluation and Benchmarks
4. LLM-based Application Evals
5. Evals Pipeline
6. RAG Evals
7. Agent Evals
8. Safety-based Evals
9. Operations Evals

## Software testing vs LLM evaluation

| Aspect | Software testing | LLM evaluation |
|---|---|---|
| Output | Deterministic: same input, same output | Non-deterministic: same input can give different outputs |
| Expected result | One exact correct answer | Many acceptable answers |
| Pass check | Exact match / assert (`==`) | Scoring: similarity, rubric, LLM-as-judge, human review |
| Result | Pass or fail | A score or percentage (e.g. 87% correct) |
| What's tested | Code logic | Prompt + model + tools + data together |
| Breaks when | The code changes | Prompt, model version, tools or data change, sometimes with no code change |
| Runs | Once is enough | Many runs/examples to average out randomness |
| Cost & speed | Cheap and fast | Costs tokens/API calls, slower |

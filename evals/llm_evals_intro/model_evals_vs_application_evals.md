# What are LLM Evals?

LLM evals are tests that measure how well an LLM or LLM app performs.
You run it on a set of example inputs, then score its outputs for things like correctness, relevance, safety, cost and speed.
They show whether a change made your app better or worse.

## LLM evals vs application evals

| Aspect | LLM evals (model evals) | Application evals |
|---|---|---|
| What's tested | The raw model on its own | The whole app: prompt + model + tools + RAG + logic |
| Question asked | "How good is this model in general?" | "Does my app do its job for my users?" |
| Data | Public benchmarks (MMLU, HumanEval, GSM8K) | Your own examples from your use case |
| Metrics | General: accuracy, reasoning, coding scores | Task-specific: right answer, right tool call, groundedness, cost, latency |
| Who runs it | Model builders (OpenAI, Anthropic, Meta) | App developers (you) |
| Used for | Picking or comparing models | Improving and shipping your app safely |
| Example | "Model X scores 88% on MMLU" | "TripMate books the right hotel 92% of the time" |

## What are model evals?

Model evals test the raw LLM on its own, with no app, tools or custom prompts around it.
They use standard benchmarks (like MMLU for knowledge or HumanEval for coding) to score skills such as reasoning, math and coding.
They help you compare models and pick the best one for your app.

### Important capabilities model evals check

- **Knowledge** – general facts and subject knowledge (MMLU)
- **Reasoning** – logical and step-by-step thinking (ARC, HellaSwag)
- **Math** – solving word and math problems (GSM8K, MATH)
- **Coding** – writing correct code (HumanEval, SWE-bench)
- **Instruction following** – doing exactly what the prompt asks (IFEval)
- **Truthfulness** – avoiding made-up answers / hallucinations (TruthfulQA)
- **Safety** – refusing harmful requests, avoiding bias and toxicity
- **Long context** – finding and using info in very long inputs like whole books or codebases, including details buried in the middle (needle-in-a-haystack, RULER, LongBench)
- **Tool use** – calling functions/tools correctly (BFCL)
- **Multimodal understanding** – understanding images, charts, audio and video along with text (MMMU, ChartQA)

### Capability areas and famous benchmarks

| Capability Area | Famous Benchmark(s) | What It Checks |
|---|---|---|
| General Knowledge + Reasoning | MMLU | Broad subject knowledge and reasoning across domains like science, history, law, medicine, and more |
| Maths | GSM8K | Grade-school math word problems and step-by-step numerical reasoning |
| Coding | HumanEval, SWE-bench | Code generation and real-world software engineering issue solving |
| Instruction Following | IFEval | Whether the model follows explicit constraints and formatting instructions |
| Long Context | Needle-in-a-Haystack | Whether the model can find specific information hidden inside a very long context |

## What are application evals?

Application evals test your whole LLM app (prompt + model + tools + RAG + logic) on your own real use case.
You build a set of example inputs from your users' tasks and score whether the app gives the right answer, calls the right tools, stays grounded, and is fast and cheap enough.
They tell you if your app actually works for your users, and catch regressions when you change a prompt, model or tool.

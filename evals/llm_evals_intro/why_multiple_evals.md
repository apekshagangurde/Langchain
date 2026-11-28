# Why we need multiple evals

One eval checks only one thing, but an LLM system has to be good at many things at the same time.
A system can score high on one eval and still fail on another. For example, it can be accurate but too slow or too expensive.
So we create one eval for each success criterion to see the full picture of how the system performs.

## Example: Zomato email router

| Success criterion | Eval / metric |
|---|---|
| Routes email to the correct team | Accuracy |
| Replies only with a valid label (Billing / Technical / General) | Format check |
| Responds fast enough | Latency |
| Stays within budget | Cost per email |

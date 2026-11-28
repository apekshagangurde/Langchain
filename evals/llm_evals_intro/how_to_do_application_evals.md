# How to do application evals

1. **Define success** – decide what "good" means for your app (right answer, right tool call, grounded, polite, fast, cheap).
2. **Build a dataset** – collect 20–50 real example inputs from your users' tasks, with the expected output or behaviour for each. Include tricky and edge cases.
3. **Run the app** – send every example through your full app (prompt + model + tools + RAG) and save the outputs.
4. **Score the outputs** – use the right check for each metric:
   - **Code checks** – exact match, valid JSON, correct tool called
   - **LLM-as-judge** – another LLM grades the answer against a rubric
   - **Human review** – a person checks a sample for quality
5. **Analyse results** – look at the overall score and read the failures to find patterns.
6. **Improve and re-run** – change the prompt, model or tools, run the same evals again, and compare scores.
7. **Automate it** – run evals on every change (CI) and keep adding new failure cases from production to the dataset.

**Tools:** LangSmith, Langfuse, DeepEval, Ragas, promptfoo.

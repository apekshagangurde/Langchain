# Use case: Email routing at Zomato (example)

Zomato gets thousands of customer emails every day. They want to automate this:
an LLM reads each email, decides if it is **Billing**, **Technical** or **General**, and routes it to the right team.

We built it with an LLM and this prompt:

> You are a customer support assistant. Read the email and route it to the correct team.
> Reply with only one word: Billing, Technical, or General.

Now we need **evals** to check it routes emails correctly.

## The system we are evaluating

```
                                        ┌──────────────────┐
                                  ┌───▶ │  💳 Billing team  │
                                  │     └──────────────────┘
 📧 "I was charged    ┌────────┐  │     ┌──────────────────┐
    twice for my  ───▶│  LLM   │──┼───▶ │ 🛠  Technical team │
    order #4521"      │ router │  │     └──────────────────┘
                      └────────┘  │     ┌──────────────────┐
                                  └───▶ │ 💬 General team   │
                                        └──────────────────┘
```

## How the eval works

```
        GOLDEN DATASET                   LLM ROUTER        COMPARE
 ┌────────────────────┬───────────┐               predicted    expected
 │ email              │ expected  │
 ├────────────────────┼───────────┤
 │ "charged twice..." │ Billing   │ ──▶ 🤖 ──▶   Billing   vs Billing    ✅
 │ "app crashes..."   │ Technical │ ──▶ 🤖 ──▶   Technical vs Technical  ✅
 │ "OTP not coming.." │ Technical │ ──▶ 🤖 ──▶   General   vs Technical  ❌
 │ "deliver to Pune?" │ General   │ ──▶ 🤖 ──▶   General   vs General    ✅
 └────────────────────┴───────────┘
                                               Accuracy = 3 / 4 = 75%
```

## Step 1: Define the task and target

- **Task:** classify a customer email into a category
- **Target:** one of `Billing`, `Technical`, `General` → routed to that team

## Step 2: Define success criteria

- **Type of task:** classification
- **Metric:** accuracy = correct predictions / total emails

## Step 3: Build a dataset (golden dataset)

Real email content plus the correct label, checked by a human. This is the **golden dataset**, the "answer key".

| Email content | Expected label |
|---|---|
| "I was charged twice for my order #4521." | Billing |
| "Refund for my cancelled order hasn't arrived yet." | Billing |
| "The app crashes when I open the payment page." | Technical |
| "I can't log in, OTP is not coming." | Technical |
| "Do you deliver to Pune airport?" | General |
| "How do I become a delivery partner?" | General |

## Step 4: Define the evaluation method

For every email in the golden dataset:
1. Send the email to the LLM and get its **predicted** label.
2. Compare it with the **expected** label.
3. Count the matches and calculate **accuracy** with Python code.

Because a script does the comparison, there's no manual checking. This is an **automated eval workflow**.

```python
from langchain_groq import ChatGroq

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

PROMPT = """You are a customer support assistant. Read the email and route it to the correct team.
Reply with only one word: Billing, Technical, or General.

Email: {email}"""

golden_dataset = [
    {"email": "I was charged twice for my order #4521.", "expected": "Billing"},
    {"email": "Refund for my cancelled order hasn't arrived yet.", "expected": "Billing"},
    {"email": "The app crashes when I open the payment page.", "expected": "Technical"},
    {"email": "I can't log in, OTP is not coming.", "expected": "Technical"},
    {"email": "Do you deliver to Pune airport?", "expected": "General"},
    {"email": "How do I become a delivery partner?", "expected": "General"},
]

correct = 0
for row in golden_dataset:
    predicted = llm.invoke(PROMPT.format(email=row["email"])).content.strip()
    is_correct = predicted.lower() == row["expected"].lower()
    correct += is_correct
    print(f"{'✅' if is_correct else '❌'} expected={row['expected']:<10} predicted={predicted}")

accuracy = correct / len(golden_dataset)
print(f"\nAccuracy: {accuracy:.0%}")
```

## Step 5: Run the model

Run the LLM on every email in the golden dataset and save its predicted label.

## Step 6: Evaluate the results

Compare each predicted label with the expected label and calculate accuracy.

## Step 7: Analyse the results

Look at the wrong predictions to understand where and why the model fails.

## Step 8: Improve the system (loop)

Improve the system based on the analysis, then go back to Step 5 and repeat until the results are good.

## Step 9: Deploy the system

Deploy the email router so incoming emails are routed to the correct team automatically.

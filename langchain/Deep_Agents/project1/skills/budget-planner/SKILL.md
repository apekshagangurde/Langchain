---
name: budget-planner
description: How to split a weekend-trip budget into travel / stay / food / activities / buffer and present it as a cost table that says whether it fits. Read this before estimating or checking the cost of any trip.
---

# Budget planner

Goal: an honest cost estimate the traveller can trust — every number labelled,
a clear "fits / over by ₹X", and the cheapest fix if it doesn't fit.

## 1. Inputs

| Input | Default if not given (say you assumed it) |
|---|---|
| Home city → destination | — (must have) |
| Days / nights | 2 days = 1 night |
| People | 1 adult |
| Total budget | — (if missing, estimate a mid-range cost and say "no budget given") |
| Transport | car/cab ≤ 4 h, else bus or train |
| Stay level | mid-range (unless budget is tight) |

Use prices the user or a tool gave first. Only fall back to the typical ranges
below, and mark those as `estimate`.

## 2. Typical mid-range prices (India, per person unless noted)

| Item | Budget | Mid-range | Notes |
|---|---|---|---|
| Bus / train, per 100 km one way | ₹100–200 | ₹200–400 | AC train / Volvo bus = upper end |
| Own car, per 100 km round trip (fuel + tolls) | ₹800–1,200 | — | per **car**, split by people |
| Cab, per 100 km one way | ₹1,500–2,000 | — | per **car** |
| Stay, per room per night | ₹1,000–2,000 | ₹2,500–4,500 | 2 people per room; hill stations cost more on weekends |
| Food, per day | ₹500–800 | ₹900–1,500 | 3 meals + snacks |
| Entry / activities, per day | ₹0–300 | ₹300–1,000 | forts/viewpoints cheap; boating, rides, adventure cost more |

## 3. Split

1. **Travel** = round trip from the home city + local travel at the destination.
2. **Stay** = nights × rooms × room rate (rooms = ceil(people ÷ 2)).
3. **Food** = days × people × daily rate.
4. **Activities** = days × people × daily rate.
5. **Buffer** = 10% of (travel + stay + food + activities).
6. **Total** = sum of all five. Compare with the budget.

Rough healthy split for a 2-day trip: travel 25–35%, stay 30–40%,
food 20–25%, activities 5–15%, buffer 10%. If one line is far above its
share, that's where to cut.

## 4. If it's over budget

Give the ONE cheapest change that fixes it, in this order of preference:
1. cheaper stay (budget hotel / homestay, or share a room)
2. bus or train instead of cab
3. fewer paid activities
4. a closer destination
5. one day instead of two

## 5. Output format

```markdown
## Budget (estimate) — <home city> → <destination>, <N> days, <P> people

| Item | Cost | Source |
|---|---|---|
| Travel | ₹... | user / tool / estimate |
| Stay | ₹... | |
| Food | ₹... | |
| Activities | ₹... | |
| Buffer (10%) | ₹... | |
| **Total** | **₹...** | vs budget ₹... |

**Verdict:** Fits the budget (₹... spare) — or — Over by ₹... → <one cheaper change>
**Assumed:** <anything you defaulted, e.g. "1 person, mid-range hotel, bus">
```

## 6. Self-check

- Do the five lines add up to the total?
- Is every number marked user / tool / estimate?
- Is per-car / per-room cost split correctly across people?
- Did you list every assumption?

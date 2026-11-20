---
name: itinerary-writer
description: How to turn trip research (weather, places, budget, traveller preferences) into a practical, realistic itinerary someone can actually follow. Read this before writing or revising any trip plan or itinerary.
---

# Itinerary writer

Goal: a plan the traveller can follow on the day without re-planning — realistic
timing, sensible routes, honest costs, and a backup for things that can go wrong.

## 1. Check you have the inputs

Before writing, make sure you know these. If something important is missing,
ask the user in ONE short message (max 3 questions) instead of guessing:

| Input | Why it matters | Default if user doesn't care |
|---|---|---|
| Destination + start city | travel time eats into day 1 | — (must ask) |
| Dates / number of days | weather, crowds, opening days | next weekend, 2 days |
| Budget (total, per person?) | hotel class, transport mode | ask |
| Group (solo, couple, family with kids, seniors) | pace, walking, safety | adults, normal pace |
| Interests (nature, food, history, adventure, shopping) | which places to pick | mix |
| Constraints (diet, mobility, no long drives, pets) | hard filters | none |
| Transport (own car, bus, train, cab) | how far places can be | ask if budget is tight |

Also check the user's memory/profile for diet, pace and dislikes before asking.

## 2. Build the plan from facts only

- Use ONLY facts from tool results or the user: weather, places, prices, timings.
- Never invent opening hours, ticket prices, phone numbers or distances. If you
  don't have one, write `check before going` next to it.
- If a tool returns no data for something, say so plainly in the plan.

## 3. Schedule realistically

- **Day 1 starts with travel.** Subtract the journey time from the start city;
  don't plan a full morning at the destination if they leave home at 7 am.
- **Last day ends with travel back.** Keep the afternoon light; leave by the
  time that gets them home at a reasonable hour.
- **Cluster by area.** Put places that are close together in the same half-day;
  never zig-zag across town.
- **Pace:** 2–3 main stops per day for relaxed trips, max 4 for active ones.
  Kids/seniors: 2 stops + a rest break.
- **Buffers:** add 30 min between stops for travel, parking, queues, food.
- **Best time per place:** viewpoints at sunrise/sunset, outdoor treks in the
  morning, museums/indoor places in the hottest or rainiest part of the day.
- **Meals:** plan lunch and dinner near where they'll be, matching their diet.

## 4. Adapt to the weather

| Forecast | Do this |
|---|---|
| Rain / drizzle / mist | indoor or covered places in the afternoon; warn about slippery trails, waterfalls and ghats; carry rain gear |
| Very hot (> 33°C) | outdoor stops before 11 am or after 4 pm; hydration reminder |
| Cold (< 15°C) | late starts; warm layers in the packing list |
| Storm / heavy rain alert | say clearly that the trip may not be safe; suggest postponing or an alternative |

## 5. Respect the budget

- Show a cost breakdown: travel, stay, food, entry/activities, buffer (~10%).
- Mark every number as an estimate and say where it came from (tool or user).
- If the plan is over budget, say by how much and give the cheapest change
  that fixes it (cheaper stay, fewer paid activities, bus instead of cab).

## 6. Always include a Plan B

For each day, one alternative if the main plan fails (rain, closure, crowds).

## 7. Output format

Use this structure. Keep each line short; the traveller reads it on a phone.

```markdown
# <Destination> — <N>-day trip (<dates>)

**Summary:** 1–2 lines: why this place, overall vibe, who it suits.
**Weather:** <forecast> → <what it means for the plan>
**Getting there:** <mode, approx. travel time, when to leave>

## Day 1 — <theme, e.g. "Lakes and viewpoints">
| Time | Plan | Notes |
|---|---|---|
| 07:00 | Leave <start city> | ~2.5 h by car |
| 10:00 | <Place> | why go, how long to spend |
| 13:00 | Lunch near <area> | veg options, etc. |
| ... | ... | ... |
**Plan B:** <what to do if it rains / place is closed>

## Day 2 — <theme>
... same table ...

## Budget (estimate)
| Item | Cost | Source |
|---|---|---|
| Travel | ₹... | tool / user / estimate |
| Stay | ₹... | |
| Food | ₹... | |
| Activities | ₹... | |
| Buffer (10%) | ₹... | |
| **Total** | **₹...** | vs budget ₹... → fits / over by ₹... |

## Before you go
- [ ] Book: <stay / tickets that sell out>
- [ ] Check: <things marked "check before going">
- [ ] Pack: <3–5 items based on weather and activities>

## Safety & tips
- 2–4 short, specific tips (weather, roads, local rules, emergency numbers if known).
```

## 8. Final self-check before answering

- Does day 1 account for travel time from the start city?
- Are places on the same day close to each other?
- Does every price/time come from a tool or the user, or is it marked `check before going`?
- Does the plan respect the diet, budget, pace and weather?
- Is there a Plan B for each day?

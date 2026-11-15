# Presentation outline (Sun 22 Nov · 10 min talk + 5 min Q&A)

The plan for every slide: what it says, which figure it shows, whose task produces that figure, who
speaks, and for how long. **Fill it in as results arrive**; the actual deck is built in **Canva** at
CP4 → CP5 (8–11 Nov) and locked after rehearsal 2 (Fri 20 Nov).

**Why plan now:** each analysis task knows which figure the talk needs from it, so we make the right
plots once instead of twenty we don't use.

## Budget: 8 min 40 s planned, 1 min 20 s buffer

| Speaker | Slides | Time |
|---|---|---|
| Lynn | 1–2, 7–8, 12 | ~3 min 10 s |
| Sumaiya | 3–6 | ~2 min 35 s |
| Mahmoud | 9–11, 13 | ~2 min 55 s |

Rubric (Part A, 7 marks): Problem & Motivation 1 · Data & EDA 1.5 · Methods & Evaluation 1.5 ·
Results & Insights 2 · Delivery & Organization 1 (within 10 min, all speak, logical flow, readable slides).

---

## Slides

**Rule for every title: state the finding, not the topic** (Lec 5). "Boosting cuts ETA error by ~30%",
not "Results". Placeholders in `[brackets]` get their numbers at CP4.

| # | Title (draft) | Content / figure | Source task | Speaker | Time | Rubric row |
|---|---|---|---|---|---|---|
| 1 | Predicting Food Delivery Time and Its Key Delay Drivers | Title, names + IDs, course | — | Lynn | 10 s | Delivery |
| 2 | Late deliveries cost trust; can we predict them at the moment of ordering? | Who uses the answer (ops team: courier allocation, promise padding) + **the research question in one sentence** (ALIGNMENT §1). The stakes must land in the first minute | L7 | Lynn | 45 s | Problem & Motivation |
| 3 | 568k real Meituan orders: we predict delivery time using only what's known at ordering | Dataset facts (8 days, 23 districts) + an **order timeline graphic**: order → dispatch → pickup → arrival, with "known at prediction time" shaded. Shows the leakage rule visually | S2 | Sumaiya | 35 s | Data & EDA |
| 4 | The raw data needed real cleaning: 654k → 546k rows | **Before → after funnel/table**: refused dispatches, zero timestamps, pre-booked, > 3 h. Answers proposal feedback FB2 | S2, S4 | Sumaiya | 50 s | Data & EDA |
| 5 | [EDA finding 1, e.g. "Delivery time rises ~X min per km, and holds within every district"] | One figure + the modelling decision it led to | S3 | Sumaiya | 35 s | Data & EDA |
| 6 | [EDA finding 2, e.g. "Deliveries are slowest at meal peaks (median X min at 11:00 vs Y overall)"] | `delivery_by_hour` + the decision it led to (`lunch_peak` / `dinner_peak` features, F5). Not load: it barely matters within area and hour (M5) | S3 | Sumaiya | 35 s | Data & EDA |
| 7 | Two baselines, three models, order-time features only | Baselines: median + **the platform's own promise**. Models: Elastic-Net (interpretable), Random Forest, gradient boosting. Features: distance, prep time, cyclical time of day, district load | L3, M2 | Lynn | 45 s | Methods & Evaluation |
| 8 | Tested like real deployment: train on earlier days, test on later ones | **Time-split diagram**: 17–22 Oct with forward-chaining folds, 23–24 Oct test used once. Why MAE. Bootstrap CIs. One line on the Saturday-fold issue → `is_weekend` dropped | split, L5 | Lynn | 40 s | Methods & Evaluation |
| 9 | [Boosting cuts ETA error by X% vs the median and Y% vs the platform] | **Bar chart of test MAE with 95% CIs**: promise, median, Elastic-Net, RF, boosting | L5/L6 table, M4 | Mahmoud | 55 s | Results & Insights |
| 10 | [Distance and prep time drive delays most; restaurant wait > road time at peaks] | Grouped permutation importance + one line from the stage analysis | M5, S6 | Mahmoud | 45 s | Results & Insights |
| 11 | [Errors grow at meal peaks and in districts A, B] | Error by hour (or district); one sentence on why | M6 | Mahmoud | 40 s | Results & Insights |
| 12 | [At the same average promise, our promises are late X% vs the platform's Y%] | **Promise-gap figure** (`experiments.promise_test`), the business answer | L4 | Lynn | 45 s | Results & Insights |
| 13 | What it means, and what it can't tell us | Answer to the RQ in one line; 2 limitations (8 days / one weekend day; no weather, traffic or courier data at order time); 1 ethics point (tighter promises pressure couriers); 1 future step | M8, L7 | Mahmoud | 35 s | Results & Insights (limitation) |

## Backup slides (after "Thank you", for the Q&A only)

The Q&A rubric rewards being able to "point to the relevant figure". Prepare these, but don't present them:

- B1 Full cleaning table with counts (S2)
- B2 Leakage audit: honest vs leaky model MAE (S5)
- B3 Hyperparameters and search ranges (L3, M4)
- B4 Error by district, all 23 (M6)
- B5 The `is_weekend` fold-4 blow-up (README §4, F8)
- B6 Haversine vs Manhattan result (M3)

## Canva rules (so three people's slides look like one deck)

- 16:9. Lynn creates the deck from one template and shares an edit link; **each person edits only their own slides**.
- Figures: export PNG at 300 dpi from the notebooks (same files as the report, so numbers always match).
- Colours: our validated pair, blue `#2a78d6` (ours) and orange `#eb6834` (platform), plus aqua `#1baf7a` as a third.
  Same meaning on every slide.
- Body text ≥ 18 pt, at most ~3 bullets per slide. One idea per slide (proposal feedback FB4: too dense).
- Speaker notes: each person writes their script in the notes; time yourself before rehearsal 1.

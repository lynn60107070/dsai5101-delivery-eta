# Presentation outline (Sun 22 Nov · 10 min talk + 5 min Q&A)

The plan for every slide: what it says, which figure it shows, whose task produces that figure, who
speaks, and for how long. **Fill it in as results arrive**; the actual deck is built in **Canva** at
15 Nov. Slides + scripts ready **Thu 19 Nov night**, dry-run call **Sat 21 Nov**, group run-through
before class **Sun 22 Nov**.

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

**Rule for every title: state the finding, not the topic** (Lec 5). All numbers below are final
(test days, CP4), except slide 10's drivers (CV). Figure files are PNGs at 300 dpi in `figures/`.

| # | Title (final numbers) | Content / figure | Source task | Speaker | Time | Rubric row |
|---|---|---|---|---|---|---|
| 1 | Predicting Food Delivery Time and Its Key Delay Drivers | Title, names + IDs, course | — | Lynn | 10 s | Delivery |
| 2 | Late deliveries cost trust: can we predict delivery time at the moment of ordering? | Who uses the answer (ops team: courier allocation, promise length) + **the research question in one sentence** (ALIGNMENT §1). The stakes must land in the first minute | L7 | Lynn | 45 s | Problem & Motivation |
| 3 | 546k real Meituan orders: we predict delivery time using only what's known at ordering | `figures/eda/order_timeline` (order → dispatch → pickup → arrival, "known at prediction time" shaded) + 8 days, 23 districts | S2 | Sumaiya | 35 s | Data & EDA |
| 4 | The raw data needed real cleaning: 654k rows → 546k orders | `figures/eda/cleaning_funnel`: refused dispatches (−85,797), pre-booked (−22,181), > 3 h (−24), 1 without arrival. Answers proposal feedback FB2 | S2, S4 | Sumaiya | 50 s | Data & EDA |
| 5 | Delivery time rises ~7 min per km, in every one of the 23 districts | `figures/eda/delivery_vs_distance` → distance is the core feature (F1); spread grows with distance, which is why promises need a higher quantile | S3 | Sumaiya | 35 s | Data & EDA |
| 6 | Deliveries are slowest at the meal peaks: median 33.5 min at 11:00 vs 27.8 overall | `figures/eda/delivery_by_hour` → `lunch_peak` / `dinner_peak` features (F5). Not load: it barely matters within area and hour | S3 | Sumaiya | 35 s | Data & EDA |
| 7 | Two baselines, three models, order-time features only | Baselines: median + **the platform's own promise**. Models: Elastic-Net (interpretable), Random Forest, gradient boosting. Features: distance, prep estimate, cyclical time of day, district load, district. Courier, dispatch, pickup never used (leakage) | L3, M2 | Lynn | 45 s | Methods & Evaluation |
| 8 | Tested like deployment: every fold trains only on earlier days | `figures/results/time_split`. Test days scored once. MAE in minutes, bootstrap CIs. One line: weekend flag dropped (one weekend day in training) | L5 | Lynn | 40 s | Methods & Evaluation |
| 9 | Boosting misses by 6.5 min on average: 31% less than the median guess, 3.1 min less than the platform's promise | `figures/results/test_mae`. RF is only 0.05 min behind → the limit is the information, not the model | L5/L6, M4 | Mahmoud | 55 s | Results & Insights |
| 10 | Distance drives delivery time far more than anything else; load barely matters | `figures/results/delay_drivers` (distance +3.10 ≫ time +0.86 ≈ area +0.83 > prep +0.67 > load +0.19). One line from S6: pickup and road each take a median 13.1 min, both ~2.7 min slower at peaks | M5, S6 | Mahmoud | 45 s | Results & Insights |
| 11 | Errors grow on long trips and at the lunch peak | `figures/results/errors_by_distance` or `errors_by_hour`. Test: < 1 km 5.6 min vs > 7 km 14.4; 11:00 7.2 vs 6.5 overall; Sunday 6.77 vs Monday 6.17. **Mahmoud: switch to the test-day version (M6)** | M6 | Mahmoud | 40 s | Results & Insights |
| 12 | Same average promise: the platform is still late less often (5.0% vs our 6.1% > 5 min late) | `figures/promise/final_test_gap`. Better estimates ≠ better promises: the platform can still act after ordering (the 8-min cliff) | L4 | Lynn | 45 s | Results & Insights |
| 13 | What it means, and what it can't tell us | Answer to the RQ in one line; leakage audit: with after-order times MAE 6.25 → 4.53, so the missing information is the ceiling; 2 limitations (8 days / one weekend day; no weather, traffic or courier data); 1 ethics point (district errors 4.4–9.0 min; promise length shifts pressure to couriers or customers); 1 future step | M8, L7, S5 | Mahmoud | 35 s | Results & Insights (limitation) |

## Backup slides (after "Thank you", for the Q&A only)

The Q&A rubric rewards being able to "point to the relevant figure". Prepare these, but don't present them:

- B1 Full cleaning table with counts (S2)
- B2 Leakage audit: honest vs leaky model MAE (`figures/eda/leakage_audit`, S5)
- B3 Hyperparameters and search ranges (report Table: models) + `figures/results/hgb_complexity_curve`
- B4 Error by district, all 23 (`figures/results/errors_by_area`, M6)
- B5 The `is_weekend` fold-4 blow-up (README §4, F8)
- B6 Haversine vs Manhattan result (M3)
- B7 Stages by area (`figures/eda/stages_by_area`, S6)
- B8 Promise padding: 35% of promises at the 30-min minimum, the 8-min cliff (`figures/eda/promise_padding`)

## Canva rules (so three people's slides look like one deck)

- 16:9. Lynn creates the deck from one template and shares an edit link; **each person edits only their own slides**.
- Figures: export PNG at 300 dpi from the notebooks (same files as the report, so numbers always match).
- Colours: our validated pair, blue `#2a78d6` (ours) and orange `#eb6834` (platform), plus aqua `#1baf7a` as a third.
  Same meaning on every slide.
- Body text ≥ 18 pt, at most ~3 bullets per slide. One idea per slide (proposal feedback FB4: too dense).
- Speaker notes: each person writes their script in the notes; time yourself before rehearsal 1.

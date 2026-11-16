# Presentation outline (Sun 22 Nov · 10 min talk + 5 min Q&A)

The deck template: sections, slides, what each slide shows, and the spoken story that runs through it.
**Speakers are not assigned yet.** The deck is built in **Canva**. Slides + scripts ready **Thu 19 Nov
night**, dry-run call **Sat 21 Nov**, group run-through before class **Sun 22 Nov**.

Rubric (Part A, 7 marks): Problem & Motivation 1 · Data & EDA 1.5 · Methods & Evaluation 1.5 ·
Results & Insights 2 · Delivery & Organization 1 (within 10 min, all speak, logical flow, readable slides).
Part B (Q&A, 3 marks): see [qa_prep.md](qa_prep.md).

## The story in one paragraph

Houston airport fixed complaints about baggage waits without making a single bag faster: it changed
how the wait *felt*. Delivery apps face the same problem about 50 times a minute in one city. We follow
one real order (#85188) through the talk: what the app knew when it was placed, why it took 43 minutes,
and how our model's guess compares with the app's promise. The app's promise looks 3 minutes worse than
ours, but that's padding: take the padding off and the app's own estimate is about as accurate as ours.
What gets us further is what the app knows in real time (free riders, each restaurant's track record).
The twist: even so, the app makes better *promises*, because it can act after the order is placed. And
someone pays for every minute a promise is shortened: the rider.

## The example order (#85188, a test day, never seen by the model)

| | |
|---|---|
| Placed | Sunday 23 Oct, 11:13 |
| Distance | 3.2 km |
| App's promise | 51 min |
| Our model's estimate | 45 min |
| Actual delivery time | 43 min (8 min before the promise, 2 min off from ours) |
| Stages | picked up after 12.5 min (overall median 13.1), then 31 min on the road |

It is typical, not cherry-picked: among the 634 Sunday orders placed at 11:xx and 3–5 km away, the
medians are actual 45.3, promise 52.2, our prediction 45.2. In that group our model is off by 8.4 min
on average and the promise by 11.0; 26% arrived after the promise.

## Three words we use precisely

- **Delivery time**: how long the food actually took, order → arrival. **This is what we predict.**
- **Promise**: the time the app showed at checkout. A commitment, deliberately padded.
- **Delay**: delivery time − promise. Only used to describe the data and count late orders.

We built two things: an **estimate** ("when will it most likely arrive?", boosting, MAE 6.49) and a
**promise** ("a time it will almost certainly arrive by", the 80th-percentile model). Only the promise
is compared with the app's promise in the promise test.

## Time budget: ~9 min 5 s planned, ~55 s buffer

Hooks are the first thing to cut if a rehearsal runs long: keep each to two sentences.

---

## Slides

**Rule for every title: state the finding, not the topic.** Numbers are final (test days) except
slide 6 (EDA, all days) and slide 10's drivers (CV). Figures: 300-dpi PNGs in `figures/`.

### Section 1 · Problem & Motivation (1 mark)

**Slide 1 · Title** (5 s)
- Predicting Food Delivery Time and Its Key Delay Drivers
- Names + student IDs, DSAI 5101, date. Go straight into the hook.

**Slide 2 · Same wait, different feeling: can we predict delivery time the moment you order?** (50 s)
- Hook (Houston): *"Houston airport had a problem: passengers complained they waited too long for
  their bags. The airport fixed it without making a single bag faster. They moved the arrival gates
  further away, so people walked six times longer, and the complaints almost disappeared. Same wait,
  different feeling."*
- Hook (right now): *"Right now, while I'm talking, about fifty people in one city just pressed
  'order', and every one of them was immediately given a promise."*
- Who uses the answer: the platform's operations team (promise length, courier planning)
- **Research question, boxed:** using only information available when an order is placed, how
  accurately can we predict delivery time, and what drives long deliveries?
- On slide: baggage-claim image or icon, the boxed question, "~50 orders a minute, in one city"

**Slide 3 · Meet order #85188: what the app knew at 11:13** (40 s)
- Script: *"Let's follow one of them. Sunday, 23 October, 11:13. Someone orders lunch from a
  restaurant 3.2 km away. The app says: 51 minutes. Here's everything it knows at that second, and
  everything it doesn't."*
- `figures/eda/order_timeline` with "known at ordering" shaded + the order's card
- 🎣 Bait: *"We predict how long it actually takes, not the promise."* → invites "what's the
  difference / why not predict delay?" (B9)
- 546k orders, 8 days, 23 districts, Meituan INFORMS TSL 2024
- Anything after the shaded part is the future (leakage): never used

### Section 2 · Data & EDA (1.5 marks)

**Slide 4 · The raw data needed real cleaning: 654k rows → 546k orders** (40 s)
- Script: *"Before we could follow any order, we had to find the real ones."*
- `figures/eda/cleaning_funnel`, each step with its reason:
  - refused dispatches (−85,797): repeat offers of the same order, not new orders
  - pre-booked (−22,181): a different population; holds almost all deliveries over 3 h
  - implausible durations (−24)
- Default prep estimates (13.8%): flagged as missing, not dropped (not missing at random)

**Slide 5 · Delivery time rises ~7 min per km, in every district** (30 s)
- Script: *"Our order was 3.2 km away. Every kilometre adds about seven minutes, so a friend ordering
  the same dish from 1 km away would get it about 15 minutes sooner."*
- `figures/eda/delivery_vs_distance`, our order marked
- Spread grows with distance → promises need a higher percentile
- → Distance is the core feature

**Slide 6 · Slowest at meal peaks: median 33.5 min at 11:00 vs 27.8 overall** (30 s)
- Script: *"And our customer ordered at the slowest hour of the day. Half the city had the same idea."*
- `figures/eda/delivery_by_hour`, 11:00 highlighted
- Area load barely matters within the same district and hour
- → Lunch/dinner peak flags + cyclical time of day (23:59 sits next to 00:00)

### Section 3 · Methods & Evaluation (1.5 marks)

**Slide 7 · Two baselines, three models, order-time information only** (50 s)
- Hook (the friend): *"You know the friend who texts 'five minutes away' and arrives twenty minutes
  later? The app is the opposite friend: it never promises under 30 minutes, promises 38 on average,
  and food takes 30."*
- 🎣 Bait (one line, no explanation): *"Padded, and still late 15% of the time."* → invites "isn't
  arriving early a good thing?" (B10)
- Baselines: the median guess; the platform's own promise
- Models, each with its reason: Elastic-Net (readable), Random Forest (robust), gradient boosting
  (strongest on tabular data). Tuned by random search on the CV folds
- Features: distance, prep estimate, time of day, district load, district. Never courier, dispatch,
  pickup (they happen after ordering)

**Slide 8 · Tested like real life: the model only ever sees the past** (40 s)
- Script: *"We held ourselves to the app's rules. The model learns from earlier days and predicts later
  ones. The last two days, including our Sunday order, were locked away until the very end."*
- `figures/results/time_split`: forward-chaining CV on 17–22 Oct, test 23–24 Oct scored once
- MAE in minutes: readable for operations, not dominated by a few extreme orders. Also RMSE, R²,
  bootstrap 95% CIs
- Weekend flag dropped: only one weekend day in training
- Imputation, scaling and encoding sit inside each model's pipeline, refitted on every fold's training
  days, so nothing leaks from validation or test days
- Tuning mattered: small inset of `figures/results/hgb_complexity_curve`. Bigger trees overfit
  (511 leaves: train error 2.45 vs CV 6.63)

### Section 4 · Results & Insights (2 marks)

**Slide 9 · Our model misses by 6.5 min: as accurate as the app's own estimate, once its padding is removed** (55 s)
- Script: *"So, our order. The app said 51. Our model said 45. It arrived in 43. Across all 140,000 test
  orders, we're off by 6.5 minutes on average, 31% better than guessing. The app looks 3 minutes worse,
  but that's its padding: take off its usual 8 minutes and it's about as accurate as we are, 6.48
  against 6.49. With public data from the moment you order, we reach the platform's own level."*
- `figures/results/test_mae` (new version): promise 9.62 · median 9.46 · promise minus padding 6.48
  (hatched) · Elastic-Net 6.80 · RF 6.54 · boosting 6.49
- The padding (8.2 min) is measured on the training days only, so no test information is used
- 🎣 Bait: *"We're better on short and long trips, the app on medium trips and at lunch."* → invites
  "where exactly?" (B11; holds even when the padding is removed per distance band, qa_prep §5)
- 🎣 Bait: *"Our order is a typical one."* → invites "isn't it cherry-picked?" (B12)
- Bootstrap 95% CIs: boosting vs median −2.97 [−3.00, −2.93]; boosting vs RF −0.05 [−0.06, −0.04],
  so real but tiny. R² 0.49 shown openly (the ceiling is on slide 13)
- Three models within 0.3 min → the limit is the information, not the model
- Test ≈ CV + 0.2 min, same ranking → holds up on new days

**Slide 10 · Distance drives delivery time; then free riders and the restaurant's track record** (50 s)
- Script: *"So why did our order take 43 minutes? 12.5 minutes until pickup, about average, then 31 on
  the road. Mostly distance, then lunchtime. How many new orders come in barely matters. What matters is
  how many riders are free: when more than three orders wait per free rider, the median delivery takes
  36 minutes instead of 26. Add that and each restaurant's past delivery times, and our error drops
  another 0.3 minutes."*
- `figures/results/delay_drivers`: distance +3.10 ≫ time +0.86 ≈ district +0.83 > prep +0.67 > load +0.19
- Extension (CV only, test untouched): riders + restaurant history + recent district delays + restaurant
  queue, CV MAE 6.25 → 5.95 (CI −0.31 to −0.29), R² 0.51 → 0.56; restaurant history −0.24, riders −0.05,
  the rest −0.01. **Beats the app's de-padded promise on the validation days: overall 5.95 vs 6.24 and in
  5 of 7 segments; the app still wins at lunch (6.66 vs 6.79).** Small inset or B13/B15
- Pickup and road each take a median 13.1 min; both ~2.7 min slower at peaks
- Proposal: right on distance and peaks, wrong on load

**Slide 11 · Our model struggles with long trips and the lunch rush** (30 s)
- Script: *"Lunch is our hardest hour: we're off by 7.2 minutes, not 6.5, and this is where the app's
  own estimate beats ours (6.7). It probably knows how many riders are free right now. Weekends are
  slower too: 1 to 3.5 minutes in the afternoon, and we only had one weekend day to learn from."*
- `figures/results/errors_by_distance` or `errors_by_hour`, **test-day version (M6)**
- < 1 km 5.6 vs > 7 km 14.4 · 11:00 7.2 vs 6.5 overall · Sunday 6.77 vs Monday 6.17 · districts 4.4–9.0

**Slide 12 · Same average promise: the app is still late less often** (60 s)
- Hook (weather): *"A weather forecast tells you it will probably rain. A promise says you'll stay dry.
  Those are different jobs."*
- Script: *"We turned our forecast into promises with the same average length as the app's, 38.2
  minutes, and the app was still late less often: 5.0% of orders more than five minutes late, against
  our 6.1%. Look at this cliff: late orders more than halve at exactly 8 minutes late. Something
  happens after the order is placed. Someone starts rushing, and a model at ordering can't see that."*
- How: gradient boosting trained with quantile (pinball) loss at the 80th percentile, shifted +2.7 min
  so its average promise equals the app's 38.2; then compare the share > 0, 5, 10 min late (bootstrap CIs)
- `figures/promise/final_test_gap` + small inset of the 8-min cliff (`figures/eda/promise_padding`)
- 🎣 Bait: *"Except for shorter promises."* (one line, no detail) → invites "so did you beat them or
  not?" (B11)
- One line: better estimates ≠ better promises

### Section 5 · Conclusion (counts for Results & Insights: meaning + limitations)

**Slide 13 · What it means, and what it can't tell us** (50 s)
- Hook (Trapped in the system): *"That 'someone rushing' is a real person. In 2020 a Chinese magazine
  published a viral article, 'Delivery Riders, Trapped in the System', on algorithms shortening
  delivery times until riders ran red lights to keep up. The company in that story is the one whose
  data we used."*
- Answer: at ordering, delivery time can be predicted to ~6.5 min, and distance is the main driver
- Leakage audit: with after-order times, MAE 6.25 → 4.53 and R² 0.51 → 0.72, so missing information
  is the ceiling (and why R² 0.49 is not a weak model)
- Limitations: 8 days with one weekend day (no drift within the week, but none measurable beyond it); no
  weather or traffic; rider availability only approximated from past deliveries
- Ethics: error uneven across districts (4.4–9.0 min); every minute cut from a promise lands on a rider
- Next: confirm the extra features on new days; update the estimate after dispatch

**Slide 14 · Thank you** (20 s)
- Closing: *"Houston didn't make the bags faster, it changed the wait. Since we started talking, about
  500 people in one city were given a promise. We can make that number more accurate. What we learned
  is that a good promise needs more than an accurate number. Thank you."*
- Questions · repo link · names

## Where each hook appears

| Hook | Slides |
|---|---|
| Houston airport | 2 (open), 14 (close) |
| "Right now, while I'm talking" | 2 (~50 a minute), 14 (~500 since we started) |
| Order #85188 | 3, 5, 6, 8, 9, 10, 11 |
| The "five minutes away" friend | 7 |
| Weather forecast vs promise | 12 |
| Trapped in the system | 13 |

**Check before the talk:** Houston baggage claim (NYT, Alex Stone, "Why Waiting Is Torture", 2012);
"Delivery Riders, Trapped in the System" (*Renwu*, Sept 2020); ~50 orders a minute = 546,340 ÷ 8 days
÷ 1,440 min ≈ 47.

## Backup slides (after "Thank you", for the Q&A only)

The Q&A rubric rewards being able to "point to the relevant figure":

- B1 Full cleaning table with counts (S2)
- B2 Leakage audit: honest vs leaky model MAE (`figures/eda/leakage_audit`, S5)
- B3 Hyperparameters and search ranges (report Table: models) + `figures/results/hgb_complexity_curve`
- B4 Error by district, all 23 (`figures/results/errors_by_area`, M6)
- B5 The `is_weekend` fold-4 blow-up (README §4, F8)
- B6 Haversine vs Manhattan result (M3)
- B7 Stages by area (`figures/eda/stages_by_area`, S6)
- B8 Promise padding: 35% of promises at the 30-min minimum, the 8-min cliff (`figures/eda/promise_padding`)

**Answer slides for the 🎣 bait.** Each main-slide bait line is one sentence with no explanation;
the full answer is ready here. Full spoken answers are in [qa_prep.md](qa_prep.md) §5.

- B9 **Delivery time vs promise vs delay**: three-row table (what it is, example from order #85188:
  43 actual, 51 promised, −8 delay) + estimate (aims at the middle) vs promise (aims at the 80th
  percentile)
- B10 **Why a padded promise isn't free**: lost orders, bad customer planning, trust wears off,
  operations need the real time; same buffer for every order → too much at 1 km, too little at 7 km
- B11 **Scorecard, won and lost** (`report/tables/depadded_test.tex`): vs the promise as shown ✓ (6.49 vs
  9.62) · vs the de-padded promise = (6.49 vs 6.48 one average; ✗ 6.49 vs 6.36 per distance band) ·
  per band: under 1 km ✓ (5.61 vs 5.86) · over 3 km ✓ (8.73 vs 9.94) · 1–3 km ✗ (6.67 vs 6.19) · lunch ✗
  (7.22 vs 6.68) · explains why ✓ · shorter promises ✓ · extended model on CV ✓ 5 of 7 segments
  (`report/tables/extension_vs_platform.tex`)
  (below ~37 min) · promises at the app's own length ✗ (6.1% vs 5.0% > 5 min late)
- B12 **Order #85188 is typical**: its segment's medians (actual 45.3, promise 52.2, ours 45.2) and
  segment MAE (ours 8.4, app 11.0)

**Answer slides for the instructor's feedback** (all from `experiments/feedback.py` and
`experiments/extension.py`; the test days were not re-scored):

- B13 **Rider pressure map** (`figures/results/rider_pressure`): orders waiting per free rider by district
  × hour; > 3 per rider (19% of orders) → median 35.6 vs 26.4 min
- B14 **Weekday vs weekend, and drift** (`figures/results/day_profiles`): same daily shape (r = 0.92),
  weekend 1–3.5 min slower noon–18:00; Mon 17 vs Mon 24 differ by 0.5 min per busy hour
- B15 **What the extended model learned** (`figures/results/partial_dependence`) + `report/tables/extension_cv.tex`
  + `report/tables/extension_vs_platform.tex` (re-tuning chose the same settings, so no gain there)
- B16 **Industry benchmark** (`report/tables/benchmark.tex`): Ele.me (MAE −9.8% online, uses supply–demand
  and restaurant backlog, like our extension), Uber DeepETA (asymmetric loss: late costs more, like padding)
- B17 **Data issues with %** (`report/tables/data_issues.tex`): no exact duplicates; 13.1% refused dispatch
  rows; 3.9% pre-booked; 1.4% prep missing; 13.8% prep default; each with its decision
- Reproducibility: `python -m experiments.reproduce` rebuilds every table, figure and notebook

**Rules for bait:** only plant questions we can answer in two sentences with a slide to point to.
Keep anything we can't defend in depth (exact tuning ranges, model internals) off the main slides,
and answer it from B3 if asked.

## Canva rules (so three people's slides look like one deck)

- 16:9. Lynn creates the deck from one template and shares an edit link; each person edits only their
  own slides once speakers are assigned.
- Figures: the 300-dpi PNGs from `figures/` (same files as the report, so numbers always match).
- Colours: blue `#2a78d6` = ours, orange `#eb6834` = the platform, aqua `#1baf7a` third. Same meaning
  on every slide.
- Body text ≥ 18 pt, at most ~3 bullets per slide. One idea per slide (proposal feedback FB4: too dense).
- Speaker notes: each person writes their script in the notes; time yourself before the dry run.
- Export a PDF and a PPTX copy before Sunday, bring them on a USB stick, and commit `slides.pdf` here.

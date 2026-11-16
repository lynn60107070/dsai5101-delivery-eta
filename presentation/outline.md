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
and how our model's guess compares with the app's promise. The twist: we predict the real time better,
but the app still makes better *promises*, because it can act after the order is placed. And someone
pays for every minute a promise is shortened: the rider.

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

**Slide 9 · Our model misses by 6.5 min: 3.1 min closer than the app's promise** (55 s)
- Script: *"So, our order. The app said 51. Our model said 45. It arrived in 43. Across all 140,000 test
  orders, we're off by 6.5 minutes on average: 31% better than guessing, 3 minutes closer than the app."*
- `figures/results/test_mae`: promise 9.62 · median 9.46 · Elastic-Net 6.80 · RF 6.54 · boosting 6.49
- 🎣 Bait, said out loud: *"But the app's promise isn't trying to be accurate, so this isn't a fair
  fight. That's slide 12."* (shows we know the weakness before anyone asks)
- 🎣 Bait: *"Our order is a typical one."* → invites "isn't it cherry-picked?" (B12)
- Bootstrap 95% CIs: boosting vs median −2.97 [−3.00, −2.93]; boosting vs RF −0.05 [−0.06, −0.04],
  so real but tiny. R² 0.49 shown openly (the ceiling is on slide 13)
- Three models within 0.3 min → the limit is the information, not the model
- Test ≈ CV + 0.2 min, same ranking → holds up on new days

**Slide 10 · Distance drives delivery time; how busy the area is barely matters** (45 s)
- Script: *"So why did our order take 43 minutes? 12.5 minutes until pickup, about average, then 31 on
  the road. Mostly distance, then lunchtime. The busy-area effect people expect? Almost nothing."*
- `figures/results/delay_drivers`: distance +3.10 ≫ time +0.86 ≈ district +0.83 > prep +0.67 > load +0.19
- Pickup and road each take a median 13.1 min; both ~2.7 min slower at peaks
- Proposal: right on distance and peaks, wrong on load

**Slide 11 · Our model struggles with long trips and the lunch rush** (30 s)
- Script: *"Lunch is our hardest hour. For orders like ours, we're off by 8.4 minutes, not 6.5. Still
  better than the app's 11."*
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
- Limitations: 8 days with one weekend day; no weather, traffic or courier data
- Ethics: error uneven across districts (4.4–9.0 min); every minute cut from a promise lands on a rider
- Next: update the estimate after dispatch; restaurant history features

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
- B11 **Scorecard, won and lost**: accuracy ✓ (6.49 vs 9.62) · explains why ✓ · shorter promises ✓
  (below ~37 min) · promises at the app's own length ✗ (6.1% vs 5.0% > 5 min late)
- B12 **Order #85188 is typical**: its segment's medians (actual 45.3, promise 52.2, ours 45.2) and
  segment MAE (ours 8.4, app 11.0)

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

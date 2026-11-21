# Alignment: why every step exists

Every task traces back to one of four sources: the **instructor's feedback** on our proposal, what we
**promised in the proposal**, the **rubrics/guidelines**, and the **lectures**
(`../lects/`: Lec 1 Intro, Lec 2 Lifecycle, Lec 3 EDA I, Lec 4 EDA II, Lec 5 Visualisation,
Lec 6 Feature Engineering, Lec 7 ML Foundations). Before you call a task done, check its row here.
In the Q&A, "why did you do X?" should always have an answer from this file.

---

## 1. The research question (fixes feedback #1: "state it clearly as one question")

> **At the moment a Meituan order is placed, using only information known at that moment, how accurately
> can we predict its delivery time (minutes from order placement to arrival), and which order-time
> conditions drive long deliveries?**

- **We predict the delivery time, not the delay.** Delay = actual − platform promise. It is used only to
  describe the data (EDA) and to score promises (late rate), never as the model target.
- **When:** at order placement. Anything recorded later (dispatch, courier, pickup, arrival, the promise)
  is never a model input.
- **The question has three parts, each with its own evidence:**
  1. *How accurately?* Test-day MAE vs the median predictor and the platform promise, with bootstrap CIs.
  2. *Which conditions?* Grouped permutation importance, plus the restaurant-wait vs road-time stage analysis.
  3. *So what for operations?* Does an 80th-percentile model give fewer late orders than the platform
     **at the same average promised time**?

**T, P, E (Lec 1, Lec 7: "if you cannot fill in T, P and E you do not yet have an ML problem")**
- **T:** predict delivery minutes for a new order at the moment it is placed (regression).
- **P:** MAE in minutes on later, unseen days (23–24 Oct). RMSE and R² are secondary, and late rate counts orders arriving > 5 min after the prediction.
- **E:** 406,553 non-pre-booked orders from 17–22 Oct 2022 across 23 districts.

**Success criteria, written before modelling (Lec 2 Stage 1: business + ML, linked)**
- **ML:** tuned boosting cuts test MAE by ≥ 20% vs the median predictor (proposal), with a CI that excludes 0.
- **Business:** at the same mean promised time as the platform, our promise model has a lower late
  rate, and the drivers give the ops team a ranked list of where and when to add couriers.
- **Fallback (proposal, Lec 2 "kill criteria"):** if accuracy gains are small, the project's value
  is the driver and segment analysis, reported honestly ("a careful negative result scores better", Guidelines §7).

---

## 2. Proposal feedback → what we changed (Grade 90/100, Approved)

| # | Feedback | What we do about it | Where / task | Status |
|---|---|---|---|---|
| FB1 | Research question hidden; be precise about what is predicted and when; delivery time or delay? | One explicit question (§1); target = delivery time at placement; delay only for EDA and late rate | §1 above, `common/clean.py` header, report intro (L7), slide 1 (L8) | ✅ fixed in docs; carry into report |
| FB2 | Data isn't clean: make sure the listed problems are **really handled**, and **show it in the EDA** | Audit table with before/after counts for every quirk; a figure or table per problem in the report | S2 (audit + data dictionary), S4 (cleaning log README §4), S8 figures, report Data section (S9) | ✅ done: report Table I + flags, appendix Figs. 4–5 |
| FB3a | Hour of day needs careful (cyclical) encoding: 23 and 0 are close | `tod_sin`, `tod_cos` from minute of day, raw hour only for segment plots | `common/features.py`; unit test `test_time_of_day_is_cyclical` | ✅ done |
| FB3b | With 8 days, check everything fitted (encoders, imputers) is learned from training days only | All fitted steps live inside each model's Pipeline, refit per fold; unit test proves the imputer ignores validation days | `common/features.preprocessor`, test `test_fitted_steps_learn_from_training_days_only` | ✅ done |
| FB3c | (same concern, found by us) | `is_weekend` dropped: one weekend day in training made scaling explode on the Saturday fold (Elastic-Net fold-4 MAE 6.8 → 18.0). Weekend is described in EDA and stated as a limitation | `common/features.py`, README §4 F8 | ✅ done; discuss in report (S9, L7) |
| FB4 | Proposal too dense; can three people finish it all; what would you cut first? | Explicit cut list (§6); report methodology as numbered steps + one table; one idea per slide | §6 below, SCHEDULE.md | ✅ plan; apply when writing |

---

## 3. Proposal commitments → task (so we deliver what we promised)

| Proposal said | Task | Owner |
|---|---|---|
| Keep accepted dispatches; zero timestamps → missing; drop missing target | `clean.py` C1–C3 (done v0), confirm in S4 | Sumaiya |
| Pre-booked orders analysed separately | C4 + S7 | Sumaiya |
| Flag implausible durations from dataset constraints and EDA | C5 (v0: > 180 min) → justify in S4 | Sumaiya |
| Impute missing inputs with training medians; one-hot district | `preprocessor` (done) | shared |
| Distance: Haversine vs Manhattan, chosen by lower validation MAE | M3 (`--features base` vs `base_manhattan`) | Mahmoud |
| Features: prep time, hour, meal peaks, weekend, district load (past 15 min) | done in `features.py`, except weekend (FB3c) | Sumaiya |
| EDA: target skew → log decision; time vs distance, hour, load; delay by district and hour; restaurant wait vs road time | S3, S6 | Sumaiya |
| Baselines: median predictor and the platform's promise | `median` model + promise in every summary (done) | Lynn |
| Elastic-Net, Gradient Boosting, Random Forest, 80th-percentile boosting | L3, M2/M4, L4 | Lynn, Mahmoud |
| Random-search tuning | `experiments/tune.py` (done) → L3, M4, L4 | all |
| Grouped permutation importance for delay drivers | M5 | Mahmoud |
| Leakage audit: honest vs model with post-order timestamps | S5 (`--features leaky`) | Sumaiya |
| Stage analysis: restaurant wait vs road time, where errors increase | S6 | Sumaiya |
| Time split: train 17–22 with forward-chaining CV, retrain on all six days, test 23–24 once | `common/split.py` + `--eval test` at CP4 | shared |
| Preprocessing fit on the training portion of each fold only | Pipeline + unit test (done) | shared |
| MAE, RMSE (R² secondary); errors by district, hour, distance, test day | `common/evaluate.py` (done) → M6 | Mahmoud |
| Late > 5 min, vary the threshold | late rate in every summary; threshold variation in L4 | Lynn |
| Q80 vs promise at the same mean promised time: late rate, pinball, coverage | L4 | Lynn |
| Bootstrap confidence intervals for model differences | `experiments/compare.py` (done) → L6 | Lynn |
| Weekend results interpreted cautiously | FB3c + Conclusion | Lynn |
| Expected: distance, peaks, load top drivers; boosting −20% MAE; errors up at meal peaks | check each explicitly in M5 and M6 and say whether it held | Mahmoud |

---

## 4. The course lifecycle (Lec 2) → our tasks → rubric row

Lec 2's nine stages, and the artefact each leaves behind ("if a competent stranger can't understand the
project from these artefacts, it isn't finished").

| Stage (Lec 2) | Our artefact | Tasks | Report rubric row |
|---|---|---|---|
| 1 Frame | RQ, T/P/E, success criteria (§1) | L7 | Introduction (1.5) |
| 2 Acquire & understand | Data dictionary + quality audit table (7 quality dimensions, Lec 2) | S2 | Data & EDA (2.5) |
| 3 Prepare | Cleaning decisions log (README §4), code in `clean.py`, raw never modified | S4, S7 | Data & EDA |
| 4 Explore | EDA notebook with written conclusions, not just plots | S3, S6 | Data & EDA |
| 5 Engineer features | Feature log (README §4, F-rows), feature sets | S4, M3 | Methodology (3) |
| 6 Model | Baseline ladder: median → promise → Elastic-Net → RF/boosting → tuned; experiment log (`results/`) | L3, M2, M4, L4 | Methodology |
| 7 Evaluate (technical + business) | CV, test once, subgroup errors, leakage audit, bootstrap, promise test | M5, M6, S5, L4, L6 | Results & Discussion (3) |
| 8 Communicate | Report, slides, Q&A sheet | S9–M9, L7–L9 | all rows + Presentation |
| 9 Monitor | Future work: drift (8 days only), retraining, input monitoring | L7 (Conclusion) | Conclusion (1) |

---

## 5. Lecture checklists, applied to our project

**Lec 3 (EDA I): S2, S3**
- [ ] The four commands (`shape`, `info`, `describe`, `isna().sum()`) on the raw file, reported
- [ ] Sentinels: zeros in timestamps are "not recorded" (Lec 3 "red flags"): count per column
- [ ] Target: centre, spread **and shape** (skew g1, histogram at more than one bin width, log1p version)
- [ ] Missingness: *where*, not only how many. Compare orders with missing prep time against complete ones (Lec 3's "single most informative check")
- [ ] Outliers: apply the Lec 3 decision tree. Error → fix/remove. Rare but real → keep. **Different population → analyse separately** (pre-booked orders are exactly this: 4,073 of 4,097 deliveries over 3 h)
- [ ] Say what you did *not* find ("no timestamp-order violations" is a finding)

**Lec 4 (EDA II): S3**
- [ ] Plot before computing r; report Pearson **or** Spearman deliberately (delivery time vs distance is likely monotonic but curved → Spearman)
- [ ] Simpson check: does the distance–time relationship hold *within* districts, not just pooled? District is the obvious confounder
- [ ] Facet by district / hour group rather than overplotting 23 colours
- [ ] State how many pairs were looked at (forking paths)

**Lec 5 (Visualisation): every report and slide figure (S8, M6, L8)**
- [x] The most important quantity on position or length; no pies, no area, no dual axes
- [x] **Title states the finding** ("Delivery time rises ~X min per km"), not the variables
- [x] Axes labelled with units; hours in chronological order; bars start at zero
- [x] viridis or a colour-blind-safe palette; meaning never carried by colour alone; check in greyscale
- [ ] Every figure numbered, captioned and referenced in the text (Guidelines §6)

**Lec 6 (Feature engineering): S4, M3, all models**
- [x] Cyclical time of day (`tod_sin`, `tod_cos`)
- [x] Missingness flag next to the imputed value (`prep_missing`)
- [x] Backward-looking window only (`load_15m` counts strictly earlier orders)
- [x] Every fitted step inside one Pipeline (imputer, scaler, encoder), unseen districts handled
- [x] High cardinality: `restaurant` (4,962 levels) is **not** one-hot or target-encoded. If S4 adds a restaurant feature, it must be computed inside CV folds (Lec 6 "target encoding trap")
- [ ] Log transform decided from EDA *and* CV (v0: `--log-target` is worse for Elastic-Net, 7.15 vs 6.92)
- [ ] For every feature: "would I have this value at the moment I need to predict?" (leakage test question)

**Lec 7 (ML foundations): L3, L4, M2, M4**
- [ ] Always compare with a do-nothing baseline (median) **and** the business baseline (promise)
- [ ] Loss vs metric: we report MAE, so try `loss="absolute_error"` for boosting (median-targeting, in `SEARCH_SPACE`)
- [ ] Over/underfitting: one training-vs-CV error curve over a complexity setting (e.g. `max_leaf_nodes` or RF `min_samples_leaf`), a figure for the Methodology section
- [ ] Reducible vs irreducible error: the leaky model (MAE 4.53 vs 6.25, frozen HGB, S5) shows how much error is information we don't have at order time
- [ ] Test days scored **once** (Lec 1, Lec 7: "if you keep tuning until the test score looks good, it has become training data")

**Lec 1/2 (reproducibility, responsibility): everyone**
- [x] Fixed seed (42), pinned `requirements.txt`, transformations in code, raw data never modified
- [ ] Every number in the report traceable to `results/final/` (L5)
- [ ] Subgroup performance: errors by district (do some districts get systematically worse ETAs?) → ethics paragraph
- [ ] Ethics: tighter promises put pressure on couriers. Padding promises shifts risk to customers. Say so (Report rubric: Conclusion)

---

## 6. Scope: what we cut first (fixes feedback #4)

**Never cut:** median and promise baselines, time-based CV + one test evaluation, leakage audit,
EDA figures that inform modelling, Elastic-Net + boosting + RF comparison with bootstrap CIs, errors by
segment, grouped permutation importance, the q80 promise test (it is the business answer).

**Cut in this order if a checkpoint slips:**
1. The 10-minute late-threshold variant (keep 5 min)
2. Large RF tuning: RF is the comparison model, so 10 iterations on a sample are enough
3. Stage analysis by district (keep overall + by hour)
4. Pre-booked orders: one paragraph from the audit instead of a separate analysis
5. Extra features beyond v0 (restaurant load etc.)
6. Log-target variants for every model (decide once, apply to all)

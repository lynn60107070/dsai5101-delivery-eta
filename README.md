# DSAI5101 Project: Predicting Food Delivery Time and Its Key Delay Drivers for ETA and Dispatch Support

**Team:** Lynn Younes (60107070, Lead), Sumaiya Rizwan (60102626), Mahmoud Abdelaziz (60328910)
**Course:** DSAI 5101 Principles of Data Science and Machine Learning, Fall 2026, Dr. Md Moshiur Rahman Farazi
**Proposal:** submitted 28 Sep 2026, **Approved, 90/100** · **Presentation:** Sun 22 Nov 2026 · **Report due:** Thu 3 Dec 2026 (we submit Sun 29 Nov)

This file is the single index for the project: links, data facts, the cleaning and feature logs, results and deadlines.
New here? Read **[CONTRIBUTING.md](CONTRIBUTING.md)** (setup + who owns what), then **[SCHEDULE.md](SCHEDULE.md)** (your
tasks and checkpoints), **[DELIVERABLES.md](DELIVERABLES.md)** (everything we hand in, mapped to the rubrics) and
**[ALIGNMENT.md](ALIGNMENT.md)** (why each step exists: proposal feedback, proposal promises, lectures, rubrics).

**Research question** (rewritten after the proposal feedback, see ALIGNMENT §1):

> At the moment a Meituan order is placed, using only information known at that moment, how accurately can we
> predict its **delivery time** (minutes from order placement to arrival), and which order-time conditions
> drive long deliveries?

We predict the delivery time, not the delay. Delay (actual − platform promise) is only used to describe the
data and to score promises, including whether an 80th-percentile model gives fewer late orders than the
platform at the same average promised time.

---

## 1. Folder map

| Path | What it is |
|---|---|
| `proposal/DSAI5101_ProjectProposal.pdf` | **The submitted proposal (Meituan data).** `DSML Project.pdf` and `proj prosposal dsml.pdf` are earlier drafts on a Kaggle dataset we dropped |
| `requirements_rubric/` | Project guidelines + proposal, presentation and report rubrics |
| `common/` | Shared, tested pipeline: `config.py` (paths, dates, seed), `data.py` (download + cached table), `clean.py`, `features.py`, `split.py`, `evaluate.py` |
| `models/` | One file per model, all following one contract (see CONTRIBUTING §3) |
| `experiments/` | `run.py` (fit + score any model), `tune.py` (random search on CV), `compare.py` (paired bootstrap), `promise_test.py` (L4), `final.py` (every final result + report tables, L5/L6), `final_params/` (frozen settings, CP3) |
| `notebooks/` | Analysis notebooks, numbered (see `notebooks/README.md`) |
| `figures/` | Report-quality figures: `eda/` (Sumaiya), `results/` (Mahmoud) |
| `report/` | The IEEE report: `main.tex` + one file per section, `refs.bib`. Written here by PR; Lynn's Overleaf only builds the PDF (`report/README.md`) |
| `presentation/` | Slides (PDF export) + Q&A prep sheet |
| `results/runs/` | Scratch runs (git-ignored). `results/final/`: committed final runs (CP4) |
| `data/` | Raw CSV + cached table, **git-ignored** (licence forbids redistribution) |
| `tests/` | Offline tests: `python -m unittest -v` |

---

## 2. Links

| Item | Link |
|---|---|
| **Dataset:** Meituan INFORMS TSL Research Challenge (we use `all_waybill_info_meituan_0322.csv`) | https://github.com/meituan/Meituan-INFORMS-TSL-Research-Challenge |
| Dataset documentation: data report + Wang et al. (2025) data paper (PDFs in the repo above) | same repo, `tsl_meituan_2024_data_report_20241015.pdf` |
| Licence: CC BY-NC 4.0, non-commercial, **no redistribution**. Required acknowledgement in the report: *"This research was supported by data provided by Meituan."* | https://creativecommons.org/licenses/by-nc/4.0/ |
| IEEE conference template (Overleaf) | https://www.overleaf.com/latex/templates/ieee-conference-template/grfzhhncsfqn |
| scikit-learn: HistGradientBoosting, permutation importance | https://scikit-learn.org/stable/modules/ensemble.html#histogram-based-gradient-boosting |

---

## 3. Data facts (checked on the real file, 22 Oct 2026)

| Fact | Value |
|---|---|
| Raw rows (one per dispatch attempt) | 654,343 · 23 columns |
| Refused dispatch attempts (`is_courier_grabbed = 0`, all repeat an order) | 85,797 |
| Accepted orders (unique `order_id`) | 568,546; 568,545 with a target (1 has no arrival time) |
| Pre-booked orders | 22,181 (excluded from modelling, described separately) |
| Deliveries over 3 h | 4,097, of which **4,073 are pre-booked**. So excluding pre-bookings removes almost all extremes |
| **Modelling table** (accepted, not pre-booked, ≤ 3 h) | **546,340** orders: train 17–22 Oct **406,553**, test 23–24 Oct **139,787** |
| Districts / couriers / restaurants | 23 / 4,955 / 4,962 |
| Target `delivery_min` = arrive − order time | median 27.9, mean 29.6 (modelling rows), right-skewed |
| Platform promise `promise_min` | mean 37.8, **minimum 30.0**: a padded promise, not an unbiased ETA |
| Missing estimated prep time (stored as 0) | 9,874 orders |
| Prep "estimate" under 5 min (a system default) | 75,361 modelling orders (13.8%), treated as missing (C2b) |
| Days | 17 Oct 2022 = Monday. Weekend days: Sat 22 (train), Sun 23 (test) |
| Coordinates | stored as degrees × 1e6 and shifted for privacy. Distances are valid, locations aren't real |

> **Why the promise beats nobody on MAE.** The promise is padded (never under 30 min, mean 8 min above
> the actual time), so even the median predictor has lower MAE. Comparing ETA models with the promise on
> MAE alone is unfair. The fair test is the proposal's promise-setting comparison: our 80th-percentile
> model vs the promise **at the same mean promised time**, on late rate (L4).

---

## 4. Cleaning log (Sumaiya; feeds the report's Data section)

Every rule, with its reason. v0 rules are provisional and are confirmed or replaced at CP2 (S4).

| # | Rule | Rows affected | Reason | Status |
|---|---|---|---|---|
| C1 | Keep `is_courier_grabbed = 1` | −85,797 | Refused attempts repeat an order that someone else delivered | v0 |
| C2 | Timestamp 0 → missing | prep time 9,874; arrival 1 | 0 means "not recorded" | v0 |
| C2b | Prep estimate under 5 min → missing, flagged `prep_default` | 75,361 modelling orders (13.8%) | Not a real estimate: 74% equal the push time exactly (when the order enters the dispatch system, ~12 s after the order; 97% within 5 s, none equal the later dispatch time, so no leakage), and these orders are slower than ones with a real estimate at the same distance (`01_data_audit` §4). CV: Elastic-Net 6.93 → 6.70, HGB no change | v1 |
| C3 | Drop orders without arrival time | −1 | No target | v0 |
| C4 | Exclude pre-booked orders from modelling | −22,181 | Different population (Lec 3 tree): delivery time follows the slot the customer picked (`01_data_audit` §7). HGB CV MAE on normal orders 6.28, vs 6.76 with those under 3 h mixed in | final |
| C5 | Exclude delivery > 180 min | −24 after C4 | Implausible durations (max ≈ 7 days) | v0 — justify threshold from EDA |
| C6 | Missing prep time → training median (inside each model) | 82,800 modelling orders (stored 0 or default) | Fit on training rows only, so no leakage | v0 |
| C7 | After-order columns (dispatch, grab, fetch, courier, promise) never model inputs | n/a | Leakage: not known when the order is placed (Lec 6) | final |

**Feature log** (Sumaiya owns `features.py`; each row says why, with the lecture or feedback it answers)

| # | Feature | Why | Status |
|---|---|---|---|
| F1 | `dist_haversine_km` (alternative `dist_manhattan_km`) | Proposal: choose by validation MAE. **M3 (26 Oct):** HGB on full training data, CV MAE 6.284 vs 6.282 (Manhattan − Haversine −0.002 min, 95% CI −0.007 to +0.003, includes 0) → no real difference, keep Haversine (simpler, default). `base_manhattan` stays as the comparison set for the report | final |
| F2 | `prep_min`: estimated meal-ready time − order time | Known at placement (assumed); median-imputed in the pipeline; defaults are missing (C2b). Spearman 0.24 with delivery (`02_eda` §8) | v1 |
| F3 | `prep_missing` + `prep_default` flags | Orders without an estimate are 2–5 min slower at the same distance (`02_eda` §6, Lec 6) | v1 |
| F4 | `tod_sin`, `tod_cos` (time of day, cyclical) | 23:59 and 00:00 are close (Lec 6, **proposal feedback**) | final |
| F5 | `lunch_peak` (11 h), `dinner_peak` (17–19 h) | Proposal "meal peaks". Hours with a median above the overall median on training days (`02_eda` §9). Best of 4 options on CV: Elastic-Net −0.07 vs v0, HGB no change | v1 |
| F6 | `load_15m_rel`: orders in the same district in the last 15 min ÷ its 15-min average over the last 24 h (missing on day 1, flagged `load_missing`) | Proposal "district load". Backward-looking only (Lec 6). The raw count mostly measured area size and hour (`02_eda` §7). Best of 4 options on CV: vs raw count, Elastic-Net −0.021, HGB −0.009. The flag: day 1 is 49% of fit rows in CV fold 1; Elastic-Net −0.005 (95% CI −0.005 to −0.005), HGB no change. `load_15m` stays in the table for EDA | v1 |
| F7 | `district` one-hot (23 levels, unseen → zeros) | Nominal, low cardinality (Lec 6) | final |
| F8 | ~~`is_weekend`~~ **excluded** | One weekend day in training, none in CV folds 1–3. Scaling blew up on the Saturday fold (Elastic-Net fold-4 MAE 6.8 → 18.0). Weekend is described in EDA and stated as a limitation (**proposal feedback**: careful with 8 days) | final |
| F9 | `restaurant` (4,962 ids), `courier_id` **excluded** | Restaurant: high cardinality; target encoding only inside folds (Lec 6). Courier: assigned after the order (leakage) | final |

---

## 5. Results so far (v0, development only: CV on the training days)

| Run | CV MAE | Promise MAE (same rows) | Note |
|---|---|---|---|
| `median`, all training rows | 9.26 | 9.51 | do-nothing baseline (Lec 7) |
| `hgb` / `elasticnet` defaults, **features v1**, all training rows | 6.28 / 6.60 | 9.51 | vs v0 features: HGB −0.006, Elastic-Net −0.33 |
| **`elasticnet` tuned (L3, frozen features, 30 Oct)** | **6.59** | 9.51 | Raw target beats log (6.59 vs 6.73), so we keep the raw target. Best α ≈ 0.002 (little regularisation; 31 of 33 coefficients non-zero). Effects in min: distance **+6.1/km**, lunch peak +4.8, dinner peak +3.6, no real prep estimate +2.0 to +2.5, prep +0.66 per estimated min, load +1.1 per "1× usual", district spread 9.2. Frozen in `experiments/final_params/elasticnet.json` |
| **`hgb_q80` tuned (L4, frozen features, 30 Oct)** | 8.20 | 9.51 | Pinball 2.391 on CV (all 20 settings within 2.391–2.418: tuning barely matters). **Promise test** at the same mean promise (37.7 min): late after the promise 14.6% vs 14.9% (−0.3 pp, CI −0.5 to −0.2); late > 5 min 5.6% vs 4.8% (+0.8 pp); > 10 min 2.2% vs 1.4% (+0.8 pp); pinball 2.44 vs 2.32. Same story as v0, so robust: from order-time information we match the platform on ordinary lateness, but it is better at preventing *very* late orders (likely because it acts after the order: see the drop at exactly 8 min late, `02_eda` §5). Frozen in `experiments/final_params/hgb_q80.json` |
| **`hgb` tuned (M4, frozen features, 7 Nov)** | **6.25** | 9.51 | Best of 20 tries uses `loss=absolute_error` (we report MAE). vs defaults 6.28: CI −0.034 to −0.025. Training-vs-CV curve over leaves: CV best at 16 leaves (other settings default); at 511 leaves training 2.45 vs CV 6.63, i.e. overfitting (`figures/results/hgb_complexity_curve`). Frozen in `experiments/final_params/hgb.json` |
| **`rf` tuned (M4, frozen features, 7 Nov)** | 6.32 | 9.51 | HGB beats RF by 0.07 (CI excludes 0). HGB is 32.5% better than the median. Frozen in `experiments/final_params/rf.json` |
| Delay drivers (M5, grouped permutation importance on CV) | n/a | n/a | MAE increase when shuffled: distance +3.10 ≫ time of day +0.86 ≈ area +0.83 > prep +0.67 > load +0.19 (time + load together +1.43). The proposal was right on distance and peaks, wrong on load (`04_drivers`) |
| **Leakage audit (S5, frozen features + frozen settings, 11 Nov)**: `hgb` / `elasticnet` with `--features leaky` | **4.53 / 4.84** | 9.51 | Same tuned models (`experiments/final_params/`), plus three times known only after the order: dispatch, courier accepts (grab), pickup (fetch). MAE falls by 27–28%: HGB 6.25 → 4.53 (−1.72, 95% CI −1.74 to −1.71), Elastic-Net 6.60 → 4.84 (−1.76, CI −1.78 to −1.74); HGB R² 0.51 → 0.72. One time at a time (HGB): dispatch 5.86, grab 5.82, **pickup 4.55**, so almost the whole gap is the time from order to pickup. Partly by construction: all three are measured from the order and dispatch ≤ grab ≤ pickup for every order, so pickup contains the other two. It covers dispatch, the courier getting to the restaurant and waiting for the food; the data can't split the last two (S6). What's left (4.5 min) is road time and noise. Reproduced in `03_stages` §7. Never use these columns as inputs (C7) |
| Delivery stages (S6, training days, 11 Nov) | n/a | n/a | Pickup (order → pickup) and road (pickup → arrival) each take a median 13.1 min. After distance neither dominates: pickup holds 53% of the leftover variance, late orders lose 7.4 min at pickup and 8.2 on the road, and the frozen HGB's CV error variance splits pickup 51% / road 47% (partly by construction, since the stages add up to the target). Both stages take ~2.7 min longer at meal peaks. Late orders lose more on the road in the 7 big, longer-trip areas (72% of late orders) and at pickup in the other 16, and at pickup at night. Areas spread 5.0 min at pickup vs 4.3 on the road; areas 18 and 6 are fast at both, area 16 slow at both (`03_stages`) |
| Errors on CV (M6) | n/a | n/a | Lunch peak MAE 7.04 vs off-peak 5.76; area 16 worst at the same distance (`05_errors`). Test-day check follows CP4 |
| `elasticnet` v0 (α = 0.01), 50k sample | 6.92 | 9.50 | stable across folds (6.8–7.1) |
| `elasticnet` v0, log target, 50k sample | 7.15 | 9.50 | log is *worse* here: input for S3's skew decision |
| `rf` v0, 50k sample | 6.46 | 9.50 | |
| `hgb` v0 defaults, 100k sample | 6.32 | 9.48 | −32% vs median before any tuning |
| `hgb` Manhattan distance, 100k sample | 6.31 | 9.48 | distance choice barely matters (M3) |
| `hgb` with `--features leaky`, 50k sample | 4.67 | 9.50 | how much error is information we don't have at order time (S5) |

The rows above are development numbers; quote only the final ones below in the report.

### Final results: test days (CP4, scored once on 9 Nov, commit `5b36430`)

`python -m experiments.final --eval test --i-am-at-cp4`; full tables in `results/final/test/` and `report/tables/*_test.tex`.

| Model | MAE | RMSE | R² | vs median (95% CI) |
|---|---|---|---|---|
| Platform promise (as a prediction) | 9.62 | 11.87 | 0.05 | +0.16 [+0.11, +0.21] |
| Median predictor | 9.46 | 12.38 | −0.04 | n/a |
| Elastic-Net | 6.80 | 8.98 | 0.46 | −2.66 [−2.69, −2.62] |
| Random Forest | 6.54 | 8.67 | 0.49 | −2.92 [−2.95, −2.88] |
| **Gradient boosting** | **6.49** | 8.70 | 0.49 | **−2.97 [−3.00, −2.93]** (31% better) |

- **Best vs second best:** HGB − RF = −0.048 min [−0.056, −0.039] (`best_vs_second.json`). Real but tiny; RF has the lower RMSE, so HGB wins on typical error and RF on big misses.
- **Test vs CV:** every model is ~0.2 min worse on test than on CV (HGB 6.25 → 6.49), and the ranking is unchanged. Test day 23 Oct (Sunday, MAE 6.77) is harder than 24 Oct (Monday, 6.17): the weekend limitation (F8) showing up.
- **Promise test (q80, same mean promise 38.2 min):** late > 0 min 15.3% vs platform 14.9% (+0.3 pp [+0.2, +0.5]), > 5 min 6.1% vs 5.0% (+1.2 pp), > 10 min 2.4% vs 1.5% (+0.9 pp); pinball 2.52 vs 2.36; coverage 84.7% vs 85.1%. **On test the platform is slightly better at every threshold**; on CV we were 0.3 pp better at > 0 min. So the honest answer to the research question: order-time information predicts delivery time far better than the platform's promise does (MAE 6.49 vs 9.62), but it does not beat the platform at setting promises, which can react after the order is placed.


---

## 6. AI-use log (feeds the report's acknowledgement; add a row whenever you use an AI tool)

| Date | Who | Tool | What was asked | What we used / changed |
|---|---|---|---|---|
| 22 Oct | Lynn | Claude Code | Set up the shared pipeline (data loading, v0 cleaning, features, split, metrics, runner, tests) and the team docs; map the proposal feedback and lectures to tasks | Reviewed; all cleaning rules and model choices are owned and revised by the team |
| 10 Nov | Lynn | Claude Code | First drafts of the abstract, introduction, methodology and conclusion from the final results, and the Q&A prep sheet | Drafts only: Lynn rewrites and checks every number against `results/final/` before CP6 |

---

## 7. Deadlines

Team tasks (S1–S10, L1–L9, M1–M9, T1–T6) and checkpoints CP1–CP6 (95% done by **Sat 14 Nov**) are in [SCHEDULE.md](SCHEDULE.md).

| Stage | Date | Weight |
|---|---|---|
| Proposal | 28 Sep 2026 ✅ Approved, 90/100 | 5% |
| Presentation & Q&A (10 + 5 min, all speak) | **Sun 22 Nov 2026** | 10% |
| Final report (IEEE, 4–6 pages) + code + data link | Thu 3 Dec 2026 (we submit **Sun 29 Nov**) | 15% |

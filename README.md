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
| C4 | Exclude pre-booked orders from modelling | −22,181 | Different timing rules (proposal) | v0 |
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
| `elasticnet` v0 (α = 0.01), 50k sample | 6.92 | 9.50 | stable across folds (6.8–7.1) |
| `elasticnet` v0, log target, 50k sample | 7.15 | 9.50 | log is *worse* here: input for S3's skew decision |
| `rf` v0, 50k sample | 6.46 | 9.50 | |
| `hgb` v0 defaults, 100k sample | 6.32 | 9.48 | −32% vs median before any tuning |
| `hgb` Manhattan distance, 100k sample | 6.31 | 9.48 | distance choice barely matters (M3) |
| `hgb_q80` v0, all training rows | 8.29 | 9.51 | **Promise test (L4)** at the same mean promise (37.7 min): late after the promise 14.6% vs platform 14.9% (−0.3 pp, CI −0.4 to −0.2); late > 5 min 5.6% vs 4.8% (+0.8 pp). The platform is better at avoiding *very* late orders, the risk the proposal named. Untuned; rerun after CP2. `python -m experiments.promise_test results/runs/hgb_q80_base_cv` |
| `hgb` with `--features leaky`, 50k sample | 4.67 | 9.50 | how much error is information we don't have at order time (S5) |

Final numbers come from `results/final/` at CP4. Never quote these v0 numbers in the report.

---

## 6. AI-use log (feeds the report's acknowledgement; add a row whenever you use an AI tool)

| Date | Who | Tool | What was asked | What we used / changed |
|---|---|---|---|---|
| 22 Oct | Lynn | Claude Code | Set up the shared pipeline (data loading, v0 cleaning, features, split, metrics, runner, tests) and the team docs; map the proposal feedback and lectures to tasks | Reviewed; all cleaning rules and model choices are owned and revised by the team |

---

## 7. Deadlines

Team tasks (S1–S10, L1–L9, M1–M9, T1–T6) and checkpoints CP1–CP6 (95% done by **Sat 14 Nov**) are in [SCHEDULE.md](SCHEDULE.md).

| Stage | Date | Weight |
|---|---|---|
| Proposal | 28 Sep 2026 ✅ Approved, 90/100 | 5% |
| Presentation & Q&A (10 + 5 min, all speak) | **Sun 22 Nov 2026** | 10% |
| Final report (IEEE, 4–6 pages) + code + data link | Thu 3 Dec 2026 (we submit **Sun 29 Nov**) | 15% |

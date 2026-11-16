# Schedule, tasks and checkpoints

**We present on Sun 22 Nov** (not 29 Nov), so everything is planned backwards from that date.

**Goal: 95% of the project done by Sat 14 Nov.** By then all experiments, figures, the full report and the
slides exist and have been reviewed by everyone. What is left after 14 Nov is polishing, two rehearsals
and the final submission. The report is submitted **Sun 29 Nov**, four days before the 3 Dec deadline.

Each person owns separate files (see [CONTRIBUTING.md](CONTRIBUTING.md)), and every model, feature set and
metric already runs end to end on the real data. **Nobody waits for anyone**: until the cleaning is
frozen at CP2, everyone builds on the v0 cleaning. When it is frozen, the same commands simply give the final numbers.

Effort estimates are hands-on time. Tuning runs take longer, so start them and work on something else while they run.

Each task's tag in brackets says why it exists: **FB** = proposal feedback, **Lec n** = the lecture it
applies, **P** = promised in the proposal. Details and checklists are in [ALIGNMENT.md](ALIGNMENT.md).
The proposal was **approved (90/100)**. The feedback asked us to sharpen the question, *show* the cleaning in
the EDA, encode time carefully, fit only on training days, and plan what to cut. All of that is built in below.

---

## Timeline

| Checkpoint | Date | Where the team should be |
|---|---|---|
| Kick-off | Thu 22 Oct | Repo handed over; everyone sets up (30 min) |
| **CP0** | **Fri 23 Oct** | **Everyone set up**: proof posted in the group chat (no call) |
| **CP1** | **Sun 25 Oct** | Everyone set up and has run their own model on the full data; data audit numbers done; report skeleton in `report/` |
| **CP2** | **Thu 29 Oct** | **Cleaning + features frozen (v1)**; EDA v1; distance method chosen; 2 sources each in `refs.bib` |
| **CP3** | **Wed 4 Nov** | **All models tuned on CV and frozen**; leakage audit, stage analysis, importance, promise test done on CV |
| **CP4** | **Sun 8 Nov** | **All experiments final**: test set scored once, all tables and figures final, one script rebuilds everything |
| **CP5** | **Thu 12 Nov** (was Wed 11) | **Full report draft** (every section). Slides: Lynn builds the deck first, then sends it for everyone's parts |
| **CP6** | **Sat 14 Nov** → report sections Mon 16 Nov, review Tue 17 Nov | **95% done**: report and slides reviewed by all, rubric self-check, code checked on a fresh clone |
| (light) | 15–17 Nov | Fix review comments only (Lynn's AICC paper is due 17 Nov) |
| Slides ready | **Thu 19 Nov, night (max)** | Everyone's slides + speaker scripts in the deck (Lynn creates it 15 Nov) |
| Dry run | **Sat 21 Nov** | Call: full timed run-through (10 min) + 5-min mock Q&A; **slides locked** |
| **Presentation** | **Sun 22 Nov** | Group run-through before class (time TBC), then 10 min talk + 5 min Q&A, all three speak |
| Report polish | 23–28 Nov | Apply anything the Q&A exposed; final read |
| **Submit** | **Sun 29 Nov** | Report PDF + code link + data link on D2L (deadline Thu 3 Dec) |

**Integration time is built in.** CP3 → CP4 is the experiment integration window (final runs, one
reproducible script, shared figure style). CP4 → CP5 is writing, and CP5 → CP6 is review. 15–21 Nov is buffer.

**Replanned 10 Nov** (sent in the group chat): the overdue analysis (S5, S6, S8, M6) is due **Wed 11 Nov, 10 pm**; all report sections (S9, M8, L7) **Thu 12 Nov, 10 pm**; CP6 stays Sat 14 Nov. The test days were scored once by Lynn on 9 Nov (L5), so nobody reruns `--eval test`.

**Daily update** in the group chat, every day by 10 pm (three lines, even if nothing changed):
```
✅ Done today:   (task IDs)
🚧 Blocked on:
➡️ Tomorrow:     (task IDs)
```
Blocked? Message **immediately**. Don't wait for the evening.

**Checkpoint call (15 min):** each person shows the tasks due (a command that runs, a `summary.json`,
a figure, a draft section), and we agree on the focus until the next checkpoint. Done means finished, not started.

---

## Tasks

### Sumaiya: data audit, cleaning, EDA, leakage audit, stage analysis
Owns `common/clean.py`, `common/features.py`, `notebooks/01_*`–`03_*`, `figures/eda/`.

| ID | Task | Effort | Due |
|---|---|---|---|
| S1 | Setup: clone, venv, `python -m unittest` passes, `python -m experiments.run --model median` works; post the four commands (`shape`, `info`, `describe`, `isna().sum()`) on the raw file [Lec 3] | 30 min | **CP0** |
| S2 | `notebooks/01_data_audit.ipynb`: the four commands; **data dictionary** (every column: meaning, units, valid range, issues); quantify every quirk (refused dispatches, zeros per column, pre-booked, durations > 3 h, missing prep time, coordinate ranges, timestamp-order checks) as **one before → after table** for the report [FB2, Lec 2–3] | 3–4 h | **CP1** |
| S3 | `notebooks/02_eda.ipynb`: target centre/spread/shape + log decision (v0 CV says log is *worse* for Elastic-Net), delivery time vs distance / hour / load (Spearman), **Simpson check within districts**, delay (actual − promise) by district and hour, missing-prep rows vs complete rows. **Each figure: a title stating the finding + which modelling choice it informs** [FB2, P, Lec 3–5] | 5–6 h | **CP2** |
| S4 | Cleaning + features v1: replace the v0 rules in `clean.py` with justified ones (outlier decision tree from Lec 3), add features EDA suggests (any restaurant-level feature must be computed inside CV folds, Lec 6), log each rule in README §4 → **freeze** [FB2, P] | 3–4 h | **CP2** |
| S5 | ✅ **Done 11 Nov** (frozen models: HGB 6.25 → 4.53; README §5, `03_stages` §7). Leakage audit: same model with `--features leaky` vs `base` (v0: MAE 4.7 vs 6.3); explain the gap as information not available at order time [P, Lec 6–7] | 1–2 h | **Wed 11 Nov** (was CP3) |
| S6 | ✅ **Done 11 Nov** (README §5, `03_stages` §1–6). `notebooks/03_stages.ipynb`: restaurant wait (`fetch_min`) vs road time (`delivery_min − fetch_min`): which stage drives delay, and where (hour, district) [P] | 3 h | **Wed 11 Nov** (was CP3) |
| S7 | ✅ **Done 6 Nov** (`01_data_audit` §7, C4). Pre-booked orders: short separate description (why excluded: a "different population" in Lec 3's outlier tree) [P] | 1 h | **CP3** |
| S8 | ✅ **Done 11 Nov** (all `figures/eda/` figures checked against Lec 5 and reworked to the agreed plan: 5 for the report, 4 for slides, 3 for backup; analysis on training days). Final EDA + stage figures at report quality, checked against the Lec 5 figure checklist (ALIGNMENT §5) [FB2, Lec 5] | 2 h | **Wed 11 Nov** (was CP4) |
| S9 | Report: Data & EDA section (each problem → how it was handled → the figure/table showing it) + Related Work section (≥ 5 sources, compared, merges everyone's) [FB2, rubric] | 5 h | **Mon 16 Nov** (was Thu 12) |
| S10 | Slides: data, cleaning, EDA findings (~3 min), in Lynn's deck once it is sent | 1.5 h | after Lynn's deck |

### Lynn (lead): baselines, Elastic-Net, promise-setting test, integration
Owns `models/baselines.py`, `models/linear.py`, `models/promise.py`, `experiments/`, `report/`.

| ID | Task | Effort | Due |
|---|---|---|---|
| L1 | Hand over: GitHub repo, add Sumaiya and Mahmoud, fill `.github/CODEOWNERS` | 30 min | **CP0** |
| L2 | IEEE two-column report skeleton in `report/`, one file per section; Lynn's Overleaf builds the PDF (sections come in by PR, see `report/README.md`) ✅ | 1 h | **CP1** |
| L3 | ✅ **Done 30 Oct** (CV 6.59, raw target; see README §5). Elastic-Net: tune with `experiments.tune`, raw vs log target, interpret coefficients (the interpretable end of Lec 1's prediction/inference trade-off) [P, Lec 7] | 3 h | **CP3** |
| L4 | ✅ **Done 30 Oct** (tuned + promise test on frozen features; README §5). Promise test (`experiments/promise_test.py`): tune `hgb_q80`; shift its predictions so the mean promised time equals the platform's, then compare late rate, pinball loss, coverage; vary the late threshold (5 / 10 min) [P, Lec 2 business evaluation] | 4–5 h | **CP3** |
| L5 | ✅ **Done 9 Nov** (test scored once, README §5). `experiments/final.py`: one command reruns every final model on test into `results/final/` and writes the report tables. **Code done 23 Oct**; at CP4: freeze params in `experiments/final_params/`, run with `--eval test --i-am-at-cp4` | 3 h → 30 min | **CP4** |
| L6 | ✅ **Done 9 Nov** (HGB vs RF −0.048 [−0.056, −0.039]). Bootstrap table: every model vs median and vs promise (**built into `final.py`, done 23 Oct**); add best vs second best with `experiments.compare` | 1 h → 15 min | **CP4** |
| L7 | ⏳ **First draft in `report/` 10 Nov** (Lynn to revise; add S5/S6 numbers to the conclusion once merged). Report: abstract, introduction (**the research question as one sentence**, T/P/E, success criteria, contributions), methodology (numbered steps + one table, not dense prose), conclusion (limitations incl. weekend, ethics, monitoring/drift) [FB1, FB4, Lec 1–2] | 6 h | **Thu 12 Nov** |
| L8 | Slide template; problem + research question in the first minute, methods, promise test (~3.5 min); one idea per slide; assemble the deck [FB1, FB4]. Lynn builds the whole deck first, then sends it for everyone's parts | 2 h → more | **Thu 12 Nov** (first version) |
| L9 | ⏳ **References + acknowledgements drafted 10 Nov** (dataset, pandas, NumPy cited; code/data/AI statements in `main.tex`); left: invite the instructor to the repo, final AI-use check, submit. References + AI-use acknowledgement + Meituan data acknowledgement; submit on D2L | 2 h | Sun 29 Nov |

### Mahmoud: boosting, Random Forest, tuning, distance comparison, delay drivers, error analysis
Owns `models/boosting.py`, `models/forest.py`, `notebooks/04_*`–`05_*`, `figures/results/`.

| ID | Task | Effort | Due |
|---|---|---|---|
| M1 | Setup (tests + median as S1); post one `python -m experiments.run --model hgb --sample 100000` result | 30 min | **CP0** |
| M2 | Boosting + RF on the full training data; decide HistGradientBoosting vs LightGBM [P] | 2 h | **CP1** |
| M3 | Distance comparison: `--features base` vs `base_manhattan`, same model, CV MAE + bootstrap (v0: 6.32 vs 6.31, so the bootstrap decides) → pick one, tell Sumaiya [P] | 1 h | **CP2** |
| M4 | ✅ **Done 7 Nov** (HGB 6.25, RF 6.32; frozen). Tune HGB (incl. `loss=absolute_error`, since we report MAE) and RF with `experiments.tune` on the frozen features (start after CP2) + **one training-vs-CV error curve** over a complexity setting for the report [P, Lec 7] | 3 h + run time | **CP3** |
| M5 | ✅ **Done 7 Nov** (README §5). `notebooks/04_drivers.ipynb`: grouped permutation importance (distance, prep, time, load, district) on CV folds, with spread → ranked delay drivers. Check the proposal's expectation (distance, peaks, load on top) and say if it held [P] | 3 h | **CP3** |
| M6 | ✅ **Done 15 Nov** (PR #9, test-day errors). `notebooks/05_errors.ipynb`: errors by district / hour / distance / day, worst orders, residual plots, do errors rise at meal peaks (proposal expectation)? Does it hold on the test days? [P, Lec 2 subgroup evaluation] | 3 h | **Mon 16 Nov** (was CP4; CV part done 7 Nov) |
| M7 | ✅ **Done 15 Nov** (PR #9). Test-day results for HGB and RF: Lynn ran the single test run on 9 Nov (L5, all models together); Mahmoud uses `results/final/test/hgb/predictions.parquet` (sent directly, not in git) for M6. Do not rerun `--eval test` | 1 h | **Mon 16 Nov** (was Wed 11) |
| M8 | ✅ **Done 15 Nov** (PR #9; merged 16 Nov). Report: Results & Discussion section (final tables already wired into `results.tex`) | 5 h | **Mon 16 Nov** (was Thu 12) |
| M9 | Slides: results, delay drivers, limitations (~3.5 min), in Lynn's deck once it is sent | 1.5 h | after Lynn's deck |

### Everyone
| ID | Task | Due |
|---|---|---|
| T1 | 2 scholarly sources each (ETA / delivery-time prediction, Meituan data, quantile or promise-setting) in `report/refs.bib` with 2 lines on how they relate to us. The rubric needs ≥ 5, compared | **CP2** |
| T2 | Read [ALIGNMENT.md](ALIGNMENT.md): the new research question, how the proposal feedback is handled, and the lecture checklists for your tasks | **CP1** |
| T3 | Read the whole report draft and comment on every section | **CP6** |
| T4 | Rubric self-check: Sumaiya on the Report rubric, Mahmoud on the Presentation rubric, Lynn on the Info checklist (§6) | **CP6** |
| T5 | ✅ **Done 15 Nov** (Mahmoud: 19 tests OK, same CV numbers). Fresh-clone test: follow README in a new folder, run the tests and the final script (Mahmoud) | **CP6** |
| T6 | Be able to explain the **whole** project (Q&A questions can go to anyone) | Dry run Sat 21 + run-through Sun 22 Nov (use `presentation/qa_prep.md`) |

### Instructor feedback (16 Nov)

Presentation-relevant items are due **Thu 19 Nov** so they can go into the slides; report-only items by
**Mon 23 Nov**. First check (16 Nov, Lynn): subtracting the platform's average padding (8.20 min, learned
on the training days only) makes its promise as accurate as our model on the test days (MAE 6.48 vs
6.49, difference +0.02, CI [−0.01, +0.04]). We are better on CV (3 of 4 folds), on trips under 1 km
(5.61 vs 6.10) and over 3 km (8.73 vs 10.06), partly because padding is not constant; the platform is better on
1–3 km and at lunch (6.69 vs 7.22). So "3.1 min better than the promise" is all padding: the headline must change.

| ID | Feedback | What we do | Owner | Due |
|---|---|---|---|---|
| F1 | ✅ **Done 16 Nov** (`day_profiles`, results.tex). Weekday encoding: is `is_weekend` needed, do weekend and weekday patterns differ, or is it just time of day? | EDA: hourly delivery-time profile per day (8 lines) + weekday vs weekend; daily medians 27.2–29.0, weekend 1–3.5 min slower noon–18:00. Keep the fold-4 reason for dropping the flag; add day-of-week only if the profiles differ in shape | Lynn | Thu 19 |
| F2 | ✅ **Done 16 Nov** (CV −0.29, `partial_dependence`). More features (feature engineering), more explainable | Candidate features (rider availability F3, restaurant history computed inside folds, day of week) on CV; explainability: partial dependence for distance, hour and load + Elastic-Net coefficients in minutes | Lynn | Thu 19 |
| F3 | ✅ **Done 16 Nov** (`rider_pressure`, riders feature). Rider availability per district, high or low (e.g. > 10 riders free → capacity high) → feature | District × time matrix of riders active in the previous 30 min, using **only events finished before the order** (leakage-safe), heatmap + `riders_30m` and orders-per-rider features | Lynn | Thu 19 |
| F4 | ✅ **Done 16 Nov** (tie 6.49 vs 6.48, `depadded_test.tex`). Compare padded with padded, unpadded with unpadded; share of trips < 1 km and > 3 km; show our model on its own, not only vs the app | Padded: q80 vs promise (done). Unpadded: our estimate vs the promise minus its average padding (above). Trip shares: < 1 km 30.0%, 1–3 km 62.8%, > 3 km 7.2%. Standalone: MAE, coverage and error by segment for our model alone | Lynn | Thu 19 |
| F5 | ✅ **Table done 16 Nov** (`report/tables/data_issues.tex`; `\input` it in data.tex once S9 is merged). % duplicates, missing values etc., with why we did what we did | One table in `data.tex`: each issue, count, % of rows, decision, reason (from `01_data_audit`) | Lynn | Mon 23 (table goes in `data.tex`) |
| F6 | ✅ **Done 16 Nov** (Mondays differ 0.5 min per busy hour). Same weekday over time: is the pattern drifting, or can we assume other days look the same? | Monday 17 vs Monday 24 (a week apart): median 27.45 vs 27.48 (modelling orders), so stable; add the hourly overlay to the F1 figure and one sentence on drift | Lynn | Thu 19 |
| F7 | ✅ **Table done 16 Nov** (`report/tables/benchmark.tex`; `\input` it in related.tex once S9 is merged). Benchmarking (optional): how industry does this, state of the art | Small table in Related Work: published ETA systems (e.g. Meituan, Ele.me, DoorDash, Uber), their inputs and reported error, with a note that numbers are not directly comparable across datasets | Lynn | Mon 23 |
| F8 | ✅ **Done 16 Nov** (`python -m experiments.reproduce`). Reproducibility: one command that runs every notebook and regenerates everything | `python -m experiments.reproduce`: tests → `experiments.final` (CV) → all notebooks executed → slide figures; README §2 updated | Lynn | Tue 17 |

**Decided 16 Nov:** new features (F2/F3) are a **CV-only extension**. The frozen models and the single
test run (9 Nov) stay the main results; the report gives the new features' CV gain separately, so the
test days are never looked at twice. Lynn does all of F1–F8; Sumaiya's and Mahmoud's remaining tasks are
unchanged.

---

## Checkpoint checklists

**CP0 · Fri 23 Oct (in the chat, by 10 pm):** S1 · L1 · M1. Each person posts a screenshot of
`python -m unittest` (17 tests OK) and `python -m experiments.run --model median` (MAE 9.26), plus the
extra output in their task. Stuck on setup? Say so in the chat right away. Don't wait until Sunday.
**CP1 · Sun 25 Oct:** S2 · L2 · M2 · T2
**CP2 · Thu 29 Oct:** S3 S4 (freeze) · M3 · T1
**CP3 · Wed 4 Nov:** S5 S6 S7 · L3 L4 · M4 M5 (models frozen)
**CP4 · Sun 8 Nov:** S8 · L5 L6 · M6 M7 (all experiments final)
**Wed 11 Nov (catch-up):** S5 S6 S8 · M6 M7

**CP5 · Thu 12 Nov:** S9 · L7 L8 · M8 (full report draft; slides S10/M9 once Lynn's deck is out)
**CP6 · Sat 14 Nov:** T3 T4 T5 (95% done)

If a task slips, say so at the checkpoint and **cut scope rather than move the date**, in the order agreed
in [ALIGNMENT.md §6](ALIGNMENT.md) (the feedback asked what we'd cut first). For example, keep the
v0 cleaning rules if S4 is late, tune fewer iterations, or drop the 10-min threshold variant.
The two freezes (features at CP2, models at CP3) are the only points where one person's work feeds
another's, and both have a working fallback.

# Team guide: start here

The shared pipeline already works and is tested on the real data: download, v0 cleaning, features,
the time split, every model (v0), the runner, the tuner, the bootstrap comparison and all metrics.
You only build and improve your own part.

## 1. One-time setup (Windows, cmd)

```bat
git clone https://github.com/lynn60107070/dsai5101-delivery-eta.git
cd dsai5101-delivery-eta
py -3.12 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Check that everything works (offline, about 5 s, no data needed):

```bat
python -m unittest -v
```

All 14 tests must pass. They also prove two things the proposal feedback asked about: time of day is
encoded cyclically, and fitted steps (imputer, scaler, encoder) only ever learn from training days. Then run the median baseline on the real data. The first run downloads the
dataset (39 MB) into `data/raw/` and builds the cached table in `data/processed/` (about 1 min):

```bat
python -m experiments.run --model median
```

You should see `MAE 9.26 ... | promise MAE 9.51`. If you do, you're set up.

> **Never commit or share the CSV.** The data is CC BY-NC 4.0 and may not be redistributed, so
> `data/` is git-ignored. Everyone downloads it from Meituan's GitHub (the code does this for you).

## 2. Who owns what

You edit only the files you own. To change someone else's file, ask them or open a PR they review.

| Owner | Files | Job |
|---|---|---|
| **Sumaiya** | `common/clean.py`, `common/features.py`, `notebooks/01_*` `02_*` `03_*`, `figures/eda/` | Data audit, cleaning rules, EDA, leakage audit, stage analysis |
| **Lynn** (lead) | `models/baselines.py`, `models/linear.py`, `models/promise.py`, `experiments/`, `notebooks/06_*`, `report/` | Baselines, Elastic-Net, promise-setting test, final script, report assembly |
| **Mahmoud** | `models/boosting.py`, `models/forest.py`, `notebooks/04_*` `05_*`, `figures/results/` | Boosting, Random Forest, tuning, distance comparison, delay drivers, error analysis |
| **Everyone** | `common/config.py`, `common/split.py`, `common/evaluate.py`, `models/__init__.py` | Change only when all three agree |

Tasks and deadlines: **[SCHEDULE.md](SCHEDULE.md)**. Everything we must hand in: **[DELIVERABLES.md](DELIVERABLES.md)**.
Why each step exists (proposal feedback, proposal promises, lecture checklists): **[ALIGNMENT.md](ALIGNMENT.md)**.

## 3. How the pieces fit (why nobody waits for anyone)

```
data/raw CSV ──clean.py──► one row per accepted order ──features.py──► cached table
                (Sumaiya)                                 (Sumaiya)        │
                                                                           ▼
                        split.py: train 17–22 Oct (4 forward-chaining CV folds) │ test 23–24 Oct
                                                                           │
   models/*.py  make(fs, seed, **params) -> sklearn estimator   ◄──────────┤  (Lynn, Mahmoud)
                                                                           ▼
   experiments/run.py ──► results/runs/<name>/predictions.parquet + summary.json (evaluate.py)
```

- **The table's columns are the contract** (listed at the top of `common/clean.py`). Sumaiya can
  change the cleaning rules freely. As long as the columns stay, every model keeps working.
- **Feature sets** (`common/features.py`) decide which columns models see. Models never choose
  columns themselves, so a new feature reaches every model at once.
- **The cache rebuilds itself.** Its key is a hash of `clean.py` and `features.py`, so when
  Sumaiya pushes new rules, your next run uses them automatically.

### The model contract

```python
def make(fs: FeatureSet, seed: int, **params) -> sklearn estimator   # unfitted
SEARCH_SPACE = {"param": [values] or scipy distribution}             # used by experiments.tune
```

Put the preprocessing inside the estimator (`common.features.preprocessor(fs)`) so that imputation
and scaling are fit on the training rows of each fold only. Register new models in `models/__init__.py`.

## 4. Running experiments

```bat
:: development: a random subset of training rows, scored on the 4 CV folds
python -m experiments.run --model hgb --sample 100000
python -m experiments.run --model elasticnet --param alpha=0.05 --log-target
python -m experiments.run --model hgb --features base_manhattan          :: distance comparison
python -m experiments.run --model hgb --features leaky                  :: leakage audit only

:: tuning: random search, scored by mean CV MAE (pinball loss for hgb_q80)
python -m experiments.tune --model hgb --n-iter 20 --sample 150000
python -m experiments.run --model hgb --params-from results\tuning\hgb_base.json

:: is A really better than B? paired bootstrap on the same orders
python -m experiments.compare results\runs\hgb_base_cv results\runs\median_base_cv
python -m experiments.compare results\runs\hgb_base_cv promise
```

- Outputs go to `results/runs/<name>/`: `predictions.parquet` (one row per scored order: y, pred,
  promise, district, hour, day, distance) and `summary.json` (MAE, RMSE, R², late rate, pinball,
  coverage, the platform promise on the same rows, errors by district / hour / distance / day, per-fold MAE).
- `results/runs/` is scratch space and git-ignored. Results that go in the report are produced at CP4
  into `results/final/` and committed.
- Your notebooks can load any run with `pd.read_parquet(...)` for plots. There's no need to refit.
- The seed is fixed (`common/config.py`, 42) everywhere.

## 5. Rules that protect our marks

1. **Choose everything on CV, never on the test days.** Tuning, distance method, log target and
   features are all decided with `--eval cv`. `--eval test` is run **once per final model at CP4**
   (Lec 1, Lec 7: once the test set influences a decision, it is no longer a fair estimate).
2. **No leakage.** Model inputs only use information known when the order is placed. Never add
   `promise_min`, `courier_id`, `dispatch_min`, `grab_min`, `fetch_min` or anything derived from them
   to a non-leaky feature set. A unit test checks this. Ask Lec 6's question for every feature:
   "would I have this value at the moment I need to predict?"
3. **Anything fitted lives inside the pipeline** (imputers, scalers, encoders, target encodings), so it is
   learned from the fit days of each fold only (proposal feedback, Lec 2, Lec 6). No `fit` on the whole table, ever.
4. **Every cleaning rule and feature has a reason**, logged in README §4. The tables become the report's
   Data and Methodology paragraphs, and **the EDA must show each problem being handled** (proposal feedback).
5. **Every figure makes one point**, its title states the finding, and it says which choice it informed
   (rubric top band; checklist in ALIGNMENT §5, from Lec 5).
6. **Report negative results honestly.** "The promise beats us on X because…" is a good result (Guidelines §7).
7. **Log AI use** as you go (tool, what you asked, what you used) in README §6. The report must acknowledge it.

## 6. Git workflow

1. Work on your own branch: `sumaiya/data`, `lynn/models`, `mahmoud/models`.
2. Pull `main` into your branch often: `git pull origin main`.
3. Run `python -m unittest` before every pull request.
4. Open a PR into `main`. Another teammate reviews it before merging. Reviewing also prepares you
   for the Q&A, where anyone can be asked about any part.
5. Never commit `data/` or large model files. Notebooks: clear huge outputs before committing.

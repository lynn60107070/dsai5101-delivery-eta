# Notebooks

Numbered in the order they should run. Each one loads the shared table (`from common.data import load_table`)
or saved runs (`pd.read_parquet("../results/runs/<name>/predictions.parquet")`). Don't fit models
in notebooks, use `experiments.run` so everyone's numbers are computed the same way. Exception: `03_stages`
refits the frozen HGB and Elastic-Net (settings from `experiments/final_params/`, same CV folds) for S5, because the
one-at-a-time leaky sets aren't in the frozen `features.py`, and for §4 when `results/final/cv/hgb/` has no saved
predictions (`python -m experiments.final` writes them).

Start every notebook with:
```python
import sys; sys.path.insert(0, "..")   # so `common` imports work from notebooks/
from common.data import load_table
```

| Notebook | Owner | Task | Saves figures to |
|---|---|---|---|
| `01_data_audit.ipynb` | Sumaiya | S2, S7 | `figures/eda/` |
| `02_eda.ipynb` | Sumaiya | S3 | `figures/eda/` |
| `03_stages.ipynb` | Sumaiya | S5, S6 | `figures/eda/` |
| `04_drivers.ipynb` | Mahmoud | M3, M5 | `figures/results/` |
| `05_errors.ipynb` | Mahmoud | M6 | `figures/results/` |
| `06_promise.ipynb` | Lynn | L3, L4 | `figures/results/` |

Every notebook must run top to bottom (Guidelines §6, Lec 1 "reproducibility is part of the method")
and end with a **written conclusion in sentences with numbers** that says what changes next (Lec 3: "prose,
with numbers, that changes what you do next"). Use the lecture checklists in `../ALIGNMENT.md` §5.

Figures: save as PDF (vector, for LaTeX) at a width of 3.5 in (one IEEE column), with a filename that says
what it shows (`delivery_vs_distance.pdf`, not `fig3.pdf`). Lec 5 rules: title states the finding, axes
labelled with units, hours in chronological order, viridis or colour-blind-safe colours, no pies, dual axes or area encodings.
Before committing, clear outputs that are larger than a few MB.

"""One command that rebuilds every result, table, figure and notebook (owner: Lynn, instructor feedback F8).

    python -m experiments.reproduce            # everything below, about 30-40 min on a laptop
    python -m experiments.reproduce --tune     # also rerun the hyperparameter searches first (adds about 1-2 h)
    python -m experiments.reproduce --skip-notebooks

Steps, in order (each one stops the run if it fails):
    1. unit tests
    2. data: download the raw CSV if missing, build the cached table           (common/data.py)
    3. [--tune] random searches for every model                                 (experiments.tune -> results/tuning/)
    4. final models on the CV folds, report tables                              (experiments.final)
    5. fair comparison, day profiles, data-issue table                          (experiments.feedback)
    6. extra features + explainability, CV only                                (experiments.extension)
    7. slide figures                                                            (experiments.slide_figures)
    8. every notebook, executed top to bottom in place                          (notebooks/*.ipynb)

The test days are never re-scored: their predictions were written once on 9 Nov
(`python -m experiments.final --eval test --i-am-at-cp4`) and every step above only reads them.
"""

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

from common.config import REPO_ROOT

NOTEBOOKS = ["01_data_audit", "02_eda", "03_stages", "04_drivers", "04_tuning", "05_errors"]
# the searches behind experiments/final_params/ (same settings as recorded in each params file)
TUNING = [["--model", "elasticnet", "--n-iter", "30"],
          ["--model", "hgb", "--n-iter", "20", "--sample", "150000"],
          ["--model", "rf", "--n-iter", "10", "--sample", "100000"],
          ["--model", "hgb_q80", "--n-iter", "20", "--sample", "150000"]]


def step(title: str, cmd: list[str], env=None) -> None:
    print(f"\n=== {title}\n$ {' '.join(cmd)}", flush=True)
    start = time.time()
    subprocess.run(cmd, cwd=REPO_ROOT, check=True, env=env)
    print(f"--- done in {time.time() - start:.0f} s", flush=True)


def kernel_env(tmp: Path) -> dict:
    """Notebooks run with this same Python, whatever kernels the machine has installed."""
    spec = tmp / "kernels" / "python3"
    spec.mkdir(parents=True)
    (spec / "kernel.json").write_text(json.dumps({
        "argv": [sys.executable, "-m", "ipykernel_launcher", "-f", "{connection_file}"],
        "display_name": "Python 3", "language": "python"}), encoding="utf8")
    return {**os.environ, "JUPYTER_PATH": str(tmp)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tune", action="store_true", help="rerun the hyperparameter searches first (slow)")
    ap.add_argument("--skip-notebooks", action="store_true")
    args = ap.parse_args(argv)
    py = sys.executable

    step("1. unit tests", [py, "-m", "unittest"])
    step("2. data", [py, "-c", "from common.data import load_table; print(len(load_table()), 'modelling orders')"])
    if args.tune:
        for flags in TUNING:
            step(f"3. tuning {flags[1]}", [py, "-m", "experiments.tune", *flags])
    step("4. final models on the CV folds", [py, "-m", "experiments.final"])
    step("5. fair comparison, day profiles, data issues", [py, "-m", "experiments.feedback"])
    step("6. extra features + explainability (CV only)", [py, "-m", "experiments.extension"])
    step("7. slide figures", [py, "-m", "experiments.slide_figures"])
    if not args.skip_notebooks:
        with tempfile.TemporaryDirectory() as tmp:
            env = kernel_env(Path(tmp))
            for nb in NOTEBOOKS:
                step(f"8. notebook {nb}", [py, "-m", "jupyter", "nbconvert", "--to", "notebook", "--execute",
                                           "--inplace", "--ExecutePreprocessor.timeout=-1",
                                           f"notebooks/{nb}.ipynb"], env=env)
    print("\nAll results, tables, figures and notebooks rebuilt. Check `git status` for what changed.")


if __name__ == "__main__":
    main()

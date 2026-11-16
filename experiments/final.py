"""Every final result in the report, from one command (owner: Lynn, tasks L5 + L6).

    python -m experiments.final                      # CV on the training days: check the plumbing any time
    python -m experiments.final --eval test --i-am-at-cp4     # CP4 ONLY: scores the test days, once

Fits each final model with its frozen settings (experiments/final_params/<model>.json, committed at CP3),
then writes, under results/final/<eval>/:
    <model>/predictions.parquet, <model>/summary.json     one folder per model
    tables.md                                              all tables, readable
    manifest.json                                          git commit, data version, settings: every number traceable
and for the report: report/tables/main_results_<eval>.tex, report/tables/promise_test_<eval>.tex,
figures/promise/final_<eval>_gap.pdf.

Test days are used once (Lec 1, Lec 7): the test mode refuses to run without --i-am-at-cp4.
"""

import argparse
import json
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from common import split
from common.config import REPO_ROOT, RESULTS, SEED
from common.data import _cache_key, load_table
from common.evaluate import paired_bootstrap, point_metrics, summarize
from common.features import FEATURE_SETS
from experiments import promise_test
from experiments.run import _scored, cross_validate, fit_predict

PARAMS_DIR = REPO_ROOT / "experiments" / "final_params"
TABLES_DIR = REPO_ROOT / "report" / "tables"
FIGURES_DIR = REPO_ROOT / "figures" / "promise"

FEATURES = "base"  # set to the distance chosen in M3 (base or base_manhattan) at CP2

# The final line-up. log_target comes from the S3/L3 decision; params from final_params/ (frozen at CP3).
FINAL_MODELS = [
    {"model": "median", "label": "Median predictor", "log_target": False},
    {"model": "elasticnet", "label": "Elastic-Net", "log_target": False},
    {"model": "rf", "label": "Random Forest", "log_target": False},
    {"model": "hgb", "label": "Gradient boosting", "log_target": False},
    {"model": "hgb_q80", "label": "Gradient boosting, q80", "log_target": False},  # promise test only
]
POINT_MODELS = ["median", "elasticnet", "rf", "hgb"]  # compared on MAE; q80 targets a quantile instead


def frozen_params(model: str) -> tuple[dict, str]:
    path = PARAMS_DIR / f"{model}.json"
    if not path.exists():
        return {}, "defaults (no frozen params file)"
    return json.loads(path.read_text(encoding="utf8"))["params"], str(path.relative_to(REPO_ROOT))


def git_commit() -> str:
    try:
        out = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True)
        dirty = subprocess.run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=REPO_ROOT, capture_output=True, text=True).stdout
        return out.stdout.strip() + ("+uncommitted" if dirty.strip() else "")
    except OSError:
        return "unknown"


def comparison_table(preds: dict) -> pd.DataFrame:
    """Point models + the platform promise on the same orders, each vs the median and vs the promise."""
    base = preds["median"]
    rows = []
    entries = [("promise", "Platform promise", base.assign(pred=base["promise"]))] + \
              [(m, next(f["label"] for f in FINAL_MODELS if f["model"] == m), preds[m]) for m in POINT_MODELS]
    abs_median = (base["y"] - base["pred"]).abs().to_numpy()
    abs_promise = (base["y"] - base["promise"]).abs().to_numpy()
    for key, label, p in entries:
        m = point_metrics(p["y"], p["pred"])
        err = (p["y"] - p["pred"]).abs().to_numpy()
        vs_median = paired_bootstrap(err, abs_median) if key != "median" else None
        vs_promise = paired_bootstrap(err, abs_promise) if key != "promise" else None
        rows.append({
            "key": key, "Model": label, "MAE": m["mae"], "RMSE": m["rmse"], "R2": m["r2"],
            "Late > 5 min": m["late_rate"],
            "dMAE vs median": vs_median["diff"] if vs_median else np.nan,
            "CI vs median": vs_median["ci95"] if vs_median else None,
            "% vs median": 100 * vs_median["diff"] / vs_median["mae_b"] if vs_median else np.nan,
            "dMAE vs promise": vs_promise["diff"] if vs_promise else np.nan,
            "CI vs promise": vs_promise["ci95"] if vs_promise else None,
        })
    return pd.DataFrame(rows)


def _ci(diff, ci) -> str:
    return "--" if ci is None else f"{diff:+.2f} [{ci[0]:+.2f}, {ci[1]:+.2f}]"


def main_results_latex(table: pd.DataFrame, eval_name: str) -> str:
    lines = [r"\begin{table*}[t]", r"\centering",
             r"\caption{Delivery-time prediction on the " + ("test days (23--24 Oct)" if eval_name == "test" else
                                                             "forward-chaining CV folds (17--22 Oct)") +
             r". $\Delta$MAE in minutes with 95\% paired bootstrap intervals; negative = lower error.}",
             r"\label{tab:main_results" + ("" if eval_name == "test" else "_cv") + "}",
             r"\begin{tabular}{lrrrrll}", r"\toprule",
             r"Model & MAE & RMSE & $R^2$ & Late $>$5 min & $\Delta$MAE vs median & $\Delta$MAE vs promise \\",
             r"\midrule"]
    for _, r in table.iterrows():
        lines.append(f"{r['Model']} & {r['MAE']:.2f} & {r['RMSE']:.2f} & {r['R2']:.3f} & "
                     f"{100 * r['Late > 5 min']:.1f}\\% & {_ci(r['dMAE vs median'], r['CI vs median'])} & "
                     f"{_ci(r['dMAE vs promise'], r['CI vs promise'])} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table*}"]
    return "\n".join(lines) + "\n"


def promise_latex(result: dict, eval_name: str) -> str:
    sm = result["same_mean"]
    lines = [r"\begin{table}[t]", r"\centering",
             r"\caption{Promise setting at the same mean promised time (" + f"{sm['platform']['mean_promise']:.1f}" +
             r" min; our q80 promises shifted by " + f"{sm['shift_min']:+.1f}" + r" min). " +
             ("Test days." if eval_name == "test" else "CV folds.") + r" Gap = ours $-$ platform, 95\% bootstrap CI.}",
             r"\label{tab:promise" + ("" if eval_name == "test" else "_cv") + "}", r"\begin{tabular}{lrrl}", r"\toprule",
             r"Metric & Ours & Platform & Gap \\", r"\midrule"]
    for t in promise_test.THRESHOLDS:
        d = sm["late_rate_diff"][f"{t}min"]
        lines.append(f"Late $>${t} min & {100 * sm['model'][f'late_rate_{t}min']:.1f}\\% & "
                     f"{100 * sm['platform'][f'late_rate_{t}min']:.1f}\\% & "
                     f"{100 * d['diff']:+.1f} pp [{100 * d['ci95'][0]:+.1f}, {100 * d['ci95'][1]:+.1f}] \\\\")
    lines.append(f"Pinball loss ($q=0.8$) & {sm['model']['pinball']:.2f} & {sm['platform']['pinball']:.2f} & -- \\\\")
    lines.append(f"Coverage & {100 * sm['model']['coverage']:.1f}\\% & {100 * sm['platform']['coverage']:.1f}\\% & -- \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    return "\n".join(lines) + "\n"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--eval", default="cv", choices=["cv", "test"])
    ap.add_argument("--i-am-at-cp4", action="store_true", help="required for --eval test (test days are used once)")
    ap.add_argument("--sample", type=int, help="random subset of training rows: plumbing checks only")
    args = ap.parse_args(argv)
    if args.eval == "test" and not args.i_am_at_cp4:
        raise SystemExit("Refusing to score the test days: they are used ONCE, at CP4, after every model is frozen.\n"
                         "If that is now, rerun with --i-am-at-cp4.")

    out = RESULTS / "final" / args.eval
    out.mkdir(parents=True, exist_ok=True)
    fs = FEATURE_SETS[FEATURES]
    train, test = split.train_test(load_table())
    if args.sample:
        train = train.sample(min(args.sample, len(train)), random_state=SEED)

    preds, manifest = {}, {"eval": args.eval, "git_commit": git_commit(), "data_cache_key": _cache_key(),
                           "features": FEATURES, "feature_columns": fs.columns, "seed": SEED, "sample": args.sample,
                           "started_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "models": {}}
    for spec in FINAL_MODELS:
        model = spec["model"]
        params, source = frozen_params(model)
        start = time.time()
        if args.eval == "cv":
            pred = cross_validate(model, fs, train, params, SEED, spec["log_target"])
        else:
            p, _ = fit_predict(model, fs, train, test, params, SEED, spec["log_target"])
            pred = _scored(test, p, 0)
        (out / model).mkdir(exist_ok=True)
        pred.to_parquet(out / model / "predictions.parquet", index=False)
        summary = summarize(pred)
        (out / model / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf8")
        preds[model] = pred
        manifest["models"][model] = {"params": params, "params_source": source, "log_target": spec["log_target"],
                                     "seconds": round(time.time() - start, 1)}
        print(f"{spec['label']:<24} MAE {summary['model']['mae']:.2f}   ({source}, {time.time() - start:.0f} s)")

    table = comparison_table(preds)
    promise = promise_test.compare(preds["hgb_q80"])
    TABLES_DIR.mkdir(parents=True, exist_ok=True)
    (TABLES_DIR / f"main_results_{args.eval}.tex").write_text(main_results_latex(table, args.eval), encoding="utf8")
    (TABLES_DIR / f"promise_test_{args.eval}.tex").write_text(promise_latex(promise, args.eval), encoding="utf8")
    promise_test.plot_gap(preds["hgb_q80"], FIGURES_DIR / f"final_{args.eval}_gap.pdf")
    (out / "promise_test.json").write_text(json.dumps(promise, indent=2), encoding="utf8")

    shown = table.drop(columns=["key"]).copy()
    for col in ["CI vs median", "CI vs promise"]:
        shown[col] = [("--" if ci is None else f"[{ci[0]:+.2f}, {ci[1]:+.2f}]") for ci in shown[col]]
    md = f"# Final results ({args.eval})\n\n" + shown.to_markdown(index=False, floatfmt=".3f") + "\n"
    (out / "tables.md").write_text(md, encoding="utf8")
    manifest["finished_utc"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf8")

    print("\n" + md)
    print(f"-> {out}\n-> {TABLES_DIR / f'main_results_{args.eval}.tex'}, promise_test_{args.eval}.tex"
          f"\n-> {FIGURES_DIR / f'final_{args.eval}_gap.pdf'}")


if __name__ == "__main__":
    main()

"""Fit one model and score it the same way for everyone (shared; Lynn).

    python -m experiments.run --model hgb --sample 50000                 # quick dev run, CV
    python -m experiments.run --model elasticnet --param alpha=0.1 --log-target
    python -m experiments.run --model hgb --features base_manhattan       # distance comparison
    python -m experiments.run --model hgb --eval test --params-from results/tuning/hgb_base.json   # CP4 only

--eval cv    forward-chaining folds on the training days (all tuning and choices use this)
--eval test  refit on all training days, score 23-24 Oct once (final runs only, from CP4)

Writes results/runs/<name>/predictions.parquet (one row per scored order) and summary.json.
"""

import argparse
import ast
import json
import time

import numpy as np
import pandas as pd
from sklearn.compose import TransformedTargetRegressor

from common import split
from common.config import RESULTS, SEED
from common.data import load_table
from common.evaluate import point_metrics, summarize
from common.features import FEATURE_SETS
from models import MODELS

TARGET = "delivery_min"


def parse_params(pairs: list[str]) -> dict:
    params = {}
    for pair in pairs:
        key, value = pair.split("=", 1)
        try:
            params[key] = ast.literal_eval(value)
        except (ValueError, SyntaxError):
            params[key] = value  # plain strings like loss=absolute_error
    return params


def fit_predict(model, fs, fit_rows, eval_rows, params=None, seed=SEED, log_target=False):
    est = MODELS[model].make(fs, seed, **(params or {}))
    if log_target:  # for a right-skewed target; decided from EDA (S3)
        est = TransformedTargetRegressor(est, func=np.log1p, inverse_func=np.expm1)
    est.fit(fit_rows[fs.columns], fit_rows[TARGET])
    return est.predict(eval_rows[fs.columns]), est


def _scored(rows: pd.DataFrame, pred, fold) -> pd.DataFrame:
    return pd.DataFrame({
        "order_id": rows["order_id"].to_numpy(), "day": rows["day"].to_numpy(),
        "district": rows["district"].to_numpy(), "hour": rows["hour"].to_numpy(),
        "dist_km": rows["dist_haversine_km"].to_numpy(), "y": rows[TARGET].to_numpy(),
        "pred": pred, "promise": rows["promise_min"].to_numpy(), "fold": fold,
    })


def cross_validate(model, fs, train, params=None, seed=SEED, log_target=False) -> pd.DataFrame:
    parts = []
    for fold, fit_rows, val_rows in split.forward_folds(train):
        pred, _ = fit_predict(model, fs, fit_rows, val_rows, params, seed, log_target)
        parts.append(_scored(val_rows, pred, fold))
    return pd.concat(parts, ignore_index=True)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--features", default="base", choices=sorted(FEATURE_SETS))
    ap.add_argument("--param", action="append", default=[], help="model parameter, e.g. max_iter=300")
    ap.add_argument("--params-from", help="JSON file of parameters, e.g. the best ones from experiments.tune")
    ap.add_argument("--log-target", action="store_true")
    ap.add_argument("--eval", default="cv", choices=["cv", "test"])
    ap.add_argument("--sample", type=int, help="random subset of training rows, for development")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--name", help="output folder name (default derived from the settings)")
    args = ap.parse_args(argv)

    params = json.loads(open(args.params_from).read())["params"] if args.params_from else {}
    params.update(parse_params(args.param))
    fs = FEATURE_SETS[args.features]
    train, test = split.train_test(load_table())
    if args.sample:
        train = train.sample(min(args.sample, len(train)), random_state=args.seed)

    name = args.name or "_".join(
        [args.model, args.features, args.eval]
        + [f"{k}{v}" for k, v in sorted(params.items())]
        + (["log"] if args.log_target else []) + ([f"n{args.sample}"] if args.sample else []))
    out = RESULTS / "runs" / name
    out.mkdir(parents=True, exist_ok=True)

    start = time.time()
    if args.eval == "cv":
        pred = cross_validate(args.model, fs, train, params, args.seed, args.log_target)
    else:
        p, _ = fit_predict(args.model, fs, train, test, params, args.seed, args.log_target)
        pred = _scored(test, p, 0)
    pred.to_parquet(out / "predictions.parquet", index=False)

    summary = {"settings": {**vars(args), "params": params, "feature_columns": fs.columns},
               "seconds": round(time.time() - start, 1), **summarize(pred)}
    if args.eval == "cv":
        folds = {int(f): point_metrics(g["y"], g["pred"])["mae"] for f, g in pred.groupby("fold")}
        summary["cv_mae_by_fold"] = folds
        summary["cv_mae_mean"], summary["cv_mae_std"] = float(np.mean(list(folds.values()))), float(np.std(list(folds.values())))
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf8")

    m, p = summary["model"], summary["promise"]
    print(f"{name}: MAE {m['mae']:.2f}  RMSE {m['rmse']:.2f}  R2 {m['r2']:.3f}  late {m['late_rate']:.1%}"
          f"   | promise MAE {p['mae']:.2f}   ({summary['seconds']} s, n={m['n']})")
    if args.eval == "cv":
        print("CV MAE by fold:", {k: round(v, 2) for k, v in summary["cv_mae_by_fold"].items()})
    print(f"-> {out}")


if __name__ == "__main__":
    main()

"""Random search over a model's SEARCH_SPACE with the forward-chaining folds (shared; Mahmoud).

    python -m experiments.tune --model hgb --n-iter 20 --sample 150000
    python -m experiments.tune --model elasticnet --n-iter 30 --log-target

Scores every configuration by mean CV MAE (the pinball loss for hgb_q80). Never touches the test days.
Writes results/tuning/<model>_<features>[_log].csv (all tries) and .json (the best), which
experiments.run reads with --params-from.
"""

import argparse
import json

import numpy as np
import pandas as pd
from sklearn.model_selection import ParameterSampler

from common import split
from common.config import RESULTS, SEED
from common.data import load_table
from common.evaluate import pinball
from common.features import FEATURE_SETS
from experiments.run import cross_validate
from models import MODELS


def score(model, pred: pd.DataFrame) -> list[float]:
    loss = (lambda g: pinball(g["y"], g["pred"])) if model == "hgb_q80" else (lambda g: (g["y"] - g["pred"]).abs().mean())
    return [float(loss(g)) for _, g in pred.groupby("fold")]


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=sorted(MODELS))
    ap.add_argument("--features", default="base", choices=sorted(FEATURE_SETS))
    ap.add_argument("--n-iter", type=int, default=20)
    ap.add_argument("--log-target", action="store_true")
    ap.add_argument("--sample", type=int, help="random subset of training rows (tuning on all rows is slow)")
    ap.add_argument("--seed", type=int, default=SEED)
    args = ap.parse_args(argv)

    space = MODELS[args.model].SEARCH_SPACE
    if not space:
        raise SystemExit(f"{args.model} has no hyperparameters to tune")
    fs = FEATURE_SETS[args.features]
    train, _ = split.train_test(load_table())
    if args.sample:
        train = train.sample(min(args.sample, len(train)), random_state=args.seed)

    rows = []
    for i, params in enumerate(ParameterSampler(space, args.n_iter, random_state=args.seed), 1):
        params = {k: (v.item() if hasattr(v, "item") else v) for k, v in params.items()}
        folds = score(args.model, cross_validate(args.model, fs, train, params, args.seed, args.log_target))
        rows.append({**params, "cv_mean": np.mean(folds), "cv_std": np.std(folds), "folds": folds})
        print(f"[{i}/{args.n_iter}] cv {np.mean(folds):.3f} ± {np.std(folds):.3f}  {params}")

    table = pd.DataFrame(rows).sort_values("cv_mean")
    stem = RESULTS / "tuning" / f"{args.model}_{args.features}{'_log' if args.log_target else ''}"
    stem.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(stem.with_suffix(".csv"), index=False)
    best = table.iloc[0]
    stem.with_suffix(".json").write_text(json.dumps({
        "params": {k: best[k] for k in space}, "cv_mean": best["cv_mean"], "cv_std": best["cv_std"],
        "settings": vars(args)}, indent=2, default=lambda v: v.item() if hasattr(v, "item") else str(v)))
    print(f"best: {best['cv_mean']:.3f}  {dict((k, best[k]) for k in space)}\n-> {stem}.json")


if __name__ == "__main__":
    main()

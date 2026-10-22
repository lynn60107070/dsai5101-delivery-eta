"""Is model A really better than model B? Paired bootstrap on the same orders (shared; Lynn).

    python -m experiments.compare results/final/hgb_base_test results/final/elasticnet_base_test
    python -m experiments.compare results/final/hgb_base_test promise    # against the platform promise

Prints MAE(A) - MAE(B) with a 95% interval. Negative means A has lower error.
"""

import argparse
import json
from pathlib import Path

import pandas as pd

from common.evaluate import paired_bootstrap


def abs_errors(run: str) -> pd.Series:
    pred = pd.read_parquet(Path(run) / "predictions.parquet").set_index(["order_id", "fold"])
    return (pred["y"] - pred["pred"]).abs()


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("a", help="run folder")
    ap.add_argument("b", help="run folder, or 'promise' for the platform promise on A's rows")
    ap.add_argument("--n-boot", type=int, default=2000)
    args = ap.parse_args(argv)

    a = abs_errors(args.a)
    if args.b == "promise":
        pred = pd.read_parquet(Path(args.a) / "predictions.parquet").set_index(["order_id", "fold"])
        b = (pred["y"] - pred["promise"]).abs()
    else:
        b = abs_errors(args.b)
    joined = pd.concat([a.rename("a"), b.rename("b")], axis=1, join="inner")
    if len(joined) < max(len(a), len(b)):
        print(f"warning: only {len(joined)} orders appear in both runs")
    result = paired_bootstrap(joined["a"], joined["b"], args.n_boot)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

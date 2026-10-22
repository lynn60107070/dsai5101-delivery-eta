"""Metrics shared by every model, so all numbers in the report are computed the same way.

Point predictions: MAE (headline), RMSE, R^2, late rate (arrived > 5 min after the prediction).
Quantile (promise) predictions: pinball loss and coverage as well.
"""

import numpy as np
import pandas as pd

from common.config import LATE_THRESHOLD_MIN, QUANTILE, SEED


def point_metrics(y, pred) -> dict:
    y, pred = np.asarray(y, float), np.asarray(pred, float)
    err = pred - y
    ss_tot = ((y - y.mean()) ** 2).sum()
    return {
        "n": int(len(y)),
        "mae": float(np.abs(err).mean()),
        "rmse": float(np.sqrt((err ** 2).mean())),
        "r2": float(1 - (err ** 2).sum() / ss_tot) if ss_tot > 0 else float("nan"),
        "late_rate": float((y - pred > LATE_THRESHOLD_MIN).mean()),
        "mean_pred": float(pred.mean()),
        "mean_y": float(y.mean()),
    }


def pinball(y, pred, q: float = QUANTILE) -> float:
    diff = np.asarray(y, float) - np.asarray(pred, float)
    return float(np.mean(np.maximum(q * diff, (q - 1) * diff)))


def quantile_metrics(y, pred, q: float = QUANTILE) -> dict:
    return {"pinball": pinball(y, pred, q), "coverage": float((np.asarray(y) <= np.asarray(pred)).mean())}


def by_segment(df: pd.DataFrame, col: str, pred_col: str = "pred") -> dict:
    """MAE, n and late rate per value of `col` (e.g. district, hour, distance bin, day)."""
    out = {}
    for key, g in df.groupby(col, observed=True):
        m = point_metrics(g["y"], g[pred_col])
        out[str(key)] = {"n": m["n"], "mae": round(m["mae"], 3), "late_rate": round(m["late_rate"], 4)}
    return out


DIST_BINS = [0, 1, 2, 3, 4, 5, 7, np.inf]


def summarize(pred: pd.DataFrame) -> dict:
    """`pred` has columns y, pred, promise, district, hour, day, dist_km (written by the runner)."""
    pred = pred.assign(dist_bin=pd.cut(pred["dist_km"], DIST_BINS, right=False).astype(str))
    return {
        "model": point_metrics(pred["y"], pred["pred"]),
        "model_quantile": quantile_metrics(pred["y"], pred["pred"]),
        "promise": point_metrics(pred["y"], pred["promise"]),  # platform promise on the same rows
        "by_district": by_segment(pred, "district"),
        "by_hour": by_segment(pred, "hour"),
        "by_distance_km": by_segment(pred, "dist_bin"),
        "by_day": by_segment(pred, "day"),
    }


def paired_bootstrap(abs_err_a, abs_err_b, n_boot: int = 2000, seed: int = SEED) -> dict:
    """MAE(a) - MAE(b) on the same orders, with a 95% bootstrap interval.
    If the interval excludes 0, the difference is unlikely to be resampling noise."""
    a, b = np.asarray(abs_err_a, float), np.asarray(abs_err_b, float)
    rng = np.random.default_rng(seed)
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, len(a), len(a))
        diffs[i] = a[idx].mean() - b[idx].mean()
    return {"mae_a": float(a.mean()), "mae_b": float(b.mean()), "diff": float(a.mean() - b.mean()),
            "ci95": [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))], "n": int(len(a))}

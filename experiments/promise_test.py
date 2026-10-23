"""Promise test (owner: Lynn, task L4): can our 80th-percentile model promise better than the platform?

    python -m experiments.run --model hgb_q80                 # CV run on the training days
    python -m experiments.promise_test results/runs/hgb_q80_base_cv
    python -m experiments.promise_test results/final/hgb_q80_base_test      # CP4, test days

A promise is "late" when the order arrives more than t minutes after it (t = 0, 5, 10; the proposal
varies the threshold). Comparing raw late rates is unfair: a longer promise is always late less often.
So we compare at the SAME mean promised time: add a constant c to every model promise so its mean equals
the platform's on the same orders (c uses only the two sets of promises, never the arrival times).
Then: late rate, pinball loss (q = 0.8) and coverage, with a paired bootstrap CI on the late-rate gap,
plus the full trade-off curve (mean promised minutes vs late rate) for the report figure.

Writes <run>/promise_test.json and figures/promise/<run>_gap.pdf (+ .png for slides).
"""

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from common.config import QUANTILE, REPO_ROOT, SEED
from common.evaluate import pinball

THRESHOLDS = (0, 5, 10)
MODEL_COLOR, PLATFORM_COLOR = "#2a78d6", "#eb6834"  # validated categorical pair (CVD dE 24.7)


def late_rate(y, promise, t: float = 0) -> float:
    return float((np.asarray(y) - np.asarray(promise) > t).mean())


def promise_metrics(y, promise, thresholds=THRESHOLDS) -> dict:
    return {"mean_promise": float(np.mean(promise)),
            **{f"late_rate_{t}min": late_rate(y, promise, t) for t in thresholds},
            "pinball": pinball(y, promise, QUANTILE),
            "coverage": float((np.asarray(y) <= np.asarray(promise)).mean())}


def paired_bootstrap_late(y, a, b, t: float = 0, n_boot: int = 2000, seed: int = SEED) -> dict:
    """Late rate of promises a minus late rate of b, on the same orders, with a 95% interval."""
    la = (np.asarray(y) - np.asarray(a) > t).astype(float)
    lb = (np.asarray(y) - np.asarray(b) > t).astype(float)
    rng = np.random.default_rng(seed)
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        idx = rng.integers(0, len(la), len(la))
        diffs[i] = la[idx].mean() - lb[idx].mean()
    return {"diff": float(la.mean() - lb.mean()),
            "ci95": [float(np.percentile(diffs, 2.5)), float(np.percentile(diffs, 97.5))]}


def tradeoff(y, promise, shifts, t: float = 0) -> pd.DataFrame:
    """Mean promised minutes vs late rate when every promise is moved by each shift."""
    y, promise = np.asarray(y, float), np.asarray(promise, float)
    return pd.DataFrame([{"shift": s, "mean_promise": promise.mean() + s, "late_rate": late_rate(y, promise + s, t)}
                         for s in shifts])


def compare(pred: pd.DataFrame, thresholds=THRESHOLDS) -> dict:
    """`pred` needs y, pred (the model's promise) and promise (the platform's), as written by experiments.run."""
    y, model, platform = pred["y"].to_numpy(), pred["pred"].to_numpy(), pred["promise"].to_numpy()
    shift = float(platform.mean() - model.mean())
    matched = model + shift
    return {
        "n": int(len(y)),
        "as_is": {"model": promise_metrics(y, model, thresholds), "platform": promise_metrics(y, platform, thresholds)},
        "same_mean": {"shift_min": shift, "model": promise_metrics(y, matched, thresholds),
                      "platform": promise_metrics(y, platform, thresholds),
                      "late_rate_diff": {f"{t}min": paired_bootstrap_late(y, matched, platform, t) for t in thresholds}},
    }


def gap_curve(y, model, platform, shifts, t: float = 0) -> pd.DataFrame:
    """Late rate of the model minus the platform's, with both moved to the same mean promise."""
    matched = np.asarray(model) + (np.mean(platform) - np.mean(model))
    m, p = tradeoff(y, matched, shifts, t), tradeoff(y, platform, shifts, t)
    return pd.DataFrame({"mean_promise": p["mean_promise"], "gap": m["late_rate"] - p["late_rate"]})


def plot_gap(pred: pd.DataFrame, path: Path, thresholds=THRESHOLDS) -> None:
    """One line per late threshold: model late rate minus platform late rate (percentage points) at
    every mean promised time. Below zero = our promises are late less often. Lec 5: plot the gap directly."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    y, model, platform = pred["y"].to_numpy(), pred["pred"].to_numpy(), pred["promise"].to_numpy()
    shifts = np.arange(-8, 12.5, 0.5)
    colors, styles = ["#2a78d6", "#eb6834", "#1baf7a"], ["-", "--", "-."]  # validated; aqua is direct-labelled

    plt.rcParams.update({"font.size": 8, "axes.edgecolor": "#52514e", "axes.labelcolor": "#0b0b0b",
                         "xtick.color": "#52514e", "ytick.color": "#52514e"})
    fig, ax = plt.subplots(figsize=(3.5, 2.7))
    ax.axhline(0, color="#52514e", lw=0.8)
    ax.axvline(platform.mean(), color="#a3a29b", lw=0.8, ls=":")
    ax.annotate("platform's mean\npromise", (platform.mean(), 0), xycoords=("data", "axes fraction"),
                xytext=(3, 3), textcoords="offset points", va="bottom", fontsize=6.5, color="#52514e")
    ends = []
    for t, color, style in zip(thresholds, colors, styles):
        g = gap_curve(y, model, platform, shifts, t)
        ax.plot(g["mean_promise"], 100 * g["gap"], color=color, lw=2, ls=style, label=f"late > {t:g} min")
        ends.append([f"> {t:g} min", g["mean_promise"].iloc[-1], 100 * g["gap"].iloc[-1]])
    # direct labels at the line ends, pushed apart so they never overlap
    low, high = ax.get_ylim()
    gap_needed = 0.07 * (high - low)
    ends.sort(key=lambda e: e[2])
    for i in range(1, len(ends)):
        ends[i][2] = max(ends[i][2], ends[i - 1][2] + gap_needed)
    for text, x, yy in ends:
        ax.annotate(text, (x, yy), xytext=(4, 0), textcoords="offset points", va="center", fontsize=7,
                    color="#0b0b0b")
    ax.set_xlabel("Mean promised delivery time (min), same for both")
    ax.set_ylabel("Late rate: model − platform (pp)")
    ax.grid(axis="y", color="#e6e5e0", lw=0.6)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_xlim(right=ax.get_xlim()[1] + 4)  # room for the direct labels
    ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(0, 1.0), ncol=3, fontsize=6.5,
              handlelength=2.2, columnspacing=1, borderaxespad=0.2)

    at = {t: late_rate(y, model + platform.mean() - model.mean(), t) - late_rate(y, platform, t) for t in thresholds}
    worst = max(thresholds, key=lambda t: at[t])
    title = ("At the same mean promise, our model has fewer late orders" if at[worst] < 0 else
             f"Same mean promise: the platform has fewer\norders late by > {worst:g} min (ours {100 * at[worst]:+.1f} pp)")
    ax.set_title(title, fontsize=8, loc="left", pad=16)
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, bbox_inches="tight")
    fig.savefig(path.with_suffix(".png"), dpi=200, bbox_inches="tight")
    plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("run", help="run folder with predictions.parquet (an hgb_q80 run)")
    args = ap.parse_args(argv)

    run = Path(args.run)
    pred = pd.read_parquet(run / "predictions.parquet")
    result = compare(pred)
    (run / "promise_test.json").write_text(json.dumps(result, indent=2), encoding="utf8")
    figure = REPO_ROOT / "figures" / "promise" / f"{run.name}_gap.pdf"
    plot_gap(pred, figure)

    sm = result["same_mean"]
    print(f"n = {result['n']}, model promises shifted by {sm['shift_min']:+.2f} min to match the platform's mean "
          f"({sm['platform']['mean_promise']:.2f} min)")
    print(f"{'':22}{'model':>10}{'platform':>10}{'diff (95% CI)':>28}")
    for t in THRESHOLDS:
        d = sm["late_rate_diff"][f"{t}min"]
        print(f"late rate, > {t:>2} min  {sm['model'][f'late_rate_{t}min']:>9.1%} {sm['platform'][f'late_rate_{t}min']:>9.1%}"
              f"   {d['diff']:+.1%} [{d['ci95'][0]:+.1%}, {d['ci95'][1]:+.1%}]")
    print(f"pinball (q={QUANTILE})       {sm['model']['pinball']:>9.3f} {sm['platform']['pinball']:>9.3f}")
    print(f"coverage              {sm['model']['coverage']:>9.1%} {sm['platform']['coverage']:>9.1%}")
    print(f"-> {run / 'promise_test.json'}\n-> {figure}")


if __name__ == "__main__":
    main()

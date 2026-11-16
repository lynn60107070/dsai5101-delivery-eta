"""Two slide figures that no analysis notebook makes (owner: Lynn, L8). Run after experiments.final and
experiments.feedback:

    python -m experiments.slide_figures

    figures/results/test_mae      slide 9: test MAE of every model, both baselines and the de-padded promise
    figures/results/time_split    slide 8: which days each fold trains and validates on, and the test days

Same palette as every other figure: blue = our models / training, orange = the platform, aqua = validation;
test days are dark grey, since orange always means the platform.
"""

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from common.config import RESULTS, REPO_ROOT

OUT = REPO_ROOT / "figures" / "results"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED, GRID, BASE = "#0b0b0b", "#52514e", "#e6e5e0", "#a3a29b"

plt.rcParams.update({"font.size": 12, "axes.edgecolor": MUTED, "axes.labelcolor": INK,
                     "xtick.color": MUTED, "ytick.color": MUTED})


def save(fig, name: str) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for ext in ("pdf", "png"):
        fig.savefig(OUT / f"{name}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("->", OUT / name)


def test_mae() -> None:
    test = RESULTS / "final" / "test"
    summary = {m: json.loads((test / m / "summary.json").read_text()) for m in ("median", "elasticnet", "rf", "hgb")}
    fair = json.loads((RESULTS / "feedback" / "summary.json").read_text())["depadded"]  # experiments.feedback
    rows = [("Platform promise", summary["hgb"]["promise"]["mae"], ORANGE),
            ("Median predictor", summary["median"]["model"]["mae"], BASE),
            (f"Promise minus its {fair['padding_learned_on_training_days']:.1f}-min padding",
             fair["test"]["depadded_promise"]["mae"], ORANGE),
            ("Elastic-Net", summary["elasticnet"]["model"]["mae"], BLUE),
            ("Random Forest", summary["rf"]["model"]["mae"], BLUE),
            ("Gradient boosting", summary["hgb"]["model"]["mae"], BLUE)]
    best, median, depadded = rows[-1][1], rows[1][1], rows[2][1]

    fig, ax = plt.subplots(figsize=(8, 4.0))
    labels, values, colors = zip(*rows)
    pos = range(len(rows))[::-1]  # platform on top, best model at the bottom
    bars = ax.barh(list(pos), values, color=colors, height=0.62)
    bars[2].set_hatch("//")  # the de-padded promise: the platform's estimate, not what it showed customers
    bars[2].set_facecolor("white")
    bars[2].set_edgecolor(ORANGE)
    for p, v in zip(pos, values):
        ax.annotate(f"{v:.2f}", (v, p), xytext=(6, 0), textcoords="offset points", va="center", color=INK)
    ax.set_yticks(list(pos), labels)
    ax.set_xlabel("Mean absolute error on the test days (minutes, lower is better)")
    ax.set_xlim(0, max(values) * 1.18)
    ax.grid(axis="x", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)
    ax.set_title(f"Gradient boosting misses by {best:.1f} min on average: {100 * (1 - best / median):.0f}% less than "
                 f"the median guess,\nand level with the platform's promise once its padding is removed "
                 f"({depadded:.2f})", loc="left", fontsize=13)
    save(fig, "test_mae")


def time_split() -> None:
    days = ["Mon\n17", "Tue\n18", "Wed\n19", "Thu\n20", "Fri\n21", "Sat\n22", "Sun\n23", "Mon\n24"]
    rows = [(f"CV fold {k}", k + 1) for k in range(1, 5)] + [("Final model", 6)]  # (label, number of fit days)

    fig, ax = plt.subplots(figsize=(8, 3.4))
    for r, (label, fit) in enumerate(rows):
        y = len(rows) - r
        for d in range(8):
            if d < fit:
                color, text = BLUE, "train"
            elif d == fit and label != "Final model":
                color, text = AQUA, "validate"
            elif d >= 6 and label == "Final model":
                color, text = MUTED, "test"
            else:
                continue
            ax.add_patch(plt.Rectangle((d + 0.04, y - 0.4), 0.92, 0.8, color=color, lw=0))
            ax.text(d + 0.5, y, text, ha="center", va="center", color="white", fontsize=9.5, fontweight="bold")
        ax.text(-0.1, y, label, ha="right", va="center", color=INK)
    ax.axvline(6, color=INK, lw=1.2, ls="--")
    ax.text(6.05, len(rows) + 0.55, "test days: scored once", ha="left", va="bottom", color=INK, fontsize=10)
    ax.set_xlim(0, 8)
    ax.set_ylim(0.4, len(rows) + 0.9)
    ax.set_xticks([d + 0.5 for d in range(8)], days)
    ax.tick_params(axis="x", length=0)
    ax.set_xlabel("October 2022")
    ax.set_yticks([])
    ax.spines[["top", "right", "left", "bottom"]].set_visible(False)
    ax.set_title("Tested like deployment: every fold trains only on earlier days", loc="left", fontsize=13)
    save(fig, "time_split")


if __name__ == "__main__":
    test_mae()
    time_split()

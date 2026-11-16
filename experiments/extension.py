"""Instructor feedback F2/F3: extra features and explainability, a CV-only extension (owner: Lynn).

    python -m experiments.extension

The frozen gradient boosting settings (final_params/hgb.json) are refitted on the CV folds with the new
feature sets (common/features.py: riders, restaurant, extended) and compared with the frozen base model on
the same orders (paired bootstrap). The test days are NOT used: the 9 Nov test run stays the main result.

Writes
    results/extension/summary.json            CV MAE per feature set, differences vs base, rider pressure,
                                              Elastic-Net effects in minutes
    report/tables/extension_cv.tex            the CV comparison for the report
    figures/results/rider_pressure            orders per available rider, by district and hour (F3)
    figures/results/partial_dependence        how the extended model's prediction moves with 4 inputs (F2)
"""

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import split
from common.config import REPO_ROOT, RESULTS, SEED
from common.data import load_table
from common.evaluate import paired_bootstrap, point_metrics
from common.features import FEATURE_SETS
from experiments.final import frozen_params
from experiments.run import cross_validate, fit_predict

OUT = RESULTS / "extension"
FIG = REPO_ROOT / "figures" / "results"
TABLE = REPO_ROOT / "report" / "tables" / "extension_cv.tex"
SETS = [("riders", "+ rider availability"), ("restaurant", "+ restaurant history"), ("extended", "+ both")]
BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e6e5e0"
PRESSURE_HIGH = 3  # orders waiting per available rider; the busiest 19% of orders on the training days


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"{name}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("->", FIG / name)


def compare(train: pd.DataFrame, params: dict) -> dict:
    base = pd.read_parquet(RESULTS / "final" / "cv" / "hgb" / "predictions.parquet")
    base_err = base.set_index(["order_id", "fold"]).eval("abs(y - pred)")
    lunch = base.set_index(["order_id", "fold"])["hour"] == 11
    rows = {"base": {"mae": float(base_err.mean()), "lunch_mae": float(base_err[lunch].mean())}}
    for name, _ in SETS:
        pred = cross_validate("hgb", FEATURE_SETS[name], train, params)
        pred.to_parquet(OUT / f"hgb_{name}_cv.parquet", index=False)
        err = pred.set_index(["order_id", "fold"]).eval("abs(y - pred)").reindex(base_err.index)
        m = point_metrics(pred["y"], pred["pred"])
        rows[name] = {"mae": m["mae"], "rmse": m["rmse"], "r2": m["r2"], "lunch_mae": float(err[lunch].mean()),
                      "vs_base": paired_bootstrap(err, base_err)}
        print(f"{name:10s} CV MAE {m['mae']:.3f}  vs base {rows[name]['vs_base']['diff']:+.3f} "
              f"{np.round(rows[name]['vs_base']['ci95'], 3)}")
    return rows


def write_table(rows: dict) -> None:
    lines = [r"\begin{table}[t]", r"\centering",
             r"\caption{Extension (CV only): frozen gradient boosting with extra order-time features. Difference in "
             r"MAE against the base features on the same orders, with paired bootstrap 95\% intervals. The test days "
             r"were not used.}", r"\label{tab:extension}", r"\small",
             r"\begin{tabular}{@{}lccc@{}}", r"\toprule",
             r"Features & CV MAE & $\Delta$ vs base & Lunch MAE \\", r"\midrule",
             f"Base (final model) & {rows['base']['mae']:.2f} & -- & {rows['base']['lunch_mae']:.2f} \\\\"]
    for name, label in SETS:
        r = rows[name]
        lo, hi = r["vs_base"]["ci95"]
        lines.append(f"Base {label} & {r['mae']:.2f} & {r['vs_base']['diff']:+.2f} [{lo:+.2f}, {hi:+.2f}] & "
                     f"{r['lunch_mae']:.2f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    TABLE.write_text("\n".join(lines) + "\n", encoding="utf8")
    print("->", TABLE)


def rider_pressure(train: pd.DataFrame) -> dict:
    """F3: the instructor's district x time matrix of rider availability, as orders waiting per rider."""
    m = train.pivot_table(index="district", columns="hour", values="orders_per_rider", aggfunc="median")
    m = m.loc[m.mean(axis=1).sort_values().index]
    fig, ax = plt.subplots(figsize=(9, 5.2))
    cmap = plt.get_cmap("Blues").copy()
    cmap.set_bad("0.85")  # grey: no orders in that district and hour
    im = ax.imshow(m.to_numpy(), aspect="auto", cmap=cmap, vmin=0, vmax=np.nanpercentile(m.to_numpy(), 98))
    ax.set_xticks(range(0, 24, 2), range(0, 24, 2))
    ax.set_yticks(range(len(m)), m.index)
    ax.set_xlabel("Hour the order was placed (local time)")
    ax.set_ylabel("District")
    fig.colorbar(im, ax=ax, label="Orders waiting per available rider (median)")
    ax.set_title("Riders are scarcest at the meal peaks, and much more so in some districts (grey: no orders)",
                 loc="left", fontsize=11)
    save(fig, "rider_pressure")

    high = train["orders_per_rider"] > PRESSURE_HIGH
    return {"threshold": PRESSURE_HIGH, "share_high": float(high.mean()),
            "median_delivery_high": float(train.loc[high, "delivery_min"].median()),
            "median_delivery_low": float(train.loc[~high, "delivery_min"].median()),
            "riders_30m_median": float(train["riders_30m"].median()),
            "riders_30m_le_10_share": float((train["riders_30m"] <= 10).mean())}


def partial_dependence(train: pd.DataFrame, params: dict) -> dict:
    """F2: average prediction when one input is set to each grid value for 5,000 training orders (others kept)."""
    fs = FEATURE_SETS["extended"]
    _, est = fit_predict("hgb", fs, train, train.head(1), params)
    sample = train.sample(5000, random_state=SEED)

    def curve(setter, grid):
        out = []
        for v in grid:
            rows = setter(sample.copy(), v)
            out.append(est.predict(rows[fs.columns]).mean())
        return np.array(out)

    def set_hour(rows, h):
        minute = h * 60 + 30
        rows["tod_sin"], rows["tod_cos"] = np.sin(2 * np.pi * minute / 1440), np.cos(2 * np.pi * minute / 1440)
        rows["lunch_peak"], rows["dinner_peak"] = int(h == 11), int(17 <= h <= 19)
        return rows

    def setter(col):
        def f(rows, v):
            rows[col] = v
            return rows
        return f

    far = train["dist_haversine_km"].quantile(0.99)  # beyond this there are too few orders to read the curve
    panels = [("Distance (km)", np.linspace(0.2, far, 25), setter("dist_haversine_km")),
              ("Hour of the order", np.arange(24), set_hour),
              ("Orders waiting per available rider", np.linspace(0.5, 6, 23), setter("orders_per_rider")),
              ("Restaurant's past mean delivery time (min)", np.linspace(18, 50, 25), setter("rest_hist_min"))]
    curves = {}
    fig, axes = plt.subplots(2, 2, figsize=(9, 6), sharey=True)
    for ax, (label, grid, f) in zip(axes.ravel(), panels):
        values = curve(f, grid)
        curves[label] = {"x": [round(float(x), 3) for x in grid], "prediction": [round(float(v), 2) for v in values]}
        ax.plot(grid, values, color=BLUE, lw=2)
        ax.set_xlabel(label)
        ax.grid(color=GRID, lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
    for ax in axes[:, 0]:
        ax.set_ylabel("Average prediction (min)")
    fig.suptitle("What the extended model learned: distance dominates, then busy riders and slow restaurants",
                 x=0.02, ha="left", fontsize=12)
    fig.tight_layout()
    save(fig, "partial_dependence")
    return curves


def elasticnet_effects(train: pd.DataFrame) -> dict:
    """F2: the linear model's effects in minutes per unit (scaled coefficients divided back by the scale)."""
    params, _ = frozen_params("elasticnet")
    out = {}
    for name in ("base", "extended"):
        fs = FEATURE_SETS[name]
        _, est = fit_predict("elasticnet", fs, train, train.head(1), params)
        pre, reg = est[0], est[-1]
        scale = pre.named_transformers_["num"][-1].scale_
        coef = reg.coef_[: len(fs.numeric)] / scale
        out[name] = {c: round(float(v), 3) for c, v in zip(fs.numeric, coef)}
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    train, _ = split.train_test(load_table())  # training days only
    params, _ = frozen_params("hgb")
    summary = {"note": "CV only; test days not used", "compare": compare(train, params)}
    write_table(summary["compare"])
    summary["rider_pressure"] = rider_pressure(train)
    summary["elasticnet_minutes_per_unit"] = elasticnet_effects(train)
    summary["partial_dependence"] = partial_dependence(train, params)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf8")
    print("->", OUT / "summary.json")


if __name__ == "__main__":
    main()

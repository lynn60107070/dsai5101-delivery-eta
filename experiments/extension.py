"""Instructor feedback F2/F3: extra features and explainability, a CV-only extension (owner: Lynn).

    python -m experiments.extension

The frozen gradient boosting settings (final_params/hgb.json) are refitted on the CV folds with the new
feature sets (common/features.py: riders, restaurant, extended, realtime, restaurant_prep, all) and compared with the frozen base
model on the same orders (paired bootstrap). The realtime set is also refitted with settings re-tuned for it
(`python -m experiments.tune --model hgb --features realtime --n-iter 20 --sample 150000`, CV only). Every
model is also compared with the platform's promise minus its per-distance padding, by segment. The test days
are NOT used: the 9 Nov test run stays the main result.

Writes
    results/extension/summary.json            CV MAE per feature set, differences vs base and vs the platform,
                                              rider pressure, Elastic-Net effects in minutes
    report/tables/extension_cv.tex            the CV comparison for the report
    report/tables/extension_vs_platform.tex   best model vs the de-padded promise by segment (CV)
    report/tables/extension_models.tex        Elastic-Net, Random Forest and boosting on base vs all features (CV)
    report/tables/elasticnet_effects.tex      Elastic-Net effects in minutes per unit, base and all features
    figures/results/rider_pressure            orders per available rider, by district and hour (F3)
    figures/results/partial_dependence        how the best model's prediction moves with 6 inputs (F2)
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
from experiments.feedback import depad_by_distance
from experiments.final import frozen_params
from experiments.run import cross_validate, fit_predict

OUT = RESULTS / "extension"
FIG = REPO_ROOT / "figures" / "results"
TABLE = REPO_ROOT / "report" / "tables" / "extension_cv.tex"
TABLE_PLATFORM = REPO_ROOT / "report" / "tables" / "extension_vs_platform.tex"
TUNED = RESULTS / "tuning" / "hgb_realtime.json"
# (run name, feature set, label, settings): "frozen" = final_params/hgb.json, "tuned" = TUNED
SETS = [("riders", "riders", "+ rider availability", "frozen"),
        ("restaurant", "restaurant", "+ restaurant history", "frozen"),
        ("extended", "extended", "+ both", "frozen"),
        ("realtime", "realtime", "+ both + recent delays, restaurant queue", "frozen"),
        ("realtime_tuned", "realtime", "same, boosting re-tuned", "tuned"),
        ("restaurant_prep", "restaurant_prep", "+ restaurant history + prep bias", "frozen"),
        ("all", "all", "all of the above + prep bias", "frozen")]
SEGMENTS = {"All orders": lambda p: p.y > -1, "Under 1 km": lambda p: p.dist_km < 1,
            "1-3 km": lambda p: p.dist_km.between(1, 3), "Over 3 km": lambda p: p.dist_km > 3,
            "Lunch peak (11:00)": lambda p: p.hour == 11, "Dinner peak (17-19)": lambda p: p.hour.between(17, 19),
            "Saturday 22": lambda p: p.day == 20221022}
BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e6e5e0"
PRESSURE_HIGH = 3  # orders waiting per available rider; the busiest 19% of orders on the training days


def save(fig, name):
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"{name}.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("->", FIG / name)


def same_settings(a: dict, b: dict) -> bool:
    """Equal parameters, allowing for float rounding between the two search logs."""
    return a.keys() == b.keys() and all(
        np.isclose(a[k], b[k]) if isinstance(a[k], float) else a[k] == b[k] for k in a)


def platform_cv(base: pd.DataFrame, orders: pd.DataFrame) -> pd.Series:
    """The promise minus its per-distance padding, learned for each fold on the days before it."""
    parts = [depad_by_distance(g, orders, [d for d in orders["day"].unique() if d < day])
             for day, g in base.groupby("day")]
    return pd.concat(parts).reindex(base.index)


def compare(train: pd.DataFrame, orders: pd.DataFrame, params: dict) -> tuple[dict, dict]:
    base = pd.read_parquet(RESULTS / "final" / "cv" / "hgb" / "predictions.parquet")
    keys = pd.MultiIndex.from_frame(base[["order_id", "fold"]])
    base_err = pd.Series((base["y"] - base["pred"]).abs().to_numpy(), index=keys)
    app_err = pd.Series((platform_cv(base, orders) - base["y"]).abs().to_numpy(), index=keys)
    masks = {name: pd.Series(f(base).to_numpy(), index=keys) for name, f in SEGMENTS.items()}
    lunch = masks["Lunch peak (11:00)"]
    rows = {"base": {"mae": float(base_err.mean()), "lunch_mae": float(base_err[lunch].mean()),
                     "vs_platform": paired_bootstrap(base_err, app_err)}}
    errors = {"Platform (de-padded)": app_err, "Base": base_err}
    for name, fs, label, settings in SETS:
        if settings == "tuned" and not TUNED.exists():
            print(f"{name}: skipped, run the tuning first ({TUNED.name} missing)")
            continue
        p = json.loads(TUNED.read_text(encoding="utf8"))["params"] if settings == "tuned" else params
        if settings == "tuned" and same_settings(p, params):
            rows[name] = {"label": label, "note": "re-tuning chose the frozen settings again; same as 'realtime'"}
            print(f"{name}: re-tuning chose the frozen settings again, nothing new to fit")
            continue
        pred = cross_validate("hgb", FEATURE_SETS[fs], train, p)
        pred.to_parquet(OUT / f"hgb_{name}_cv.parquet", index=False)
        err = pd.Series((pred["y"] - pred["pred"]).abs().to_numpy(),
                        index=pd.MultiIndex.from_frame(pred[["order_id", "fold"]])).reindex(keys)
        m = point_metrics(pred["y"], pred["pred"])
        rows[name] = {"label": label, "settings": settings, "mae": m["mae"], "rmse": m["rmse"], "r2": m["r2"],
                      "lunch_mae": float(err[lunch].mean()), "vs_base": paired_bootstrap(err, base_err),
                      "vs_platform": paired_bootstrap(err, app_err)}
        errors[label] = err
        print(f"{name:15s} CV MAE {m['mae']:.3f}  vs base {rows[name]['vs_base']['diff']:+.3f} "
              f"{np.round(rows[name]['vs_base']['ci95'], 3)}  vs platform {rows[name]['vs_platform']['diff']:+.3f}")
    segments = {seg: {"share": float(m.mean()), **{who: float(e[m].mean()) for who, e in errors.items()}}
                for seg, m in masks.items()}
    return rows, segments


def write_tables(rows: dict, segments: dict) -> None:
    lines = [r"\begin{table}[t]", r"\centering",
             r"\caption{Extension (CV only): gradient boosting with extra order-time features, all computed from "
             r"deliveries finished before each order. $\Delta$ = MAE difference against the base features on the "
             r"same orders, with paired bootstrap 95\% intervals. Lunch: CV MAE at the 11:00 peak. The test days were not used.}",
             r"\label{tab:extension}", r"\small",
             r"\begin{tabular}{@{}p{0.42\columnwidth}ccc@{}}", r"\toprule",
             r"Features & CV MAE & $\Delta$ vs base & Lunch \\", r"\midrule",
             f"Base (final model) & {rows['base']['mae']:.2f} & -- & {rows['base']['lunch_mae']:.2f} \\\\"]
    for name, _, label, _ in SETS:
        if name in rows and "mae" in rows[name]:
            r = rows[name]
            lo, hi = r["vs_base"]["ci95"]
            lines.append(f"{label} & {r['mae']:.2f} & {r['vs_base']['diff']:+.2f} [{lo:+.2f}, {hi:+.2f}] & "
                         f"{r['lunch_mae']:.2f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    TABLE.write_text("\n".join(lines) + "\n", encoding="utf8")
    print("->", TABLE)

    best = [label for name, _, label, _ in SETS if name in rows and "mae" in rows[name]][-1]
    lines = [r"\begin{table}[t]", r"\centering",
             r"\caption{CV MAE (minutes) by segment: the platform's promise minus its per-distance padding (learned "
             r"on earlier days), our final model, and our best extended model (" + best + r").}",
             r"\label{tab:extension_platform}", r"\small", r"\begin{tabular}{@{}lrccc@{}}", r"\toprule",
             r"Orders & Share & Platform & Base & Extended \\", r"\midrule"]
    for seg, s in segments.items():
        cells = [s["Platform (de-padded)"], s["Base"], s[best]]
        win = min(cells)
        cells = [f"\\textbf{{{c:.2f}}}" if c == win else f"{c:.2f}" for c in cells]
        lines.append(f"{seg} & {100 * s['share']:.0f}\\% & " + " & ".join(cells) + r" \\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    TABLE_PLATFORM.write_text("\n".join(lines) + "\n", encoding="utf8")
    print("->", TABLE_PLATFORM)


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
    """F2: average prediction when one input is set to each grid value for 5,000 training orders (others kept),
    for the model with every extension feature (frozen settings: re-tuning chose them again)."""
    fs = FEATURE_SETS["all"]
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
              ("Restaurant's past mean delivery time (min)", np.linspace(18, 50, 25), setter("rest_hist_min")),
              ("District's mean delivery time, last 30 min", np.linspace(18, 42, 25), setter("recent_delivery_30m")),
              ("Orders waiting for pickup at the restaurant", np.arange(0, 11), setter("rest_backlog"))]
    curves = {}
    fig, axes = plt.subplots(3, 2, figsize=(9, 8.5), sharey=True)
    for ax, (label, grid, f) in zip(axes.ravel(), panels):
        values = curve(f, grid)
        curves[label] = {"x": [round(float(x), 3) for x in grid], "prediction": [round(float(v), 2) for v in values]}
        ax.plot(grid, values, color=BLUE, lw=2)
        ax.set_xlabel(label)
        ax.grid(color=GRID, lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
    for ax in axes[:, 0]:
        ax.set_ylabel("Average prediction (min)")
    fig.suptitle("What the extended model learned: distance dominates, then busy riders and slow restaurants;\n"
                 "recent district delays and the restaurant's queue add little", x=0.02, ha="left", fontsize=12)
    fig.tight_layout()
    save(fig, "partial_dependence")
    return curves


def elasticnet_effects(train: pd.DataFrame) -> dict:
    """F2: the linear model's effects in minutes per unit (scaled coefficients divided back by the scale)."""
    params, _ = frozen_params("elasticnet")
    out = {}
    for name in ("base", "all"):
        fs = FEATURE_SETS[name]
        _, est = fit_predict("elasticnet", fs, train, train.head(1), params)
        pre, reg = est[0], est[-1]
        scale = pre.named_transformers_["num"][-1].scale_
        coef = reg.coef_[: len(fs.numeric)] / scale
        out[name] = {c: round(float(v), 3) for c, v in zip(fs.numeric, coef)}
    return out


EFFECTS = [("dist_haversine_km", "Distance (per km)"), ("prep_min", "Prep estimate (per min)"),
           ("prep_default", "Prep estimate is a default"), ("prep_missing", "Prep estimate missing"),
           ("lunch_peak", "Lunch peak (11:00)"), ("dinner_peak", "Dinner peak (17--19)"),
           ("load_15m_rel", "District load (per $\\times$ usual)"),
           ("orders_per_rider", "Orders per available rider (per order)"),
           ("rest_hist_min", "Restaurant's past delivery time (per min)"),
           ("rest_pickup_hist", "Restaurant's past pickup time (per min)"),
           ("prep_bias", "Restaurant's prep-estimate bias (per min)"),
           ("recent_delivery_30m", "District's recent delivery time (per min)"),
           ("rest_backlog", "Orders waiting at the restaurant (per order)")]
LADDER = [("elasticnet", "Elastic-Net"), ("rf", "Random Forest"), ("hgb", "Gradient boosting")]


def model_ladder(train: pd.DataFrame) -> dict:
    """Simple vs complex on the extended features: each model with its frozen settings, base vs all features,
    on the same CV orders. Every fitted step (imputer, scaler, model) is refitted inside each fold."""
    out = {}
    for model, _ in LADDER:
        base = pd.read_parquet(RESULTS / "final" / "cv" / model / "predictions.parquet")
        path = OUT / f"{model}_all_cv.parquet"
        if model == "hgb":
            path = OUT / "hgb_all_cv.parquet"  # written by compare()
        else:
            params, _ = frozen_params(model)
            cross_validate(model, FEATURE_SETS["all"], train, params).to_parquet(path, index=False)
        ext = pd.read_parquet(path)
        keys = ["order_id", "fold"]
        both = base.merge(ext[keys + ["pred"]].rename(columns={"pred": "ext"}), on=keys)
        e_base, e_ext = (both["pred"] - both["y"]).abs(), (both["ext"] - both["y"]).abs()
        out[model] = {"base_mae": float(e_base.mean()), "all_mae": float(e_ext.mean()),
                      "base_r2": point_metrics(both["y"], both["pred"])["r2"],
                      "all_r2": point_metrics(both["y"], both["ext"])["r2"],
                      "all_vs_base": paired_bootstrap(e_ext, e_base)}
        print(f"{model:10s} base {e_base.mean():.3f} -> all {e_ext.mean():.3f}")
    return out


def write_ladder_tables(ladder: dict, effects: dict) -> None:
    lines = [r"\begin{table}[t]", r"\centering",
             r"\caption{Simple to complex models on the base and the extended features (CV only, frozen settings, "
             r"the same orders). $\Delta$ with paired bootstrap 95\% intervals.}", r"\label{tab:ladder}", r"\small",
             r"\begin{tabular}{@{}lcccc@{}}", r"\toprule",
             r"Model & Base & Extended & $\Delta$ & $R^2$ \\", r"\midrule"]
    for model, label in LADDER:
        r = ladder[model]
        lo, hi = r["all_vs_base"]["ci95"]
        lines.append(f"{label} & {r['base_mae']:.2f} & {r['all_mae']:.2f} & {r['all_vs_base']['diff']:+.2f} "
                     f"[{lo:+.2f}, {hi:+.2f}] & {r['base_r2']:.2f} $\\to$ {r['all_r2']:.2f} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    (REPO_ROOT / "report" / "tables" / "extension_models.tex").write_text("\n".join(lines) + "\n", encoding="utf8")

    lines = [r"\begin{table}[t]", r"\centering",
             r"\caption{Elastic-Net effects in minutes of delivery time per unit of each input, holding the others "
             r"fixed (fitted on the six training days). Correlated inputs share their effect, so read signs and sizes, "
             r"not causes. A default prep estimate sets both prep flags, so its total effect is their sum (base: "
             r"$+2.0$). Time of day (sine and cosine) and districts are left out.}",
             r"\label{tab:effects}", r"\small", r"\begin{tabular}{@{}lrr@{}}", r"\toprule",
             r"Input & Base & Extended \\", r"\midrule"]
    for col, label in EFFECTS:
        base, ext = effects["base"].get(col), effects["all"].get(col)
        cell = lambda v: "--" if v is None else ("0.00" if round(v, 2) == 0 else f"{v:+.2f}")
        lines.append(f"{label} & {cell(base)} & {cell(ext)} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    (REPO_ROOT / "report" / "tables" / "elasticnet_effects.tex").write_text("\n".join(lines) + "\n", encoding="utf8")
    print("-> report/tables/extension_models.tex, report/tables/elasticnet_effects.tex")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    orders = load_table()
    train, _ = split.train_test(orders)  # training days only
    params, _ = frozen_params("hgb")
    rows, segments = compare(train, orders, params)
    summary = {"note": "CV only; test days not used", "compare": rows, "segments_vs_platform": segments}
    write_tables(rows, segments)
    summary["rider_pressure"] = rider_pressure(train)
    summary["elasticnet_minutes_per_unit"] = elasticnet_effects(train)
    summary["model_ladder"] = model_ladder(train)
    write_ladder_tables(summary["model_ladder"], summary["elasticnet_minutes_per_unit"])
    summary["partial_dependence"] = partial_dependence(train, params)
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf8")
    print("->", OUT / "summary.json")


if __name__ == "__main__":
    main()

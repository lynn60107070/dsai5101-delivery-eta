"""Instructor feedback F1, F4, F5, F6: analyses on the existing predictions and data (owner: Lynn).

    python -m experiments.feedback        # after experiments.final (needs results/final/*/hgb/predictions.parquet)

F4  Fair comparison with the platform. Padded vs padded is the promise test (final.py). Unpadded vs
    unpadded: our estimate against the promise minus its average padding, learned only from days before
    the scored day (CV: earlier days; test: the six training days), so no test information is used.
    Plus trip-length shares and our model's results on its own.
F1  Weekday vs weekend: hourly median delivery time per day.
F6  Drift: the same weekday a week apart (Mon 17 vs Mon 24).
F5  Data issues: count, % of rows, decision.

Writes results/feedback/summary.json, report/tables/depadded_test.tex, report/tables/data_issues.tex,
figures/results/day_profiles.{pdf,png}. No model is refitted and the test days are not re-scored: this
only reads the 9 Nov predictions.
"""

import json

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from common import clean
from common.config import REPO_ROOT, RESULTS, TRAIN_DAYS
from common.data import load_raw, load_table
from common.evaluate import paired_bootstrap, point_metrics

OUT = RESULTS / "feedback"
FIG = REPO_ROOT / "figures" / "results"
TABLES = REPO_ROOT / "report" / "tables"
BLUE, ORANGE, INK, MUTED, GRID = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e6e5e0"
DAY_NAMES = {20221017: "Mon 17", 20221018: "Tue 18", 20221019: "Wed 19", 20221020: "Thu 20", 20221021: "Fri 21",
             20221022: "Sat 22", 20221023: "Sun 23", 20221024: "Mon 24"}
WEEKEND = [20221022, 20221023]
SEGMENTS = {"under 1 km": lambda p: p.dist_km < 1, "1-3 km": lambda p: p.dist_km.between(1, 3),
            "over 3 km": lambda p: p.dist_km > 3, "lunch peak (11:00)": lambda p: p.hour == 11,
            "Sunday 23": lambda p: p.day == 20221023, "Monday 24": lambda p: p.day == 20221024}


PAD_BINS_KM = [0, 1, 2, 3, 4, 5, np.inf]


def padding(orders: pd.DataFrame, days) -> float:
    rows = orders[orders["day"].isin(days)]
    return float((rows["promise_min"] - rows["delivery_min"]).mean())


def depad_by_distance(pred: pd.DataFrame, orders: pd.DataFrame, days) -> pd.Series:
    """Stricter de-padding: the promise minus its average padding in the same distance band, learned on `days`.
    The padding is about 10 min under 1 km (the 30-min floor), 7 min at 1-3 km and 12-14 min beyond 4 km, so
    one average over-corrects short and long trips; this version is fairer to the platform."""
    rows = orders[orders["day"].isin(days)]
    pad = (rows["promise_min"] - rows["delivery_min"]).groupby(np.digitize(rows["dist_haversine_km"], PAD_BINS_KM)).mean()
    return pred["promise"] - pd.Series(np.digitize(pred["dist_km"], PAD_BINS_KM), index=pred.index).map(pad)


def depadded(orders: pd.DataFrame) -> dict:
    test = pd.read_parquet(RESULTS / "final" / "test" / "hgb" / "predictions.parquet")
    shift = padding(orders, TRAIN_DAYS)
    test["depadded"] = test["promise"] - shift
    ours, theirs = (test.pred - test.y).abs(), (test.depadded - test.y).abs()
    out = {"padding_learned_on_training_days": shift,
           "test": {"ours": point_metrics(test.y, test.pred), "depadded_promise": point_metrics(test.y, test.depadded),
                    "ours_minus_depadded": paired_bootstrap(ours, theirs)},
           "test_segments": {}, "cv_folds": {}}
    strict = (depad_by_distance(test, orders, TRAIN_DAYS) - test.y).abs()
    out["test_by_distance_band"] = {"depadded_promise_mae": float(strict.mean()),
                                    "ours_minus_depadded": paired_bootstrap(ours, strict)}
    # segments against the stricter, per-distance de-padding, so a single average can't flatter us
    for name, f in SEGMENTS.items():
        m = f(test)
        out["test_segments"][name] = {"n": int(m.sum()), "ours": float(ours[m].mean()),
                                      "depadded": float(strict[m].mean()),
                                      "ours_minus_depadded": paired_bootstrap(ours[m], strict[m])}
    cv = pd.read_parquet(RESULTS / "final" / "cv" / "hgb" / "predictions.parquet")
    for day, g in cv.groupby("day"):
        earlier = [d for d in TRAIN_DAYS if d < day]
        s = padding(orders, earlier)
        out["cv_folds"][DAY_NAMES[day]] = {"padding": s, "ours": float((g.pred - g.y).abs().mean()),
                                           "depadded": float((g.promise - s - g.y).abs().mean()),
                                           "depadded_by_distance": float(
                                               (depad_by_distance(g, orders, earlier) - g.y).abs().mean())}
    return out


def standalone() -> dict:
    """Our models on their own, not only against the app."""
    test = pd.read_parquet(RESULTS / "final" / "test" / "hgb" / "predictions.parquet")
    err = test.pred - test.y
    q80 = json.loads((RESULTS / "final" / "test" / "hgb_q80" / "summary.json").read_text(encoding="utf8"))
    return {"mae": float(err.abs().mean()), "median_abs_error": float(err.abs().median()),
            "within_5_min": float((err.abs() <= 5).mean()), "within_10_min": float((err.abs() <= 10).mean()),
            "q80_coverage_unshifted": q80["model_quantile"]["coverage"]}


def trip_shares(orders: pd.DataFrame) -> dict:
    d = orders["dist_haversine_km"]
    return {"under_1_km": float((d < 1).mean()), "1_to_3_km": float(d.between(1, 3).mean()),
            "over_3_km": float((d > 3).mean())}


def day_profiles(orders: pd.DataFrame) -> dict:
    """F1 + F6: hourly median delivery time for every day; Monday 17 vs Monday 24."""
    prof = orders.pivot_table(index="hour", columns="day", values="delivery_min", aggfunc="median")
    weekdays = [d for d in prof.columns if d not in WEEKEND]
    wk, we = prof[weekdays].mean(axis=1), prof[WEEKEND].mean(axis=1)

    busy = orders.groupby("hour").size() >= 0.02 * len(orders)
    fig, axes = plt.subplots(1, 2, figsize=(11, 3.8), sharey=True)
    for ax in axes:
        for h in busy.index[~busy]:
            ax.axvspan(h - 0.5, h + 0.5, color="0.94", zorder=0, lw=0)
        ax.text(3.5, 34.6, "few orders", ha="center", fontsize=8, color=MUTED)
    for d in weekdays:
        axes[0].plot(prof.index, prof[d], color=BLUE, lw=1, alpha=0.45)
    for d, ls in zip(WEEKEND, ["--", "-"]):
        axes[0].plot(prof.index, prof[d], color=INK, lw=2, ls=ls, label=DAY_NAMES[d])
    axes[0].plot([], [], color=BLUE, lw=1, alpha=0.6, label="weekdays")
    axes[0].set_title("Weekend: same daily shape, 1-3.5 min slower from noon to 18:00", loc="left", fontsize=11)
    for d, color in [(20221017, BLUE), (20221024, MUTED)]:
        axes[1].plot(prof.index, prof[d], color=color, lw=2, label=DAY_NAMES[d])
    axes[1].set_title("Same weekday a week apart: almost identical", loc="left", fontsize=11)
    for ax in axes:
        ax.set_xticks(range(0, 24, 3))
        ax.set_xlabel("Hour the order was placed (local time)")
        ax.grid(color=GRID, lw=0.8)
        ax.spines[["top", "right"]].set_visible(False)
        ax.legend(frameon=False, fontsize=9)
    axes[0].set_ylabel("Median delivery time (min)")
    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(FIG / f"day_profiles.{ext}", dpi=300, bbox_inches="tight")
    plt.close(fig)
    print("->", FIG / "day_profiles")

    daily = orders.groupby("day")["delivery_min"].agg(["mean", "median"])
    diff = (we - wk)[busy]
    mon = (prof[20221024] - prof[20221017])[busy]
    return {"daily_median": {DAY_NAMES[d]: float(v) for d, v in daily["median"].items()},
            "daily_mean": {DAY_NAMES[d]: float(v) for d, v in daily["mean"].items()},
            "weekend_minus_weekday_by_busy_hour": {int(h): round(float(v), 2) for h, v in diff.items()},
            "weekend_minus_weekday_mean": float(diff.mean()),
            "profile_correlation_weekday_weekend": float(np.corrcoef(wk[busy], we[busy])[0, 1]),
            "mon24_minus_mon17_mean_abs_by_busy_hour": float(mon.abs().mean()),
            "mon24_minus_mon17_max_abs": float(mon.abs().max())}


def data_issues() -> list:
    """F5: every data issue with its count, % of rows and the decision (numbers from the raw file)."""
    raw = load_raw()
    accepted = raw[raw["is_courier_grabbed"] == 1]
    cleaned = clean.clean(raw)
    model_rows = clean.modelling_rows(cleaned)
    n_raw, n_acc, n_mod = len(raw), len(accepted), len(model_rows)
    non_pre = cleaned[cleaned["is_prebook"] == 0]
    rows = [
        ("Exact duplicate rows", int(raw.duplicated().sum()), n_raw, "none found"),
        ("Refused dispatch attempts (order repeated)", int((raw["is_courier_grabbed"] == 0).sum()), n_raw,
         "removed: keep the accepted attempt, one row per order"),
        ("No arrival time (no target)", int((accepted["arrive_time"] == 0).sum()), n_acc, "removed"),
        ("Pre-booked orders", int(cleaned["is_prebook"].sum()), n_acc,
         "excluded: timing follows the chosen slot"),
        ("Delivery over 3 h, not pre-booked", int(non_pre["implausible"].sum()), n_acc, "removed as implausible"),
        ("Prep estimate missing (stored as 0)",
         int((model_rows["prep_min"].isna() & (model_rows["prep_default"] == 0)).sum()), n_mod,
         "imputed inside the pipeline + flag"),
        ("Prep estimate is a default (< 5 min)", int(model_rows["prep_default"].sum()), n_mod,
         "treated as missing + flag (not missing at random)"),
    ]
    out = [{"issue": i, "count": c, "of": of, "pct": 100 * c / of, "decision": d} for i, c, of, d in rows]
    lines = [r"\begin{table}[t]", r"\centering",
             r"\caption{Data issues, how often they occur and what we did. Percentages are of the \num{654343} raw rows "
             r"(first two lines), the \num{568546} accepted orders (next three) and the \num{546340} modelling orders "
             r"(last two).}", r"\label{tab:data_issues}", r"\footnotesize",
             r"\begin{tabular}{@{}p{0.34\columnwidth}rrp{0.36\columnwidth}@{}}", r"\toprule",
             r"Issue & Rows & \% & Decision \\", r"\midrule"]
    for r in out:
        lines.append(f"{r['issue']} & \\num{{{r['count']}}} & {r['pct']:.1f} & {r['decision']} \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    (TABLES / "data_issues.tex").write_text("\n".join(lines).replace("< 5", "$<$ 5") + "\n", encoding="utf8")
    print("->", TABLES / "data_issues.tex")
    return out


def depadded_table(d: dict) -> None:
    t = d["test"]
    lo, hi = t["ours_minus_depadded"]["ci95"]
    lines = [r"\begin{table}[t]", r"\centering",
             r"\caption{Unpadded vs unpadded on the test days: our estimate against the platform's promise minus its "
             r"average padding (" + f"{d['padding_learned_on_training_days']:.2f}" +
             r" min, learned on the training days only; second row: the average padding of the same distance band, "
             r"which is fairer to the platform). MAE in minutes; $\Delta$ = ours $-$ de-padded promise with "
             r"a paired bootstrap 95\% interval. Segment rows use the per-band padding.}", r"\label{tab:depadded}",
             r"\small",
             r"\begin{tabular}{@{}lrccc@{}}", r"\toprule",
             r"Orders & $n$ & Ours & Promise $-$ padding & $\Delta$ \\", r"\midrule",
             f"All test orders & \\num{{{t['ours']['n']}}} & {t['ours']['mae']:.2f} & "
             f"{t['depadded_promise']['mae']:.2f} & {t['ours_minus_depadded']['diff']:+.2f} [{lo:+.2f}, {hi:+.2f}] \\\\"]
    s = d["test_by_distance_band"]
    lo, hi = s["ours_minus_depadded"]["ci95"]
    lines.append(f"All, padding per distance band & \\num{{{t['ours']['n']}}} & {t['ours']['mae']:.2f} & "
                 f"{s['depadded_promise_mae']:.2f} & {s['ours_minus_depadded']['diff']:+.2f} [{lo:+.2f}, {hi:+.2f}] \\\\")
    lines.append(r"\midrule")
    for name, s in d["test_segments"].items():
        lo, hi = s["ours_minus_depadded"]["ci95"]
        lines.append(f"{name.capitalize()} & \\num{{{s['n']}}} & {s['ours']:.2f} & {s['depadded']:.2f} & "
                     f"{s['ours_minus_depadded']['diff']:+.2f} [{lo:+.2f}, {hi:+.2f}] \\\\")
    lines += [r"\bottomrule", r"\end{tabular}", r"\end{table}"]
    (TABLES / "depadded_test.tex").write_text("\n".join(lines) + "\n", encoding="utf8")
    print("->", TABLES / "depadded_test.tex")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    orders = load_table()
    summary = {"depadded": depadded(orders), "standalone_test": standalone(), "trip_shares": trip_shares(orders),
               "day_profiles": day_profiles(orders), "data_issues": data_issues()}
    depadded_table(summary["depadded"])
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf8")
    print("->", OUT / "summary.json")
    t = summary["depadded"]["test"]
    print(f"test MAE ours {t['ours']['mae']:.2f} vs de-padded promise {t['depadded_promise']['mae']:.2f}: "
          f"{t['ours_minus_depadded']['diff']:+.3f} {np.round(t['ours_minus_depadded']['ci95'], 3)}")


if __name__ == "__main__":
    main()

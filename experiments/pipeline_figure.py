"""Pipeline overview figure: every step from the raw file to the final predictions.

python -m experiments.pipeline_figure  ->  figures/results/pipeline.png, pipeline_columns.png,
and pipeline.pdf (page 1: the pipeline, page 2: the 23 raw columns and how each is used)
Numbers are copied from README §3-5 (data facts, cleaning log, final test results).
"""

from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

OUT = Path(__file__).resolve().parents[1] / "figures" / "results"
BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
INK, MUTED = "#0b0b0b", "#52514e"

# (title, colour, body lines). A line starting with "!" is bold; "~" is muted.
DATA = [
    ("1  Raw data", AQUA, [
        "!654,343 rows, 23 columns",
        "one row per dispatch attempt",
        "Meituan, 17–24 Oct 2022",
        "8 days · 23 districts",
    ]),
    ("2  Cleaning", AQUA, [
        "− 85,797 refused dispatches",
        "   (repeats of the same order)",
        "− 22,181 pre-booked orders",
        "− 25 implausible / no arrival",
        "prep defaults (13.8%) → missing",
        "!= 546,340 orders",
    ]),
    ("3  Features (order time only)", AQUA, [
        "distance (km)",
        "prep estimate + missing flags",
        "time of day (sin/cos) + peaks",
        "area load (last 15 min vs usual)",
        "district",
        "~never: courier, pickup, promise",
    ]),
    ("4  Time split", AQUA, [
        "!train 17–22 Oct: 406,553",
        "4 forward-chaining CV folds",
        "   (fit on earlier days only)",
        "!test 23–24 Oct: 139,787",
        "   locked until the end",
    ]),
]
MODEL = [
    ("5  Leak-proof pipeline", BLUE, [
        "fill missing (median)",
        "scale (Elastic-Net only)",
        "one-hot encode district",
        "!refit on each fold's",
        "!training days only",
    ]),
    ("6  Baselines + models", BLUE, [
        "~baselines: median guess,",
        "~the app's promise",
        "Elastic-Net · Random Forest",
        "gradient boosting",
        "+ 80th-percentile boosting",
        "   (for promises)",
    ]),
    ("7  Tune, then test once", BLUE, [
        "random search on CV folds",
        "metric: MAE (+ RMSE, R²)",
        "bootstrap 95% CIs",
        "retrain on all 6 days",
        "!test scored once (9 Nov)",
        "!best: boosting, MAE 6.49",
    ]),
    ("8  What we learned", BLUE, [
        "drivers: distance matters most",
        "leakage audit: 6.25 → 4.53",
        "!estimate: tie with the app",
        "   (6.49 vs 6.48 unpadded)",
        "!promise: the app wins",
        "   (late 5.0% vs our 6.1%)",
    ]),
]

W, H, GAP = 3.55, 3.05, 0.55   # box width, height, horizontal gap (inches = data units)
HEAD = 0.48


def box(ax, x, y, title, colour, lines):
    ax.add_patch(FancyBboxPatch((x, y), W, H, boxstyle="round,pad=0,rounding_size=0.12",
                                fc="white", ec=colour, lw=2))
    ax.add_patch(FancyBboxPatch((x, y + H - HEAD), W, HEAD, boxstyle="round,pad=0,rounding_size=0.12",
                                fc=colour, ec=colour, lw=2))
    ax.add_patch(plt.Rectangle((x, y + H - HEAD), W, HEAD / 2, fc=colour, ec=colour, lw=0))  # square bottom
    ax.text(x + 0.16, y + H - HEAD / 2, title, color="white", fontsize=13.5, fontweight="bold", va="center")
    for i, line in enumerate(lines):
        bold, muted = line.startswith("!"), line.startswith("~")
        ax.text(x + 0.16, y + H - HEAD - 0.36 - i * 0.39, line.lstrip("!~"), fontsize=12,
                fontweight="bold" if bold else "normal", color=MUTED if muted else INK, va="center",
                style="italic" if muted else "normal")


def arrow(ax, start, end, colour=MUTED, **kw):
    ax.add_patch(FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=18, lw=2, color=colour, **kw))


def main():
    plt.rcParams.update({"font.family": "DejaVu Sans"})
    total_w = 4 * W + 3 * GAP
    fig = plt.figure(figsize=(total_w + 0.6, 9))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-0.3, total_w + 0.3)
    ax.set_ylim(0, 9)
    ax.axis("off")

    ax.text(total_w / 2, 8.55, "From raw orders to predictions: every step uses only what is known when the order is placed",
            ha="center", fontsize=16, color=INK)
    y_top, y_bot = 4.65, 0.55
    ax.text(0, y_top + H + 0.2, "DATA SCIENCE: understand and prepare the data", fontsize=11.5,
            color=AQUA, fontweight="bold")
    ax.text(W / 2 + 0.25, y_bot + H + 0.2, "MACHINE LEARNING: model and evaluate honestly", fontsize=11.5,
            color=BLUE, fontweight="bold")

    for row, y in ((DATA, y_top), (MODEL, y_bot)):
        for i, (title, colour, lines) in enumerate(row):
            x = i * (W + GAP)
            box(ax, x, y, title, colour, lines)
            if i:
                arrow(ax, (x - GAP + 0.05, y + H / 2), (x - 0.05, y + H / 2))

    # elbow from the end of row 1 down to the start of row 2
    x_end, mid_y = total_w, (y_top + y_bot + H) / 2
    ax.plot([x_end - W / 2, x_end - W / 2], [y_top - 0.05, mid_y], color=MUTED, lw=2)
    ax.plot([x_end - W / 2, W / 2], [mid_y, mid_y], color=MUTED, lw=2)
    arrow(ax, (W / 2, mid_y), (W / 2, y_bot + H + 0.05))

    cols_fig = columns_page(total_w)

    OUT.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT / "pipeline.png", dpi=300, facecolor="white")
    cols_fig.savefig(OUT / "pipeline_columns.png", dpi=300, facecolor="white")
    with PdfPages(OUT / "pipeline.pdf") as pdf:  # page 1: the pipeline, page 2: the raw columns
        pdf.savefig(fig, facecolor="white")
        pdf.savefig(cols_fig, facecolor="white")
    print("saved", OUT / "pipeline.png", OUT / "pipeline_columns.png", OUT / "pipeline.pdf")


# Raw file: 23 columns (README §3). (column(s), group, meaning, known at order time?, how we use it)
# known: "y" yes, "n" no (after the order), "b" known but used only as a baseline
COLUMNS = [
    ("dt", "ID", "date of the order", "y", "train / test split by day"),
    ("order_id", "ID", "the order", "y", "one row per order"),
    ("waybill_id", "ID", "one courier offer (dispatch attempt)", "y", "not used"),
    ("courier_id", "ID", "courier offered the order", "n", "never (leakage)"),
    ("da_id", "ID", "district (23)", "y", "feature: district + area load"),
    ("poi_id", "ID", "restaurant (4,962)", "y", "not used (too many; future work)"),
    ("is_courier_grabbed", "Flag", "1 = courier accepted, 0 = refused", "n", "cleaning: keep accepted only"),
    ("is_weekend", "Flag", "1 = weekend", "y", "not used (1 weekend day in training)"),
    ("is_prebook", "Flag", "1 = pre-booked for later", "y", "cleaning: excluded"),
    ("sender_lat, sender_lng", "Location", "restaurant position", "y", "feature: distance"),
    ("recipient_lat, recipient_lng", "Location", "customer position", "y", "feature: distance"),
    ("grab_lat, grab_lng", "Location", "courier position when accepting", "n", "never (leakage)"),
    ("platform_order_time", "Time", "order placed", "y", "target start; time of day, peaks"),
    ("order_push_time", "Time", "order enters dispatch (~12 s later)", "y", "spots default prep estimates"),
    ("estimate_meal_prepare_time", "Time", "restaurant's food-ready estimate", "y", "feature: prep estimate"),
    ("estimate_arrived_time", "Time", "the app's promise", "b", "baseline + promise test only"),
    ("dispatch_time", "Time", "offered to a courier", "n", "never; leakage audit only"),
    ("grab_time", "Time", "courier accepted", "n", "never; leakage audit only"),
    ("fetch_time", "Time", "courier picked up the food", "n", "never; leakage audit, stages"),
    ("arrive_time", "Time", "food arrived", "n", "target end"),
]


def columns_page(total_w):
    fig = plt.figure(figsize=(total_w + 0.6, 9))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(-0.3, total_w + 0.3)
    ax.set_ylim(0, 9)
    ax.axis("off")
    ax.text(total_w / 2, 8.55, "The raw file: 23 columns, and what we did with each", ha="center", fontsize=16, color=INK)
    ax.text(total_w / 2, 8.2, "Target = arrive_time − platform_order_time (minutes).  Locations are degrees × 10⁶, "
            "shifted for privacy; all times are Unix seconds.", ha="center", fontsize=11, color=MUTED)

    xs = [0, 3.2, 4.3, 8.2, 10.75]          # column starts
    heads = ["Column", "Group", "Meaning", "Known at order time?", "How we use it"]
    top, rh = 7.8, 0.35
    ax.add_patch(plt.Rectangle((-0.1, top - rh / 2), total_w + 0.2, rh, fc=BLUE, ec=BLUE))
    for x, head in zip(xs, heads):
        ax.text(x, top, head, color="white", fontsize=12, fontweight="bold", va="center")

    known = {"y": ("✓ yes", AQUA), "n": ("✗ after the order", ORANGE), "b": ("✓ (baseline only)", MUTED)}
    group_fill = {"ID": "#f4f6f9", "Flag": "white", "Location": "#f4f6f9", "Time": "white"}
    for i, (col, group, meaning, k, use) in enumerate(COLUMNS):
        y = top - (i + 1) * rh
        ax.add_patch(plt.Rectangle((-0.1, y - rh / 2), total_w + 0.2, rh, fc=group_fill[group], ec="none"))
        ax.text(xs[0], y, col, fontsize=11, family="DejaVu Sans Mono", va="center", color=INK)
        ax.text(xs[1], y, group, fontsize=11, va="center", color=MUTED)
        ax.text(xs[2], y, meaning, fontsize=11, va="center", color=INK)
        label, colour = known[k]
        ax.text(xs[3], y, label, fontsize=11, va="center", color=colour, fontweight="bold")
        ax.text(xs[4], y, use, fontsize=11, va="center", color=INK,
                fontweight="bold" if use.startswith(("feature", "target")) else "normal")
    bottom = top - len(COLUMNS) * rh - rh / 2
    ax.plot([-0.1, total_w + 0.1], [bottom, bottom], color=MUTED, lw=1)
    ax.text(0, bottom - 0.35, "6 IDs + 3 flags + 6 coordinates + 8 timestamps = 23 columns (coordinate pairs share a row). "
            "Bold = used as a model input or to build the target.", fontsize=10.5, color=MUTED)
    return fig


if __name__ == "__main__":
    main()

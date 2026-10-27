"""Cleaning rules (owner: Sumaiya). Version v0: provisional rules that let everyone start.

Sumaiya replaces the provisional rules (marked v0) with ones justified by the data audit and EDA,
by CP2. Everyone else keeps working unchanged: the output columns below are the contract.
Log every rule and its reason in README section 4 (the cleaning log feeds the report).

Output: one row per accepted order.
    order_id, day, district, restaurant, courier_id, is_weekend, is_prebook,
    order_ts (unix seconds), rest_lat, rest_lng, cust_lat, cust_lng,
    prep_min       estimated meal-ready time, minutes after the order   (input; NaN when missing or a default)
    prep_default   1 if the "estimate" was a default under 5 min (set to NaN in prep_min)   (input)
    promise_min    the platform's promised delivery time, minutes        (baseline only, never an input)
    delivery_min   actual delivery time, minutes = TARGET. We predict the delivery time, not the
                   delay; delay (delivery_min - promise_min) is analysed in EDA only (proposal feedback)
    dispatch_min, grab_min, fetch_min   after-order times              (analysis + leakage audit only)
    implausible    True for rows excluded as impossible durations
"""

import numpy as np
import pandas as pd

TIME_COLS = ["estimate_arrived_time", "dispatch_time", "grab_time", "fetch_time", "arrive_time",
             "estimate_meal_prepare_time", "order_push_time", "platform_order_time"]

MAX_DELIVERY_MIN = 180  # v0: 4,097 accepted orders (0.7%) exceed 3 h, max is ~7 days. Sumaiya to justify or change.
PREP_DEFAULT_MAX_MIN = 5  # v1: estimates under 5 min are defaults, not forecasts (01_data_audit §4)


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    # 85,797 refused dispatch attempts repeat an order that was later accepted by someone else
    df = raw[raw["is_courier_grabbed"] == 1].copy()
    assert df["order_id"].is_unique
    df[TIME_COLS] = df[TIME_COLS].replace(0, np.nan)  # 0 means "not recorded"
    df = df.dropna(subset=["arrive_time", "platform_order_time"])  # no target (1 order)

    t0 = df["platform_order_time"]

    def minutes(col):
        return (df[col] - t0) / 60

    out = pd.DataFrame({
        "order_id": df["order_id"],
        "day": df["dt"],
        "district": df["da_id"],
        "restaurant": df["poi_id"],
        "courier_id": df["courier_id"],  # known only after dispatch: never an input
        "is_weekend": df["is_weekend"],
        "is_prebook": df["is_prebook"],
        "order_ts": t0,
        "rest_lat": df["sender_lat"] / 1e6,  # coordinates are stored as degrees x 1e6
        "rest_lng": df["sender_lng"] / 1e6,
        "cust_lat": df["recipient_lat"] / 1e6,
        "cust_lng": df["recipient_lng"] / 1e6,
        "prep_min": minutes("estimate_meal_prepare_time"),
        "promise_min": minutes("estimate_arrived_time"),
        "delivery_min": minutes("arrive_time"),
        "dispatch_min": minutes("dispatch_time"),
        "grab_min": minutes("grab_time"),
        "fetch_min": minutes("fetch_time"),
    })
    # An "estimate" under 5 min is a second missing-value code: most equal order_push_time (~12 s after the
    # order, known at placement; never the later dispatch_time), and these orders are slower than ones with
    # real estimates at the same distance
    out["prep_default"] = (out["prep_min"] < PREP_DEFAULT_MAX_MIN).astype(int)
    out.loc[out["prep_default"] == 1, "prep_min"] = np.nan
    out["implausible"] = out["delivery_min"] > MAX_DELIVERY_MIN
    return out.reset_index(drop=True)


def modelling_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Rows used for training and evaluation. Pre-booked orders follow different timing rules
    and are analysed separately (proposal)."""
    keep = (df["is_prebook"] == 0) & ~df["implausible"]
    return df[keep].reset_index(drop=True)

"""Feature engineering and feature sets (owner: Sumaiya; distance comparison: Mahmoud).

A feature set is the list of columns a model may use. Models never pick columns themselves,
so changing a feature set changes every model the same way.

    --features base            order-time features, Haversine distance (default)
    --features base_manhattan  same, Manhattan distance (distance comparison, M3)
    --features leaky           base + after-order times; ONLY for the leakage audit (S5)
    --features riders          base + rider availability and open orders in the district (instructor feedback F3)
    --features restaurant      base + the restaurant's delivery and pickup history (F2)
    --features extended        base + both (F2/F3). A CV-only extension: the test days stay as scored on 9 Nov
    --features realtime        extended + recent district delays and the restaurant's pickup queue (CV only)

Rule: only information known when the order is placed. Never add this order's promise_min, courier_id,
dispatch_min, grab_min, fetch_min or anything derived from them to a non-leaky set. Other orders' times
may be used once they have happened: the rider and restaurant features count only orders delivered
before this one was placed, which the platform knows in real time.
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from common.config import UTC_OFFSET_HOURS

EARTH_RADIUS_KM = 6371.0
LOAD_WINDOW_MIN = 15
LOAD_BASELINE_H = 24  # relative load: compared with this area's average over the previous 24 h
RIDER_WINDOW_MIN = 30  # a rider counts as available in an area if they finished a delivery there in the last 30 min
AFTER_ORDER = ["promise_min", "courier_id", "dispatch_min", "grab_min", "fetch_min", "delivery_min"]


def haversine_km(lat1, lng1, lat2, lng2):
    lat1, lng1, lat2, lng2 = map(np.radians, (lat1, lng1, lat2, lng2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lng2 - lng1) / 2) ** 2
    return 2 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(a))


def manhattan_km(lat1, lng1, lat2, lng2):
    """North-south leg plus east-west leg (a grid-street approximation)."""
    return haversine_km(lat1, lng1, lat2, lng1) + haversine_km(lat2, lng1, lat2, lng2)


def past_count(times: pd.Series, groups: pd.Series, window_s: float) -> np.ndarray:
    """For each row, the number of rows in the same group placed in [t - window, t).
    Strictly earlier, so it only uses what was known when the order was placed."""
    out = np.zeros(len(times), dtype=np.int64)
    for _, idx in groups.groupby(groups).groups.items():
        t = times.loc[idx].to_numpy()
        order = np.argsort(t, kind="stable")
        ts = t[order]
        counts = np.searchsorted(ts, ts, side="left") - np.searchsorted(ts, ts - window_s, side="left")
        out[times.index.get_indexer(idx[order])] = counts
    return out


def _finished(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray]:
    """Arrival time (unix s) of every order, and which orders count as observed activity: not pre-booked
    (their slot is hours later) and not implausible."""
    arrive = (df["order_ts"] + df["delivery_min"] * 60).to_numpy()
    ok = ((df["is_prebook"] == 0) & ~df["implausible"]).to_numpy()
    return arrive, ok


def rider_supply(df: pd.DataFrame, window_s: float) -> tuple[np.ndarray, np.ndarray]:
    """For each order, in its district at the moment it is placed:
    riders  distinct riders who finished a delivery there in [t - window, t)
    open    orders placed before t and not yet delivered at t (the backlog)
    Both use only deliveries that had already happened, so they are known at ordering."""
    arrive, ok = _finished(df)
    t_all, courier = df["order_ts"].to_numpy(), df["courier_id"].to_numpy()
    riders, backlog = np.zeros(len(df)), np.zeros(len(df))
    for _, idx in df.groupby("district").groups.items():
        pos = df.index.get_indexer(idx)
        ev = pos[ok[pos]]
        order = np.argsort(arrive[ev], kind="stable")
        a, c = arrive[ev][order], courier[ev][order]
        placed = np.sort(t_all[ev])
        t = t_all[pos]
        hi, lo = np.searchsorted(a, t, "left"), np.searchsorted(a, t - window_s, "left")
        riders[pos] = [len(np.unique(c[l:h])) for l, h in zip(lo, hi)]
        backlog[pos] = np.searchsorted(placed, t, "left") - hi
    return riders, backlog


def restaurant_history(df: pd.DataFrame) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """For each order: how many of the restaurant's earlier orders were delivered before it was placed, and
    their mean delivery and pickup times (minutes). NaN when there is no such order yet."""
    arrive, ok = _finished(df)
    t_all = df["order_ts"].to_numpy()
    y, pickup = df["delivery_min"].to_numpy(), df["fetch_min"].to_numpy()
    n_out, y_out, p_out = np.zeros(len(df)), np.full(len(df), np.nan), np.full(len(df), np.nan)
    for _, idx in df.groupby("restaurant").groups.items():
        pos = df.index.get_indexer(idx)
        ev = pos[ok[pos]]
        order = np.argsort(arrive[ev], kind="stable")
        a, yy, pp = arrive[ev][order], y[ev][order], pickup[ev][order]
        cy = np.concatenate([[0], np.cumsum(yy)])
        cp = np.concatenate([[0], np.cumsum(np.nan_to_num(pp))])
        cn = np.concatenate([[0], np.cumsum(~np.isnan(pp))])
        k = np.searchsorted(a, t_all[pos], "left")
        n_out[pos] = k
        with np.errstate(invalid="ignore", divide="ignore"):
            y_out[pos] = np.where(k > 0, cy[k] / k, np.nan)
            p_out[pos] = np.where(cn[k] > 0, cp[k] / cn[k], np.nan)
    return n_out, y_out, p_out


def recent_deliveries(df: pd.DataFrame, window_s: float) -> tuple[np.ndarray, np.ndarray]:
    """For each order: mean delivery time and mean lateness (actual - promise, minutes) of the deliveries that
    arrived in its district in [t - window, t). Other orders' promises were shown at their checkout and their
    arrivals have happened, so both are known at t. NaN when nothing arrived in the window."""
    arrive, ok = _finished(df)
    t_all = df["order_ts"].to_numpy()
    y = df["delivery_min"].to_numpy()
    late = (df["delivery_min"] - df["promise_min"]).to_numpy()
    mean_y, mean_late = np.full(len(df), np.nan), np.full(len(df), np.nan)
    for _, idx in df.groupby("district").groups.items():
        pos = df.index.get_indexer(idx)
        ev = pos[ok[pos]]
        order = np.argsort(arrive[ev], kind="stable")
        a = arrive[ev][order]
        cy = np.concatenate([[0], np.cumsum(y[ev][order])])
        cl = np.concatenate([[0], np.cumsum(late[ev][order])])
        t = t_all[pos]
        hi, lo = np.searchsorted(a, t, "left"), np.searchsorted(a, t - window_s, "left")
        n = hi - lo
        with np.errstate(invalid="ignore", divide="ignore"):
            mean_y[pos] = np.where(n > 0, (cy[hi] - cy[lo]) / n, np.nan)
            mean_late[pos] = np.where(n > 0, (cl[hi] - cl[lo]) / n, np.nan)
    return mean_y, mean_late


def restaurant_backlog(df: pd.DataFrame) -> np.ndarray:
    """For each order: the restaurant's orders placed before it and not yet picked up when it is placed."""
    _, ok = _finished(df)
    t_all = df["order_ts"].to_numpy()
    picked = (df["order_ts"] + df["fetch_min"] * 60).to_numpy()
    out = np.zeros(len(df))
    for _, idx in df.groupby("restaurant").groups.items():
        pos = df.index.get_indexer(idx)
        ev = pos[ok[pos]]
        placed, pick = np.sort(t_all[ev]), np.sort(picked[ev])
        t = t_all[pos]
        out[pos] = np.searchsorted(placed, t, "left") - np.searchsorted(pick, t, "left")
    return out


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["dist_haversine_km"] = haversine_km(df.rest_lat, df.rest_lng, df.cust_lat, df.cust_lng)
    df["dist_manhattan_km"] = manhattan_km(df.rest_lat, df.rest_lng, df.cust_lat, df.cust_lng)
    local = pd.to_datetime(df["order_ts"] + UTC_OFFSET_HOURS * 3600, unit="s")
    df["hour"] = local.dt.hour  # for segment analysis; models get the cyclical pair below
    df["minute_of_day"] = local.dt.hour * 60 + local.dt.minute
    # Cyclical time of day (Lecture 6; proposal feedback): 23:59 and 00:00 end up next to each other
    df["tod_sin"] = np.sin(2 * np.pi * df["minute_of_day"] / 1440)
    df["tod_cos"] = np.cos(2 * np.pi * df["minute_of_day"] / 1440)
    # v1: the hours whose median delivery time (training days) is above the overall median (02_eda §9)
    df["lunch_peak"] = (df["hour"] == 11).astype(int)
    df["dinner_peak"] = df["hour"].between(17, 19).astype(int)
    # Missingness as a feature (Lecture 6): the imputer fills prep_min, this keeps the fact it was missing.
    # Covers both missing codes (stored 0 and defaults); prep_default (clean.py) says which one
    df["prep_missing"] = df["prep_min"].isna().astype(int)
    # Strictly backward-looking window (Lecture 6): only orders placed before this one
    df["load_15m"] = past_count(df["order_ts"], df["district"], LOAD_WINDOW_MIN * 60)
    # v1: the same load relative to this area's average 15 minutes over the previous 24 h, so a big area is not
    # "busy" just for being big (02_eda §7). Missing until a full day of history exists (the first training day)
    usual = past_count(df["order_ts"], df["district"], LOAD_BASELINE_H * 3600) / (LOAD_BASELINE_H * 60 / LOAD_WINDOW_MIN)
    df["load_15m_rel"] = (df["load_15m"] / usual).where(usual > 0)
    first = df.loc[df["is_prebook"] == 0, "order_ts"].min()
    df.loc[df["order_ts"] < first + LOAD_BASELINE_H * 3600, "load_15m_rel"] = np.nan
    # Same idea as prep_missing: day 1 is up to half the fit rows in early CV folds and the imputer fills it
    df["load_missing"] = df["load_15m_rel"].isna().astype(int)
    # F3 (instructor feedback): rider supply vs backlog. Load counts new orders; this counts who can deliver them
    df["riders_30m"], df["open_orders"] = rider_supply(df, RIDER_WINDOW_MIN * 60)
    df["orders_per_rider"] = df["open_orders"] / df["riders_30m"].clip(lower=1)
    # F2: restaurants differ in how long they take; only their orders delivered before this one count
    df["rest_hist_n"], df["rest_hist_min"], df["rest_pickup_hist"] = restaurant_history(df)
    df["rest_hist_missing"] = df["rest_hist_min"].isna().astype(int)
    # Real-time conditions: how slow and how late the district's latest deliveries were, and the queue at the
    # restaurant. These move fastest at lunch, where the platform's estimate beat ours
    df["recent_delivery_30m"], df["recent_late_30m"] = recent_deliveries(df, RIDER_WINDOW_MIN * 60)
    df["recent_missing"] = df["recent_delivery_30m"].isna().astype(int)
    df["rest_backlog"] = restaurant_backlog(df)
    return df


@dataclass(frozen=True)
class FeatureSet:
    name: str
    numeric: tuple
    categorical: tuple

    @property
    def columns(self) -> list:
        return [*self.numeric, *self.categorical]


# No is_weekend: the training days hold one weekend day (Sat 22) and CV folds 1-3 hold none, so the
# effect can't be learned or validated. With it, scaling blew up on fold 4 (Elastic-Net MAE 6.8 -> 18.0).
# Weekend is described in EDA and stated as a limitation instead (README §4, F8).
_TIME_AND_LOAD = ("prep_min", "prep_missing", "prep_default", "tod_sin", "tod_cos", "lunch_peak", "dinner_peak",
                  "load_15m_rel", "load_missing")

FEATURE_SETS = {
    "base": FeatureSet("base", ("dist_haversine_km", *_TIME_AND_LOAD), ("district",)),
    "base_manhattan": FeatureSet("base_manhattan", ("dist_manhattan_km", *_TIME_AND_LOAD), ("district",)),
    "leaky": FeatureSet("leaky", ("dist_haversine_km", *_TIME_AND_LOAD, "dispatch_min", "grab_min", "fetch_min"),
                        ("district",)),
}
_RIDERS = ("riders_30m", "open_orders", "orders_per_rider")
_RESTAURANT = ("rest_hist_n", "rest_hist_min", "rest_pickup_hist", "rest_hist_missing")
FEATURE_SETS["riders"] = FeatureSet("riders", (*FEATURE_SETS["base"].numeric, *_RIDERS), ("district",))
FEATURE_SETS["restaurant"] = FeatureSet("restaurant", (*FEATURE_SETS["base"].numeric, *_RESTAURANT), ("district",))
FEATURE_SETS["extended"] = FeatureSet("extended", (*FEATURE_SETS["base"].numeric, *_RIDERS, *_RESTAURANT),
                                      ("district",))
_REALTIME = ("recent_delivery_30m", "recent_late_30m", "recent_missing", "rest_backlog")
FEATURE_SETS["realtime"] = FeatureSet("realtime", (*FEATURE_SETS["extended"].numeric, *_REALTIME), ("district",))


def preprocessor(fs: FeatureSet, scale: bool = False) -> ColumnTransformer:
    """Median imputation (+ optional scaling) for numbers, one-hot for categories.
    It sits inside each model's pipeline, so it is fit on the training rows of each fold only
    (Lecture 6, "the structural fix"; tests/test_pipeline.py checks it). Districts never seen in
    training are encoded as all zeros instead of crashing."""
    numeric = make_pipeline(SimpleImputer(strategy="median"), *([StandardScaler()] if scale else []))
    return ColumnTransformer([
        ("num", numeric, list(fs.numeric)),
        ("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), list(fs.categorical)),
    ])

"""Feature engineering and feature sets (owner: Sumaiya; distance comparison: Mahmoud).

A feature set is the list of columns a model may use. Models never pick columns themselves,
so changing a feature set changes every model the same way.

    --features base            order-time features, Haversine distance (default)
    --features base_manhattan  same, Manhattan distance (distance comparison, M3)
    --features leaky           base + after-order times; ONLY for the leakage audit (S5)

Rule: only information known when the order is placed. Never add promise_min, courier_id,
dispatch_min, grab_min, fetch_min or anything derived from them to a non-leaky set.
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
                  "load_15m_rel")

FEATURE_SETS = {
    "base": FeatureSet("base", ("dist_haversine_km", *_TIME_AND_LOAD), ("district",)),
    "base_manhattan": FeatureSet("base_manhattan", ("dist_manhattan_km", *_TIME_AND_LOAD), ("district",)),
    "leaky": FeatureSet("leaky", ("dist_haversine_km", *_TIME_AND_LOAD, "dispatch_min", "grab_min", "fetch_min"),
                        ("district",)),
}


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

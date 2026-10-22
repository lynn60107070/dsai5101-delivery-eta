"""Time-based split from the proposal (shared; change only with the whole team's agreement).

Train: 17-22 Oct. Validation: forward-chaining folds inside training
(fit days 1-2 -> validate day 3, fit 1-3 -> 4, fit 1-4 -> 5, fit 1-5 -> 6).
Test: 23-24 Oct, scored ONCE per final model at CP4 after retraining on all six training days.
"""

import pandas as pd

from common.config import TEST_DAYS, TRAIN_DAYS


def train_test(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    train = df[df["day"].isin(TRAIN_DAYS)].reset_index(drop=True)
    test = df[df["day"].isin(TEST_DAYS)].reset_index(drop=True)
    return train, test


def forward_folds(train: pd.DataFrame, min_fit_days: int = 2):
    """Yield (fold, fit_rows, val_rows), each later fold with one more fit day."""
    days = sorted(train["day"].unique())
    for k in range(min_fit_days, len(days)):
        yield k - min_fit_days + 1, train[train["day"].isin(days[:k])], train[train["day"] == days[k]]

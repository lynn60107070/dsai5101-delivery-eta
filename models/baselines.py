"""Median predictor (owner: Lynn). Done.

The second baseline, the platform's own promise, is not a model: the runner reports it on the
same rows as every run (summary.json -> "promise").
"""

from sklearn.dummy import DummyRegressor

SEARCH_SPACE = {}


def make(fs, seed, **params):
    return DummyRegressor(strategy="median")

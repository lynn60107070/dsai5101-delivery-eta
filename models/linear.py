"""Elastic-Net regression (owner: Lynn). v0: runs with defaults; tune and justify by CP3 (L3)."""

from scipy.stats import loguniform, uniform
from sklearn.linear_model import ElasticNet
from sklearn.pipeline import make_pipeline

from common.features import preprocessor

SEARCH_SPACE = {"alpha": loguniform(1e-4, 1e1), "l1_ratio": uniform(0, 1)}


def make(fs, seed, alpha=0.01, l1_ratio=0.5, **params):
    return make_pipeline(preprocessor(fs, scale=True),
                         ElasticNet(alpha=alpha, l1_ratio=l1_ratio, random_state=seed, max_iter=5000, **params))

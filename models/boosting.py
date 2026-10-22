"""Gradient boosting (owner: Mahmoud). v0: runs with defaults; tune by CP3 (M2).

Swapping in LightGBM is fine (it is installed) as long as make() keeps the contract.
"""

from scipy.stats import loguniform, randint
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.pipeline import make_pipeline

from common.features import preprocessor

# loss: we report MAE, and absolute loss targets the median rather than the mean (Lecture 7)
SEARCH_SPACE = {"loss": ["squared_error", "absolute_error"],
                "learning_rate": loguniform(0.02, 0.3), "max_leaf_nodes": randint(15, 127),
                "min_samples_leaf": randint(20, 500), "l2_regularization": loguniform(1e-3, 10),
                "max_iter": [200, 400, 800]}


def make(fs, seed, **params):
    return make_pipeline(preprocessor(fs), HistGradientBoostingRegressor(random_state=seed, **params))

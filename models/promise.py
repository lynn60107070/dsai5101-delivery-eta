"""80th-percentile boosting model for promise-setting (owner: Lynn).

v0: runs with defaults. Compared against the platform promise at the same mean promised time
(late rate, pinball loss, coverage) in L5.
"""

from scipy.stats import loguniform, randint
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.pipeline import make_pipeline

from common.config import QUANTILE
from common.features import preprocessor

SEARCH_SPACE = {"learning_rate": loguniform(0.02, 0.3), "max_leaf_nodes": randint(15, 127),
                "min_samples_leaf": randint(20, 500), "max_iter": [200, 400, 800]}


def make(fs, seed, **params):
    return make_pipeline(preprocessor(fs),
                         HistGradientBoostingRegressor(loss="quantile", quantile=QUANTILE, random_state=seed, **params))

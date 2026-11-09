"""Random Forest (owner: Mahmoud). Comparison model for HGB; tuned with 10 tries on a sample (M4, ALIGNMENT §6).

Develop with --sample 100000: a full forest on ~400k rows is slow.
"""

from scipy.stats import randint, uniform
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import make_pipeline

from common.features import preprocessor

SEARCH_SPACE = {"n_estimators": [100, 200, 300], "min_samples_leaf": randint(5, 200),
                "max_features": uniform(0.3, 0.7), "max_depth": [None, 12, 20]}


def make(fs, seed, n_estimators=100, min_samples_leaf=20, max_features=0.5, **params):
    # tune.py stores max_depth through a pandas table, so None comes back as NaN and 20 as 20.0
    if "max_depth" in params:
        depth = params["max_depth"]
        params["max_depth"] = None if depth is None or depth != depth else int(depth)
    return make_pipeline(preprocessor(fs), RandomForestRegressor(
        n_estimators=n_estimators, min_samples_leaf=min_samples_leaf, max_features=max_features,
        n_jobs=-1, random_state=seed, **params))

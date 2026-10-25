"""Gradient boosting (owner: Mahmoud). v0: runs with defaults; tune by CP3 (M4).

Two engines behind one model, so the runner, tuner and final script stay unchanged (M2):

    python -m experiments.run --model hgb                          # scikit-learn HistGradientBoosting (default)
    python -m experiments.run --model hgb --param engine=lgbm      # LightGBM, same settings

The parameters use the HistGradientBoosting names. For LightGBM they are renamed to its
equivalents, so SEARCH_SPACE and any tuned params file work for both engines.
"""

from lightgbm import LGBMRegressor
from scipy.stats import loguniform, randint
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.pipeline import make_pipeline

from common.features import preprocessor

# loss: we report MAE, and absolute loss targets the median rather than the mean (Lecture 7)
SEARCH_SPACE = {"loss": ["squared_error", "absolute_error"],
                "learning_rate": loguniform(0.02, 0.3), "max_leaf_nodes": randint(15, 127),
                "min_samples_leaf": randint(20, 500), "l2_regularization": loguniform(1e-3, 10),
                "max_iter": [200, 400, 800]}

# HistGradientBoosting name -> LightGBM name
_LGBM_NAMES = {"max_iter": "n_estimators", "max_leaf_nodes": "num_leaves",
               "min_samples_leaf": "min_child_samples", "l2_regularization": "reg_lambda"}
_LGBM_LOSS = {"squared_error": "regression", "absolute_error": "l1"}


def _lgbm(seed, **params):
    params = {_LGBM_NAMES.get(k, k): v for k, v in params.items()}
    if "loss" in params:
        params["objective"] = _LGBM_LOSS[params.pop("loss")]
    return LGBMRegressor(random_state=seed, n_jobs=-1, verbose=-1, **params)


def make(fs, seed, engine="sklearn", **params):
    if engine == "lgbm":
        # pandas output keeps the column names at fit and predict, so LightGBM does not warn
        return make_pipeline(preprocessor(fs).set_output(transform="pandas"), _lgbm(seed, **params))
    return make_pipeline(preprocessor(fs), HistGradientBoostingRegressor(random_state=seed, **params))

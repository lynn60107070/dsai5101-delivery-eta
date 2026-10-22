"""Registry of models the runner and tuner can call by name.

The contract (change only with the whole team's agreement). Every model module provides

    def make(fs: FeatureSet, seed: int, **params) -> sklearn estimator   # unfitted
    SEARCH_SPACE = {param: list or scipy distribution}                   # for experiments.tune

The estimator gets a DataFrame with exactly fs.columns and the target in minutes. Put the
preprocessing inside it (common.features.preprocessor), so it is fit on training rows only.
"""

from models import baselines, boosting, forest, linear, promise

MODELS = {
    "median": baselines,      # Lynn
    "elasticnet": linear,     # Lynn
    "hgb_q80": promise,       # Lynn
    "hgb": boosting,          # Mahmoud
    "rf": forest,             # Mahmoud
}

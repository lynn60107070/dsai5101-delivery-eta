"""Offline checks of the shared pipeline on a small synthetic table. No data download needed.

    python -m unittest -v
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import numpy as np
import pandas as pd

from common import clean, evaluate, features, split
from common.config import TEST_DAYS, TRAIN_DAYS
from experiments import run, tune

DAYS = TRAIN_DAYS + TEST_DAYS


def fake_raw(per_day: int = 80, seed: int = 0) -> pd.DataFrame:
    """Same columns and encodings as the Meituan CSV, including its quirks."""
    rng = np.random.default_rng(seed)
    rows = []
    for i, day in enumerate(DAYS):
        midnight = int(pd.Timestamp(f"2022-10-{17 + i}").timestamp()) - 8 * 3600
        for _ in range(per_day):
            oid = len(rows)
            t0 = midnight + int(rng.integers(10 * 3600, 21 * 3600))
            dist = rng.uniform(0.002, 0.03)
            minutes = 10 + 600 * dist + rng.normal(0, 3)
            rows.append({
                "dt": day, "order_id": oid, "waybill_id": oid, "courier_id": int(rng.integers(0, 20)),
                "da_id": int(rng.integers(0, 3)), "is_courier_grabbed": 1, "is_weekend": int(day == 20221022 or day == 20221023),
                "estimate_arrived_time": t0 + 2400, "is_prebook": 0, "poi_id": int(rng.integers(0, 30)),
                "sender_lng": 174_550_000, "sender_lat": 45_880_000,
                "recipient_lng": int(174_550_000 + dist * 1e6), "recipient_lat": 45_880_000,
                "grab_lng": 174_550_000, "grab_lat": 45_880_000, "dispatch_time": t0 + 60, "grab_time": t0 + 90,
                "fetch_time": t0 + 600, "arrive_time": t0 + int(minutes * 60),
                "estimate_meal_prepare_time": t0 + 600, "order_push_time": t0 + 5, "platform_order_time": t0,
            })
    raw = pd.DataFrame(rows)
    refused = raw.iloc[:5].copy()  # a refused dispatch attempt repeats an accepted order
    refused[["is_courier_grabbed", "grab_time", "fetch_time", "arrive_time", "grab_lng", "grab_lat"]] = 0
    raw.loc[6, "estimate_meal_prepare_time"] = 0  # missing stored as 0
    raw.loc[9, "estimate_meal_prepare_time"] = raw.loc[9, "order_push_time"]  # a default, not an estimate
    raw.loc[7, "is_prebook"] = 1
    raw.loc[8, "arrive_time"] = raw.loc[8, "platform_order_time"] + 5 * 3600  # implausible
    return pd.concat([raw, refused], ignore_index=True)


def fake_table() -> pd.DataFrame:
    return clean.modelling_rows(features.add_features(clean.clean(fake_raw())))


class TestClean(unittest.TestCase):
    def setUp(self):
        self.df = clean.clean(fake_raw())

    def test_one_row_per_accepted_order(self):
        self.assertTrue(self.df["order_id"].is_unique)
        self.assertEqual(len(self.df), 80 * len(DAYS))

    def test_zero_is_missing_and_target_in_minutes(self):
        self.assertTrue(np.isnan(self.df.loc[self.df.order_id == 6, "prep_min"]).all())
        self.assertTrue((self.df["delivery_min"] > 0).all())

    def test_default_prep_estimate_is_missing_and_flagged(self):
        """An estimate a few seconds after the order is a default: missing for the imputer, but flagged."""
        row = self.df.set_index("order_id").loc[9]
        self.assertTrue(np.isnan(row["prep_min"]))
        self.assertEqual(row["prep_default"], 1)
        self.assertEqual(self.df.loc[self.df.order_id == 6, "prep_default"].item(), 0)  # stored 0 is not a default

    def test_modelling_rows_exclude_prebook_and_implausible(self):
        kept = set(clean.modelling_rows(self.df)["order_id"])
        self.assertNotIn(7, kept)
        self.assertNotIn(8, kept)


class TestFeatures(unittest.TestCase):
    def test_distances(self):
        self.assertAlmostEqual(features.haversine_km(0, 0, 1, 0), 111.19, places=1)
        self.assertGreaterEqual(features.manhattan_km(30, 120, 30.01, 120.01),
                                features.haversine_km(30, 120, 30.01, 120.01))

    def test_load_counts_only_earlier_orders_in_window(self):
        times = pd.Series([0, 100, 100, 1000, 2000])
        groups = pd.Series(["a", "a", "a", "a", "b"])
        # window 900 s: order at 1000 sees 100 and 100 (0 is 1000 s back, outside); ties are not "earlier"
        self.assertEqual(list(features.past_count(times, groups, 900)), [0, 1, 1, 2, 0])

    def test_relative_load_needs_a_day_of_history(self):
        full = features.add_features(clean.clean(fake_raw()))
        first_day = full["order_ts"] < full.loc[full["is_prebook"] == 0, "order_ts"].min() + 24 * 3600
        self.assertTrue(full.loc[first_day, "load_15m_rel"].isna().all())
        self.assertTrue(full.loc[first_day, "load_missing"].eq(1).all())
        later = full[~first_day]
        self.assertTrue(later.loc[later["load_15m"] > 0, "load_15m_rel"].gt(0).all())
        self.assertTrue((full["load_missing"] == full["load_15m_rel"].isna()).all())

    def test_time_of_day_is_cyclical(self):
        """Proposal feedback: 23:59 and 00:00 must be close, not 1439 minutes apart."""
        df = pd.DataFrame({"minute_of_day": [1439, 0, 720]})
        sin, cos = np.sin(2 * np.pi * df.minute_of_day / 1440), np.cos(2 * np.pi * df.minute_of_day / 1440)
        t = fake_table()
        self.assertTrue(np.allclose(t["tod_sin"], np.sin(2 * np.pi * t["minute_of_day"] / 1440)))
        self.assertLess(np.hypot(sin[0] - sin[1], cos[0] - cos[1]), 0.01)  # 23:59 vs 00:00
        self.assertGreater(np.hypot(sin[1] - sin[2], cos[1] - cos[2]), 1.9)  # midnight vs noon

    def test_rider_and_restaurant_features_use_only_finished_deliveries(self):
        """F2/F3: an order may only see deliveries that arrived before it was placed."""
        df = pd.DataFrame({
            "order_ts": [0, 60, 600, 1200, 1300], "delivery_min": [5, 30, 5, 5, 5],
            "district": ["a"] * 5, "restaurant": ["r"] * 5, "courier_id": [1, 2, 1, 3, 3],
            "fetch_min": [2.0, 10.0, 4.0, 1.0, 1.0], "is_prebook": [0] * 5, "implausible": [False] * 5})
        riders, backlog = features.rider_supply(df, 30 * 60)
        # arrivals: 300 (rider 1), 1860 (rider 2), 900 (rider 1), 1500 (rider 3), 1600 (rider 3)
        self.assertEqual(list(riders), [0, 0, 1, 1, 1])   # at 1200 and 1300 only rider 1 has finished (twice)
        self.assertEqual(list(backlog), [0, 1, 1, 1, 2])  # placed before t and not yet arrived at t
        n, mean_y, mean_pickup = features.restaurant_history(df)
        self.assertEqual(list(n), [0, 0, 1, 2, 2])        # the 30-min order is still out at 1300
        self.assertTrue(np.isnan(mean_y[0]))
        self.assertAlmostEqual(mean_y[4], 5)
        self.assertAlmostEqual(mean_pickup[3], (2 + 4) / 2)

    def test_no_leakage_in_deployable_feature_sets(self):
        for name, fs in features.FEATURE_SETS.items():
            if name != "leaky":
                self.assertFalse(set(fs.columns) & set(features.AFTER_ORDER), name)


class TestSplit(unittest.TestCase):
    def test_time_split_and_forward_folds(self):
        train, test = split.train_test(fake_table())
        self.assertFalse(set(train["day"]) & set(test["day"]))
        folds = list(split.forward_folds(train))
        self.assertEqual(len(folds), len(TRAIN_DAYS) - 2)
        for _, fit_rows, val_rows in folds:
            self.assertLess(fit_rows["day"].max(), val_rows["day"].min())

    def test_fitted_steps_learn_from_training_days_only(self):
        """Proposal feedback: imputers/encoders must be fit on the training days only.
        Give the validation day a very different prep time; the imputer must not see it."""
        train, _ = split.train_test(fake_table())
        _, fit_rows, val_rows = next(split.forward_folds(train))
        val_rows = val_rows.assign(prep_min=1000.0)
        _, est = run.fit_predict("elasticnet", features.FEATURE_SETS["base"], fit_rows, val_rows)
        imputer = est[0].named_transformers_["num"][0]
        prep_median = imputer.statistics_[list(features.FEATURE_SETS["base"].numeric).index("prep_min")]
        self.assertAlmostEqual(prep_median, fit_rows["prep_min"].median())


class TestEvaluate(unittest.TestCase):
    def test_point_metrics_by_hand(self):
        m = evaluate.point_metrics([10, 20, 30], [12, 20, 20])
        self.assertAlmostEqual(m["mae"], 4.0)
        self.assertAlmostEqual(m["rmse"], np.sqrt(104 / 3))
        self.assertAlmostEqual(m["late_rate"], 1 / 3)  # only the 30 arrived > 5 min after its prediction

    def test_pinball(self):
        self.assertAlmostEqual(evaluate.pinball([10], [8], 0.8), 1.6)  # under-predicted: 0.8 * 2
        self.assertAlmostEqual(evaluate.pinball([10], [12], 0.8), 0.4)  # over-predicted: 0.2 * 2

    def test_bootstrap_sign(self):
        r = evaluate.paired_bootstrap(np.full(200, 1.0), np.full(200, 2.0), n_boot=50)
        self.assertAlmostEqual(r["diff"], -1.0)
        self.assertLess(r["ci95"][1], 0)


class TestPromiseTest(unittest.TestCase):
    def test_late_rate_thresholds(self):
        from experiments.promise_test import late_rate
        y, promise = [10, 20, 30], [12, 14, 21]  # arrive 2 early, 6 late, 9 late
        self.assertAlmostEqual(late_rate(y, promise, 0), 2 / 3)
        self.assertAlmostEqual(late_rate(y, promise, 5), 2 / 3)
        self.assertAlmostEqual(late_rate(y, promise, 8), 1 / 3)

    def test_same_mean_comparison(self):
        """The model's promises are shifted so both have the same mean; a model that is the platform
        minus 3 minutes must then match the platform exactly."""
        from experiments.promise_test import compare
        rng = np.random.default_rng(0)
        y = rng.gamma(9, 3, 2000)
        platform = y + rng.normal(5, 4, 2000)
        pred = pd.DataFrame({"y": y, "pred": platform - 3, "promise": platform})
        r = compare(pred)
        sm = r["same_mean"]
        self.assertAlmostEqual(sm["shift_min"], 3.0)
        self.assertAlmostEqual(sm["model"]["mean_promise"], sm["platform"]["mean_promise"])
        for t in (0, 5, 10):
            self.assertAlmostEqual(sm["late_rate_diff"][f"{t}min"]["diff"], 0.0)
        self.assertGreater(r["as_is"]["model"]["late_rate_0min"], r["as_is"]["platform"]["late_rate_0min"])


class TestRunner(unittest.TestCase):
    def test_every_model_runs_end_to_end(self):
        table = fake_table()
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.object(run, "RESULTS", Path(td)), mock.patch.object(run, "load_table", lambda: table):
            for model in ["median", "elasticnet", "hgb", "rf", "hgb_q80"]:
                run.main(["--model", model, "--name", model, "--param", "max_iter=20"] if model.startswith("hgb")
                         else ["--model", model, "--name", model])
                s = json.loads((Path(td) / "runs" / model / "summary.json").read_text())
                self.assertEqual(len(s["cv_mae_by_fold"]), 4, model)
            run.main(["--model", "median", "--eval", "test", "--name", "final"])
            pred = pd.read_parquet(Path(td) / "runs/final/predictions.parquet")
            self.assertEqual(set(pred["day"]), set(TEST_DAYS))
            median = json.loads((Path(td) / "runs/median/summary.json").read_text())["model"]["mae"]
            hgb = json.loads((Path(td) / "runs/hgb/summary.json").read_text())["model"]["mae"]
            self.assertLess(hgb, median)  # the fake target depends on distance, so boosting must win

    def test_final_builds_every_table_and_guards_the_test_days(self):
        from experiments import final
        table = fake_table()
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.object(final, "RESULTS", Path(td)), mock.patch.object(final, "load_table", lambda: table), \
                mock.patch.object(final, "TABLES_DIR", Path(td) / "tables"), \
                mock.patch.object(final, "FIGURES_DIR", Path(td) / "figures"), \
                mock.patch.object(final, "PARAMS_DIR", Path(td) / "params"):
            with self.assertRaises(SystemExit):
                final.main(["--eval", "test"])  # test days need --i-am-at-cp4
            self.assertFalse((Path(td) / "final" / "test").exists())
            final.main([])
            manifest = json.loads((Path(td) / "final/cv/manifest.json").read_text())
            self.assertEqual(set(manifest["models"]), {m["model"] for m in final.FINAL_MODELS})
            self.assertIn("Gradient boosting", (Path(td) / "tables/main_results_cv.tex").read_text())
            self.assertTrue((Path(td) / "tables/promise_test_cv.tex").exists())
            self.assertTrue((Path(td) / "figures/final_cv_gap.pdf").exists())

    def test_tune_writes_best_params(self):
        table = fake_table()
        with tempfile.TemporaryDirectory() as td, \
                mock.patch.object(tune, "RESULTS", Path(td)), mock.patch.object(tune, "load_table", lambda: table):
            tune.main(["--model", "elasticnet", "--n-iter", "2"])
            best = json.loads((Path(td) / "tuning/elasticnet_base.json").read_text())
        self.assertEqual(set(best["params"]), {"alpha", "l1_ratio"})


if __name__ == "__main__":
    unittest.main()

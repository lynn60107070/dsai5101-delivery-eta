"""Paths, dates and settings shared by everyone.

Change this file only with the whole team's agreement: every result depends on it.
"""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = REPO_ROOT / "data" / "raw"
DATA_PROCESSED = REPO_ROOT / "data" / "processed"
RESULTS = REPO_ROOT / "results"

# Meituan INFORMS TSL Research Challenge (CC BY-NC 4.0: link to it, never commit or share the CSV)
DATA_URL = ("https://github.com/meituan/Meituan-INFORMS-TSL-Research-Challenge/raw/main/"
            "all_waybill_info_meituan_0322.csv.zip")
RAW_CSV = DATA_RAW / "all_waybill_info_meituan_0322.csv"

SEED = 42
UTC_OFFSET_HOURS = 8  # timestamps are unix seconds; local time is China Standard Time (no DST)

# Time split from the proposal. `dt` is the dataset's day column; 17 Oct 2022 is a Monday,
# so the only weekend day in training is Sat 22 Oct.
TRAIN_DAYS = [20221017, 20221018, 20221019, 20221020, 20221021, 20221022]
TEST_DAYS = [20221023, 20221024]  # used once, at the end (CP4)

LATE_THRESHOLD_MIN = 5  # "late" = arrived more than 5 min after the prediction
QUANTILE = 0.8  # promise-setting model

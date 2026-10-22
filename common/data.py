"""Download the raw data and build the modelling table (shared; Lynn).

    from common.data import load_table
    df = load_table()                 # one row per accepted, non-pre-booked, plausible order
    df = load_table(modelling=False)  # every accepted order, with the is_prebook/implausible flags

The table is raw -> clean.clean() -> features.add_features(), cached in data/processed/.
The cache key is a hash of clean.py and features.py, so editing either file rebuilds it.
"""

import hashlib
import io
import urllib.request
import zipfile

import pandas as pd

from common import clean, features
from common.config import DATA_PROCESSED, DATA_RAW, DATA_URL, RAW_CSV


def download(force: bool = False):
    """Fetch the waybill CSV (~39 MB zip, ~122 MB unzipped) into data/raw/ if it is missing."""
    if RAW_CSV.exists() and not force:
        return RAW_CSV
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    print(f"downloading {DATA_URL} ...")
    with urllib.request.urlopen(DATA_URL) as response:
        archive = zipfile.ZipFile(io.BytesIO(response.read()))
    with archive.open(RAW_CSV.name) as src:
        RAW_CSV.write_bytes(src.read())
    return RAW_CSV


def load_raw() -> pd.DataFrame:
    """The CSV exactly as Meituan published it (654,343 rows: one per dispatch attempt)."""
    return pd.read_csv(download(), index_col=0)


def _cache_key() -> str:
    source = "".join(open(m.__file__, encoding="utf8").read() for m in (clean, features))
    return hashlib.sha1(source.encode()).hexdigest()[:10]


def load_table(modelling: bool = True, refresh: bool = False) -> pd.DataFrame:
    path = DATA_PROCESSED / f"orders_{_cache_key()}.parquet"
    if path.exists() and not refresh:
        df = pd.read_parquet(path)
    else:
        df = features.add_features(clean.clean(load_raw()))
        DATA_PROCESSED.mkdir(parents=True, exist_ok=True)
        for old in DATA_PROCESSED.glob("orders_*.parquet"):
            old.unlink()
        df.to_parquet(path, index=False)
    return clean.modelling_rows(df) if modelling else df

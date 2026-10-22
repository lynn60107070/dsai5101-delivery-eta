import os

# Below the core count, so joblib skips its physical-core probe (it fails noisily on Windows)
# and one core stays free for the rest of the laptop.
os.environ.setdefault("LOKY_MAX_CPU_COUNT", str(max(1, (os.cpu_count() or 2) - 1)))

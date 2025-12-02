import time
import numpy as np
import polars as pl
import torch

# ---------- Config ----------
N = 50_000_000        # for elementwise benchmarks
N_GROUP = 5_000_000   # for realistic groupby benchmark
NUM_SENSORS = 1_000   # unique sensor_ids


# ---------- A. Simple elementwise benchmarks ----------

def bench_python():
    data = [i * 0.5 for i in range(N)]
    t0 = time.time()
    out = [x * 1.2345 for x in data]
    return time.time() - t0


def bench_numpy():
    arr = np.random.rand(N)
    t0 = time.time()
    out = arr * 1.2345
    return time.time() - t0


def bench_polars():
    df = pl.DataFrame({"x": np.random.rand(N)})
    t0 = time.time()
    df2 = df.with_columns((pl.col("x") * 1.2345).alias("y"))
    return time.time() - t0


def bench_torch():
    tensor = torch.rand(N)
    t0 = time.time()
    out = tensor * 1.2345
    return time.time() - t0


# ---------- B. More realistic task: groupby mean ----------

def bench_python_groupby():
    """
    Pure Python:
    - Simulate N_GROUP sensor readings
    - Each has (sensor_id, value)
    - Compute mean value per sensor_id using dicts
    """
    import random

    # generate data
    data = [
        (random.randint(0, NUM_SENSORS - 1), random.random())
        for _ in range(N_GROUP)
    ]

    t0 = time.time()

    sums = {}
    counts = {}

    for sensor_id, value in data:
        if sensor_id in sums:
            sums[sensor_id] += value
            counts[sensor_id] += 1
        else:
            sums[sensor_id] = value
            counts[sensor_id] = 1

    means = {sid: sums[sid] / counts[sid] for sid in sums}

    elapsed = time.time() - t0
    # avoid “unused variable” optimisation (not really needed, but explicit)
    assert len(means) > 0
    return elapsed


def bench_polars_groupby():
    """
    Polars:
    - Same logical task as Python version
    - Use DataFrame + groupby + mean
    """
    df = pl.DataFrame(
        {
            "sensor_id": np.random.randint(0, NUM_SENSORS, size=N_GROUP),
            "value": np.random.rand(N_GROUP),
        }
    )

    t0 = time.time()
    result = (
        df
        .group_by("sensor_id")
        .agg(pl.col("value").mean())
    )
    elapsed = time.time() - t0
    # Avoid unused warning
    assert result.height > 0
    return elapsed


# ---------- Utilities ----------

def pretty_print(label, time_s, baseline):
    speedup = baseline / time_s
    print(f"{label:<18} {time_s:>8.4f} sec   ({speedup:>5.1f}× faster)")


# ---------- Main ----------

if __name__ == "__main__":
    print(f"\n⚡ Week 2 · Day 1 Benchmarks (N = {N:,})")
    print("--------------------------------------------")

    # Elementwise benchmarks
    t_python = bench_python()
    t_numpy = bench_numpy()
    t_polars = bench_polars()
    t_torch = bench_torch()

    print("\nA. Elementwise multiply (size N)")
    pretty_print("Python (loop)", t_python, t_python)
    pretty_print("NumPy", t_numpy, t_python)
    pretty_print("Polars", t_polars, t_python)
    pretty_print("PyTorch", t_torch, t_python)

    # Realistic groupby benchmark
    print(f"\nB. Realistic task: groupby mean over sensor_id (N_GROUP = {N_GROUP:,})")
    t_py_grp = bench_python_groupby()
    t_pl_grp = bench_polars_groupby()

    pretty_print("Python groupby", t_py_grp, t_py_grp)
    pretty_print("Polars groupby", t_pl_grp, t_py_grp)

    print("\nDone.\n")
#!/usr/bin/env python
"""
Week 2 Benchmark Script

Benchmarks:
- Pandas vs Polars CSV read
- Pandas vs Polars Parquet write
- Pandas vs Polars Parquet read
- Simple groupby/agg workload

If no CSV exists at DATA_CSV, a synthetic sensor CSV is generated first.
"""

import os
import time
from pathlib import Path
from statistics import mean

import pandas as pd
import polars as pl

# psutil is optional – if not installed, we skip memory metrics
try:
    import psutil
    HAVE_PSUTIL = True
except ImportError:
    HAVE_PSUTIL = False

# -----------------------------
# CONFIG – tweak paths if needed
# -----------------------------
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

DATA_CSV = DATA_DIR / "sensor_log.csv"          # synthetic or real CSV
PANDAS_PARQUET = DATA_DIR / "sensor_pandas.parquet"
POLARS_PARQUET = DATA_DIR / "sensor_polars.parquet"

N_ROWS_SYNTHETIC = 1_000_000  # rows for synthetic dataset
N_RUNS = 3                    # how many times to repeat each benchmark


# -----------------------------
# Helpers
# -----------------------------
def mb(val: int) -> float:
    return val / (1024 ** 2)


def measure(op_name: str, lib: str, fn, *args, **kwargs):
    """
    Measure wall-clock time (and optional memory) for a function.
    Returns dict with metrics.
    """
    mem_before = mem_after = None
    if HAVE_PSUTIL:
        proc = psutil.Process(os.getpid())
        mem_before = proc.memory_info().rss

    t0 = time.perf_counter()
    result = fn(*args, **kwargs)
    t1 = time.perf_counter()

    if HAVE_PSUTIL:
        mem_after = proc.memory_info().rss

    return {
        "operation": op_name,
        "library": lib,
        "time_s": t1 - t0,
        "mem_before_mb": mb(mem_before) if mem_before is not None else None,
        "mem_after_mb": mb(mem_after) if mem_after is not None else None,
    }, result


def print_table(rows):
    """
    Print a simple text table from list of dicts.
    """
    if not rows:
        print("No results to display.")
        return

    # Columns in desired order
    cols = ["operation", "library", "time_s", "mem_before_mb", "mem_after_mb"]

    # Header
    header = " | ".join(f"{c:>14}" for c in cols)
    sep = "-" * len(header)
    print(sep)
    print(header)
    print(sep)

    for r in rows:
        line = " | ".join(
            f"{(r[c] if r[c] is not None else '-'):>14.4f}"
            if isinstance(r[c], (int, float))
            else f"{str(r[c]):>14}"
            for c in cols
        )
        print(line)
    print(sep)


def write_markdown_summary(rows, path: Path):
    """
    Write a Markdown summary you can paste into your README.
    """
    by_op = {}
    for r in rows:
        key = (r["operation"], r["library"])
        by_op.setdefault(key, []).append(r)

    lines = []
    lines.append("# Week 2 Pipeline Benchmarks\n")
    lines.append(f"- Rows: ~{N_ROWS_SYNTHETIC:,}")
    lines.append(f"- Runs per test: {N_RUNS}")
    lines.append(f"- Host: Raspberry Pi 5 (your setup)\n")
    lines.append("| Operation | Library | Avg Time (s) | Avg Mem Before (MB) | Avg Mem After (MB) |")
    lines.append("|-----------|---------|--------------|----------------------|---------------------|")

    for (op, lib), samples in sorted(by_op.items()):
        avg_t = mean(s["time_s"] for s in samples)
        if HAVE_PSUTIL:
            avg_mb_before = mean(s["mem_before_mb"] for s in samples)
            avg_mb_after = mean(s["mem_after_mb"] for s in samples)
        else:
            avg_mb_before = avg_mb_after = None

        lines.append(
            f"| {op} | {lib} | {avg_t:.4f} | "
            f"{(f'{avg_mb_before:.1f}' if avg_mb_before is not None else '-')} | "
            f"{(f'{avg_mb_after:.1f}' if avg_mb_after is not None else '-')} |"
        )

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"\nMarkdown summary written to: {path}")


# -----------------------------
# Synthetic data generation
# -----------------------------
def generate_synthetic_csv(path: Path, n_rows: int):
    """
    Generate a synthetic sensor CSV if none exists.
    Columns: timestamp, accel_x, accel_y, accel_z, gyro_x, gyro_y, gyro_z, temp_c
    """
    import numpy as np

    print(f"[INFO] Generating synthetic CSV at {path} with {n_rows:,} rows...")
    ts = pd.date_range("2023-01-01", periods=n_rows, freq="10ms")
    data = {
        "timestamp": ts.astype("int64") / 1e9,  # seconds
        "accel_x": np.random.normal(0, 1, n_rows),
        "accel_y": np.random.normal(0, 1, n_rows),
        "accel_z": np.random.normal(9.81, 0.1, n_rows),
        "gyro_x": np.random.normal(0, 0.05, n_rows),
        "gyro_y": np.random.normal(0, 0.05, n_rows),
        "gyro_z": np.random.normal(0, 0.05, n_rows),
        "temp_c": np.random.normal(25, 1, n_rows),
    }
    df = pd.DataFrame(data)
    path.parent.mkdir(exist_ok=True)
    df.to_csv(path, index=False)
    print("[INFO] Synthetic CSV generated.")


# -----------------------------
# Benchmark routines
# -----------------------------
def benchmark_all():
    results = []

    # 1. Ensure CSV exists
    if not DATA_CSV.exists():
        generate_synthetic_csv(DATA_CSV, N_ROWS_SYNTHETIC)
    else:
        print(f"[INFO] Using existing CSV at {DATA_CSV}")

    # 2. CSV read: Pandas vs Polars
    print("\n[STEP] Benchmarking CSV read...")

    for i in range(N_RUNS):
        r, df_pd = measure("read_csv", "pandas", pd.read_csv, DATA_CSV)
        results.append(r)

        r, df_pl = measure("read_csv", "polars", pl.read_csv, DATA_CSV)
        results.append(r)

    # 3. Parquet write: Pandas vs Polars
    print("\n[STEP] Benchmarking Parquet write...")

    # Use the last-read dataframes
    for i in range(N_RUNS):
        r, _ = measure("to_parquet", "pandas", df_pd.to_parquet, PANDAS_PARQUET)
        results.append(r)

        r, _ = measure("to_parquet", "polars", df_pl.write_parquet, POLARS_PARQUET)
        results.append(r)

    # 4. Parquet read: Pandas vs Polars
    print("\n[STEP] Benchmarking Parquet read...")

    for i in range(N_RUNS):
        r, _ = measure("read_parquet", "pandas", pd.read_parquet, PANDAS_PARQUET)
        results.append(r)

        r, _ = measure("read_parquet", "polars", pl.read_parquet, POLARS_PARQUET)
        results.append(r)

    # 5. Simple workload: groupby + aggregation
    print("\n[STEP] Benchmarking groupby/agg workload...")

    # Add a simple "bucket" column for grouping, in both frames
    df_pd["bucket"] = (df_pd["timestamp"] // 1).astype(int)
    df_pl = df_pl.with_columns((pl.col("timestamp") // 1).cast(pl.Int64).alias("bucket"))

    def pandas_groupby():
        return df_pd.groupby("bucket").agg(
            {
                "accel_x": "mean",
                "accel_y": "mean",
                "accel_z": "mean",
                "gyro_x": "mean",
                "gyro_y": "mean",
                "gyro_z": "mean",
            }
        )

    def polars_groupby():
        return (
            df_pl
            .group_by("bucket")
            .agg(
                [
                    pl.col("accel_x").mean(),
                    pl.col("accel_y").mean(),
                    pl.col("accel_z").mean(),
                    pl.col("gyro_x").mean(),
                    pl.col("gyro_y").mean(),
                    pl.col("gyro_z").mean(),
                ]
            )
        )

    for i in range(N_RUNS):
        r, _ = measure("groupby_mean", "pandas", pandas_groupby)
        results.append(r)

        r, _ = measure("groupby_mean", "polars", polars_groupby)
        results.append(r)

    return results


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    print("=== Week 2 Pipeline Benchmarks ===")
    if not HAVE_PSUTIL:
        print("[WARN] psutil not installed – memory stats will be '-'.")

    res = benchmark_all()

    # Print raw samples
    print("\n=== Raw Samples ===")
    print_table(res)

    # Write Markdown summary for README
    write_markdown_summary(res, Path("benchmarks_week2.md"))
    
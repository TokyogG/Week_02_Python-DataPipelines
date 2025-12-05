# Day 1 — Vectorization Benchmarks

This folder contains the Day 1 work for **Week 2: Modern Python Data Pipelines**.

The goal of Day 1 was to compare different compute backends and understand why vectorized operations are critical for edge workloads.

## Benchmarks Included

### 1. Elementwise Multiply (N = 50,000,000)
We compare:
- Pure Python loops
- NumPy (SIMD-optimized)
- Polars (Apache Arrow + Rust)
- PyTorch (tensor engine)

### 2. Realistic Sensor Analytics
Group 5 million synthetic sensor readings by `sensor_id` and compute the mean.

## Summary of Findings

| Method        | Time (sec) | Speed-up vs Python |
|---------------|------------|--------------------|
| Python loop   | 1.97 s     | 1×                 |
| NumPy         | 0.11 s     | 17.5×              |
| Polars        | 0.12 s     | 16.6×              |
| PyTorch       | 0.07 s     | **28×**            |

Polars is also **10× faster** than Python for realistic groupby workloads.

## Why This Matters

These speedups demonstrate why edge AI data pipelines should rely on:
- **NumPy or PyTorch** for pure tensor math  
- **Polars** for dataframe processing  
- **Never pure Python loops**  

## Files


### **Modern Python Vectorization & Data Pipeline Benchmarks**

*Part of the 16-Week Edge AI Engineering Bootcamp*

---

## 🎯 **Goal**

Understand and benchmark the performance differences between:

* **Pure Python loops**
* **NumPy** (C + SIMD)
* **Polars** (Rust + Apache Arrow + multithreading)
* **PyTorch** (tensor engine)

Tasks:

1. **Elementwise multiply** on arrays of size **N = 50,000,000**
2. **Realistic workload**: Group sensor readings by `sensor_id` and compute mean
   (5,000,000 rows, 1,000 sensor IDs)

This establishes why vectorized, columnar, and tensor-based operations are essential for **edge data pipelines**.

---
### Repo Structure

```bash
Week_02_Python-DataPipelines/
├── src/
│   ├── sensors/
│   │   └── mpu6050.py          # Thin wrapper around MPU6050 driver
│   └── pipelines/
│       └── parquet_writer.py   # Chunked Parquet writer using Polars
├── data/
│   └── parquet/                # Logged IMU chunks (Day 2)
├── logger_v2.py                # 20 Hz streaming logger → Parquet
├── live_dashboard.py           # Basic Parquet-backed dashboard
├── live_dashboard_pro.py       # Direct-streaming PRO demo (dark mode, 3D cube)
└── README.md

---

# 🧪 **A. Elementwise Multiply (N = 50,000,000)**

| Method        | Time (sec) | Speed-up vs Python |
| ------------- | ---------- | ------------------ |
| Python (loop) | **1.9672** | 1.0×               |
| NumPy         | **0.1124** | 17.5×              |
| Polars        | **0.1187** | 16.6×              |
| PyTorch       | **0.0703** | 28.0×              |

### 🔍 **Interpretation**

* **Python loops** scale linearly and quickly saturate CPU.
* **NumPy** and **PyTorch** leverage **contiguous memory + SIMD**, making them drastically faster.
* **Polars**, although a DataFrame engine, catches up at large N (the DataFrame overhead becomes negligible).
* **PyTorch** is fastest because it uses highly optimized tensor kernels.

**Conclusion:**
For raw numeric transforms on large arrays, NumPy/Polars/PyTorch deliver **16–28× speedups** over Python.

---

# 🧪 **B. Realistic Task — GroupBy Mean (5,000,000 sensor readings)**

| Method                      | Time (sec) | Speed-up vs Python |
| --------------------------- | ---------- | ------------------ |
| Python groupby (dict-based) | **1.4242** | 1.0×               |
| Polars groupby              | **0.1375** | 10.4×              |

### 🔍 **Interpretation**

* Pure Python requires manual dictionary accumulation — **slow, single-threaded**, no SIMD.
* **Polars** uses:

  * Rust
  * Apache Arrow columnar memory
  * Multithreading (Rayon)
  * SIMD vectorization
* It completes the same task **10.4× faster**, even with only 1,000 group keys.

This is where Polars shines: realistic analytics workloads, not just toy elementwise ops.

---

# 🧠 **Why This Matters for Edge AI Pipelines**

Your workload in the Edge AI Bootcamp (and in your railway sensor projects) involves:

* Large, continuous sensor streams
* Timestamp alignment
* Grouping / averaging / window filters
* Multi-sensor joins
* Parquet I/O
* Post-processing for ML and quantized inference

These are EXACTLY the operations where Polars is engineered to win.

**This benchmark demonstrates:**

| Task Type                               | Best Tool       | Why                        |
| --------------------------------------- | --------------- | -------------------------- |
| pure math on huge arrays                | PyTorch / NumPy | optimal SIMD kernels       |
| dataframe analytics, groupby, windowing | Polars          | Rust engine, multithreaded |
| Python loops                            | ❌ never use     | no SIMD, slow              |

---

# 📁 **Files in This Folder**

```
Week_02/
  Day_01/
    benchmarks.py     # Runs all benchmarks end-to-end
    README.md         # (this file)
```

---

# ▶️ **How to Run**

```
python benchmarks.py
```

Runs all tests:

* Elementwise vectorization benchmarks
* Realistic sensor-grouping benchmark

---

# 🏁 **Summary**

* Python loops: **too slow for edge workloads**
* NumPy: **strong baseline**, SIMD-enabled
* PyTorch: **fastest for raw tensor ops**
* Polars: **best for real multi-column analytics**, 10× faster groupbys
* For your edge pipelines, Polars + PyTorch form the ideal foundation.

---

## Day 2 – Real-Time Sensor Pipeline + Dashboards

**Goal:** Turn a simple IMU logger into a modern, efficient data pipeline with live visualization.

### What I Built

- **Streaming logger (`logger_v2.py`)**
  - Reads MPU6050 IMU over I²C at **20 Hz**
  - Buffers samples in memory and writes **chunked Parquet** files (`data/parquet/`)
  - Uses **Polars** for fast DataFrame handling
  - Designed to keep RAM and CPU usage low on a Raspberry Pi 5

- **Student dashboard (`live_dashboard.py`)**
  - Reads latest Parquet chunk(s) with Polars
  - Dash + Plotly app with:
    - Live plot of `accel_x` (and optionally other axes)
    - Rolling window of recent samples
  - Updates every 0.5 s (Dash `Interval` callback)

- **Pro dashboard (`live_dashboard_pro.py`) – demo only**
  - **No disk I/O**: talks directly to the MPU6050 in a background thread
  - Keeps a rolling **10 second ring buffer** in RAM (deque)
  - Dark-mode Dash UI with:
    - KPI cards:
      - RMS Accel (m/s²)
      - Peak Gyro (°/s)
      - Temperature (°C)
      - Motion state: `STILL / MOVING / SHAKING`
    - 3 stacked time-series plots:
      - Acceleration (x, y, z)
      - Gyro (x, y, z)
      - Temperature
    - 3D **orientation cube** driven by accelerometer-based pitch/roll
  - Runs at ~5–10 FPS, fully interactive in the browser

### How to Run

#### 1. Logger + basic dashboard (student version)

```bash
# Terminal 1 – logger
cd ~/EdgeAI_Bootcamp/Week_02_Python-DataPipelines
python logger_v2.py

# Terminal 2 – basic dashboard
cd ~/EdgeAI_Bootcamp/Week_02_Python-DataPipelines
python live_dashboard.py

# If running Pro Dashboard there is not need to run logger but note that no parquet files are kept
# It's more of a showcase of what can be presented

cd ~/EdgeAI_Bootcamp/Week_02_Python-DataPipelines
python live_dashboard_pro.py


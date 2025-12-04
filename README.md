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

## Day 3 Quantization performance results

### TinyNet – Dynamic Quantization (PyTorch)

| Model        | Type   | Avg Latency (ms) | Speedup |
|-------------|--------|------------------|---------|
| TinyNet     | FP32   | 0.2805           | 1.00×   |
| TinyNet     | INT8   | 0.2285           | 1.23×   |

On a tiny fully-connected network, dynamic INT8 quantization gives ~20% speedup on the Pi 5 CPU. Larger models (e.g. MobileNet) and batched inputs should show bigger gains

### BiggerNet – Dynamic Quantization (PyTorch)

| Model        | Type   | Avg Latency (ms) | Speedup  |
|--------------|--------|------------------|----------|
| BiggerNet    | FP32   | 1.3467           | 1.00×    |
| BiggerNet    | INT8   | 0.4190           | **3.21×**|

Quantizing a larger FC model produces a 3.2× speedup on the Pi 5. This matches expected INT8 gains and confirms that quantization benefits grow significantly with model size

## 🔢 Quantization Methods — Comparison Table

| Method | What Gets Quantized | Accuracy | Speedup | Memory Reduction | Calibration Needed | Best For |
|--------|----------------------|----------|---------|------------------|---------------------|----------|
| **Dynamic Quantization** | Weights (INT8), activations stay FP32 | ⭐⭐☆☆ (Moderate) | ⭐⭐☆☆ (~1.2–2×) | ⭐⭐☆☆ (≈4× smaller weights) | ❌ No | LLMs, Transformers on CPU, fast prototyping |
| **Static PTQ (Post-Training Quantization)** | Weights + activations (INT8) | ⭐⭐⭐☆ (Good) | ⭐⭐⭐☆ (~1.5–3×) | ⭐⭐⭐⭐ (4× smaller model + smaller activations) | ✔️ Yes (small calibration dataset) | CNNs, MobileNet, ResNet, image models |
| **QAT (Quantization-Aware Training)** | Weights + activations (INT8 simulated during training) | ⭐⭐⭐⭐ (Best) | ⭐⭐⭐⭐ (~2–4×) | ⭐⭐⭐⭐ (4× smaller) | ✔️ Yes (training/fine-tuning) | Production-grade edge AI, MCUs, NPUs, tiny models |
| **INT4 Quantization** | Weights (INT4) + optional activations | ⭐⭐☆☆ to ⭐⭐⭐☆ | ⭐⭐⭐⭐ (~3–5×) | ⭐⭐⭐⭐⭐ (8× smaller) | Depends (dynamic or PTQ) | LLMs on CPU/GPU, memory-constrained models |
| **Mixed-Precision (FP16 + INT8)** | Critical layers FP16, others INT8 | ⭐⭐⭐⭐ (Very high) | ⭐⭐⭐☆ (~1.5–2.5×) | ⭐⭐⭐☆ (2×–3×) | Optional | Models that lose too much accuracy in full INT8 |

### Notes
- **QAT provides the best accuracy** and is preferred for edge deployments (Pi, Hailo, NPUs, MCUs).
- **PTQ requires a small “calibration set”** (100–1000 samples) to map activation ranges.
- **Dynamic quantization is the easiest** but gives the smallest gains.
- **INT4** is becoming the standard for LLMs when memory is tight.
- **Speedups vary by hardware** (ARM CPUs ≈ 1.3–3×, NPUs ≈ 5–10×).
- **Per-channel INT8** for weights produces significantly better accuracy than per-tensor.
- **Symmetric weights, asymmetric activations** is the industry standard layout.

### Recommended Quantization Path for Edge AI
1. **Start with Dynamic Quantization** → quick size/latency check.
2. **Move to Static PTQ** → get INT8 activations + lower latency.
3. **Finish with QAT** → maximize accuracy for deployment to Pi/Hailo/MCU.


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
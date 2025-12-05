
---

# ✅ **`day3_quant/README.md` (simple + clean)**

```markdown
# Day 3 — Quantization (TinyNet & BiggerNet)

This folder contains the Day 3 work for **Week 2: Modern Python Data Pipelines**.

The focus was on **dynamic INT8 quantization** using PyTorch and benchmarking the impact on latency and model size.

## Models Quantized
### 1. TinyNet
A very small fully connected network used to demonstrate the basics of quantization.

### 2. BiggerNet
A larger FC model that shows how quantization benefits increase with model size.

## Results

### TinyNet — Dynamic Quantization

| Model    | Type | Latency (ms) | Speedup |
|----------|------|--------------|---------|
| FP32     | —    | 0.2805       | 1×      |
| INT8     | —    | 0.2285       | 1.23×   |

### BiggerNet — Dynamic Quantization

| Model      | Type | Latency (ms) | Speedup |
|------------|------|--------------|---------|
| FP32       | —    | 1.3467       | 1×      |
| INT8       | —    | 0.4190       | **3.21×** |

## Notes

- Dynamic quantization quantizes **weights** to INT8 while keeping **activations** FP32.
- Very easy to apply — no calibration dataset required.
- Speedup tends to grow with model size.

## Files
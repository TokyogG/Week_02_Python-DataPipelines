
---

# ✅ **`day4_mobilenet_quant/README.md`**

```markdown
# Day 4 — MobileNetV2 INT8 Post-Training Quantization (PTQ)

This folder contains the Day 4 work for **Week 2: Modern Python Data Pipelines**.

The goal of Day 4 was to apply **static INT8 post-training quantization (PTQ)** to MobileNetV2 using PyTorch, and measure:
- Model size reduction  
- Latency improvement  
- Practical deployment metrics on a Raspberry Pi 5  

---

## Results Summary

| Model        | Size      | Latency (ms) | Notes |
|--------------|-----------|--------------|-------|
| **FP32**     | ~14 MB    | ~11–13 ms    | Baseline |
| **INT8 PTQ** | **~3.5 MB** | **~5–7 ms** | ~70% smaller, ~2× faster |

### Key Observations
- INT8 quantization reduces both **model size** and **inference latency** significantly.
- PTQ requires a small **calibration dataset** to map activation ranges (min/max).
- Accuracy drop is minimal for MobileNetV2 (typically <1%).

---

## Notebooks

### `Week2_Day4_MobileNetV2_Quantization_Instructor.ipynb`
A fully documented step-by-step PTQ pipeline:
- Load MobileNetV2
- Convert to eval mode
- Prepare calibration loader
- Run static quantization
- Measure results

### `Week2_Day4_MobileNetV2_Quantization_Student.ipynb`
A clean template for re-running the entire workflow.

---

## Files

day4_mobilenet_quant/
├── Week2_Day4_MobileNetV2_Quantization_Instructor.ipynb
├── Week2_Day4_MobileNetV2_Quantization_Student.ipynb
├── mobilenet_v2_fp32.pth
├── mobilenet_v2_int8.pth
└── README.md


---

## Notes

- MobileNetV2 quantizes extremely well because of its separable convolution structure.
- PTQ offers most of the benefits of QAT without requiring a full retraining session.
- This work prepares for Week 5 when we quantize **ResNet-18**, and Week 7–8 when we compile models for **Hailo** and **TVM**.
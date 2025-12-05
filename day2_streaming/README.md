# Day 2 — Real-Time Sensor Pipeline & Dashboards

This folder contains the Day 2 work for **Week 2: Modern Python Data Pipelines**.

The goal of Day 2 was to build a modern, efficient **real-time data pipeline** on the Raspberry Pi 5 with:
- 20 Hz sensor ingestion
- Chunked Parquet storage
- Live dashboards using Dash + Plotly
- Low CPU / low RAM operation

---

## Components

### 1. `logger_v2.py`  
A real-time IMU sensor logger (MPU6050) that:
- Reads accelerometer, gyro, and temperature at **20 Hz**
- Uses Polars for DataFrame handling  
- Writes **chunked Parquet** files to `data/parquet/`
- Keeps CPU use low on the Pi 5

### 2. `live_dashboard.py` (Student Version)
- Reads the most recent Parquet chunk(s)
- Updates live plots every 0.5 seconds
- Displays:
  - Accelerometer axes  
  - Gyroscope axes  
  - Optional temperature  
- Simple, clean Dash layout

### 3. `live_dashboard_pro.py` (Pro Demo)
A more advanced “demo” dashboard:
- **Direct-streaming** (no disk I/O)
- Background thread to read MPU6050
- Rolling **10-second ring buffer**
- Dark-mode UI with:
  - KPI cards (RMS accel, peak gyro, temperature)
  - Stacked accel/gyro/temp plots
  - 3D orientation cube
- Typically runs at **5–10 FPS**

---

## Screenshot

![Live Dashboard Demo](dashboard.png)

---

## How to Run

### Logger + Basic Dashboard

```bash
# Terminal 1 – run the logger
python logger_v2.py

# Terminal 2 – run the basic dashboard
python live_dashboard.py
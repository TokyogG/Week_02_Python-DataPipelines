import time
import polars as pl
from datetime import datetime

from src.sensors.mpu6050 import MPU6050
from src.pipelines.parquet_writer import ParquetWriter


SAMPLE_RATE = 20           # Hz
CHUNK_SIZE = 200           # 200 samples per Parquet file
OUTPUT_DIR = "data/parquet"

def main():
    sensor = MPU6050()
    writer = ParquetWriter(output_dir=OUTPUT_DIR, chunk_size=CHUNK_SIZE)

    buffer = []
    period = 1.0 / SAMPLE_RATE

    print(f"Logging at {SAMPLE_RATE} Hz...")

    while True:
        ts = datetime.utcnow().isoformat()
        reading = sensor.read()

        buffer.append({
            "timestamp": ts,
            **reading
        })

        if len(buffer) >= CHUNK_SIZE:
            df = pl.DataFrame(buffer)
            writer.write_chunk(df)
            buffer = []

        time.sleep(period)


if __name__ == "__main__":
    main()
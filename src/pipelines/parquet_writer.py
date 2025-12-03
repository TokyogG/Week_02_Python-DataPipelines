import os
import polars as pl
from datetime import datetime

class ParquetWriter:
    def __init__(self, output_dir="data/parquet", chunk_size=200):
        self.output_dir = output_dir
        self.chunk_size = chunk_size
        os.makedirs(output_dir, exist_ok=True)

    def write_chunk(self, df: pl.DataFrame):
        fname = datetime.utcnow().strftime("%Y%m%d_%H%M%S_%f") + ".parquet"
        path = os.path.join(self.output_dir, fname)
        df.write_parquet(path)
        print(f"▶ Saved chunk: {path}")

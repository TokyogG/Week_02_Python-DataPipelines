# Week 2 Pipeline Benchmarks

- Rows: ~1,000,000
- Runs per test: 3
- Host: Raspberry Pi 5 (your setup)

| Operation | Library | Avg Time (s) | Avg Mem Before (MB) | Avg Mem After (MB) |
|-----------|---------|--------------|----------------------|---------------------|
| groupby_mean | pandas | 0.0689 | 1030.6 | 1040.1 |
| groupby_mean | polars | 0.0558 | 1040.1 | 1066.4 |
| read_csv | pandas | 1.5653 | 303.9 | 325.1 |
| read_csv | polars | 0.1974 | 284.4 | 471.2 |
| read_parquet | pandas | 0.1336 | 635.9 | 777.1 |
| read_parquet | polars | 0.0848 | 777.1 | 826.5 |
| to_parquet | pandas | 1.1427 | 424.4 | 415.3 |
| to_parquet | polars | 1.6016 | 415.3 | 428.4 |
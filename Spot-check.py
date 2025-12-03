import polars as pl, glob

f = sorted(glob.glob("data/parquet/*.parquet"))[-1]
df = pl.read_parquet(f)
print(f, df.shape)
print(df.head())

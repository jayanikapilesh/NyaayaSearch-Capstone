import duckdb
result = duckdb.sql("SELECT * FROM read_parquet('data/case_law/raw/metadata_1950.parquet')")
print(result.columns)

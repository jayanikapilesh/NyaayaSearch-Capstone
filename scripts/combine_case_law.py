import duckdb

query = """
SELECT *
FROM read_parquet([
    'data/case_law/raw/metadata_1950.parquet',
    'data/case_law/raw/metadata_1951.parquet'
])
"""

result = duckdb.sql(query)

output = "data/case_law/processed/case_law_1950_1951.csv"
result.write_csv(output)

print("Combined cases:", result.shape[0])
print("Columns:", result.shape[1])
print("Saved to:", output)
import duckdb

url = "https://indian-supreme-court-judgments.s3.ap-south-1.amazonaws.com/metadata/parquet/year=1950/metadata.parquet"

result = duckdb.sql(
    f"SELECT * FROM read_parquet('{url}') LIMIT 3"
)

print(result)
import duckdb

files = [
    f"data/case_law/raw/metadata_{year}.parquet"
    for year in range(2015, 2026)
]

result = duckdb.sql(
    f"""
    SELECT *
    FROM read_parquet({files})
    ORDER BY year, decision_date
    """
)

output = "data/case_law/processed/case_law_2015_2025.csv"
result.write_csv(output)

print("Combined cases:", result.shape[0])
print("Columns:", result.shape[1])
print("Saved to:", output)
import duckdb
result = duckdb.sql("SELECT year, COUNT(*) AS cases FROM read_csv_auto('data/case_law/processed/case_law_2015_2025.csv') GROUP BY year ORDER BY year")
print(result)

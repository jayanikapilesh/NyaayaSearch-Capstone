import duckdb

result = duckdb.sql("""
SELECT court, COUNT(*) AS cases
FROM read_csv_auto('data/case_law/processed/case_law_2015_2025_clean.csv')
GROUP BY court
ORDER BY cases DESC
""")

print(result)
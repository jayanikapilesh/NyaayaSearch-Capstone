import duckdb
result = duckdb.sql("SELECT * FROM read_csv_auto('data/case_law/processed/case_law_2015_2025.csv') WHERE year = 2014")
print(result)

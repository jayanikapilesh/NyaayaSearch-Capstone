import duckdb

input_file = "data/case_law/processed/case_law_2015_2025.csv"
output_file = "data/case_law/processed/case_law_2015_2025_clean.csv"

result = duckdb.sql(
    f"""
    SELECT *
    FROM read_csv_auto('{input_file}')
    WHERE year BETWEEN 2015 AND 2025
    ORDER BY year, decision_date
    """
)

result.write_csv(output_file)

print("Cleaned cases:", result.shape[0])
print("Saved to:", output_file)
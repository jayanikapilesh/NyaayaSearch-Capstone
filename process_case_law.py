import duckdb
result = duckdb.sql("SELECT title, petitioner, respondent, description, judge, author_judge, citation, case_id, cnr, decision_date, disposal_nature, court, available_languages, path, year FROM read_parquet('data/case_law/raw/metadata_1950.parquet')")
result.write_csv('data/case_law/processed/case_law_1950.csv')
print('Saved:', result.shape)

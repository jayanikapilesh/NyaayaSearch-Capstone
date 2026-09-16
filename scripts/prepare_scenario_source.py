import csv
import openpyxl

input_file = "Legal_Knowledge_Base_combined.xlsx"
output_file = "data/scenarios/processed/scenario_source_sections.csv"

workbook = openpyxl.load_workbook(input_file, read_only=True)
sheet = workbook.active

rows = []

for row in sheet.iter_rows(min_row=2, values_only=True):
    rows.append({
        "law_id": row[0],
        "domain": row[1],
        "act_name": row[2],
        "act_number": row[3],
        "section_number": row[4],
        "section_title": row[5],
        "legal_text": row[6],
        "jurisdiction": row[7],
        "source_url": row[10]
    })

fieldnames = [
    "law_id",
    "domain",
    "act_name",
    "act_number",
    "section_number",
    "section_title",
    "legal_text",
    "jurisdiction",
    "source_url"
]

with open(output_file, "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print("Scenario source created successfully!")
print("Legal sections:", len(rows))
print("Saved to:", output_file)
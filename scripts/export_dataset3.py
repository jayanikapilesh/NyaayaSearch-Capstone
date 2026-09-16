import csv
import json

input_file = "data/scenarios/processed/scenario_multilingual.json"
output_file = "data/scenarios/processed/dataset3_multilingual_legal_scenarios.csv"

with open(input_file, "r", encoding="utf-8") as file:
    records = json.load(file)

fieldnames = [
    "scenario_id",
    "domain",
    "user_query",
    "language",
    "act_name",
    "section_number",
    "section_title",
    "plain_explanation",
    "what_to_do_next",
    "source_url"
]

with open(output_file, "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()

    for index, record in enumerate(records, start=1):
        writer.writerow({
            "scenario_id": f"SC-{index:05d}",
            "domain": record["domain"],
            "user_query": record["user_query"],
            "language": record["language"],
            "act_name": record["act_name"],
            "section_number": record["section_number"],
            "section_title": record["section_title"],
            "plain_explanation": "",
            "what_to_do_next": "",
            "source_url": record["source_url"]
        })

print("Dataset 3 CSV created successfully!")
print("Records:", len(records))
print("Columns:", len(fieldnames))
print("Languages:", sorted(set(r["language"] for r in records)))
print("Saved to:", output_file)
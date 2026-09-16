import csv
import json
import re

input_file = "data/scenarios/processed/scenario_source_sections.csv"
output_file = "data/scenarios/processed/legal_concepts.json"

with open(input_file, "r", encoding="utf-8-sig") as file:
    sections = list(csv.DictReader(file))

concepts = []

for section in sections:
    title = section["section_title"].strip()
    legal_text = section["legal_text"].strip()

    # Create a simple concept from the section title.
    concept = re.sub(r"\s+", " ", title)
    concept = concept.rstrip(".")

    concepts.append({
        "law_id": section["law_id"],
        "domain": section["domain"],
        "act_name": section["act_name"],
        "section_number": section["section_number"],
        "section_title": title,
        "legal_concept": concept,
        "legal_text": legal_text,
        "source_url": section["source_url"]
    })

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(concepts, file, indent=2, ensure_ascii=False)

print("Legal concepts created successfully!")
print("Concepts:", len(concepts))
print("Acts:", len(set(x["act_name"] for x in concepts)))
print("Saved to:", output_file)
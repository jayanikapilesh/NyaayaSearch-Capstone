import json

input_file = "data/scenarios/processed/legal_concepts.json"
output_file = "data/scenarios/processed/scenario_sections_classified.json"

with open(input_file, "r", encoding="utf-8") as file:
    sections = json.load(file)

# Only clearly non-scenario structural provisions are excluded.
# Rights, offences, remedies, authorities, commissions, procedures,
# and citizen-facing legal powers remain scenario-worthy.

exclude_exact = {
    ("Consumer Protection Act, 2019", "1"),
    ("Consumer Protection Act, 2019", "2"),
    ("Consumer Protection Act, 2019", "4"),
    ("Consumer Protection Act, 2019", "5"),
    ("Consumer Protection Act, 2019", "7"),
    ("Consumer Protection Act, 2019", "9"),
    ("Consumer Protection Act, 2019", "26"),
    ("Consumer Protection Act, 2019", "27"),
    ("Consumer Protection Act, 2019", "64"),

    ("Transfer of Property Act, 1882", "1"),
    ("Transfer of Property Act, 1882", "104"),

    ("Bharatiya Nyaya Sanhita, 2023", "1"),
    ("Bharatiya Nyaya Sanhita, 2023", "2"),
}

scenario_sections = []
non_scenario_sections = []

for section in sections:
    key = (
        section["act_name"],
        str(section["section_number"])
    )

    if key in exclude_exact:
        record = {
            **section,
            "scenario_worthy": False,
            "classification_reason": "Clearly structural, definitional, or rule-making provision"
        }
        non_scenario_sections.append(record)
    else:
        record = {
            **section,
            "scenario_worthy": True,
            "classification_reason": "Potential citizen-facing legal scenario"
        }
        scenario_sections.append(record)

result = {
    "total_sections": len(sections),
    "scenario_worthy_sections": len(scenario_sections),
    "non_scenario_sections": len(non_scenario_sections),
    "scenario_sections": scenario_sections,
    "non_scenario_sections": non_scenario_sections
}

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(result, file, indent=2, ensure_ascii=False)

print("Scenario section classification completed!")
print("Total sections:", len(sections))
print("Scenario-worthy sections:", len(scenario_sections))
print("Non-scenario sections:", len(non_scenario_sections))
print("Saved to:", output_file)
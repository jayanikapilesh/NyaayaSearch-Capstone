import json

input_file = "data/scenarios/processed/legal_concepts.json"
output_file = "data/scenarios/processed/scenario_templates.json"

with open(input_file, "r", encoding="utf-8") as file:
    concepts = json.load(file)

templates = [
    {
        "template_type": "problem",
        "template": "I am facing a problem related to {concept}. What does the law say?"
    },
    {
        "template_type": "rights",
        "template": "What are my rights regarding {concept}?"
    },
    {
        "template_type": "action",
        "template": "What should I do if I am affected by an issue involving {concept}?"
    },
    {
        "template_type": "complaint",
        "template": "Where can I complain about an issue involving {concept}?"
    },
    {
        "template_type": "procedure",
        "template": "What is the legal procedure for {concept}?"
    }
]

result = {
    "source_sections": len(concepts),
    "templates_per_section": len(templates),
    "languages": [
        "English",
        "Hindi",
        "Kannada"
    ],
    "templates": templates
}

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(result, file, indent=2, ensure_ascii=False)

print("Scenario templates created successfully!")
print("Source sections:", len(concepts))
print("Templates per section:", len(templates))
print("Languages:", "English, Hindi, Kannada")
print("Saved to:", output_file)
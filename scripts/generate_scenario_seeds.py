import json

input_file = "data/scenarios/processed/legal_concepts.json"
output_file = "data/scenarios/processed/scenario_seeds.json"

with open(input_file, "r", encoding="utf-8") as file:
    sections = json.load(file)

# Seed situations for the most important citizen-facing concepts
# in the three current Acts. These are used only as high-quality
# starting points; they must remain mapped to the actual section.
seed_map = {
    ("Consumer Protection Act, 2019", "2"): [
        "I bought a product for my personal use and want to know whether I am legally a consumer.",
        "I paid for a service for personal use and want to know whether consumer protection law applies to me."
    ],
    ("Consumer Protection Act, 2019", "17"): [
        "I want to report a violation of consumer rights or an unfair trade practice. Where can I send the complaint?",
        "I saw an advertisement that appears to harm consumers. Which authority can I report it to?"
    ],
    ("Consumer Protection Act, 2019", "20"): [
        "I bought a product that appears dangerous or unsafe. What can the consumer authority do?",
        "Unsafe goods are being sold to consumers. What action can the Central Consumer Protection Authority take?"
    ],
    ("Consumer Protection Act, 2019", "21"): [
        "A company is using a false or misleading advertisement for its product. What action can be taken?",
        "An advertisement makes a claim that is not true. What can the consumer authority do?"
    ],
    ("Transfer of Property Act, 1882", "53"): [
        "Someone transferred property to avoid a claim from a creditor. Can that transfer be challenged?",
        "A property transfer appears to have been made to defeat the rights of a creditor. What does the law provide?"
    ],
    ("Transfer of Property Act, 1882", "54"): [
        "I am buying a property and want to know when a transaction legally amounts to a sale.",
        "I paid for property and want to understand what legally constitutes a sale of the property."
    ],
    ("Transfer of Property Act, 1882", "58"): [
        "I want to use my property as security for a loan. What does the law say about a mortgage?",
        "I have mortgaged my property for a loan and want to understand my legal position."
    ],
    ("Transfer of Property Act, 1882", "105"): [
        "I am renting out my property and want to understand the legal meaning of a lease.",
        "I am a tenant and want to understand my legal position under a lease."
    ],
    ("Transfer of Property Act, 1882", "106"): [
        "My landlord wants to end my tenancy. What notice is legally required?",
        "I want to terminate a lease and need to know what notice period the law provides."
    ],
    ("Transfer of Property Act, 1882", "111"): [
        "My landlord says my lease has ended. What are the legal ways a lease can terminate?",
        "I am a tenant and want to know when a lease can legally come to an end."
    ],
    ("Bharatiya Nyaya Sanhita, 2023", "40"): [
        "Someone is attacking me and I act to protect myself. When does the right of private defence apply?",
        "I used force to protect myself from an immediate attack. What does the law say?"
    ],
    ("Bharatiya Nyaya Sanhita, 2023", "43"): [
        "Someone is trying to interfere with my property and I act to protect it. When can private defence of property apply?",
        "I used force to protect my property from an immediate threat. What are my legal rights?"
    ],
}

seeds = []

for section in sections:
    key = (
        section["act_name"],
        str(section["section_number"])
    )

    if key not in seed_map:
        continue

    for query in seed_map[key]:
        seeds.append({
            "law_id": section["law_id"],
            "domain": section["domain"],
            "act_name": section["act_name"],
            "section_number": section["section_number"],
            "section_title": section["section_title"],
            "legal_text": section["legal_text"],
            "scenario": query,
            "user_query": query,
            "language": "English",
            "source_url": section["source_url"]
        })

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(seeds, file, indent=2, ensure_ascii=False)

print("Scenario seeds created successfully!")
print("Seed records:", len(seeds))
print("Acts covered:", len(set(x["act_name"] for x in seeds)))
print("Saved to:", output_file)
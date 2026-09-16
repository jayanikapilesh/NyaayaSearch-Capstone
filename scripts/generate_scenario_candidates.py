import json
import re

input_file = "data/scenarios/processed/scenario_sections_classified.json"
output_file = "data/scenarios/processed/scenario_candidates.json"

with open(input_file, "r", encoding="utf-8") as file:
    data = json.load(file)

sections = data["scenario_sections"]


def clean_text(text):
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([,.;:])", r"\1", text)
    return text.strip()


# Generate scenarios from distinctive phrases in each section.
# This keeps the situation tied to the actual provision instead
# of reusing the same generic scenario across unrelated sections.
def extract_topic(section):
    title = clean_text(section["section_title"])
    text = clean_text(section["legal_text"])

    # Prefer the section title because it is the clearest description
    # of what the provision deals with.
    topic = title.rstrip(".")

    # Remove common structural wording from titles.
    topic = re.sub(
        r"^(power of|procedure for|provisions relating to|special provisions relating to)\s+",
        "",
        topic,
        flags=re.IGNORECASE
    )

    return topic.strip()


templates = [
    "I have a legal issue involving {topic}. What does this provision say?",
    "I am affected by an issue involving {topic}. What are my legal rights?",
    "What should I do if I face a problem involving {topic}?",
    "What legal remedy may be available in a case involving {topic}?",
    "Which authority or court should I approach about {topic}?"
]


candidates = []
candidate_id = 1

for section in sections:
    topic = extract_topic(section)

    if len(topic) < 5:
        continue

    for template in templates:
        query = template.format(topic=topic)

        # Clean punctuation spacing.
        query = re.sub(r"([.!?])(?=[A-Za-z])", r"\1 ", query)

        candidates.append({
            "candidate_id": f"CAND-{candidate_id:05d}",
            "law_id": section["law_id"],
            "domain": section["domain"],
            "act_name": section["act_name"],
            "section_number": section["section_number"],
            "section_title": clean_text(section["section_title"]),
            "legal_concept": clean_text(section["legal_concept"]),
            "legal_text": clean_text(section["legal_text"]),
            "scenario": topic,
            "scenario_type": "section_specific_candidate",
            "user_query": query,
            "language": "English",
            "source_url": section["source_url"]
        })

        candidate_id += 1


with open(output_file, "w", encoding="utf-8") as file:
    json.dump(candidates, file, indent=2, ensure_ascii=False)

print("Section-specific scenario candidates generated!")
print("Source sections:", len(sections))
print("Candidates:", len(candidates))
print("Unique queries:", len(set(x["user_query"] for x in candidates)))
print("Languages: English")
print("Saved to:", output_file)
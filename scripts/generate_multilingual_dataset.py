import csv
import requests
import time

input_file = "data/scenarios/processed/dataset3_english_expanded.csv"
output_file = "data/scenarios/processed/dataset3_multilingual_legal_scenarios_v2.csv"

with open(input_file, "r", encoding="utf-8-sig") as file:
    rows = list(csv.DictReader(file))


def translate(text, target_language):
    url = "https://api.mymemory.translated.net/get"

    params = {
        "q": text,
        "langpair": f"en|{target_language}"
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()

    if data["responseStatus"] != 200:
        raise Exception(data["responseDetails"])

    return data["responseData"]["translatedText"]


new_rows = []
scenario_id = 1

for index, row in enumerate(rows, start=1):
    print(f"Processing {index}/{len(rows)}")

    english_row = row.copy()
    english_row["scenario_id"] = f"SCN-{scenario_id:05d}"
    english_row["language"] = "English"
    new_rows.append(english_row)
    scenario_id += 1

    time.sleep(1)

    hindi_row = row.copy()
    hindi_row["scenario_id"] = f"SCN-{scenario_id:05d}"
    hindi_row["user_query"] = translate(row["user_query"], "hi")
    hindi_row["language"] = "Hindi"
    new_rows.append(hindi_row)
    scenario_id += 1

    time.sleep(1)

    kannada_row = row.copy()
    kannada_row["scenario_id"] = f"SCN-{scenario_id:05d}"
    kannada_row["user_query"] = translate(row["user_query"], "kn")
    kannada_row["language"] = "Kannada"
    new_rows.append(kannada_row)
    scenario_id += 1

    time.sleep(1)


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
    writer.writerows(new_rows)

print("Multilingual Dataset 3 created successfully!")
print("Total rows:", len(new_rows))
print("English:", sum(r["language"] == "English" for r in new_rows))
print("Hindi:", sum(r["language"] == "Hindi" for r in new_rows))
print("Kannada:", sum(r["language"] == "Kannada" for r in new_rows))
print("Saved to:", output_file)
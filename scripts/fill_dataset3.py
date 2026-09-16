import csv
from openpyxl import load_workbook

dataset1 = "Legal_Knowledge_Base_combined.xlsx"
dataset3 = "data/scenarios/processed/dataset3_multilingual_legal_scenarios_v2.csv"

wb = load_workbook(dataset1, read_only=True)
ws = wb.active

legal = {}

for r in ws.iter_rows(min_row=2, values_only=True):
    key = (str(r[2]).strip(), str(r[4]).strip())
    legal[key] = {
        "title": str(r[5] or "").strip(),
        "text": str(r[6] or "").strip()
    }

wb.close()

with open(dataset3, encoding="utf-8-sig") as f:
    rows = list(csv.DictReader(f))

for row in rows:
    key = (row["act_name"].strip(), row["section_number"].strip())
    law = legal.get(key)

    if law:
        row["plain_explanation"] = (
            f"This section of the {row['act_name']} covers {law['title']}."
        )
        row["what_to_do_next"] = (
            "Read the relevant section and keep documents or evidence related "
            "to the situation. For specific legal action, consult a qualified lawyer."
        )

with open(dataset3, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("Updated rows:", len(rows))
print("Saved:", dataset3)

import re
from openpyxl import Workbook

input_path = "data/processed/specific_relief_act_1963.txt"
output_path = "Legal_Knowledge_Base_specific_relief_fixed.xlsx"

act_name = "Specific Relief Act, 1963"
act_number = "47 of 1963"
domain = "Civil Remedies"
law_prefix = "SRA"

with open(input_path, "r", encoding="utf-8") as file:
    text = file.read()

marker = "10. Specific performance in respect of contracts"
positions = [m.start() for m in re.finditer(re.escape(marker), text)]
if len(positions) < 1:
    raise ValueError("Could not find real Act body")

marker1 = "1. Short title, extent and commencement.\u2014(1) This Act"
positions1 = [m.start() for m in re.finditer(re.escape(marker1), text)]
if len(positions1) < 1:
    raise ValueError("Could not find real Section 1 body")

start = positions1[-1]
text = text[start:]

end_markers = ["SCHEDULE", "THE SCHEDULE"]
end = len(text)
for marker in end_markers:
    pos = text.find(marker)
    if pos != -1:
        end = min(end, pos)
text = text[:end]

# Strip footnote reference lines (e.g. "1. The words ... omitted by Act 34 of 2019, s. 95")
# These repeat small numbers (1, 2, 3...) mid-document and confuse section splitting.
footnote_pattern = re.compile(
    r"\n\d{1,2}\.\s+(?:The words|Subs\.|Ins\.|ins\.|Omitted|omitted|Inserted|Substituted|subs\.|Cl\.|Section \d+ substituted|vide notification|w\.e\.f).*?(?=\n\d|\n\n|\Z)",
    re.DOTALL
)
text = footnote_pattern.sub("\n", text)

pattern = r"(?<!\d)(\d{1,3}[A-Z]?)\.\s*(?:\u2014|\-)?\s*(?=[A-Z\u201c\[])|(?<!\d)\d\[(\d{1,3}[A-Z]?)\.\s+"

matches = list(re.finditer(pattern, text))
sections = {}

for i, match in enumerate(matches):
    label = match.group(1) or match.group(2)
    section_start = match.start()
    section_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
    section_text = text[section_start:section_end].strip()
    section_text = re.sub(r"\n\s*\d+\s*\n", "\n", section_text)
    section_text = section_text.replace("IndiaCode", " ")
    section_text = re.sub(r"\s+", " ", section_text).strip()
    if label not in sections:
        sections[label] = section_text

print("Sections found:", len(sections))

workbook = Workbook()
sheet = workbook.active
sheet.title = "Legal Knowledge Base"
headers = [
    "law_id", "domain", "act_name", "act_number", "section_number",
    "section_title", "legal_text", "jurisdiction", "enforcement_status",
    "effective_date", "source_url", "source_date_checked", "verification_status"
]
sheet.append(headers)

def sort_key(label):
    m = re.match(r"(\d+)([A-Z]?)", label)
    return (int(m.group(1)), m.group(2))

for label in sorted(sections.keys(), key=sort_key):
    full_text = sections[label]
    content = re.sub(rf"^\d?\[?{re.escape(label)}\.\s*(?:\u2014|\-)?\s*", "", full_text, count=1).strip()
    title_match = re.match(r"^(.+?)(?:\u2014|—)\s*", content)
    if title_match:
        title = title_match.group(1).strip()
    else:
        title_match = re.match(r"^(.+?\.)\s", content)
        title = title_match.group(1).strip() if title_match else content[:150]
    sheet.append([
        f"{law_prefix}-{label}", domain, act_name, act_number, label,
        title, content, "India", "To be verified", "",
        "https://www.indiacode.nic.in/", "2026-09-17", "Candidate\u2014verify"
    ])

workbook.save(output_path)
print("Saved to:", output_path)

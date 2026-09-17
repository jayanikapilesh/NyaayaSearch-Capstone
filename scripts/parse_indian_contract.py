import re
from openpyxl import Workbook

input_path = "data/processed/indian_contract_act_1872.txt"
output_path = "Legal_Knowledge_Base_contract_fixed.xlsx"

act_name = "Indian Contract Act, 1872"
act_number = "9 of 1872"
domain = "Contract"
law_prefix = "ICA"

with open(input_path, "r", encoding="utf-8") as file:
    text = file.read()

# Skip the Table of Contents — jump to the second occurrence of Section 15's
# full text, which only exists in the real Act body, not the TOC.
marker = "15. \u201cCoercion\u201d defined.\u2014"
positions = [m.start() for m in re.finditer(re.escape(marker), text)]

if len(positions) < 1:
    raise ValueError("Could not find real Act body")

# Back up from that marker to the start of Section 1 in the same block.
body_start_region = text[:positions[-1]]
start = body_start_region.rfind("\n1. ")

if start == -1:
    raise ValueError("Section 1 not found before Section 15's real body")

text = text[start:]

# Stop at a reasonable end marker (adjust if needed based on inspection).
end_markers = ["SCHEDULE", "THE SCHEDULE"]
end = len(text)
for marker in end_markers:
    pos = text.find(marker)
    if pos != -1:
        end = min(end, pos)

text = text[:end]

# Match sections 1-266 (including lettered sub-sections like 19A).
pattern = r"(?<!\d)(\d{1,3}[A-Z]?)\.\s+(?=[A-Z\u201c\[])"

matches = list(re.finditer(pattern, text))

sections = {}

for i, match in enumerate(matches):
    label = match.group(1)

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

    content = re.sub(rf"^{re.escape(label)}\.\s+", "", full_text, count=1).strip()

    title_match = re.match(r"^(.+?\.)\s*\u2014\s*", content)
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
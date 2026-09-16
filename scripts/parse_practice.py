import re
from openpyxl import Workbook

input_path = "data/processed/right_to_information_act_2005.txt"
output_path = "Legal_Knowledge_Base_rti.xlsx"

act_name = "Right to Information Act, 2005"
act_number = "22 of 2005"
domain = "Right to Information"
law_prefix = "RTI"

with open(input_path, "r", encoding="utf-8") as file:
    text = file.read()

# Find the actual Act text, not the Arrangement of Sections.
heading = "THE RIGHT TO INFORMATION ACT, 2005"
positions = [m.start() for m in re.finditer(re.escape(heading), text)]

if len(positions) < 2:
    raise ValueError("Actual Act text not found")

text = text[positions[1]:]

# Start from actual Section 1.
start = text.find("1. Short title, extent and commencement")

if start == -1:
    raise ValueError("Section 1 not found")

text = text[start:]

# Match sections 1–31.
pattern = r"(?<!\d)(\d{1,2})\.\s+(?:\d+\s*)?(?=[A-Z\[])"

matches = list(re.finditer(pattern, text))

sections = {}

for i, match in enumerate(matches):
    label = match.group(1)
    number = int(label)

    if number < 1 or number > 31:
        continue

    section_start = match.start()
    section_end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

    section_text = text[section_start:section_end].strip()

    # Remove page numbers and IndiaCode markers.
    section_text = re.sub(r"\n\s*\d+\s*\n", "\n", section_text)
    section_text = section_text.replace("IndiaCode", " ")

    # Clean excessive whitespace.
    section_text = re.sub(r"\s+", " ", section_text).strip()

    if label not in sections:
        sections[label] = section_text

# Verify all 31 sections are present.
missing = [
    str(number)
    for number in range(1, 32)
    if str(number) not in sections
]

if missing:
    raise ValueError(f"Missing sections: {missing}")

# Create Excel file.
workbook = Workbook()
sheet = workbook.active
sheet.title = "Legal Knowledge Base"

headers = [
    "law_id",
    "domain",
    "act_name",
    "act_number",
    "section_number",
    "section_title",
    "legal_text",
    "jurisdiction",
    "enforcement_status",
    "effective_date",
    "source_url",
    "source_date_checked",
    "verification_status"
]

sheet.append(headers)

for label in sorted(sections.keys(), key=int):

    full_text = sections[label]

    content = re.sub(
        rf"^{re.escape(label)}\.\s+",
        "",
        full_text,
        count=1
    ).strip()

    # Extract section title.
    title_match = re.match(r"^(.+?)(?:—|-)\s*", content)

    if title_match:
        title = title_match.group(1).strip()
    else:
        title_match = re.match(r"^(.+?\.)\s", content)
        title = title_match.group(1).strip() if title_match else content[:150]

    sheet.append([
        f"{law_prefix}-{label}",
        domain,
        act_name,
        act_number,
        label,
        title,
        content,
        "India",
        "To be verified",
        "",
        "https://www.indiacode.nic.in/",
        "2026-09-15",
        "Candidate—verify"
    ])

workbook.save(output_path)

print("Right to Information Act Dataset created successfully!")
print("Actual section records found:", len(sections))
print("Missing sections:", len(missing))
print("Saved to:", output_path)
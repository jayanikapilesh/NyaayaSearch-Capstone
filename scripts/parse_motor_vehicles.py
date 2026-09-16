import re
from openpyxl import Workbook

text = open("data/processed/motor_vehicles_act_1988.txt", encoding="utf-8").read()

start = text.find("1. Short title, extent and commencement.")
if start == -1:
    raise ValueError("Section 1 not found")

text = text[start:]

pattern = r"(?m)^\s*(\d{1,3}[A-Z]?)\.\s+"
matches = list(re.finditer(pattern, text))

sections = {}

for i, m in enumerate(matches):
    number = m.group(1)
    if int(re.match(r"\d+", number).group()) > 217:
        continue

    end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
    sections.setdefault(number, text[m.start():end].strip())

print("Sections found:", len(sections))

wb = Workbook()
ws = wb.active
ws.title = "Legal Knowledge Base"

ws.append([
    "law_id","domain","act_name","act_number","section_number",
    "section_title","legal_text","jurisdiction","enforcement_status",
    "effective_date","source_url","source_date_checked","verification_status"
])

for number, value in sections.items():
    content = re.sub(r"^\s*" + re.escape(number) + r"\.\s*", "", value)
    title = content.split("—")[0].split("-")[0].strip()

    ws.append([
        "MVA-" + number,
        "Motor Vehicles Law",
        "Motor Vehicles Act, 1988",
        "59 of 1988",
        number,
        title[:150],
        content,
        "India",
        "To be verified",
        "",
        "https://www.indiacode.nic.in/",
        "2026-09-15",
        "Candidate—verify"
    ])

wb.save("Legal_Knowledge_Base_motor_vehicles.xlsx")
print("Saved: Legal_Knowledge_Base_motor_vehicles.xlsx")

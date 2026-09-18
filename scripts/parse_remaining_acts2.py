import re
from openpyxl import Workbook

configs = [
    {
        "input": "data/processed/transfer_of_property_act_1882.txt",
        "output": "Legal_Knowledge_Base_property_fixed.xlsx",
        "act_name": "Transfer of Property Act, 1882",
        "act_number": "4 of 1882",
        "domain": "Property",
        "prefix": "TPA",
    },
    {
        "input": "data/processed/bharatiya_nyaya_sanhita_2023.txt",
        "output": "Legal_Knowledge_Base_bns_fixed.xlsx",
        "act_name": "Bharatiya Nyaya Sanhita, 2023",
        "act_number": "45 of 2023",
        "domain": "Criminal Law",
        "prefix": "BNS",
    },
]

body_anchor = re.compile(r"\.\s*[\u2014\u2013\-]+\s*(?:\(1\)\s*)?This\s+Act\s+may\s+be\s+call\w*\s*d", re.DOTALL)
section_start_pattern = re.compile(r"\n(\d{1,3}[A-Z]?)\.\s")

footnote_pattern = re.compile(
    r"\n\d{1,2}\.\s+(?:The words|Subs\.|Ins\.|ins\.|Omitted|omitted|Inserted|Substituted|subs\.|Cl\.|Section \d+ substituted|vide notification|w\.e\.f|Rep\.|rep\.|Added|added).*?(?=\n\d|\n\n|\Z)",
    re.DOTALL
)

section_pattern = re.compile(
    r"(?<!\d)(\d{1,3}[A-Z]?)\.\s*(?:\u2014|\u2013|\-)?\s*(?=[A-Z\u201c\[])|(?<!\d)\d\[(\d{1,3}[A-Z]?)\.\s+"
)


def sort_key(label):
    m = re.match(r"(\d+)([A-Z]?)", label)
    return (int(m.group(1)), m.group(2))


headers = [
    "law_id", "domain", "act_name", "act_number", "section_number",
    "section_title", "legal_text", "jurisdiction", "enforcement_status",
    "effective_date", "source_url", "source_date_checked", "verification_status"
]

for cfg in configs:
    print("=====", cfg["act_name"], "=====")
    with open(cfg["input"], "r", encoding="utf-8") as f:
        text = f.read()

    anchor_match = body_anchor.search(text)
    if not anchor_match:
        print("  ANCHOR STILL NOT FOUND - SKIPPED")
        continue

    preceding = text[:anchor_match.start()]
    starts = list(section_start_pattern.finditer(preceding))
    if not starts:
        print("  SECTION 1 START NOT FOUND - SKIPPED")
        continue

    start = starts[-1].start() + 1
    text2 = text[start:]

    end = len(text2)
    for marker in ["SCHEDULE", "THE SCHEDULE", "THE FIRST SCHEDULE"]:
        pos = text2.find(marker)
        if pos != -1:
            end = min(end, pos)
    text2 = text2[:end]

    text2 = footnote_pattern.sub("\n", text2)

    matches = list(section_pattern.finditer(text2))
    sections = {}

    for i, match in enumerate(matches):
        label = match.group(1) or match.group(2)
        s_start = match.start()
        s_end = matches[i + 1].start() if i + 1 < len(matches) else len(text2)
        section_text = text2[s_start:s_end].strip()
        section_text = re.sub(r"\n\s*\d+\s*\n", "\n", section_text)
        section_text = section_text.replace("IndiaCode", " ")
        section_text = re.sub(r"\s+", " ", section_text).strip()
        if label not in sections:
            sections[label] = section_text

    broken = 0
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Legal Knowledge Base"
    sheet.append(headers)

    for label in sorted(sections.keys(), key=sort_key):
        full_text = sections[label]
        content = re.sub(rf"^\d?\[?{re.escape(label)}\.\s*(?:\u2014|\u2013|\-)?\s*", "", full_text, count=1).strip()
        title_match = re.match(r"^(.+?)(?:\u2014|\u2013)\s*", content)
        if title_match:
            title = title_match.group(1).strip()
        else:
            title_match = re.match(r"^(.+?\.)\s", content)
            title = title_match.group(1).strip() if title_match else content[:150]

        if content.strip() == title.strip():
            broken += 1

        sheet.append([
            f"{cfg['prefix']}-{label}", cfg["domain"], cfg["act_name"], cfg["act_number"], label,
            title, content, "India", "To be verified", "",
            "https://www.indiacode.nic.in/", "2026-09-17", "Candidate\u2014verify"
        ])

    workbook.save(cfg["output"])
    print("  Sections found:", len(sections), "| Still broken:", broken, "| Saved to:", cfg["output"])
    print()

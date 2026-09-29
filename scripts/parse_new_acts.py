import re
from openpyxl import Workbook

# One "settings card" per new Act.
# Optional card settings:
#   normalize_spacing: tidy "1 ." -> "1." and "( 1 )" -> "(1)" for PDFs with odd spacing
#   text_fixes: exact text replacements applied before parsing (for one-off PDF quirks)
#   drop_labels: section labels to leave out (e.g. state amendments printed as notes)
configs = [
    {"input": "data/processed/hindu_marriage_act_1955.txt", "output": "Legal_Knowledge_Base_hma.xlsx",
     "act_name": "Hindu Marriage Act, 1955", "act_number": "25 of 1955", "domain": "Family", "prefix": "HMA"},
    {"input": "data/processed/hindu_succession_act_1956.txt", "output": "Legal_Knowledge_Base_hsa.xlsx",
     "act_name": "Hindu Succession Act, 1956", "act_number": "30 of 1956", "domain": "Family", "prefix": "HSA",
     "drop_labels": ["6A", "6B", "6C"]},
    {"input": "data/processed/special_marriage_act_1954.txt", "output": "Legal_Knowledge_Base_sma.xlsx",
     "act_name": "Special Marriage Act, 1954", "act_number": "43 of 1954", "domain": "Family", "prefix": "SMA",
     "normalize_spacing": True},
    {"input": "data/processed/dowry_prohibition_act_1961.txt", "output": "Legal_Knowledge_Base_dpa.xlsx",
     "act_name": "Dowry Prohibition Act, 1961", "act_number": "28 of 1961", "domain": "Family", "prefix": "DPA"},
    {"input": "data/processed/hindu_adoptions_maintenance_act_1956.txt", "output": "Legal_Knowledge_Base_hama.xlsx",
     "act_name": "Hindu Adoptions and Maintenance Act, 1956", "act_number": "78 of 1956", "domain": "Family", "prefix": "HAMA"},
    {"input": "data/processed/negotiable_instruments_act_1881.txt", "output": "Legal_Knowledge_Base_nia.xlsx",
     "act_name": "Negotiable Instruments Act, 1881", "act_number": "26 of 1881", "domain": "Banking and Finance", "prefix": "NIA"},
    {"input": "data/processed/code_on_wages_2019.txt", "output": "Legal_Knowledge_Base_cow.xlsx",
     "act_name": "Code on Wages, 2019", "act_number": "29 of 2019", "domain": "Labour", "prefix": "COW",
     "normalize_spacing": True},
    {"input": "data/processed/code_on_social_security_2020.txt", "output": "Legal_Knowledge_Base_css.xlsx",
     "act_name": "Code on Social Security, 2020", "act_number": "36 of 2020", "domain": "Labour", "prefix": "CSS",
     "text_fixes": [("131. other modes of recovery.", "131. Other modes of recovery.")]},
    {"input": "data/processed/posh_act_2013.txt", "output": "Legal_Knowledge_Base_posh.xlsx",
     "act_name": "Sexual Harassment of Women at Workplace (Prevention, Prohibition and Redressal) Act, 2013",
     "act_number": "14 of 2013", "domain": "Labour", "prefix": "POSH"},
    {"input": "data/processed/senior_citizens_act_2007.txt", "output": "Legal_Knowledge_Base_mwpsc.xlsx",
     "act_name": "Maintenance and Welfare of Parents and Senior Citizens Act, 2007", "act_number": "56 of 2007",
     "domain": "Family", "prefix": "MWPSC"},
    {"input": "data/processed/pocso_act_2012.txt", "output": "Legal_Knowledge_Base_pocso.xlsx",
     "act_name": "Protection of Children from Sexual Offences Act, 2012", "act_number": "32 of 2012",
     "domain": "Criminal Law", "prefix": "POCSO"},
    {"input": "data/processed/bharatiya_sakshya_adhiniyam_2023.txt", "output": "Legal_Knowledge_Base_bsa.xlsx",
     "act_name": "Bharatiya Sakshya Adhiniyam, 2023", "act_number": "47 of 2023", "domain": "Evidence", "prefix": "BSA"},
]

SOURCE_DATE_CHECKED = "2026-09-29"

# If a section number appears twice, the first one is kept (real sections come before
# their page footnotes). It is replaced only when the first text is tiny or looks like a footnote.
TINY_TEXT_CHARS = 60

# Footnote openings, with flexible spacing between words (for PDFs with odd spacing).
FOOTNOTE_OPENINGS = (
    r"The\s+words?|The\s+Act\s+has\s+been\s+extended|Certain\s+words|Subs\s*\.|Ins\s*\.|ins\s*\.|"
    r"Omitted|omitted|Inserted|Substituted|subs\s*\.|Cl\s*\.|Section\s+\d+\s+substituted|"
    r"Section\s+\d+\s+numbered|vide\s+notification|w\s*\.\s*e\s*\.\s*f|Rep\s*\.|rep\s*\.|Added|added"
)

# Dashes accepted everywhere: em dash, en dash, horizontal bar (used in older PDFs), hyphen.
# Accepts "This Act/Code may be called", and "(1)" with or without inner spaces.
body_anchor = re.compile(
    r"\.\s*[\u2014\u2013\u2015\-]+\s*(?:\(\s*1\s*\)\s*)?This\s+(?:Act|Code)\s+may\s+be\s+call\w*\s*d",
    re.DOTALL
)
section_start_pattern = re.compile(r"\n(\d{1,3}[A-Z]?)\.\s")

# Footnotes at the bottom of pages (removed before splitting into sections).
footnote_pattern = re.compile(
    r"\n\s*\d{1,2}\.\s+(?:" + FOOTNOTE_OPENINGS + r").*?(?=\n\d|\n\n|\Z)",
    re.DOTALL
)

# Used to recognise a section text that is really a leftover footnote.
footnote_like = re.compile(r"^\d?\[?\d{1,3}[A-Z]?\.\s*(?:" + FOOTNOTE_OPENINGS + r")")

section_pattern = re.compile(
    r"(?<!\d)(\d{1,3}[A-Z]?)\.\s*(?:\u2014|\u2013|\u2015|\-)?\s*(?=[A-Z\u201c\[])|(?<!\d)\d\[(\d{1,3}[A-Z]?)\.\s+"
)

# A number right after these words is a cross-reference ("under section 138."), not a new section.
xref_before = re.compile(r"(?:sections?|sub-sections?|clauses?|articles?|rules?|\band|\bor|,)\s*$", re.IGNORECASE)


def is_cross_reference(match, text):
    before = text[max(0, match.start() - 30):match.start()]
    return xref_before.search(before) is not None


def is_junk(section_text):
    return len(section_text) < TINY_TEXT_CHARS or footnote_like.match(section_text) is not None


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

    for old, new in cfg.get("text_fixes", []):
        text = text.replace(old, new)

    # Only for PDFs with odd spacing: "1 ." -> "1." and "( 1 )" -> "(1)"
    if cfg.get("normalize_spacing"):
        text = re.sub(r"(?<=\d) +\.", ".", text)
        text = re.sub(r"\(\s*(\d+)\s*\)", r"(\1)", text)

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

    matches = [m for m in section_pattern.finditer(text2) if not is_cross_reference(m, text2)]
    drop = set(cfg.get("drop_labels", []))
    sections = {}

    for i, match in enumerate(matches):
        label = match.group(1) or match.group(2)
        if label in drop:
            continue
        s_start = match.start()
        s_end = matches[i + 1].start() if i + 1 < len(matches) else len(text2)
        section_text = text2[s_start:s_end].strip()
        section_text = re.sub(r"\n\s*\d+\s*\n", "\n", section_text)
        section_text = section_text.replace("IndiaCode", " ")
        section_text = re.sub(r"\s+", " ", section_text).strip()
        # Duplicate rule: first one wins, unless the first is junk (tiny or footnote-like)
        # and the new one is not.
        if label not in sections:
            sections[label] = section_text
        elif is_junk(sections[label]) and not is_junk(section_text):
            sections[label] = section_text

    broken = 0
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Legal Knowledge Base"
    sheet.append(headers)

    for label in sorted(sections.keys(), key=sort_key):
        full_text = sections[label]
        content = re.sub(rf"^\d?\[?{re.escape(label)}\.\s*(?:\u2014|\u2013|\u2015|\-)?\s*", "", full_text, count=1).strip()
        title_match = re.match(r"^(.+?)(?:\u2014|\u2013|\u2015)\s*", content)
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
            "https://www.indiacode.nic.in/", SOURCE_DATE_CHECKED, "Candidate\u2014verify"
        ])

    workbook.save(cfg["output"])
    print("  Sections found:", len(sections), "| Still broken:", broken, "| Saved to:", cfg["output"])
    print()
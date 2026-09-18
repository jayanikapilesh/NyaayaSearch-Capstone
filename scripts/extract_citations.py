import re
import pandas as pd
from bs4 import BeautifulSoup

INPUT_FILE = "../data/case_law/processed/Dataset2_Case_Law_Corpus_2015_2025.csv"
OUTPUT_FILE = "../data/case_law/processed/case_citations.csv"

WORD = r"(?:[A-Z][a-z]+|of|the|and)"

PATTERN_ACT_SECTION = re.compile(
    rf"((?:{WORD}\s+){{1,6}}Act,?\s*\d{{4}})\s*-?\s*[:\-]?\s*s\.?\s*(\d+[A-Za-z]?(?:\(\w+\))?)",
)

PATTERN_US_OF = re.compile(
    rf"u[/l1]s\.?\s*(\d+[A-Za-z]?(?:\(\w+\))?)\s*of\s*(?:the\s*)?((?:{WORD}\s+){{1,6}}Act)",
)

# Note: Code pattern excludes the word "Code" itself from the WORD list match
# so "Code of Criminal Procedure" doesn't double up with the literal "Code" suffix
CODE_WORD = r"(?:[A-Z][a-z]+|of|the|and)(?<!Code)"
PATTERN_CODE_SECTION = re.compile(
    rf"((?:{WORD}\s+){{0,5}}(?:Penal Code|Code of Criminal Procedure|Insolvency and Bankruptcy Code)),?\s*\d{{4}}\s*[:\-]?\s*ss?\.?\s*(\d+[A-Za-z]?(?:/\d+[A-Za-z]?)*(?:\(\w+\))?)",
)

BLOCKLIST = {"the act", "act", "this act", "said act", "the code", "code"}


def clean_act_name(name):
    name = re.sub(r"\s+", " ", name).strip().rstrip(",")
    name = re.sub(r"^(the|of|and)\s+", "", name, flags=re.IGNORECASE)
    return name.strip()


def is_low_confidence_section(section):
    # A section number with 5+ digits and no separator is likely an OCR-garbled
    # concatenation of two numbers (e.g. "302134" probably meant "302/34")
    digits_only = re.sub(r"[^\d]", "", section)
    return len(digits_only) >= 5


def extract_citations(text):
    citations = []

    for act_name, section in PATTERN_ACT_SECTION.findall(text):
        cleaned = clean_act_name(act_name)
        if cleaned.lower() not in BLOCKLIST:
            citations.append({
                "act_name": cleaned,
                "section_number": section,
                "low_confidence": is_low_confidence_section(section),
            })

    for section, act_name in PATTERN_US_OF.findall(text):
        cleaned = clean_act_name(act_name)
        if cleaned.lower() not in BLOCKLIST:
            citations.append({
                "act_name": cleaned,
                "section_number": section,
                "low_confidence": is_low_confidence_section(section),
            })

    for code_name, section in PATTERN_CODE_SECTION.findall(text):
        cleaned = clean_act_name(code_name)
        if cleaned.lower() not in BLOCKLIST:
            for sec in section.split("/"):
                citations.append({
                    "act_name": cleaned,
                    "section_number": sec,
                    "low_confidence": is_low_confidence_section(sec),
                })

    return citations


def normalize_act_name(name):
    return re.sub(r",?\s*\d{4}$", "", name).strip()


def main():
    print("Loading case law dataset...")
    df = pd.read_csv(INPUT_FILE)
    print(f"Loaded {len(df)} cases")

    rows = []
    matched_cases = 0

    for i, row in df.iterrows():
        html = row["raw_html"]
        if not isinstance(html, str):
            continue

        soup = BeautifulSoup(html, "html.parser")
        text = soup.get_text(separator=" ", strip=True)

        citations = extract_citations(text)

        if citations:
            matched_cases += 1
            for c in citations:
                rows.append({
                    "case_id": row["case_id"],
                    "title": row["title"],
                    "decision_date": row["decision_date"],
                    "court": row["court"],
                    "act_name": c["act_name"],
                    "act_name_normalized": normalize_act_name(c["act_name"]),
                    "section_number": c["section_number"],
                    "low_confidence": c["low_confidence"],
                })

        if (i + 1) % 5000 == 0:
            print(f"Processed {i + 1}/{len(df)} cases, {matched_cases} matched so far...")

    print(f"\nDone. Matched {matched_cases} out of {len(df)} cases ({matched_cases/len(df)*100:.1f}%)")
    print(f"Total citation links extracted: {len(rows)}")

    result_df = pd.DataFrame(rows)
    low_conf_count = result_df["low_confidence"].sum()
    print(f"Low-confidence (likely OCR-garbled) citations flagged: {low_conf_count}")

    result_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

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

BLOCKLIST = {"the act", "act", "this act", "said act"}


def clean_act_name(name):
    name = re.sub(r"\s+", " ", name).strip().rstrip(",")
    name = re.sub(r"^(the|of|and)\s+", "", name, flags=re.IGNORECASE)
    return name.strip()


def extract_citations(text):
    citations = []

    for act_name, section in PATTERN_ACT_SECTION.findall(text):
        cleaned = clean_act_name(act_name)
        if cleaned.lower() in BLOCKLIST:
            continue
        citations.append({"act_name": cleaned, "section_number": section})

    for section, act_name in PATTERN_US_OF.findall(text):
        cleaned = clean_act_name(act_name)
        if cleaned.lower() in BLOCKLIST:
            continue
        citations.append({"act_name": cleaned, "section_number": section})

    return citations


def normalize_act_name(name):
    # Strip trailing year so "Arbitration and Conciliation Act, 1996" and
    # "Arbitration and Conciliation Act" merge into one canonical form.
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
                })

        if (i + 1) % 10000 == 0:
            print(f"Processed {i + 1}/{len(df)} cases, {matched_cases} matched so far...")

    print(f"\nDone. Matched {matched_cases} out of {len(df)} cases ({matched_cases/len(df)*100:.1f}%)")
    print(f"Total citation links extracted: {len(rows)}")

    result_df = pd.DataFrame(rows)
    result_df.to_csv(OUTPUT_FILE, index=False)
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

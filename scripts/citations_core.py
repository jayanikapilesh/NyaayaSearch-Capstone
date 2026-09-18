import pandas as pd
import os

CITATIONS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "case_law", "processed", "case_citations.csv")

_citations_df = None


def load_citations():
    global _citations_df
    if _citations_df is None:
        _citations_df = pd.read_csv(CITATIONS_FILE)
    return _citations_df


def find_related_cases(act_name, section_number, max_results=3):
    df = load_citations()

    # Match on normalized act name (case-insensitive, ignoring year) and section number
    act_name_lower = act_name.lower()
    section_str = str(section_number).strip()

    matches = df[
        df["act_name_normalized"].str.lower().apply(lambda x: x in act_name_lower or act_name_lower in x if isinstance(x, str) else False)
        & (df["section_number"].astype(str).str.strip() == section_str)
        & (df["low_confidence"] == False)
    ]

    results = []
    for _, row in matches.head(max_results).iterrows():
        results.append({
            "title": row["title"],
            "court": row["court"],
            "decision_date": row["decision_date"],
            "case_id": row["case_id"],
        })

    return results

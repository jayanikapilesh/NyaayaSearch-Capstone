import os
import glob
import json
import pandas as pd

kb_path = "Legal_Knowledge_Base_combined.xlsx"
clean_csv_path = "data/eval/classifier_training_data_clean.csv"
prod826_csv_path = "data/eval/classifier_training_data_production826.csv"
output_uncovered = "data/uncovered_sections.csv"

def normalize_section(sec):
    if pd.isna(sec):
        return ""
    s = str(sec).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s

def get_covered_sections_strict():
    df_kb = pd.read_excel(kb_path)
    df_kb["clean_act"] = df_kb["act_name"].astype(str).str.strip()
    df_kb["norm_sec"] = df_kb["section_number"].apply(normalize_section)
    kb_sections = set(zip(df_kb["clean_act"], df_kb["norm_sec"]))

    covered_sections = set()

    # 1. Load from classifier_training_data_clean.csv filtering ONLY is_relevant == 1
    if os.path.exists(clean_csv_path):
        df_csv = pd.read_csv(clean_csv_path)
        df_csv_relevant = df_csv[df_csv["is_relevant"] == 1]
        for _, row in df_csv_relevant.iterrows():
            act = str(row.get("act_name", "")).strip()
            sec = normalize_section(row.get("section_number"))
            if (act, sec) in kb_sections:
                covered_sections.add((act, sec))

    # 2. Load from training_pairs*.jsonl files (section target field is section_number)
    jsonl_files = glob.glob("data/training_pairs*.jsonl")
    for jf in jsonl_files:
        with open(jf, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                    act = str(item.get("act_name", "")).strip()
                    sec = normalize_section(item.get("section_number"))
                    if (act, sec) in kb_sections:
                        covered_sections.add((act, sec))
                except Exception:
                    continue

    return df_kb, covered_sections

def get_prod826_covered_sections(df_kb):
    kb_sections = set(zip(df_kb["clean_act"], df_kb["norm_sec"]))
    prod_sections = set()

    if os.path.exists(prod826_csv_path):
        df_p826 = pd.read_csv(prod826_csv_path)
        df_p826_relevant = df_p826[df_p826["is_relevant"] == 1]
        for _, row in df_p826_relevant.iterrows():
            act = str(row.get("act_name", "")).strip()
            sec = normalize_section(row.get("section_number"))
            if (act, sec) in kb_sections:
                prod_sections.add((act, sec))

    return prod_sections

def main():
    print("Loading Legal Knowledge Base & training datasets...")
    df_kb, covered_sections = get_covered_sections_strict()
    prod_sections = get_prod826_covered_sections(df_kb)

    print("\n--- Strict Coverage Report per Act (Relevant CSV Rows [is_relevant==1] + JSONL Target Sections) ---")
    print(f"{'Act Name':<55} | {'Total':<6} | {'Covered':<7} | {'Coverage %':<10}")
    print("-" * 88)

    uncovered_list = []

    for act_name, group in df_kb.groupby("clean_act"):
        total_count = len(group)
        covered_count = 0
        for _, row in group.iterrows():
            key = (row["clean_act"], row["norm_sec"])
            if key in covered_sections:
                covered_count += 1
            else:
                uncovered_list.append({
                    "act_name": row["clean_act"],
                    "section_number": row["section_number"],
                    "section_title": row.get("section_title", "")
                })
        
        pct = (covered_count / total_count * 100) if total_count > 0 else 0.0
        print(f"{act_name:<55} | {total_count:<6} | {covered_count:<7} | {pct:<10.1f}%")

    total_kb = len(df_kb)
    total_cov = len(covered_sections)
    overall_pct = (total_cov / total_kb * 100) if total_kb > 0 else 0.0
    print("-" * 88)
    print(f"{'TOTAL / OVERALL':<55} | {total_kb:<6} | {total_cov:<7} | {overall_pct:<10.1f}%")

    df_uncovered = pd.DataFrame(uncovered_list)
    df_uncovered.to_csv(output_uncovered, index=False, encoding="utf-8")
    print(f"\nSaved {len(uncovered_list)} uncovered sections to {output_uncovered}")

    print("\n--- Coverage Comparison using ONLY classifier_training_data_production826.csv (is_relevant==1) ---")
    print(f"{'Act Name':<55} | {'Total':<6} | {'Covered':<7} | {'Coverage %':<10}")
    print("-" * 88)

    for act_name, group in df_kb.groupby("clean_act"):
        total_count = len(group)
        prod_count = sum(1 for _, row in group.iterrows() if (row["clean_act"], row["norm_sec"]) in prod_sections)
        pct = (prod_count / total_count * 100) if total_count > 0 else 0.0
        print(f"{act_name:<55} | {total_count:<6} | {prod_count:<7} | {pct:<10.1f}%")

    total_prod = len(prod_sections)
    prod_overall_pct = (total_prod / total_kb * 100) if total_kb > 0 else 0.0
    print("-" * 88)
    print(f"{'TOTAL / OVERALL (prod826 only)':<55} | {total_kb:<6} | {total_prod:<7} | {prod_overall_pct:<10.1f}%")

if __name__ == "__main__":
    main()

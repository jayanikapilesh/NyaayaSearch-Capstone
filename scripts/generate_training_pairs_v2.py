import os
import sys
import json
import time
import argparse
import csv
import re
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("Error: GROQ_API_KEY not found in environment/.env file.")
    sys.exit(1)

client = Groq(api_key=api_key)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UNCOVERED_CSV = os.path.join(BASE_DIR, "..", "data", "uncovered_sections.csv")
KB_EXCEL = os.path.join(BASE_DIR, "..", "Legal_Knowledge_Base_combined.xlsx")
OUTPUT_JSONL = os.path.join(BASE_DIR, "..", "data", "training_pairs_v2.jsonl")
SKIPPED_CSV = os.path.join(BASE_DIR, "..", "data", "training_pairs_v2_skipped.csv")

MODEL_NAME = "openai/gpt-oss-20b"

SYSTEM_PROMPT = """You generate plain-language questions that an ordinary Indian citizen (not a lawyer) might ask when describing their real-life situation, which this specific legal section would answer.

Rules:
- Generate exactly 3 different questions describing different real-life situations.
- Keep each question under 25 words.
- Write naturally in everyday language as a citizen would type into a search box. Talk only about your own situation.
- NEVER mention the name of any law, 'this Act', 'the Act', 'this law's name' or any section number.
- DO NOT copy verbatim legal jargon.
- Each question must be answerable specifically by THIS section.
- IF the section is purely technical (e.g. short title, definitions only, repeal, rules for courts' internal procedure) and no citizen would ask about it, return: {"questions": [], "skip_reason": "explanation why it is technical/not relevant for citizens"}
- Otherwise return ONLY valid JSON: {"questions": ["question 1", "question 2", "question 3"]}
"""

def normalize_sec(sec):
    if pd.isna(sec):
        return ""
    s = str(sec).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s

def load_processed_and_skipped():
    processed = set()
    if os.path.exists(OUTPUT_JSONL):
        with open(OUTPUT_JSONL, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    item = json.loads(line)
                    act = str(item.get("act_name", "")).strip()
                    sec = normalize_sec(item.get("section_number"))
                    if act and sec:
                        processed.add((act, sec))
                except Exception:
                    continue

    skipped = set()
    if os.path.exists(SKIPPED_CSV):
        df_skip = pd.read_csv(SKIPPED_CSV)
        for _, r in df_skip.iterrows():
            act = str(r.get("act_name", "")).strip()
            sec = normalize_sec(r.get("section_number"))
            if act and sec:
                skipped.add((act, sec))

    return processed, skipped

def is_valid_question(q):
    if not q or not isinstance(q, str):
        return False, "Empty or invalid string"
    
    # Case-sensitive check for "Act" (as standalone word or part of Act name, excluding ordinary lowercase words)
    if re.search(r'\bAct\b', q):
        return False, "Contains 'Act'"
        
    # Case-insensitive checks
    q_lower = q.lower()
    if "this act" in q_lower:
        return False, "Contains 'this act'"
    if "the act" in q_lower:
        return False, "Contains 'the act'"
    if "this law" in q_lower:
        return False, "Contains 'this law'"
    if "sanhita" in q_lower:
        return False, "Contains 'sanhita'"
    if "domestic violence act" in q_lower:
        return False, "Contains 'domestic violence act'"
        
    if re.search(r'\bsection\s*\d+\b', q, re.IGNORECASE):
        return False, "Contains section number"
    if re.search(r'\bsec\.\s*\d+\b', q, re.IGNORECASE):
        return False, "Contains sec. number"
        
    words = q.strip().split()
    if len(words) > 25:
        return False, f"Over 25 words ({len(words)} words)"
        
    return True, "OK"

def call_groq_api(act_name, section_number, section_title, legal_text):
    text_snippet = legal_text[:800] if legal_text else ""
    base_user_prompt = f"Act: {act_name}\nSection Number: {section_number}\nSection Title: {section_title}\nLegal Text: {text_snippet}"

    backoff_delays = [10, 20, 40, 60, 60, 60, 60, 60]
    
    # We allow up to 3 generation attempts if validation fails
    feedback = ""
    for gen_pass in range(3):
        user_prompt = base_user_prompt
        if feedback:
            user_prompt += f"\n\nCRITICAL FIX NEEDED: The previous generated questions had invalid references:\n{feedback}\nPlease regenerate 3 questions following all rules strictly without mentioning Act names, 'this Act', 'the Act', or section numbers."
            
        attempt_success = False
        parsed_result = None
        
        for attempt in range(8):
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.7,
                    max_tokens=1000,
                    reasoning_effort="low",
                )
                raw = response.choices[0].message.content.strip()
                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                    raw = raw.strip()
                
                parsed_result = json.loads(raw)
                attempt_success = True
                break
            except Exception as e:
                err_msg = str(e)
                if "tpd" in err_msg.lower() or "tokens per day" in err_msg.lower() or "daily" in err_msg.lower():
                    return None, "DAILY_LIMIT"
                
                if "429" in err_msg or "rate limit" in err_msg.lower() or "tpm" in err_msg.lower() or "rpm" in err_msg.lower():
                    wait_time = backoff_delays[attempt]
                    if "retry-after" in err_msg.lower():
                        import re
                        m = re.search(r"try again in (\d+(?:\.\d+)?)s", err_msg, re.IGNORECASE)
                        if m:
                            wait_time = float(m.group(1)) + 1.0
                    time.sleep(wait_time)
                    continue
                else:
                    if attempt < 7:
                        time.sleep(2)
                        continue
                    return None, f"ERROR: {err_msg}"
        
        if not attempt_success or parsed_result is None:
            return None, "MAX_RETRIES_EXCEEDED"

        questions = parsed_result.get("questions", [])
        skip_reason = parsed_result.get("skip_reason", "")

        if not questions or skip_reason:
            return parsed_result, None

        # Validate questions
        invalid_feedback = []
        valid_questions = []
        for q in questions:
            ok, reason = is_valid_question(q)
            if ok:
                valid_questions.append(q)
            else:
                invalid_feedback.append(f"- Question '{q}': {reason}")
                
        if not invalid_feedback:
            # All valid!
            return {"questions": valid_questions, "skip_reason": ""}, None
            
        feedback = "\n".join(invalid_feedback)
        
    # After 3 passes, filter to only valid questions
    final_questions = [q for q in parsed_result.get("questions", []) if is_valid_question(q)[0]]
    return {"questions": final_questions, "skip_reason": parsed_result.get("skip_reason", "")}, None

    return None, "MAX_RETRIES_EXCEEDED"

def main():
    parser = argparse.ArgumentParser(description="Generate training pairs v2 for uncovered sections")
    parser.add_argument("--act", type=str, required=True, help="Act name to target")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit on sections to process")
    args = parser.parse_args()

    target_act = args.act.strip()
    limit = args.limit

    if not os.path.exists(UNCOVERED_CSV):
        print(f"Error: {UNCOVERED_CSV} not found. Run scripts/coverage_report.py first.")
        sys.exit(1)

    df_unc = pd.read_csv(UNCOVERED_CSV)
    df_unc["clean_act"] = df_unc["act_name"].astype(str).str.strip()
    df_target = df_unc[df_unc["clean_act"] == target_act].copy()

    if df_target.empty:
        print(f"No uncovered sections found for Act: '{target_act}'")
        sys.exit(0)

    print(f"Loading legal text from KB for {target_act}...")
    df_kb = pd.read_excel(KB_EXCEL)
    df_kb["clean_act"] = df_kb["act_name"].astype(str).str.strip()
    df_kb["norm_sec"] = df_kb["section_number"].apply(normalize_sec)
    
    kb_dict = {}
    for _, r in df_kb[df_kb["clean_act"] == target_act].iterrows():
        sec = r["norm_sec"]
        kb_dict[sec] = {
            "section_title": r.get("section_title", ""),
            "legal_text": str(r.get("legal_text", ""))
        }

    processed_set, skipped_set = load_processed_and_skipped()
    
    sections_to_do = []
    for _, r in df_target.iterrows():
        sec = normalize_sec(r["section_number"])
        if (target_act, sec) not in processed_set and (target_act, sec) not in skipped_set:
            sections_to_do.append({
                "act_name": target_act,
                "section_number": sec,
                "section_title": r.get("section_title", "") or kb_dict.get(sec, {}).get("section_title", ""),
                "legal_text": kb_dict.get(sec, {}).get("legal_text", "")
            })

    total_available = len(sections_to_do)
    if limit and limit > 0:
        sections_to_do = sections_to_do[:limit]

    print(f"Found {len(df_target)} uncovered sections for '{target_act}'. {len(processed_set | skipped_set)} already handled. To process: {len(sections_to_do)} (out of {total_available}).")

    if not sections_to_do:
        print("All target sections are already processed or skipped.")
        sys.exit(0)

    # Prepare skipped CSV header if not exists
    if not os.path.exists(SKIPPED_CSV):
        with open(SKIPPED_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["act_name", "section_number", "section_title", "skip_reason", "logged_at"])

    done_count = 0
    skipped_count = 0
    failed_count = 0

    for idx, item in enumerate(sections_to_do):
        sec = item["section_number"]
        act = item["act_name"]
        title = item["section_title"]
        text = item["legal_text"]

        parsed_res, err_type = call_groq_api(act, sec, title, text)

        if err_type == "DAILY_LIMIT":
            print(f"\nDaily limit reached - rerun tomorrow to resume. Sections done so far: {done_count}")
            break

        if parsed_res is None:
            print(f"[{idx+1}/{len(sections_to_do)}] {act} Sec {sec} -> FAILED ({err_type})")
            failed_count += 1
            time.sleep(1)
            continue

        questions = parsed_res.get("questions", [])
        skip_reason = parsed_res.get("skip_reason", "")

        if not questions or skip_reason:
            skipped_count += 1
            reason_clean = str(skip_reason if skip_reason else "No questions generated").strip()
            print(f"[{idx+1}/{len(sections_to_do)}] {act} Sec {sec} -> SKIPPED ({reason_clean})")
            
            with open(SKIPPED_CSV, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([act, sec, title, reason_clean, datetime.now().isoformat()])
        else:
            done_count += 1
            print(f"[{idx+1}/{len(sections_to_do)}] {act} Sec {sec} -> {len(questions)} questions")
            
            now_iso = datetime.now().isoformat()
            with open(OUTPUT_JSONL, "a", encoding="utf-8") as f:
                for q in questions:
                    rec = {
                        "query": q,
                        "act_name": act,
                        "section_number": sec,
                        "section_title": title,
                        "model": MODEL_NAME,
                        "generated_at": now_iso
                    }
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")

        time.sleep(0.5)

    print(f"\nProcessing Complete. Done: {done_count}, Skipped: {skipped_count}, Failed: {failed_count}.")

if __name__ == "__main__":
    main()

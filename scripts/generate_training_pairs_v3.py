import os
import sys
import json
import time
import argparse
import csv
import re
from datetime import datetime
import openpyxl
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
# A teammate's key can be used by setting GROQ_API_KEY_GEN; otherwise the normal key is used.
api_key = os.environ.get("GROQ_API_KEY_GEN") or os.environ.get("GROQ_API_KEY")
if not api_key:
    print("Error: no GROQ_API_KEY_GEN or GROQ_API_KEY found in environment/.env file.")
    sys.exit(1)

client = Groq(api_key=api_key)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KB_EXCEL = os.path.join(BASE_DIR, "..", "Legal_Knowledge_Base_combined.xlsx")
EXCLUDED_CSV = os.path.join(BASE_DIR, "..", "data", "excluded_placeholder_sections.csv")
OUTPUT_JSONL = os.path.join(BASE_DIR, "..", "data", "training_pairs_v3.jsonl")
SKIPPED_CSV = os.path.join(BASE_DIR, "..", "data", "training_pairs_v3_skipped.csv")

MODEL_NAME = "openai/gpt-oss-20b"
MIN_SHORT_QUESTIONS = 2   # at least this many questions must be short and casual
SHORT_MAX_WORDS = 10

# Definition sections are skipped by the script itself (the AI does not reliably skip them).
DEFINITION_TITLE = re.compile(r"^\s*[\u201c\u2018\"']|\bdefinitions?\b|\binterpretation\b|\bmeaning of\b", re.IGNORECASE)
DEFINITION_TEXT = re.compile(r"in this (?:act|code|adhiniyam),?\s*unless the context otherwise requires", re.IGNORECASE)


def is_definition_section(title, text):
    if DEFINITION_TITLE.search(title or ""):
        return True
    return DEFINITION_TEXT.search((text or "")[:300]) is not None


def build_system_prompt(n):
    return f"""You generate questions that an ordinary Indian citizen with NO legal knowledge might type into a search box when facing a real-life problem that this specific legal section would answer.

First, understand the section: in ONE plain sentence, say what this section lets a citizen do, protects them from, or what happens to them. Then write questions about exactly that situation.

Rules for the questions:
- Generate exactly {n} different questions describing different real-life situations.
- At least {MIN_SHORT_QUESTIONS} questions must be SHORT and CASUAL: {SHORT_MAX_WORDS} words or fewer, like a quick phone search (e.g. "cheque bounced what can i do", "boss not paying salary").
- The other questions can describe the situation in one or two sentences, under 25 words.
- Use only everyday words. Do NOT use legal or technical terms from the section (for example: holder in due course, drawee, instrument, endorsement, co-parcener, cognizance, presumption). Describe the situation instead.
- Talk only about your own situation, in the first person.
- NEVER mention the name of any law, 'this Act', 'the Act', 'this Code', any abbreviation of a law, or any section number.
- Every question must be one that THIS section actually answers, according to your one-sentence summary.
- SKIP the section if it is purely technical (short title, extent, commencement, repeal, power to make rules, internal court procedure) and no citizen would ask about it. To skip, return: {{"summary": "", "questions": [], "skip_reason": "short explanation"}}
- Otherwise return ONLY valid JSON: {{"summary": "one plain sentence", "questions": ["question 1", "question 2", ...]}}
"""


# Law names or giveaways that must never appear in a question (checked case-insensitively).
BANNED_PHRASES = [
    "this act", "the act", "this law", "this code", "sanhita", "adhiniyam",
    "domestic violence act", "hindu marriage act", "special marriage act",
    "hindu succession act", "negotiable instruments", "code on wages",
    "code on social security", "dowry prohibition act", "senior citizens act",
    "holder in due course",
]
BANNED_WORDS = ["pocso", "posh", "bsa", "bns", "bnss"]


def normalize_sec(sec):
    if sec is None:
        return ""
    s = str(sec).strip()
    if s.endswith(".0"):
        s = s[:-2]
    return s


def load_excluded():
    excluded = set()
    if os.path.exists(EXCLUDED_CSV):
        with open(EXCLUDED_CSV, "r", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                act = str(row.get("act") or "").strip().lower()
                sec = str(row.get("section") or "").strip().lower()
                if act and sec:
                    excluded.add((act, sec))
    return excluded


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
        with open(SKIPPED_CSV, "r", encoding="utf-8") as f:
            for r in csv.DictReader(f):
                act = str(r.get("act_name", "")).strip()
                sec = normalize_sec(r.get("section_number"))
                if act and sec:
                    skipped.add((act, sec))

    return processed, skipped


def is_valid_question(q):
    if not q or not isinstance(q, str):
        return False, "Empty or invalid string"
    if re.search(r"\bAct\b", q):
        return False, "Contains 'Act'"
    q_lower = q.lower()
    for phrase in BANNED_PHRASES:
        if phrase in q_lower:
            return False, f"Contains '{phrase}'"
    for word in BANNED_WORDS:
        if re.search(rf"\b{word}\b", q_lower):
            return False, f"Contains '{word}'"
    if re.search(r"\bsection\s*\d+\b", q, re.IGNORECASE):
        return False, "Contains section number"
    if re.search(r"\bsec\.\s*\d+\b", q, re.IGNORECASE):
        return False, "Contains sec. number"
    if len(q.strip().split()) > 25:
        return False, "Over 25 words"
    return True, "OK"


def count_short(questions):
    return sum(1 for q in questions if len(q.strip().split()) <= SHORT_MAX_WORDS)


def call_groq_api(n, act_name, section_number, section_title, legal_text):
    text_snippet = legal_text[:1000] if legal_text else ""
    base_user_prompt = (
        f"Act: {act_name}\nSection Number: {section_number}\n"
        f"Section Title: {section_title}\nLegal Text: {text_snippet}"
    )
    system_prompt = build_system_prompt(n)
    backoff_delays = [10, 20, 40, 60, 60, 60, 60, 60]

    feedback = ""
    parsed_result = None
    for gen_pass in range(3):
        user_prompt = base_user_prompt
        if feedback:
            user_prompt += (
                "\n\nCRITICAL FIX NEEDED in your previous answer:\n"
                f"{feedback}\nPlease regenerate {n} questions following ALL rules strictly."
            )

        attempt_success = False
        for attempt in range(8):
            try:
                response = client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    temperature=0.7,
                    max_tokens=1500,
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
                    m = re.search(r"try again in (\d+(?:\.\d+)?)s", err_msg, re.IGNORECASE)
                    if m:
                        wait_time = float(m.group(1)) + 1.0
                    time.sleep(wait_time)
                    continue
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

        invalid_feedback = []
        valid_questions = []
        for q in questions:
            ok, reason = is_valid_question(q)
            if ok:
                valid_questions.append(q)
            else:
                invalid_feedback.append(f"- Question '{q}': {reason}")

        if count_short(valid_questions) < MIN_SHORT_QUESTIONS:
            invalid_feedback.append(
                f"- Only {count_short(valid_questions)} question(s) are short and casual; at least "
                f"{MIN_SHORT_QUESTIONS} must be {SHORT_MAX_WORDS} words or fewer, in everyday words."
            )

        if not invalid_feedback:
            return {"summary": parsed_result.get("summary", ""), "questions": valid_questions, "skip_reason": ""}, None
        feedback = "\n".join(invalid_feedback)

    final_questions = [q for q in parsed_result.get("questions", []) if is_valid_question(q)[0]]
    return {"summary": parsed_result.get("summary", ""), "questions": final_questions,
            "skip_reason": parsed_result.get("skip_reason", "")}, None


def log_skip(act, sec, title, reason):
    with open(SKIPPED_CSV, "a", newline="", encoding="utf-8") as f:
        csv.writer(f).writerow([act, sec, title, reason, datetime.now().isoformat()])


def main():
    parser = argparse.ArgumentParser(description="Generate training questions (v3) for every section of one Act")
    parser.add_argument("--act", type=str, required=True, help="Exact Act name as in the knowledge base")
    parser.add_argument("--n", type=int, default=5, help="Questions per section (default 5)")
    parser.add_argument("--limit", type=int, default=None, help="Optional limit on sections to process")
    parser.add_argument("--sections", type=str, default=None,
                        help="Optional comma-separated section numbers to process, e.g. 138,139,142")
    args = parser.parse_args()

    target_act = args.act.strip()
    only_sections = None
    if args.sections:
        only_sections = {s.strip() for s in args.sections.split(",") if s.strip()}

    print(f"Loading sections for {target_act} from the knowledge base...")
    wb = openpyxl.load_workbook(KB_EXCEL, read_only=True, data_only=True)
    ws = wb.active
    rows = ws.iter_rows(values_only=True)
    headers = [str(h).strip() if h is not None else "" for h in next(rows)]
    i_act = headers.index("act_name")
    i_sec = headers.index("section_number")
    i_title = headers.index("section_title")
    i_text = headers.index("legal_text")

    excluded = load_excluded()
    all_sections = []
    for row in rows:
        act = str(row[i_act]).strip() if row[i_act] is not None else ""
        if act != target_act:
            continue
        sec = normalize_sec(row[i_sec])
        if (act.lower(), sec.lower()) in excluded:
            continue
        if only_sections and sec not in only_sections:
            continue
        all_sections.append({
            "act_name": act,
            "section_number": sec,
            "section_title": str(row[i_title]) if row[i_title] is not None else "",
            "legal_text": str(row[i_text]) if row[i_text] is not None else "",
        })
    wb.close()

    if not all_sections:
        print(f"No sections found for Act: '{target_act}'. Check the exact name (and --sections).")
        sys.exit(0)

    processed_set, skipped_set = load_processed_and_skipped()
    sections_to_do = [s for s in all_sections
                      if (target_act, s["section_number"]) not in processed_set
                      and (target_act, s["section_number"]) not in skipped_set]
    total_available = len(sections_to_do)
    if args.limit and args.limit > 0:
        sections_to_do = sections_to_do[:args.limit]

    print(f"{len(all_sections)} usable sections selected for '{target_act}'. "
          f"To process now: {len(sections_to_do)} (out of {total_available} remaining).")
    if not sections_to_do:
        print("All selected sections are already processed or skipped.")
        sys.exit(0)

    if not os.path.exists(SKIPPED_CSV):
        with open(SKIPPED_CSV, "w", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow(["act_name", "section_number", "section_title", "skip_reason", "logged_at"])

    done_count = skipped_count = failed_count = question_count = 0

    for idx, item in enumerate(sections_to_do):
        act, sec, title = item["act_name"], item["section_number"], item["section_title"]
        tag = f"[{idx+1}/{len(sections_to_do)}] {act} Sec {sec}"

        # Skip definition sections without calling the AI.
        if is_definition_section(title, item["legal_text"]):
            skipped_count += 1
            print(f"{tag} -> SKIPPED (definition section, auto)")
            log_skip(act, sec, title, "Definition section (auto-skipped)")
            continue

        parsed_res, err_type = call_groq_api(args.n, act, sec, title, item["legal_text"])

        if err_type == "DAILY_LIMIT":
            print(f"\nDaily limit reached - rerun later to resume. Sections done so far: {done_count}")
            break

        if parsed_res is None:
            print(f"{tag} -> FAILED ({err_type})")
            failed_count += 1
            time.sleep(1)
            continue

        questions = parsed_res.get("questions", [])
        skip_reason = parsed_res.get("skip_reason", "")
        summary = parsed_res.get("summary", "")

        if not questions or skip_reason:
            skipped_count += 1
            reason_clean = str(skip_reason or "No questions generated").strip()
            print(f"{tag} -> SKIPPED ({reason_clean.encode('ascii', errors='replace').decode('ascii')[:80]})")
            log_skip(act, sec, title, reason_clean)
        else:
            done_count += 1
            question_count += len(questions)
            print(f"{tag} -> {len(questions)} questions")
            now_iso = datetime.now().isoformat()
            with open(OUTPUT_JSONL, "a", encoding="utf-8") as f:
                for q in questions:
                    f.write(json.dumps({
                        "query": q,
                        "act_name": act,
                        "section_number": sec,
                        "section_title": title,
                        "section_summary": summary,
                        "model": MODEL_NAME,
                        "generated_at": now_iso,
                    }, ensure_ascii=False) + "\n")

        time.sleep(0.5)

    print(f"\nDone: {done_count} sections ({question_count} questions), "
          f"Skipped: {skipped_count}, Failed: {failed_count}.")


if __name__ == "__main__":
    main()
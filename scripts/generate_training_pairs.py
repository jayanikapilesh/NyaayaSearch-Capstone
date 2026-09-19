import os
import json
import time
import openpyxl
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

DATASET = os.path.join(os.path.dirname(__file__), "..", "Legal_Knowledge_Base_combined.xlsx")
OUTPUT_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "training_pairs.jsonl")

SYSTEM_PROMPT = """You generate plain-language questions that an ordinary person (not a lawyer) might ask, which this specific legal section would answer.

Rules:
- Generate exactly 2 different questions. No more, no less.
- Keep each question short - under 20 words.
- Questions must be things a real person would type into a search box, in everyday language, no legal jargon.
- Each question must be answerable specifically by THIS section (not generically true of many sections).
- Return ONLY valid JSON, nothing else, no explanation: {"questions": ["question 1", "question 2"]}
"""


def generate_questions(act_name, section_title, legal_text):
    text_snippet = legal_text[:500] if legal_text else ""
    user_prompt = f"Act: {act_name}\nSection title: {section_title}\nSection text: {text_snippet}"

    for attempt in range(2):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.5,
                max_tokens=500,
            )
            raw = response.choices[0].message.content.strip()
            if raw.startswith("```"):
                raw = raw.split("```")[1]
                if raw.startswith("json"):
                    raw = raw[4:]
                raw = raw.strip()
            parsed = json.loads(raw)
            questions = parsed.get("questions", [])
            if questions:
                return questions
        except Exception:
            if attempt == 0:
                time.sleep(1)
                continue
    return []


def main():
    print("Loading legal dataset...")
    wb = openpyxl.load_workbook(DATASET, read_only=True)
    ws = wb.active
    headers = list(next(ws.values))
    records = []
    for row in ws.iter_rows(values_only=True):
        record = dict(zip(headers, row))
        title = str(record.get("section_title") or "").strip().lower()
        if title in {"repeal.", "[repealed.]", "[repealed .].", "[omitted.]."}:
            continue
        records.append(record)

    print(f"Loaded {len(records)} sections")
    print("Generating training pairs (this will take a while)...")

    pairs = []
    failures = 0
    for i, record in enumerate(records):
        act_name = record.get("act_name")
        section_title = record.get("section_title")
        section_number = record.get("section_number")
        legal_text = record.get("legal_text")

        questions = generate_questions(act_name, section_title, legal_text)

        if not questions:
            failures += 1

        for q in questions:
            pairs.append({
                "query": q,
                "act_name": act_name,
                "section_number": str(section_number),
                "section_title": section_title,
            })

        if (i + 1) % 25 == 0:
            print(f"Processed {i + 1}/{len(records)} sections, {len(pairs)} pairs so far, {failures} failures...")
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                for p in pairs:
                    f.write(json.dumps(p) + "\n")

        time.sleep(0.3)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for p in pairs:
            f.write(json.dumps(p) + "\n")

    print(f"\nDone. Generated {len(pairs)} training pairs from {len(records)} sections.")
    print(f"Failures: {failures} ({failures/len(records)*100:.1f}%)")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

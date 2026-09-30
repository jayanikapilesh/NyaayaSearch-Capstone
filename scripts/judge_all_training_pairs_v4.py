"""Judge ALL pairs of data/training_pairs_v4_clean.jsonl with the same judge as scripts/judge_training_pairs_v4.py.

Same model (openai/gpt-oss-120b), same system prompt (imported, not copied), temperature 0, reasoning_effort low. Resumable: every verdict
is appended to data/training_pairs_v4_judge_verdicts.jsonl and pairs already judged are skipped on the next run. A cumulative cost ledger
(data/training_pairs_v4_judge_all_cost.json) stops the run at $10.

    python scripts/judge_all_training_pairs_v4.py            # judge what is left, then write the outputs and the report
    python scripts/judge_all_training_pairs_v4.py --report-only

A pair PASSES when the judge says both "the section really matches the question" and "it sounds like a real person".
Outputs: data/training_pairs_v4_judged.jsonl (passing pairs, original fields) and data/training_pairs_v4_rejected.csv (failures + reason).
Pairs the judge could not answer (API errors after retries) are listed as UNJUDGED in the report and belong to neither file.
"""
import argparse
import collections
import csv
import hashlib
import json
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from judge_training_pairs_v4 import MODEL, PRICE_IN, PRICE_OUT, SYSTEM, load_sections  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DATA = os.path.join(ROOT, "data")
INPUT = os.path.join(DATA, "training_pairs_v4_clean.jsonl")
VERDICTS = os.path.join(DATA, "training_pairs_v4_judge_verdicts.jsonl")
COST_JSON = os.path.join(DATA, "training_pairs_v4_judge_all_cost.json")
OUT_PASS = os.path.join(DATA, "training_pairs_v4_judged.jsonl")
OUT_REJECT = os.path.join(DATA, "training_pairs_v4_rejected.csv")
MAX_COST_USD = 10.0
TPM_BUDGET = 220_000
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def pair_key(r):
    return hashlib.sha1(f"{r['act_name']}|{r['section_number']}|{r['query']}".encode("utf-8")).hexdigest()


class Ledger:
    def __init__(self):
        self.lock = threading.Lock()
        self.window = collections.deque()
        d = json.load(open(COST_JSON)) if os.path.exists(COST_JSON) else {}
        self.pt, self.ct, self.calls = d.get("prompt_tokens", 0), d.get("completion_tokens", 0), d.get("calls", 0)
        self.stop = threading.Event()

    @property
    def cost(self):
        return self.pt * PRICE_IN / 1e6 + self.ct * PRICE_OUT / 1e6

    def wait_for_room(self, est=1200):
        while not self.stop.is_set():
            with self.lock:
                now = time.time()
                while self.window and now - self.window[0][0] > 60:
                    self.window.popleft()
                if sum(t for _, t in self.window) + est <= TPM_BUDGET:
                    return
                wait = 60 - (now - self.window[0][0]) + 0.2
            time.sleep(max(0.2, min(wait, 5)))

    def add(self, usage):
        with self.lock:
            p, c = int(usage.prompt_tokens or 0), int(usage.completion_tokens or 0)
            self.pt += p
            self.ct += c
            self.calls += 1
            self.window.append((time.time(), p + c))
            if self.cost >= MAX_COST_USD:
                self.stop.set()

    def save(self):
        with self.lock:
            json.dump({"prompt_tokens": self.pt, "completion_tokens": self.ct, "calls": self.calls, "estimated_cost_usd": round(self.cost, 4),
                       "model": MODEL, "price_per_million_usd": {"input": PRICE_IN, "output": PRICE_OUT}}, open(COST_JSON, "w"), indent=2)


def judge_all(workers):
    from dotenv import load_dotenv
    from groq import Groq
    load_dotenv()
    key = os.environ.get("GROQ_API_KEY_GEN") or os.environ.get("GROQ_API_KEY")
    if not key:
        sys.exit("no GROQ_API_KEY(_GEN) in the environment/.env")
    client = Groq(api_key=key)
    rows = [json.loads(l) for l in open(INPUT, encoding="utf-8") if l.strip()]
    done = set()
    if os.path.exists(VERDICTS):
        for l in open(VERDICTS, encoding="utf-8"):
            if l.strip():
                try:
                    done.add(json.loads(l)["key"])
                except Exception:
                    pass
    todo = [r for r in rows if pair_key(r) not in done]
    sections = load_sections()
    ledger = Ledger()
    print(f"pairs {len(rows)} | already judged {len(done)} | to judge {len(todo)} | cost so far ${ledger.cost:.3f} (cap ${MAX_COST_USD:.0f}) | workers {workers}", flush=True)
    out_lock = threading.Lock()
    counts = collections.Counter()
    t0 = time.time()

    def judge(r):
        if ledger.stop.is_set():
            return
        title, text = sections.get((r["act_name"], str(r["section_number"])), (r.get("section_title", ""), ""))
        user = f"Law: {r['act_name']}\nSection {r['section_number']}: {title}\nSection text: {text[:1800]}\n\nQuestion: {r['query']}"
        verdict = None
        for attempt in range(6):
            ledger.wait_for_room()
            if ledger.stop.is_set():
                return
            try:
                resp = client.chat.completions.create(model=MODEL, temperature=0, max_tokens=800, reasoning_effort="low",
                                                      messages=[{"role": "system", "content": SYSTEM}, {"role": "user", "content": user}])
                ledger.add(resp.usage)
                m = re.search(r"\{.*\}", (resp.choices[0].message.content or "").strip(), re.S)
                verdict = json.loads(m.group(0))
                break
            except Exception as e:
                time.sleep(5 * (attempt + 1) if ("429" in str(e) or "rate" in str(e).lower()) else 1)
        with out_lock:
            counts["attempted"] += 1
            if verdict is None:
                counts["unanswered"] += 1
            else:
                counts["pass" if (verdict.get("section_matches") and verdict.get("sounds_real")) else "fail"] += 1
                with open(VERDICTS, "a", encoding="utf-8") as f:
                    f.write(json.dumps({"key": pair_key(r), "section_matches": bool(verdict.get("section_matches")),
                                        "sounds_real": bool(verdict.get("sounds_real")), "reason": str(verdict.get("reason", ""))}, ensure_ascii=False) + "\n")
            if counts["attempted"] % 200 == 0:
                ledger.save()
                el = time.time() - t0
                print(f"[{counts['attempted']}/{len(todo)}] pass {counts['pass']} fail {counts['fail']} unanswered {counts['unanswered']} | "
                      f"cost ${ledger.cost:.3f} | {counts['attempted'] / el * 60:.0f} pairs/min | eta {(len(todo) - counts['attempted']) / max(1, counts['attempted'] / el * 60):.0f} min", flush=True)

    with ThreadPoolExecutor(max_workers=workers) as ex:
        list(ex.map(judge, todo))
    ledger.save()
    print(f"run finished: {dict(counts)} | cumulative judge cost ${ledger.cost:.4f} ({ledger.calls} calls)"
          + ("  ** STOPPED: budget reached **" if ledger.stop.is_set() else ""), flush=True)


BUCKETS = [
    ("section only defines / describes something (no action a citizen can take)", r"defin|only (states|describes|lists|provides that)|merely|just (states|defines)"),
    ("section is about a different situation / topic", r"different|instead|neighbou?r|another section|separate|other section|covered by|different (law|act)"),
    ("procedure / administrative / institutional (delegation, powers of authority, funds, staff)", r"delegat|procedur|administrat|authority|officer|commission|fund|committee|board|tribunal jurisdiction|power of"),
    ("section is about penalty / offence, question is about rights or remedy (or vice-versa)", r"penal|punish|offence|cognizable|bailable|fine\b|imprison"),
    ("question too broad / vague for this section", r"broad|vague|generic|too general|unclear|ambiguous"),
    ("does not sound like a real person (terse, unnatural, jargon)", r"terse|unnatural|robotic|jargon|awkward|not how a"),
]


def report():
    from kb_v2_variants_eval import section_type
    rows = [json.loads(l) for l in open(INPUT, encoding="utf-8") if l.strip()]
    verdicts = {}
    for l in open(VERDICTS, encoding="utf-8"):
        if l.strip():
            d = json.loads(l)
            verdicts[d["key"]] = d
    passed, failed, unjudged = [], [], []
    for r in rows:
        v = verdicts.get(pair_key(r))
        if v is None:
            unjudged.append(r)
        elif v["section_matches"] and v["sounds_real"]:
            passed.append(r)
        else:
            failed.append((r, v))
    with open(OUT_PASS, "w", encoding="utf-8") as f:
        for r in passed:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    with open(OUT_REJECT, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)
        w.writerow(["query", "act_name", "section_number", "section_title", "section_matches", "sounds_real", "reason"])
        for r, v in failed:
            w.writerow([r["query"], r["act_name"], r["section_number"], r.get("section_title", ""), v["section_matches"], v["sounds_real"], v["reason"]])
    n = len(rows) - len(unjudged)
    print("=" * 78)
    print(f"pairs in {len(rows)} | judged {n} | PASS {len(passed)} = {100 * len(passed) / max(1, n):.1f}% | FAIL {len(failed)} | UNJUDGED {len(unjudged)}")
    both = sum(1 for _, v in failed if not v["section_matches"] and not v["sounds_real"])
    only_sec = sum(1 for _, v in failed if not v["section_matches"] and v["sounds_real"])
    only_real = sum(1 for _, v in failed if v["section_matches"] and not v["sounds_real"])
    print(f"failures by judged criterion: section does not match only {only_sec} | does not sound real only {only_real} | both {both}")
    bucket_counts = collections.Counter()
    for _, v in failed:
        hit = next((name for name, pat in BUCKETS if re.search(pat, v["reason"], re.I)), "other / unclassified")
        bucket_counts[hit] += 1
    print("\nfailures by reason (keyword grouping of the judge's one-line reason; first match wins):")
    for k, c in bucket_counts.most_common():
        print(f"  {c:>6}  {100 * c / max(1, len(failed)):4.1f}%  {k}")
    per_act = collections.Counter(r["act_name"] for r in rows)
    fail_act = collections.Counter(r["act_name"] for r, _ in failed)
    print("\nfailures by Act (highest failure counts):")
    for a, c in fail_act.most_common(15):
        print(f"  {c:>5} of {per_act[a]:>5} ({100 * c / per_act[a]:4.1f}%)  {a[:70]}")
    print("\nActs with the HIGHEST failure RATE (>= 200 pairs):")
    for a, c in sorted(((a, c) for a, c in fail_act.items() if per_act[a] >= 200), key=lambda x: -x[1] / per_act[x[0]])[:8]:
        print(f"  {100 * c / per_act[a]:4.1f}%  ({c}/{per_act[a]})  {a[:70]}")
    per_type, fail_type = collections.Counter(), collections.Counter()
    for r in rows:
        per_type[section_type(r.get("section_title", ""))] += 1
    for r, _ in failed:
        fail_type[section_type(r.get("section_title", ""))] += 1
    print("\nfailure rate by section type (from the section title):")
    for t, c in per_type.most_common():
        print(f"  {100 * fail_type[t] / c:4.1f}%  ({fail_type[t]}/{c})  {t}")
    return len(passed), len(failed), len(unjudged)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=12)
    ap.add_argument("--report-only", action="store_true")
    args = ap.parse_args()
    if not args.report_only:
        judge_all(args.workers)
    report()
    if os.path.exists(COST_JSON):
        print("\ncost ledger:", open(COST_JSON).read().replace("\n", " "))


if __name__ == "__main__":
    main()

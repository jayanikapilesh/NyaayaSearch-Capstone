"""Diagnose which v2 rows push the correct section out of the top 5 (reads kb_v2_variants_eval.py output).

    python scripts/kb_v2_diagnose.py --run data/open_india_law/variants_run [--system rr|prod]

Lost query = the old KB had the expected section in its top 5 but plain v2 does not. "Newcomers" = rows in v2's top 5
that are not in the old KB's top 5 for that query; the ones from new Acts are the pushers.
"""
import argparse
import collections
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from kb_v2_variants_eval import BOILERPLATE, section_type  # noqa: E402

LANGS = ("en", "hi", "kn")


def load(run):
    raw = json.loads((Path(run) / "raw_results.json").read_text(encoding="utf-8"))
    kb = pd.read_excel(ROOT / "Legal_Knowledge_Base_v2.xlsx", usecols=["act_name", "section_number", "section_title", "source"])
    new = kb[kb.source != "own"]
    return raw, kb, new


def diagnose(raw, kb, new, system, out_lines):
    p = out_lines.append
    new_acts = set(new.act_name)
    old, v2 = raw["old_kb"], raw["v2_plain"]
    lost, gained, total = [], 0, 0
    for lang in LANGS:
        for eo, ev in zip(old[lang], v2[lang]):
            total += 1
            ro, rv = eo[system]["rank"], ev[system]["rank"]
            o5, v5 = ro is not None and ro <= 5, rv is not None and rv <= 5
            if o5 and not v5:
                lost.append((lang, eo, ev))
            elif v5 and not o5:
                gained += 1
    p(f"\n===== {('Production + Reranker' if system == 'rr' else 'Production')}: {len(lost)} queries lost (old top-5 -> v2 not in top-5), {gained} gained, of {total} =====")

    push_rows = collections.Counter()
    push_queries = collections.defaultdict(set)
    push_act = collections.Counter()
    push_act_q = collections.defaultdict(set)
    push_type = collections.Counter()
    push_type_q = collections.defaultdict(set)
    own_only = 0
    slots_new = slots_own = 0
    for qi, (lang, eo, ev) in enumerate(lost):
        old5 = {(a, s) for a, s, _ in eo[system]["top10"][:5]}
        newcomers = [(a, s, t) for a, s, t in ev[system]["top10"][:5] if (a, s) not in old5]
        pushers = [r for r in newcomers if r[0] in new_acts]
        slots_new += len(pushers)
        slots_own += len(newcomers) - len(pushers)
        if not pushers:
            own_only += 1
        for a, s, t in pushers:
            key = (a, s, t)
            push_rows[key] += 1
            push_queries[key].add(qi)
            push_act[a] += 1
            push_act_q[a].add(qi)
            ty = section_type(t)
            push_type[ty] += 1
            push_type_q[ty].add(qi)
    p(f"newcomer slots in v2 top-5 of lost queries: {slots_new} from NEW Acts, {slots_own} from our original Acts")
    p(f"lost queries with no new-Act newcomer in the top 5 (loss caused by reshuffling among original rows): {own_only} of {len(lost)}")

    # base rate: type shares among all new-Act rows in the KB
    base = collections.Counter(section_type(t) for t in new.section_title)
    base_n = sum(base.values())
    tot_push = sum(push_type.values()) or 1
    p("\n-- pushers by SECTION TYPE (share of pushers vs share of all new-Act rows in v2 -> lift) --")
    rows = []
    for ty, c in push_type.most_common():
        share_p, share_b = c / tot_push, base[ty] / base_n
        rows.append((ty, c, len(push_type_q[ty]), f"{100 * share_p:.0f}%", f"{100 * share_b:.0f}%", f"{share_p / share_b:.1f}x" if share_b else "-", "BOILERPLATE" if ty in BOILERPLATE else ""))
    p(pd.DataFrame(rows, columns=["section type", "pusher slots", "lost queries", "share of pushers", "share of new rows", "lift", ""]).to_string(index=False))
    bp = sum(c for ty, c in push_type.items() if ty in BOILERPLATE)
    p(f"boilerplate types (short title / definitions / rule-making / repeal) = {bp} of {tot_push} pusher slots ({100 * bp / tot_push:.0f}%), "
      f"vs {100 * sum(base[t] for t in BOILERPLATE) / base_n:.0f}% of new-Act rows")

    p("\n-- pushers by ACT (top 15) --")
    acts_n = new.groupby("act_name").size()
    rows = [(a[:58], c, len(push_act_q[a]), int(acts_n.get(a, 0))) for a, c in push_act.most_common(15)]
    p(pd.DataFrame(rows, columns=["act", "pusher slots", "lost queries", "rows in KB"]).to_string(index=False))
    top_share = sum(c for _, c in push_act.most_common(5)) / max(1, sum(push_act.values()))
    p(f"top-5 Acts account for {100 * top_share:.0f}% of pusher slots")

    p("\n-- most frequent individual pusher rows (top 20) --")
    rows = [(a[:44], s, (t or "")[:52], c, len(push_queries[(a, s, t)]), section_type(t)) for (a, s, t), c in push_rows.most_common(20)]
    p(pd.DataFrame(rows, columns=["act", "sec", "title", "slots", "lost queries", "type"]).to_string(index=False))
    return lost


def compare_variants(raw, out_lines):
    p = out_lines.append
    labels = list(raw)
    p("\n===== Variants vs old KB (pooled over 270 dev queries: en 150 + hi 60 + kn 60) =====")
    for system, name in (("rr", "Production + Reranker"), ("prod", "Production")):
        rows = []
        for lab in labels:
            rr = []
            for lang in LANGS:
                rr += [e[system] for e in raw[lab][lang]]
            r5 = sum(e["r5"] for e in rr) / len(rr)
            p1 = sum(e["p1"] for e in rr) / len(rr)
            mrr = sum(e["mrr"] for e in rr) / len(rr)
            lost = gained = lost1 = gained1 = 0
            for lang in LANGS:
                for eo, ev in zip(raw["old_kb"][lang], raw[lab][lang]):
                    a, b = eo[system], ev[system]
                    lost += int(a["r5"] == 1 and b["r5"] == 0)
                    gained += int(a["r5"] == 0 and b["r5"] == 1)
                    lost1 += int(a["p1"] == 1 and b["p1"] == 0)
                    gained1 += int(a["p1"] == 0 and b["p1"] == 1)
            rows.append((lab, f"{r5:.4f}", f"{p1:.4f}", f"{mrr:.4f}", f"-{lost}/+{gained}", f"-{lost1}/+{gained1}"))
        p(f"\n{name}")
        p(pd.DataFrame(rows, columns=["config", "R@5", "P@1", "MRR", "R@5 lost/gained vs old", "P@1 lost/gained vs old"]).to_string(index=False))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--system", default="both", choices=["both", "rr", "prod"])
    args = ap.parse_args()
    raw, kb, new = load(args.run)
    lines = []
    for system in (("rr", "prod") if args.system == "both" else (args.system,)):
        diagnose(raw, kb, new, system, lines)
    compare_variants(raw, lines)
    text = "\n".join(lines)
    (Path(args.run) / "diagnosis.txt").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    main()

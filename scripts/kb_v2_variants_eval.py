"""Dev-set evaluation of KB variants: old KB, plain v2, v2 minus boilerplate (a), and (a) + score penalty (b).

Offline experiment script (not part of the request path; the app default is unchanged). Run from the repo root:
    python scripts/kb_v2_variants_eval.py --out <dir> [--penalties 0.95,0.90]

Same evaluation as `eval_reranker.py --strict-clean --languages en,hi,kn` (test_270, cached translations, Production =
search(rerank=False), Production + Reranker = search(rerank=True), top-20 pool, metrics from eval_reranker.compute_query_metrics),
but all variants share ONE v2 engine: rows are sliced out and BM25 is rebuilt, so v2 is embedded once. A per-row score
multiplier is injected by patching the `final_scores * boost` line of SearchEngine.search itself, so scoring is otherwise identical.

State isolation: the embedding cache and the excluded-sections CSV are redirected into --out, so data/ is not touched.
Raw top-10 lists per query are written to <out>/raw_results.json for the diagnosis.
"""
import argparse
import copy
import inspect
import json
import os
import re
import shutil
import sys
import textwrap
import time
import types
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
os.chdir(ROOT)  # --strict-clean shells out to `git diff ... scripts/search_core.py`

# ---------------------------------------------------------------- section types (shared with the diagnosis)
TYPES = [
    ("short title / extent / commencement", r"\bshort title\b|\bcommencement\b|^extent\b|\bextent of (this |the )?act\b|^title\b|application of (this |the )?act\b"),
    ("definitions", r"^(definitions?|interpretation|meaning of|explanation of terms)\b"),
    ("rule-making power", r"power to make (rules|regulations|bye-?laws|by-laws)|power .{0,50}to make (rules|regulations)|^(rules|regulations)\b|rule[- ]making|power to frame rules|rules and regulations|\bbye-?laws?\b"),
    ("repeal / savings", r"repeal|\bsavings?\b"),
    ("removal of difficulties", r"removal of difficult|remove difficult"),
    ("offences / penalties", r"penalt|punish|offence|\bfine\b|imprison|contravention|cognizance|abetment|compounding"),
    ("powers / authority / institutions", r"^(power|powers|duties|functions|constitution|composition|appointment|establishment|incorporation|term of office|disqualification|meetings?|staff|officers?|secretary|chairperson|chairman|members?|authority|board|committee)\b"),
    ("procedure / appeal / jurisdiction", r"appeal|procedure|jurisdiction|revision|review|court|tribunal|application|hearing|notice|summons|order|evidence|complaint|inquiry|enquiry"),
]
BOILERPLATE = {"short title / extent / commencement", "definitions", "rule-making power", "repeal / savings"}


def section_type(title):
    t = re.sub(r"\s+", " ", str(title or "")).strip().lower()
    for name, pat in TYPES:
        if re.search(pat, t):
            return name
    return "other"


def is_new(record):
    return str(record.get("source") or "") not in ("", "own")


# ---------------------------------------------------------------- engine plumbing
def build_engine(sc, kb_env, cache_dir, tag):
    if kb_env:
        os.environ["NYAAYA_KB_PATH"] = kb_env
    else:
        os.environ.pop("NYAAYA_KB_PATH", None)
    sc.CACHE_DIR = str(cache_dir)
    sc.CACHE_FILE = str(cache_dir / f"{tag}.npy")
    sc.CACHE_META_FILE = str(cache_dir / f"{tag}_meta.json")
    sc.EXCLUDED_SECTIONS_FILE = str(cache_dir / f"{tag}_excluded.csv")
    return sc.SearchEngine()


def make_patched_search(sc):
    src = textwrap.dedent(inspect.getsource(sc.SearchEngine.search))
    old = "final_scores = final_scores * boost\n"
    assert old in src, "SearchEngine.search changed: cannot inject the per-row multiplier"
    src = src.replace(old, "final_scores = final_scores * boost * self.row_mult\n")
    ns = {}
    exec(src, sc.__dict__, ns)
    return ns["search"]


def make_variant(sc, base, patched_search, keep, penalty=None):
    """Engine over a subset of the base engine's rows; rows from new Acts get their score multiplied by `penalty`."""
    e = copy.copy(base)
    e.records = [base.records[i] for i in keep]
    e.embeddings = base.embeddings[keep]
    docs = [sc.tokenize(str(r.get("act_name") or "") + " " + str(r.get("section_number") or "") + " " +
                        str(r.get("section_title") or "") + " " + str(r.get("legal_text") or "")) for r in e.records]
    e.bm25 = sc.BM25Okapi(docs)
    e.row_mult = np.array([penalty if (penalty and is_new(r)) else 1.0 for r in e.records], dtype=float)
    e.search = types.MethodType(patched_search, e)
    return e


def evaluate(er, engine, label, log):
    files = {"en": "test_270_en.json", "hi": "test_270_hi.json", "kn": "test_270_kn.json"}
    raw, agg = {}, {}
    for lang, fn in files.items():
        queries = er.load_test_dataset(str(ROOT / "data" / "eval" / fn), lang)
        rows = []
        for q, act, sec in queries:
            sq = q if lang == "en" else er.TRANSLATION_CACHE[er.get_translation_cache_key(q)]
            entry = {"query": sq, "act": act, "section": sec}
            for name, rerank in (("prod", False), ("rr", True)):
                res = engine.search(sq, top_k=20, rerank=rerank)[:10]
                m = er.compute_query_metrics(res, act, sec)
                entry[name] = {"rank": m["rank_of_correct"], "r5": m["recall_at_5"], "p1": m["precision_at_1"], "mrr": m["mrr"],
                               "top10": [[str(r["act_name"]), str(r["section_number"]), str(r.get("section_title") or "")] for r in res]}
            rows.append(entry)
        raw[lang] = rows
        for name in ("prod", "rr"):
            agg[f"{lang}|{name}"] = {k: float(np.mean([e[name][k] for e in rows])) for k in ("r5", "p1", "mrr")}
        log(f"  [{label}] {lang}: prod {agg[f'{lang}|prod']}  rr {agg[f'{lang}|rr']}")
    return raw, agg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--penalties", default="0.95,0.90")
    args = ap.parse_args()
    out = Path(args.out)
    (out / "cache").mkdir(parents=True, exist_ok=True)
    logf = open(out / "variants_eval.log", "a", encoding="utf-8")

    def log(msg):
        print(msg, flush=True)
        logf.write(msg + "\n")
        logf.flush()

    import search_core as sc
    import eval_reranker as er
    er.load_translation_cache()

    # the old KB's embedding cache is only READ: copy it next to the others so the engine never touches data/
    shutil.copy2(ROOT / "data" / "section_embeddings_cache.npy", out / "cache" / "old.npy")
    shutil.copy2(ROOT / "data" / "section_embeddings_cache_meta.json", out / "cache" / "old_meta.json")

    t0 = time.time()
    old = build_engine(sc, None, out / "cache", "old")
    log(f"old KB engine: {len(old.records)} rows ({time.time() - t0:.0f}s)")
    v2 = build_engine(sc, "Legal_Knowledge_Base_v2.xlsx", out / "cache", "v2")
    log(f"v2 engine: {len(v2.records)} rows ({time.time() - t0:.0f}s)")
    er.apply_strict_clean(old)  # in-memory patches on search_core globals: apply to every engine

    patched = make_patched_search(sc)
    n = len(v2.records)
    all_idx = np.arange(n)
    new_mask = np.array([is_new(r) for r in v2.records])
    types_ = [section_type(r.get("section_title")) for r in v2.records]
    boiler = np.array([new_mask[i] and types_[i] in BOILERPLATE for i in range(n)])
    keep_a = all_idx[~boiler]
    log(f"v2 rows {n}: new-Act rows {int(new_mask.sum())}; boilerplate new-Act rows removed by (a): {int(boiler.sum())}; kept {len(keep_a)}")
    by_type = {}
    for i in np.where(boiler)[0]:
        by_type[types_[i]] = by_type.get(types_[i], 0) + 1
    log(f"  removed by type: {by_type}")

    configs = [("old_kb", old), ("v2_plain", make_variant(sc, v2, patched, all_idx)), ("v2_a_no_boilerplate", make_variant(sc, v2, patched, keep_a))]
    for p in [float(x) for x in args.penalties.split(",") if x]:
        configs.append((f"v2_b_no_boilerplate_x{p:.2f}", make_variant(sc, v2, patched, keep_a, penalty=p)))

    raw_all, agg_all = {}, {}
    for label, eng in configs:
        t1 = time.time()
        raw, agg = evaluate(er, eng, label, log)
        raw_all[label], agg_all[label] = raw, agg
        log(f"[{label}] done in {(time.time() - t1) / 60:.1f} min")
        (out / "raw_results.json").write_text(json.dumps(raw_all, ensure_ascii=False), encoding="utf-8")
        (out / "aggregate.json").write_text(json.dumps(agg_all, indent=2), encoding="utf-8")
    log("ALL DONE")


if __name__ == "__main__":
    main()

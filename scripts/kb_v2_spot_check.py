"""Spot check Legal_Knowledge_Base_v2.xlsx: compare random open-india-law sections against the Act PDFs.

Offline verification script (not part of the request path). Run from the repo root:
    python scripts/kb_v2_spot_check.py [--n 20] [--seed 20260930]

For each sampled section the Act PDF is downloaded, text is extracted with pypdf (same library as
scripts/extract_act_text.py), the section is located in the PDF text, and the KB text is compared with the
PDF passage by word overlap: match % = share of the KB section's words found, in order, in the PDF passage.

PDF source: India Code first. India Code refuses non-Indian IPs, so if it cannot be reached the dataset's own
mirror of the same India Code PDF is used instead, and the report says so per row.
"""
import argparse
import difflib
import io
import re
import urllib.request
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
OIL = ROOT / "data" / "open_india_law"
KB = ROOT / "Legal_Knowledge_Base_v2.xlsx"
UA = {"User-Agent": "Mozilla/5.0 (NyaayaSearch KB spot check)"}
RISKY = ["Code of Civil Procedure, 1908", "Indian Stamp Act, 1899"]   # Acts whose dataset numbering was known to be messy


def get(url, timeout=25):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def india_code_pdf(handle_url):
    """Download the Act PDF from India Code (handle page -> bitstream PDF link). Raises if unreachable."""
    page = get(handle_url).decode("utf-8", "ignore")
    m = re.search(r'href="(/bitstream/[^"]+\.pdf[^"]*)"', page)
    if not m:
        raise RuntimeError("no PDF link on India Code handle page")
    return get("https://www.indiacode.nic.in" + m.group(1), timeout=90)


def pdf_text(data):
    reader = PdfReader(io.BytesIO(data))
    return "\n".join((p.extract_text() or "") for p in reader.pages), len(reader.pages)


def toks(s):
    return re.findall(r"[a-z]+|\d+", s.lower())


def locate_and_score(kb_text, sec, pdf_tokens):
    """Best match % of the KB section text against any passage of the PDF that starts like the section."""
    # continuation parts of a split section start "Title (continued). ...": locate them by their body, not the repeated title
    kb_text = re.sub(r"^.{0,200}?\(continued\)\.\s*", "", kb_text, count=1, flags=re.S)
    kb = toks(kb_text)
    if len(kb) < 5:
        return None, "KB text too short to compare"
    k = min(4, len(kb))
    head = kb[:k]
    starts = [i for i in range(len(pdf_tokens) - k) if pdf_tokens[i:i + k] == head]
    if not starts:  # heading text differs slightly: fall back to the section number followed by a few title words
        head2 = kb[:2]
        starts = [i for i in range(len(pdf_tokens) - 2) if pdf_tokens[i:i + 2] == head2]
    if not starts:
        return None, "section heading not found in PDF"
    best, best_i = -1.0, None
    for i in starts[:40]:
        window = pdf_tokens[max(0, i - 3): i + int(len(kb) * 1.4) + 60]
        sm = difflib.SequenceMatcher(None, kb, window, autojunk=False)
        matched = sum(b.size for b in sm.get_matching_blocks())
        score = matched / len(kb)
        if score > best:
            best, best_i = score, i
    return best, ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--seed", type=int, default=20260930)
    ap.add_argument("--extra", type=int, default=3, help="extra sections from each known-risky Act (CPC, Stamp Act)")
    ap.add_argument("--full-act", action="append", default=[], metavar="ACT_NAME",
                    help="score EVERY row of this Act (exact act_name in the KB) instead of sampling; repeatable. "
                         "Writes kb_v2_full_act_check.csv and kb_v2_unverified_rows.csv (rows <90%% or not located)")
    args = ap.parse_args()

    kb = pd.read_excel(KB)
    new = kb[kb.source != "own"].copy()
    acts = pd.read_csv(OIL / "kb_v2_acts.csv")[["name", "act_id"]]
    new = new.merge(acts, left_on="act_name", right_on="name")
    mirrors = {}
    for f in ("in_central_legislation.parquet", "in_karnataka_legislation.parquet"):
        d = pd.read_parquet(OIL / f, columns=["act_id", "mirror_url", "source_url"]).drop_duplicates("act_id")
        mirrors.update({r.act_id: (r.source_url, r.mirror_url) for r in d.itertuples()})

    if args.full_act:
        unknown = set(args.full_act) - set(new.act_name)
        assert not unknown, f"not open-india-law Acts in the KB: {unknown}"
        sample = new[new.act_name.isin(args.full_act)].assign(group="full-act")
    else:
        sample = new.sample(args.n, random_state=args.seed).assign(group="random")
        extra = pd.concat([new[new.act_name == a].sample(min(args.extra, (new.act_name == a).sum()), random_state=args.seed).assign(group="risky-act probe") for a in RISKY]) if args.extra else new.iloc[0:0]
        sample = pd.concat([sample, extra]).sort_values(["group", "act_name"], ascending=[False, True])

    # is India Code reachable at all from here? one quick probe, reported once
    india_ok = True
    try:
        get(mirrors[sample.iloc[0].act_id][0], timeout=20)
    except Exception as e:
        india_ok = False
        print(f"India Code NOT reachable from this machine ({type(e).__name__}: {str(e)[:80]}) -> using the dataset's PDF mirror of the same India Code PDFs")

    cache, rows = {}, []
    for r in sample.itertuples():
        aid = r.act_id
        if aid not in cache:
            data, used = None, ""
            if india_ok:
                try:
                    data, used = india_code_pdf(mirrors[aid][0]), "India Code"
                except Exception:
                    data = None
            if data is None:
                try:
                    data, used = get(mirrors[aid][1], timeout=90), "dataset mirror of India Code PDF"
                except Exception as e:
                    cache[aid] = (None, f"download failed: {type(e).__name__}", 0)
            if data is not None:
                txt, pages = pdf_text(data)
                cache[aid] = (toks(txt), used, pages)
                print(f"  {r.act_name[:55]:55} {pages:>4} pages via {used}")
        ptoks, used, pages = cache[aid]
        if ptoks is None:
            rows.append({"group": r.group, "act": r.act_name, "section": r.section_number, "title": r.section_title, "pdf_source": used, "match_pct": None, "flag": "NO PDF", "note": used})
            continue
        score, note = locate_and_score(r.legal_text, str(r.section_number), ptoks)
        flag = "NOT LOCATED" if score is None else ("BELOW 90%" if score < 0.90 else "ok")
        rows.append({"group": r.group, "act": r.act_name, "section": r.section_number, "title": r.section_title[:70], "pdf_source": used,
                     "kb_words": len(toks(r.legal_text)), "match_pct": None if score is None else round(100 * score, 1), "flag": flag, "note": note})
    out = pd.DataFrame(rows)
    pd.set_option("display.width", 220)
    if args.full_act:
        # merge with earlier full-Act checks: results of Acts checked now replace the old ones, other Acts are kept
        f = OIL / "kb_v2_full_act_check.csv"
        merged = out
        if f.exists():
            old = pd.read_csv(f)
            merged = pd.concat([old[~old.act.isin(set(out.act))], out], ignore_index=True)
        merged.to_csv(f, index=False, encoding="utf-8-sig")
        bad = merged[~(merged.match_pct >= 90)][["act", "section"]]
        bad.to_csv(OIL / "kb_v2_unverified_rows.csv", index=False, encoding="utf-8-sig")
        for act, d in out.groupby("act"):
            ok = d.match_pct >= 90
            print(f"{act[:50]:50} rows {len(d):>4} | >=90%: {ok.sum():>4} ({100 * ok.mean():.0f}%) | below 90%: {(d.match_pct < 90).sum():>4} | not located: {d.match_pct.isna().sum():>4}")
        print(f"\nwrote {len(bad)} rows below 90% / not located (over all Acts in the check file) to kb_v2_unverified_rows.csv")
        return
    out.to_csv(OIL / "kb_v2_spot_check.csv", index=False, encoding="utf-8-sig")
    print(out.to_string(max_colwidth=48, index=False))
    for g, d in out.groupby("group"):
        ok = d.match_pct.notna()
        print(f"\n[{g}] {len(d)} sections | located {ok.sum()} | >=90%: {(d.match_pct >= 90).sum()} | below 90%: {(d.match_pct < 90).sum()} | "
              f"not located/no PDF: {(~ok).sum()} | mean match {d.match_pct.mean():.1f}%")
    print("India Code reachable:", india_ok)


if __name__ == "__main__":
    main()

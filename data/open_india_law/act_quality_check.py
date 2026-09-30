"""Quality check for candidate Acts from the Open India Law legislation files.

Read-only exploration script (not part of the app). Run from the repo root:
    python data/open_india_law/act_quality_check.py

For every candidate Act that is NOT already in our KB (in_kb == "no" in candidate_acts.csv):
  a) re-splits chunks where a new section heading appears inside the text ("**66. Title.** -"),
     fixing the section-number folding (amended sections written as "1[66. ...]" get merged into
     the previous chunk by the dataset's parser);
  b) compares expected vs found section numbers per Act (numeric gaps, excluding sections marked
     omitted / repealed);
  c) writes act_quality_report.csv and sections_fixed.parquet (re-split section text, gitignored).

The 23 Acts that are already in our KB are never touched; three of them (BNS, IT Act, Karnataka Rent
Act) are only used as a calibration test of the splitter, printed to the console.
"""
import html
import re
from pathlib import Path

import pandas as pd

D = Path(__file__).parent
ROOT = D.parent.parent

# a section heading at the start of a line:  "## � **68. Title", "> **1[66. Title", "**43** . **Repealed**"
HEAD = re.compile(
    r"""(?m)^[>\s#_*�—–\d\[\]"'|\-]*?\*\*[\s\[�—]*(?:\d+\s*\[\s*)*(\d+[A-Z]{0,3})\s*(?:\*\*)?\s*\.(?=[\s*_�—–\-\[(A-Z]|$)"""
    r"(?P<rest>[^\n]{0,160})"
)
# "**12 to 15. Omitted**" / "**5-9. Repealed**"
RANGE = re.compile(
    r"(?m)^[>\s#_*�—–\d\[\]]*?\*\*[\s\[�—]*(?:\d+\s*\[\s*)*(\d+)([A-Z]{0,3})\s*(?:to|-|–|—)\s*(\d+)([A-Z]{0,3})\s*(?:\*\*)?\s*\.\s*(?P<rest>[^\n]{0,80})"
)
OMITTED = re.compile(r"\b(omitted|repealed|rep\.|deleted|ins\.? and omitted|not in force|\[\s*\*\s*\*)", re.I)
HEADER_LINE = re.compile(r"\| Section ([^:]+): ([^\n]*)")


def num(sec):
    m = re.match(r"(\d+)([A-Z]*)$", sec)
    return (int(m.group(1)), m.group(2)) if m else None


ID_RE = re.compile(r"_s(\d+)([A-Z]*)(?:_(\d+))?(?:_p(\d+))?(?:_d(\d+))?$")


def doc_order_key(chunk_id):
    """Document order of a chunk: section index, then the section's own parts (_pN), then its sub-sections (_N), then overflow (_dN)."""
    m = ID_RE.search(chunk_id)
    if not m:
        return (10**9, "", 0, 0, 0, chunk_id)
    idx, suf, sub, p, d = m.groups()
    phase = 0 if sub is None else 1
    return (int(idx), suf, phase, int(p or 0) if phase == 0 else int(sub), int(d) if d is not None else -1, chunk_id)


HEADER2 = re.compile(r"^(?:(?:Chapter|Part|CHAPTER|PART)\b[^\n|]*\|\s*)?Section [^\n]*$")
CHAPTER_ONLY = re.compile(r"^(?:Chapter|Part|CHAPTER|PART)\b[^\n]*$")


def chunk_body(text):
    """Chunk text without its leading 'Act: ... | India | Central | In Force' line and 'Chapter X | Section N: title' line(s)."""
    rest = text.split("\n")
    while rest and (rest[0].startswith("Act: ") or HEADER2.match(rest[0]) or CHAPTER_ONLY.match(rest[0])):
        rest = rest[1:]
    return "\n".join(rest)


START_OMITTED = re.compile(r"^[\s*_\ufffd\u2014\u2013\-\[(]*(omitted|repealed|rep\.|deleted)\b", re.I)


def add(secs, sec, seg, ctype=None):
    """Append a text segment to a section, skipping exact repeats (the dataset repeats some overflow chunks)."""
    e = secs.setdefault(sec, {"text": "", "omitted": False, "folded": False, "seen": set()})
    e.setdefault("seen", set())
    key = re.sub(r"\s+", " ", seg).strip()
    if ctype == "schedule":
        # Schedule chunks are numbered like sections (CPC Orders/Rules 1..158 collide with sections 1..158):
        # remember that the section number was seen in a Schedule, but keep the text out of the section
        if key:
            e.setdefault("types_all", set()).add("schedule")
        return
    if key and key in e["seen"]:
        return
    e["seen"].add(key)
    e["text"] += seg
    if ctype and key:
        e.setdefault("types", set()).add(ctype)


def split_act(chunks):
    """Return (sections dict {sec: {'text': str, 'omitted': bool, 'folded': bool}}, labelled set, n_split_chunks)."""
    chunks = chunks.assign(_k=chunks.chunk_id.map(doc_order_key)).sort_values("_k")
    labelled = set(chunks.section_number.fillna("").str.strip()) - {""}
    lab_nums = [num(x)[0] for x in labelled if num(x)]
    cap = (max(lab_nums) + 8) if lab_nums else 10**6  # headings far above any chunk label = schedule/footnote numbering
    secs = {}
    split_chunks = 0
    prev_label = None
    cur = None
    for r in chunks.itertuples():
        label = (r.section_number or "").strip()
        body = chunk_body(r.text)
        # a chunk continues the previous section when it carries the same label as the previous chunk
        if label != prev_label or cur is None:
            cur = label or cur
        prev_label = label
        pos = 0
        heads = [h for h in HEAD.finditer(body) if num(h.group(1))[0] <= cap]
        if any(h.group(1) != label for h in heads):
            split_chunks += 1
        # section title on the header line ("Section 42: Repealed") tells us about omitted sections
        hm = HEADER_LINE.search(r.text.split("\n", 2)[1] if r.text.count("\n") else "")
        if hm and label and START_OMITTED.search(hm.group(2)):
            secs.setdefault(label, {"text": "", "omitted": True, "folded": False})
        for h in heads:
            seg = body[pos:h.start()]
            if cur:
                add(secs, cur, seg, r.section_type)
            cur = h.group(1)
            e = secs.setdefault(cur, {"text": "", "omitted": False, "folded": False})
            e.setdefault("heading_rest", h.group("rest"))
            if cur not in labelled:
                e["folded"] = True
            if START_OMITTED.search(h.group("rest")):
                e["omitted"] = True
            pos = h.start()
        if cur:
            add(secs, cur, body[pos:], r.section_type)
        for m in RANGE.finditer(body):  # "12 to 15. Omitted"
            if START_OMITTED.search(m.group("rest")):
                a, b = int(m.group(1)), int(m.group(3))
                if 0 < b - a < 200:
                    for n in range(a, b + 1):
                        secs.setdefault(str(n), {"text": "", "omitted": True, "folded": False})["omitted"] = True
    return secs, labelled, split_chunks


def check(secs, labelled):
    keyed = {s: num(s) for s in secs}
    nums = sorted({k[0] for k in keyed.values() if k})
    if not nums:
        return [], nums
    # ignore stray numbers far above the bulk (e.g. schedule / footnote numbering)
    top = nums[-1]
    body = [n for n in nums if n <= max(20, nums[int(len(nums) * 0.9)] * 1.5)] or nums
    lo, hi = 1, body[-1]
    have = set(nums)
    missing = [str(n) for n in range(lo, hi + 1) if n not in have]
    # lettered series: 66B and 66D present but 66C absent -> 66C missing (a missing *last* letter is undetectable)
    series = {}
    for k in keyed.values():
        if k and k[1] and len(k[1]) == 1:
            series.setdefault(k[0], set()).add(k[1])
    for n, letters in series.items():
        top_letter = max(letters)
        for L in map(chr, range(ord("A"), ord(top_letter))):
            if L not in letters and L not in "IO":  # Indian drafting skips I and O in lettered series
                missing.append(f"{n}{L}")
    missing.sort(key=lambda x: (num(x)[0], num(x)[1]))
    return missing, (lo, hi, top)


def load_all():
    cen = pd.read_parquet(D / "in_central_legislation.parquet")
    kar = pd.read_parquet(D / "in_karnataka_legislation.parquet")
    return {"Central": cen, "Karnataka": kar}


if __name__ == "__main__":
    cand = pd.read_csv(D / "candidate_acts.csv")
    data = load_all()
    rows, out_secs = [], []
    calib = []
    for r in cand.itertuples():
        chunks = data[r.level][data[r.level].act_id == r.act_id]
        secs, labelled, nsplit = split_act(chunks)
        missing, rng = check(secs, labelled)
        folded = sorted([s for s, e in secs.items() if e["folded"]], key=lambda s: (num(s) or (9999, s)))
        if r.in_kb == "yes":
            if r.title in ("The Bharatiya Nyaya Sanhita, 2023", "The Information Technology Act, 2000", "The KARNATAKA RENT ACT, 1999"):
                calib.append((r, secs, labelled, folded, missing))
            continue
        omitted = [s for s, e in secs.items() if e["omitted"]]
        found_after = {s for s in secs if num(s)}
        status = "OK" if not missing else "NEEDS CHECK"
        ints = sorted(int(m) for m in missing if m.isdigit())
        run = best = 0
        for i, v in enumerate(ints):
            run = run + 1 if i and v == ints[i - 1] + 1 else 1
            best = max(best, run)
        note = ""
        if best >= 10:
            note = f"block of {best} consecutive sections missing: Act truncated in dataset, or Schedule/footnote numbering mixed in"
        elif missing and len(found_after) < 10:
            note = "very few sections present: Act largely absent or only amendment fragments"
        rows.append({
            "act": r.title, "level": r.level, "year": r.year,
            "sections_before_fix": len({s for s in labelled if num(s)}),
            "sections": len(found_after),
            "folded_sections_fixed": len(folded),
            "folded_list": ";".join(folded),
            "omitted_or_repealed": len(omitted),
            "expected_range": f"{rng[0]}-{rng[1]}" if rng else "",
            "missing_count": len(missing),
            "missing_sections": ";".join(map(str, missing)),
            "status": status, "note": note, "act_id": r.act_id,
        })
        for s, e in secs.items():
            out_secs.append({"act_id": r.act_id, "act": r.title, "section_number": s, "text": e["text"].strip(),
                             "omitted": e["omitted"], "folded_fixed": e["folded"],
                             "chunk_types": ",".join(sorted(e.get("types", []))), "heading_rest": e.get("heading_rest", ""),
                             "in_schedule": "schedule" in e.get("types_all", set())})
    rep = pd.DataFrame(rows).sort_values(["status", "missing_count"], ascending=[False, False])
    rep.to_csv(D / "act_quality_report.csv", index=False, encoding="utf-8-sig")
    pd.DataFrame(out_secs).to_parquet(D / "sections_fixed.parquet", index=False)

    print(f"Acts checked (non-KB): {len(rep)}   OK: {(rep.status == 'OK').sum()}   NEEDS CHECK: {(rep.status != 'OK').sum()}")
    print(f"folded sections fixed: {rep.folded_sections_fixed.sum()} across {(rep.folded_sections_fixed > 0).sum()} Acts;"
          f" sections before fix {rep.sections_before_fix.sum()} -> after {rep.sections.sum()}")

    # ---- calibration on KB Acts: does the splitter recover the sections our own workbook has? ----
    kb = pd.read_excel(ROOT / "Legal_Knowledge_Base_combined.xlsx", usecols=["act_name", "section_number"])
    kbmap = {"The Bharatiya Nyaya Sanhita, 2023": "Bharatiya Nyaya Sanhita, 2023",
             "The Information Technology Act, 2000": "Information Technology Act, 2000",
             "The KARNATAKA RENT ACT, 1999": "Karnataka Rent Act, 1999"}
    print("\nCALIBRATION on KB Acts (KB workbook = ground truth; these Acts are not in the report):")
    for r, secs, labelled, folded, missing in calib:
        kbs = set(kb[kb.act_name == kbmap[r.title]].section_number.astype(str).str.strip())
        before = {s for s in labelled if num(s)}
        after = {s for s in secs if num(s)}
        print(f"  {r.title[:34]:34} KB {len(kbs)} | dataset labels {len(before)} -> after split {len(after)} | "
              f"KB sections recovered {len((kbs - before) & after)}/{len(kbs - before)}; still missing {sorted(kbs - after, key=lambda x: (len(x), x))};"
              f" extra vs KB {sorted(after - kbs, key=lambda x: (len(x), x))[:12]}")

"""Extract each new Act's extent clause ("It extends to ...") from the first pages of its PDF (dataset mirror of the India Code PDF).

Offline exploration script (not part of the request path). Run from the repo root:
    python scripts/kb_v2_extent_scan.py
Writes data/open_india_law/kb_v2_extent_scan.csv (act, act_id, extent_clause, source) for every central Act in kb_v2_acts.csv.
Karnataka Acts are not scanned: they are all kept.
"""
import io
import re
import urllib.request
from pathlib import Path

import pandas as pd
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parent.parent
OIL = ROOT / "data" / "open_india_law"
UA = {"User-Agent": "Mozilla/5.0 (NyaayaSearch extent scan)"}
END = r"(?:\.\s+[A-Z(\[]|\n\s*\n|$)"
SUBJECT = r"\b(?:it|this\s+(?:act|code|adhiniyam))\s*(?:\[\s*\d*\s*\]\s*)?"
PATTERNS = [
    # 1. "It extends to ..." / "This Act shall extend to ..."
    re.compile(r"(?is)" + SUBJECT + r"(?:shall\s+|also\s+)?extends?\s+(?:in\s+the\s+first\s+instance\s+)?to\b(.{3,400}?)" + END),
    # 2. "It applies, in the first instance, to the whole of the States of ..."
    re.compile(r"(?is)" + SUBJECT + r"(?:shall\s+)?applies\s*,?\s+(?:in\s+the\s+first\s+instance\s*,?\s*)?to\s+(?:the\s+)?(?:whole|entire|all|States?|Union)\b(.{0,380}?)" + END),
    # 3. "Local extent.-- It applies to the whole of India" / "Extent.-- This Act extends ..."
    re.compile(r"(?is)(?:local\s+)?extent\s*[.—–:-]{1,3}\s*(?=" + SUBJECT + r")(.{3,400}?)" + END),
]


def fetch(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()


def clause(pdf_bytes):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = "\n".join((reader.pages[i].extract_text() or "") for i in range(min(8, len(reader.pages))))
    flat = re.sub(r"\s+", " ", text)
    for pat in PATTERNS:
        m = pat.search(flat)
        if m:
            return re.sub(r"\s+", " ", m.group(0)).strip()
    return ""


def main():
    # scan the stable candidate list (not kb_v2_acts.csv, which the builder rewrites without the removed Acts)
    acts = pd.read_csv(OIL / "candidate_acts.csv")
    acts = acts[(acts.level == "Central") & (acts.in_kb == "no")].rename(columns={"title": "name"})
    urls = {r.act_id: r.mirror_url for r in pd.read_parquet(OIL / "in_central_legislation.parquet", columns=["act_id", "mirror_url"]).drop_duplicates("act_id").itertuples()}
    rows = []
    for i, a in enumerate(acts.itertuples(), 1):
        try:
            q, src = clause(fetch(urls[a.act_id])), "PDF first pages"
        except Exception as e:  # keep going: an Act with no clause is reviewed by title
            q, src = "", f"PDF failed: {type(e).__name__}"
        rows.append({"act": a.name, "act_id": a.act_id, "extent_clause": q, "source": src})
        print(f"{i:>3}/{len(acts)} {a.name[:58]:58} {q[:90]}", flush=True)
    pd.DataFrame(rows).to_csv(OIL / "kb_v2_extent_scan.csv", index=False, encoding="utf-8-sig")


if __name__ == "__main__":
    main()

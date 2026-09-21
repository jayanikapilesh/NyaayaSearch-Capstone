# Comparative Evaluation: NyaayaSearch vs. Nyaaya.org

Nyaaya.org (Vidhi Centre for Legal Policy, est. 2016) was selected as the comparison
baseline: it is the most established, widely-cited public legal-literacy resource for
India, covers overlapping topics (rent, arrest, consumer rights), and - unlike most
alternatives - is a genuine content resource rather than a paywalled professional
research tool (e.g. Manupatra, SCC Online), making it a fair peer comparison for an
accessibility-focused system.

Method: the same two topics tested in our own evaluation (security deposit / landlord
disputes; arrest without warrant) were looked up on Nyaaya.org directly, and the
retrieved content was compared against NyaayaSearch's output on structural and
content criteria. This is a qualitative comparison (not a scored recall/precision
test, since Nyaaya.org is not a retrieval system - it is a curated explainer wiki),
but the criteria below are directly relevant to what makes a legal-access tool useful
and trustworthy.

## Comparison 1: "Landlord not returning security deposit"

| Criterion | Nyaaya.org | NyaayaSearch |
|---|---|---|
| Specific Act/Section cited | None. General guidance only ("there is no specific law... amount is negotiated") | Karnataka Rent Act, 1999, Sections 15, 17, 19, 45 explicitly cited with full original text |
| Actionable next steps | General negotiation advice | Specific procedure: file application with Controller under S17, required documents, penalty provisions |
| Query flexibility | Fixed article; user must browse to the matching topic | Free-text query in the user's own words, system retrieves the matching content |
| Multilingual | Hindi and Kannada available as separate static translated sites | Same explanation dynamically translatable between English/Hindi/Kannada on demand |
| Content currency | Last updated Jun 7, 2022 | Generated live from current Act text at query time |

## Comparison 2: "Arrest without warrant"

| Criterion | Nyaaya.org | NyaayaSearch |
|---|---|---|
| Specific Act/Section cited | References "Indian Penal Code, 1860 and the Code of Criminal Procedure, 1973" generally, no section numbers | Cites specific BNS/BNSS sections (the current 2023 codes) |
| **Legal currency** | **References IPC/CrPC (1860/1973), which were repealed and replaced by BNS/BNSS effective July 2024** | **Uses BNS/BNSS 2023, the codes currently in force** |
| Content depth | Comprehensive, well-written, human-curated by legal experts | Grounded directly in statutory text, generated per-query |
| Content currency | Last updated Jun 22, 2022 (predates the 2023 code replacement) | Reflects current law |

## Comparison 3: "Consumer complaint for a defective product"

| Criterion | Nyaaya.org | NyaayaSearch |
|---|---|---|
| Specific Act/Section cited | Yes - this article cites Sections 2(5), 2(6), 2(7) of the Consumer Protection Act, 2019 via footnotes | Cites Consumer Protection Act, 2019 sections with full original text inline |
| Actionable next steps | Lists complaint forums (district/state/national commissions), INGRAM portal | Similar procedural guidance grounded in the Act text |
| Content currency | Article dated as recently as 2026 (appears actively maintained) | Generated live |

**Important correction to Comparisons 1-2:** this third comparison shows Nyaaya.org
DOES cite specific sections on some topics (Consumer Protection here) but not on
others (Security Deposit, Arrest, checked above). Citation practice is inconsistent
across their content rather than uniformly absent - this is a more accurate and
more interesting finding than claiming they never cite sections. The real, consistent
difference found across all three comparisons is: (a) NyaayaSearch always includes
the full original statutory text inline for verification, not just a citation number,
and (b) NyaayaSearch is generated from the current Act text at query time, so it
cannot lag behind updates like the confirmed IPC/CrPC vs BNS/BNSS gap found in
Comparison 2.

## Honest Assessment

**Where Nyaaya.org is stronger:**
- Content is written and reviewed by legal experts, not AI-generated - likely more
  polished prose and less risk of subtle AI generation errors
- Broader topical coverage (9 major themes, hundreds of articles) versus NyaayaSearch's
  11 Acts
- Established credibility, sample forms, video content, and community Q&A (visible in
  comments) that NyaayaSearch does not offer
- No dependency on an LLM API, so no rate-limiting or hallucination risk at all

**Where NyaayaSearch is stronger:**
- **Explicit statutory citation** (Act name + Section number + verbatim text) on every
  answer - Nyaaya.org cites specific sections on some topics but not others
- **Legal currency**: Nyaaya.org's arrest-related content still references the
  pre-2024 IPC/CrPC framework, which was fully repealed and replaced by BNS/BNSS in
  July 2024. NyaayaSearch is built directly on the current codes. This is a
  significant, concrete finding: a widely-used, well-established legal literacy
  resource contains content that is now legally outdated on a core topic (arrest law),
  which underscores the real-world value of a system that generates explanations
  directly from current statutory text rather than relying on periodically-updated
  static content.
- **Free-text query interface**: users describe their situation in their own words;
  Nyaaya.org requires browsing a fixed topic hierarchy or knowing the right search term
- **Dynamic, on-demand multilingual translation** of the same answer, versus separate
  static translated sites that may lag behind the English content in updates
- **Integrated toolset**: document drafting, case simplification, BNS section lookup,
  and PDF analysis in one system, versus Nyaaya.org's explainer-only format

## Implication for the Paper

This comparison supports the core research-gap claim: existing accessible legal
resources for India prioritize breadth and expert-curated content, but do not
consistently provide direct statutory citation or guarantee currency against recent
legal changes (e.g. the 2023 BNS/BNSS replacement of IPC/CrPC). A RAG-based system
generating from live statutory text, as built here, offers a genuine and demonstrable
advantage on exactly this dimension - even while being narrower in topical breadth and
lacking Nyaaya.org's human-expert review.

This finding (Nyaaya.org referencing repealed IPC/CrPC provisions) should be stated
factually and without exaggeration in the paper: it does not mean Nyaaya.org is
unreliable overall, only that its specific arrest-related content had not yet been
updated to reflect the 2024 code replacement at the time of this comparison
(content dated June 2022).





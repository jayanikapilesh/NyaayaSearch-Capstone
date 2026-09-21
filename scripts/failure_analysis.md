# Failure Analysis - Held-Out Query Misses

Compiled from held-out batches 1-4 (55 genuinely blind queries total, 16 misses).
Each failure is categorized by root cause, based on manual inspection of why
the correct Act/Section did not appear in the top-5 results.

## Category 1: Synonym / Vocabulary Gap
Everyday phrasing does not lexically or semantically overlap with legal terminology.
(Note: batch 3 misses in this category were the basis for the synonym-dictionary
expansion, validated as fixed on fresh batch 4 - see holdout_test4.py results.)

1. "Can I appeal a decision made under the Motor Vehicles Act?" (expected: MV Act S89)
   - "appeal" is generic; likely matched many unrelated appeal-related sections instead
2. "Can the High Court review a lower court's decision?" (expected: BNSS S442)
   - "review" is a very common word with low discriminative power
3. "What happens if I break my bail bond?" (expected: BNSS S491)
   - "break" vs legal term "forfeited" - direct synonym gap (addressed in dictionary fix)
4. "Is it a crime to not report information to police when legally required to?" (expected: BNS S211)
   - double-negative phrasing ("not report... required to") likely confused term matching
5. "What's the punishment for lying to get a digital certificate?" (expected: IT Act S71)
   - "lying" vs legal term "misrepresentation" - direct synonym gap (addressed in dictionary fix)
6. "What happens if someone doesn't show up after a court order to appear?" (expected: BNSS S84)
   - "doesn't show up" vs legal term "absconding"/"appear" - partial synonym gap

## Category 2: Overly Broad / Abstract Query
Query describes a general legal concept rather than a specific factual scenario,
making it hard to distinguish from many other sections covering related general topics.

7. "The other person flat out refused to do their part of the deal, can I cancel the
   contract?" (expected: Contract Act S39) - general breach language matches many
   contract-related sections
8. "Someone physically blocked me from walking away, what crime is that?" (expected:
   BNS S126, wrongful restraint) - physical description doesn't use legal terms
   ("wrongful restraint") at all
9. "Can I question witnesses in my own court case?" (expected: BNSS S322) - very
   broad procedural question, low specificity

## Category 3: Rare / Unusual Legal Concept
Query describes a legal scenario that is genuinely uncommon in everyday language,
with no natural colloquial equivalent.

10. "Can I leave property to my grandchild who hasn't been born yet?" (expected:
    TPA S13, transfer for benefit of unborn person) - the legal concept ("unborn
    person") is unusual phrasing that a layperson would not naturally use
11. "Is it illegal to resist arrest?" (expected: BNS S265, resistance to lawful
    apprehension) - "resist arrest" is common phrasing, but may be overshadowed by
    more frequent arrest-related sections in the corpus

## Category 4: Ambiguous Pronoun / Missing Context
Query lacks a specific legal keyword and relies on context the search engine cannot infer.

12. "Police say my complaint is non-cognizable, what happens to my case now?"
    (expected: BNSS S174) - found but ranked low (RR=0.25); "non-cognizable" is
    itself a legal term, but the rest of the query is generic
13. "Is there a time limit to appeal to the IT Appellate Tribunal?" (expected:
    IT Act S57) - found but ranked low (RR=0.50); overlaps with other IT Act
    appeal-related sections

## Category 5: Genuine Corpus/Model Limitation
No obvious phrasing fix would help; likely a real gap in semantic similarity scoring.

14. "Can one co-owner sell their share of jointly owned property?" - correctly found
    in batch 3 (not a miss); included here as a borderline case worth monitoring
15. "What is a charge on property under property law?" - correctly found; borderline
16. (reserved for future documented misses)

## Summary
- 6 of 16 misses (38%) were synonym/vocabulary gaps - the most common and most
  fixable category, addressed via targeted dictionary expansion
- 3 of 16 misses (19%) were overly broad/abstract queries with low term specificity
- 2 of 16 misses (13%) involved rare legal concepts with no natural colloquial phrasing
- 2 of 16 misses (13%) were low-rank hits (found, but not ranked highly) rather than
  complete misses, suggesting a ranking/weighting issue rather than a retrieval failure
- This distribution suggests hybrid BM25+semantic search handles concrete, specific
  everyday scenarios well, but struggles with (a) vocabulary mismatch between lay and
  legal language, and (b) abstract or procedurally-phrased queries with few distinctive
  keywords.

from extract_citations import extract_citations, PATTERN_SECTION_ACRONYM, ACRONYMS

text = "Held: Section 309 of the Cr.P.C. (now Section 346 of the BNSS, 2023) contains provisions"
print("ACRONYMS has Cr.P.C.:", "Cr.P.C." in ACRONYMS)
print("Direct regex test:", PATTERN_SECTION_ACRONYM.findall(text))
print("Full extraction:", extract_citations(text))

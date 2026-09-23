from extract_citations import extract_citations

text = "Foreign Contribution (Regulation) Act, 1976 - s. 23 r/w. s. 4"
print("With parenthetical:", extract_citations(text))

text2 = "Foreign Contribution Act, 1976 - s. 23"
print("Without parenthetical:", extract_citations(text2))

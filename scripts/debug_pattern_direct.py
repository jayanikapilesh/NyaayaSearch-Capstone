from extract_citations import PATTERN_US_OF

text = "convicted by the Trial Court u/ss.306 and 114 of Penal Code, 1860 and sentenced"
print("Direct pattern test:", PATTERN_US_OF.findall(text))
print("\nPattern itself:")
print(PATTERN_US_OF.pattern)

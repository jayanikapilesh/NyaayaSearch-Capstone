from extract_citations import extract_citations

text1 = "the (Lease and Rent Control) Act, 1965; and whether the transfer of possession"
print("Multi-word parenthetical test:", extract_citations(text1 + " s. 5"))

text2 = "Code of Criminal Procedure. 1973 - s. 408 - Power of Sessions"
print("Period before year test:", extract_citations(text2))

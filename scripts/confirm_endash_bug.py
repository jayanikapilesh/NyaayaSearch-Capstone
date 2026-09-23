from extract_citations import extract_citations

text = "Transfer of Property Act, 1882 \u2013 s. 48 - One CLR was the owner"
print("Testing with EN-DASH:", extract_citations(text))

text2 = "Transfer of Property Act, 1882 - s. 48 - One CLR was the owner"
print("Testing with regular hyphen:", extract_citations(text2))

from pypdf import PdfReader
import sys
import os

pdf_path = sys.argv[1]

base_name = os.path.splitext(os.path.basename(pdf_path))[0]
output_path = f"data/processed/{base_name}.txt"

reader = PdfReader(pdf_path)

text = ""

for page in reader.pages:
    page_text = page.extract_text()
    if page_text:
        text += page_text + "\n"

with open(output_path, "w", encoding="utf-8") as file:
    file.write(text)

print("PDF text extracted successfully!")
print("Pages:", len(reader.pages))
print("Saved to:", output_path)
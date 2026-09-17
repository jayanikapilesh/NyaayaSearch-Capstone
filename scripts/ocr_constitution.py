import fitz
import pytesseract
from PIL import Image
import os

pytesseract.pytesseract.tesseract_cmd = os.environ.get(
    "TESSERACT_PATH", r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

input_path = "data/raw/Constitution of India.pdf"
output_path = "data/processed/constitution_of_india_ocr.txt"

doc = fitz.open(input_path)

os.makedirs("data/processed", exist_ok=True)

with open(output_path, "w", encoding="utf-8") as output:

    for i, page in enumerate(doc):
        print(f"Processing page {i + 1}/{len(doc)}...", flush=True)

        pix = page.get_pixmap(
            matrix=fitz.Matrix(1.3, 1.3),
            alpha=False
        )

        image = Image.frombytes(
            "RGB",
            [pix.width, pix.height],
            pix.samples
        )

        text = pytesseract.image_to_string(
            image,
            config="--psm 6"
        )

        output.write(f"\n--- PAGE {i + 1} ---\n")
        output.write(text)

doc.close()

print("\nOCR completed!")
print("Saved to:", output_path)
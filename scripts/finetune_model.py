import json
import os
import openpyxl
from sentence_transformers import SentenceTransformer, InputExample, losses
from torch.utils.data import DataLoader

TRAINING_PAIRS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "training_pairs.jsonl")
DATASET = os.path.join(os.path.dirname(__file__), "..", "Legal_Knowledge_Base_combined.xlsx")
OUTPUT_MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "finetuned_legal_model")

print("Loading legal dataset to look up section text...")
wb = openpyxl.load_workbook(DATASET, read_only=True)
ws = wb.active
headers = list(next(ws.values))
section_lookup = {}
for row in ws.iter_rows(values_only=True):
    record = dict(zip(headers, row))
    key = (str(record.get("act_name")), str(record.get("section_number")))
    text = (
        str(record.get("act_name") or "") + ". " +
        str(record.get("section_title") or "") + ". " +
        str(record.get("legal_text") or "")
    )
    section_lookup[key] = text

print("Loading training pairs...")
examples = []
missing = 0
with open(TRAINING_PAIRS_FILE, "r", encoding="utf-8") as f:
    for line in f:
        pair = json.loads(line)
        key = (str(pair["act_name"]), str(pair["section_number"]))
        section_text = section_lookup.get(key)
        if section_text is None:
            missing += 1
            continue
        examples.append(InputExample(texts=[pair["query"], section_text[:500]]))

print(f"Built {len(examples)} training examples ({missing} could not be matched to a section)")

print("Loading base model...")
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

train_dataloader = DataLoader(examples, shuffle=True, batch_size=16)
train_loss = losses.MultipleNegativesRankingLoss(model)

print("Starting fine-tuning (this may take a while on CPU)...")
model.fit(
    train_objectives=[(train_dataloader, train_loss)],
    epochs=3,
    warmup_steps=int(len(train_dataloader) * 0.1),
    show_progress_bar=True,
)

model.save(OUTPUT_MODEL_DIR)
print(f"\nDone. Fine-tuned model saved to {OUTPUT_MODEL_DIR}")

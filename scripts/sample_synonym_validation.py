import openpyxl
import random

wb = openpyxl.load_workbook("../Legal_Knowledge_Base_combined.xlsx", read_only=True)
ws = wb.active
headers = list(next(ws.values))
records = []
for row in ws.iter_rows(values_only=True):
    record = dict(zip(headers, row))
    records.append(record)

random.seed(60513)
sample = random.sample(records, 20)
for r in sample:
    print(f"{r.get('act_name')} | Section {r.get('section_number')}: {r.get('section_title')}")

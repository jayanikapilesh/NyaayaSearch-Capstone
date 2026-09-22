import openpyxl

wb = openpyxl.load_workbook("../Legal_Knowledge_Base_combined.xlsx", read_only=True)
ws = wb.active
headers = list(next(ws.values))

for row in ws.iter_rows(values_only=True):
    record = dict(zip(headers, row))
    act_name = str(record.get("act_name") or "")
    section_number = str(record.get("section_number") or "")
    if "bharatiya nyaya sanhita" in act_name.lower() and section_number == "103":
        print(f"FOUND: act_name={repr(act_name)}, section_number={repr(section_number)}")
        print(f"Title: {record.get('section_title')}")

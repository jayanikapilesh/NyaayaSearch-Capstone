content = open("extract_citations.py", encoding="utf-8").read()

old_pattern = """PATTERN_CODE_SECTION = re.compile(
    rf"((?:{WORD}\\s+){{0,5}}(?:Penal Code|Code of Criminal Procedure|Code of Civil Procedure|Insolvency and Bankruptcy Code)),?\\s*\\d{{4}}\\s*[:\\-\u2013\u2014]?\\s*(?:ss?\\.?|Sections?)\\s*(\\d+[A-Za-z]?(?:/\\d+[A-Za-z]?)*(?:\\(\\w+\\))?)",
)"""
new_pattern = """PATTERN_CODE_SECTION = re.compile(
    rf"((?:{WORD}\\s+){{0,5}}(?:Penal Code|Code of Criminal Procedure|Code of Civil Procedure|Insolvency and Bankruptcy Code)),?\\s*\\d{{4}}\\s*[:\\-\u2013\u2014]?\\s*(?:ss?\\.?|Sections?)\\s*((?:\\d+[A-Za-z]?(?:/\\d+[A-Za-z]?)*(?:\\(\\w+\\))?\\s*(?:,\\s*|and\\s+))*\\d+[A-Za-z]?(?:/\\d+[A-Za-z]?)*(?:\\(\\w+\\))?)",
)"""
count1 = content.count(old_pattern)
print(f"Pattern fix: found {count1}")
if count1 == 1:
    content = content.replace(old_pattern, new_pattern)

old_loop = """    for code_name, section in PATTERN_CODE_SECTION.findall(text):
        cleaned = clean_act_name(code_name)
        if cleaned.lower() not in BLOCKLIST:
            for sec in section.split("/"):
                citations.append({
                    "act_name": cleaned,
                    "section_number": sec,
                    "low_confidence": is_low_confidence_section(sec),
                    "source_pattern": "code_year_section",
                })
            found_any_named_act = True"""
new_loop = """    for code_name, section_list in PATTERN_CODE_SECTION.findall(text):
        cleaned = clean_act_name(code_name)
        if cleaned.lower() not in BLOCKLIST:
            comma_split = re.split(r"\\s*,\\s*|\\s+and\\s+", section_list)
            for section_piece in comma_split:
                section_piece = section_piece.strip()
                for sec in section_piece.split("/"):
                    sec = sec.strip()
                    if sec:
                        citations.append({
                            "act_name": cleaned,
                            "section_number": sec,
                            "low_confidence": is_low_confidence_section(sec),
                            "source_pattern": "code_year_section",
                        })
            found_any_named_act = True"""
count2 = content.count(old_loop)
print(f"Loop fix: found {count2}")
if count2 == 1:
    content = content.replace(old_loop, new_loop)

open("extract_citations.py", "w", encoding="utf-8").write(content)
print("Done")

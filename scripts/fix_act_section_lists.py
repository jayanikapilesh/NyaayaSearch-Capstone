content = open("extract_citations.py", encoding="utf-8").read()

old_pattern = """PATTERN_ACT_SECTION = re.compile(
    rf"((?:{WORD}\\s+){{1,6}}Act,?\\s*\\d{{4}})\\s*[\\-\u2013\u2014]?\\s*[:\\-\u2013\u2014]?\\s*(?:s\\.?|Sections?)\\s*(\\d+[A-Za-z]?(?:\\(\\w+\\))?)",
)"""
new_pattern = """PATTERN_ACT_SECTION = re.compile(
    rf"((?:{WORD}\\s+){{1,6}}Act,?\\s*\\d{{4}})\\s*[\\-\u2013\u2014]?\\s*[:\\-\u2013\u2014]?\\s*(?:ss?\\.?|Sections?)\\s*((?:\\d+[A-Za-z]?(?:\\(\\w+\\))?\\s*(?:,\\s*|and\\s+))*\\d+[A-Za-z]?(?:\\(\\w+\\))?)",
)"""
count1 = content.count(old_pattern)
print(f"Pattern fix: found {count1}")
if count1 == 1:
    content = content.replace(old_pattern, new_pattern)

old_loop = """    for act_name, section in PATTERN_ACT_SECTION.findall(text):
        cleaned = clean_act_name(act_name)
        if cleaned.lower() not in BLOCKLIST:
            citations.append({
                "act_name": cleaned,
                "section_number": section,
                "low_confidence": is_low_confidence_section(section),
                "source_pattern": "act_year_section",
            })
            found_any_named_act = True"""
new_loop = """    for act_name, section_list in PATTERN_ACT_SECTION.findall(text):
        cleaned = clean_act_name(act_name)
        if cleaned.lower() not in BLOCKLIST:
            individual_sections = re.split(r"\\s*,\\s*|\\s+and\\s+", section_list)
            for section in individual_sections:
                section = section.strip()
                if section:
                    citations.append({
                        "act_name": cleaned,
                        "section_number": section,
                        "low_confidence": is_low_confidence_section(section),
                        "source_pattern": "act_year_section",
                    })
            found_any_named_act = True"""
count2 = content.count(old_loop)
print(f"Loop fix: found {count2}")
if count2 == 1:
    content = content.replace(old_loop, new_loop)

open("extract_citations.py", "w", encoding="utf-8").write(content)
print("Done")

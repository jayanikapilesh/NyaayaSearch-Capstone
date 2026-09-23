content = open("extract_citations.py", encoding="utf-8").read()

old_pattern = """PATTERN_US_OF = re.compile(
    rf"u[/l1]ss?\\.?\\s*(\\d+[A-Za-z]?(?:\\(\\w+\\))?)\\s*of\\s*(?:the\\s*)?((?:{WORD}\\s+){{1,6}}Act)",
)"""
new_pattern = """PATTERN_US_OF = re.compile(
    rf"u[/l1]ss?\\.?\\s*((?:\\d+[A-Za-z]?(?:\\(\\w+\\))?\\s*(?:,\\s*|and\\s+))*\\d+[A-Za-z]?(?:\\(\\w+\\))?)\\s*of\\s*(?:the\\s*)?((?:{WORD}\\s+){{1,6}}Act)",
)"""
count1 = content.count(old_pattern)
print(f"Pattern update: found {count1}")
if count1 == 1:
    content = content.replace(old_pattern, new_pattern)

old_loop = """    for section, act_name in PATTERN_US_OF.findall(text):
        cleaned = clean_act_name(act_name)
        if cleaned.lower() not in BLOCKLIST:
            citations.append({
                "act_name": cleaned,
                "section_number": section,
                "low_confidence": is_low_confidence_section(section),
                "source_pattern": "us_of_act",
            })
            found_any_named_act = True"""
new_loop = """    for section_list, act_name in PATTERN_US_OF.findall(text):
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
                        "source_pattern": "us_of_act",
                    })
            found_any_named_act = True"""
count2 = content.count(old_loop)
print(f"Loop update: found {count2}")
if count2 == 1:
    content = content.replace(old_loop, new_loop)

open("extract_citations.py", "w", encoding="utf-8").write(content)
print("Done")

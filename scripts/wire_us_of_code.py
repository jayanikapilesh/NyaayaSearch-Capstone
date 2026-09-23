content = open("extract_citations.py", encoding="utf-8").read()
old = """    for section_list, act_name in PATTERN_US_OF.findall(text):
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
new = """    for section_list, act_name in PATTERN_US_OF.findall(text):
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
            found_any_named_act = True

    for section_list, code_name in PATTERN_US_OF_CODE.findall(text):
        cleaned = clean_act_name(code_name)
        if cleaned.lower() not in BLOCKLIST:
            individual_sections = re.split(r"\\s*,\\s*|\\s+and\\s+", section_list)
            for section in individual_sections:
                section = section.strip()
                if section:
                    citations.append({
                        "act_name": cleaned,
                        "section_number": section,
                        "low_confidence": is_low_confidence_section(section),
                        "source_pattern": "us_of_code",
                    })
            found_any_named_act = True"""
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("extract_citations.py", "w", encoding="utf-8").write(content)
    print("Wired PATTERN_US_OF_CODE into extract_citations()")

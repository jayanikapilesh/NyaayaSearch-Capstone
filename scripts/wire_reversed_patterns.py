content = open("extract_citations.py", encoding="utf-8").read()
old = """    # Constitution Article references - always flagged with a fixed "act name"
    for section in PATTERN_ARTICLE.findall(text):"""
new = """    for section, act_name in PATTERN_SECTION_OF_ACT.findall(text):
        cleaned = clean_act_name(act_name)
        if cleaned.lower() not in BLOCKLIST:
            citations.append({
                "act_name": cleaned,
                "section_number": section,
                "low_confidence": is_low_confidence_section(section),
                "source_pattern": "section_of_act",
            })
            found_any_named_act = True

    for section, code_name in PATTERN_SECTION_OF_CODE.findall(text):
        cleaned = clean_act_name(code_name)
        if cleaned.lower() not in BLOCKLIST:
            citations.append({
                "act_name": cleaned,
                "section_number": section,
                "low_confidence": is_low_confidence_section(section),
                "source_pattern": "section_of_code",
            })
            found_any_named_act = True

    for section, acronym in PATTERN_SECTION_ACRONYM.findall(text):
        full_name = ACRONYMS.get(acronym, acronym)
        citations.append({
            "act_name": full_name,
            "section_number": section,
            "low_confidence": is_low_confidence_section(section),
            "source_pattern": "section_acronym",
        })
        found_any_named_act = True

    # Constitution Article references - always flagged with a fixed "act name"
    for section in PATTERN_ARTICLE.findall(text):"""
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("extract_citations.py", "w", encoding="utf-8").write(content)
    print("Wired the 3 new patterns into extract_citations()")

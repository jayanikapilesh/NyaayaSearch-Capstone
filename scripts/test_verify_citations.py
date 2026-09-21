from rag_core import verify_citations

fake_results = [
    {"section_number": "97"},
    {"section_number": "17"},
    {"section_number": "44"},
]

# Test 1: explanation only mentions sections that WERE retrieved - should be valid
good_explanation = "Under Section 97 and Section 17, you have certain rights."
is_valid, unverified = verify_citations(good_explanation, fake_results)
print(f"Test 1 (should be VALID): is_valid={is_valid}, unverified={unverified}")

# Test 2: explanation mentions a section that was NOT retrieved - should be flagged
bad_explanation = "Under Section 97, you have rights. Also see Section 999 for more detail."
is_valid, unverified = verify_citations(bad_explanation, fake_results)
print(f"Test 2 (should be INVALID): is_valid={is_valid}, unverified={unverified}")

# Test 3: no sections mentioned at all - should be valid (nothing to check)
no_section_explanation = "This situation is governed by general contract principles."
is_valid, unverified = verify_citations(no_section_explanation, fake_results)
print(f"Test 3 (should be VALID): is_valid={is_valid}, unverified={unverified}")

content = open("METRICS_AND_MODEL_COMPARISON.md", encoding="utf-8").read()
old = """| Coverage | 24.9% (2,180/8,757) | **26.8% (2,349/8,757)** |"""
new = """| Coverage | 24.9% (2,180/8,757) | **41.8% (3,659/8,757)** |

**Update (later same session):** a second, much larger fix was found - nearly all headnote-
style citations use an EN-DASH character instead of a regular hyphen, which the regex
patterns did not recognize. This was a structural/encoding bug, not a content-specific
pattern, confirmed via direct A/B test (identical text, only the dash character differed).
Fixing this took coverage from 26.8% to 41.8% - a genuine +15pp jump from one root-cause fix.
Proof: git commit `7963f58`, `scripts/confirm_endash_bug.py` for the A/B test."""
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("METRICS_AND_MODEL_COMPARISON.md", "w", encoding="utf-8").write(content)
    print("Updated")

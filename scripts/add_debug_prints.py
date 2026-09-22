content = open("search_core.py", encoding="utf-8").read()
old = """        final_scores = final_scores * boost

        top_indices = np.argsort(final_scores)[::-1][:top_k]"""
new = """        final_scores = final_scores * boost

        if ipc_target_section is not None:
            for i, record in enumerate(self.records):
                if "bharatiya nyaya sanhita" in str(record.get("act_name") or "").lower() and str(record.get("section_number") or "") == ipc_target_section:
                    print(f"DEBUG: target record boost={boost[i]}, final_score={final_scores[i]}")
            print(f"DEBUG: max final_score overall={final_scores.max()}, at index={final_scores.argmax()}")
            top_idx = final_scores.argmax()
            print(f"DEBUG: winning record = {self.records[top_idx].get(\\"act_name\\")} S{self.records[top_idx].get(\\"section_number\\")}")

        top_indices = np.argsort(final_scores)[::-1][:top_k]"""
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("search_core.py", "w", encoding="utf-8").write(content)
    print("Added debug prints")

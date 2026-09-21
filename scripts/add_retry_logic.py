content = open("rag_core.py", encoding="utf-8").read()

old_imports = """import os
import re
from dotenv import load_dotenv
from groq import Groq"""
new_imports = """import os
import re
import time
import groq
from dotenv import load_dotenv
from groq import Groq"""
count1 = content.count(old_imports)
print(f"Import block found: {count1}")
if count1 == 1:
    content = content.replace(old_imports, new_imports)

old_call = """    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=2500,
    )

    return response.choices[0].message.content"""

new_call = """    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=2500,
            )
            return response.choices[0].message.content
        except groq.RateLimitError:
            raise
        except Exception:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise"""

count2 = content.count(old_call)
print(f"API call block found: {count2}")
if count2 == 1:
    content = content.replace(old_call, new_call)

open("rag_core.py", "w", encoding="utf-8").write(content)
print("Done")

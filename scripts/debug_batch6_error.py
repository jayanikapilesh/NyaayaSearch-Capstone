from groq import Groq
import os
from dotenv import load_dotenv
load_dotenv()
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

try:
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {"role": "system", "content": "You generate plain-language questions. Return ONLY valid JSON with EXACTLY 2 questions, nothing more: {\"questions\": [\"q1\", \"q2\"]}"},
            {"role": "user", "content": "Act: Karnataka Rent Act, 1999\nSection title: Rent payable.\nSection text: Rent payable under a lease..."},
        ],
        temperature=0.5,
        max_tokens=600,
    )
    print("RAW RESPONSE:")
    print(repr(response.choices[0].message.content))
except Exception as e:
    print(f"ERROR TYPE: {type(e).__name__}")
    print(f"ERROR MESSAGE: {e}")

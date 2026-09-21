from search_core import SearchEngine
from rag_core import translate_to_english

engine = SearchEngine()

multilingual_queries = [
    ("Hindi", "मकान मालिक मेरी जमा राशि वापस नहीं कर रहा है", "Karnataka Rent Act, 1999", "17"),
    ("Hindi", "बिना वारंट के गिरफ्तारी", "Bharatiya Nagarik Suraksha Sanhita, 2023", "35"),
    ("Hindi", "उपभोक्ता शिकायत कैसे दर्ज करें", "Consumer Protection Act, 2019", "35"),
    ("Kannada", "ಮನೆ ಮಾಲೀಕ ಠೇವಣಿ ಹಿಂತಿರುಗಿಸುತ್ತಿಲ್ಲ", "Karnataka Rent Act, 1999", "17"),
    ("Kannada", "ವಾರಂಟ್ ಇಲ್ಲದೆ ಬಂಧನ", "Bharatiya Nagarik Suraksha Sanhita, 2023", "35"),
    ("Hindi", "बाल विवाह के लिए अपहरण की सजा क्या है", "Bharatiya Nyaya Sanhita, 2023", "87"),
    ("Kannada", "ನಕಲಿ ಕರೆನ್ಸಿ ನೋಟುಗಳಿಗೆ ಶಿಕ್ಷೆ ಏನು", "Bharatiya Nyaya Sanhita, 2023", "178"),
    ("Kannada", "RTI ಅರ್ಜಿ ಹೇಗೆ ಸಲ್ಲಿಸುವುದು", "Right to Information Act, 2005", "6"),
    ("Hindi", "यदि मैं अदालत में उपस्थित नहीं होता तो क्या होगा", "Bharatiya Nagarik Suraksha Sanhita, 2023", "84"),
]

hits = 0
print(f"{'Lang':<8} {'Query':<45} {'Translated':<55} {'Hit?'}")
print("-" * 120)

for lang, query, expected_act, expected_section in multilingual_queries:
    try:
        translated = translate_to_english(query)
    except Exception as e:
        translated = f"[TRANSLATION FAILED: {e}]"
        print(f"{lang:<8} {query:<45} {translated}")
        continue

    results = engine.search(translated, top_k=5)
    hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
    if hit:
        hits += 1
    print(f"{lang:<8} {query:<45} {translated:<55} {'YES' if hit else 'NO'}")

print("-" * 120)
print(f"\nMultilingual test: {hits}/{len(multilingual_queries)} correct")

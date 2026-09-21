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
    ("Hindi", "दस साल से कम उम्र के बच्चे का अपहरण करके उससे चोरी करने की सजा क्या है", "Bharatiya Nyaya Sanhita, 2023", "97"),
    ("Hindi", "अनुबंध में एजेंट के रूप में कौन कार्य कर सकता है", "Indian Contract Act, 1872", "184"),
    ("Hindi", "केंद्रीय उपभोक्ता संरक्षण प्राधिकरण क्या है", "Consumer Protection Act, 2019", "10"),
    ("Hindi", "झूठा दस्तावेज़ बनाना अपराध है क्या", "Bharatiya Nyaya Sanhita, 2023", "335"),
    ("Hindi", "क्या लाइसेंसिंग प्राधिकरण मेरा ड्राइविंग लाइसेंस रद्द कर सकता है", "Motor Vehicles Act, 1988", "19"),
    ("Hindi", "क्या घरेलू हिंसा कानून परामर्श का प्रावधान करता है", "Protection of Women from Domestic Violence Act, 2005", "14"),
    ("Hindi", "धोखाधड़ी की कानूनी परिभाषा क्या है", "Bharatiya Nyaya Sanhita, 2023", "318"),
    ("Hindi", "दंगा करने की सजा क्या है", "Bharatiya Nyaya Sanhita, 2023", "191"),
    ("Hindi", "जमानतदार की जिम्मेदारी अनुबंध कानून के तहत क्या है", "Indian Contract Act, 1872", "128"),
    ("Hindi", "किराया न देने पर पट्टा जब्त होने पर राहत मिल सकती है क्या", "Transfer of Property Act, 1882", "114"),
    ("Hindi", "दंगे की साजिश की सजा क्या है", "Bharatiya Nyaya Sanhita, 2023", "148"),
    ("Hindi", "क्या मैं मुचलके के बजाय पैसे जमा कर सकता हूं", "Bharatiya Nagarik Suraksha Sanhita, 2023", "490"),
    ("Hindi", "बच्चे की खरीद-फरोख्त की सजा क्या है", "Bharatiya Nyaya Sanhita, 2023", "96"),
    ("Hindi", "सरकारी कर्मचारी पर हमला करने की सजा क्या है", "Bharatiya Nyaya Sanhita, 2023", "132"),
    ("Hindi", "आरटीआई अधिनियम के तहत नियम बनाने की शक्ति किसके पास है", "Right to Information Act, 2005", "28"),
    ("Hindi", "क्या प्रमाणन प्राधिकरण को मुझे सूचित करना होगा अगर मेरा डिजिटल हस्ताक्षर प्रमाणपत्र रद्द हो जाता है", "Information Technology Act, 2000", "39"),
    ("Kannada", "ಕ್ರಿಯಾತ್ಮಕ ಹಕ್ಕಿನ ವರ್ಗಾವಣೆದಾರನ ಹೊಣೆಗಾರಿಕೆ ಏನು", "Transfer of Property Act, 1882", "132"),
    ("Kannada", "ಗರ್ಭಪಾತ ಉಂಟುಮಾಡುವ ಉದ್ದೇಶದಿಂದ ಸಾವು ಸಂಭವಿಸಿದರೆ ಶಿಕ್ಷೆ ಏನು", "Bharatiya Nyaya Sanhita, 2023", "90"),
    ("Kannada", "ಸೈನಿಕನನ್ನು ಅಸಹಕಾರಕ್ಕೆ ಪ್ರೇರೇಪಿಸುವ ಶಿಕ್ಷೆ ಏನು", "Bharatiya Nyaya Sanhita, 2023", "166"),
    ("Kannada", "ಸುಳ್ಳು ಡಿಕ್ರಿ ಪಡೆಯುವ ಶಿಕ್ಷೆ ಏನು", "Bharatiya Nyaya Sanhita, 2023", "247"),
    ("Kannada", "ಗ್ರಾಹಕ ದೂರು ಹೇಗೆ ಸಲ್ಲಿಸುವುದು", "Consumer Protection Act, 2019", "35"),
    ("Kannada", "ಬಾಲ್ಯ ವಿವಾಹಕ್ಕಾಗಿ ಅಪಹರಣದ ಶಿಕ್ಷೆ ಏನು", "Bharatiya Nyaya Sanhita, 2023", "87"),
    ("Kannada", "ಠೇವಣಿ ಹಿಂತಿರುಗಿಸದಿದ್ದರೆ ಏನು ಮಾಡಬೇಕು", "Karnataka Rent Act, 1999", "17"),
    ("Kannada", "ನಾನು ನ್ಯಾಯಾಲಯದಲ್ಲಿ ಹಾಜರಾಗದಿದ್ದರೆ ಏನಾಗುತ್ತದೆ", "Bharatiya Nagarik Suraksha Sanhita, 2023", "84"),
    ("Kannada", "ಮೋಸ ಮಾಡುವುದು ಎಂದರೆ ಏನು", "Bharatiya Nyaya Sanhita, 2023", "318"),
    ("Kannada", "ಗಲಭೆ ಮಾಡುವ ಶಿಕ್ಷೆ ಏನು", "Bharatiya Nyaya Sanhita, 2023", "191"),
    ("Kannada", "ಪರವಾನಗಿ ಪ್ರಾಧಿಕಾರವು ನನ್ನ ಚಾಲನಾ ಪರವಾನಗಿಯನ್ನು ರದ್ದುಗೊಳಿಸಬಹುದೇ", "Motor Vehicles Act, 1988", "19"),
    ("Kannada", "ಮಗುವಿನ ಖರೀದಿ-ಮಾರಾಟದ ಶಿಕ್ಷೆ ಏನು", "Bharatiya Nyaya Sanhita, 2023", "96"),
    ("Kannada", "ಸರ್ಕಾರಿ ನೌಕರನ ಮೇಲೆ ಹಲ್ಲೆ ಮಾಡುವ ಶಿಕ್ಷೆ ಏನು", "Bharatiya Nyaya Sanhita, 2023", "132"),
    ("Kannada", "ಈ ಕಾನೂನಿನಡಿ ಸಮಾಲೋಚನೆ ಇದೆಯೇ", "Protection of Women from Domestic Violence Act, 2005", "14"),
    ("Kannada", "ಒಪ್ಪಂದದಲ್ಲಿ ಏಜೆಂಟ್ ಆಗಿ ಯಾರು ಕಾರ್ಯನಿರ್ವಹಿಸಬಹುದು", "Indian Contract Act, 1872", "184"),
]

hits = 0
failures = []
hindi_n = sum(1 for l, q, a, s in multilingual_queries if l == "Hindi")
kannada_n = sum(1 for l, q, a, s in multilingual_queries if l == "Kannada")
hindi_hits = 0
kannada_hits = 0

print(f"Total multilingual queries: {len(multilingual_queries)}")
print(f"{'Lang':<8} {'Translated':<55} {'Hit?'}")
print("-" * 80)

for lang, query, expected_act, expected_section in multilingual_queries:
    try:
        translated = translate_to_english(query)
    except Exception as e:
        translated = f"[FAILED: {e}]"
        print(f"{lang:<8} {translated}")
        failures.append((lang, query))
        continue

    results = engine.search(translated, top_k=5)
    hit = any(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section for r in results)
    if hit:
        hits += 1
        if lang == "Hindi":
            hindi_hits += 1
        else:
            kannada_hits += 1
    else:
        failures.append((lang, query))
    print(f"{lang:<8} {translated:<55} {'YES' if hit else 'NO'}")

n = len(multilingual_queries)
print("-" * 80)
print(f"\nOverall multilingual: {hits}/{n} = {hits/n:.4f}")
print(f"\nPER-LANGUAGE BREAKDOWN:")
print(f"English (frozen 148-query set): Recall@5 = 0.7770")
print(f"Hindi: {hindi_hits}/{hindi_n} = {hindi_hits/hindi_n:.4f}")
print(f"Kannada: {kannada_hits}/{kannada_n} = {kannada_hits/kannada_n:.4f}")
print(f"\nFailures ({len(failures)}):")
for lang, q in failures:
    print(f"  [{lang}] {q[:50]}")

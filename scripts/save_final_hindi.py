paired_multilingual = [
    ("Hindi", "किसी को मारने की कोशिश करना लेकिन असफल होना, इसकी सजा क्या है", "Bharatiya Nyaya Sanhita, 2023", "109"),
    ("Hindi", "जानबूझकर किसी को गंभीर चोट पहुंचाने की सजा क्या है", "Bharatiya Nyaya Sanhita, 2023", "117"),
    ("Hindi", "क्या झूठे विज्ञापन के लिए कंपनी को सजा हो सकती है", "Consumer Protection Act, 2019", "89"),
    ("Hindi", "क्या दुकान को खराब सामान बेचने के लिए जिम्मेदार ठहराया जा सकता है", "Consumer Protection Act, 2019", "86"),
    ("Hindi", "क्या निर्माता पर खराब उत्पाद के लिए मुकदमा किया जा सकता है", "Consumer Protection Act, 2019", "84"),
    ("Hindi", "क्या पुलिस को मुझे बताना होगा कि मुझे गिरफ्तार क्यों किया जा रहा है", "Bharatiya Nagarik Suraksha Sanhita, 2023", "47"),
    ("Hindi", "क्या घरेलू हिंसा पीड़िता को आर्थिक मुआवजा मिल सकता है", "Protection of Women from Domestic Violence Act, 2005", "20"),
    ("Hindi", "क्या घरेलू हिंसा का मामला बच्चे की कस्टडी को प्रभावित कर सकता है", "Protection of Women from Domestic Violence Act, 2005", "21"),
    ("Hindi", "क्या मकान खाली करते समय मुझे इसे खाली सौंपना होगा", "Karnataka Rent Act, 1999", "41"),
    ("Hindi", "क्या अदालत किराए के विवादों को बिना मुकदमे के सुलझाने की कोशिश करती है", "Karnataka Rent Act, 1999", "44"),
    ("Hindi", "क्या मैं कर्ज चुकाने के बाद अपनी गिरवी रखी संपत्ति वापस पा सकता हूं", "Transfer of Property Act, 1882", "62"),
    ("Hindi", "अदालत कब निषेधाज्ञा देने से इनकार करेगी", "Specific Relief Act, 1963", "41"),
    ("Hindi", "क्या मैं किसी को व्यक्तिगत सेवा अनुबंध पूरा करने के लिए मजबूर कर सकता हूं", "Specific Relief Act, 1963", "14"),
    ("Hindi", "मैं कानूनी रूप से अपनी संपत्ति किसी से कैसे वापस लूं जो उस पर कब्जा किए हुए है", "Specific Relief Act, 1963", "5"),
    ("Hindi", "क्या मैं समय सीमा चूकने के बाद भी अपनी गिरवी रखी चीज वापस पा सकता हूं", "Indian Contract Act, 1872", "177"),
    ("Hindi", "क्या मेरा एजेंट मुझसे पूछे बिना मेरा काम करने के लिए किसी और को नियुक्त कर सकता है", "Indian Contract Act, 1872", "190"),
    ("Hindi", "अगर दोनों पक्ष अनुबंध बदलने पर सहमत हो जाएं तो क्या होता है", "Indian Contract Act, 1872", "62"),
    ("Hindi", "क्या किसी को धोखा देने के लिए नकली डिजिटल प्रमाणपत्र बनाना गैरकानूनी है", "Information Technology Act, 2000", "74"),
    ("Hindi", "क्या मैं साइबर ट्रिब्यूनल के फैसले को हाईकोर्ट में चुनौती दे सकता हूं", "Information Technology Act, 2000", "62"),
    ("Hindi", "क्या सरकार मेरे इंटरनेट संचार की निगरानी कर सकती है", "Information Technology Act, 2000", "69"),
    ("Hindi", "ट्रेन को तोड़फोड़ करने की सजा क्या है", "Bharatiya Nyaya Sanhita, 2023", "327"),
    ("Hindi", "क्या जानबूझकर खतरनाक बीमारी फैलाना अपराध है", "Bharatiya Nyaya Sanhita, 2023", "272"),
    ("Hindi", "किसी की जान को लापरवाही से खतरे में डालने की सजा क्या है", "Bharatiya Nyaya Sanhita, 2023", "125"),
    ("Hindi", "क्या किसी को अदालत का समन मिलने से रोकना गैरकानूनी है", "Bharatiya Nyaya Sanhita, 2023", "207"),
    ("Hindi", "अदालत आधिकारिक रूप से समन कैसे भेजती है", "Bharatiya Nagarik Suraksha Sanhita, 2023", "64"),
    ("Hindi", "अदालत द्वारा अपराध का संज्ञान लेने का क्या मतलब है", "Bharatiya Nagarik Suraksha Sanhita, 2023", "221"),
    ("Hindi", "क्या मजिस्ट्रेट संदिग्ध मौतों की जांच करता है", "Bharatiya Nagarik Suraksha Sanhita, 2023", "196"),
    ("Hindi", "क्या मुझे गिरफ्तारी वारंट निष्पादित करने वाले व्यक्ति की मदद करनी होगी", "Bharatiya Nagarik Suraksha Sanhita, 2023", "32"),
    ("Hindi", "क्या मजिस्ट्रेट कार्रवाई से पहले शिकायत की सच्चाई जांचता है", "Bharatiya Nagarik Suraksha Sanhita, 2023", "135"),
    ("Hindi", "क्या मेरी बीमा कंपनी सीधे मेरे साथ दावा निपटा सकती है", "Motor Vehicles Act, 1988", "153"),
]

import json
with open("../data/eval/final_test_hindi.json", "w", encoding="utf-8") as f:
    json.dump(paired_multilingual, f, indent=2, ensure_ascii=False)
print(f"Saved {len(paired_multilingual)} Hindi queries")

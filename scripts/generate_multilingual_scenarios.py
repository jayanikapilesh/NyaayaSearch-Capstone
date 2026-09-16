import json

input_file = "data/scenarios/processed/scenario_candidates.json"
output_file = "data/scenarios/processed/scenario_multilingual.json"

with open(input_file, "r", encoding="utf-8") as file:
    candidates = json.load(file)

# Fixed translations for the scenario/question patterns.
# This avoids relying on machine translation that could change legal meaning.
translations = {
    "I bought a product for personal use and the seller is refusing to resolve my complaint.": {
        "Hindi": "मैंने निजी उपयोग के लिए एक उत्पाद खरीदा है और विक्रेता मेरी शिकायत का समाधान करने से इनकार कर रहा है।",
        "Kannada": "ನಾನು ವೈಯಕ್ತಿಕ ಬಳಕೆಗಾಗಿ ಒಂದು ಉತ್ಪನ್ನವನ್ನು ಖರೀದಿಸಿದ್ದೇನೆ ಮತ್ತು ಮಾರಾಟಗಾರನು ನನ್ನ ದೂರನ್ನು ಪರಿಹರಿಸಲು ನಿರಾಕರಿಸುತ್ತಿದ್ದಾನೆ।"
    },
    "I paid for a service but the service provider did not provide what was promised.": {
        "Hindi": "मैंने एक सेवा के लिए भुगतान किया, लेकिन सेवा प्रदाता ने वादा की गई सेवा नहीं दी।",
        "Kannada": "ನಾನು ಒಂದು ಸೇವೆಗೆ ಹಣ ಪಾವತಿಸಿದ್ದೇನೆ, ಆದರೆ ಸೇವಾ ಪೂರೈಕೆದಾರರು ಭರವಸೆ ನೀಡಿದ ಸೇವೆಯನ್ನು ನೀಡಲಿಲ್ಲ।"
    },
    "A business has treated me unfairly after I purchased a product or service.": {
        "Hindi": "किसी उत्पाद या सेवा को खरीदने के बाद एक व्यवसाय ने मेरे साथ अनुचित व्यवहार किया।",
        "Kannada": "ಒಂದು ಉತ್ಪನ್ನ ಅಥವಾ ಸೇವೆಯನ್ನು ಖರೀದಿಸಿದ ನಂತರ ಒಂದು ವ್ಯಾಪಾರ ಸಂಸ್ಥೆಯು ನನ್ನೊಂದಿಗೆ ಅನ್ಯಾಯವಾಗಿ ವರ್ತಿಸಿದೆ।"
    },
    "A company advertised a product with claims that turned out to be false.": {
        "Hindi": "एक कंपनी ने किसी उत्पाद का ऐसे दावों के साथ विज्ञापन किया जो बाद में झूठे निकले।",
        "Kannada": "ಒಂದು ಕಂಪನಿಯು ನಂತರ ಸುಳ್ಳು ಎಂದು ತಿಳಿದುಬಂದ ಹೇಳಿಕೆಗಳೊಂದಿಗೆ ಉತ್ಪನ್ನದ ಜಾಹೀರಾತು ಮಾಡಿದೆ।"
    },
    "An advertisement promised a benefit that the product did not actually provide.": {
        "Hindi": "एक विज्ञापन में ऐसे लाभ का वादा किया गया जो उत्पाद ने वास्तव में प्रदान नहीं किया।",
        "Kannada": "ಒಂದು ಜಾಹೀರಾತಿನಲ್ಲಿ ಉತ್ಪನ್ನವು ವಾಸ್ತವವಾಗಿ ನೀಡದ ಪ್ರಯೋಜನವನ್ನು ನೀಡುವುದಾಗಿ ಭರವಸೆ ನೀಡಲಾಗಿತ್ತು।"
    },
    "A seller used a misleading advertisement to convince me to buy a product.": {
        "Hindi": "एक विक्रेता ने मुझे उत्पाद खरीदने के लिए भ्रामक विज्ञापन का इस्तेमाल किया।",
        "Kannada": "ಒಬ್ಬ ಮಾರಾಟಗಾರನು ನನಗೆ ಉತ್ಪನ್ನವನ್ನು ಖರೀದಿಸುವಂತೆ ಮಾಡಲು ದಾರಿ ತಪ್ಪಿಸುವ ಜಾಹೀರಾತನ್ನು ಬಳಸಿದನು।"
    },
    "The product I purchased has a defect that the seller is refusing to fix.": {
        "Hindi": "मेरे द्वारा खरीदे गए उत्पाद में खराबी है और विक्रेता उसे ठीक करने से इनकार कर रहा है।",
        "Kannada": "ನಾನು ಖರೀದಿಸಿದ ಉತ್ಪನ್ನದಲ್ಲಿ ದೋಷವಿದ್ದು, ಮಾರಾಟಗಾರನು ಅದನ್ನು ಸರಿಪಡಿಸಲು ನಿರಾಕರಿಸುತ್ತಿದ್ದಾನೆ।"
    },
    "A service I paid for was deficient and the provider refuses to correct the problem.": {
        "Hindi": "जिस सेवा के लिए मैंने भुगतान किया वह दोषपूर्ण थी और सेवा प्रदाता समस्या को ठीक करने से इनकार कर रहा है।",
        "Kannada": "ನಾನು ಹಣ ಪಾವತಿಸಿದ ಸೇವೆಯಲ್ಲಿ ಕೊರತೆಯಿದ್ದು, ಸೇವಾ ಪೂರೈಕೆದಾರರು ಸಮಸ್ಯೆಯನ್ನು ಸರಿಪಡಿಸಲು ನಿರಾಕರಿಸುತ್ತಿದ್ದಾರೆ।"
    },
    "I received a defective product and the seller is refusing a refund or replacement.": {
        "Hindi": "मुझे खराब उत्पाद मिला है और विक्रेता धनवापसी या प्रतिस्थापन से इनकार कर रहा है।",
        "Kannada": "ನನಗೆ ದೋಷಪೂರಿತ ಉತ್ಪನ್ನ ದೊರೆತಿದ್ದು, ಮಾರಾಟಗಾರನು ಹಣ ಮರುಪಾವತಿ ಅಥವಾ ಬದಲಿಯನ್ನು ನೀಡಲು ನಿರಾಕರಿಸುತ್ತಿದ್ದಾನೆ।"
    },
    "I want to complain about a problem with a product or service.": {
        "Hindi": "मैं किसी उत्पाद या सेवा से जुड़ी समस्या के बारे में शिकायत करना चाहता हूँ।",
        "Kannada": "ನಾನು ಉತ್ಪನ್ನ ಅಥವಾ ಸೇವೆಗೆ ಸಂಬಂಧಿಸಿದ ಸಮಸ್ಯೆಯ ಬಗ್ಗೆ ದೂರು ನೀಡಲು ಬಯಸುತ್ತೇನೆ।"
    },
    "My complaint about a product or service has not been resolved.": {
        "Hindi": "किसी उत्पाद या सेवा के बारे में मेरी शिकायत का समाधान नहीं हुआ है।",
        "Kannada": "ಉತ್ಪನ್ನ ಅಥವಾ ಸೇವೆಯ ಬಗ್ಗೆ ನಾನು ನೀಡಿದ ದೂರನ್ನು ಪರಿಹರಿಸಲಾಗಿಲ್ಲ।"
    },
    "I need to know where I can submit a consumer complaint.": {
        "Hindi": "मुझे जानना है कि मैं उपभोक्ता शिकायत कहाँ दर्ज कर सकता हूँ।",
        "Kannada": "ನಾನು ಗ್ರಾಹಕರ ದೂರನ್ನು ಎಲ್ಲಿ ಸಲ್ಲಿಸಬಹುದು ಎಂಬುದನ್ನು ತಿಳಿದುಕೊಳ್ಳಬೇಕು।"
    },
    "I am involved in a dispute about ownership or possession of property.": {
        "Hindi": "मैं संपत्ति के स्वामित्व या कब्जे से जुड़े विवाद में शामिल हूँ।",
        "Kannada": "ನಾನು ಆಸ್ತಿಯ ಮಾಲೀಕತ್ವ ಅಥವಾ ಸ್ವಾಧೀನಕ್ಕೆ ಸಂಬಂಧಿಸಿದ ವಿವಾದದಲ್ಲಿ ಇದ್ದೇನೆ।"
    },
    "There is a disagreement about the transfer or sale of a property.": {
        "Hindi": "संपत्ति के हस्तांतरण या बिक्री को लेकर विवाद है।",
        "Kannada": "ಆಸ್ತಿಯ ವರ್ಗಾವಣೆ ಅಥವಾ ಮಾರಾಟದ ಬಗ್ಗೆ ವಿವಾದವಿದೆ।"
    },
    "I am facing a dispute with a landlord or tenant about a property.": {
        "Hindi": "मुझे संपत्ति को लेकर मकान मालिक या किरायेदार के साथ विवाद का सामना करना पड़ रहा है।",
        "Kannada": "ಆಸ್ತಿಗೆ ಸಂಬಂಧಿಸಿದಂತೆ ನಾನು ಮನೆ ಮಾಲೀಕರು ಅಥವಾ ಬಾಡಿಗೆದಾರರೊಂದಿಗೆ ವಿವಾದವನ್ನು ಎದುರಿಸುತ್ತಿದ್ದೇನೆ।"
    },
    "I have been accused of an offence and want to understand my legal position.": {
        "Hindi": "मुझ पर किसी अपराध का आरोप लगाया गया है और मैं अपनी कानूनी स्थिति समझना चाहता हूँ।",
        "Kannada": "ನನ್ನ ಮೇಲೆ ಅಪರಾಧದ ಆರೋಪವಿದ್ದು, ನನ್ನ ಕಾನೂನು ಸ್ಥಿತಿಯನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ಬಯಸುತ್ತೇನೆ।"
    },
    "Someone has committed an offence against me and I want to know what I can do.": {
        "Hindi": "किसी व्यक्ति ने मेरे खिलाफ अपराध किया है और मैं जानना चाहता हूँ कि मैं क्या कर सकता हूँ।",
        "Kannada": "ಯಾರೋ ನನ್ನ ವಿರುದ್ಧ ಅಪರಾಧ ಮಾಡಿದ್ದಾರೆ ಮತ್ತು ನಾನು ಏನು ಮಾಡಬಹುದು ಎಂಬುದನ್ನು ತಿಳಿದುಕೊಳ್ಳಲು ಬಯಸುತ್ತೇನೆ।"
    },
    "I want to understand the legal consequences of this criminal conduct.": {
        "Hindi": "मैं इस आपराधिक कृत्य के कानूनी परिणामों को समझना चाहता हूँ।",
        "Kannada": "ಈ ಅಪರಾಧ ಕೃತ್ಯದ ಕಾನೂನು ಪರಿಣಾಮಗಳನ್ನು ನಾನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು ಬಯಸುತ್ತೇನೆ।"
    },
    "Someone attacked me and I acted to protect myself.": {
        "Hindi": "किसी ने मुझ पर हमला किया और मैंने अपनी रक्षा के लिए कार्रवाई की।",
        "Kannada": "ಯಾರೋ ನನ್ನ ಮೇಲೆ ದಾಳಿ ಮಾಡಿದರು ಮತ್ತು ನಾನು ನನ್ನನ್ನು ರಕ್ಷಿಸಿಕೊಳ್ಳಲು ಕ್ರಮ ಕೈಗೊಂಡೆ।"
    },
    "I used force to protect myself from an immediate attack.": {
        "Hindi": "मैंने तत्काल हमले से खुद को बचाने के लिए बल का इस्तेमाल किया।",
        "Kannada": "ತಕ್ಷಣದ ದಾಳಿಯಿಂದ ನನ್ನನ್ನು ರಕ್ಷಿಸಿಕೊಳ್ಳಲು ನಾನು ಬಲವನ್ನು ಬಳಸಿದೆ।"
    },
    "I acted to protect my property when someone tried to interfere with it.": {
        "Hindi": "जब किसी ने मेरी संपत्ति में हस्तक्षेप करने की कोशिश की तो मैंने उसकी रक्षा के लिए कार्रवाई की।",
        "Kannada": "ಯಾರೋ ನನ್ನ ಆಸ್ತಿಯಲ್ಲಿ ಹಸ್ತಕ್ಷೇಪ ಮಾಡಲು ಪ್ರಯತ್ನಿಸಿದಾಗ ಅದನ್ನು ರಕ್ಷಿಸಲು ನಾನು ಕ್ರಮ ಕೈಗೊಂಡೆ।"
    }
}

question_translations = {
    "What does the law say in this situation?": {
        "Hindi": "इस स्थिति में कानून क्या कहता है?",
        "Kannada": "ಈ ಪರಿಸ್ಥಿತಿಯಲ್ಲಿ ಕಾನೂನು ಏನು ಹೇಳುತ್ತದೆ?"
    },
    "What are my legal rights in this situation?": {
        "Hindi": "इस स्थिति में मेरे कानूनी अधिकार क्या हैं?",
        "Kannada": "ಈ ಪರಿಸ್ಥಿತಿಯಲ್ಲಿ ನನ್ನ ಕಾನೂನು ಹಕ್ಕುಗಳು ಯಾವುವು?"
    },
    "What should I do next?": {
        "Hindi": "मुझे आगे क्या करना चाहिए?",
        "Kannada": "ನಾನು ಮುಂದೆ ಏನು ಮಾಡಬೇಕು?"
    },
    "What legal remedy may be available to me?": {
        "Hindi": "मेरे लिए कौन सा कानूनी उपाय उपलब्ध हो सकता है?",
        "Kannada": "ನನಗೆ ಯಾವ ಕಾನೂನು ಪರಿಹಾರ ಲಭ್ಯವಾಗಬಹುದು?"
    },
    "Which authority or court should I approach?": {
        "Hindi": "मुझे किस प्राधिकरण या न्यायालय से संपर्क करना चाहिए?",
        "Kannada": "ನಾನು ಯಾವ ಪ್ರಾಧಿಕಾರ ಅಥವಾ ನ್ಯಾಯಾಲಯವನ್ನು ಸಂಪರ್ಕಿಸಬೇಕು?"
    }
}

output = []

for item in candidates:
    english_query = item["user_query"]

    matched_scenario = None
    matched_question = None

    for scenario, translated in translations.items():
        if english_query.startswith(scenario):
            matched_scenario = scenario
            remainder = english_query[len(scenario):].strip()
            matched_question = remainder
            break

    if not matched_scenario or matched_question not in question_translations:
        continue

    for language in ["English", "Hindi", "Kannada"]:
        if language == "English":
            query = english_query
        else:
            query = (
                translations[matched_scenario][language]
                + " "
                + question_translations[matched_question][language]
            )

        record = dict(item)
        record["language"] = language
        record["user_query"] = query
        record["scenario"] = (
            matched_scenario
            if language == "English"
            else translations[matched_scenario][language]
        )

        output.append(record)

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(output, file, indent=2, ensure_ascii=False)

print("Multilingual scenarios generated successfully!")
print("English candidates:", len(candidates))
print("Final multilingual records:", len(output))
print("Languages: English, Hindi, Kannada")
print("Saved to:", output_file)
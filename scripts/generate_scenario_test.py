import csv
import json

input_file = "data/scenarios/processed/scenario_source_sections.csv"
output_file = "data/scenarios/processed/scenario_test_candidates.json"

with open(input_file, "r", encoding="utf-8-sig") as file:
    sections = list(csv.DictReader(file))

# Multilingual test scenarios grounded in Dataset 1.
test_scenarios = [
    {
        "section_number": "2",
        "scenario": "A customer wants to know whether they qualify as a consumer under the Consumer Protection Act.",
        "queries": {
            "English": "I bought a product for personal use. Am I considered a consumer under the law?",
            "Hindi": "मैंने अपने निजी उपयोग के लिए एक सामान खरीदा है। क्या कानून के अनुसार मैं उपभोक्ता माना जाता हूँ?",
            "Kannada": "ನನ್ನ ವೈಯಕ್ತಿಕ ಬಳಕೆಗಾಗಿ ನಾನು ಒಂದು ವಸ್ತುವನ್ನು ಖರೀದಿಸಿದ್ದೇನೆ. ಕಾನೂನಿನ ಪ್ರಕಾರ ನಾನು ಗ್ರಾಹಕನೆಂದು ಪರಿಗಣಿಸಲ್ಪಡುತ್ತೇನೆಯೇ?"
        }
    },
    {
        "section_number": "10",
        "scenario": "A consumer wants to know about the authority responsible for protecting consumer interests.",
        "queries": {
            "English": "Which authority is responsible for protecting consumers from unfair practices?",
            "Hindi": "उपभोक्ताओं को अनुचित व्यापार प्रथाओं से बचाने के लिए कौन सा प्राधिकरण जिम्मेदार है?",
            "Kannada": "ಅನ್ಯಾಯವಾದ ವ್ಯಾಪಾರ ಪದ್ಧತಿಗಳಿಂದ ಗ್ರಾಹಕರನ್ನು ರಕ್ಷಿಸಲು ಯಾವ ಪ್ರಾಧಿಕಾರ ಜವಾಬ್ದಾರಿಯಾಗಿದೆ?"
        }
    },
    {
        "section_number": "17",
        "scenario": "A consumer wants to know where a complaint about a consumer-related issue can be made.",
        "queries": {
            "English": "Where can I make a complaint about a problem with a product or service?",
            "Hindi": "किसी उत्पाद या सेवा से जुड़ी समस्या की शिकायत मैं कहाँ कर सकता हूँ?",
            "Kannada": "ಉತ್ಪನ್ನ ಅಥವಾ ಸೇವೆಗೆ ಸಂಬಂಧಿಸಿದ ಸಮಸ್ಯೆಯ ಬಗ್ಗೆ ನಾನು ಎಲ್ಲಿ ದೂರು ನೀಡಬಹುದು?"
        }
    },
    {
        "section_number": "20",
        "scenario": "A consumer is concerned about unsafe goods being sold in the market.",
        "queries": {
            "English": "What can the consumer authority do if unsafe goods are being sold?",
            "Hindi": "अगर बाजार में असुरक्षित सामान बेचा जा रहा है तो उपभोक्ता प्राधिकरण क्या कर सकता है?",
            "Kannada": "ಮಾರುಕಟ್ಟೆಯಲ್ಲಿ ಅಸುರಕ್ಷಿತ ವಸ್ತುಗಳನ್ನು ಮಾರಾಟ ಮಾಡುತ್ತಿದ್ದರೆ ಗ್ರಾಹಕ ಪ್ರಾಧಿಕಾರ ಏನು ಮಾಡಬಹುದು?"
        }
    },
    {
        "section_number": "21",
        "scenario": "A consumer sees an advertisement making a false or misleading claim about a product.",
        "queries": {
            "English": "What can be done about a false or misleading advertisement for a product?",
            "Hindi": "किसी उत्पाद के झूठे या भ्रामक विज्ञापन के खिलाफ क्या किया जा सकता है?",
            "Kannada": "ಉತ್ಪನ್ನದ ಬಗ್ಗೆ ಸುಳ್ಳು ಅಥವಾ ದಾರಿ ತಪ್ಪಿಸುವ ಜಾಹೀರಾತಿನ ವಿರುದ್ಧ ಏನು ಮಾಡಬಹುದು?"
        }
    }
]

section_map = {
    str(section["section_number"]): section
    for section in sections
    if section["act_name"] == "Consumer Protection Act, 2019"
}

candidates = []

scenario_id = 1

for item in test_scenarios:
    section = section_map.get(item["section_number"])

    if not section:
        raise ValueError(
            f"Section {item['section_number']} was not found in Dataset 1"
        )

    for language, user_query in item["queries"].items():
        candidates.append({
            "scenario_id": f"SC-{scenario_id:03d}",
            "act_name": section["act_name"],
            "section_number": section["section_number"],
            "section_title": section["section_title"],
            "legal_text": section["legal_text"],
            "scenario": item["scenario"],
            "user_query": user_query,
            "language": language
        })

        scenario_id += 1

with open(output_file, "w", encoding="utf-8") as file:
    json.dump(candidates, file, indent=2, ensure_ascii=False)

print("Multilingual test scenarios generated:", len(candidates))
print("Languages: English, Hindi, Kannada")
print("All scenarios mapped to Dataset 1 sections.")
print("Saved to:", output_file)
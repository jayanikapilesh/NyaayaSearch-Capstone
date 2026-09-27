export const BNS_CONTENT = {
  en: {
    heading: "BNS Decoder",
    intro: "Enter a Bharatiya Nyaya Sanhita (BNS) section number to see what it says, explained in plain language.",
    srLabel: "BNS section number",
    placeholder: "e.g. 103",
    buttonDecode: "Decode Section",
    buttonLoading: "Looking up...",
    sectionLabel: "Section",
    originalText: "Original text:",
  },

  hi: {
    heading: "बीएनएस डिकोडर",
    intro: "भारतीय न्याय संहिता (BNS) की धारा संख्या दर्ज करें और देखें कि वह सरल भाषा में क्या कहती है।",
    srLabel: "बीएनएस धारा संख्या",
    placeholder: "जैसे 103",
    buttonDecode: "धारा समझें",
    buttonLoading: "खोज रहे हैं...",
    sectionLabel: "धारा",
    originalText: "मूल पाठ:",
  },

  kn: {
    heading: "ಬಿಎನ್‌ಎಸ್ ಡಿಕೋಡರ್",
    intro: "ಭಾರತೀಯ ನ್ಯಾಯ ಸಂಹಿತೆ (BNS) ಯ ವಿಭಾಗ ಸಂಖ್ಯೆಯನ್ನು ನಮೂದಿಸಿ ಮತ್ತು ಅದು ಸರಳ ಭಾಷೆಯಲ್ಲಿ ಏನು ಹೇಳುತ್ತದೆ ಎಂಬುದನ್ನು ನೋಡಿ.",
    srLabel: "ಬಿಎನ್‌ಎಸ್ ವಿಭಾಗ ಸಂಖ್ಯೆ",
    placeholder: "ಉದಾ. 103",
    buttonDecode: "ವಿಭಾಗವನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ",
    buttonLoading: "ಹುಡುಕಲಾಗುತ್ತಿದೆ...",
    sectionLabel: "ವಿಭಾಗ",
    originalText: "ಮೂಲ ಪಠ್ಯ:",
  },
};

export function getBnsContent(uiLanguage) {
  return BNS_CONTENT[uiLanguage] || BNS_CONTENT.en;
}

// NOTE: this file covers the Drafter UI chrome only. Document type labels,
// section titles, field labels/placeholders and options come from
// documentSchemas.js / constants.js and are still English-only - they're
// legal document content, so machine-translating them needs a native
// speaker's review rather than a guess. Left alone intentionally.
const DRAFTER_CONTENT = {
  en: {
    heading: "Legal Document Generator",
    typeSelectLabel: "What document do you want to create?",
    subtitle: function (label) { return "Let's create your " + label; },
    selectPlaceholder: "Select...",
    genericFormNotice: "This document type doesn't have a detailed form yet. Enter any details you'd like included, one per line (e.g. \"name: John Doe\") - anything you leave out will appear as a blank line to fill in later.",
    submitButton: "Generate Document",
    submittingButton: "Generating...",
    downloadButton: "Download as Word",
    errDefault: "Could not generate the document.",
    errNetwork: "Could not reach the server. Make sure the backend is running.",
  },
  hi: {
    heading: "कानूनी दस्तावेज़ जनरेटर",
    typeSelectLabel: "आप कौन सा दस्तावेज़ बनाना चाहते हैं?",
    subtitle: function (label) { return "आइए आपका " + label + " तैयार करते हैं"; },
    selectPlaceholder: "चुनें...",
    genericFormNotice: "इस दस्तावेज़ प्रकार के लिए अभी विस्तृत फ़ॉर्म उपलब्ध नहीं है। जो विवरण शामिल करना चाहें, एक-एक पंक्ति में लिखें (जैसे \"name: John Doe\") - जो छोड़ेंगे वह खाली लाइन के रूप में बाद में भरने के लिए दिखेगा।",
    submitButton: "दस्तावेज़ बनाएं",
    submittingButton: "बनाया जा रहा है...",
    downloadButton: "वर्ड में डाउनलोड करें",
    errDefault: "दस्तावेज़ बनाने में समस्या आई।",
    errNetwork: "सर्वर से संपर्क नहीं हो पाया। सुनिश्चित करें कि बैकएंड चल रहा है।",
  },
  kn: {
    heading: "ಕಾನೂನು ದಾಖಲೆ ಜನರೇಟರ್",
    typeSelectLabel: "ನೀವು ಯಾವ ದಾಖಲೆಯನ್ನು ರಚಿಸಲು ಬಯಸುತ್ತೀರಿ?",
    subtitle: function (label) { return "ನಿಮ್ಮ " + label + " ಅನ್ನು ರಚಿಸೋಣ"; },
    selectPlaceholder: "ಆಯ್ಕೆಮಾಡಿ...",
    genericFormNotice: "ಈ ದಾಖಲೆ ಪ್ರಕಾರಕ್ಕೆ ಇನ್ನೂ ವಿವರವಾದ ಫಾರ್ಮ್ ಇಲ್ಲ. ನೀವು ಸೇರಿಸಲು ಬಯಸುವ ವಿವರಗಳನ್ನು ಒಂದೊಂದು ಸಾಲಿನಲ್ಲಿ ನಮೂದಿಸಿ (ಉದಾ: \"name: John Doe\") - ನೀವು ಬಿಟ್ಟುಬಿಡುವುದು ನಂತರ ಭರ್ತಿ ಮಾಡಲು ಖಾಲಿ ಸಾಲಿನಂತೆ ಕಾಣಿಸುತ್ತದೆ.",
    submitButton: "ದಾಖಲೆ ರಚಿಸಿ",
    submittingButton: "ರಚಿಸಲಾಗುತ್ತಿದೆ...",
    downloadButton: "ವರ್ಡ್ ಆಗಿ ಡೌನ್‌ಲೋಡ್ ಮಾಡಿ",
    errDefault: "ದಾಖಲೆಯನ್ನು ರಚಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ.",
    errNetwork: "ಸರ್ವರ್ ಸಂಪರ್ಕಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ಬ್ಯಾಕೆಂಡ್ ಚಾಲನೆಯಲ್ಲಿದೆಯೇ ಎಂದು ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ.",
  },
};

export function getDrafterContent(uiLanguage) {
  return DRAFTER_CONTENT[uiLanguage] || DRAFTER_CONTENT.en;
}

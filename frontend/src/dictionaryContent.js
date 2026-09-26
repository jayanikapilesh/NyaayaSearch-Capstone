const DICTIONARY_CONTENT = {
  en: {
    heading: "Legal Dictionary",
    srLabel: "Legal term to look up",
    placeholder: "Look up a legal term, e.g. 'cognizable offence'",
    buttonLookingUp: "Looking up...",
    buttonDefine: "Define",
    notFoundFallback: "No definition found.",
    errDefault: "Something went wrong looking up this term.",
    errNetwork: "Could not reach the server. Please try again.",
  },
  hi: {
    heading: "कानूनी शब्दकोश",
    srLabel: "खोजने के लिए कानूनी शब्द",
    placeholder: "कोई कानूनी शब्द खोजें, जैसे 'cognizable offence'",
    buttonLookingUp: "खोज रहे हैं...",
    buttonDefine: "मतलब देखें",
    notFoundFallback: "इस शब्द का मतलब नहीं मिला।",
    errDefault: "इस शब्द को खोजने में कुछ समस्या आई।",
    errNetwork: "सर्वर से संपर्क नहीं हो पाया। फिर से कोशिश करें।",
  },
  kn: {
    heading: "ಕಾನೂನು ನಿಘಂಟು",
    srLabel: "ಹುಡುಕಬೇಕಾದ ಕಾನೂನು ಪದ",
    placeholder: "ಕಾನೂನು ಪದವನ್ನು ಹುಡುಕಿ, ಉದಾ: 'cognizable offence'",
    buttonLookingUp: "ಹುಡುಕಲಾಗುತ್ತಿದೆ...",
    buttonDefine: "ಅರ್ಥ ನೋಡಿ",
    notFoundFallback: "ಈ ಪದದ ಅರ್ಥ ಸಿಗಲಿಲ್ಲ.",
    errDefault: "ಈ ಪದವನ್ನು ಹುಡುಕುವಲ್ಲಿ ಏನೋ ತೊಂದರೆಯಾಗಿದೆ.",
    errNetwork: "ಸರ್ವರ್ ಸಂಪರ್ಕಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
  },
};

export function getDictionaryContent(uiLanguage) {
  return DICTIONARY_CONTENT[uiLanguage] || DICTIONARY_CONTENT.en;
}

const SIMPLIFIER_CONTENT = {
  en: {
    heading: "Case Simplifier",
    intro: "Paste a court judgment, order, or legal case text to get a plain-language explanation.",
    textareaSrLabel: "Case text to simplify",
    textareaPlaceholder: "Paste the case text here...",
    submitButton: "Simplify Case",
    submittingButton: "Simplifying...",
    resultHeading: "Explanation",
    errDefault: "Could not simplify this case. Please try again.",
    errNetwork: "Could not reach the server. Make sure the backend is running.",
    caseContextHint: "Paste the judgment text for this case below to simplify it.",
    caseContextDismiss: "Dismiss",
  },
  hi: {
    heading: "केस सरलीकरण",
    intro: "सरल भाषा में स्पष्टीकरण पाने के लिए कोर्ट का फैसला, आदेश, या कानूनी मामले का पाठ पेस्ट करें।",
    textareaSrLabel: "सरल किया जाने वाला केस टेक्स्ट",
    textareaPlaceholder: "यहां केस का पाठ पेस्ट करें...",
    submitButton: "केस सरल करें",
    submittingButton: "सरल किया जा रहा है...",
    resultHeading: "स्पष्टीकरण",
    errDefault: "इस केस को सरल करने में समस्या आई। कृपया फिर से कोशिश करें।",
    errNetwork: "सर्वर से संपर्क नहीं हो पाया। सुनिश्चित करें कि बैकएंड चल रहा है।",
    caseContextHint: "इस मामले को सरल करने के लिए नीचे फैसले का पाठ पेस्ट करें।",
    caseContextDismiss: "बंद करें",
  },
  kn: {
    heading: "ಪ್ರಕರಣ ಸರಳೀಕರಣ",
    intro: "ಸರಳ ಭಾಷೆಯ ವಿವರಣೆ ಪಡೆಯಲು ನ್ಯಾಯಾಲಯದ ತೀರ್ಪು, ಆದೇಶ, ಅಥವಾ ಕಾನೂನು ಪ್ರಕರಣದ ಪಠ್ಯವನ್ನು ಅಂಟಿಸಿ.",
    textareaSrLabel: "ಸರಳಗೊಳಿಸಬೇಕಾದ ಪ್ರಕರಣದ ಪಠ್ಯ",
    textareaPlaceholder: "ಪ್ರಕರಣದ ಪಠ್ಯವನ್ನು ಇಲ್ಲಿ ಅಂಟಿಸಿ...",
    submitButton: "ಪ್ರಕರಣ ಸರಳಗೊಳಿಸಿ",
    submittingButton: "ಸರಳಗೊಳಿಸಲಾಗುತ್ತಿದೆ...",
    resultHeading: "ವಿವರಣೆ",
    errDefault: "ಈ ಪ್ರಕರಣವನ್ನು ಸರಳಗೊಳಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ.",
    errNetwork: "ಸರ್ವರ್ ಸಂಪರ್ಕಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ಬ್ಯಾಕೆಂಡ್ ಚಾಲನೆಯಲ್ಲಿದೆಯೇ ಎಂದು ಖಚಿತಪಡಿಸಿಕೊಳ್ಳಿ.",
    caseContextHint: "ಈ ಪ್ರಕರಣವನ್ನು ಸರಳಗೊಳಿಸಲು ಕೆಳಗೆ ತೀರ್ಪಿನ ಪಠ್ಯವನ್ನು ಅಂಟಿಸಿ.",
    caseContextDismiss: "ಮುಚ್ಚಿ",
  },
};

export function getSimplifierContent(uiLanguage) {
  return SIMPLIFIER_CONTENT[uiLanguage] || SIMPLIFIER_CONTENT.en;
}

import { DOCUMENT_SCHEMAS, ADDITIONAL_DOCUMENT_SCHEMAS } from "./documentSchemas";

export const API_URL = "http://127.0.0.1:8000";
export const HISTORY_KEY = "nyaaya-search-history";
export const MAX_HISTORY = 8;
export const SAVED_RESULTS_KEY = "nyaaya-saved-results";

export const LANGUAGE_LABELS = {
  en: "English",
  hi: "हिंदी",
  kn: "ಕನ್ನಡ",
};

export const ALL_LANGUAGES = ["en", "hi", "kn"];

// UI strings for the search/results view - the only screen with a language
// toggle. The AI-generated explanation itself is translated separately via
// the /translate-explanation API; these are the surrounding interface labels,
// which that API never touches.
export const UI_STRINGS = {
  en: {
    search: "Search",
    searching: "Searching...",
    searchingFull: "Searching legal database and generating explanation...",
    mic: "Mic",
    listeningIndicator: "Listening... (click mic again to stop)",
    tryAsking: "Try asking:",
    recent: "Recent:",
    clear: "Clear",
    savedResults: "Saved Results",
    delete: "Delete",
    lowConfidenceWarning: "We're not fully confident in these results. Try rephrasing your question with more specific details for a better match. Showing our best guess below.",
    explanation: "Explanation",
    listen: "Listen",
    stop: "Stop",
    save: "Save",
    saved: "Saved",
    translating: "Translating...",
    sources: "Sources",
    section: "Section",
    strongMatch: "Strong match",
    goodMatch: "Good match",
    possibleMatch: "Possible match",
    whyThisMatched: "Why this matched:",
    relatedCases: "Related Supreme Court Cases",
  },
  hi: {
    search: "खोजें",
    searching: "खोज रहे हैं...",
    searchingFull: "कानूनी डेटाबेस खोजा जा रहा है और व्याख्या तैयार की जा रही है...",
    mic: "माइक",
    listeningIndicator: "सुन रहे हैं... (रोकने के लिए माइक पर फिर से क्लिक करें)",
    tryAsking: "ऐसे पूछकर देखें:",
    recent: "हाल ही में:",
    clear: "साफ़ करें",
    savedResults: "सहेजे गए परिणाम",
    delete: "हटाएं",
    lowConfidenceWarning: "हमें इन परिणामों पर पूरा भरोसा नहीं है। बेहतर मिलान के लिए अपने प्रश्न को अधिक विशिष्ट विवरण के साथ दोबारा लिखने का प्रयास करें। नीचे हमारा सबसे अच्छा अनुमान दिखाया जा रहा है।",
    explanation: "व्याख्या",
    listen: "सुनें",
    stop: "रोकें",
    save: "सहेजें",
    saved: "सहेजा गया",
    translating: "अनुवाद हो रहा है...",
    sources: "स्रोत",
    section: "धारा",
    strongMatch: "मजबूत मिलान",
    goodMatch: "अच्छा मिलान",
    possibleMatch: "संभावित मिलान",
    whyThisMatched: "यह क्यों मेल खाया:",
    relatedCases: "संबंधित सर्वोच्च न्यायालय के मामले",
  },
  kn: {
    search: "ಹುಡುಕಿ",
    searching: "ಹುಡುಕಲಾಗುತ್ತಿದೆ...",
    searchingFull: "ಕಾನೂನು ಡೇಟಾಬೇಸ್ ಹುಡುಕಲಾಗುತ್ತಿದೆ ಮತ್ತು ವಿವರಣೆಯನ್ನು ರಚಿಸಲಾಗುತ್ತಿದೆ...",
    mic: "ಮೈಕ್",
    listeningIndicator: "ಆಲಿಸಲಾಗುತ್ತಿದೆ... (ನಿಲ್ಲಿಸಲು ಮೈಕ್ ಅನ್ನು ಮತ್ತೆ ಕ್ಲಿಕ್ ಮಾಡಿ)",
    tryAsking: "ಹೀಗೆ ಕೇಳಲು ಪ್ರಯತ್ನಿಸಿ:",
    recent: "ಇತ್ತೀಚಿನ:",
    clear: "ತೆರವುಗೊಳಿಸಿ",
    savedResults: "ಉಳಿಸಿದ ಫಲಿತಾಂಶಗಳು",
    delete: "ಅಳಿಸಿ",
    lowConfidenceWarning: "ಈ ಫಲಿತಾಂಶಗಳ ಬಗ್ಗೆ ನಮಗೆ ಸಂಪೂರ್ಣ ವಿಶ್ವಾಸವಿಲ್ಲ. ಉತ್ತಮ ಹೊಂದಾಣಿಕೆಗಾಗಿ ಹೆಚ್ಚು ನಿರ್ದಿಷ್ಟ ವಿವರಗಳೊಂದಿಗೆ ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಮರುರೂಪಿಸಲು ಪ್ರಯತ್ನಿಸಿ. ಕೆಳಗೆ ನಮ್ಮ ಅತ್ಯುತ್ತಮ ಊಹೆಯನ್ನು ತೋರಿಸಲಾಗಿದೆ.",
    explanation: "ವಿವರಣೆ",
    listen: "ಆಲಿಸಿ",
    stop: "ನಿಲ್ಲಿಸಿ",
    save: "ಉಳಿಸಿ",
    saved: "ಉಳಿಸಲಾಗಿದೆ",
    translating: "ಅನುವಾದಿಸಲಾಗುತ್ತಿದೆ...",
    sources: "ಮೂಲಗಳು",
    section: "ವಿಭಾಗ",
    strongMatch: "ಬಲವಾದ ಹೊಂದಾಣಿಕೆ",
    goodMatch: "ಉತ್ತಮ ಹೊಂದಾಣಿಕೆ",
    possibleMatch: "ಸಂಭವನೀಯ ಹೊಂದಾಣಿಕೆ",
    whyThisMatched: "ಇದು ಏಕೆ ಹೊಂದಿಕೆಯಾಯಿತು:",
    relatedCases: "ಸಂಬಂಧಿತ ಸುಪ್ರೀಂ ಕೋರ್ಟ್ ಪ್ರಕರಣಗಳು",
  },
};

export const MERGED_DOCUMENT_SCHEMAS = Object.assign({}, DOCUMENT_SCHEMAS, ADDITIONAL_DOCUMENT_SCHEMAS);

export const ALL_DOCUMENT_TYPE_LABELS = {
  ...Object.fromEntries(Object.entries(MERGED_DOCUMENT_SCHEMAS).map(([key, schema]) => [key, schema.label])),
};

import { DOCUMENT_SCHEMAS, ADDITIONAL_DOCUMENT_SCHEMAS } from "./documentSchemas";

export const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";
export const HISTORY_KEY = "nyaaya-search-history";
export const MAX_HISTORY = 8;
export const SAVED_RESULTS_KEY = "nyaaya-saved-results";
export const MAX_SAVED_RESULTS = 20;
export const UPLOADED_DOCS_KEY = "nyaaya-uploaded-docs";
export const GENERATED_DOCS_KEY = "nyaaya-generated-docs";
export const MAX_STORED_DOCS = 15;
export const PINNED_QUERIES_KEY = "nyaaya-pinned-queries";
export const DAILY_QUIZ_KEY = "nyaaya-legal-iq-daily";

// A small, curated list of terms that show up often in real NyaayaSearch
// queries and in the app's own copy (drawn from the backend's own
// query-synonym dictionary in scripts/search_core.py, plus the Acts this
// app covers), used only to catch obvious single-word typos before search -
// never a general-purpose English dictionary, which would flag correct
// legal terms as "misspelled".
export const KNOWN_LEGAL_TERMS = [
  "landlord", "tenant", "deposit", "rent", "lease", "eviction", "agreement",
  "contract", "threat", "coercion", "minor", "hacked", "blackmail",
  "occupying", "licence", "license", "suspended", "revoked", "sale",
  "harmful", "attacked", "assault", "arrest", "warrant", "custody",
  "detention", "stop", "injunction", "lying", "misrepresentation", "break",
  "breach", "appeal", "review", "report", "therapy", "counselling",
  "compensation", "consumer", "complaint", "defective", "product",
  "extortion", "fraud", "forgery", "trademark", "summons", "cognizance",
  "bail", "bond", "surety", "police", "fir", "grievous", "injury",
  "negligence", "defamation", "divorce", "inheritance", "will",
  "property", "mortgage", "possession", "notice", "tribunal", "cybercrime",
  "harassment", "domestic", "violence", "dowry", "trespass", "vehicle",
  "accident", "insurance", "registration", "driving",
];

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
    searchingFull: "Searching legal database...",
    loadingExplanation: "Generating plain-language explanation...",
    mic: "Mic",
    listeningIndicator: "Listening... (click mic again to stop)",
    tryAsking: "Try asking:",
    recent: "Recent:",
    clear: "Clear",
    savedResults: "Saved Results",
    delete: "Delete",
    deleteConfirm: "Delete this saved result?",
    deleteConfirmYes: "Yes, delete",
    cancel: "Cancel",
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
    simplifyThisCase: "Simplify this case",
    lookUpSection: "Look up this section",
    didYouMean: "Did you mean:",
    confidenceInfoToggle: "What do these mean?",
    confidenceInfoIntro: "These labels compare each result's match score to the top result for this search - they are not a percentage, and not a measure of legal accuracy.",
    confidenceInfoStrong: "Strong match - very close to the best match found for this search.",
    confidenceInfoGood: "Good match - a solid match, a little further from the top result.",
    confidenceInfoWeak: "Possible match - worth checking, but a looser match than the others.",
    pinned: "Pinned:",
    pin: "Pin",
    unpin: "Unpin",
  },
  hi: {
    search: "खोजें",
    searching: "खोज रहे हैं...",
    searchingFull: "कानूनी डेटाबेस खोजा जा रहा है...",
    loadingExplanation: "आसान भाषा में जवाब तैयार हो रहा है...",
    mic: "माइक",
    listeningIndicator: "सुन रहे हैं... (रोकने के लिए माइक पर फिर से क्लिक करें)",
    tryAsking: "ऐसे पूछकर देखें:",
    recent: "हाल ही में:",
    clear: "साफ़ करें",
    savedResults: "सहेजे गए परिणाम",
    delete: "हटाएं",
    deleteConfirm: "यह सहेजा गया परिणाम हटाएं?",
    deleteConfirmYes: "हां, हटाएं",
    cancel: "रद्द करें",
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
    simplifyThisCase: "इस मामले को सरल करें",
    lookUpSection: "यह धारा देखें",
    didYouMean: "क्या आपका मतलब यह था:",
    confidenceInfoToggle: "इनका क्या मतलब है?",
    confidenceInfoIntro: "ये लेबल हर परिणाम के मिलान स्कोर की तुलना इस खोज के सबसे अच्छे परिणाम से करते हैं - यह कोई प्रतिशत नहीं है, और न ही कानूनी सटीकता का माप है।",
    confidenceInfoStrong: "मजबूत मिलान - इस खोज के सबसे अच्छे परिणाम के बहुत करीब।",
    confidenceInfoGood: "अच्छा मिलान - एक ठोस मिलान, शीर्ष परिणाम से थोड़ा दूर।",
    confidenceInfoWeak: "संभावित मिलान - जांचने लायक, पर बाकी की तुलना में ढीला मिलान।",
    pinned: "पिन किए गए:",
    pin: "पिन करें",
    unpin: "अनपिन करें",
  },
  kn: {
    search: "ಹುಡುಕಿ",
    searching: "ಹುಡುಕಲಾಗುತ್ತಿದೆ...",
    searchingFull: "ಕಾನೂನು ಡೇಟಾಬೇಸ್ ಹುಡುಕಲಾಗುತ್ತಿದೆ...",
    loadingExplanation: "ಸರಳ ಭಾಷೆಯ ವಿವರಣೆಯನ್ನು ರಚಿಸಲಾಗುತ್ತಿದೆ...",
    mic: "ಮೈಕ್",
    listeningIndicator: "ಆಲಿಸಲಾಗುತ್ತಿದೆ... (ನಿಲ್ಲಿಸಲು ಮೈಕ್ ಅನ್ನು ಮತ್ತೆ ಕ್ಲಿಕ್ ಮಾಡಿ)",
    tryAsking: "ಹೀಗೆ ಕೇಳಲು ಪ್ರಯತ್ನಿಸಿ:",
    recent: "ಇತ್ತೀಚಿನ:",
    clear: "ತೆರವುಗೊಳಿಸಿ",
    savedResults: "ಉಳಿಸಿದ ಫಲಿತಾಂಶಗಳು",
    delete: "ಅಳಿಸಿ",
    deleteConfirm: "ಈ ಉಳಿಸಿದ ಫಲಿತಾಂಶವನ್ನು ಅಳಿಸಬೇಕೆ?",
    deleteConfirmYes: "ಹೌದು, ಅಳಿಸಿ",
    cancel: "ರದ್ದುಮಾಡಿ",
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
    simplifyThisCase: "ಈ ಪ್ರಕರಣವನ್ನು ಸರಳಗೊಳಿಸಿ",
    lookUpSection: "ಈ ವಿಭಾಗವನ್ನು ನೋಡಿ",
    didYouMean: "ನಿಮ್ಮ ಉದ್ದೇಶ ಇದೇ ಆಗಿತ್ತೇ:",
    confidenceInfoToggle: "ಇವುಗಳ ಅರ್ಥವೇನು?",
    confidenceInfoIntro: "ಈ ಲೇಬಲ್‌ಗಳು ಪ್ರತಿ ಫಲಿತಾಂಶದ ಹೊಂದಾಣಿಕೆ ಸ್ಕೋರ್ ಅನ್ನು ಈ ಹುಡುಕಾಟದ ಅತ್ಯುತ್ತಮ ಫಲಿತಾಂಶದೊಂದಿಗೆ ಹೋಲಿಸುತ್ತವೆ - ಇದು ಶೇಕಡಾವಾರು ಅಲ್ಲ, ಮತ್ತು ಕಾನೂನು ನಿಖರತೆಯ ಅಳತೆಯೂ ಅಲ್ಲ.",
    confidenceInfoStrong: "ಬಲವಾದ ಹೊಂದಾಣಿಕೆ - ಈ ಹುಡುಕಾಟದ ಅತ್ಯುತ್ತಮ ಫಲಿತಾಂಶಕ್ಕೆ ಬಹಳ ಹತ್ತಿರ.",
    confidenceInfoGood: "ಉತ್ತಮ ಹೊಂದಾಣಿಕೆ - ಉತ್ತಮ ಹೊಂದಾಣಿಕೆ, ಅಗ್ರ ಫಲಿತಾಂಶದಿಂದ ಸ್ವಲ್ಪ ದೂರ.",
    confidenceInfoWeak: "ಸಂಭವನೀಯ ಹೊಂದಾಣಿಕೆ - ಪರಿಶೀಲಿಸಲು ಯೋಗ್ಯ, ಆದರೆ ಇತರರಿಗಿಂತ ಸಡಿಲವಾದ ಹೊಂದಾಣಿಕೆ.",
    pinned: "ಪಿನ್ ಮಾಡಿದವು:",
    pin: "ಪಿನ್ ಮಾಡಿ",
    unpin: "ಅನ್‌ಪಿನ್ ಮಾಡಿ",
  },
};

export const MERGED_DOCUMENT_SCHEMAS = Object.assign({}, DOCUMENT_SCHEMAS, ADDITIONAL_DOCUMENT_SCHEMAS);

export const ALL_DOCUMENT_TYPE_LABELS = {
  ...Object.fromEntries(Object.entries(MERGED_DOCUMENT_SCHEMAS).map(([key, schema]) => [key, schema.label])),
};

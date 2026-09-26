// Static copy for HomeTab, keyed by language. Mirrors the pattern already
// used for UI_STRINGS in constants.js: en is authoritative, hi/kn are
// best-effort translations (not professionally reviewed).
export const HOME_CONTENT = {
  en: {
    eyebrow: "Law In Your Language",
    heroHeadlineLine1: "Search, draft, and understand",
    heroHeadlineLine2: "Indian law in plain language.",
    heroSubtitle: "NyaayaSearch matches your question to the exact Acts and Sections that apply, explains what they mean, and helps you act on them - in English, Hindi, or Kannada.",
    ctaLabel: "Start Searching",
    statsLabels: {
      acts: "Acts Covered",
      sections: "Sections Indexed",
      cases: "SC Cases Linked to Acts",
      languages: "Languages Supported",
    },
    workflowHeading: "How NyaayaSearch Works",
    workflowSteps: [
      { title: "Describe your situation", description: "Type or speak your question in English, Hindi, or Kannada." },
      { title: "We search real statutes", description: "Hybrid search matches your question to the exact Acts and Sections that apply." },
      { title: "Get a plain-language explanation", description: "See what the law means for you, with every citation traceable to its source section." },
      { title: "Explore more tools", description: "Draft documents, decode BNS sections, simplify judgments, and more." },
    ],
    featureCardsHeading: "What You Can Do Here",
    featureCards: [
      { tab: "search", title: "Search", description: "Describe a legal situation and get matched sections with a plain-language explanation." },
      { tab: "drafter", title: "Document Generator", description: "Generate rent agreements, notices, and other legal documents from a guided form." },
      { tab: "dictionary", title: "Dictionary", description: "Look up legal terms in plain English." },
      { tab: "documents", title: "My Documents", description: "Revisit your saved searches and uploaded PDFs anytime." },
      { tab: "simplifier", title: "Case Simplifier", description: "Paste a court judgment and get a plain-language summary." },
      { tab: "bns", title: "BNS Decoder", description: "Look up any Bharatiya Nyaya Sanhita section number and see what it means." },
      { tab: "quiz", title: "Legal IQ Daily", description: "Test your knowledge of Indian law with a daily quiz." },
    ],
    problem: {
      eyebrow: "The Problem",
      heading: "Legal Information Isn't Built For Everyone",
      body: "Most legal information in India is written in dense English legal language, scattered across government sites, PDFs, and outdated portals. For the hundreds of millions of people who read Hindi or Kannada, or who simply aren't trained in legal terminology, that gap makes it hard to know what the law actually says, or what to do next.",
      imageSubject: "old law book, dark",
    },
    howItWorksSection: {
      eyebrow: "How It Works",
      heading: "From Question To Explanation",
      body: "NyaayaSearch runs a hybrid search, keyword matching combined with a fine-tuned semantic model, over Indian Acts and Sections, then uses an LLM to explain the matched sections in plain language, with guardrails that check every citation against the source text.",
    },
    everyone: {
      eyebrow: "Built For Everyone",
      heading: "Support For Every Reader",
      body: "Search, results, and explanations all work in English, Hindi, and Kannada, and voice input lets you ask your question instead of typing it, built for people who aren't comfortable reading legal English.",
      imageSubject: "people using phone",
    },
    footerDisclaimer: "NyaayaSearch provides legal information, not legal advice. Consult a lawyer for your specific situation.",
  },

  hi: {
    eyebrow: "आपकी भाषा में कानून",
    heroHeadlineLine1: "भारतीय कानून को खोजें, तैयार करें,",
    heroHeadlineLine2: "और सरल भाषा में समझें।",
    heroSubtitle: "न्यायासर्च आपके प्रश्न से जुड़ी सटीक धाराओं और अधिनियमों को खोजता है, उनका अर्थ समझाता है, और अंग्रेज़ी, हिंदी या कन्नड़ में आपको आगे बढ़ने में मदद करता है।",
    ctaLabel: "खोजना शुरू करें",
    statsLabels: {
      acts: "शामिल अधिनियम",
      sections: "शामिल धाराएं",
      cases: "अधिनियमों से जुड़े सुप्रीम कोर्ट मामले",
      languages: "समर्थित भाषाएं",
    },
    workflowHeading: "न्यायासर्च कैसे काम करता है",
    workflowSteps: [
      { title: "अपनी स्थिति बताएं", description: "अंग्रेज़ी, हिंदी या कन्नड़ में अपना प्रश्न टाइप करें या बोलें।" },
      { title: "हम वास्तविक कानूनों में खोजते हैं", description: "हाइब्रिड खोज आपके प्रश्न को सही अधिनियमों और धाराओं से मिलाती है।" },
      { title: "सरल भाषा में व्याख्या पाएं", description: "देखें कि कानून का आपके लिए क्या अर्थ है, हर हवाला उसकी मूल धारा से जुड़ा है।" },
      { title: "और उपकरण देखें", description: "दस्तावेज़ तैयार करें, बीएनएस धाराएं समझें, फैसले सरल करें, और भी बहुत कुछ।" },
    ],
    featureCardsHeading: "यहां आप क्या कर सकते हैं",
    featureCards: [
      { tab: "search", title: "खोज", description: "किसी कानूनी स्थिति का वर्णन करें और सरल भाषा में व्याख्या के साथ मिलती-जुलती धाराएं पाएं।" },
      { tab: "drafter", title: "दस्तावेज़ जनरेटर", description: "एक निर्देशित फ़ॉर्म से किराया समझौते, नोटिस और अन्य कानूनी दस्तावेज़ तैयार करें।" },
      { tab: "dictionary", title: "शब्दकोश", description: "कानूनी शब्दों का सरल अंग्रेज़ी में अर्थ देखें।" },
      { tab: "documents", title: "मेरे दस्तावेज़", description: "अपनी सहेजी गई खोजें और अपलोड की गई पीडीएफ़ कभी भी दोबारा देखें।" },
      { tab: "simplifier", title: "फैसला सरल भाषा में", description: "किसी अदालती फैसले को पेस्ट करें और सरल भाषा में सारांश पाएं।" },
      { tab: "bns", title: "बीएनएस डिकोडर", description: "किसी भी भारतीय न्याय संहिता धारा संख्या का अर्थ जानें।" },
      { tab: "quiz", title: "लीगल आईक्यू डेली", description: "रोज़ाना क्विज़ के साथ भारतीय कानून का अपना ज्ञान परखें।" },
    ],
    problem: {
      eyebrow: "समस्या",
      heading: "कानूनी जानकारी सबके लिए सुलभ नहीं है",
      body: "भारत में अधिकांश कानूनी जानकारी जटिल अंग्रेज़ी भाषा में लिखी है, जो सरकारी वेबसाइटों, पीडीएफ़ और पुराने पोर्टलों में बिखरी हुई है। करोड़ों हिंदी और कन्नड़ भाषी लोगों के लिए, या जिन्हें कानूनी शब्दावली की जानकारी नहीं है, यह अंतर यह जानना मुश्किल बना देता है कि कानून वास्तव में क्या कहता है, या आगे क्या करना चाहिए।",
      imageSubject: "old law book, dark",
    },
    howItWorksSection: {
      eyebrow: "यह कैसे काम करता है",
      heading: "प्रश्न से व्याख्या तक",
      body: "न्यायासर्च भारतीय अधिनियमों और धाराओं पर एक हाइब्रिड खोज चलाता है, कीवर्ड मिलान को एक फाइन-ट्यून किए गए सिमेंटिक मॉडल के साथ जोड़कर, फिर एक एलएलएम मिली धाराओं को सरल भाषा में समझाता है, और हर उद्धरण को मूल पाठ से जांचता है।",
    },
    everyone: {
      eyebrow: "सभी के लिए बनाया गया",
      heading: "हर पाठक के लिए सहायता",
      body: "खोज, परिणाम और व्याख्याएं अंग्रेज़ी, हिंदी और कन्नड़ में काम करती हैं, और वॉइस इनपुट से आप टाइप करने के बजाय अपना प्रश्न बोल सकते हैं, यह उन लोगों के लिए बनाया गया है जिन्हें कानूनी अंग्रेज़ी पढ़ने में सहजता नहीं है।",
      imageSubject: "people using phone",
    },
    footerDisclaimer: "न्यायासर्च कानूनी जानकारी प्रदान करता है, कानूनी सलाह नहीं। अपनी विशेष स्थिति के लिए किसी वकील से सलाह लें।",
  },

  kn: {
    eyebrow: "ನಿಮ್ಮ ಭಾಷೆಯಲ್ಲಿ ಕಾನೂನು",
    heroHeadlineLine1: "ಭಾರತೀಯ ಕಾನೂನನ್ನು ಹುಡುಕಿ, ರಚಿಸಿ,",
    heroHeadlineLine2: "ಮತ್ತು ಸರಳ ಭಾಷೆಯಲ್ಲಿ ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ.",
    heroSubtitle: "ನ್ಯಾಯಸರ್ಚ್ ನಿಮ್ಮ ಪ್ರಶ್ನೆಗೆ ಸಂಬಂಧಿಸಿದ ನಿಖರವಾದ ಕಾಯ್ದೆಗಳು ಮತ್ತು ವಿಭಾಗಗಳನ್ನು ಹೊಂದಿಸುತ್ತದೆ, ಅವುಗಳ ಅರ್ಥವನ್ನು ವಿವರಿಸುತ್ತದೆ, ಮತ್ತು ಇಂಗ್ಲಿಷ್, ಹಿಂದಿ ಅಥವಾ ಕನ್ನಡದಲ್ಲಿ ಮುಂದುವರಿಯಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ.",
    ctaLabel: "ಹುಡುಕಾಟ ಪ್ರಾರಂಭಿಸಿ",
    statsLabels: {
      acts: "ಸೇರಿಸಲಾದ ಕಾಯ್ದೆಗಳು",
      sections: "ಸೂಚ್ಯಂಕಗೊಳಿಸಿದ ವಿಭಾಗಗಳು",
      cases: "ಕಾಯ್ದೆಗಳಿಗೆ ಲಿಂಕ್ ಆದ ಸುಪ್ರೀಂ ಕೋರ್ಟ್ ಪ್ರಕರಣಗಳು",
      languages: "ಬೆಂಬಲಿತ ಭಾಷೆಗಳು",
    },
    workflowHeading: "ನ್ಯಾಯಸರ್ಚ್ ಹೇಗೆ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತದೆ",
    workflowSteps: [
      { title: "ನಿಮ್ಮ ಪರಿಸ್ಥಿತಿಯನ್ನು ವಿವರಿಸಿ", description: "ಇಂಗ್ಲಿಷ್, ಹಿಂದಿ ಅಥವಾ ಕನ್ನಡದಲ್ಲಿ ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಟೈಪ್ ಮಾಡಿ ಅಥವಾ ಹೇಳಿ." },
      { title: "ನಾವು ನಿಜವಾದ ಕಾನೂನುಗಳಲ್ಲಿ ಹುಡುಕುತ್ತೇವೆ", description: "ಹೈಬ್ರಿಡ್ ಹುಡುಕಾಟ ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಸರಿಯಾದ ಕಾಯ್ದೆಗಳು ಮತ್ತು ವಿಭಾಗಗಳೊಂದಿಗೆ ಹೊಂದಿಸುತ್ತದೆ." },
      { title: "ಸರಳ ಭಾಷೆಯಲ್ಲಿ ವಿವರಣೆ ಪಡೆಯಿರಿ", description: "ಕಾನೂನು ನಿಮಗೆ ಏನು ಅರ್ಥೈಸುತ್ತದೆ ಎಂಬುದನ್ನು ನೋಡಿ, ಪ್ರತಿ ಉಲ್ಲೇಖವನ್ನೂ ಅದರ ಮೂಲ ವಿಭಾಗಕ್ಕೆ ಪತ್ತೆಹಚ್ಚಬಹುದು." },
      { title: "ಇನ್ನಷ್ಟು ಸಾಧನಗಳನ್ನು ಅನ್ವೇಷಿಸಿ", description: "ದಾಖಲೆಗಳನ್ನು ರಚಿಸಿ, ಬಿಎನ್‌ಎಸ್ ವಿಭಾಗಗಳನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ, ತೀರ್ಪುಗಳನ್ನು ಸರಳಗೊಳಿಸಿ, ಮತ್ತು ಇನ್ನಷ್ಟು." },
    ],
    featureCardsHeading: "ಇಲ್ಲಿ ನೀವು ಏನು ಮಾಡಬಹುದು",
    featureCards: [
      { tab: "search", title: "ಹುಡುಕಾಟ", description: "ಕಾನೂನು ಪರಿಸ್ಥಿತಿಯನ್ನು ವಿವರಿಸಿ ಮತ್ತು ಸರಳ ಭಾಷೆಯ ವಿವರಣೆಯೊಂದಿಗೆ ಹೊಂದಾಣಿಕೆಯಾಗುವ ವಿಭಾಗಗಳನ್ನು ಪಡೆಯಿರಿ." },
      { tab: "drafter", title: "ದಾಖಲೆ ಜನರೇಟರ್", description: "ಮಾರ್ಗದರ್ಶಿತ ಫಾರ್ಮ್‌ನಿಂದ ಬಾಡಿಗೆ ಒಪ್ಪಂದಗಳು, ಸೂಚನೆಗಳು ಮತ್ತು ಇತರ ಕಾನೂನು ದಾಖಲೆಗಳನ್ನು ರಚಿಸಿ." },
      { tab: "dictionary", title: "ನಿಘಂಟು", description: "ಕಾನೂನು ಪದಗಳ ಅರ್ಥವನ್ನು ಸರಳ ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿ ನೋಡಿ." },
      { tab: "documents", title: "ನನ್ನ ದಾಖಲೆಗಳು", description: "ನಿಮ್ಮ ಉಳಿಸಿದ ಹುಡುಕಾಟಗಳು ಮತ್ತು ಅಪ್‌ಲೋಡ್ ಮಾಡಿದ ಪಿಡಿಎಫ್‌ಗಳನ್ನು ಯಾವಾಗ ಬೇಕಾದರೂ ನೋಡಿ." },
      { tab: "simplifier", title: "ಪ್ರಕರಣ ಸರಳೀಕರಣ", description: "ನ್ಯಾಯಾಲಯದ ತೀರ್ಪನ್ನು ಅಂಟಿಸಿ ಮತ್ತು ಸರಳ ಭಾಷೆಯ ಸಾರಾಂಶ ಪಡೆಯಿರಿ." },
      { tab: "bns", title: "ಬಿಎನ್‌ಎಸ್ ಡಿಕೋಡರ್", description: "ಯಾವುದೇ ಭಾರತೀಯ ನ್ಯಾಯ ಸಂಹಿತೆ ವಿಭಾಗ ಸಂಖ್ಯೆಯ ಅರ್ಥವನ್ನು ನೋಡಿ." },
      { tab: "quiz", title: "ಲೀಗಲ್ ಐಕ್ಯೂ ಡೈಲಿ", description: "ದೈನಂದಿನ ಪ್ರಶ್ನಾವಳಿಯೊಂದಿಗೆ ಭಾರತೀಯ ಕಾನೂನಿನ ಬಗ್ಗೆ ನಿಮ್ಮ ಜ್ಞಾನವನ್ನು ಪರೀಕ್ಷಿಸಿ." },
    ],
    problem: {
      eyebrow: "ಸಮಸ್ಯೆ",
      heading: "ಕಾನೂನು ಮಾಹಿತಿ ಎಲ್ಲರಿಗೂ ಸುಲಭವಾಗಿ ಸಿಗುವುದಿಲ್ಲ",
      body: "ಭಾರತದಲ್ಲಿ ಹೆಚ್ಚಿನ ಕಾನೂನು ಮಾಹಿತಿ ಜಟಿಲವಾದ ಇಂಗ್ಲಿಷ್ ಭಾಷೆಯಲ್ಲಿ ಬರೆಯಲಾಗಿದ್ದು, ಸರ್ಕಾರಿ ಜಾಲತಾಣಗಳು, ಪಿಡಿಎಫ್‌ಗಳು ಮತ್ತು ಹಳೆಯ ಪೋರ್ಟಲ್‌ಗಳಲ್ಲಿ ಹರಡಿಕೊಂಡಿದೆ. ಕೋಟ್ಯಂತರ ಹಿಂದಿ ಮತ್ತು ಕನ್ನಡ ಮಾತನಾಡುವವರಿಗೆ, ಅಥವಾ ಕಾನೂನು ಪದಗಳ ಪರಿಚಯವಿಲ್ಲದವರಿಗೆ, ಈ ಅಂತರವು ಕಾನೂನು ನಿಜವಾಗಿ ಏನು ಹೇಳುತ್ತದೆ ಅಥವಾ ಮುಂದೆ ಏನು ಮಾಡಬೇಕು ಎಂಬುದನ್ನು ತಿಳಿಯುವುದನ್ನು ಕಷ್ಟಕರವಾಗಿಸುತ್ತದೆ.",
      imageSubject: "old law book, dark",
    },
    howItWorksSection: {
      eyebrow: "ಇದು ಹೇಗೆ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತದೆ",
      heading: "ಪ್ರಶ್ನೆಯಿಂದ ವಿವರಣೆಯವರೆಗೆ",
      body: "ನ್ಯಾಯಸರ್ಚ್ ಭಾರತೀಯ ಕಾಯ್ದೆಗಳು ಮತ್ತು ವಿಭಾಗಗಳ ಮೇಲೆ ಹೈಬ್ರಿಡ್ ಹುಡುಕಾಟವನ್ನು ನಡೆಸುತ್ತದೆ, ಕೀವರ್ಡ್ ಹೊಂದಾಣಿಕೆಯನ್ನು ಫೈನ್-ಟ್ಯೂನ್ ಮಾಡಿದ ಸೆಮ್ಯಾಂಟಿಕ್ ಮಾದರಿಯೊಂದಿಗೆ ಸಂಯೋಜಿಸಿ, ನಂತರ ಎಲ್‌ಎಲ್‌ಎಂ ಹೊಂದಾಣಿಕೆಯಾದ ವಿಭಾಗಗಳನ್ನು ಸರಳ ಭಾಷೆಯಲ್ಲಿ ವಿವರಿಸುತ್ತದೆ, ಪ್ರತಿ ಉಲ್ಲೇಖವನ್ನೂ ಮೂಲ ಪಠ್ಯದೊಂದಿಗೆ ಪರಿಶೀಲಿಸುತ್ತದೆ.",
    },
    everyone: {
      eyebrow: "ಎಲ್ಲರಿಗಾಗಿ ರೂಪಿಸಲಾಗಿದೆ",
      heading: "ಪ್ರತಿಯೊಬ್ಬ ಓದುಗರಿಗೂ ಸಹಾಯ",
      body: "ಹುಡುಕಾಟ, ಫಲಿತಾಂಶಗಳು ಮತ್ತು ವಿವರಣೆಗಳು ಇಂಗ್ಲಿಷ್, ಹಿಂದಿ ಮತ್ತು ಕನ್ನಡದಲ್ಲಿ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತವೆ, ಮತ್ತು ಧ್ವನಿ ಇನ್‌ಪುಟ್‌ನೊಂದಿಗೆ ನೀವು ಟೈಪ್ ಮಾಡುವ ಬದಲು ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಬಹುದು, ಕಾನೂನು ಇಂಗ್ಲಿಷ್ ಓದಲು ಕಷ್ಟಪಡುವವರಿಗಾಗಿ ಇದನ್ನು ರೂಪಿಸಲಾಗಿದೆ.",
      imageSubject: "people using phone",
    },
    footerDisclaimer: "ನ್ಯಾಯಸರ್ಚ್ ಕಾನೂನು ಮಾಹಿತಿಯನ್ನು ಒದಗಿಸುತ್ತದೆ, ಕಾನೂನು ಸಲಹೆಯನ್ನಲ್ಲ. ನಿಮ್ಮ ನಿರ್ದಿಷ್ಟ ಪರಿಸ್ಥಿತಿಗಾಗಿ ವಕೀಲರನ್ನು ಸಂಪರ್ಕಿಸಿ.",
  },
};

export function getHomeContent(uiLanguage) {
  return HOME_CONTENT[uiLanguage] || HOME_CONTENT.en;
}

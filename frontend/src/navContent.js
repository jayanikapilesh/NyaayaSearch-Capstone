// Translated strings for the persistent chrome (top bar, bottom nav, More
// menu). Mirrors the pattern in homeContent.js: en is authoritative, hi/kn
// are best-effort translations (not professionally reviewed).
export const NAV_CONTENT = {
  en: {
    languageSwitcherLabel: "Interface language",
    themeToggleToDark: "Switch to dark mode",
    themeToggleToLight: "Switch to light mode",
    primaryNavLabel: "Primary",
    moreMenuLabel: "More options",
    nav: {
      home: "Home",
      search: "Search",
      bns: "BNS Decoder",
      documents: "My Documents",
      more: "More",
    },
    more: {
      drafter: "Document Generator",
      dictionary: "Dictionary",
      simplifier: "Case Simplifier",
      quiz: "Legal IQ Daily",
    },
  },

  hi: {
    languageSwitcherLabel: "इंटरफ़ेस भाषा",
    themeToggleToDark: "डार्क मोड में बदलें",
    themeToggleToLight: "लाइट मोड में बदलें",
    primaryNavLabel: "मुख्य नेविगेशन",
    moreMenuLabel: "अधिक विकल्प",
    nav: {
      home: "होम",
      search: "खोज",
      bns: "बीएनएस डिकोडर",
      documents: "मेरे दस्तावेज़",
      more: "अधिक",
    },
    more: {
      drafter: "दस्तावेज़ जनरेटर",
      dictionary: "शब्दकोश",
      simplifier: "फैसला सरल भाषा में",
      quiz: "लीगल आईक्यू डेली",
    },
  },

  kn: {
    languageSwitcherLabel: "ಇಂಟರ್ಫೇಸ್ ಭಾಷೆ",
    themeToggleToDark: "ಡಾರ್ಕ್ ಮೋಡ್‌ಗೆ ಬದಲಿಸಿ",
    themeToggleToLight: "ಲೈಟ್ ಮೋಡ್‌ಗೆ ಬದಲಿಸಿ",
    primaryNavLabel: "ಮುಖ್ಯ ನ್ಯಾವಿಗೇಷನ್",
    moreMenuLabel: "ಇನ್ನಷ್ಟು ಆಯ್ಕೆಗಳು",
    nav: {
      home: "ಮುಖಪುಟ",
      search: "ಹುಡುಕಾಟ",
      bns: "ಬಿಎನ್‌ಎಸ್ ಡಿಕೋಡರ್",
      documents: "ನನ್ನ ದಾಖಲೆಗಳು",
      more: "ಇನ್ನಷ್ಟು",
    },
    more: {
      drafter: "ದಾಖಲೆ ಜನರೇಟರ್",
      dictionary: "ನಿಘಂಟು",
      simplifier: "ಪ್ರಕರಣ ಸರಳೀಕರಣ",
      quiz: "ಲೀಗಲ್ ಐಕ್ಯೂ ಡೈಲಿ",
    },
  },
};

export function getNavContent(uiLanguage) {
  return NAV_CONTENT[uiLanguage] || NAV_CONTENT.en;
}

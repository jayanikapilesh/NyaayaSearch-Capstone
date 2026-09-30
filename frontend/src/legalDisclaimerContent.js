// Single shared "not legal advice" line shown under every AI-generated
// answer across the app (Search explanation, BNS Decoder, My Documents
// answers/summaries, Case Simplifier, Dictionary) - one string, reused
// everywhere, not duplicated per screen. Hindi/Kannada are AI-generated
// and need native review - see TRANSLATIONS_TO_REVIEW.md.
const LEGAL_DISCLAIMER = {
  en: "This is general legal information, not legal advice. For your specific situation, consult a lawyer or free legal aid (NALSA 15100).",
  hi: "यह सामान्य कानूनी जानकारी है, कानूनी सलाह नहीं है। अपनी विशेष स्थिति के लिए किसी वकील या निःशुल्क कानूनी सहायता (NALSA 15100) से सलाह लें।",
  kn: "ಇದು ಸಾಮಾನ್ಯ ಕಾನೂನು ಮಾಹಿತಿ, ಕಾನೂನು ಸಲಹೆಯಲ್ಲ. ನಿಮ್ಮ ನಿರ್ದಿಷ್ಟ ಪರಿಸ್ಥಿತಿಗಾಗಿ, ವಕೀಲರನ್ನು ಅಥವಾ ಉಚಿತ ಕಾನೂನು ನೆರವು (NALSA 15100) ಸಂಪರ್ಕಿಸಿ.",
};

export function getLegalDisclaimer(uiLanguage) {
  return LEGAL_DISCLAIMER[uiLanguage] || LEGAL_DISCLAIMER.en;
}

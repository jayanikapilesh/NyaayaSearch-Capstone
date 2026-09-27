// NOTE: this file only covers the quiz UI chrome (headings, streak label,
// feedback copy). The quiz questions, options, and explanations themselves
// live in quizData.js and are still English-only - translating legal quiz
// content accurately needs a native-speaker review, so it's intentionally
// left alone rather than machine-translated. See kisha-frontend notes.
const QUIZ_CONTENT = {
  en: {
    heading: "Legal IQ Daily",
    streakLabel: function (streak) { return streak === 1 ? "1-day streak" : streak + "-day streak"; },
    comeBackTomorrow: "You've answered today's question. Come back tomorrow for a new one.",
  },
  hi: {
    heading: "लीगल आईक्यू डेली",
    streakLabel: function (streak) { return streak + " दिन की स्ट्रीक"; },
    comeBackTomorrow: "आपने आज का प्रश्न हल कर लिया है। नया प्रश्न पाने के लिए कल फिर आएं।",
  },
  kn: {
    heading: "ಲೀಗಲ್ ಐಕ್ಯೂ ಡೈಲಿ",
    streakLabel: function (streak) { return streak + "-ದಿನದ ಸ್ಟ್ರೀಕ್"; },
    comeBackTomorrow: "ನೀವು ಇಂದಿನ ಪ್ರಶ್ನೆಗೆ ಉತ್ತರಿಸಿದ್ದೀರಿ. ಹೊಸ ಪ್ರಶ್ನೆಗಾಗಿ ನಾಳೆ ಮತ್ತೆ ಬನ್ನಿ.",
  },
};

export function getQuizContent(uiLanguage) {
  return QUIZ_CONTENT[uiLanguage] || QUIZ_CONTENT.en;
}

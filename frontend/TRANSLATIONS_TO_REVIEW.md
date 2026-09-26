Hindi reviewed by Jayani (native speaker): 4 fixes applied. Kannada reviewed: no changes needed.

# Translations to review

Every Hindi and Kannada string currently in the frontend, with its English
source, for review. These are AI-generated translations, not professionally
reviewed - please correct anything that reads awkwardly, uses the wrong
register, or gets a legal term wrong.

Grouped by source file. Each file also defines `en` as the authoritative
source string (shown here as "English source").

Not included: the `imageSubject` fields in `src/homeContent.js` (e.g. "old
law book, dark") and the "SOS" short label in `src/components/EmergencyButton.jsx`
- both are intentionally identical across all three languages (dev-facing
placeholder text / a universally recognized abbreviation), not translated
content.

## `src/constants.js` - `UI_STRINGS` (Search tab and results)

| Key | English source | Hindi | Kannada |
|---|---|---|---|
| search | Search | खोजें | ಹುಡುಕಿ |
| searching | Searching... | खोज रहे हैं... | ಹುಡುಕಲಾಗುತ್ತಿದೆ... |
| searchingFull | Searching legal database and generating explanation... | कानूनी डेटाबेस खोजा जा रहा है और व्याख्या तैयार की जा रही है... | ಕಾನೂನು ಡೇಟಾಬೇಸ್ ಹುಡುಕಲಾಗುತ್ತಿದೆ ಮತ್ತು ವಿವರಣೆಯನ್ನು ರಚಿಸಲಾಗುತ್ತಿದೆ... |
| mic | Mic | माइक | ಮೈಕ್ |
| listeningIndicator | Listening... (click mic again to stop) | सुन रहे हैं... (रोकने के लिए माइक पर फिर से क्लिक करें) | ಆಲಿಸಲಾಗುತ್ತಿದೆ... (ನಿಲ್ಲಿಸಲು ಮೈಕ್ ಅನ್ನು ಮತ್ತೆ ಕ್ಲಿಕ್ ಮಾಡಿ) |
| tryAsking | Try asking: | ऐसे पूछकर देखें: | ಹೀಗೆ ಕೇಳಲು ಪ್ರಯತ್ನಿಸಿ: |
| recent | Recent: | हाल ही में: | ಇತ್ತೀಚಿನ: |
| clear | Clear | साफ़ करें | ತೆರವುಗೊಳಿಸಿ |
| savedResults | Saved Results | सहेजे गए परिणाम | ಉಳಿಸಿದ ಫಲಿತಾಂಶಗಳು |
| delete | Delete | हटाएं | ಅಳಿಸಿ |
| lowConfidenceWarning | We're not fully confident in these results. Try rephrasing your question with more specific details for a better match. Showing our best guess below. | हमें इन परिणामों पर पूरा भरोसा नहीं है। बेहतर मिलान के लिए अपने प्रश्न को अधिक विशिष्ट विवरण के साथ दोबारा लिखने का प्रयास करें। नीचे हमारा सबसे अच्छा अनुमान दिखाया जा रहा है। | ಈ ಫಲಿತಾಂಶಗಳ ಬಗ್ಗೆ ನಮಗೆ ಸಂಪೂರ್ಣ ವಿಶ್ವಾಸವಿಲ್ಲ. ಉತ್ತಮ ಹೊಂದಾಣಿಕೆಗಾಗಿ ಹೆಚ್ಚು ನಿರ್ದಿಷ್ಟ ವಿವರಗಳೊಂದಿಗೆ ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಮರುರೂಪಿಸಲು ಪ್ರಯತ್ನಿಸಿ. ಕೆಳಗೆ ನಮ್ಮ ಅತ್ಯುತ್ತಮ ಊಹೆಯನ್ನು ತೋರಿಸಲಾಗಿದೆ. |
| explanation | Explanation | व्याख्या | ವಿವರಣೆ |
| listen | Listen | सुनें | ಆಲಿಸಿ |
| stop | Stop | रोकें | ನಿಲ್ಲಿಸಿ |
| save | Save | सहेजें | ಉಳಿಸಿ |
| saved | Saved | सहेजा गया | ಉಳಿಸಲಾಗಿದೆ |
| translating | Translating... | अनुवाद हो रहा है... | ಅನುವಾದಿಸಲಾಗುತ್ತಿದೆ... |
| sources | Sources | स्रोत | ಮೂಲಗಳು |
| section | Section | धारा | ವಿಭಾಗ |
| strongMatch | Strong match | मजबूत मिलान | ಬಲವಾದ ಹೊಂದಾಣಿಕೆ |
| goodMatch | Good match | अच्छा मिलान | ಉತ್ತಮ ಹೊಂದಾಣಿಕೆ |
| possibleMatch | Possible match | संभावित मिलान | ಸಂಭವನೀಯ ಹೊಂದಾಣಿಕೆ |
| whyThisMatched | Why this matched: | यह क्यों मेल खाया: | ಇದು ಏಕೆ ಹೊಂದಿಕೆಯಾಯಿತು: |
| relatedCases | Related Supreme Court Cases | संबंधित सर्वोच्च न्यायालय के मामले | ಸಂಬಂಧಿತ ಸುಪ್ರೀಂ ಕೋರ್ಟ್ ಪ್ರಕರಣಗಳು |

## `src/homeContent.js` - Home tab

### Hero

| Key | English source | Hindi | Kannada |
|---|---|---|---|
| eyebrow | Law In Your Language | आपकी भाषा में कानून | ನಿಮ್ಮ ಭಾಷೆಯಲ್ಲಿ ಕಾನೂನು |
| heroHeadlineLine1 | Search, draft, and understand | भारतीय कानून को खोजें, तैयार करें, | ಭಾರತೀಯ ಕಾನೂನನ್ನು ಹುಡುಕಿ, ರಚಿಸಿ, |
| heroHeadlineLine2 | Indian law in plain language. | और सरल भाषा में समझें। | ಮತ್ತು ಸರಳ ಭಾಷೆಯಲ್ಲಿ ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ. |
| heroSubtitle | NyaayaSearch matches your question to the exact Acts and Sections that apply, explains what they mean, and helps you act on them - in English, Hindi, or Kannada. | न्यायासर्च आपके प्रश्न से जुड़ी सटीक धाराओं और अधिनियमों को खोजता है, उनका अर्थ समझाता है, और अंग्रेज़ी, हिंदी या कन्नड़ में आपको आगे बढ़ने में मदद करता है। | ನ್ಯಾಯಸರ್ಚ್ ನಿಮ್ಮ ಪ್ರಶ್ನೆಗೆ ಸಂಬಂಧಿಸಿದ ನಿಖರವಾದ ಕಾಯ್ದೆಗಳು ಮತ್ತು ವಿಭಾಗಗಳನ್ನು ಹೊಂದಿಸುತ್ತದೆ, ಅವುಗಳ ಅರ್ಥವನ್ನು ವಿವರಿಸುತ್ತದೆ, ಮತ್ತು ಇಂಗ್ಲಿಷ್, ಹಿಂದಿ ಅಥವಾ ಕನ್ನಡದಲ್ಲಿ ಮುಂದುವರಿಯಲು ಸಹಾಯ ಮಾಡುತ್ತದೆ. |
| ctaLabel | Start Searching | खोजना शुरू करें | ಹುಡುಕಾಟ ಪ್ರಾರಂಭಿಸಿ |

Note: `heroHeadlineLine1`'s Hindi/Kannada translations restructure the sentence relative to the English line break (the comma naturally falls in a different place given SOV word order) - the two lines together still form one sentence in every language, just split at a different point than the English does.

### Stat labels (note: `cases` was explicitly worded to say what it counts - 4,525 linked cases out of 8,757 in the corpus)

| Key | English source | Hindi | Kannada |
|---|---|---|---|
| statsLabels.acts | Acts Covered | शामिल अधिनियम | ಸೇರಿಸಲಾದ ಕಾಯ್ದೆಗಳು |
| statsLabels.sections | Sections Indexed | शामिल धाराएं | ಸೂಚ್ಯಂಕಗೊಳಿಸಿದ ವಿಭಾಗಗಳು |
| statsLabels.cases | SC Cases Linked to Acts | अधिनियमों से जुड़े सुप्रीम कोर्ट मामले | ಕಾಯ್ದೆಗಳಿಗೆ ಲಿಂಕ್ ಆದ ಸುಪ್ರೀಂ ಕೋರ್ಟ್ ಪ್ರಕರಣಗಳು |
| statsLabels.languages | Languages Supported | समर्थित भाषाएं | ಬೆಂಬಲಿತ ಭಾಷೆಗಳು |

### "How NyaayaSearch Works" checklist card

| Key | English source | Hindi | Kannada |
|---|---|---|---|
| workflowHeading | How NyaayaSearch Works | न्यायासर्च कैसे काम करता है | ನ್ಯಾಯಸರ್ಚ್ ಹೇಗೆ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತದೆ |
| workflowSteps[0].title | Describe your situation | अपनी स्थिति बताएं | ನಿಮ್ಮ ಪರಿಸ್ಥಿತಿಯನ್ನು ವಿವರಿಸಿ |
| workflowSteps[0].description | Type or speak your question in English, Hindi, or Kannada. | अंग्रेज़ी, हिंदी या कन्नड़ में अपना प्रश्न टाइप करें या बोलें। | ಇಂಗ್ಲಿಷ್, ಹಿಂದಿ ಅಥವಾ ಕನ್ನಡದಲ್ಲಿ ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಟೈಪ್ ಮಾಡಿ ಅಥವಾ ಹೇಳಿ. |
| workflowSteps[1].title | We search real statutes | हम वास्तविक कानूनों में खोजते हैं | ನಾವು ನಿಜವಾದ ಕಾನೂನುಗಳಲ್ಲಿ ಹುಡುಕುತ್ತೇವೆ |
| workflowSteps[1].description | Hybrid search matches your question to the exact Acts and Sections that apply. | हाइब्रिड खोज आपके प्रश्न को सही अधिनियमों और धाराओं से मिलाती है। | ಹೈಬ್ರಿಡ್ ಹುಡುಕಾಟ ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಸರಿಯಾದ ಕಾಯ್ದೆಗಳು ಮತ್ತು ವಿಭಾಗಗಳೊಂದಿಗೆ ಹೊಂದಿಸುತ್ತದೆ. |
| workflowSteps[2].title | Get a plain-language explanation | सरल भाषा में व्याख्या पाएं | ಸರಳ ಭಾಷೆಯಲ್ಲಿ ವಿವರಣೆ ಪಡೆಯಿರಿ |
| workflowSteps[2].description | See what the law means for you, with every citation traceable to its source section. | देखें कि कानून का आपके लिए क्या अर्थ है, हर हवाला उसकी मूल धारा से जुड़ा है। | ಕಾನೂನು ನಿಮಗೆ ಏನು ಅರ್ಥೈಸುತ್ತದೆ ಎಂಬುದನ್ನು ನೋಡಿ, ಪ್ರತಿ ಉಲ್ಲೇಖವನ್ನೂ ಅದರ ಮೂಲ ವಿಭಾಗಕ್ಕೆ ಪತ್ತೆಹಚ್ಚಬಹುದು. |
| workflowSteps[3].title | Explore more tools | और उपकरण देखें | ಇನ್ನಷ್ಟು ಸಾಧನಗಳನ್ನು ಅನ್ವೇಷಿಸಿ |
| workflowSteps[3].description | Draft documents, decode BNS sections, simplify judgments, and more. | दस्तावेज़ तैयार करें, बीएनएस धाराएं समझें, फैसले सरल करें, और भी बहुत कुछ। | ದಾಖಲೆಗಳನ್ನು ರಚಿಸಿ, ಬಿಎನ್‌ಎಸ್ ವಿಭಾಗಗಳನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಿ, ತೀರ್ಪುಗಳನ್ನು ಸರಳಗೊಳಿಸಿ, ಮತ್ತು ಇನ್ನಷ್ಟು. |

### Feature cards

| Key | English source | Hindi | Kannada |
|---|---|---|---|
| featureCardsHeading | What You Can Do Here | यहां आप क्या कर सकते हैं | ಇಲ್ಲಿ ನೀವು ಏನು ಮಾಡಬಹುದು |
| featureCards[search].title | Search | खोज | ಹುಡುಕಾಟ |
| featureCards[search].description | Describe a legal situation and get matched sections with a plain-language explanation. | किसी कानूनी स्थिति का वर्णन करें और सरल भाषा में व्याख्या के साथ मिलती-जुलती धाराएं पाएं। | ಕಾನೂನು ಪರಿಸ್ಥಿತಿಯನ್ನು ವಿವರಿಸಿ ಮತ್ತು ಸರಳ ಭಾಷೆಯ ವಿವರಣೆಯೊಂದಿಗೆ ಹೊಂದಾಣಿಕೆಯಾಗುವ ವಿಭಾಗಗಳನ್ನು ಪಡೆಯಿರಿ. |
| featureCards[drafter].title | Document Generator | दस्तावेज़ जनरेटर | ದಾಖಲೆ ಜನರೇಟರ್ |
| featureCards[drafter].description | Generate rent agreements, notices, and other legal documents from a guided form. | एक निर्देशित फ़ॉर्म से किराया समझौते, नोटिस और अन्य कानूनी दस्तावेज़ तैयार करें। | ಮಾರ್ಗದರ್ಶಿತ ಫಾರ್ಮ್‌ನಿಂದ ಬಾಡಿಗೆ ಒಪ್ಪಂದಗಳು, ಸೂಚನೆಗಳು ಮತ್ತು ಇತರ ಕಾನೂನು ದಾಖಲೆಗಳನ್ನು ರಚಿಸಿ. |
| featureCards[dictionary].title | Dictionary | शब्दकोश | ನಿಘಂಟು |
| featureCards[dictionary].description | Look up legal terms in plain English. | कानूनी शब्दों का सरल अंग्रेज़ी में अर्थ देखें। | ಕಾನೂನು ಪದಗಳ ಅರ್ಥವನ್ನು ಸರಳ ಇಂಗ್ಲಿಷ್‌ನಲ್ಲಿ ನೋಡಿ. |
| featureCards[documents].title | My Documents | मेरे दस्तावेज़ | ನನ್ನ ದಾಖಲೆಗಳು |
| featureCards[documents].description | Revisit your saved searches and uploaded PDFs anytime. | अपनी सहेजी गई खोजें और अपलोड की गई पीडीएफ़ कभी भी दोबारा देखें। | ನಿಮ್ಮ ಉಳಿಸಿದ ಹುಡುಕಾಟಗಳು ಮತ್ತು ಅಪ್‌ಲೋಡ್ ಮಾಡಿದ ಪಿಡಿಎಫ್‌ಗಳನ್ನು ಯಾವಾಗ ಬೇಕಾದರೂ ನೋಡಿ. |
| featureCards[simplifier].title | Case Simplifier | फैसला सरल भाषा में | ಪ್ರಕರಣ ಸರಳೀಕರಣ |
| featureCards[simplifier].description | Paste a court judgment and get a plain-language summary. | किसी अदालती फैसले को पेस्ट करें और सरल भाषा में सारांश पाएं। | ನ್ಯಾಯಾಲಯದ ತೀರ್ಪನ್ನು ಅಂಟಿಸಿ ಮತ್ತು ಸರಳ ಭಾಷೆಯ ಸಾರಾಂಶ ಪಡೆಯಿರಿ. |
| featureCards[bns].title | BNS Decoder | बीएनएस डिकोडर | ಬಿಎನ್‌ಎಸ್ ಡಿಕೋಡರ್ |
| featureCards[bns].description | Look up any Bharatiya Nyaya Sanhita section number and see what it means. | किसी भी भारतीय न्याय संहिता धारा संख्या का अर्थ जानें। | ಯಾವುದೇ ಭಾರತೀಯ ನ್ಯಾಯ ಸಂಹಿತೆ ವಿಭಾಗ ಸಂಖ್ಯೆಯ ಅರ್ಥವನ್ನು ನೋಡಿ. |
| featureCards[quiz].title | Legal IQ Daily | लीगल आईक्यू डेली | ಲೀಗಲ್ ಐಕ್ಯೂ ಡೈಲಿ |
| featureCards[quiz].description | Test your knowledge of Indian law with a daily quiz. | रोज़ाना क्विज़ के साथ भारतीय कानून का अपना ज्ञान परखें। | ದೈನಂದಿನ ಪ್ರಶ್ನಾವಳಿಯೊಂದಿಗೆ ಭಾರತೀಯ ಕಾನೂನಿನ ಬಗ್ಗೆ ನಿಮ್ಮ ಜ್ಞಾನವನ್ನು ಪರೀಕ್ಷಿಸಿ. |

### "The Problem" section

| Key | English source | Hindi | Kannada |
|---|---|---|---|
| problem.eyebrow | The Problem | समस्या | ಸಮಸ್ಯೆ |
| problem.heading | Legal Information Isn't Built For Everyone | कानूनी जानकारी सबके लिए सुलभ नहीं है | ಕಾನೂನು ಮಾಹಿತಿ ಎಲ್ಲರಿಗೂ ಸುಲಭವಾಗಿ ಸಿಗುವುದಿಲ್ಲ |
| problem.body | Most legal information in India is written in dense English legal language, scattered across government sites, PDFs, and outdated portals. For the hundreds of millions of people who read Hindi or Kannada, or who simply aren't trained in legal terminology, that gap makes it hard to know what the law actually says, or what to do next. | भारत में अधिकांश कानूनी जानकारी जटिल अंग्रेज़ी भाषा में लिखी है, जो सरकारी वेबसाइटों, पीडीएफ़ और पुराने पोर्टलों में बिखरी हुई है। करोड़ों हिंदी और कन्नड़ भाषी लोगों के लिए, या जिन्हें कानूनी शब्दावली की जानकारी नहीं है, यह अंतर यह जानना मुश्किल बना देता है कि कानून वास्तव में क्या कहता है, या आगे क्या करना चाहिए। | ಭಾರತದಲ್ಲಿ ಹೆಚ್ಚಿನ ಕಾನೂನು ಮಾಹಿತಿ ಜಟಿಲವಾದ ಇಂಗ್ಲಿಷ್ ಭಾಷೆಯಲ್ಲಿ ಬರೆಯಲಾಗಿದ್ದು, ಸರ್ಕಾರಿ ಜಾಲತಾಣಗಳು, ಪಿಡಿಎಫ್‌ಗಳು ಮತ್ತು ಹಳೆಯ ಪೋರ್ಟಲ್‌ಗಳಲ್ಲಿ ಹರಡಿಕೊಂಡಿದೆ. ಕೋಟ್ಯಂತರ ಹಿಂದಿ ಮತ್ತು ಕನ್ನಡ ಮಾತನಾಡುವವರಿಗೆ, ಅಥವಾ ಕಾನೂನು ಪದಗಳ ಪರಿಚಯವಿಲ್ಲದವರಿಗೆ, ಈ ಅಂತರವು ಕಾನೂನು ನಿಜವಾಗಿ ಏನು ಹೇಳುತ್ತದೆ ಅಥವಾ ಮುಂದೆ ಏನು ಮಾಡಬೇಕು ಎಂಬುದನ್ನು ತಿಳಿಯುವುದನ್ನು ಕಷ್ಟಕರವಾಗಿಸುತ್ತದೆ. |

### "How It Works" section

| Key | English source | Hindi | Kannada |
|---|---|---|---|
| howItWorksSection.eyebrow | How It Works | यह कैसे काम करता है | ಇದು ಹೇಗೆ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತದೆ |
| howItWorksSection.heading | From Question To Explanation | प्रश्न से व्याख्या तक | ಪ್ರಶ್ನೆಯಿಂದ ವಿವರಣೆಯವರೆಗೆ |
| howItWorksSection.body | NyaayaSearch runs a hybrid search, keyword matching combined with a fine-tuned semantic model, over Indian Acts and Sections, then uses an LLM to explain the matched sections in plain language, with guardrails that check every citation against the source text. | न्यायासर्च भारतीय अधिनियमों और धाराओं पर एक हाइब्रिड खोज चलाता है, कीवर्ड मिलान को एक फाइन-ट्यून किए गए सिमेंटिक मॉडल के साथ जोड़कर, फिर एक एलएलएम मिली धाराओं को सरल भाषा में समझाता है, और हर उद्धरण को मूल पाठ से जांचता है। | ನ್ಯಾಯಸರ್ಚ್ ಭಾರತೀಯ ಕಾಯ್ದೆಗಳು ಮತ್ತು ವಿಭಾಗಗಳ ಮೇಲೆ ಹೈಬ್ರಿಡ್ ಹುಡುಕಾಟವನ್ನು ನಡೆಸುತ್ತದೆ, ಕೀವರ್ಡ್ ಹೊಂದಾಣಿಕೆಯನ್ನು ಫೈನ್-ಟ್ಯೂನ್ ಮಾಡಿದ ಸೆಮ್ಯಾಂಟಿಕ್ ಮಾದರಿಯೊಂದಿಗೆ ಸಂಯೋಜಿಸಿ, ನಂತರ ಎಲ್‌ಎಲ್‌ಎಂ ಹೊಂದಾಣಿಕೆಯಾದ ವಿಭಾಗಗಳನ್ನು ಸರಳ ಭಾಷೆಯಲ್ಲಿ ವಿವರಿಸುತ್ತದೆ, ಪ್ರತಿ ಉಲ್ಲೇಖವನ್ನೂ ಮೂಲ ಪಠ್ಯದೊಂದಿಗೆ ಪರಿಶೀಲಿಸುತ್ತದೆ. |

### "Built for Everyone" section

| Key | English source | Hindi | Kannada |
|---|---|---|---|
| everyone.eyebrow | Built For Everyone | सभी के लिए बनाया गया | ಎಲ್ಲರಿಗಾಗಿ ರೂಪಿಸಲಾಗಿದೆ |
| everyone.heading | Support For Every Reader | हर पाठक के लिए सहायता | ಪ್ರತಿಯೊಬ್ಬ ಓದುಗರಿಗೂ ಸಹಾಯ |
| everyone.body | Search, results, and explanations all work in English, Hindi, and Kannada, and voice input lets you ask your question instead of typing it, built for people who aren't comfortable reading legal English. | खोज, परिणाम और व्याख्याएं अंग्रेज़ी, हिंदी और कन्नड़ में काम करती हैं, और वॉइस इनपुट से आप टाइप करने के बजाय अपना प्रश्न बोल सकते हैं, यह उन लोगों के लिए बनाया गया है जिन्हें कानूनी अंग्रेज़ी पढ़ने में सहजता नहीं है। | ಹುಡುಕಾಟ, ಫಲಿತಾಂಶಗಳು ಮತ್ತು ವಿವರಣೆಗಳು ಇಂಗ್ಲಿಷ್, ಹಿಂದಿ ಮತ್ತು ಕನ್ನಡದಲ್ಲಿ ಕಾರ್ಯನಿರ್ವಹಿಸುತ್ತವೆ, ಮತ್ತು ಧ್ವನಿ ಇನ್‌ಪುಟ್‌ನೊಂದಿಗೆ ನೀವು ಟೈಪ್ ಮಾಡುವ ಬದಲು ನಿಮ್ಮ ಪ್ರಶ್ನೆಯನ್ನು ಕೇಳಬಹುದು, ಕಾನೂನು ಇಂಗ್ಲಿಷ್ ಓದಲು ಕಷ್ಟಪಡುವವರಿಗಾಗಿ ಇದನ್ನು ರೂಪಿಸಲಾಗಿದೆ. |

### Footer

| Key | English source | Hindi | Kannada |
|---|---|---|---|
| footerDisclaimer | NyaayaSearch provides legal information, not legal advice. Consult a lawyer for your specific situation. | न्यायासर्च कानूनी जानकारी प्रदान करता है, कानूनी सलाह नहीं। अपनी विशेष स्थिति के लिए किसी वकील से सलाह लें। | ನ್ಯಾಯಸರ್ಚ್ ಕಾನೂನು ಮಾಹಿತಿಯನ್ನು ಒದಗಿಸುತ್ತದೆ, ಕಾನೂನು ಸಲಹೆಯನ್ನಲ್ಲ. ನಿಮ್ಮ ನಿರ್ದಿಷ್ಟ ಪರಿಸ್ಥಿತಿಗಾಗಿ ವಕೀಲರನ್ನು ಸಂಪರ್ಕಿಸಿ. |

Note: the app's brand name is transliterated two different ways across the two languages here ("न्यायासर्च" in Hindi copy vs. "ನ್ಯಾಯಸರ್ಚ್" in Kannada copy) - both are reasonable transliterations of "NyaayaSearch," but teammates should confirm whether one consistent transliteration is preferred everywhere it appears in running Hindi/Kannada text (the brand name itself is never translated, only how it's written in Devanagari/Kannada script within a sentence).

## `src/navContent.js` - Top bar, bottom nav, More menu

| Key | English source | Hindi | Kannada |
|---|---|---|---|
| languageSwitcherLabel (aria-label) | Interface language | इंटरफ़ेस भाषा | ಇಂಟರ್ಫೇಸ್ ಭಾಷೆ |
| themeToggleToDark (aria-label) | Switch to dark mode | डार्क मोड में बदलें | ಡಾರ್ಕ್ ಮೋಡ್‌ಗೆ ಬದಲಿಸಿ |
| themeToggleToLight (aria-label) | Switch to light mode | लाइट मोड में बदलें | ಲೈಟ್ ಮೋಡ್‌ಗೆ ಬದಲಿಸಿ |
| primaryNavLabel (aria-label) | Primary | मुख्य नेविगेशन | ಮುಖ್ಯ ನ್ಯಾವಿಗೇಷನ್ |
| moreMenuLabel (aria-label) | More options | अधिक विकल्प | ಇನ್ನಷ್ಟು ಆಯ್ಕೆಗಳು |
| nav.home | Home | होम | ಮುಖಪುಟ |
| nav.search | Search | खोज | ಹುಡುಕಾಟ |
| nav.bns | BNS Decoder | बीएनएस डिकोडर | ಬಿಎನ್‌ಎಸ್ ಡಿಕೋಡರ್ |
| nav.documents | My Documents | मेरे दस्तावेज़ | ನನ್ನ ದಾಖಲೆಗಳು |
| nav.more | More | अधिक | ಇನ್ನಷ್ಟು |
| more.drafter | Document Generator | दस्तावेज़ जनरेटर | ದಾಖಲೆ ಜನರೇಟರ್ |
| more.dictionary | Dictionary | शब्दकोश | ನಿಘಂಟು |
| more.simplifier | Case Simplifier | फैसला सरल भाषा में | ಪ್ರಕರಣ ಸರಳೀಕರಣ |
| more.quiz | Legal IQ Daily | लीगल आईक्यू डेली | ಲೀಗಲ್ ಐಕ್ಯೂ ಡೈಲಿ |

## `src/components/EmergencyButton.jsx` - Floating emergency button

| Key | English source | Hindi | Kannada |
|---|---|---|---|
| full (label + aria-label) | Emergency Help | आपात सहायता | ತುರ್ತು सहायता |

## `src/emergencyContent.js` & `src/components/EmergencyTab.jsx` - Emergency tab

| Key | English source | Hindi | Kannada |
|---|---|---|---|
| call112 | Call 112 | 112 पर कॉल करें | 112 ಕ್ಕೆ ಕರೆ ಮಾಡಿ |
| heading | Emergency and Legal Aid Resources | इमरजेंसी और कानूनी सहायता नंबर | ತುರ್ತು ಮತ್ತು ಕಾನೂನು ನೆರವಿನ ಸಂಖ್ಯೆಗಳು |
| intro | If you need urgent help, contact these resources directly. | अगर आपको तुरंत मदद चाहिए, तो सीधे इन नंबरों पर संपर्क करें। | ನಿಮಗೆ ತಕ್ಷಣದ ಸಹಾಯ ಬೇಕಾದರೆ, ಈ ಸಂಖ್ಯೆಗಳನ್ನು ನೇರವಾಗಿ ಸಂಪರ್ಕಿಸಿ. |
| policeTitle | Police Emergency | पुलिस आपातकालीन सेवा | ಪೊಲೀಸ್ ತುರ್ತು ಸೇವೆ |
| policeDesc | National emergency helpline for police assistance. | पुलिस की मदद के लिए राष्ट्रीय इमरजेंसी नंबर। | ಪೊಲೀಸ್ ನೆರವಿಗಾಗಿ ರಾಷ್ಟ್ರೀಯ ತುರ್ತು ಸಹಾಯವಾಣಿ. |
| womenTitle | Women Helpline | महिला हेल्पलाइन | ಮಹಿಳಾ ಸಹಾಯವಾಣಿ |
| womenDesc | National helpline for women in distress. | संकट में फंसी महिलाओं के लिए राष्ट्रीय हेल्पलाइन। | ಸಂಕಷ್ಟದಲ್ಲಿರುವ ಮಹಿಳೆಯರಿಗಾಗಿ ರಾಷ್ಟ್ರೀಯ ಸಹಾಯವಾಣಿ. |
| domesticTitle | Domestic Violence Helpline | घरेलू हिंसा हेल्पलाइन | ಕೌಟುಂಬಿಕ ದೌರ್ಜನ್ಯ ಸಹಾಯವಾಣಿ |
| domesticDesc | National helpline for domestic violence support. | घरेलू हिंसा से पीड़ित लोगों की मदद के लिए राष्ट्रीय हेल्पलाइन। | ಕೌಟುಂಬಿಕ ದೌರ್ಜನ್ಯಕ್ಕೆ ಒಳಗಾದವರ ನೆರವಿಗಾಗಿ ರಾಷ್ಟ್ರೀಯ ಸಹಾಯವಾಣಿ. |
| childTitle | Child Helpline | चाइल्ड हेल्पलाइन (बच्चों की मदद) | ಮಕ್ಕಳ ಸಹಾಯವಾಣಿ |
| childDesc | National helpline for children in need of help. | मदद की जरूरत वाले बच्चों के लिए राष्ट्रीय हेल्पलाइन। | ನೆರವು ಬೇಕಾದ ಮಕ್ಕಳಿಗಾಗಿ ರಾಷ್ಟ್ರೀಯ ಸಹಾಯವಾಣಿ. |
| nalsaTitle | National Legal Services Authority (NALSA) | राष्ट्रीय कानूनी सेवा प्राधिकरण (NALSA) | ರಾಷ್ಟ್ರೀಯ ಕಾನೂನು ಸೇವೆಗಳ ಪ್ರಾಧಿಕಾರ (NALSA) |
| nalsaDesc | Free legal aid and services for eligible citizens. | जरूरतमंद नागरिकों के लिए मुफ्त कानूनी मदद और सेवाएं। | ಅರ್ಹ ನಾಗರಿಕರಿಗೆ ಉಚಿತ ಕಾನೂನು ನೆರವು ಮತ್ತು ಸೇವೆಗಳು. |
| consumerTitle | Consumer Helpline | ग्राहक हेल्पलाइन | ಗ್ರಾಹಕ ಸಹಾಯವಾಣಿ |
| consumerDesc | National Consumer Helpline for consumer grievances. | खरीदे गए सामान या सेवा से जुड़ी शिकायतों के लिए राष्ट्रीय हेल्पलाइन। | ಗ್ರಾಹಕ ಹಕ್ಕುಗಳು ಮತ್ತು ದೂರುಗಳಿಗಾಗಿ ರಾಷ್ಟ್ರೀಯ ಸಹಾಯವಾಣಿ. |
| cyberTitle | Cyber Crime Helpline | साइबर क्राइम हेल्पलाइन | ಸೈಬರ್ ಕ್ರೈಮ್ ಸಹಾಯವಾಣಿ |
| cyberDesc | National helpline to report cyber crimes and online fraud. | ऑनलाइन धोखाधड़ी और साइबर अपराध की रिपोर्ट करने के लिए हेल्पलाइन। | ಆನ್‌ಲೈನ್ ವಂಚನೆ ಮತ್ತು ಸೈಬರ್ ಅಪರಾಧ ದೂರುಗಳಿಗಾಗಿ ಸಹಾಯವಾಣಿ. |
| seniorTitle | Senior Citizen Helpline | वरिष्ठ नागरिक हेल्पलाइन | ಹಿರಿಯ ನಾಗರಿಕರ ಸಹಾಯವಾಣಿ |
| seniorDesc | National helpline for elderly citizens needing assistance. | बुजुर्ग नागरिकों की सहायता के लिए राष्ट्रीय हेल्पलाइन। | ಹಿರಿಯ ನಾಗರಿಕರ ಸಹಾಯ ಮತ್ತು ನೆರವಿಗಾಗಿ ರಾಷ್ಟ್ರೀಯ ಸಹಾಯವಾಣಿ. |
| disclaimer | These are general national helpline numbers. In an emergency, always contact local police or emergency services directly. | ये सामान्य राष्ट्रीय हेल्पलाइन नंबर हैं। किसी भी आपात स्थिति में, हमेशा स्थानीय पुलिस या नजदीकी आपातकालीन सेवा से सीधे संपर्क करें। | ಇವು ಸಾಮಾನ್ಯ ರಾಷ್ಟ್ರೀಯ ಸಹಾಯವಾಣಿ ಸಂಖ್ಯೆಗಳು. ತುರ್ತು ಸಂದರ್ಭದಲ್ಲಿ, ಯಾವಾಗಲೂ ಸ್ಥಳೀಯ ಪೊಲೀಸರನ್ನು ಅಥವಾ ಹತ್ತಿರದ ತುರ್ತು ಸೇವೆಯನ್ನು ನೇರವಾಗಿ ಸಂಪರ್ಕಿಸಿ। |

## `src/dictionaryContent.js` & `src/components/DictionaryTab.jsx` - Legal Dictionary tab

| Key | English source | Hindi | Kannada |
|---|---|---|---|
| heading | Legal Dictionary | कानूनी शब्दकोश | ಕಾನೂನು ನಿಘಂಟು |
| srLabel | Legal term to look up | खोजने के लिए कानूनी शब्द | ಹುಡುಕಬೇಕಾದ ಕಾನೂನು ಪದ |
| placeholder | Look up a legal term, e.g. 'cognizable offence' | कोई कानूनी शब्द खोजें, जैसे 'cognizable offence' | ಕಾನೂನು ಪದವನ್ನು ಹುಡುಕಿ, ಉದಾ: 'cognizable offence' |
| buttonLookingUp | Looking up... | खोज रहे हैं... | ಹುಡುಕಲಾಗುತ್ತಿದೆ... |
| buttonDefine | Define | मतलब देखें | ಅರ್ಥ ನೋಡಿ |
| notFoundFallback | No definition found. | इस शब्द का मतलब नहीं मिला। | ಈ ಪದದ ಅರ್ಥ ಸಿಗಲಿಲ್ಲ. |
| errDefault | Something went wrong looking up this term. | इस शब्द को खोजने में कुछ समस्या आई। | ಈ ಪದವನ್ನು ಹುಡುಕುವಲ್ಲಿ ಏನೋ ತೊಂದರೆಯಾಗಿದೆ. |
| errNetwork | Could not reach the server. Please try again. | सर्वर से संपर्क नहीं हो पाया। फिर से कोशिश करें। | ಸರ್ವರ್ ಸಂಪರ್ಕಿಸಲು ಸಾಧ್ಯವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಪ್ರಯತ್ನಿಸಿ. |

## Not yet translated (English-only, out of scope for this pass)

These strings still show in English regardless of the language setting -
flagging so nothing is assumed translated that isn't. This was a restyle
pass (Batch A: Search, BNS Decoder, My Documents); these tabs' *existing*
translated strings (via `t()` / `UI_STRINGS`) still work exactly as before,
only the strings below were never wired to a language at all.

### `src/components/SearchTab.jsx`
- Input placeholder: "Describe your legal situation, e.g. 'landlord not returning deposit'"
- Screen-reader label: "Describe your legal situation"
- Mic button tooltip (`title` attribute): "Search by voice"
- The 4 example-query chips: "Landlord not returning deposit", "Police arrest without warrant", "How to file an RTI request", "Consumer complaint for defective product"

### `src/components/BnsTab.jsx`
- Heading: "BNS Decoder"
- Intro line: "Enter a Bharatiya Nyaya Sanhita (BNS) section number to see what it says, explained in plain language."
- Screen-reader label: "BNS section number"
- Input placeholder: "e.g. 103"
- Button: "Looking up..." / "Decode Section"
- Citation tag label: "Section" (hardcoded here, not routed through the same translation as Search's "Section" label)
- "Original text:" caption above the source legal text

### `src/components/DocumentsTab.jsx`
- Heading: "Ask about your own document"
- Screen-reader label: "Upload a PDF document"
- Loading text: "Reading and summarizing your document..."
- Section title: "Important Dates and Deadlines"
- Screen-reader label: "Ask a question about this document"
- Input placeholder: "Ask a question about this document..."
- Button: "Asking..." / "Ask"
- Error fallback text shown inline (e.g. "Could not upload the document...", "Something went wrong asking about the document.", "Could not reach the server...")

### `src/components/DrafterTab.jsx`
- Heading: "Legal Document Generator"
- Label: "What document do you want to create?"
- Subtitle template: "Let's create your {document type}"
- Fallback-form label: "This document type doesn't have a detailed form yet. Enter any details you'd like included, one per line (e.g. "name: John Doe") - anything you leave out will appear as a blank line to fill in later."
- Fallback textarea placeholder: "e.g. / name: John Doe / date: 2026-01-01"
- Select placeholder option: "Select..."
- Button: "Generating..." / "Generate Document"
- Button: "Download as Word"
- `src/documentSchemas.js` - every document type's label, section titles, and field labels/placeholders/options (many; not enumerated here since it's most of the file's content). The AI-generated document text itself is produced by the backend in English regardless of `uiLanguage`.

### `src/components/SimplifierTab.jsx`
- Heading: "Case Simplifier"
- Intro line: "Paste a court judgment, order, or legal case text to get a plain-language explanation."
- Screen-reader label: "Case text to simplify"
- Textarea placeholder: "Paste the case text here..."
- Button: "Simplifying..." / "Simplify Case"
- Result heading: "Explanation" (hardcoded here, not routed through the same translation as Search's "Explanation" heading)
- Error fallback text: "Could not simplify this case. Please try again.", "Could not reach the server. Make sure the backend is running."

### `src/components/QuizTab.jsx` and `src/quizData.js`
- Heading: "Legal IQ Daily"
- "Question X of Y" progress label
- Every question, its options, and its explanation (in `quizData.js`; not enumerated here)
- Button: "Next Question" / "See Results"
- Results text: "You scored X out of Y"
- Button: "Try Again"

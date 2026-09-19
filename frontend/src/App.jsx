import { useState, useRef } from "react";
import "./App.css";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";

const API_URL = "http://127.0.0.1:8000";

const LANGUAGE_LABELS = {
  en: "English",
  hi: "\u0939\u093F\u0902\u0926\u0940",
  kn: "\u0C95\u0CA8\u0CCD\u0CA8\u0CA1",
};

const ALL_LANGUAGES = ["en", "hi", "kn"];

function getConfidenceLabel(score, topScore) {
  const ratio = topScore > 0 ? score / topScore : 0;
  if (ratio >= 0.95) return { label: "Strong match", className: "confidence-strong" };
  if (ratio >= 0.8) return { label: "Good match", className: "confidence-good" };
  return { label: "Possible match", className: "confidence-weak" };
}

function isOverallLowConfidence(topScore) {
  return topScore < 0.75;
}

async function extractErrorMessage(response, fallback) {
  try {
    const data = await response.json();
    if (data.detail) return data.detail;
  } catch (e) {
    // response wasn't JSON, fall through to fallback
  }
  return fallback;
}

function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState([]);
  const [explanation, setExplanation] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const recognitionRef = useRef(null);

  const [currentLanguage, setCurrentLanguage] = useState("en");
  const [explanationCache, setExplanationCache] = useState({});
  const [translating, setTranslating] = useState(false);

  const [uploadedDoc, setUploadedDoc] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [docQuestion, setDocQuestion] = useState("");
  const [docAnswer, setDocAnswer] = useState("");
  const [docAsking, setDocAsking] = useState(false);

  const [dictTerm, setDictTerm] = useState("");
  const [dictDefinition, setDictDefinition] = useState("");
  const [dictLoading, setDictLoading] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) {
      setError("Please enter a question or describe your situation to search.");
      return;
    }

    setLoading(true);
    setError(null);
    setExplanation("");
    setResults([]);
    setExplanationCache({});

    try {
      const response = await fetch(`${API_URL}/explain`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k: 5 }),
      });

      if (!response.ok) {
        const message = await extractErrorMessage(
          response,
          "Something went wrong. Make sure the backend server is running."
        );
        setError(message);
        return;
      }

      const data = await response.json();
      setResults(data.results || []);
      setExplanation(data.explanation || "");

      const detectedLang = data.language || "en";
      setCurrentLanguage(detectedLang);
      setExplanationCache({ [detectedLang]: data.explanation || "" });
    } catch (err) {
      setError("Could not reach the server. Make sure the backend is running.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleLanguageSwitch = async (targetLang) => {
    if (targetLang === currentLanguage) return;

    if (explanationCache[targetLang]) {
      setExplanation(explanationCache[targetLang]);
      setCurrentLanguage(targetLang);
      return;
    }

    setTranslating(true);
    try {
      const response = await fetch(`${API_URL}/translate-explanation`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: explanation, target_language: targetLang }),
      });

      if (!response.ok) {
        const message = await extractErrorMessage(response, "Could not translate the explanation.");
        setError(message);
        return;
      }

      const data = await response.json();
      setExplanation(data.translation);
      setCurrentLanguage(targetLang);
      setExplanationCache((prev) => ({ ...prev, [targetLang]: data.translation }));
    } catch (err) {
      setError("Could not reach the server to translate.");
      console.error(err);
    } finally {
      setTranslating(false);
    }
  };

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError("Voice input is not supported in this browser. Try Chrome.");
      return;
    }

    if (recognitionRef.current) {
      recognitionRef.current.stop();
      recognitionRef.current = null;
      setIsListening(false);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => {
      setIsListening(false);
      recognitionRef.current = null;
    };
    recognition.onerror = () => {
      setIsListening(false);
      recognitionRef.current = null;
      setError("Could not hear you. Please try again.");
    };
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setQuery(transcript);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const speakExplanation = () => {
    if (!explanation) return;

    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
      return;
    }

    const cleanText = explanation
      .replace(/\*\*/g, "")
      .replace(/\|/g, " ")
      .replace(/#+/g, "")
      .replace(/-{2,}/g, "");

    const utterance = new SpeechSynthesisUtterance(cleanText);
    utterance.lang = currentLanguage === "hi" ? "hi-IN" : currentLanguage === "kn" ? "kn-IN" : "en-IN";
    utterance.onend = () => setIsSpeaking(false);
    utterance.onerror = () => setIsSpeaking(false);

    setIsSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    setUploading(true);
    setError(null);
    setUploadedDoc(null);
    setDocAnswer("");
    setDocQuestion("");

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_URL}/upload-pdf`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const message = await extractErrorMessage(
          response,
          "Could not upload the document. Make sure the backend server is running."
        );
        setError(message);
        return;
      }

      const data = await response.json();
      setUploadedDoc(data);
    } catch (err) {
      setError("Could not reach the server. Make sure the backend is running.");
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const handleAskDocument = async (e) => {
    e.preventDefault();
    if (!docQuestion.trim() || !uploadedDoc) return;

    setDocAsking(true);
    setDocAnswer("");

    try {
      const response = await fetch(`${API_URL}/ask-document`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          document_id: uploadedDoc.document_id,
          question: docQuestion,
        }),
      });

      if (!response.ok) {
        const message = await extractErrorMessage(response, "Something went wrong asking about the document.");
        setDocAnswer(message);
        return;
      }

      const data = await response.json();
      setDocAnswer(data.answer || "No answer returned.");
    } catch (err) {
      setDocAnswer("Could not reach the server. Please try again.");
      console.error(err);
    } finally {
      setDocAsking(false);
    }
  };

  const handleDefine = async (e) => {
    e.preventDefault();
    if (!dictTerm.trim()) return;

    setDictLoading(true);
    setDictDefinition("");

    try {
      const response = await fetch(`${API_URL}/define`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ term: dictTerm }),
      });

      if (!response.ok) {
        const message = await extractErrorMessage(response, "Something went wrong looking up this term.");
        setDictDefinition(message);
        return;
      }

      const data = await response.json();
      setDictDefinition(data.definition || "No definition found.");
    } catch (err) {
      setDictDefinition("Could not reach the server. Please try again.");
      console.error(err);
    } finally {
      setDictLoading(false);
    }
  };

  const topScore = results.length > 0 ? results[0].hybrid_score : 0;
  const showLowConfidenceWarning = results.length > 0 && isOverallLowConfidence(topScore);
  const otherLanguages = ALL_LANGUAGES.filter((lang) => lang !== currentLanguage);

  return (
    <div className="app">
      <header className="header">
        <h1>NyaayaSearch</h1>
        <p className="tagline">Understand Indian law in plain language</p>
      </header>

      <div className="dictionary-section">
        <h2>Legal Dictionary</h2>
        <form className="dict-form" onSubmit={handleDefine}>
          <input
            type="text"
            className="search-input"
            placeholder="Look up a legal term, e.g. 'cognizable offence'"
            value={dictTerm}
            onChange={(e) => setDictTerm(e.target.value)}
          />
          <button type="submit" className="search-button" disabled={dictLoading}>
            {dictLoading ? "Looking up..." : "Define"}
          </button>
        </form>
        {dictDefinition && <div className="dict-definition">{dictDefinition}</div>}
      </div>

      <div className="upload-section">
        <h2>Ask about your own document</h2>
        <input type="file" accept="application/pdf" onChange={handleFileUpload} />
        {uploading && <div className="loading">Reading and summarizing your document...</div>}

        {uploadedDoc && (
          <div className="document-card">
            <div className="document-filename">{uploadedDoc.filename}</div>
            <div className="document-summary">{uploadedDoc.summary}</div>

            {uploadedDoc.dates && uploadedDoc.dates.length > 0 && (
              <div className="dates-section">
                <div className="dates-title">Important Dates and Deadlines</div>
                {uploadedDoc.dates.map((d, i) => (
                  <div className="date-item" key={i}>
                    <span className="date-value">{d.value}</span>
                    <span className="date-description">{d.description}</span>
                  </div>
                ))}
              </div>
            )}

            {uploadedDoc.document_id && (
              <form className="doc-question-form" onSubmit={handleAskDocument}>
                <input
                  type="text"
                  className="search-input"
                  placeholder="Ask a question about this document..."
                  value={docQuestion}
                  onChange={(e) => setDocQuestion(e.target.value)}
                />
                <button type="submit" className="search-button" disabled={docAsking}>
                  {docAsking ? "Asking..." : "Ask"}
                </button>
              </form>
            )}

            {docAnswer && <div className="document-answer">{docAnswer}</div>}
          </div>
        )}
      </div>

      <hr className="section-divider" />

      <form className="search-form" onSubmit={handleSearch}>
        <input
          type="text"
          className="search-input"
          placeholder="Describe your legal situation, e.g. 'landlord not returning deposit'"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button
          type="button"
          className={`mic-button ${isListening ? "listening" : ""}`}
          onClick={startListening}
          title="Search by voice"
        >
          Mic
        </button>
        <button type="submit" className="search-button" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {isListening && <div className="listening-indicator">Listening... (click mic again to stop)</div>}

      {error && <div className="error">{error}</div>}

      {loading && (
        <div className="loading">
          Searching legal database and generating explanation...
        </div>
      )}

      {showLowConfidenceWarning && (
        <div className="low-confidence-warning">
          We're not fully confident in these results. Try rephrasing your question
          with more specific details (e.g. mention the situation, the people involved,
          or what you're trying to do) for a better match. Showing our best guess below.
        </div>
      )}

      {explanation && (
        <div className="explanation-card">
          <div className="explanation-header">
            <h2>Explanation</h2>
            <div className="explanation-controls">
              <div className="language-toggle">
                {otherLanguages.map((lang) => (
                  <button
                    key={lang}
                    className="language-toggle-button"
                    onClick={() => handleLanguageSwitch(lang)}
                    disabled={translating}
                  >
                    {LANGUAGE_LABELS[lang]}
                  </button>
                ))}
              </div>
              <button className="listen-button" onClick={speakExplanation}>
                {isSpeaking ? "Stop" : "Listen"}
              </button>
            </div>
          </div>
          {translating ? (
            <div className="loading">Translating...</div>
          ) : (
            <div className="explanation-text"><ReactMarkdown remarkPlugins={[remarkGfm]}>{explanation}</ReactMarkdown></div>
          )}
        </div>
      )}

      {results.length > 0 && (
        <div className="results-section">
          <h2>Sources</h2>
          {results.map((r, i) => {
            const confidence = getConfidenceLabel(r.hybrid_score, topScore);
            return (
              <div className="result-card" key={i}>
                <div className="result-header">
                  <span className="act-name">{r.act_name}</span>
                  <span className="section-number">Section {r.section_number}</span>
                </div>
                <div className={`confidence-badge ${confidence.className}`}>
                  {confidence.label}
                </div>

                {r.matched_terms && r.matched_terms.length > 0 && (
                  <div className="matched-terms">
                    <span className="matched-terms-label">Why this matched: </span>
                    {r.matched_terms.map((term, k) => (
                      <span className="matched-term-tag" key={k}>{term}</span>
                    ))}
                  </div>
                )}

                <div className="section-title">{r.section_title}</div>
                <div className="legal-text">{r.legal_text}</div>

                {r.related_cases && r.related_cases.length > 0 && (
                  <div className="related-cases">
                    <div className="related-cases-title">Related Supreme Court Cases</div>
                    {r.related_cases.map((c, j) => (
                      <div className="case-item" key={j}>
                        <span className="case-title">{c.title}</span>
                        <span className="case-meta">{c.court} · {c.decision_date}</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export default App;

import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { API_URL, LANGUAGE_LABELS, ALL_LANGUAGES, MAX_HISTORY } from "../constants";
import {
  getConfidenceLabel,
  isOverallLowConfidence,
  extractErrorMessage,
  loadHistory,
  saveHistory,
  loadSavedResults,
  persistSavedResults,
  t,
} from "../utils";

function SearchTab({ setError, uiLanguage, onLanguageChange }) {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState([]);
  const [explanation, setExplanation] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const recognitionRef = useRef(null);

  const [currentLanguage, setCurrentLanguage] = useState("en");
  const [explanationCache, setExplanationCache] = useState({});
  const [translating, setTranslating] = useState(false);

  const [searchHistory, setSearchHistory] = useState(function () { return loadHistory(); });
  const [savedResults, setSavedResults] = useState(function () { return loadSavedResults(); });

  const addToHistory = function (searchedQuery) {
    setSearchHistory(function (prev) {
      const withoutDupe = prev.filter(function (q) { return q !== searchedQuery; });
      const updated = [searchedQuery].concat(withoutDupe).slice(0, MAX_HISTORY);
      saveHistory(updated);
      return updated;
    });
  };

  const clearHistory = function () {
    setSearchHistory([]);
    saveHistory([]);
  };

  const isCurrentResultSaved = savedResults.some(function (r) { return r.query === query && r.explanation === explanation; });

  const handleSaveResult = function () {
    if (!query || !explanation) return;
    const newItem = {
      id: Date.now(),
      query: query,
      explanation: explanation,
      language: currentLanguage,
      savedAt: new Date().toISOString(),
    };
    setSavedResults(function (prev) {
      const updated = [newItem].concat(prev);
      persistSavedResults(updated);
      return updated;
    });
  };

  const handleDeleteSaved = function (id) {
    setSavedResults(function (prev) {
      const updated = prev.filter(function (r) { return r.id !== id; });
      persistSavedResults(updated);
      return updated;
    });
  };

  const handleViewSaved = function (item) {
    setQuery(item.query);
    setExplanation(item.explanation);
    setCurrentLanguage(item.language || "en");
    setExplanationCache({ [item.language || "en"]: item.explanation });
    setResults([]);
  };

  const runSearch = async function (searchQuery) {
    if (!searchQuery.trim()) {
      setError("Please enter a question or describe your situation to search.");
      return;
    }

    setLoading(true);
    setError(null);
    setExplanation("");
    setResults([]);
    setExplanationCache({});

    try {
      const response = await fetch(API_URL + "/explain", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery, top_k: 5 }),
      });

      if (!response.ok) {
        const message = await extractErrorMessage(response, "Something went wrong. Make sure the backend server is running.");
        setError(message);
        return;
      }

      const data = await response.json();
      setResults(data.results || []);
      setExplanation(data.explanation || "");

      const detectedLang = data.language || "en";
      setCurrentLanguage(detectedLang);
      setExplanationCache({ [detectedLang]: data.explanation || "" });

      addToHistory(searchQuery);
    } catch (err) {
      setError("Could not reach the server. Make sure the backend is running.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async function (e) {
    e.preventDefault();
    await runSearch(query);
  };

  const handleHistoryClick = function (historyQuery) {
    setQuery(historyQuery);
    runSearch(historyQuery);
  };

  const handleLanguageSwitch = async function (targetLang) {
    if (targetLang === currentLanguage) return;

    if (explanationCache[targetLang]) {
      setExplanation(explanationCache[targetLang]);
      setCurrentLanguage(targetLang);
      return;
    }

    setTranslating(true);
    try {
      const response = await fetch(API_URL + "/translate-explanation", {
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
      setExplanationCache(function (prev) {
        const copy = Object.assign({}, prev);
        copy[targetLang] = data.translation;
        return copy;
      });
    } catch (err) {
      setError("Could not reach the server to translate.");
      console.error(err);
    } finally {
      setTranslating(false);
    }
  };

  useEffect(function () {
    if (typeof onLanguageChange === "function") onLanguageChange(currentLanguage);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [currentLanguage]);

  useEffect(function () {
    if (!uiLanguage || uiLanguage === currentLanguage || !explanation) return;
    const timer = setTimeout(function () { handleLanguageSwitch(uiLanguage); }, 0);
    return function () { clearTimeout(timer); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [uiLanguage]);

  const startListening = function () {
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

    recognition.onstart = function () { setIsListening(true); };
    recognition.onend = function () {
      setIsListening(false);
      recognitionRef.current = null;
    };
    recognition.onerror = function () {
      setIsListening(false);
      recognitionRef.current = null;
      setError("Could not hear you. Please try again.");
    };
    recognition.onresult = function (event) {
      const transcript = event.results[0][0].transcript;
      setQuery(transcript);
    };

    recognitionRef.current = recognition;
    recognition.start();
  };

  const speakExplanation = function () {
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
    utterance.onend = function () { setIsSpeaking(false); };
    utterance.onerror = function () { setIsSpeaking(false); };

    setIsSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  const topScore = results.length > 0 ? results[0].hybrid_score : 0;
  const showLowConfidenceWarning = results.length > 0 && isOverallLowConfidence(topScore);
  const otherLanguages = ALL_LANGUAGES.filter(function (lang) { return lang !== currentLanguage; });

  return (
    <div>
      <form className="search-form" onSubmit={handleSearch}>
        <label className="sr-only" htmlFor="search-query">Describe your legal situation</label>
        <input
          id="search-query"
          type="text"
          className="search-input"
          placeholder="Describe your legal situation, e.g. 'landlord not returning deposit'"
          value={query}
          onChange={function (e) { setQuery(e.target.value); }}
        />
        <button
          type="button"
          className={"mic-button" + (isListening ? " listening" : "")}
          onClick={startListening}
          title="Search by voice"
        >
          {t(currentLanguage, "mic")}
        </button>
        <button type="submit" className="search-button" disabled={loading}>
          {loading ? t(currentLanguage, "searching") : t(currentLanguage, "search")}
        </button>
      </form>

      {searchHistory.length === 0 && !explanation && !loading && (
        <div className="example-queries">
          <span className="example-queries-label">{t(currentLanguage, "tryAsking")}</span>
          <button className="example-chip" onClick={function () { setQuery("landlord not returning deposit"); runSearch("landlord not returning deposit"); }}>Landlord not returning deposit</button>
          <button className="example-chip" onClick={function () { setQuery("police arrest without warrant"); runSearch("police arrest without warrant"); }}>Police arrest without warrant</button>
          <button className="example-chip" onClick={function () { setQuery("how to file an RTI request"); runSearch("how to file an RTI request"); }}>How to file an RTI request</button>
          <button className="example-chip" onClick={function () { setQuery("consumer complaint for defective product"); runSearch("consumer complaint for defective product"); }}>Consumer complaint for defective product</button>
        </div>
      )}

      {searchHistory.length > 0 && (
        <div className="search-history">
          <span className="search-history-label">{t(currentLanguage, "recent")}</span>
          {searchHistory.map(function (h, i) {
            return (
              <button key={i} className="history-chip" onClick={function () { handleHistoryClick(h); }}>
                {h.length > 40 ? h.slice(0, 40) + "..." : h}
              </button>
            );
          })}
          <button className="history-clear" onClick={clearHistory}>{t(currentLanguage, "clear")}</button>
        </div>
      )}

      {savedResults.length > 0 && (
        <div className="saved-results-section">
          <h2>{t(currentLanguage, "savedResults")}</h2>
          {savedResults.map(function (item) {
            return (
              <div className="saved-result-card" key={item.id}>
                <div className="saved-result-header">
                  <button type="button" className="saved-result-query" onClick={function () { handleViewSaved(item); }}>
                    {item.query}
                  </button>
                  <button className="saved-result-delete" onClick={function () { handleDeleteSaved(item.id); }}>{t(currentLanguage, "delete")}</button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {isListening && <div className="listening-indicator">{t(currentLanguage, "listeningIndicator")}</div>}

      {loading && (
        <div className="loading">{t(currentLanguage, "searchingFull")}</div>
      )}

      {showLowConfidenceWarning && (
        <div className="low-confidence-warning">
          {t(currentLanguage, "lowConfidenceWarning")}
        </div>
      )}

      {explanation && (
        <div className="explanation-card">
          <div className="explanation-header">
            <h2>{t(currentLanguage, "explanation")}</h2>
            <div className="explanation-controls">
              <div className="language-toggle">
                {otherLanguages.map(function (lang) {
                  return (
                    <button
                      key={lang}
                      className="language-toggle-button"
                      onClick={function () { handleLanguageSwitch(lang); }}
                      disabled={translating}
                    >
                      {LANGUAGE_LABELS[lang]}
                    </button>
                  );
                })}
              </div>
              <button className="listen-button" onClick={speakExplanation}>
                {isSpeaking ? t(currentLanguage, "stop") : t(currentLanguage, "listen")}
              </button>
              <button className="save-button" onClick={handleSaveResult} disabled={isCurrentResultSaved}>
                {isCurrentResultSaved ? t(currentLanguage, "saved") : t(currentLanguage, "save")}
              </button>
            </div>
          </div>
          {translating ? (
            <div className="loading">{t(currentLanguage, "translating")}</div>
          ) : (
            <div className="explanation-text"><ReactMarkdown remarkPlugins={[remarkGfm]}>{explanation}</ReactMarkdown></div>
          )}
        </div>
      )}

      {results.length > 0 && (
        <div className="results-section">
          <h2>{t(currentLanguage, "sources")}</h2>
          {results.map(function (r, i) {
            const confidence = getConfidenceLabel(r.hybrid_score, topScore, currentLanguage);
            return (
              <div className="result-card" key={i}>
                <div className="result-header">
                  <span className="act-name">{r.act_name}</span>
                  <span className="citation-tag">
                    <span className="citation-tag-label">{t(currentLanguage, "section")}</span>
                    <span className="citation-tag-number">{r.section_number}</span>
                  </span>
                </div>
                <div className={"confidence-badge " + confidence.className}>{confidence.label}</div>

                {r.matched_terms && r.matched_terms.length > 0 && (
                  <div className="matched-terms">
                    <span className="matched-terms-label">{t(currentLanguage, "whyThisMatched")} </span>
                    {r.matched_terms.map(function (term, k) {
                      return <span className="matched-term-tag" key={k}>{term}</span>;
                    })}
                  </div>
                )}

                <div className="section-title">{r.section_title}</div>
                <div className="legal-text">{r.legal_text}</div>

                {r.related_cases && r.related_cases.length > 0 && (
                  <div className="related-cases">
                    <div className="related-cases-title">{t(currentLanguage, "relatedCases")}</div>
                    {r.related_cases.map(function (c, j) {
                      return (
                        <div className="case-item" key={j}>
                          <span className="case-title">{c.title}</span>
                          <span className="case-meta">{c.court} - {c.decision_date}</span>
                        </div>
                      );
                    })}
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

export default SearchTab;

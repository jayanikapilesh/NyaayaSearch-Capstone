import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { API_URL, LANGUAGE_LABELS, ALL_LANGUAGES, MAX_HISTORY } from "../constants";
import {
  getConfidenceLabel,
  extractErrorMessage,
  loadHistory,
  saveHistory,
  loadSavedResults,
  persistSavedResults,
  t,
} from "../utils";

function SearchTab({ setError, uiLanguage, onLanguageChange }) {
  const [query, setQuery] = useState("");
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [loadingExplanation, setLoadingExplanation] = useState(false);
  const [results, setResults] = useState([]);
  const [lowConfidence, setLowConfidence] = useState(false);
  const [explanation, setExplanation] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const recognitionRef = useRef(null);
  const searchIdRef = useRef(0);

  const [explanationCache, setExplanationCache] = useState({});
  const [translating, setTranslating] = useState(false);
  const latestUiLanguageRef = useRef(uiLanguage);

  useEffect(function () {
    latestUiLanguageRef.current = uiLanguage;
  }, [uiLanguage]);

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
      language: uiLanguage,
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

  const translateExplanationTo = async function (targetLang, sourceText) {
    const textToTranslate = sourceText || explanation;
    if (!textToTranslate) return;

    if (explanationCache[targetLang]) {
      setExplanation(explanationCache[targetLang]);
      return;
    }

    setTranslating(true);
    try {
      const response = await fetch(API_URL + "/translate-explanation", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: textToTranslate, target_language: targetLang }),
      });

      if (!response.ok) {
        const message = await extractErrorMessage(response, "Could not translate the explanation.");
        setError(message);
        return;
      }

      const data = await response.json();
      setExplanation(data.translation);
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

  const handleViewSaved = async function (item) {
    setQuery(item.query);
    setResults([]);
    setLowConfidence(false);
    setLoadingSearch(false);
    setLoadingExplanation(false);
    const savedLang = item.language || "en";
    const currentUiLang = uiLanguage || "en";

    setExplanationCache({ [savedLang]: item.explanation });

    if (currentUiLang === savedLang) {
      setExplanation(item.explanation);
    } else if (explanationCache[currentUiLang]) {
      setExplanation(explanationCache[currentUiLang]);
    } else {
      await translateExplanationTo(currentUiLang, item.explanation);
    }
  };

  const runSearch = async function (searchQuery) {
    if (!searchQuery.trim()) {
      setError("Please enter a question or describe your situation to search.");
      return;
    }

    const requestLang = uiLanguage || "en";
    const searchId = ++searchIdRef.current;

    setLoadingSearch(true);
    setLoadingExplanation(false);
    setError(null);
    setExplanation("");
    setResults([]);
    setLowConfidence(false);
    setExplanationCache({});

    // Step 1: Fast search to show matched sections immediately (< 1s)
    let searchData;
    try {
      const response = await fetch(API_URL + "/search", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchQuery, top_k: 5, rerank: true, language: requestLang }),
      });

      if (!response.ok) {
        const message = await extractErrorMessage(response, "Something went wrong. Make sure the backend server is running.");
        if (searchIdRef.current === searchId) {
          setError(message);
          setLoadingSearch(false);
        }
        return;
      }

      searchData = await response.json();
    } catch (err) {
      if (searchIdRef.current === searchId) {
        setError("Could not reach the server. Make sure the backend is running.");
        setLoadingSearch(false);
      }
      console.error(err);
      return;
    }

    if (searchIdRef.current !== searchId) return;

    const foundResults = searchData.results || [];
    setResults(foundResults);
    setLowConfidence(Boolean(searchData.low_confidence));
    setLoadingSearch(false);
    addToHistory(searchQuery);

    // If no results, display static message and do not call /explain
    if (foundResults.length === 0) {
      if (searchData.explanation) {
        setExplanation(searchData.explanation);
      }
      return;
    }

    // If low confidence, show results with low-confidence message and do NOT call /explain
    if (searchData.low_confidence) {
      const lowConfExp = searchData.explanation || "";
      setExplanation(lowConfExp);
      setExplanationCache({ [requestLang]: lowConfExp });
      return;
    }

    // Step 2: Load plain-language explanation in the background
    setLoadingExplanation(true);
    const sectionRefs = foundResults.map(function (r) {
      return {
        act_name: r.act_name,
        section_number: r.section_number,
      };
    });

    try {
      const expResponse = await fetch(API_URL + "/explain", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query: searchQuery,
          language: requestLang,
          sections: sectionRefs,
        }),
      });

      if (searchIdRef.current !== searchId) return;

      if (!expResponse.ok) {
        const message = await extractErrorMessage(expResponse, "Could not generate an explanation right now.");
        setError(message);
        setLoadingExplanation(false);
        return;
      }

      const expData = await expResponse.json();
      if (searchIdRef.current !== searchId) return;

      const returnedExplanation = expData.explanation || "";
      setExplanationCache(function (prev) {
        const copy = Object.assign({}, prev);
        copy[requestLang] = returnedExplanation;
        return copy;
      });

      const currentUiLang = latestUiLanguageRef.current || "en";
      if (currentUiLang !== requestLang) {
        await translateExplanationTo(currentUiLang, returnedExplanation);
      } else {
        setExplanation(returnedExplanation);
      }
    } catch (err) {
      if (searchIdRef.current === searchId) {
        setError("Could not reach the server for explanation.");
      }
      console.error(err);
    } finally {
      if (searchIdRef.current === searchId) {
        setLoadingExplanation(false);
      }
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

  useEffect(function () {
    if (!explanation) return;
    const timer = setTimeout(function () {
      if (explanationCache[uiLanguage]) {
        setExplanation(explanationCache[uiLanguage]);
      } else {
        translateExplanationTo(uiLanguage, explanation);
      }
    }, 0);
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
    utterance.lang = uiLanguage === "hi" ? "hi-IN" : uiLanguage === "kn" ? "kn-IN" : "en-IN";
    utterance.onend = function () { setIsSpeaking(false); };
    utterance.onerror = function () { setIsSpeaking(false); };

    setIsSpeaking(true);
    window.speechSynthesis.speak(utterance);
  };

  const topScore = results.length > 0 ? results[0].hybrid_score : 0;
  const showLowConfidenceWarning = results.length > 0 && lowConfidence;
  const otherLanguages = ALL_LANGUAGES.filter(function (lang) { return lang !== uiLanguage; });

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
          {t(uiLanguage, "mic")}
        </button>
        <button type="submit" className="search-button" disabled={loadingSearch}>
          {loadingSearch ? t(uiLanguage, "searching") : t(uiLanguage, "search")}
        </button>
      </form>

      {searchHistory.length === 0 && !explanation && !loadingSearch && !loadingExplanation && (
        <div className="example-queries">
          <span className="example-queries-label">{t(uiLanguage, "tryAsking")}</span>
          <button className="example-chip" onClick={function () { setQuery("landlord not returning deposit"); runSearch("landlord not returning deposit"); }}>Landlord not returning deposit</button>
          <button className="example-chip" onClick={function () { setQuery("police arrest without warrant"); runSearch("police arrest without warrant"); }}>Police arrest without warrant</button>
          <button className="example-chip" onClick={function () { setQuery("how to file an RTI request"); runSearch("how to file an RTI request"); }}>How to file an RTI request</button>
          <button className="example-chip" onClick={function () { setQuery("consumer complaint for defective product"); runSearch("consumer complaint for defective product"); }}>Consumer complaint for defective product</button>
        </div>
      )}

      {searchHistory.length > 0 && (
        <div className="search-history">
          <span className="search-history-label">{t(uiLanguage, "recent")}</span>
          {searchHistory.map(function (h, i) {
            return (
              <button key={i} className="history-chip" onClick={function () { handleHistoryClick(h); }}>
                {h.length > 40 ? h.slice(0, 40) + "..." : h}
              </button>
            );
          })}
          <button className="history-clear" onClick={clearHistory}>{t(uiLanguage, "clear")}</button>
        </div>
      )}

      {savedResults.length > 0 && (
        <div className="saved-results-section">
          <h2>{t(uiLanguage, "savedResults")}</h2>
          {savedResults.map(function (item) {
            return (
              <div className="saved-result-card" key={item.id}>
                <div className="saved-result-header">
                  <button type="button" className="saved-result-query" onClick={function () { handleViewSaved(item); }}>
                    {item.query}
                  </button>
                  <button className="saved-result-delete" onClick={function () { handleDeleteSaved(item.id); }}>{t(uiLanguage, "delete")}</button>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {isListening && <div className="listening-indicator">{t(uiLanguage, "listeningIndicator")}</div>}

      {loadingSearch && (
        <div className="loading">{t(uiLanguage, "searchingFull")}</div>
      )}

      {showLowConfidenceWarning && (
        <div className="low-confidence-warning">
          {t(uiLanguage, "lowConfidenceWarning")}
        </div>
      )}

      {loadingExplanation && (
        <div className="explanation-card">
          <div className="explanation-header">
            <h2>{t(uiLanguage, "explanation")}</h2>
          </div>
          <div className="loading">{t(uiLanguage, "loadingExplanation")}</div>
        </div>
      )}

      {explanation && !loadingExplanation && (
        <div className="explanation-card">
          <div className="explanation-header">
            <h2>{t(uiLanguage, "explanation")}</h2>
            <div className="explanation-controls">
              <div className="language-toggle">
                {otherLanguages.map(function (lang) {
                  return (
                    <button
                      key={lang}
                      className="language-toggle-button"
                      onClick={function () {
                        if (typeof onLanguageChange === "function") {
                          onLanguageChange(lang);
                        }
                      }}
                      disabled={translating}
                    >
                      {LANGUAGE_LABELS[lang]}
                    </button>
                  );
                })}
              </div>
              <button className="listen-button" onClick={speakExplanation}>
                {isSpeaking ? t(uiLanguage, "stop") : t(uiLanguage, "listen")}
              </button>
              <button className="save-button" onClick={handleSaveResult} disabled={isCurrentResultSaved || loadingExplanation || !explanation}>
                {isCurrentResultSaved ? t(uiLanguage, "saved") : t(uiLanguage, "save")}
              </button>
            </div>
          </div>
          {translating ? (
            <div className="loading">{t(uiLanguage, "translating")}</div>
          ) : (
            <div className="explanation-text"><ReactMarkdown remarkPlugins={[remarkGfm]}>{explanation}</ReactMarkdown></div>
          )}
        </div>
      )}

      {results.length > 0 && (
        <div className="results-section">
          <h2>{t(uiLanguage, "sources")}</h2>
          {results.map(function (r, i) {
            const confidence = getConfidenceLabel(r.hybrid_score, topScore, uiLanguage);
            return (
              <div className="result-card" key={i}>
                <div className="result-header">
                  <span className="act-name">{r.act_name}</span>
                  <span className="citation-tag">
                    <span className="citation-tag-label">{t(uiLanguage, "section")}</span>
                    <span className="citation-tag-number">{r.section_number}</span>
                  </span>
                </div>
                <div className={"confidence-badge " + confidence.className}>{confidence.label}</div>

                {r.matched_terms && r.matched_terms.length > 0 && (
                  <div className="matched-terms">
                    <span className="matched-terms-label">{t(uiLanguage, "whyThisMatched")} </span>
                    {r.matched_terms.map(function (term, k) {
                      return <span className="matched-term-tag" key={k}>{term}</span>;
                    })}
                  </div>
                )}

                <div className="section-title">{r.section_title}</div>
                <div className="legal-text">{r.legal_text}</div>

                {r.related_cases && r.related_cases.length > 0 && (
                  <div className="related-cases">
                    <div className="related-cases-title">{t(uiLanguage, "relatedCases")}</div>
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

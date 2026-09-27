import { useState, useRef, useEffect } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { API_URL, LANGUAGE_LABELS, ALL_LANGUAGES, MAX_HISTORY, MAX_SAVED_RESULTS } from "../constants";
import {
  getConfidenceLabel,
  extractErrorMessage,
  loadHistory,
  saveHistory,
  loadSavedResults,
  persistSavedResults,
  loadPinnedQueries,
  savePinnedQueries,
  getSpellingSuggestion,
  t,
} from "../utils";

// The BNS Decoder (main.py's /bns-lookup) only ever explains Bharatiya Nyaya
// Sanhita sections, not BNSS or BSA - so the "Look up this section" action
// only makes sense when a result's act is actually the BNS.
function isBnsAct(actName) {
  return typeof actName === "string" && /\bbharatiya nyaya sanhita\b/i.test(actName);
}

function SearchTab({ setError, uiLanguage, onLanguageChange, isActive, pendingViewSavedId, onConsumePendingViewSavedId, onLookUpBnsSection, onSimplifyCase, pendingSearchQuery, onConsumePendingSearchQuery }) {
  const [query, setQuery] = useState("");
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [loadingExplanation, setLoadingExplanation] = useState(false);
  const [results, setResults] = useState([]);
  const [lowConfidence, setLowConfidence] = useState(false);
  const [searchAttempted, setSearchAttempted] = useState(false);
  const [showConfidenceInfo, setShowConfidenceInfo] = useState(false);
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
  const [pinnedQueries, setPinnedQueries] = useState(function () { return loadPinnedQueries(); });
  const [savedResults, setSavedResults] = useState(function () { return loadSavedResults(); });
  const [confirmingDeleteId, setConfirmingDeleteId] = useState(null);

  // Search history and saved results can also be edited from the My
  // Documents tab (e.g. deleting a saved search there), which writes to the
  // same localStorage keys but cannot update this component's in-memory
  // state directly, since every tab stays mounted for the life of the app.
  // Re-reading from storage whenever this tab becomes active keeps the two
  // views from drifting out of sync.
  useEffect(function () {
    if (!isActive) return;
    const timer = setTimeout(function () {
      setSearchHistory(loadHistory());
      setPinnedQueries(loadPinnedQueries());
      setSavedResults(loadSavedResults());
    }, 0);
    return function () { clearTimeout(timer); };
  }, [isActive]);

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

  const deleteHistoryItem = function (queryToRemove) {
    setSearchHistory(function (prev) {
      const updated = prev.filter(function (q) { return q !== queryToRemove; });
      saveHistory(updated);
      return updated;
    });
  };

  const pinQuery = function (queryToPin) {
    setPinnedQueries(function (prev) {
      if (prev.includes(queryToPin)) return prev;
      const updated = [queryToPin].concat(prev);
      savePinnedQueries(updated);
      return updated;
    });
  };

  const unpinQuery = function (queryToUnpin) {
    setPinnedQueries(function (prev) {
      const updated = prev.filter(function (q) { return q !== queryToUnpin; });
      savePinnedQueries(updated);
      return updated;
    });
  };

  const isCurrentResultSaved = savedResults.some(function (r) { return r.query === query && r.explanation === explanation; });

  const handleSaveResult = function () {
    if (!query || !explanation) return;
    const newItem = {
      id: Date.now(),
      query: query,
      explanation: explanation,
      language: uiLanguage,
      results: results,
      savedAt: new Date().toISOString(),
    };
    setSavedResults(function (prev) {
      // Capped like the other My Documents lists (uploaded/generated docs)
      // so saved searches - which duplicate the full explanation and result
      // set for reliable offline recall - can't grow localStorage without
      // bound. Oldest saved searches drop off first.
      const updated = [newItem].concat(prev).slice(0, MAX_SAVED_RESULTS);
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
    setConfirmingDeleteId(null);
  };

  const requestDeleteSaved = function (id) {
    setConfirmingDeleteId(id);
  };

  const cancelDeleteSaved = function () {
    setConfirmingDeleteId(null);
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
    setResults(item.results || []);
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

  // "Open in Search" from the My Documents tab: App.jsx hands us the id of
  // the saved search to jump to via a prop rather than a query re-run, since
  // we already have the full saved result. Consume it once, then clear it
  // upstream so switching tabs later doesn't re-trigger the same view.
  useEffect(function () {
    if (!isActive || !pendingViewSavedId) return;
    const timer = setTimeout(function () {
      const item = savedResults.find(function (r) { return r.id === pendingViewSavedId; });
      if (item) handleViewSaved(item);
      if (typeof onConsumePendingViewSavedId === "function") onConsumePendingViewSavedId();
    }, 0);
    return function () { clearTimeout(timer); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isActive, pendingViewSavedId, savedResults]);

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
    setSearchAttempted(true);
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

  // Home's "Continue where you left off" hands us the last query the same
  // way as the saved-search handoff above: re-run it here rather than
  // having Home duplicate the search logic.
  useEffect(function () {
    if (!isActive || !pendingSearchQuery) return;
    const timer = setTimeout(function () {
      setQuery(pendingSearchQuery);
      runSearch(pendingSearchQuery);
      if (typeof onConsumePendingSearchQuery === "function") onConsumePendingSearchQuery();
    }, 0);
    return function () { clearTimeout(timer); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isActive, pendingSearchQuery]);

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
    // interimResults is false, so this only fires once recognition has
    // settled on a final transcript - safe to submit immediately rather
    // than making the user press Search again after already speaking it.
    recognition.onresult = function (event) {
      const transcript = event.results[0][0].transcript;
      setQuery(transcript);
      runSearch(transcript);
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

  // Purely derived from the query text - no dictionary lookup - so this is
  // cheap enough to compute on every render and needs no effect/state of
  // its own. Only shown once a search has actually come back thin, so it
  // never nags while someone is still typing.
  const showSpellingSuggestion = searchAttempted && !loadingSearch && (results.length === 0 || lowConfidence);
  const spellingSuggestion = showSpellingSuggestion ? getSpellingSuggestion(query) : null;

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

      {pinnedQueries.length > 0 && (
        <div className="search-history">
          <span className="search-history-label">{t(uiLanguage, "pinned")}</span>
          {pinnedQueries.map(function (h, i) {
            return (
              <div className="history-chip" key={i}>
                <button type="button" className="history-chip-text" onClick={function () { handleHistoryClick(h); }}>
                  {h.length > 40 ? h.slice(0, 40) + "..." : h}
                </button>
                <button type="button" className="history-chip-action" onClick={function () { unpinQuery(h); }}>{t(uiLanguage, "unpin")}</button>
              </div>
            );
          })}
        </div>
      )}

      {searchHistory.filter(function (h) { return !pinnedQueries.includes(h); }).length > 0 && (
        <div className="search-history">
          <span className="search-history-label">{t(uiLanguage, "recent")}</span>
          {searchHistory.filter(function (h) { return !pinnedQueries.includes(h); }).map(function (h, i) {
            return (
              <div className="history-chip" key={i}>
                <button type="button" className="history-chip-text" onClick={function () { handleHistoryClick(h); }}>
                  {h.length > 40 ? h.slice(0, 40) + "..." : h}
                </button>
                <button type="button" className="history-chip-action" onClick={function () { pinQuery(h); }}>{t(uiLanguage, "pin")}</button>
                <button type="button" className="history-chip-action history-chip-action-delete" onClick={function () { deleteHistoryItem(h); }} aria-label={t(uiLanguage, "delete")}>×</button>
              </div>
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
                  {confirmingDeleteId === item.id ? (
                    <span className="saved-result-confirm">
                      <span className="saved-result-confirm-label">{t(uiLanguage, "deleteConfirm")}</span>
                      <button type="button" className="saved-result-confirm-yes" onClick={function () { handleDeleteSaved(item.id); }}>
                        {t(uiLanguage, "deleteConfirmYes")}
                      </button>
                      <button type="button" className="saved-result-confirm-cancel" onClick={cancelDeleteSaved}>
                        {t(uiLanguage, "cancel")}
                      </button>
                    </span>
                  ) : (
                    <button type="button" className="saved-result-delete" onClick={function () { requestDeleteSaved(item.id); }}>
                      {t(uiLanguage, "delete")}
                    </button>
                  )}
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

      {spellingSuggestion && (
        <div className="spelling-suggestion">
          <span>
            {t(uiLanguage, "didYouMean")}{" "}
            <button
              type="button"
              className="spelling-suggestion-link"
              onClick={function () { setQuery(spellingSuggestion.correctedQuery); runSearch(spellingSuggestion.correctedQuery); }}
            >
              {spellingSuggestion.correctedQuery}
            </button>
          </span>
        </div>
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
              <button
                className={"save-button" + (isCurrentResultSaved ? " save-button-saved" : "")}
                onClick={handleSaveResult}
                disabled={isCurrentResultSaved || loadingExplanation || !explanation}
              >
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
          <div className="results-heading-row">
            <h2>{t(uiLanguage, "sources")}</h2>
            <button
              type="button"
              className="confidence-info-toggle"
              onClick={function () { setShowConfidenceInfo(!showConfidenceInfo); }}
              aria-expanded={showConfidenceInfo}
            >
              {t(uiLanguage, "confidenceInfoToggle")}
            </button>
          </div>
          {showConfidenceInfo && (
            <div className="confidence-info-panel">
              <p className="confidence-info-intro">{t(uiLanguage, "confidenceInfoIntro")}</p>
              <p><span className="confidence-badge confidence-strong">{t(uiLanguage, "strongMatch")}</span> {t(uiLanguage, "confidenceInfoStrong")}</p>
              <p><span className="confidence-badge confidence-good">{t(uiLanguage, "goodMatch")}</span> {t(uiLanguage, "confidenceInfoGood")}</p>
              <p><span className="confidence-badge confidence-weak">{t(uiLanguage, "possibleMatch")}</span> {t(uiLanguage, "confidenceInfoWeak")}</p>
            </div>
          )}
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
                <div className="result-header-secondary">
                  <div className={"confidence-badge " + confidence.className}>{confidence.label}</div>
                  {isBnsAct(r.act_name) && typeof onLookUpBnsSection === "function" && (
                    <button
                      type="button"
                      className="contextual-action-link"
                      onClick={function () { onLookUpBnsSection(r.section_number); }}
                    >
                      {t(uiLanguage, "lookUpSection")}
                    </button>
                  )}
                </div>

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
                          {typeof onSimplifyCase === "function" && (
                            <button
                              type="button"
                              className="contextual-action-link"
                              onClick={function () { onSimplifyCase({ title: c.title, court: c.court, decision_date: c.decision_date }); }}
                            >
                              {t(uiLanguage, "simplifyThisCase")}
                            </button>
                          )}
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

import { useState, useRef, useEffect } from "react";
import "./App.css";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Document, Packer, Paragraph, TextRun, HeadingLevel } from "docx";
import { saveAs } from "file-saver";
import { DOCUMENT_SCHEMAS, GENERIC_DOCUMENT_TYPES, ADDITIONAL_DOCUMENT_SCHEMAS } from "./documentSchemas";
import { QUIZ_QUESTIONS } from "./quizData";

const API_URL = "http://127.0.0.1:8000";
const HISTORY_KEY = "nyaaya-search-history";
const MAX_HISTORY = 8;
const SAVED_RESULTS_KEY = "nyaaya-saved-results";

const LANGUAGE_LABELS = {
  en: "English",
  hi: "\u0939\u093F\u0902\u0926\u0940",
  kn: "\u0C95\u0CA8\u0CCD\u0CA8\u0CA1",
};

const ALL_LANGUAGES = ["en", "hi", "kn"];

const MERGED_DOCUMENT_SCHEMAS = Object.assign({}, DOCUMENT_SCHEMAS, ADDITIONAL_DOCUMENT_SCHEMAS);

const ALL_DOCUMENT_TYPE_LABELS = {
  ...Object.fromEntries(Object.entries(MERGED_DOCUMENT_SCHEMAS).map(([key, schema]) => [key, schema.label])),

};

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
    return fallback;
  }
  return fallback;
}

function loadHistory() {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
}

function saveHistory(history) {
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  } catch (e) {
    return;
  }
}

function loadSavedResults() {
  try {
    const raw = localStorage.getItem(SAVED_RESULTS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
}

function persistSavedResults(items) {
  try {
    localStorage.setItem(SAVED_RESULTS_KEY, JSON.stringify(items));
  } catch (e) {
    return;
  }
}

function buildDocxFromMarkdown(markdownText) {
  const lines = markdownText.split("\n");
  const paragraphs = [];

  const parseBoldRuns = (text) => {
    const parts = text.split(/(\*\*[^*]+\*\*)/g).filter(Boolean);
    return parts.map((part) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return new TextRun({ text: part.slice(2, -2), bold: true });
      }
      return new TextRun(part);
    });
  };

  for (const rawLine of lines) {
    const line = rawLine.replace(/\s+$/, "");

    if (line.startsWith("# ")) {
      paragraphs.push(new Paragraph({ text: line.slice(2), heading: HeadingLevel.TITLE, spacing: { after: 200 } }));
    } else if (line.startsWith("## ")) {
      paragraphs.push(new Paragraph({ text: line.slice(3), heading: HeadingLevel.HEADING_1, spacing: { before: 200, after: 100 } }));
    } else if (line.startsWith("### ")) {
      paragraphs.push(new Paragraph({ text: line.slice(4), heading: HeadingLevel.HEADING_2, spacing: { before: 150, after: 80 } }));
    } else if (line.trim() === "") {
      paragraphs.push(new Paragraph({ text: "" }));
    } else {
      paragraphs.push(new Paragraph({ children: parseBoldRuns(line), spacing: { after: 100 } }));
    }
  }

  return new Document({
    sections: [{ properties: {}, children: paragraphs }],
  });
}

function App() {
  const [query, setQuery] = useState("");
  const [activeTab, setActiveTab] = useState("search");
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

  const [caseText, setCaseText] = useState("");
  const [simplifiedCase, setSimplifiedCase] = useState("");
  const [simplifying, setSimplifying] = useState(false);

  const [bnsSectionInput, setBnsSectionInput] = useState("");
  const [bnsResult, setBnsResult] = useState(null);
  const [bnsLoading, setBnsLoading] = useState(false);

  const [quizIndex, setQuizIndex] = useState(0);
  const [quizScore, setQuizScore] = useState(0);
  const [quizSelected, setQuizSelected] = useState(null);
  const [quizFinished, setQuizFinished] = useState(false);

  const [dictTerm, setDictTerm] = useState("");
  const [dictDefinition, setDictDefinition] = useState("");
  const [dictLoading, setDictLoading] = useState(false);

  const [draftType, setDraftType] = useState("rent_agreement");
  const [formValues, setFormValues] = useState({});
  const [genericDetails, setGenericDetails] = useState("");
  const [draftText, setDraftText] = useState("");
  const [drafting, setDrafting] = useState(false);

  const [darkMode, setDarkMode] = useState(function () {
    try {
      return localStorage.getItem("nyaaya-dark-mode") === "true";
    } catch (e) {
      return false;
    }
  });

  const [searchHistory, setSearchHistory] = useState(function () { return loadHistory(); });
  const [savedResults, setSavedResults] = useState(function () { return loadSavedResults(); });

  useEffect(function () {
    try {
      localStorage.setItem("nyaaya-dark-mode", darkMode ? "true" : "false");
    document.body.style.background = darkMode ? "#1a1a1a" : "#f7f7f5";
    } catch (e) {
      return;
    }
  }, [darkMode]);

  const toggleDarkMode = function () { setDarkMode(function (prev) { return !prev; }); };

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
    setActiveTab("search");
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

  const handleFileUpload = async function (e) {
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

      const response = await fetch(API_URL + "/upload-pdf", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const message = await extractErrorMessage(response, "Could not upload the document. Make sure the backend server is running.");
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

  const handleAskDocument = async function (e) {
    e.preventDefault();
    if (!docQuestion.trim() || !uploadedDoc) return;

    setDocAsking(true);
    setDocAnswer("");

    try {
      const response = await fetch(API_URL + "/ask-document", {
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

  const handleSimplifyCase = async function (e) {
    e.preventDefault();
    if (!caseText.trim()) return;

    setSimplifying(true);
    setError(null);
    setSimplifiedCase("");

    try {
      const response = await fetch(API_URL + "/simplify-case", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ case_text: caseText }),
      });

      if (!response.ok) {
        const message = await extractErrorMessage(response, "Could not simplify this case. Please try again.");
        setError(message);
        return;
      }

      const data = await response.json();
      setSimplifiedCase(data.simplified_explanation || "");
    } catch (err) {
      setError("Could not reach the server. Make sure the backend is running.");
      console.error(err);
    } finally {
      setSimplifying(false);
    }
  };

  const handleBnsLookup = async function (e) {
    e.preventDefault();
    if (!bnsSectionInput.trim()) return;

    setBnsLoading(true);
    setError(null);
    setBnsResult(null);

    try {
      const response = await fetch(API_URL + "/bns-lookup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ section_number: bnsSectionInput.trim() }),
      });

      if (!response.ok) {
        const message = await extractErrorMessage(response, "Could not find this section.");
        setError(message);
        return;
      }

      const data = await response.json();
      setBnsResult(data);
    } catch (err) {
      setError("Could not reach the server. Make sure the backend is running.");
      console.error(err);
    } finally {
      setBnsLoading(false);
    }
  };

  const handleQuizAnswer = function (optionIndex) {
    if (quizSelected !== null) return;
    setQuizSelected(optionIndex);
    if (optionIndex === QUIZ_QUESTIONS[quizIndex].correctIndex) {
      setQuizScore(function (prev) { return prev + 1; });
    }
  };

  const handleQuizNext = function () {
    if (quizIndex + 1 < QUIZ_QUESTIONS.length) {
      setQuizIndex(function (prev) { return prev + 1; });
      setQuizSelected(null);
    } else {
      setQuizFinished(true);
    }
  };

  const handleQuizRestart = function () {
    setQuizIndex(0);
    setQuizScore(0);
    setQuizSelected(null);
    setQuizFinished(false);
  };

  const handleDefine = async function (e) {
    e.preventDefault();
    if (!dictTerm.trim()) return;

    setDictLoading(true);
    setDictDefinition("");

    try {
      const response = await fetch(API_URL + "/define", {
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

  const handleDraftTypeChange = function (newType) {
    setDraftType(newType);
    setFormValues({});
    setGenericDetails("");
    setDraftText("");
  };

  const handleFormFieldChange = function (key, value) {
    setFormValues(function (prev) {
      const copy = Object.assign({}, prev);
      copy[key] = value;
      return copy;
    });
  };

  const handleDraft = async function (e) {
    e.preventDefault();

    setDrafting(true);
    setError(null);
    setDraftText("");

    let details = {};

    const schema = MERGED_DOCUMENT_SCHEMAS[draftType];
    if (schema) {
      Object.keys(formValues).forEach(function (key) {
        const value = formValues[key];
        if (value && value.trim && value.trim() !== "") details[key] = value;
        else if (value && typeof value !== "string") details[key] = value;
      });
    } else {
      genericDetails.split("\n").forEach(function (line) {
        const idx = line.indexOf(":");
        if (idx > -1) {
          const key = line.slice(0, idx).trim().toLowerCase().replace(/\s+/g, "_");
          const value = line.slice(idx + 1).trim();
          if (key && value) details[key] = value;
        }
      });
    }

    try {
      const response = await fetch(API_URL + "/draft-document", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ document_type: draftType, details: details }),
      });

      if (!response.ok) {
        const message = await extractErrorMessage(response, "Could not generate the document.");
        setError(message);
        return;
      }

      const data = await response.json();
      setDraftText(data.document_text || "");
    } catch (err) {
      setError("Could not reach the server. Make sure the backend is running.");
      console.error(err);
    } finally {
      setDrafting(false);
    }
  };

  const handleDownloadDraft = async function () {
    const doc = buildDocxFromMarkdown(draftText);
    const blob = await Packer.toBlob(doc);
    saveAs(blob, draftType + ".docx");
  };

  const topScore = results.length > 0 ? results[0].hybrid_score : 0;
  const showLowConfidenceWarning = results.length > 0 && isOverallLowConfidence(topScore);
  const otherLanguages = ALL_LANGUAGES.filter(function (lang) { return lang !== currentLanguage; });
  const activeSchema = MERGED_DOCUMENT_SCHEMAS[draftType];

  return (
    <div className={"app" + (darkMode ? " dark-mode" : "")}>
      <header className="header">
        <div className="header-top">
          <h1>NyaayaSearch</h1>
          <button className="theme-toggle" onClick={toggleDarkMode}>
            {darkMode ? "Light Mode" : "Dark Mode"}
          </button>
        </div>
        <p className="tagline">Understand Indian law in plain language</p>
      </header>

      <nav className="tab-nav">
        <button className={"tab-button" + (activeTab === "search" ? " active" : "")} onClick={function () { setActiveTab("search"); }}>Search</button>
        <button className={"tab-button" + (activeTab === "drafter" ? " active" : "")} onClick={function () { setActiveTab("drafter"); }}>Document Generator</button>
        <button className={"tab-button" + (activeTab === "dictionary" ? " active" : "")} onClick={function () { setActiveTab("dictionary"); }}>Dictionary</button>
        <button className={"tab-button" + (activeTab === "documents" ? " active" : "")} onClick={function () { setActiveTab("documents"); }}>My Documents</button>
        <button className={"tab-button" + (activeTab === "simplifier" ? " active" : "")} onClick={function () { setActiveTab("simplifier"); }}>Case Simplifier</button>
        <button className={"tab-button" + (activeTab === "emergency" ? " active" : "")} onClick={function () { setActiveTab("emergency"); }}>Emergency Help</button>
        <button className={"tab-button" + (activeTab === "bns" ? " active" : "")} onClick={function () { setActiveTab("bns"); }}>BNS Decoder</button>
        <button className={"tab-button" + (activeTab === "quiz" ? " active" : "")} onClick={function () { setActiveTab("quiz"); }}>Legal IQ Daily</button>
      </nav>

      {error && <div className="error">{error}</div>}

      {activeTab === "dictionary" && (
        <div className="dictionary-section">
          <h2>Legal Dictionary</h2>
          <form className="dict-form" onSubmit={handleDefine}>
            <input
              type="text"
              className="search-input"
              placeholder="Look up a legal term, e.g. 'cognizable offence'"
              value={dictTerm}
              onChange={function (e) { setDictTerm(e.target.value); }}
            />
            <button type="submit" className="search-button" disabled={dictLoading}>
              {dictLoading ? "Looking up..." : "Define"}
            </button>
          </form>
          {dictDefinition && <div className="dict-definition">{dictDefinition}</div>}
        </div>
      )}

      {activeTab === "drafter" && (
        <div className="drafter-section">
          <h2>Legal Document Generator</h2>
          <p className="drafter-intro">What document do you want to create?</p>

          <select
            className="search-input"
            value={draftType}
            onChange={function (e) { handleDraftTypeChange(e.target.value); }}
          >
            {Object.keys(ALL_DOCUMENT_TYPE_LABELS).map(function (value) {
              return <option key={value} value={value}>{ALL_DOCUMENT_TYPE_LABELS[value]}</option>;
            })}
          </select>

          <form className="drafter-form" onSubmit={handleDraft}>
            {activeSchema ? (
              <div>
                <p className="drafter-subtitle">Let's create your {activeSchema.label}</p>
                {activeSchema.sections.map(function (section) {
                  return (
                    <div className="form-section" key={section.title}>
                      <div className="form-section-title">{section.title}</div>
                      {section.fields.map(function (field) {
                        return (
                          <div className="form-field" key={field.key}>
                            <label className="form-field-label">{field.label}</label>
                            {field.type === "textarea" ? (
                              <textarea
                                className="drafter-textarea"
                                placeholder={field.placeholder}
                                rows={2}
                                value={formValues[field.key] || ""}
                                onChange={function (e) { handleFormFieldChange(field.key, e.target.value); }}
                              />
                            ) : field.type === "select" ? (
                              <select
                                className="search-input"
                                value={formValues[field.key] || ""}
                                onChange={function (e) { handleFormFieldChange(field.key, e.target.value); }}
                              >
                                <option value="">Select...</option>
                                {field.options.map(function (opt) {
                                  return <option key={opt} value={opt}>{opt}</option>;
                                })}
                              </select>
                            ) : (
                              <input
                                type={field.type === "date" ? "date" : field.type === "number" ? "number" : "text"}
                                className="search-input"
                                placeholder={field.placeholder}
                                value={formValues[field.key] || ""}
                                onChange={function (e) { handleFormFieldChange(field.key, e.target.value); }}
                              />
                            )}
                          </div>
                        );
                      })}
                    </div>
                  );
                })}
              </div>
            ) : (
              <div>
                <p className="drafter-subtitle">
                  This document type doesn't have a detailed form yet. Enter any details you'd like included, one per line (e.g. "name: John Doe") - anything you leave out will appear as a blank line to fill in later.
                </p>
                <textarea
                  className="drafter-textarea"
                  placeholder={"e.g.\nname: John Doe\ndate: 2026-01-01"}
                  value={genericDetails}
                  onChange={function (e) { setGenericDetails(e.target.value); }}
                  rows={5}
                />
              </div>
            )}

            <button type="submit" className="search-button" disabled={drafting}>
              {drafting ? "Generating..." : "Generate Document"}
            </button>
          </form>

          {draftText && (
            <div className="draft-result">
              <div className="draft-result-header">
                <h3>{ALL_DOCUMENT_TYPE_LABELS[draftType]}</h3>
                <button className="search-button" onClick={handleDownloadDraft}>Download as Word</button>
              </div>
              <div className="draft-text">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{draftText}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === "bns" && (
        <div className="drafter-section">
          <h2>BNS Decoder</h2>
          <p className="drafter-intro">Enter a Bharatiya Nyaya Sanhita (BNS) section number to see what it says, explained in plain language.</p>
          <form className="drafter-form" onSubmit={handleBnsLookup}>
            <input
              type="text"
              className="search-input"
              placeholder="e.g. 103"
              value={bnsSectionInput}
              onChange={function (e) { setBnsSectionInput(e.target.value); }}
            />
            <button type="submit" className="search-button" disabled={bnsLoading}>
              {bnsLoading ? "Looking up..." : "Decode Section"}
            </button>
          </form>

          {bnsResult && (
            <div className="draft-result">
              <div className="draft-result-header">
                <h3>Section {bnsResult.section_number}: {bnsResult.section_title}</h3>
              </div>
              <div className="draft-text">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{bnsResult.explanation}</ReactMarkdown>
                <p className="bns-original-label">Original text:</p>
                <p className="bns-original-text">{bnsResult.legal_text}</p>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === "quiz" && (
        <div className="drafter-section">
          <h2>Legal IQ Daily</h2>
          {!quizFinished ? (
            <div>
              <p className="quiz-progress">Question {quizIndex + 1} of {QUIZ_QUESTIONS.length}</p>
              <p className="quiz-question">{QUIZ_QUESTIONS[quizIndex].question}</p>
              <div className="quiz-options">
                {QUIZ_QUESTIONS[quizIndex].options.map(function (option, i) {
                  let optionClass = "quiz-option";
                  if (quizSelected !== null) {
                    if (i === QUIZ_QUESTIONS[quizIndex].correctIndex) optionClass += " correct";
                    else if (i === quizSelected) optionClass += " incorrect";
                  }
                  return (
                    <button key={i} className={optionClass} onClick={function () { handleQuizAnswer(i); }} disabled={quizSelected !== null}>
                      {option}
                    </button>
                  );
                })}
              </div>
              {quizSelected !== null && (
                <div className="quiz-feedback">
                  <p className="quiz-explanation">{QUIZ_QUESTIONS[quizIndex].explanation}</p>
                  <button className="search-button" onClick={handleQuizNext}>
                    {quizIndex + 1 < QUIZ_QUESTIONS.length ? "Next Question" : "See Results"}
                  </button>
                </div>
              )}
            </div>
          ) : (
            <div className="quiz-results">
              <p className="quiz-score">You scored {quizScore} out of {QUIZ_QUESTIONS.length}</p>
              <button className="search-button" onClick={handleQuizRestart}>Try Again</button>
            </div>
          )}
        </div>
      )}

      {activeTab === "emergency" && (
        <div className="drafter-section">
          <h2>Emergency and Legal Aid Resources</h2>
          <p className="drafter-intro">If you need urgent help, contact these resources directly.</p>

          <div className="emergency-list">
            <div className="emergency-item">
              <div className="emergency-title">Police Emergency</div>
              <div className="emergency-number">100 / 112</div>
              <div className="emergency-desc">National emergency helpline for police assistance.</div>
            </div>
            <div className="emergency-item">
              <div className="emergency-title">Women Helpline</div>
              <div className="emergency-number">1091</div>
              <div className="emergency-desc">National helpline for women in distress.</div>
            </div>
            <div className="emergency-item">
              <div className="emergency-title">Domestic Violence Helpline</div>
              <div className="emergency-number">181</div>
              <div className="emergency-desc">National helpline for domestic violence support.</div>
            </div>
            <div className="emergency-item">
              <div className="emergency-title">Child Helpline</div>
              <div className="emergency-number">1098</div>
              <div className="emergency-desc">National helpline for children in need of help.</div>
            </div>
            <div className="emergency-item">
              <div className="emergency-title">National Legal Services Authority (NALSA)</div>
              <div className="emergency-number">15100</div>
              <div className="emergency-desc">Free legal aid and services for eligible citizens.</div>
            </div>
            <div className="emergency-item">
              <div className="emergency-title">Consumer Helpline</div>
              <div className="emergency-number">1915</div>
              <div className="emergency-desc">National Consumer Helpline for consumer grievances.</div>
            </div>
            <div className="emergency-item">
              <div className="emergency-title">Cyber Crime Helpline</div>
              <div className="emergency-number">1930</div>
              <div className="emergency-desc">National helpline to report cyber crimes and online fraud.</div>
            </div>
            <div className="emergency-item">
              <div className="emergency-title">Senior Citizen Helpline</div>
              <div className="emergency-number">14567</div>
              <div className="emergency-desc">National helpline for elderly citizens needing assistance.</div>
            </div>
          </div>

          <p className="emergency-disclaimer">These are general national helpline numbers. In an emergency, always contact local police or emergency services directly.</p>
        </div>
      )}

      {activeTab === "simplifier" && (
        <div className="drafter-section">
          <h2>Case Simplifier</h2>
          <p className="drafter-intro">Paste a court judgment, order, or legal case text to get a plain-language explanation.</p>
          <form className="drafter-form" onSubmit={handleSimplifyCase}>
            <textarea
              className="drafter-textarea"
              placeholder="Paste the case text here..."
              rows={10}
              value={caseText}
              onChange={function (e) { setCaseText(e.target.value); }}
            />
            <button type="submit" className="search-button" disabled={simplifying}>
              {simplifying ? "Simplifying..." : "Simplify Case"}
            </button>
          </form>

          {simplifiedCase && (
            <div className="draft-result">
              <div className="draft-result-header">
                <h3>Explanation</h3>
              </div>
              <div className="draft-text">
                <ReactMarkdown remarkPlugins={[remarkGfm]}>{simplifiedCase}</ReactMarkdown>
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === "documents" && (
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
                  {uploadedDoc.dates.map(function (d, i) {
                    return (
                      <div className="date-item" key={i}>
                        <span className="date-value">{d.value}</span>
                        <span className="date-description">{d.description}</span>
                      </div>
                    );
                  })}
                </div>
              )}

              {uploadedDoc.document_id && (
                <form className="doc-question-form" onSubmit={handleAskDocument}>
                  <input
                    type="text"
                    className="search-input"
                    placeholder="Ask a question about this document..."
                    value={docQuestion}
                    onChange={function (e) { setDocQuestion(e.target.value); }}
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
      )}

      {activeTab === "search" && (
        <div>
          <form className="search-form" onSubmit={handleSearch}>
            <input
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
              Mic
            </button>
            <button type="submit" className="search-button" disabled={loading}>
              {loading ? "Searching..." : "Search"}
            </button>
          </form>

          {searchHistory.length === 0 && !explanation && !loading && (
            <div className="example-queries">
              <span className="example-queries-label">Try asking:</span>
              <button className="example-chip" onClick={function () { setQuery("landlord not returning deposit"); runSearch("landlord not returning deposit"); }}>Landlord not returning deposit</button>
              <button className="example-chip" onClick={function () { setQuery("police arrest without warrant"); runSearch("police arrest without warrant"); }}>Police arrest without warrant</button>
              <button className="example-chip" onClick={function () { setQuery("how to file an RTI request"); runSearch("how to file an RTI request"); }}>How to file an RTI request</button>
              <button className="example-chip" onClick={function () { setQuery("consumer complaint for defective product"); runSearch("consumer complaint for defective product"); }}>Consumer complaint for defective product</button>
            </div>
          )}

          {searchHistory.length > 0 && (
            <div className="search-history">
              <span className="search-history-label">Recent:</span>
              {searchHistory.map(function (h, i) {
                return (
                  <button key={i} className="history-chip" onClick={function () { handleHistoryClick(h); }}>
                    {h.length > 40 ? h.slice(0, 40) + "..." : h}
                  </button>
                );
              })}
              <button className="history-clear" onClick={clearHistory}>Clear</button>
            </div>
          )}

          {savedResults.length > 0 && (
            <div className="saved-results-section">
              <h2>Saved Results</h2>
              {savedResults.map(function (item) {
                return (
                  <div className="saved-result-card" key={item.id}>
                    <div className="saved-result-header">
                      <span className="saved-result-query" onClick={function () { handleViewSaved(item); }}>
                        {item.query}
                      </span>
                      <button className="saved-result-delete" onClick={function () { handleDeleteSaved(item.id); }}>Delete</button>
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {isListening && <div className="listening-indicator">Listening... (click mic again to stop)</div>}

          {loading && (
            <div className="loading">Searching legal database and generating explanation...</div>
          )}

          {showLowConfidenceWarning && (
            <div className="low-confidence-warning">
              We're not fully confident in these results. Try rephrasing your question with more specific details for a better match. Showing our best guess below.
            </div>
          )}

          {explanation && (
            <div className="explanation-card">
              <div className="explanation-header">
                <h2>Explanation</h2>
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
                    {isSpeaking ? "Stop" : "Listen"}
                  </button>
                  <button className="save-button" onClick={handleSaveResult} disabled={isCurrentResultSaved}>
                    {isCurrentResultSaved ? "Saved" : "Save"}
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
              {results.map(function (r, i) {
                const confidence = getConfidenceLabel(r.hybrid_score, topScore);
                return (
                  <div className="result-card" key={i}>
                    <div className="result-header">
                      <span className="act-name">{r.act_name}</span>
                      <span className="section-number">Section {r.section_number}</span>
                    </div>
                    <div className={"confidence-badge " + confidence.className}>{confidence.label}</div>

                    {r.matched_terms && r.matched_terms.length > 0 && (
                      <div className="matched-terms">
                        <span className="matched-terms-label">Why this matched: </span>
                        {r.matched_terms.map(function (term, k) {
                          return <span className="matched-term-tag" key={k}>{term}</span>;
                        })}
                      </div>
                    )}

                    <div className="section-title">{r.section_title}</div>
                    <div className="legal-text">{r.legal_text}</div>

                    {r.related_cases && r.related_cases.length > 0 && (
                      <div className="related-cases">
                        <div className="related-cases-title">Related Supreme Court Cases</div>
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
      )}
    </div>
  );
}

export default App;































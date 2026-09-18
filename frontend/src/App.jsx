import { useState, useRef } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState([]);
  const [explanation, setExplanation] = useState("");
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const recognitionRef = useRef(null);

  const [uploadedDoc, setUploadedDoc] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [docQuestion, setDocQuestion] = useState("");
  const [docAnswer, setDocAnswer] = useState("");
  const [docAsking, setDocAsking] = useState(false);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setExplanation("");
    setResults([]);

    try {
      const response = await fetch(`${API_URL}/explain`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, top_k: 5 }),
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      setResults(data.results || []);
      setExplanation(data.explanation || "");
    } catch (err) {
      setError("Something went wrong. Make sure the backend server is running.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const startListening = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      setError("Voice input is not supported in this browser. Try Chrome.");
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = "en-IN";
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    recognition.onerror = () => {
      setIsListening(false);
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
    utterance.lang = "en-IN";
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

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_URL}/upload-pdf`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Server returned ${response.status}`);
      }

      const data = await response.json();
      setUploadedDoc(data);
    } catch (err) {
      setError("Could not upload the document. Make sure the backend server is running.");
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

      const data = await response.json();
      setDocAnswer(data.answer || data.error || "No answer returned.");
    } catch (err) {
      setDocAnswer("Something went wrong asking about the document.");
      console.error(err);
    } finally {
      setDocAsking(false);
    }
  };

  return (
    <div className="app">
      <header className="header">
        <h1>NyaayaSearch</h1>
        <p className="tagline">Understand Indian law in plain language</p>
      </header>

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
                <div className="dates-title">📅 Important Dates & Deadlines</div>
                {uploadedDoc.dates.map((d, i) => (
                  <div className="date-item" key={i}>
                    <span className="date-value">{d.value}</span>
                    <span className="date-description">{d.description}</span>
                  </div>
                ))}
              </div>
            )}

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
          🎤
        </button>
        <button type="submit" className="search-button" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {isListening && <div className="listening-indicator">Listening...</div>}

      {error && <div className="error">{error}</div>}

      {loading && (
        <div className="loading">
          Searching legal database and generating explanation...
        </div>
      )}

      {explanation && (
        <div className="explanation-card">
          <div className="explanation-header">
            <h2>Explanation</h2>
            <button className="listen-button" onClick={speakExplanation}>
              {isSpeaking ? "⏹ Stop" : "🔊 Listen"}
            </button>
          </div>
          <div className="explanation-text">{explanation}</div>
        </div>
      )}

      {results.length > 0 && (
        <div className="results-section">
          <h2>Sources</h2>
          {results.map((r, i) => (
            <div className="result-card" key={i}>
              <div className="result-header">
                <span className="act-name">{r.act_name}</span>
                <span className="section-number">Section {r.section_number}</span>
              </div>
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
          ))}
        </div>
      )}
    </div>
  );
}

export default App;

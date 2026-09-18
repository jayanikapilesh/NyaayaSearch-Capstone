import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [results, setResults] = useState([]);
  const [explanation, setExplanation] = useState("");

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

  return (
    <div className="app">
      <header className="header">
        <h1>NyaayaSearch</h1>
        <p className="tagline">Understand Indian law in plain language</p>
      </header>

      <form className="search-form" onSubmit={handleSearch}>
        <input
          type="text"
          className="search-input"
          placeholder="Describe your legal situation, e.g. 'landlord not returning deposit'"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
        />
        <button type="submit" className="search-button" disabled={loading}>
          {loading ? "Searching..." : "Search"}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {loading && (
        <div className="loading">
          Searching legal database and generating explanation...
        </div>
      )}

      {explanation && (
        <div className="explanation-card">
          <h2>Explanation</h2>
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

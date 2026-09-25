import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { API_URL } from "../constants";
import { extractErrorMessage } from "../utils";

function SimplifierTab({ setError }) {
  const [caseText, setCaseText] = useState("");
  const [simplifiedCase, setSimplifiedCase] = useState("");
  const [simplifying, setSimplifying] = useState(false);

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

  return (
    <div className="drafter-section">
      <h2>Case Simplifier</h2>
      <p className="drafter-intro">Paste a court judgment, order, or legal case text to get a plain-language explanation.</p>
      <form className="drafter-form" onSubmit={handleSimplifyCase}>
        <label className="sr-only" htmlFor="case-text">Case text to simplify</label>
        <textarea
          id="case-text"
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
  );
}

export default SimplifierTab;

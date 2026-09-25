import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { API_URL } from "../constants";
import { extractErrorMessage } from "../utils";

function BnsTab({ setError }) {
  const [bnsSectionInput, setBnsSectionInput] = useState("");
  const [bnsResult, setBnsResult] = useState(null);
  const [bnsLoading, setBnsLoading] = useState(false);

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

  return (
    <div className="drafter-section">
      <h2>BNS Decoder</h2>
      <p className="drafter-intro">Enter a Bharatiya Nyaya Sanhita (BNS) section number to see what it says, explained in plain language.</p>
      <form className="drafter-form" onSubmit={handleBnsLookup}>
        <label className="sr-only" htmlFor="bns-section">BNS section number</label>
        <input
          id="bns-section"
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
            <div className="citation-heading">
              <span className="citation-tag">
                <span className="citation-tag-label">Section</span>
                <span className="citation-tag-number">{bnsResult.section_number}</span>
              </span>
              <h3>{bnsResult.section_title}</h3>
            </div>
          </div>
          <div className="draft-text">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{bnsResult.explanation}</ReactMarkdown>
            <p className="bns-original-label">Original text:</p>
            <p className="bns-original-text">{bnsResult.legal_text}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default BnsTab;

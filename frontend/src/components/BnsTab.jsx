import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { API_URL } from "../constants";
import { extractErrorMessage } from "../utils";
import { getBnsContent } from "../bnsContent";

function BnsTab({ setError, uiLanguage = "en", pendingSection, onConsumePendingSection }) {
  const content = getBnsContent(uiLanguage);
  const [bnsSectionInput, setBnsSectionInput] = useState("");
  const [bnsResult, setBnsResult] = useState(null);
  const [bnsLoading, setBnsLoading] = useState(false);

  const runBnsLookup = async function (sectionNumber) {
    if (!sectionNumber.trim()) return;

    setBnsLoading(true);
    setError(null);
    setBnsResult(null);

    try {
      const response = await fetch(API_URL + "/bns-lookup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          section_number: sectionNumber.trim(),
          language: uiLanguage,
        }),
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

  const handleBnsLookup = function (e) {
    e.preventDefault();
    runBnsLookup(bnsSectionInput);
  };

  // "Look up this section" from a Search result hands us a section number to
  // look up immediately, rather than making the user retype it here.
  useEffect(function () {
    if (!pendingSection) return;
    const timer = setTimeout(function () {
      setBnsSectionInput(pendingSection);
      runBnsLookup(pendingSection);
      if (typeof onConsumePendingSection === "function") onConsumePendingSection();
    }, 0);
    return function () { clearTimeout(timer); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pendingSection]);

  return (
    <div className="drafter-section">
      <h2>{content.heading}</h2>
      <p className="drafter-intro">{content.intro}</p>
      <form className="drafter-form" onSubmit={handleBnsLookup}>
        <label className="sr-only" htmlFor="bns-section">{content.srLabel}</label>
        <input
          id="bns-section"
          type="text"
          className="search-input"
          placeholder={content.placeholder}
          value={bnsSectionInput}
          onChange={function (e) { setBnsSectionInput(e.target.value); }}
        />
        <button type="submit" className="search-button" disabled={bnsLoading}>
          {bnsLoading ? content.buttonLoading : content.buttonDecode}
        </button>
      </form>

      {bnsResult && (
        <div className="draft-result">
          <div className="draft-result-header">
            <div className="citation-heading">
              <span className="citation-tag">
                <span className="citation-tag-label">{content.sectionLabel}</span>{" "}
                <span className="citation-tag-number">{bnsResult.section_number}</span>
              </span>
              <h3>{bnsResult.section_title}</h3>
            </div>
          </div>
          <div className="draft-text">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{bnsResult.explanation}</ReactMarkdown>
            <p className="bns-original-label">{content.originalText}</p>
            <p className="bns-original-text">{bnsResult.legal_text}</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default BnsTab;


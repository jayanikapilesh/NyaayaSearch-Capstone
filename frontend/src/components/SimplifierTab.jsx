import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { API_URL } from "../constants";
import { extractErrorMessage } from "../utils";
import { getSimplifierContent } from "../simplifierContent";

function SimplifierTab({ setError, uiLanguage = "en", pendingCaseContext, onConsumePendingCaseContext }) {
  const content = getSimplifierContent(uiLanguage);
  const [caseText, setCaseText] = useState("");
  const [simplifiedCase, setSimplifiedCase] = useState("");
  const [simplifying, setSimplifying] = useState(false);
  const [caseContext, setCaseContext] = useState(null);

  // "Simplify this case" from a Search result only ever gives us the case's
  // citation metadata (title/court/date) - the app has no source for the
  // actual judgment text anywhere - so this shows that context as a banner
  // and leaves the textarea for the user to paste the real text into,
  // rather than pretending we can auto-fill a simplification.
  useEffect(function () {
    if (!pendingCaseContext) return;
    const timer = setTimeout(function () {
      setCaseContext(pendingCaseContext);
      setCaseText("");
      setSimplifiedCase("");
      if (typeof onConsumePendingCaseContext === "function") onConsumePendingCaseContext();
    }, 0);
    return function () { clearTimeout(timer); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pendingCaseContext]);

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
        const message = await extractErrorMessage(response, content.errDefault);
        setError(message);
        return;
      }

      const data = await response.json();
      setSimplifiedCase(data.simplified_explanation || "");
    } catch (err) {
      setError(content.errNetwork);
      console.error(err);
    } finally {
      setSimplifying(false);
    }
  };

  return (
    <div className="drafter-section">
      <h2>{content.heading}</h2>
      <p className="drafter-intro">{content.intro}</p>

      {caseContext && (
        <div className="case-context-banner">
          <div className="case-context-banner-text">
            <strong>{caseContext.title}</strong>
            <span> — {caseContext.court}{caseContext.decision_date ? ", " + caseContext.decision_date : ""}</span>
            <div>{content.caseContextHint}</div>
          </div>
          <button type="button" className="case-context-banner-dismiss" onClick={function () { setCaseContext(null); }} aria-label={content.caseContextDismiss}>×</button>
        </div>
      )}

      <form className="drafter-form" onSubmit={handleSimplifyCase}>
        <label className="sr-only" htmlFor="case-text">{content.textareaSrLabel}</label>
        <textarea
          id="case-text"
          className="drafter-textarea"
          placeholder={content.textareaPlaceholder}
          rows={10}
          value={caseText}
          onChange={function (e) { setCaseText(e.target.value); }}
        />
        <button type="submit" className="search-button" disabled={simplifying}>
          {simplifying ? content.submittingButton : content.submitButton}
        </button>
      </form>

      {simplifiedCase && (
        <div className="draft-result">
          <div className="draft-result-header">
            <h3>{content.resultHeading}</h3>
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

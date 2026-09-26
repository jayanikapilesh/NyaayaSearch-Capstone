import { useState } from "react";
import { API_URL } from "../constants";
import { extractErrorMessage } from "../utils";
import { getDictionaryContent } from "../dictionaryContent";

function DictionaryTab({ uiLanguage }) {
  const content = getDictionaryContent(uiLanguage);
  const [dictTerm, setDictTerm] = useState("");
  const [dictDefinition, setDictDefinition] = useState("");
  const [dictLoading, setDictLoading] = useState(false);

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
        const message = await extractErrorMessage(response, content.errDefault);
        setDictDefinition(message);
        return;
      }

      const data = await response.json();
      setDictDefinition(data.definition || content.notFoundFallback);
    } catch (err) {
      setDictDefinition(content.errNetwork);
      console.error(err);
    } finally {
      setDictLoading(false);
    }
  };

  return (
    <div className="dictionary-section">
      <h2>{content.heading}</h2>
      <form className="dict-form" onSubmit={handleDefine}>
        <label className="sr-only" htmlFor="dict-term">{content.srLabel}</label>
        <input
          id="dict-term"
          type="text"
          className="search-input"
          placeholder={content.placeholder}
          value={dictTerm}
          onChange={function (e) { setDictTerm(e.target.value); }}
        />
        <button type="submit" className="search-button" disabled={dictLoading}>
          {dictLoading ? content.buttonLookingUp : content.buttonDefine}
        </button>
      </form>
      {dictDefinition && <div className="dict-definition">{dictDefinition}</div>}
    </div>
  );
}

export default DictionaryTab;

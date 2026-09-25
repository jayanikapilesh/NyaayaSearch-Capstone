import { useState } from "react";
import { API_URL } from "../constants";
import { extractErrorMessage } from "../utils";

function DictionaryTab() {
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

  return (
    <div className="dictionary-section">
      <h2>Legal Dictionary</h2>
      <form className="dict-form" onSubmit={handleDefine}>
        <label className="sr-only" htmlFor="dict-term">Legal term to look up</label>
        <input
          id="dict-term"
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
  );
}

export default DictionaryTab;

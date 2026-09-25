import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Packer } from "docx";
import { saveAs } from "file-saver";
import { API_URL, MERGED_DOCUMENT_SCHEMAS, ALL_DOCUMENT_TYPE_LABELS } from "../constants";
import { extractErrorMessage } from "../utils";
import { buildDocxFromMarkdown } from "../docxExport";

function DrafterTab({ setError }) {
  const [draftType, setDraftType] = useState("rent_agreement");
  const [formValues, setFormValues] = useState({});
  const [genericDetails, setGenericDetails] = useState("");
  const [draftText, setDraftText] = useState("");
  const [drafting, setDrafting] = useState(false);

  const activeSchema = MERGED_DOCUMENT_SCHEMAS[draftType];

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

  return (
    <div className="drafter-section">
      <h2>Legal Document Generator</h2>
      <label className="drafter-intro" htmlFor="draft-type">What document do you want to create?</label>

      <select
        id="draft-type"
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
                        <label className="form-field-label" htmlFor={"field-" + field.key}>{field.label}</label>
                        {field.type === "textarea" ? (
                          <textarea
                            id={"field-" + field.key}
                            className="drafter-textarea"
                            placeholder={field.placeholder}
                            rows={2}
                            value={formValues[field.key] || ""}
                            onChange={function (e) { handleFormFieldChange(field.key, e.target.value); }}
                          />
                        ) : field.type === "select" ? (
                          <select
                            id={"field-" + field.key}
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
                            id={"field-" + field.key}
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
            <label className="drafter-subtitle" htmlFor="generic-details">
              This document type doesn't have a detailed form yet. Enter any details you'd like included, one per line (e.g. "name: John Doe") - anything you leave out will appear as a blank line to fill in later.
            </label>
            <textarea
              id="generic-details"
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
            <button className="search-button secondary-button" onClick={handleDownloadDraft}>Download as Word</button>
          </div>
          <div className="draft-text">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>{draftText}</ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
}

export default DrafterTab;

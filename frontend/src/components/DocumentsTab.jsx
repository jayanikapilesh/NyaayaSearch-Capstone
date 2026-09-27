import { useState } from "react";
import { API_URL } from "../constants";
import { extractErrorMessage } from "../utils";

const PRIVACY_NOTICES = {
  en: "Uploaded documents are sent to an AI service to answer your questions; don't upload sensitive personal documents.",
  hi: "अपलोड किए गए दस्तावेज़ आपके प्रश्नों के उत्तर देने के लिए एक एआई सेवा को भेजे जाते हैं; संवेदनशील व्यक्तिगत दस्तावेज़ अपलोड न करें।",
  kn: "ನಿಮ್ಮ ಪ್ರಶ್ನೆಗಳಿಗೆ ಉತ್ತರಿಸಲು ಅಪ್‌ಲೋಡ್ ಮಾಡಿದ ದಾಖಲೆಗಳನ್ನು AI ಸೇವೆಗೆ ಕಳುಹಿಸಲಾಗುತ್ತದೆ; ಸೂಕ್ಷ್ಮ ವೈಯಕ್ತಿಕ ದಾಖಲೆಗಳನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಬೇಡಿ.",
};

function DocumentsTab({ setError, uiLanguage = "en" }) {
  const [uploadedDoc, setUploadedDoc] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [docQuestion, setDocQuestion] = useState("");
  const [docAnswer, setDocAnswer] = useState("");
  const [docAsking, setDocAsking] = useState(false);

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

  return (
    <div className="upload-section">
      <h2>Ask about your own document</h2>
      <p className="document-privacy-notice" style={{ fontSize: "0.85rem", color: "var(--text-secondary, #666)", marginBottom: "1rem", lineHeight: "1.4" }}>
        {PRIVACY_NOTICES[uiLanguage] || PRIVACY_NOTICES.en}
      </p>
      <label className="sr-only" htmlFor="pdf-upload">Upload a PDF document</label>
      <input id="pdf-upload" className="file-input" type="file" accept="application/pdf" onChange={handleFileUpload} />
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
              <label className="sr-only" htmlFor="doc-question">Ask a question about this document</label>
              <input
                id="doc-question"
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
  );
}

export default DocumentsTab;

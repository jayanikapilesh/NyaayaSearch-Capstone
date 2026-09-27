import { useEffect, useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Packer } from "docx";
import { saveAs } from "file-saver";
import { API_URL } from "../constants";
import {
  extractErrorMessage,
  loadUploadedDocs,
  saveUploadedDocs,
  loadGeneratedDocs,
  saveGeneratedDocs,
  loadSavedResults,
} from "../utils";
import { buildDocxFromMarkdown } from "../docxExport";
import { getDocumentsContent } from "../documentsContent";
import { UploadIcon, BookmarkIcon } from "./icons";

function formatDate(iso) {
  try {
    return new Date(iso).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
  } catch (e) {
    return "";
  }
}

function DocumentsTab({ setError, uiLanguage = "en", isActive, onOpenSavedSearch }) {
  const content = getDocumentsContent(uiLanguage);
  const [selectedFileName, setSelectedFileName] = useState("");
  const [uploadedDoc, setUploadedDoc] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [docQuestion, setDocQuestion] = useState("");
  const [docAnswer, setDocAnswer] = useState("");
  const [docAsking, setDocAsking] = useState(false);
  const [dragActive, setDragActive] = useState(false);

  const [uploadedDocsList, setUploadedDocsList] = useState(function () { return loadUploadedDocs(); });
  const [generatedDocsList, setGeneratedDocsList] = useState(function () { return loadGeneratedDocs(); });
  const [savedSearchesList, setSavedSearchesList] = useState(function () { return loadSavedResults(); });
  const [expandedGeneratedId, setExpandedGeneratedId] = useState(null);
  const [confirmingDelete, setConfirmingDelete] = useState(null); // { type: "upload" | "generated", id }

  // Uploaded docs can be added here, but generated documents are added from
  // the Drafter tab while this tab sits hidden in the background - every tab
  // stays mounted for the app's lifetime, so refresh from storage whenever
  // the user actually switches to this tab rather than only once at mount.
  useEffect(function () {
    if (!isActive) return;
    const timer = setTimeout(function () {
      setUploadedDocsList(loadUploadedDocs());
      setGeneratedDocsList(loadGeneratedDocs());
      setSavedSearchesList(loadSavedResults());
    }, 0);
    return function () { clearTimeout(timer); };
  }, [isActive]);

  const uploadFile = async function (file) {
    if (!file) return;

    setSelectedFileName(file.name);
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
        const message = await extractErrorMessage(response, content.errUpload);
        setError(message);
        return;
      }

      const data = await response.json();
      setUploadedDoc(data);

      if (data.document_id) {
        setUploadedDocsList(function (prev) {
          const withoutDupe = prev.filter(function (d) { return d.document_id !== data.document_id; });
          const entry = {
            document_id: data.document_id,
            filename: data.filename,
            summary: data.summary,
            dates: data.dates || [],
            uploadedAt: new Date().toISOString(),
          };
          const updated = [entry].concat(withoutDupe);
          saveUploadedDocs(updated);
          return updated;
        });
      }
    } catch (err) {
      setError(content.errNetworkUpload);
      console.error(err);
    } finally {
      setUploading(false);
    }
  };

  const handleFileInputChange = function (e) {
    uploadFile(e.target.files[0]);
  };

  const handleDrop = function (e) {
    e.preventDefault();
    setDragActive(false);
    const file = e.dataTransfer.files && e.dataTransfer.files[0];
    if (file) uploadFile(file);
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
        const message = await extractErrorMessage(response, content.errAsk);
        setDocAnswer(message);
        return;
      }

      const data = await response.json();
      setDocAnswer(data.answer || content.noAnswerFallback);
    } catch (err) {
      setDocAnswer(content.errNetworkAsk);
      console.error(err);
    } finally {
      setDocAsking(false);
    }
  };

  const handleOpenUploadedDoc = function (entry) {
    setUploadedDoc({
      document_id: entry.document_id,
      filename: entry.filename,
      summary: entry.summary,
      dates: entry.dates,
    });
    setSelectedFileName(entry.filename);
    setDocQuestion("");
    setDocAnswer("");
  };

  const handleDeleteUploadedDoc = function (documentId) {
    setUploadedDocsList(function (prev) {
      const updated = prev.filter(function (d) { return d.document_id !== documentId; });
      saveUploadedDocs(updated);
      return updated;
    });
    if (uploadedDoc && uploadedDoc.document_id === documentId) {
      setUploadedDoc(null);
    }
    setConfirmingDelete(null);
  };

  const handleDeleteGeneratedDoc = function (id) {
    setGeneratedDocsList(function (prev) {
      const updated = prev.filter(function (d) { return d.id !== id; });
      saveGeneratedDocs(updated);
      return updated;
    });
    if (expandedGeneratedId === id) setExpandedGeneratedId(null);
    setConfirmingDelete(null);
  };

  const handleDownloadGenerated = async function (entry) {
    const doc = buildDocxFromMarkdown(entry.document_text);
    const blob = await Packer.toBlob(doc);
    saveAs(blob, (entry.documentType || "document") + ".docx");
  };

  return (
    <div className="upload-section">
      <h2>{content.heading}</h2>
      <p className="document-privacy-notice">{content.privacyNotice}</p>

      <label
        className={"dropzone" + (dragActive ? " dropzone-active" : "") + (selectedFileName ? " dropzone-has-file" : "")}
        htmlFor="pdf-upload"
        onDragOver={function (e) { e.preventDefault(); setDragActive(true); }}
        onDragLeave={function () { setDragActive(false); }}
        onDrop={handleDrop}
      >
        <UploadIcon className="dropzone-icon" />
        <span className="dropzone-text">{selectedFileName || content.dropzoneHint}</span>
        <span className="dropzone-hint">{selectedFileName ? content.changeFileHint : content.dropzoneFileTypeHint}</span>
        <span className="sr-only">{content.uploadSrLabel}</span>
        <input
          id="pdf-upload"
          className="dropzone-input"
          type="file"
          accept="application/pdf"
          onChange={handleFileInputChange}
        />
      </label>

      {uploading && <div className="loading">{content.uploading}</div>}

      {uploadedDoc && (
        <div className="document-card">
          <div className="document-filename">{uploadedDoc.filename}</div>
          <div className="document-summary">{uploadedDoc.summary}</div>

          {uploadedDoc.dates && uploadedDoc.dates.length > 0 && (
            <div className="dates-section">
              <div className="dates-title">{content.datesHeading}</div>
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
              <label className="sr-only" htmlFor="doc-question">{content.questionSrLabel}</label>
              <input
                id="doc-question"
                type="text"
                className="search-input"
                placeholder={content.questionPlaceholder}
                value={docQuestion}
                onChange={function (e) { setDocQuestion(e.target.value); }}
              />
              <button type="submit" className="search-button" disabled={docAsking}>
                {docAsking ? content.askingButton : content.askButton}
              </button>
            </form>
          )}

          {docAnswer && <div className="document-answer">{docAnswer}</div>}
          {uploadedDoc.document_id && <p className="document-reupload-hint">{content.reuploadHint}</p>}
        </div>
      )}

      <div className="my-documents-lists">
        <p className="my-documents-intro">{content.myDocsIntro}</p>

        <div className="document-list-section document-list-section-featured">
          <h3 className="document-list-heading document-list-heading-featured">
            <BookmarkIcon className="document-list-heading-icon" />
            {content.savedSearchesListHeading}
          </h3>
          {savedSearchesList.length === 0 ? (
            <p className="document-list-empty">{content.savedSearchesListEmpty}</p>
          ) : (
            savedSearchesList.map(function (entry) {
              return (
                <div className="document-list-item" key={entry.id}>
                  <div className="document-list-item-main">
                    <span className="document-list-item-title">{entry.query}</span>
                    <span className="document-list-item-meta">{content.savedOnLabel} {formatDate(entry.savedAt)}</span>
                  </div>
                  <div className="document-list-item-actions">
                    <button
                      type="button"
                      className="document-list-action"
                      onClick={function () {
                        if (typeof onOpenSavedSearch === "function") onOpenSavedSearch(entry.id);
                      }}
                    >
                      {content.viewInSearchButton}
                    </button>
                  </div>
                </div>
              );
            })
          )}
        </div>

        <div className="document-list-section">
          <h3 className="document-list-heading">{content.uploadedListHeading}</h3>
          {uploadedDocsList.length === 0 ? (
            <p className="document-list-empty">{content.uploadedListEmpty}</p>
          ) : (
            uploadedDocsList.map(function (entry) {
              return (
                <div className="document-list-item" key={entry.document_id}>
                  <div className="document-list-item-main">
                    <span className="document-list-item-title">{entry.filename}</span>
                    <span className="document-list-item-meta">{content.uploadedOnLabel} {formatDate(entry.uploadedAt)}</span>
                  </div>
                  <div className="document-list-item-actions">
                    <button type="button" className="document-list-action" onClick={function () { handleOpenUploadedDoc(entry); }}>
                      {content.openButton}
                    </button>
                    {confirmingDelete && confirmingDelete.type === "upload" && confirmingDelete.id === entry.document_id ? (
                      <span className="saved-result-confirm">
                        <span className="saved-result-confirm-label">{content.deleteUploadedConfirm}</span>
                        <button type="button" className="saved-result-confirm-yes" onClick={function () { handleDeleteUploadedDoc(entry.document_id); }}>
                          {content.deleteConfirmYes}
                        </button>
                        <button type="button" className="saved-result-confirm-cancel" onClick={function () { setConfirmingDelete(null); }}>
                          {content.cancelButton}
                        </button>
                      </span>
                    ) : (
                      <button type="button" className="saved-result-delete" onClick={function () { setConfirmingDelete({ type: "upload", id: entry.document_id }); }}>
                        {content.deleteButton}
                      </button>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </div>

        <div className="document-list-section">
          <h3 className="document-list-heading">{content.generatedListHeading}</h3>
          {generatedDocsList.length === 0 ? (
            <p className="document-list-empty">{content.generatedListEmpty}</p>
          ) : (
            generatedDocsList.map(function (entry) {
              return (
                <div className="document-list-item document-list-item-stacked" key={entry.id}>
                  <div className="document-list-item-row">
                    <div className="document-list-item-main">
                      <span className="document-list-item-title">{entry.label}</span>
                      <span className="document-list-item-meta">{content.generatedOnLabel} {formatDate(entry.createdAt)}</span>
                    </div>
                    <div className="document-list-item-actions">
                      <button
                        type="button"
                        className="document-list-action"
                        onClick={function () { setExpandedGeneratedId(expandedGeneratedId === entry.id ? null : entry.id); }}
                      >
                        {content.openButton}
                      </button>
                      <button type="button" className="document-list-action" onClick={function () { handleDownloadGenerated(entry); }}>
                        {content.downloadButton}
                      </button>
                      {confirmingDelete && confirmingDelete.type === "generated" && confirmingDelete.id === entry.id ? (
                        <span className="saved-result-confirm">
                          <span className="saved-result-confirm-label">{content.deleteGeneratedConfirm}</span>
                          <button type="button" className="saved-result-confirm-yes" onClick={function () { handleDeleteGeneratedDoc(entry.id); }}>
                            {content.deleteConfirmYes}
                          </button>
                          <button type="button" className="saved-result-confirm-cancel" onClick={function () { setConfirmingDelete(null); }}>
                            {content.cancelButton}
                          </button>
                        </span>
                      ) : (
                        <button type="button" className="saved-result-delete" onClick={function () { setConfirmingDelete({ type: "generated", id: entry.id }); }}>
                          {content.deleteButton}
                        </button>
                      )}
                    </div>
                  </div>
                  {expandedGeneratedId === entry.id && (
                    <div className="document-list-item-expanded draft-text">
                      <ReactMarkdown remarkPlugins={[remarkGfm]}>{entry.document_text}</ReactMarkdown>
                    </div>
                  )}
                </div>
              );
            })
          )}
        </div>
      </div>
    </div>
  );
}

export default DocumentsTab;

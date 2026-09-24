import { Document, Paragraph, TextRun, HeadingLevel } from "docx";
import { HISTORY_KEY, SAVED_RESULTS_KEY } from "./constants";

export function getConfidenceLabel(score, topScore) {
  const ratio = topScore > 0 ? score / topScore : 0;
  if (ratio >= 0.95) return { label: "Strong match", className: "confidence-strong" };
  if (ratio >= 0.8) return { label: "Good match", className: "confidence-good" };
  return { label: "Possible match", className: "confidence-weak" };
}

export function isOverallLowConfidence(topScore) {
  return topScore < 0.75;
}

export async function extractErrorMessage(response, fallback) {
  try {
    const data = await response.json();
    if (data.detail) return data.detail;
  } catch (e) {
    return fallback;
  }
  return fallback;
}

export function loadHistory() {
  try {
    const raw = localStorage.getItem(HISTORY_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
}

export function saveHistory(history) {
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(history));
  } catch (e) {
    return;
  }
}

export function loadSavedResults() {
  try {
    const raw = localStorage.getItem(SAVED_RESULTS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
}

export function persistSavedResults(items) {
  try {
    localStorage.setItem(SAVED_RESULTS_KEY, JSON.stringify(items));
  } catch (e) {
    return;
  }
}

export function buildDocxFromMarkdown(markdownText) {
  const lines = markdownText.split("\n");
  const paragraphs = [];

  const parseBoldRuns = (text) => {
    const parts = text.split(/(\*\*[^*]+\*\*)/g).filter(Boolean);
    return parts.map((part) => {
      if (part.startsWith("**") && part.endsWith("**")) {
        return new TextRun({ text: part.slice(2, -2), bold: true });
      }
      return new TextRun(part);
    });
  };

  for (const rawLine of lines) {
    const line = rawLine.replace(/\s+$/, "");

    if (line.startsWith("# ")) {
      paragraphs.push(new Paragraph({ text: line.slice(2), heading: HeadingLevel.TITLE, spacing: { after: 200 } }));
    } else if (line.startsWith("## ")) {
      paragraphs.push(new Paragraph({ text: line.slice(3), heading: HeadingLevel.HEADING_1, spacing: { before: 200, after: 100 } }));
    } else if (line.startsWith("### ")) {
      paragraphs.push(new Paragraph({ text: line.slice(4), heading: HeadingLevel.HEADING_2, spacing: { before: 150, after: 80 } }));
    } else if (line.trim() === "") {
      paragraphs.push(new Paragraph({ text: "" }));
    } else {
      paragraphs.push(new Paragraph({ children: parseBoldRuns(line), spacing: { after: 100 } }));
    }
  }

  return new Document({
    sections: [{ properties: {}, children: paragraphs }],
  });
}

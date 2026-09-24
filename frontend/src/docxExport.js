import { Document, Paragraph, TextRun, HeadingLevel } from "docx";

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

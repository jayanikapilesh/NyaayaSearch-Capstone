import { HISTORY_KEY, SAVED_RESULTS_KEY, UPLOADED_DOCS_KEY, GENERATED_DOCS_KEY, MAX_STORED_DOCS, PINNED_QUERIES_KEY, KNOWN_LEGAL_TERMS, DAILY_QUIZ_KEY, UI_STRINGS } from "./constants";

export function t(lang, key) {
  return (UI_STRINGS[lang] && UI_STRINGS[lang][key]) || UI_STRINGS.en[key];
}

export function getConfidenceLabel(score, topScore, lang) {
  const ratio = topScore > 0 ? score / topScore : 0;
  if (ratio >= 0.95) return { label: t(lang, "strongMatch"), className: "confidence-strong" };
  if (ratio >= 0.8) return { label: t(lang, "goodMatch"), className: "confidence-good" };
  return { label: t(lang, "possibleMatch"), className: "confidence-weak" };
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


export function loadUploadedDocs() {
  try {
    const raw = localStorage.getItem(UPLOADED_DOCS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
}

export function saveUploadedDocs(items) {
  try {
    localStorage.setItem(UPLOADED_DOCS_KEY, JSON.stringify(items.slice(0, MAX_STORED_DOCS)));
  } catch (e) {
    return;
  }
}

export function loadGeneratedDocs() {
  try {
    const raw = localStorage.getItem(GENERATED_DOCS_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
}

export function saveGeneratedDocs(items) {
  try {
    localStorage.setItem(GENERATED_DOCS_KEY, JSON.stringify(items.slice(0, MAX_STORED_DOCS)));
  } catch (e) {
    return;
  }
}

// Kept as a plain module-level function (not inlined in DrafterTab's submit
// handler) so the only place that reads the wall clock lives outside any
// component body.
export function recordGeneratedDocument(documentType, label, documentText) {
  const entry = {
    id: Date.now(),
    documentType: documentType,
    label: label,
    document_text: documentText,
    createdAt: new Date().toISOString(),
  };
  const existing = loadGeneratedDocs();
  saveGeneratedDocs([entry].concat(existing));
  return entry;
}

export function loadPinnedQueries() {
  try {
    const raw = localStorage.getItem(PINNED_QUERIES_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch (e) {
    return [];
  }
}


export function savePinnedQueries(queries) {
  try {
    localStorage.setItem(PINNED_QUERIES_KEY, JSON.stringify(queries));
  } catch (e) {
    return;
  }
}

function levenshteinDistance(a, b) {
  const rows = a.length + 1;
  const cols = b.length + 1;
  const dist = Array.from({ length: rows }, function (_row, i) {
    return [i].concat(new Array(cols - 1).fill(0));
  });
  for (let j = 1; j < cols; j++) dist[0][j] = j;
  for (let i = 1; i < rows; i++) {
    for (let j = 1; j < cols; j++) {
      const cost = a[i - 1] === b[j - 1] ? 0 : 1;
      dist[i][j] = Math.min(
        dist[i - 1][j] + 1,
        dist[i][j - 1] + 1,
        dist[i - 1][j - 1] + cost
      );
    }
  }
  return dist[rows - 1][cols - 1];
}

// Catches an obvious single-word typo against KNOWN_LEGAL_TERMS (a small,
// curated list - see constants.js - not a general English dictionary, so
// this never flags a correctly-spelled legal term as wrong). Returns null
// when nothing looks like a typo, so callers can render nothing rather than
// a misleading always-on suggestion.
export function getSpellingSuggestion(searchQuery, knownTerms = KNOWN_LEGAL_TERMS) {
  if (!searchQuery || !searchQuery.trim()) return null;
  const knownSet = new Set(knownTerms.map(function (w) { return w.toLowerCase(); }));
  const words = searchQuery.match(/[a-zA-Z]+/g) || [];

  for (const word of words) {
    const lower = word.toLowerCase();
    if (lower.length < 4 || knownSet.has(lower)) continue;

    let bestMatch = null;
    let bestDistance = Infinity;
    for (const term of knownTerms) {
      const distance = levenshteinDistance(lower, term.toLowerCase());
      if (distance < bestDistance) {
        bestDistance = distance;
        bestMatch = term;
      }
    }

    const maxAllowedDistance = lower.length >= 7 ? 2 : 1;
    if (bestMatch && bestDistance > 0 && bestDistance <= maxAllowedDistance) {
      const correctedQuery = searchQuery.replace(word, bestMatch);
      return { originalWord: word, suggestedWord: bestMatch, correctedQuery: correctedQuery };
    }
  }

  return null;
}

export function loadDailyQuizState() {
  try {
    const raw = localStorage.getItem(DAILY_QUIZ_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch (e) {
    return null;
  }
}

export function saveDailyQuizState(state) {
  try {
    localStorage.setItem(DAILY_QUIZ_KEY, JSON.stringify(state));
  } catch (e) {
    return;
  }
}

// "Today" as a plain date-only key (local time). This is the one place that
// reads the real clock for the daily quiz - kept in a standalone exported
// function, never called directly from a component body, matching the
// react-hooks/purity fix used for recordGeneratedDocument above.
export function getTodayDateKey() {
  const now = new Date();
  const year = now.getFullYear();
  const month = String(now.getMonth() + 1).padStart(2, "0");
  const day = String(now.getDate()).padStart(2, "0");
  return year + "-" + month + "-" + day;
}

// Deterministic day-count derived from a date key (not the live clock), so
// this is pure given its argument and safe to call from anywhere, including
// component render bodies.
function daysSinceEpoch(dateKey) {
  const [year, month, day] = dateKey.split("-").map(Number);
  return Math.floor(Date.UTC(year, month - 1, day) / 86400000);
}

export function daysBetweenDateKeys(laterKey, earlierKey) {
  return daysSinceEpoch(laterKey) - daysSinceEpoch(earlierKey);
}

// Same date key always maps to the same question, and the rotation moves
// through the whole existing question bank (quizData.js) one per day before
// wrapping around, rather than picking randomly or always showing #1.
export function getDailyQuizIndex(dateKey, totalQuestions) {
  const dayCount = daysSinceEpoch(dateKey);
  return ((dayCount % totalQuestions) + totalQuestions) % totalQuestions;
}

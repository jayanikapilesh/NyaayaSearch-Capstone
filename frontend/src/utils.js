import { HISTORY_KEY, SAVED_RESULTS_KEY, UI_STRINGS } from "./constants";

export function t(lang, key) {
  return (UI_STRINGS[lang] && UI_STRINGS[lang][key]) || UI_STRINGS.en[key];
}

export function getConfidenceLabel(score, topScore, lang) {
  const ratio = topScore > 0 ? score / topScore : 0;
  if (ratio >= 0.95) return { label: t(lang, "strongMatch"), className: "confidence-strong" };
  if (ratio >= 0.8) return { label: t(lang, "goodMatch"), className: "confidence-good" };
  return { label: t(lang, "possibleMatch"), className: "confidence-weak" };
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


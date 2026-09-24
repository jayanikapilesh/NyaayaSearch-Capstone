import { DOCUMENT_SCHEMAS, ADDITIONAL_DOCUMENT_SCHEMAS } from "./documentSchemas";

export const API_URL = "http://127.0.0.1:8000";
export const HISTORY_KEY = "nyaaya-search-history";
export const MAX_HISTORY = 8;
export const SAVED_RESULTS_KEY = "nyaaya-saved-results";

export const LANGUAGE_LABELS = {
  en: "English",
  hi: "हिंदी",
  kn: "ಕನ್ನಡ",
};

export const ALL_LANGUAGES = ["en", "hi", "kn"];

export const MERGED_DOCUMENT_SCHEMAS = Object.assign({}, DOCUMENT_SCHEMAS, ADDITIONAL_DOCUMENT_SCHEMAS);

export const ALL_DOCUMENT_TYPE_LABELS = {
  ...Object.fromEntries(Object.entries(MERGED_DOCUMENT_SCHEMAS).map(([key, schema]) => [key, schema.label])),
};

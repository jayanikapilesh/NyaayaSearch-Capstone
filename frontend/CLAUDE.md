# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

This directory is the frontend of NyaayaSearch, an Indian legal-assistance web app. It's a single-page React app (Vite) that talks to a separate FastAPI backend (`../scripts/main.py` in the parent repo) running at `http://127.0.0.1:8000` — that URL is hardcoded as `API_URL` in `src/App.jsx`. The backend must be running separately for any feature in this app to work; this directory has no backend code of its own.

## Commands

Run from this directory (`frontend/`):

- `npm run dev` — start the Vite dev server
- `npm run build` — production build
- `npm run preview` — preview the production build
- `npm run lint` — run ESLint (flat config in `eslint.config.js`)

There is no test suite configured in this project (no test script, no test runner dependency).

## Architecture

**Single-component app.** Nearly all UI and state lives in one file, `src/App.jsx` (~1200 lines) — there is no router and no component directory; the app is a tab switcher over one big function component. State is plain `useState`/`useEffect`, no external state library.

**Tabs (`activeTab`)**, each corresponding to a backend endpoint:
- `search` → `POST /explain` (and `POST /translate-explanation` for re-translating an existing answer)
- `drafter` (Document Generator) → `POST /draft-document`, form driven by `src/documentSchemas.js`
- `dictionary` → `POST /define`
- `documents` (My Documents) → local view over `localStorage`-saved search results, plus `POST /upload-pdf` and `POST /ask-document` for the uploaded-PDF Q&A flow
- `simplifier` (Case Simplifier) → `POST /simplify-case`
- `emergency` (Emergency Help) → static content, no backend call
- `bns` (BNS Decoder) → `POST /bns-lookup`
- `quiz` (Legal IQ Daily) → static questions from `src/quizData.js`, no backend call

**Document generation (`src/documentSchemas.js`)** is a data-driven form system: `DOCUMENT_SCHEMAS` and `ADDITIONAL_DOCUMENT_SCHEMAS` each map a document type key to `{ label, sections: [{ title, fields: [{ key, label, type, placeholder?, options? }] }] }`. `App.jsx` merges these (`MERGED_DOCUMENT_SCHEMAS`) and renders the form dynamically from the schema — adding a new document type means adding an entry here, not writing new form JSX. `GENERIC_DOCUMENT_TYPES` covers document types without a structured schema (free-text "details" field instead of per-field inputs).

**Client-side .docx export.** `buildDocxFromMarkdown()` in `App.jsx` hand-parses the markdown returned by the backend (headings `#`/`##`/`###`, `**bold**`, blank lines) into a `docx` library `Document`, then saves it via `file-saver`. This is a small bespoke markdown→docx converter, not a full markdown parser — if the backend's markdown output format changes, this function needs to stay in sync.

**Client-side persistence** (`localStorage`, no backend involved):
- `nyaaya-search-history` — recent queries (capped at `MAX_HISTORY = 8`)
- `nyaaya-saved-results` — saved search results (query + explanation + language)
- `nyaaya-dark-mode` — theme toggle

**Multilingual support.** The app supports English/Hindi/Kannada (`ALL_LANGUAGES = ["en", "hi", "kn"]`). Explanations are cached per-language in `explanationCache` so switching languages doesn't require re-hitting the backend if already translated.

**Voice I/O.** Search supports browser speech recognition for input and speech synthesis for reading answers aloud (`isListening`/`isSpeaking`/`recognitionRef`), using the Web Speech API directly — no external library.

**Styling** is a single global stylesheet, `src/App.css` (~1200 lines), plus `src/index.css` for base/reset styles. There's no CSS-in-JS or CSS modules.
## Rules

- `App.jsx` is large. Make small, targeted edits. Never rewrite or reformat the whole file.
- Don't rename or change any backend endpoint path or request/response shape. The backend in `../scripts/main.py` depends on them.
- Every user-facing feature must keep working in English, Hindi and Kannada.
- Don't read `.env` files or print API keys.
- Ask before adding any new npm dependency.

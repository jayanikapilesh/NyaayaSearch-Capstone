import re
import os
import numpy as np
import openpyxl
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

DATASET = os.path.join(os.path.dirname(__file__), "..", "Legal_Knowledge_Base_combined.xlsx")

STOP_WORDS = {
    "the", "a", "an", "is", "are", "am", "my", "me", "i",
    "what", "which", "who", "how", "can", "could", "would",
    "should", "do", "does", "did", "if", "to", "of", "for",
    "and", "or", "in", "on", "with", "from", "about", "law",
    "legal", "rights", "section", "not"
}

SYNONYMS = {
    "landlord": ["landlord", "owner", "house owner"],
    "tenant": ["tenant", "renter", "renting"],
    "deposit": ["deposit", "security deposit", "rental deposit"],
    "return": ["return", "refund", "repay", "give back"],
    "rent": ["rent", "rental", "lease", "tenancy"],
    "threat": ["threat", "coercion", "intimidation", "forced", "duress"],
    "forced": ["forced", "coercion", "duress", "threat"],
    "agreement": ["agreement", "contract", "obligation"],
    "not fulfilling": ["not fulfilling", "breach", "default", "non-performance"],
    "minor": ["minor", "child", "underage", "competent to contract"],
    "hacked": ["hacked", "unauthorized access", "computer offence"],
    "stole data": ["stole data", "data theft", "data breach"],
    "blackmail": ["blackmail", "privacy violation", "obscene", "extortion"],
    "fake account": ["fake account", "impersonation", "identity theft", "cheating by personation"],
    "impersonat": ["impersonat", "identity theft", "cheating by personation"],
    "licence": ["licence", "license", "driving licence", "revocation"],
    "suspended": ["suspended", "revoked", "revocation", "disqualification"],
    "won't complete": ["won't complete", "specific performance", "breach of contract"],
    "sale": ["sale", "contract of sale", "transfer"],
    "stop someone": ["stop someone", "injunction", "restrain"],
    "harmful": ["harmful", "injunction", "wrongful act"],
    "defend myself": ["defend myself", "private defence", "self-defence"],
    "attacked": ["attacked", "assault", "hurt", "criminal force"],
    "fir": ["fir", "first information report", "cognizable offence", "information to police"],
    "arrest": ["arrest", "arrested", "custody", "detention"],
    "warrant": ["warrant", "arrest without warrant", "cognizable"],
    "own it": ["own it", "ostensible owner", "title", "ownership"],
    "seller doesn't own": ["seller doesn't own", "ostensible owner", "fraudulent transfer"]
}


def tokenize(text):
    words = re.findall(r"[a-zA-Z]+", text.lower())
    return [word for word in words if word not in STOP_WORDS]


def expand_query(query):
    query_lower = query.lower()
    expanded = query_lower
    for key, values in SYNONYMS.items():
        if key in query_lower:
            expanded += " " + " ".join(values)
    return expanded


def find_matched_terms(query_tokens, section_text, max_terms=5):
    """Find which query keywords actually appear in this section's text -
    used to show the user WHY a result matched, not just a score."""
    text_tokens = set(tokenize(section_text))
    matched = [t for t in dict.fromkeys(query_tokens) if t in text_tokens]
    return matched[:max_terms]


class SearchEngine:
    def __init__(self):
        print("Loading legal dataset...")
        wb = openpyxl.load_workbook(DATASET, read_only=True)
        ws = wb.active

        headers = list(next(ws.values))
        records = []

        for row in ws.iter_rows(values_only=True):
            record = dict(zip(headers, row))
            title = str(record.get("section_title") or "").strip().lower()
            if title in {"repeal.", "[repealed.]", "[repealed .].", "[omitted.]."}:
                continue
            records.append(record)

        print("Legal records loaded:", len(records))
        self.records = records

        documents = []
        texts = []
        for record in records:
            tok_text = (
                str(record.get("act_name") or "") + " " +
                str(record.get("section_number") or "") + " " +
                str(record.get("section_title") or "") + " " +
                str(record.get("legal_text") or "")
            )
            documents.append(tokenize(tok_text))

            embed_text = (
                str(record.get("act_name") or "") + ". " +
                str(record.get("section_title") or "") + ". " +
                str(record.get("legal_text") or "")
            )
            texts.append(embed_text)

        print("Creating BM25 index...")
        self.bm25 = BM25Okapi(documents)

        print("Creating semantic embeddings...")
        self.model = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        self.embeddings = self.model.encode(
            texts, normalize_embeddings=True, show_progress_bar=True
        )
        print("Search system ready.")

    def search(self, query, top_k=5):
        expanded_query = expand_query(query)
        query_tokens = tokenize(expanded_query)

        bm25_scores = np.array(self.bm25.get_scores(query_tokens), dtype=float)
        if bm25_scores.max() > 0:
            bm25_scores = bm25_scores / bm25_scores.max()

        query_embedding = self.model.encode(
            [expanded_query], normalize_embeddings=True
        )[0]
        semantic_scores = np.dot(self.embeddings, query_embedding)
        semantic_scores = np.clip(semantic_scores, 0, 1)

        boost = np.ones(len(self.records))
        query_lower = query.lower()

        for i, record in enumerate(self.records):
            title = str(record.get("section_title") or "").lower()
            legal_text = str(record.get("legal_text") or "").lower()
            act_name = str(record.get("act_name") or "").lower()
            combined = title + " " + legal_text + " " + act_name

            if "landlord" in query_lower and "landlord" in combined:
                boost[i] *= 1.25
            if "tenant" in query_lower and "tenant" in combined:
                boost[i] *= 1.25
            if "security deposit" in query_lower:
                if "security" in combined and "deposit" in combined:
                    boost[i] *= 1.5
            if "return" in query_lower or "refund" in query_lower:
                if any(word in combined for word in ["return", "refund", "repay"]):
                    boost[i] *= 1.2

        final_scores = (0.15 * bm25_scores) + (0.85 * semantic_scores)

        if "landlord" in query_lower or "tenant" in query_lower:
            for i, record in enumerate(self.records):
                text = (
                    str(record.get("section_title") or "") + " " +
                    str(record.get("legal_text") or "")
                ).lower()
                if any(word in text for word in [
                    "tenant", "landlord", "lessee", "lessor", "rent", "lease", "tenancy"
                ]):
                    final_scores[i] *= 1.5
                if "security deposit" in query_lower:
                    if "deposit" not in text:
                        final_scores[i] *= 0.3

        final_scores = final_scores * boost

        top_indices = np.argsort(final_scores)[::-1][:top_k]

        results = []
        for index in top_indices:
            record = self.records[index]
            section_text = (
                str(record.get("section_title") or "") + " " +
                str(record.get("legal_text") or "")
            )
            matched_terms = find_matched_terms(query_tokens, section_text)

            results.append({
                "act_name": record.get("act_name"),
                "section_number": record.get("section_number"),
                "section_title": record.get("section_title"),
                "legal_text": record.get("legal_text"),
                "hybrid_score": float(final_scores[index]),
                "semantic_score": float(semantic_scores[index]),
                "bm25_score": float(bm25_scores[index]),
                "matched_terms": matched_terms,
            })
        return results

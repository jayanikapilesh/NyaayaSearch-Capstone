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
    "doesn't own": ["doesn't own", "ostensible owner", "fraudulent transfer"],
    "seller doesn't own": ["seller doesn't own", "ostensible owner", "fraudulent transfer"],
    "stop": ["stop", "injunction", "restrain", "prevent"],
    "court order": ["court order", "injunction", "perpetual injunction"],
    "lying": ["lying", "misrepresentation", "false statement", "suppression of fact"],
    "break": ["break", "breach", "forfeit", "violate", "default"],
    "show up": ["show up", "appear", "attendance", "present"],
    "appeal": ["appeal", "revision", "review", "challenge decision"],
    "review": ["review", "revision", "reconsider", "appeal"],
    "bail bond": ["bail bond", "bond", "surety", "forfeited"],
    "report": ["report", "inform", "notify", "disclose", "give information"],
    "sells debt": ["sells debt", "actionable claim", "transferee", "assignment of debt"],
    "on my behalf": ["on my behalf", "agent", "represent me"],
    "rulebook": ["rulebook", "rules", "regulations"],
    "therapy": ["therapy", "counselling", "counseling"],
    "on the hook": ["on the hook", "surety", "guarantee", "liable"],
    "kicking out": ["kicking out", "eviction", "forfeiture", "forfeited"],
    "plan a riot": ["plan a riot", "conspiracy", "conspire"],
    "tricked a court": ["tricked a court", "fraudulently obtaining", "fraud on court"],
    "pushed a cop": ["pushed a cop", "assault", "criminal force", "public servant"],
    "protects buyers": ["protects buyers", "consumer", "consumer protection"]
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
            os.path.join(os.path.dirname(__file__), "..", "finetuned_legal_model")
        )
        self.embeddings = self.model.encode(
            texts, normalize_embeddings=True, show_progress_bar=True
        )
        print("Search system ready.")

    def lookup_section(self, act_name_contains, section_number):
        section_number = str(section_number).strip()
        for record in self.records:
            act_name = str(record.get("act_name", ""))
            record_section = str(record.get("section_number", "")).strip()
            if act_name_contains.lower() in act_name.lower() and record_section == section_number:
                return record
        return None

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
            section_number = str(record.get("section_number") or "")
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

            if "minor" in query_lower and "contract" in query_lower:
                if "contract act" in act_name and ("minor" in combined or "competent" in combined or "age of majority" in combined):
                    boost[i] *= 2.0

            if ("hacked" in query_lower or "stole data" in query_lower or "hacking" in query_lower):
                if "information technology" in act_name and (
                    "unauthorised access" in combined or "unauthorized access" in combined
                    or "damage to computer" in combined or "data" in combined and "steal" in combined
                ):
                    boost[i] *= 2.0

            if "driving" in query_lower and "licence" in query_lower:
                if "motor vehicles act" in act_name:
                    boost[i] *= 2.0
                elif "information technology" in act_name:
                    boost[i] *= 0.3

            if "driving" in query_lower and "licence" in query_lower and "appeal" in query_lower:
                if "motor vehicles act" in act_name and "appeal" in combined:
                    boost[i] *= 3.0

            if "rti" in query_lower or "right to information" in query_lower:
                if "right to information act" in act_name:
                    boost[i] *= 2.0

            if "won't complete" in query_lower or "specific performance" in expanded_query:
                if "specific relief act" in act_name and "specific performance" in combined:
                    boost[i] *= 2.5
                    if section_number == "10":
                        boost[i] *= 2.0

            if "doesn't own" in query_lower or "doesn't actually own" in query_lower:
                if "transfer of property act" in act_name and "ostensible owner" in combined:
                    boost[i] *= 3.0
                elif "transfer of property act" in act_name:
                    boost[i] *= 0.7

            if "stop someone" in query_lower or ("stop" in query_lower and "harmful" in query_lower):
                if "specific relief act" in act_name and "injunction" in combined:
                    boost[i] *= 2.5

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





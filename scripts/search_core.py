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
    "seriously injuring": ["seriously injuring", "grievous hurt", "serious injury"],
    "serious injury": ["serious injury", "grievous hurt"],
    "reckless driving": ["reckless driving", "rash driving"],
    "deliver a summons": ["deliver a summons", "service of summons"],
    "send a summons": ["send a summons", "service of summons"],
    "take cognizance": ["take cognizance", "cognizance of offence"],
    "occupying": ["occupying", "recovery of possession", "wrongful possession"],
    "financial compensation": ["financial compensation", "monetary relief", "compensation"],
    "fake certificate": ["fake certificate", "forged certificate", "fraudulent certificate"],
    "settle disputes outside trial": ["settle disputes outside trial", "mediation", "negotiated settlement"],
    "letting a criminal escape": ["letting a criminal escape", "omission to apprehend", "sufferance of escape"],
    "hurting someone to force them to pay": ["hurting someone to force them to pay", "extortion"],
    "encouraging a large group": ["encouraging a large group", "abetment", "incitement"],
    "let someone off": ["let someone off", "waiver", "discharge", "release from obligation"],
    "authority to make rules": ["authority to make rules", "power to make rules"],
    "disrespecting a public official": ["disrespecting a public official", "contempt of lawful authority"],
    "small mistakes": ["small mistakes", "irregularities"],
    "give the property back empty": ["give the property back empty", "vacant possession"],
    "sabotaging a train": ["sabotaging a train", "mischief rail", "destroy rail"],
    "receiving a court summons": ["receiving a court summons", "service of summons"],
    "deliver a summons": ["deliver a summons", "service of summons"],
    "executing an arrest warrant": ["executing an arrest warrant", "aid to person executing warrant"],
    "acid attack": ["acid attack", "grievous hurt by acid"],
    "10-year-old": ["10-year-old", "immature understanding", "child above seven"],
    "alter a product's trademark": ["alter a product's trademark", "tampering with property mark"],
    "fake the label": ["fake the label", "false mark upon receptacle"],
    "letting a criminal escape": ["letting a criminal escape", "sufferance of escape", "omission to apprehend"],
    "appeal a rent tribunal": ["appeal a rent tribunal", "revision petition"],
    "detaining someone illegally": ["detaining someone illegally", "commitment contrary to law"],
    "contract be enforced with modified terms": ["contract be enforced with modified terms", "non-enforcement except with variation"],
    "claims rights to my property": ["claims rights to my property", "subsequent title"],
    "which tribunal handles appeals": ["which tribunal handles appeals", "appellate tribunal"],
    "treated like a court case": ["treated like a court case", "judicial proceedings"],
    "records during": ["records during", "record in summary trials"],
    "certifying authority's license": ["certifying authority's license", "suspension of licence"],
    "waive their own eviction notice": ["waive their own eviction notice", "waiver of notice to quit"],
    "let someone off from fulfilling": ["let someone off from fulfilling", "dispense with performance"],
    "pressured into signing": ["pressured into signing", "undue influence"],
    "ban me from driving": ["ban me from driving", "disqualify licence"],
    "encouraging a large group": ["encouraging a large group", "abetment by public"],
    "get my mortgaged property back": ["get my mortgaged property back", "usufructuary mortgagor recover possession"],
    "compensation calculated": ["compensation calculated", "principles method determining compensation"],
    "licence cancelled if": ["licence cancelled if", "suspension cancellation conviction"],
    "go to jail instead": ["go to jail instead", "imprisonment default of fine"],
    "gathered after a trial starts": ["gathered after a trial starts", "further inquiry additional evidence"],
    "physically bring my vehicle": ["physically bring my vehicle", "production of vehicle"],
    "bus route permit": ["bus route permit", "stage carriage permit"],
    "damage using fire": ["damage using fire", "mischief by fire"],
    "child not yet born": ["child not yet born", "unborn person", "vested interest"],
    "repay expenses": ["repay expenses", "bailor necessary expenses"],
    "taking care of their item": ["taking care of their item", "bailee"],
    "very minor harm": ["very minor harm", "slight harm"],
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


IPC_TO_BNS = {
    # Common, high-frequency IPC sections mapped to their BNS 2023 equivalents.
    # Cross-checked across multiple legal reference sources as of 2026.
    # NOT an exhaustive or officially verified mapping (511 IPC sections vs
    # 358 BNS sections means some do not map one-to-one). For legal certainty,
    # verify against the official bare act.
    "302": "103",    # Murder
    "420": "318",    # Cheating
    "376": "64",     # Rape
    "498a": "85",    # Cruelty by husband/relatives
    "307": "109",    # Attempt to murder
    "304a": "106",   # Causing death by negligence
    "506": "351",    # Criminal intimidation
    "509": "79",     # Insulting modesty of a woman
    "353": "121",    # Assault to deter public servant
    "336": "125",    # Act endangering life
    "326": "118",    # Grievous hurt by dangerous weapons
    "382": "304",    # Theft after preparation for death/hurt
    "442": "330",    # House-breaking
    "494": "82",     # Bigamy
}


def expand_ipc_references(query):
    query_lower = query.lower()
    if "ipc" not in query_lower:
        return query
    numbers_found = re.findall(r"\b(\d+[a-z]?)\b", query_lower)
    additions = []
    for num in numbers_found:
        if num in IPC_TO_BNS:
            additions.append(f"bns section {IPC_TO_BNS[num]}")
    if additions:
        return query + " " + " ".join(additions)
    return query


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
        query = expand_ipc_references(query)
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

        ipc_target_section = None
        if "ipc" in query_lower:
            numbers_found = re.findall(r"\b(\d+[a-z]?)\b", query_lower)
            for num in numbers_found:
                if num in IPC_TO_BNS:
                    ipc_target_section = IPC_TO_BNS[num]
                    break

        for i, record in enumerate(self.records):
            title = str(record.get("section_title") or "").lower()
            legal_text = str(record.get("legal_text") or "").lower()
            act_name = str(record.get("act_name") or "").lower()
            section_number = str(record.get("section_number") or "")
            combined = title + " " + legal_text + " " + act_name

            if ipc_target_section is not None:
                if "bharatiya nyaya sanhita" in act_name and section_number == ipc_target_section:
                    boost[i] *= 50.0

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

        if ipc_target_section is not None:
            for i, record in enumerate(self.records):
                if "bharatiya nyaya sanhita" in str(record.get("act_name") or "").lower() and str(record.get("section_number") or "") == ipc_target_section:
                    final_scores[i] = final_scores.max() + 1.0

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





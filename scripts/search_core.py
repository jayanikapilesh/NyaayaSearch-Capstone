import csv
import hashlib
import json
import re
import os
import numpy as np
import openpyxl
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer, CrossEncoder

DATASET = os.path.join(os.path.dirname(__file__), "..", "Legal_Knowledge_Base_combined.xlsx")
CACHE_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CACHE_FILE = os.path.join(CACHE_DIR, "section_embeddings_cache.npy")
CACHE_META_FILE = os.path.join(CACHE_DIR, "section_embeddings_cache_meta.json")
EXCLUDED_SECTIONS_FILE = os.path.join(CACHE_DIR, "excluded_placeholder_sections.csv")


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


IPC_MAPPING_FILE = os.path.join(CACHE_DIR, "ipc_bns_mapping.csv")


def load_ipc_bns_mapping(filepath=IPC_MAPPING_FILE):
    mapping = {}
    omitted = set()
    if not os.path.exists(filepath):
        return mapping, omitted
    import csv
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            ipc_sec = str(row.get("ipc_section") or "").strip().lower()
            if not ipc_sec or ipc_sec == "n/a":
                continue
            relation = str(row.get("relation") or "").strip().lower()
            if relation == "omitted_from_ipc":
                omitted.add(ipc_sec)
                if ipc_sec not in mapping:
                    mapping[ipc_sec] = []
            elif relation in ("direct", "split"):
                bns_base = str(row.get("bns_base_section") or "").strip()
                if bns_base and bns_base.lower() != "n/a":
                    if ipc_sec not in mapping:
                        mapping[ipc_sec] = []
                    if bns_base not in mapping[ipc_sec]:
                        mapping[ipc_sec].append(bns_base)
    return mapping, omitted


IPC_TO_BNS, IPC_OMITTED = load_ipc_bns_mapping()


def extract_ipc_sections(query: str):
    if not IPC_TO_BNS:
        return []
    ql = query.lower()
    ql = re.sub(r"\b(\d+)\s+([a-z]{1,2})\b", r"\1\2", ql)
    res = []
    has_ipc = bool(re.search(r"\b(?:ipc|indian penal code)\b", ql))
    if has_ipc:
        nums = re.findall(r"\b(\d+[a-z]*)\b", ql)
        for n in nums:
            if n in IPC_TO_BNS and n not in res:
                res.append(n)
    else:
        letter_nums = re.findall(r"\b(\d+[a-z]+)\b", ql)
        for n in letter_nums:
            if n in IPC_TO_BNS and n not in res:
                res.append(n)
        if re.search(r"\b420\b", ql) and any(w in ql for w in ["cheat", "fraud", "section", "what is", "case"]):
            if "420" in IPC_TO_BNS and "420" not in res:
                res.append("420")
    return res


def expand_ipc_references(query):
    ipc_sections = extract_ipc_sections(query)
    if not ipc_sections:
        return query
    additions = []
    for num in ipc_sections:
        for bns_sec in IPC_TO_BNS.get(num, []):
            additions.append(f"bns section {bns_sec}")
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


def _get_model_files_hash(model_path):
    """
    Computes a deterministic hash of the embedding model folder's weight and configuration files
    based on relative file paths, sizes, and last modified times (int seconds).
    If model_path is a file, hashes its size and mtime.
    If model_path does not exist or is not a local directory/file, returns an empty string.
    """
    if not model_path or not os.path.exists(model_path):
        return ""
    if os.path.isfile(model_path):
        st = os.stat(model_path)
        sig = f"{os.path.basename(model_path)}:{st.st_size}:{int(st.st_mtime)}"
        return hashlib.sha256(sig.encode("utf-8")).hexdigest()

    entries = []
    for root, _, files in os.walk(model_path):
        for f in sorted(files):
            if not f.startswith(".") and not f.endswith(".pyc"):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, model_path).replace("\\", "/")
                try:
                    st = os.stat(full_path)
                    entries.append(f"{rel_path}:{st.st_size}:{int(st.st_mtime)}")
                except OSError:
                    pass

    entries.sort()
    raw_sig = ";".join(entries)
    return hashlib.sha256(raw_sig.encode("utf-8")).hexdigest()


def _compute_embeddings_hash(texts, model_name, model_path=None):
    hasher = hashlib.sha256(model_name.encode("utf-8"))
    if model_path:
        files_hash = _get_model_files_hash(model_path)
        hasher.update(b"\x00")
        hasher.update(files_hash.encode("utf-8"))
    for t in texts:
        hasher.update(b"\x00")
        hasher.update(t.encode("utf-8"))
    return hasher.hexdigest()


def is_placeholder_record(record):
    """Identifies placeholder rows in the knowledge base that contain no real legal content
    (e.g., repealed/omitted section stubs, pure amendment markers, and corrupted/truncated fragments).
    Returns (is_placeholder, reason).
    """
    act = str(record.get("act_name") or "").strip()
    sec = str(record.get("section_number") or "").strip()
    title = str(record.get("section_title") or "").strip()
    text = str(record.get("legal_text") or "").strip()

    # Exceptions:
    # 1. Indian Contract Act Sec 123 has Sec 124 & 125 conjoined into its text
    if act == "Indian Contract Act, 1872" and sec == "123":
        return False, None

    # 2. Right to Information Act Sec 31 has 1,012 chars of real text including Schedules
    if act == "Right to Information Act, 2005" and sec == "31":
        return False, None

    t_low = text.lower()
    tit_low = title.lower()

    # Rule 1: Amendment markers without statutory text (Ins. / Subs.)
    if tit_low in {"ins.", "subs."} or t_low.startswith("ins. by") or t_low.startswith("subs. by"):
        return True, "Amendment marker without statutory text (Ins./Subs.)"

    # Rule 2: Corrupted or truncated stubs
    if (title == text and len(text) < 80) or text == "73" or title == "73":
        return True, "Corrupted / truncated title fragment"
    if "panth piploda" in tit_low:
        return True, "Territorial regulation footnote stub"

    # Rule 3: Repealed or omitted statutory provisions with no substantive text (len < 300)
    has_rep_or_omit_title = any(k in tit_low for k in ["omitted by", "omitted.", "[omitted", "rep.", "[repealed"])
    has_rep_or_omit_text = any(k in t_low for k in ["omitted by", "rep. by", "repealed by"])
    if (has_rep_or_omit_title or has_rep_or_omit_text) and "repeal and savings" not in tit_low:
        if len(text) < 300:
            if "omitted" in tit_low or "omitted" in t_low:
                return True, "Omitted statutory provision"
            return True, "Repealed statutory provision"

    return False, None


class SearchEngine:
    def __init__(self, model_path=None, model_name=None):
        print("Loading legal dataset...")
        wb = openpyxl.load_workbook(DATASET, read_only=True)
        ws = wb.active

        headers = list(next(ws.values))
        records = []
        excluded_rows = []

        for row in ws.iter_rows(values_only=True):
            record = dict(zip(headers, row))
            is_ph, reason = is_placeholder_record(record)
            if is_ph:
                excluded_rows.append({
                    "act": record.get("act_name"),
                    "section": record.get("section_number"),
                    "title": record.get("section_title"),
                    "reason": reason,
                })
                continue
            records.append(record)

        if excluded_rows:
            try:
                with open(EXCLUDED_SECTIONS_FILE, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=["act", "section", "title", "reason"])
                    writer.writeheader()
                    writer.writerows(excluded_rows)
            except Exception as e:
                print(f"Warning: Failed to save excluded placeholder sections: {e}")

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

        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), "..", "finetuned_legal_model")
        if model_name is None:
            model_name = os.path.basename(os.path.normpath(model_path)) or "finetuned_legal_model"
        self.model = SentenceTransformer(model_path)

        current_hash = _compute_embeddings_hash(texts, model_name, model_path=model_path)
        loaded_from_cache = False

        if os.path.exists(CACHE_FILE) and os.path.exists(CACHE_META_FILE):
            try:
                with open(CACHE_META_FILE, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                if (
                    meta.get("hash") == current_hash
                    and meta.get("model_name") == model_name
                    and meta.get("num_sections") == len(texts)
                ):
                    print("Loading section embeddings from cache...")
                    self.embeddings = np.load(CACHE_FILE)
                    if len(self.embeddings) == len(texts):
                        print(f"Loaded {len(self.embeddings)} section embeddings from cache.")
                        loaded_from_cache = True
            except Exception as e:
                print(f"Warning: Failed to load embeddings cache ({e}), recomputing...")

        if not loaded_from_cache:
            print("Creating semantic embeddings...")
            self.embeddings = self.model.encode(
                texts, normalize_embeddings=True, show_progress_bar=True
            )
            try:
                os.makedirs(CACHE_DIR, exist_ok=True)
                np.save(CACHE_FILE, self.embeddings)
                with open(CACHE_META_FILE, "w", encoding="utf-8") as f:
                    json.dump(
                        {
                            "hash": current_hash,
                            "model_name": model_name,
                            "model_files_hash": _get_model_files_hash(model_path),
                            "num_sections": len(texts),
                        },
                        f,
                        indent=2,
                    )
                print(f"Saved {len(self.embeddings)} section embeddings to cache.")
            except Exception as e:
                print(f"Warning: Could not save embeddings cache: {e}")

        # Cross-Encoder Reranker: loaded ONCE at startup
        self.reranker_model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
        self.use_reranker = os.environ.get("USE_RERANKER", "1").lower() in ("1", "true", "yes")
        self.cross_encoder = None
        try:
            try:
                self.cross_encoder = CrossEncoder(self.reranker_model_name, local_files_only=True)
                print(f"Loaded CrossEncoder from local cache: {self.reranker_model_name}")
            except Exception:
                self.cross_encoder = CrossEncoder(self.reranker_model_name)
                print(f"Loaded CrossEncoder: {self.reranker_model_name}")
        except Exception as e:
            print(f"Warning: Failed to load cross-encoder {self.reranker_model_name} ({e}), reranking disabled.")
            self.use_reranker = False

        print("Search system ready.")

    def lookup_section(self, act_name_contains, section_number):
        section_number = str(section_number).strip()
        for record in self.records:
            act_name = str(record.get("act_name", ""))
            record_section = str(record.get("section_number", "")).strip()
            if act_name_contains.lower() in act_name.lower() and record_section == section_number:
                return record
        return None

    def search(self, query, top_k=5, rerank=True):
        raw_query = query
        ipc_sections = extract_ipc_sections(raw_query)
        ipc_target_sections = []
        for num in ipc_sections:
            for bns_sec in IPC_TO_BNS.get(num, []):
                if bns_sec not in ipc_target_sections:
                    ipc_target_sections.append(bns_sec)

        query = expand_ipc_references(raw_query)
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

            if ipc_target_sections:
                if "bharatiya nyaya sanhita" in act_name and section_number in ipc_target_sections:
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

        if ipc_target_sections:
            base_override = final_scores.max() + 1.0
            for i, record in enumerate(self.records):
                if "bharatiya nyaya sanhita" in str(record.get("act_name") or "").lower():
                    sec_str = str(record.get("section_number") or "")
                    if sec_str in ipc_target_sections:
                        priority = len(ipc_target_sections) - ipc_target_sections.index(sec_str)
                        final_scores[i] = base_override + priority

        # Determine if reranking should be performed
        should_rerank = bool(rerank) and self.cross_encoder is not None
        if os.environ.get("USE_RERANKER", "1").lower() in ("0", "false", "no"):
            should_rerank = False

        if not should_rerank:
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

        # Reranking path: retrieve top-20 (or max(20, top_k)), rerank top-10
        pool_k = max(20, top_k)
        candidate_indices = np.argsort(final_scores)[::-1][:pool_k]

        candidates = []
        for index in candidate_indices:
            record = self.records[index]
            section_text = (
                str(record.get("section_title") or "") + " " +
                str(record.get("legal_text") or "")
            )
            matched_terms = find_matched_terms(query_tokens, section_text)
            candidates.append({
                "act_name": record.get("act_name"),
                "section_number": record.get("section_number"),
                "section_title": record.get("section_title"),
                "legal_text": record.get("legal_text"),
                "hybrid_score": float(final_scores[index]),
                "semantic_score": float(semantic_scores[index]),
                "bm25_score": float(bm25_scores[index]),
                "matched_terms": matched_terms,
            })

        n_rerank = min(10, len(candidates))
        if n_rerank <= 1:
            return candidates[:top_k]

        to_rerank = candidates[:n_rerank]
        remaining = candidates[n_rerank:]

        pairs = [
            (raw_query, f"{r.get('act_name', '')}, Section {r.get('section_number', '')}: {r.get('section_title', '')}. {str(r.get('legal_text') or '')[:400]}")
            for r in to_rerank
        ]

        cross_logits = self.cross_encoder.predict(pairs, show_progress_bar=False)

        hybrid_scores = np.array([r.get("hybrid_score", 0.0) for r in to_rerank], dtype=float)
        h_max = hybrid_scores.max() if hybrid_scores.max() > 0 else 1.0
        h_norm = hybrid_scores / h_max

        c_norm = 1.0 / (1.0 + np.exp(-cross_logits))
        rerank_scores = 0.2 * h_norm + 0.8 * c_norm

        for i, r in enumerate(to_rerank):
            r["rerank_score"] = float(rerank_scores[i])

        for r in remaining:
            r["rerank_score"] = float(0.2 * (r.get("hybrid_score", 0.0) / h_max))

        sort_order = np.argsort(rerank_scores)[::-1]
        reranked = [to_rerank[i] for i in sort_order] + remaining
        return reranked[:top_k]





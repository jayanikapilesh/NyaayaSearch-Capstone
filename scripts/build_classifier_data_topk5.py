import json
import pandas as pd
from search_core import SearchEngine

engine = SearchEngine()

rows = []
queries_and_targets = []

with open("../data/eval/eval_queries.json", "r", encoding="utf-8") as f:
    eval_queries = json.load(f)
for q in eval_queries:
    for section in q["expected_sections"]:
        queries_and_targets.append((q["query"], q["act_name"], str(section)))

with open("../data/training_pairs.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        pair = json.loads(line)
        queries_and_targets.append((pair["query"], pair["act_name"], str(pair["section_number"])))

with open("../data/training_pairs_batch2.jsonl", "r", encoding="utf-8") as f:
    for line in f:
        pair = json.loads(line)
        queries_and_targets.append((pair["query"], pair["act_name"], str(pair["section_number"])))

holdout_all = [
    ("Can I leave property to my grandchild who hasn't been born yet?", "Transfer of Property Act, 1882", "13"),
    ("Someone took my car without asking me, is that a crime?", "Motor Vehicles Act, 1988", "197"),
    ("The other person flat out refused to do their part of the deal, can I cancel the contract?", "Indian Contract Act, 1872", "39"),
    ("If my agent's authority ends, does that also end my sub-agent's authority?", "Indian Contract Act, 1872", "210"),
    ("Does my landlord have to give me notice before increasing my rent?", "Karnataka Rent Act, 1999", "10"),
    ("Police say my complaint is non-cognizable, what happens to my case now?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "174"),
    ("Someone physically blocked me from walking away, what crime is that?", "Bharatiya Nyaya Sanhita, 2023", "126"),
    ("There's an arrest warrant against me, what happens when the police come?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "82"),
    ("Can the government change traffic fine amounts after they're set?", "Motor Vehicles Act, 1988", "199B"),
    ("Is there a time limit to appeal to the IT Appellate Tribunal?", "Information Technology Act, 2000", "60"),
    ("When does an agent's authority to act for someone officially end?", "Indian Contract Act, 1872", "201"),
    ("What happens if I drive without a proper licence?", "Motor Vehicles Act, 1988", "181"),
    ("Is it a crime to give police false information to get someone else in trouble?", "Bharatiya Nyaya Sanhita, 2023", "217"),
    ("What's the difference between a temporary and a permanent court injunction?", "Specific Relief Act, 1963", "37"),
    ("Can I get in trouble for parking my car somewhere unsafe?", "Motor Vehicles Act, 1988", "122"),
    ("What's the punishment for kidnapping someone for ransom?", "Bharatiya Nyaya Sanhita, 2023", "140"),
    ("If I settle my consumer complaint, does the commission record that officially?", "Consumer Protection Act, 2019", "81"),
    ("Can a court order my abuser to stay away from me?", "Protection of Women from Domestic Violence Act, 2005", "18"),
    ("Can police search me after they arrest me?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "49"),
    ("Is it a crime to convince a soldier to disobey orders?", "Bharatiya Nyaya Sanhita, 2023", "159"),
    ("Who appoints the Chief Information Commissioner?", "Right to Information Act, 2005", "12"),
    ("Can I appeal a decision made under the Motor Vehicles Act?", "Motor Vehicles Act, 1988", "89"),
    ("Can a boss be punished for sexual relations with an employee by misusing his position?", "Bharatiya Nyaya Sanhita, 2023", "68"),
    ("What's the punishment for kidnapping a woman to force her into marriage?", "Bharatiya Nyaya Sanhita, 2023", "87"),
    ("What types of criminal courts exist in India?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "6"),
    ("Can the High Court review a lower court's decision?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "442"),
    ("Which police officer rank can investigate cyber crimes?", "Information Technology Act, 2000", "78"),
    ("What happens if I break my bail bond?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "491"),
    ("Who is legally allowed to act as an agent in a contract?", "Indian Contract Act, 1872", "184"),
    ("What happens if I don't show up in court after being released on bail?", "Bharatiya Nyaya Sanhita, 2023", "269"),
    ("What's the punishment for robbery where the robber tries to kill someone?", "Bharatiya Nyaya Sanhita, 2023", "311"),
    ("What's the punishment for making fake currency notes?", "Bharatiya Nyaya Sanhita, 2023", "178"),
    ("Can one co-owner sell their share of jointly owned property?", "Transfer of Property Act, 1882", "47"),
    ("Is it a crime to not report information to police when legally required to?", "Bharatiya Nyaya Sanhita, 2023", "211"),
    ("Can I use force to defend myself even if it risks hurting an innocent bystander?", "Bharatiya Nyaya Sanhita, 2023", "44"),
    ("What happens if I plead guilty in court?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "264"),
    ("Is it a crime to give false information about a crime to the police?", "Bharatiya Nyaya Sanhita, 2023", "240"),
    ("Is singing an obscene song in public illegal?", "Bharatiya Nyaya Sanhita, 2023", "296"),
    ("Can the accused testify as a witness in their own trial?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "353"),
    ("What's the punishment for lying to get a digital certificate?", "Information Technology Act, 2000", "71"),
    ("What is a charge on property under property law?", "Transfer of Property Act, 1882", "100"),
    ("Can a magistrate order me to give a handwriting sample?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "349"),
    ("Can police sell seized perishable goods before the trial ends?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "505"),
    ("What happens if someone doesn't show up after a court order to appear?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "84"),
    ("How long is an arrest warrant valid?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "72"),
    ("Where can I file a big consumer complaint at the national level?", "Consumer Protection Act, 2019", "53"),
    ("Is it a crime to hide that you know someone plans to commit a serious crime?", "Bharatiya Nyaya Sanhita, 2023", "58"),
    ("Can the government take action against misleading advertisements?", "Consumer Protection Act, 2019", "21"),
    ("Can I question witnesses in my own court case?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "322"),
    ("Can I file a defamation case against someone?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "222"),
    ("Can I get information about a third party through an RTI request?", "Right to Information Act, 2005", "11"),
    ("Is it illegal to resist arrest?", "Bharatiya Nyaya Sanhita, 2023", "265"),
    ("What is a continuing offence?", "Bharatiya Nagarik Suraksha Sanhita, 2023", "518"),
    ("Can I be protected if I help someone in an emergency without their consent?", "Bharatiya Nyaya Sanhita, 2023", "30"),
    ("What makes an electronic signature legally secure?", "Information Technology Act, 2000", "15"),
]
queries_and_targets.extend(holdout_all)

print(f"Total labeled query->section pairs to process: {len(queries_and_targets)}")

for i, (query, expected_act, expected_section) in enumerate(queries_and_targets):
    results = engine.search(query, top_k=5)
    query_word_count = len(query.split())

    for rank, r in enumerate(results, start=1):
        is_relevant = int(str(r["act_name"]) == expected_act and str(r["section_number"]) == expected_section)
        matched_count = len(r.get("matched_terms", []))
        rows.append({
            "query": query,
            "act_name": r["act_name"],
            "section_number": r["section_number"],
            "hybrid_score": r["hybrid_score"],
            "semantic_score": r["semantic_score"],
            "bm25_score": r["bm25_score"],
            "matched_term_count": matched_count,
            "rank": rank,
            "reciprocal_rank": 1.0 / rank,
            "query_length": query_word_count,
            "matched_term_ratio": matched_count / query_word_count if query_word_count > 0 else 0,
            "semantic_minus_bm25": r["semantic_score"] - r["bm25_score"],
            "is_relevant": is_relevant,
        })

    if (i + 1) % 50 == 0:
        print(f"Processed {i + 1}/{len(queries_and_targets)} queries...")

df = pd.DataFrame(rows)
df.to_csv("../data/eval/classifier_training_data_topk5.csv", index=False)
print(f"\nBuilt {len(df)} labeled examples with engineered features")
print(f"Relevant: {df['is_relevant'].sum()}, Not relevant: {(df['is_relevant']==0).sum()}")



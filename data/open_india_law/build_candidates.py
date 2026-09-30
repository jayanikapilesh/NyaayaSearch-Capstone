"""Build candidate_acts.csv from the Open India Law central + Karnataka legislation parquet files.

Read-only exploration script (not part of the app). Run from the repo root:
    python data/open_india_law/build_candidates.py
"""
import html
import re
import sys
from pathlib import Path

import pandas as pd

D = Path(__file__).parent
EXCLUDE = re.compile(r"Amendment|Appropriation|Repealing|Validation|Finance Act", re.I)


def norm(t):
    t = html.unescape(str(t)).replace("�", "'")
    return re.sub(r"\s+", " ", t).strip().rstrip(".")


def per_act(df, level):
    df = df.assign(_sec=df.section_number.fillna("").str.strip())
    g = df.groupby("act_id").agg(
        title=("title", "first"), year=("year", "first"), status=("act_status", "first"),
        sections=("_sec", lambda s: s[s != ""].nunique()), chunks=("chunk_id", "count"),
    ).reset_index()
    g["title"] = g.title.map(norm)
    g["level"] = level
    g["year"] = g.year.astype("Int64")
    # the Karnataka file repeats a few Acts under several act_ids: keep the fullest copy
    g = g.sort_values("sections", ascending=False).drop_duplicates(["title", "level"])
    return g


central = per_act(pd.read_parquet(D / "in_central_legislation.parquet"), "Central")
karn = per_act(pd.read_parquet(D / "in_karnataka_legislation.parquet"), "Karnataka")

# (topic, why, [case-insensitive regexes matched against the normalised title])
T = [
 ("Family/marriage/succession/maintenance", "personal-law / family matters", [
  r"Hindu Marriage Act", r"Hindu Succession Act", r"Hindu Adoptions and Maintenance", r"Hindu Minority and Guardianship",
  r"Special Marriage Act", r"Dowry Prohibition", r"Indian Christian Marriage", r"Parsi Marriage and Divorce", r"^The Divorce Act",
  r"Foreign Marriage Act", r"Anand Marriage", r"Dissolution of Muslim Marriages", r"Muslim Personal Law \(Shariat\)",
  r"Muslim Women \(Protection of Rights on", r"Prohibition of Child Marriage", r"Indian Succession Act", r"Guardians and Wards",
  r"Married Womens Property", r"Family Courts Act", r"Maintenance Orders Enforcement", r"Maintenance and Welfare of Parents",
  r"Births, Deaths and Marriages Registration", r"Registration of Births and Deaths", r"^The Majority Act",
  r"Surrogacy \(Regulation\)", r"Assisted Reproductive Technology", r"KARNATAKA MARRIAGES \(REGISTRATION"]),
 ("Labour/wages/employment", "wages, workplace rights, social security", [
  r"Code on Wages", r"Code on Social Security", r"Industrial Relations Code", r"Occupational Safety, Health and Working",
  r"^The Industrial Disputes Act", r"Industrial Employ.*Standing Orders", r"Trade Unions Act", r"Employees Provident Funds",
  r"^The Apprentices Act", r"Bonded Labour System", r"Mahatma Gandhi National Rural Employment", r"Child and Adolescent Labour",
  r"Manual Scavengers", r"Street Vendors", r"KARNATAKA SHOPS AND COMMERCIAL", r"KARNATAKA PAYMENT OF SUBSISTENCE",
  r"KARNATAKA DAILY WAGE EMPLOYEES"]),
 ("Consumer", "consumer rights / fair trade", [
  r"Consumer Protection Act", r"Legal Metrology Act", r"Sale of Goods Act", r"Food Safety and Standards",
  r"Drugs and Magic Remedies", r"National Food Security Act"]),
 ("Contract/civil law", "contracts, partnerships, limitation", [
  r"Indian Contract Act", r"Indian Partnership Act", r"Specific Relief Act", r"^The Limitation Act", r"Powers-of.Attorney",
  r"Indian Trust Act"]),
 ("Property/rent/registration/land", "property transfer, rent, registration, land", [
  r"Transfer of Property Act", r"^The Registration Act", r"Indian Stamp Act", r"Indian Easements", r"^The Partition Act",
  r"delhi rent control", r"Delhi \(Urban Areas\) Tenants Relief", r"Cantonments \(Extension of Rent Control",
  r"East Punjab Urban Rent Restriction", r"Public Premises \(Eviction", r"Delhi Apartment Ownership", r"Prohibition of Benami",
  r"Right to Fair Compensation.*Land Acquisition", r"Scheduled Tribes and Other Traditional Forest Dwellers",
  r"Slum Areas \(Improvement", r"Central Provinces Tenancy", r"Punjab Tenancy", r"Ajmer Tenancy",
  r"KARNATAKA RENT ACT", r"KARNATAKA LAND REFORMS", r"KARNATAKA LAND GRABBING", r"KARNATAKA LAND \(RESTRICTION ON TRANSFER",
  r"KARNATAKA\s+APARTMENT OWNERSHIP", r"KARNATAKA STAMP ACT", r"KARNATAKA PUBLIC PREMISES", r"KARNATAKA SLUM AREAS",
  r"KARNATAKA TOWN AND COUNTRY PLANNING", r"KARNATAKA\s+ACQUISITION OF LANDS FOR GRANT OF HOUSE SITES"]),
 ("Housing (RERA)", "homebuyer protection", [r"Real Estate \(Regulation and Development\)"]),
 ("Money/cheques/banking disputes", "cheque bounce, debt recovery, loans, deposits", [
  r"Negotiable Instruments Act", r"Banking Regulation Act", r"Recovery of Debts and Bankruptcy", r"Securitisation and Reconstruction",
  r"Insolvency and Bankruptcy Code", r"Banning of Unregulated Deposit", r"Chit Funds Act", r"Prize Chits and Money Circulation",
  r"Credit Information Companies", r"Payment and Settlement Systems", r"Bankers Books Evidence", r"^The Insurance Act",
  r"^The Interest Act", r"Usurious Loans", r"Provincial Insolvency", r"Presidency-Towns Insolvency",
  r"KARNATAKA MONEY-LENDERS", r"KARNATAKA PAWNBROKERS", r"EXORBITANT INTEREST", r"MICRO LOAN AND SMALL LOAN",
  r"KARNATAKA DEBT RELIEF"]),
 ("Crime/police/courts/bail/evidence", "criminal law, procedure, courts, evidence", [
  r"Bharatiya Nyaya Sanhita", r"Bharatiya Nagarik Suraksha Sanhita", r"Bharatiya Sakshya Adhiniyam", r"Code of Civil Procedure",
  r"^The Police Act, 1861", r"Prevention of Corruption Act", r"Narcotic Drugs and Psychotropic", r"Unlawful Activities \(Prevention\)",
  r"Probation of Offenders", r"^The Prisoners Act", r"^The Prisons Act", r"Criminal Procedure \(Identification\)",
  r"Prevention of Money-Laundering", r"Public Gambling Act", r"Prevention of Damage to Public Property", r"^The Oaths Act",
  r"Court-Fees Act", r"Contempt of Courts", r"Legal Services Authorities", r"Gram Nyayalayas", r"Provincial Small Cause Courts",
  r"Presidency Small Cause Courts", r"^The Notaries Act", r"Arbitration and Conciliation", r"^The Mediation Act",
  r"Protection of Civil Rights Act",
  r"KARNATAKA POLICE ACT", r"KARNATAKA CIVIL COURTS", r"KARNATAKA SMALL CAUSE COURTS", r"KARNATAKA COURT-FEE",
  r"KARNATAKA CONTROL OF ORGANIZED CRIMES"]),
 ("Cyber/IT/data", "cybercrime, e-commerce, personal data, identity", [
  r"Information Technology Act", r"Digital Personal Data Protection", r"^The Aadhaar"]),
 ("Fundamental rights/citizenship", "civil status and civil rights (Constitution itself not in dataset)", [
  r"Citizenship Act", r"^The Passports Act"]),
 ("Women/children/elderly/disability protection", "protection statutes", [
  r"Protection of Women from Domestic Violence", r"Sexual Harassment of Women at Workplace", r"Protection of Children from Sexual",
  r"Juvenile Justice", r"Rights of Persons with Disabilities", r"Commissions for Protection of Child Rights",
  r"Transgender Persons", r"National Commission for Women Act", r"Commission of Sati", r"Indecent Representation of Women",
  r"Immoral Traffic", r"Medical Termination of Pregnancy", r"Right of Children to Free and Compulsory Education",
  r"Human Immunodeficiency Virus", r"National Trust for Welfare of Persons with Autism", r"Orphanages and other Charitable Homes",
  r"Women.s and Children.s Institutions", r"Infant Milk Substitutes", r"KARNATAKA DEVADASIS", r"KARNATAKA STATE COMMISSION FOR WOMEN",
  r"KARNATAKA PROHIBITION OF BEGGARY"]),
 ("Motor vehicles/transport", "driving, accidents, insurance, traffic", [
  r"^The Motor Vehicles Act", r"KARNATAKA\s+MOTOR VEHICLES TAXATION", r"KARNATAKA TRAFFIC CONTROL"]),
 ("RTI/transparency", "access to government information & services", [
  r"Right to Information Act", r"KARNATAKA SAKAALA SERVICES"]),
 ("Education", "student and admission rights", [
  r"Central Educational Institutions \(Reservation in Admission\)", r"Public Examinations \(Prevention of Unfair",
  r"KARNATAKA EDUCATION ACT", r"CAPITATION FEE"]),
 ("Health", "patient and public-health rights", [
  r"Clinical Establishments", r"Mental Healthcare Act", r"Drugs and Cosmetics", r"Transplantation of Human Organs",
  r"Cigarettes and Other Tobacco", r"Prohibition of Electronic Cigarettes", r"Epidemic Diseases Act, 1897",
  r"KARNATAKA PRIVATE MEDICAL ESTABLISHMENTS"]),
 ("Environment/pollution", "citizen-facing pollution & wildlife rules", [
  r"Environment \(Protection\) Act", r"Air \(Prevention and Control", r"Water \(Prevention and Control", r"Wild Life \(Protection\)",
  r"Indian Forest Act", r"Van \(Sanrakshan", r"Biological Diversity Act", r"National Green Tribunal", r"Public Liability Insurance",
  r"Prevention of Cruelty to Animals Act, 1960", r"KARNATAKA PRESERVATION OF TREES"]),
 ("Local bodies (Karnataka)", "municipal / panchayat governance citizens deal with", [
  r"KARNATAKA MUNICIPAL CORPORATIONS", r"KARNATAKA MUNICIPALITIES", r"BRUHAT BENGALURU MAHANAGARA PALIKE",
  r"GREATER BENGALURU GOVERNANCE", r"KARNATAKA GRAM SWARAJ AND PANCHAYAT RAJ"]),
]

# Acts already in our KB (all 23), matched to dataset titles.
KB = pd.read_excel(D.parent.parent / "Legal_Knowledge_Base_combined.xlsx", usecols=["act_name", "jurisdiction"]).drop_duplicates()
kb_rows = KB.groupby("act_name").size()
KB_ACTS = list(KB.act_name)


def key(t):
    t = re.sub(r"[^a-z0-9 ]", " ", norm(t).lower())
    return re.sub(r"\b(the|act)\b", " ", re.sub(r"\s+", " ", t)).split()


def kbkey(t):
    return " ".join(key(t))


kb_keys = {kbkey(a): a for a in KB_ACTS}

pool = pd.concat([central, karn], ignore_index=True)
pool["kb_key"] = pool.title.map(kbkey)
pool["in_kb"] = pool.kb_key.isin(kb_keys)
principal = (pool.status == "in_force") & ~pool.title.str.contains(EXCLUDE) & (pool.sections >= 3)

pool["topic"] = ""
pool["why"] = ""
unmatched = []
for topic, why, pats in T:
    for p in pats:
        m = pool.title.str.contains(p, flags=re.I, regex=True) & (principal | pool.in_kb)
        if not m.any():
            unmatched.append((topic, p))
        first = m & (pool.topic == "")
        pool.loc[first, "topic"] = topic
        pool.loc[first, "why"] = why

# KB Acts that no rule tagged (should be none) -> tag from KB domain
kbdom = pd.read_excel(D.parent.parent / "Legal_Knowledge_Base_combined.xlsx", usecols=["act_name", "domain"]).drop_duplicates("act_name").set_index("act_name").domain
for i, r in pool[pool.in_kb & (pool.topic == "")].iterrows():
    pool.loc[i, "topic"] = "KB domain: " + kbdom[kb_keys[r.kb_key]]
    pool.loc[i, "why"] = "already in KB"

sel = pool[pool.topic != ""].copy()
sel.loc[sel.in_kb, "why"] = "already in our KB; " + sel.loc[sel.in_kb, "why"]
sel["in_kb"] = sel.in_kb.map({True: "yes", False: "no"})
out = sel.rename(columns={"sections": "section_count"})[["title", "year", "status", "section_count", "topic", "why", "level", "in_kb", "act_id"]]
out = out.sort_values(["level", "topic", "title"])
out.to_csv(D / "candidate_acts.csv", index=False, encoding="utf-8-sig")

print("unmatched patterns:", unmatched)
print("KB acts missing from dataset:", [a for k_, a in kb_keys.items() if k_ not in set(pool.kb_key)])
print("Acts:", len(out), " sections:", int(out.section_count.sum()))
print(out.groupby("level").agg(acts=("title", "size"), sections=("section_count", "sum")))
print(out.groupby("topic").agg(acts=("title", "size"), sections=("section_count", "sum")).sort_values("acts", ascending=False))
print("KB Acts in list:", (out.in_kb == "yes").sum())

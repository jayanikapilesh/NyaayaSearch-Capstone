import json
import csv

input_file = "data/scenarios/processed/scenario_seeds.json"
output_file = "data/scenarios/processed/dataset3_english_expanded.csv"

with open(input_file, "r", encoding="utf-8") as file:
    seeds = json.load(file)


scenario_variants = {

    # ============================================================
    # CONSUMER PROTECTION ACT, 2019
    # ============================================================

    ("Consumer Protection Act, 2019", "2"): [
        "I bought a mobile phone for my personal use. Am I considered a consumer?",
        "I purchased a washing machine for my home. Does consumer protection law cover me?",
        "I paid for a repair service for my own vehicle. Am I a consumer under the law?",
        "I bought a product for personal use and it turned out to be defective. Do I qualify as a consumer?",
        "I paid for an online service for myself. Can I seek protection under consumer law?",
        "I purchased furniture for my house. Can I approach a consumer forum if there is a problem?",
        "I bought a laptop for my personal use. Does the Consumer Protection Act apply to me?",
        "I paid for a service for my family. Can I be treated as a consumer?",
        "I purchased a product from an online seller for personal use. Am I protected as a consumer?",
        "I bought an appliance for my home and the seller refuses to address the problem. Do I have consumer rights?",
    ],

    ("Consumer Protection Act, 2019", "17"): [
        "I want to complain about an unfair trade practice. Where should I report it?",
        "A business has violated consumer rights. Which authority can I approach?",
        "I want to report a consumer rights violation. Where can I file the complaint?",
        "I believe a business is following an unfair trade practice. Who can I complain to?",
        "Where can a consumer report a violation of consumer rights?",
        "A seller is using an unfair business practice against customers. Which authority should I contact?",
        "A company is treating consumers unfairly. What is the proper way to report it?",
        "I want to bring a consumer rights issue to the attention of the authorities. Where should I start?",
        "A business is engaging in conduct that appears unfair to consumers. Can I report it to an authority?",
        "I believe my consumer rights have been violated. Which consumer authority should I approach?",
    ],

    ("Consumer Protection Act, 2019", "20"): [
        "I bought a product that may be unsafe. What action can the consumer authority take?",
        "A company is selling goods that could be dangerous to consumers. What can the authority do?",
        "I believe a product is dangerous for consumers. Can the consumer authority intervene?",
        "Unsafe products are being sold. What powers does the consumer authority have?",
        "What can happen when goods sold to consumers are found to be unsafe?",
        "A product may put consumers at risk. Can the authority investigate the matter?",
        "I discovered that a product may be dangerous. What action can the consumer authority take?",
        "A company continues selling a product that may cause harm. Can an authority intervene?",
        "Consumers are being exposed to a potentially unsafe product. What powers are available to the authority?",
        "A product has a serious safety problem. Can the consumer authority order action against it?",
    ],

    ("Consumer Protection Act, 2019", "21"): [
        "A company is making false claims in its advertisement. What action can be taken?",
        "I saw a misleading advertisement for a product. Can the company be penalised?",
        "A product advertisement contains information that is not true. What can consumers do?",
        "What happens if a company publishes a misleading advertisement?",
        "Can action be taken against a business for a false advertisement?",
        "An advertisement promises results that the product cannot actually provide. What can be done?",
        "A company is making exaggerated claims about its product in advertisements. Can action be taken?",
        "I think an advertisement is misleading consumers. Which authority can deal with it?",
        "A seller advertised a product using claims that appear false. What does consumer law provide?",
        "A business is using misleading advertising to attract customers. Can the authorities intervene?",
    ],


    # ============================================================
    # TRANSFER OF PROPERTY ACT, 1882
    # ============================================================

    ("Transfer of Property Act, 1882", "53"): [
        "A property owner transferred property to avoid paying a creditor. Can the transfer be challenged?",
        "Someone transferred their property to defeat a creditor's claim. Is that transfer legally valid?",
        "My debtor transferred property after I made a claim against them. Can I challenge the transfer?",
        "A person appears to have transferred property to avoid a debt. What does the law provide?",
        "Can a fraudulent transfer of property made to defeat creditors be challenged?",
        "My debtor transferred a house to a relative to avoid repayment. Can the transaction be challenged?",
        "A person owing me money transferred valuable property to someone else. What legal issue does this raise?",
        "I believe property was transferred only to prevent creditors from recovering money. Can creditors challenge it?",
        "A debtor transferred land shortly after a debt became due. Could the transfer be questioned?",
        "Someone appears to have moved property into another person's name to avoid paying debts. What can a creditor do?",
    ],

    ("Transfer of Property Act, 1882", "54"): [
        "I am buying a property. When is the transaction legally considered a sale?",
        "I paid for a property. What makes the transaction a legal sale?",
        "What is legally meant by a sale of immovable property?",
        "I have agreed to buy property and want to understand when ownership is legally sold.",
        "Does paying money for a property automatically amount to a legal sale?",
        "I signed an agreement to purchase a house. Does that itself make me the owner?",
        "I paid an advance for land but have not completed the transaction. Has a legal sale taken place?",
        "The seller agreed to sell me a property but the formal sale has not happened. What is my legal position?",
        "I have an agreement to buy a flat. When does the transaction become a sale under property law?",
        "I paid the full price for land but want to know whether that alone completes the legal sale.",
    ],

    ("Transfer of Property Act, 1882", "58"): [
        "I want to mortgage my property to get a loan. What does the law provide?",
        "I used my house as security for a loan. What is my legal position?",
        "What is a mortgage of property under Indian property law?",
        "I am considering a property-backed loan. What does the law say about mortgages?",
        "I have given my property as security for a debt. What are the legal implications?",
        "I want to use my house as security when borrowing money. What type of transaction is this?",
        "The bank wants my property as security for a loan. What does a mortgage legally mean?",
        "I borrowed money against my land. What rights and obligations arise from the mortgage?",
        "I am planning to mortgage my property to secure a debt. How does property law define this?",
        "My property has been offered as security for a loan. What does the law say about this arrangement?",
    ],

    ("Transfer of Property Act, 1882", "105"): [
        "I am renting out my property. What is a lease in legal terms?",
        "I am a tenant and want to understand what a lease legally means.",
        "What does Indian property law mean by a lease?",
        "I am entering into a rental arrangement. When is it legally considered a lease?",
        "What rights and obligations arise from a lease of property?",
        "I have rented my apartment to someone. What makes the arrangement a lease?",
        "I am renting a shop for several years. How is this arrangement defined under property law?",
        "My landlord and I have agreed that I can use the property for rent. Is this a lease?",
        "I am about to sign a rental agreement. What does the law mean by a lease?",
        "I have possession of a property in return for rent. Is this legally a lease?",
    ],

    ("Transfer of Property Act, 1882", "106"): [
        "My landlord wants me to leave. What notice is legally required?",
        "I want to end my tenancy. How much notice do I need to give?",
        "My tenant is being asked to vacate. What notice period applies?",
        "What notice is required to terminate a lease when the agreement does not specify it?",
        "Can my landlord terminate my tenancy without giving the required notice?",
        "My landlord suddenly told me to vacate the property. Is notice required?",
        "I want to ask my tenant to leave but the agreement does not mention a notice period. What applies?",
        "My tenancy agreement is silent about notice. What does property law provide?",
        "I received a notice from my landlord asking me to vacate. What legal notice rules apply?",
        "I want to terminate my tenancy properly. What notice should I give the other party?",
    ],

    ("Transfer of Property Act, 1882", "111"): [
        "My landlord says my lease has ended. How can a lease legally terminate?",
        "I am a tenant and want to know the legal ways my lease can come to an end.",
        "Under what circumstances can a lease of property be terminated?",
        "My lease is being terminated. What legal grounds can bring a lease to an end?",
        "How does a tenancy legally come to an end under property law?",
        "The lease period has ended. Does the lease automatically terminate?",
        "My landlord and I want to end the lease early. How can a lease legally come to an end?",
        "I have breached a condition of my lease. Can this result in termination?",
        "The property has changed hands and I want to know whether my existing lease can terminate.",
        "My lease is being ended because of a condition in the agreement. What does property law say about termination?",
    ],


    # ============================================================
    # BHARATIYA NYAYA SANHITA, 2023
    # ============================================================

    ("Bharatiya Nyaya Sanhita, 2023", "40"): [
        "Someone attacked me and I used force to protect myself. Can private defence apply?",
        "I defended myself during an attack. When does the right of private defence apply?",
        "I used reasonable force because someone was attacking me. What does the law say?",
        "Someone threatened me with immediate harm and I defended myself. What are my legal rights?",
        "When can a person legally defend themselves against an attack?",
        "Someone tried to physically hurt me and I pushed them away. Can private defence apply?",
        "I was attacked and acted to protect myself. When is such defensive action legally protected?",
        "A person threatened me with immediate violence and I defended myself. What does the law allow?",
        "I used force to stop someone from attacking me. Could this fall under private defence?",
        "I was in danger of being physically harmed and defended myself. When is private defence available?",
    ],

    ("Bharatiya Nyaya Sanhita, 2023", "43"): [
        "Someone tried to take or damage my property and I used force to protect it. Can private defence apply?",
        "I used force to protect my property from an immediate threat. Is that covered by private defence?",
        "Someone was interfering with my property and I defended it. What does the law say?",
        "When can I legally use private defence to protect my property?",
        "My property was under immediate threat and I acted to protect it. What are my legal rights?",
        "Someone entered my property and I acted to protect it. Can the right of private defence apply?",
        "A person tried to take my belongings by force. Can I rely on private defence?",
        "Someone was damaging my property and I intervened to protect it. What does the law allow?",
        "My property was being unlawfully taken and I used force to stop it. Could private defence apply?",
        "Someone threatened my property and I acted immediately to protect it. What are the legal limits?",
    ]
}


# Keep one seed record for each unique Act + Section.
section_map = {}

for seed in seeds:
    key = (
        seed["act_name"],
        str(seed["section_number"])
    )

    if key not in section_map:
        section_map[key] = seed


rows = []
scenario_id = 1

for key, seed in section_map.items():

    queries = scenario_variants.get(key, [seed["user_query"]])

    for query in queries:
        rows.append({
            "scenario_id": f"SCN-{scenario_id:05d}",
            "domain": seed["domain"],
            "user_query": query,
            "language": "English",
            "act_name": seed["act_name"],
            "section_number": seed["section_number"],
            "section_title": seed["section_title"],
            "plain_explanation": "",
            "what_to_do_next": "",
            "source_url": seed["source_url"]
        })

        scenario_id += 1


fieldnames = [
    "scenario_id",
    "domain",
    "user_query",
    "language",
    "act_name",
    "section_number",
    "section_title",
    "plain_explanation",
    "what_to_do_next",
    "source_url"
]

with open(output_file, "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)


print("English scenario dataset created successfully!")
print("Unique legal sections:", len(section_map))
print("Generated rows:", len(rows))
print("Unique queries:", len(set(r["user_query"] for r in rows)))
print("Saved to:", output_file)
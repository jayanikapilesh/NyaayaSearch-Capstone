import csv
import openpyxl

output_file = "data/scenarios/processed/legal_scenarios.csv"
legal_kb_file = "Legal_Knowledge_Base_combined.xlsx"


# Load verified legal knowledge base
workbook = openpyxl.load_workbook(legal_kb_file, read_only=True)
sheet = workbook.active

section_titles = {}

for row in sheet.iter_rows(min_row=2, values_only=True):
    act_name = row[2]
    section_number = row[4]
    section_title = row[5]

    section_titles[(act_name, section_number)] = section_title


def get_section_title(act_name, section_number):
    return section_titles.get(
        (act_name, section_number),
        "Section title not found"
    )


scenarios = [
    # ---------------------------------------------------------
    # CONSUMER PROTECTION
    # ---------------------------------------------------------

    {
        "scenario_id": "SC001",
        "domain": "Consumer Protection",
        "user_query": "I bought a defective product. What can I do?",
        "language": "English",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": 35,
        "plain_explanation": "A consumer can file a complaint before the appropriate Consumer Commission when there is a problem with a product or service.",
        "what_to_do_next": "Keep your bill, warranty, messages, photos and other proof. You can file a consumer complaint before the appropriate Consumer Commission."
    },

    {
        "scenario_id": "SC002",
        "domain": "Consumer Protection",
        "user_query": "The online seller sent me a damaged product. What are my rights?",
        "language": "English",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": 35,
        "plain_explanation": "You may complain about a defective or damaged product through the consumer dispute redressal system.",
        "what_to_do_next": "Save the order details, invoice, delivery photos and communication with the seller. Seek replacement, refund or other appropriate relief."
    },

    {
        "scenario_id": "SC003",
        "domain": "Consumer Protection",
        "user_query": "A company refused to refund me for a faulty product. What can I do?",
        "language": "English",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": 35,
        "plain_explanation": "A consumer can approach the consumer dispute redressal system when a dispute with a seller or service provider is not resolved.",
        "what_to_do_next": "Keep the invoice, payment proof, product details and refund correspondence. You can pursue a consumer complaint."
    },

    {
        "scenario_id": "SC004",
        "domain": "Consumer Protection",
        "user_query": "The service I paid for was not provided properly. Can I complain?",
        "language": "English",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": 35,
        "plain_explanation": "Consumers can raise complaints about problems with goods or services through the consumer dispute redressal system.",
        "what_to_do_next": "Keep receipts, contracts, screenshots and communications. First request resolution from the service provider and retain the response."
    },

    {
        "scenario_id": "SC005",
        "domain": "Consumer Protection",
        "user_query": "I was charged for a service I did not receive. What should I do?",
        "language": "English",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": 35,
        "plain_explanation": "A consumer may seek redress when a paid service has not been provided as agreed.",
        "what_to_do_next": "Keep proof of payment and the promised service. Contact the provider in writing and preserve the response before pursuing further consumer remedies."
    },

    {
        "scenario_id": "SC006",
        "domain": "Consumer Protection",
        "user_query": "An advertisement made a false claim about a product. What can I do?",
        "language": "English",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": 21,
        "plain_explanation": "The law gives the Central Consumer Protection Authority powers concerning false or misleading advertisements.",
        "what_to_do_next": "Save the advertisement, product details and evidence supporting the claim. You can report the issue to the appropriate consumer protection authority."
    },

    {
        "scenario_id": "SC007",
        "domain": "Consumer Protection",
        "user_query": "A product advertisement promised something that the product does not actually do.",
        "language": "English",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": 21,
        "plain_explanation": "False or misleading advertisements can be subject to action under the Consumer Protection Act.",
        "what_to_do_next": "Take a screenshot or save the advertisement and product information. Keep your purchase documents if you bought the product."
    },

    {
        "scenario_id": "SC008",
        "domain": "Consumer Protection",
        "user_query": "The product I received is different from what was advertised online.",
        "language": "English",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": 35,
        "plain_explanation": "A consumer can raise a complaint when the goods received do not match what was represented or promised.",
        "what_to_do_next": "Save the original listing, screenshots, invoice and photographs of the product received. Contact the seller and keep the response."
    },

    {
        "scenario_id": "SC009",
        "domain": "Consumer Protection",
        "user_query": "The seller will not replace a defective item even though it is under warranty.",
        "language": "English",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": 35,
        "plain_explanation": "A consumer can seek redress for a dispute concerning a defective product or failure to provide an agreed remedy.",
        "what_to_do_next": "Keep the warranty document, invoice and all communications with the seller or manufacturer. Request the remedy in writing."
    },

    {
        "scenario_id": "SC010",
        "domain": "Consumer Protection",
        "user_query": "I paid for an online purchase but the seller never delivered it.",
        "language": "English",
        "act_name": "Consumer Protection Act, 2019",
        "section_number": 35,
        "plain_explanation": "A consumer may seek redress when goods paid for are not delivered as agreed.",
        "what_to_do_next": "Keep the order confirmation, payment receipt, delivery promise and messages with the seller. Request delivery or refund in writing."
    },


    # ---------------------------------------------------------
    # PROPERTY
    # ---------------------------------------------------------

    {
        "scenario_id": "SC011",
        "domain": "Property",
        "user_query": "My brother and I own property together. Can he sell his share?",
        "language": "English",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": 44,
        "plain_explanation": "The law contains rules about transfers by one co-owner of their share in jointly owned property.",
        "what_to_do_next": "Collect the title documents and ownership records. Check the nature of the co-ownership and the share being transferred before taking further action."
    },

    {
        "scenario_id": "SC012",
        "domain": "Property",
        "user_query": "Someone is trying to sell a property while a court case about it is still going on. What should I do?",
        "language": "English",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": 52,
        "plain_explanation": "The law contains rules concerning transfers of property during the pendency of certain court proceedings involving that property.",
        "what_to_do_next": "Keep the case documents and information about the proposed transfer. Inform your lawyer or the court about the transaction."
    },

    {
        "scenario_id": "SC013",
        "domain": "Property",
        "user_query": "The owner transferred the property to avoid paying a debt. Can that transfer be challenged?",
        "language": "English",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": 53,
        "plain_explanation": "The law addresses certain transfers made with intent to defeat or delay creditors.",
        "what_to_do_next": "Keep evidence of the debt, ownership records and details of the transfer. Obtain legal advice about whether the transfer can be challenged."
    },

    {
        "scenario_id": "SC014",
        "domain": "Property",
        "user_query": "I paid for a property but the seller is refusing to complete the sale. What can I do?",
        "language": "English",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": 54,
        "plain_explanation": "The law defines a sale of immovable property and sets out requirements connected with such transfers.",
        "what_to_do_next": "Keep the agreement, payment records, receipts and communications with the seller. Consider the appropriate legal remedy based on the documents."
    },

    {
        "scenario_id": "SC015",
        "domain": "Property",
        "user_query": "I have a mortgage on my house. Can I get the property back after paying the mortgage?",
        "language": "English",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": 60,
        "plain_explanation": "The law provides for redemption of a mortgage subject to the applicable legal requirements.",
        "what_to_do_next": "Keep the mortgage deed, payment records and statements showing repayment. Request the relevant release or redemption documents."
    },

    {
        "scenario_id": "SC016",
        "domain": "Property",
        "user_query": "I am renting a property and want to understand my rights as a tenant.",
        "language": "English",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": 108,
        "plain_explanation": "The law contains rights and liabilities of lessors and lessees in relation to leases, subject to the applicable agreement and law.",
        "what_to_do_next": "Keep your rental agreement, rent receipts and communication with the landlord. Check the applicable tenancy rules for your state and the terms of your agreement."
    },

    {
        "scenario_id": "SC017",
        "domain": "Property",
        "user_query": "My landlord is trying to end my lease before the agreed period. What can I do?",
        "language": "English",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": 111,
        "plain_explanation": "The law provides circumstances in which a lease may be determined.",
        "what_to_do_next": "Keep the lease agreement, rent receipts and any notice received from the landlord. Check whether the proposed termination follows the agreement and applicable law."
    },

    {
        "scenario_id": "SC018",
        "domain": "Property",
        "user_query": "My parent gave me property as a gift. What makes a gift of property legally effective?",
        "language": "English",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": 123,
        "plain_explanation": "The law sets out how a gift of immovable property is to be effected.",
        "what_to_do_next": "Keep the gift deed and registration documents. Verify that the required formalities have been completed."
    },

    {
        "scenario_id": "SC019",
        "domain": "Property",
        "user_query": "Someone is claiming ownership of my land because they say the previous owner transferred it to them.",
        "language": "English",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": 41,
        "plain_explanation": "The law contains rules concerning transfers by an ostensible owner when certain conditions are satisfied.",
        "what_to_do_next": "Collect the title deed, previous sale documents and land records. Have the chain of ownership examined before accepting or disputing the claim."
    },

    {
        "scenario_id": "SC020",
        "domain": "Property",
        "user_query": "Can a person transfer property that they do not legally own?",
        "language": "English",
        "act_name": "Transfer of Property Act, 1882",
        "section_number": 43,
        "plain_explanation": "The law addresses certain transfers made by a person who represents that they are authorised to transfer property.",
        "what_to_do_next": "Collect the sale agreement, title documents and proof of the transferor's ownership or authority. Seek legal advice about the effect of the transaction."
    }
]


# Add section titles automatically from Dataset 1
for scenario in scenarios:
    scenario["section_title"] = get_section_title(
        scenario["act_name"],
        scenario["section_number"]
    )

    scenario["source_url"] = "https://www.indiacode.nic.in/"


# Keep the desired column order
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


with open(output_file, "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(scenarios)


print("Created scenarios:", len(scenarios))
print("Consumer scenarios:", 10)
print("Property scenarios:", 10)
print("Saved to:", output_file)
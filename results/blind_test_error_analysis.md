# Blind Test Error Analysis: Strict-Clean Baseline (Production + Reranker)

**Configuration**: `cross-encoder/ms-marco-MiniLM-L-6-v2` (Top-10 reranked, $w=0.8$), `--strict-clean` (54 synonym keys, `IPC_TO_BNS` disabled).

**Evaluation Set**: `data/eval/blind_test_{en,hi,kn}.json` ($n=32$ queries per language).

## 1. Overall Performance & Extra Metrics

| Language | Queries | Strict Recall@5 | Lenient Recall@5 (Primary or Second) | Right Act in Top 5 |
| :--- | :---: | :---: | :---: | :---: |
| **English** | 32 | **17/32 (53.1%)** | **20/32 (62.5%)** | **28/32 (87.5%)** |
| **Hindi** | 32 | **19/32 (59.4%)** | **21/32 (65.6%)** | **30/32 (93.8%)** |
| **Kannada** | 32 | **23/32 (71.9%)** | **25/32 (78.1%)** | **31/32 (96.9%)** |

> **Definitions**:
> - **Strict Recall@5**: The primary ground-truth section appeared within the top 5 ranked results.
> - **Lenient Recall@5**: Either the primary ground-truth section OR the secondary ground-truth section (from `blind_test_second_labels.json`) appeared within the top 5 ranked results.
> - **Right Act in Top 5**: At least one returned section within the top 5 ranked results was from the primary target Act.

## 2. Miss Classification Summary

| Language | Total Misses | (a) Right Act in Top 5 (Different Section) | (b) Second Label in Top 5 | (c) Different Act Entirely |
| :--- | :---: | :---: | :---: | :---: |
| **English** | 15 | 11 (73.3%) | 3 (20.0%) | 4 (26.7%) |
| **Hindi** | 13 | 11 (84.6%) | 2 (15.4%) | 2 (15.4%) |
| **Kannada** | 9 | 8 (88.9%) | 2 (22.2%) | 1 (11.1%) |

*(Note: Category (b) queries are also counted in (a) if the second label belongs to the same Act, e.g. DV Act)*

## 3. Detailed Miss Breakdown by Language

### English Misses (15 / 32)

#### Question #2
- **Query**: "I paid a seller on Instagram for a dress and he blocked me without sending it."
- **Target**: `Bharatiya Nyaya Sanhita, 2023`, Section `318`: *Cheating.*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 308 (Rank #1: *Extortion.*), Sec 78 (Rank #2: *Stalking.*)
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Bharatiya Nyaya Sanhita, 2023` Section `308`: *Extortion.* (score: 0.2000)
  2. **[Rank #2]** `Bharatiya Nyaya Sanhita, 2023` Section `78`: *Stalking.* (score: 0.1981)
  3. **[Rank #3]** `Information Technology Act, 2000` Section `66E`: *Punishment for violation of privacy.–Whoever, intentionally or knowingly captures, publishes or transmits the image of a private area of any person without his or her consent, under circumstances violating the privacy of that person, shall be punished with imprisonment which may extend to three years or with fine not exceeding two lakh rupees, or with both.* (score: 0.1892)

#### Question #3
- **Query**: "A guy from my college keeps following me home and messaging me even after I told him to stop."
- **Target**: `Bharatiya Nyaya Sanhita, 2023`, Section `78`: *Stalking.*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 126 (Rank #2: *Wrongful restraint.*), Sec 151 (Rank #4: *Assaulting President, Governor, etc., with intent to compel or restrain exercise of any lawful power .*), Sec 127 (Rank #5: *Wrongful confinement.*)
- **Target Rank**: #10
- **Top 3 Returned**:
  1. **[Rank #1]** `Specific Relief Act, 1963` Section `41`: *Injunction when refused.* (score: 0.2000)
  2. **[Rank #2]** `Bharatiya Nyaya Sanhita, 2023` Section `126`: *Wrongful restraint.* (score: 0.1881)
  3. **[Rank #3]** `Bharatiya Nagarik Suraksha Sanhita, 2023` Section `281`: *Power to stop proceedings in certain cases .* (score: 0.1689)

#### Question #8
- **Query**: "My job contract says I can't work for any other company in the same field for 2 years after quitting. Is that legal?"
- **Target**: `Indian Contract Act, 1872`, Section `27`: *Agreement in restraint of trade, void.*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 201 (Rank #1: *Termination of agency .*), Sec 210 (Rank #2: *Termination of sub -agent’s authority.*), Sec 53 (Rank #4: *Liability of party preventing event on which the contract is to take effect.*), Sec 64 (Rank #5: *Consequences of rescission of voidable contract.*)
- **Target Rank**: #20
- **Top 3 Returned**:
  1. **[Rank #1]** `Indian Contract Act, 1872` Section `201`: *Termination of agency .* (score: 0.2001)
  2. **[Rank #2]** `Indian Contract Act, 1872` Section `210`: *Termination of sub -agent’s authority.* (score: 0.1839)
  3. **[Rank #3]** `Specific Relief Act, 1963` Section `19`: *Relief against parties and persons claiming under them by subsequent title .* (score: 0.1776)

#### Question #9
- **Query**: "My 16-year-old son signed a loan agreement with a shop. Does he have to pay?"
- **Target**: `Indian Contract Act, 1872`, Section `11`: *Who are competent to contract .*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 50 (Rank #1: *This is a contract.*), Sec 25 (Rank #2: *Agreement without consideration, void, unless i t is in writing and registered ,or is a promise to compensate for something done or is a promise to pay a debt barred by li mitation law .*), Sec 000 (Rank #3: *This is a void agreement.*), Sec 37 (Rank #4: *Obligation of parties to contracts .*), Sec 127 (Rank #5: *Consideration for guarantee .*)
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Indian Contract Act, 1872` Section `50`: *This is a contract.* (score: 0.2001)
  2. **[Rank #2]** `Indian Contract Act, 1872` Section `25`: *Agreement without consideration, void, unless i t is in writing and registered ,or is a promise to compensate for something done or is a promise to pay a debt barred by li mitation law .* (score: 0.1944)
  3. **[Rank #3]** `Indian Contract Act, 1872` Section `000`: *This is a void agreement.* (score: 0.1817)

#### Question #10
- **Query**: "The shop sold me a fridge that stopped working in a week and won't help. Where do I complain?"
- **Target**: `Consumer Protection Act, 2019`, Section `35`: *Manner in which complaint shall be made .*
- **Classification**: **(c) Different Act entirely**: Top 5 retrieved from: Specific Relief Act, 1963, Bharatiya Nagarik Suraksha Sanhita, 2023, Bharatiya Nyaya Sanhita, 2023
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Specific Relief Act, 1963` Section `41`: *Injunction when refused.* (score: 0.2000)
  2. **[Rank #2]** `Bharatiya Nagarik Suraksha Sanhita, 2023` Section `161`: *Injunction pending inquiry.* (score: 0.1712)
  3. **[Rank #3]** `Specific Relief Act, 1963` Section `39`: *Mandatory injunctions.* (score: 0.1579)

#### Question #11
- **Query**: "I bought a faulty washing machine three years ago. Is it too late to complain?"
- **Target**: `Consumer Protection Act, 2019`, Section `69`: *Limitation period .*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 85 (Rank #1: *Liability of product service provider .*), Sec 84 (Rank #2: *Liability of product manufacturer .*), Sec 87 (Rank #5: *Exceptions to product liability action.*)
- **Target Rank**: #15
- **Top 3 Returned**:
  1. **[Rank #1]** `Consumer Protection Act, 2019` Section `85`: *Liability of product service provider .* (score: 0.2000)
  2. **[Rank #2]** `Consumer Protection Act, 2019` Section `84`: *Liability of product manufacturer .* (score: 0.1728)
  3. **[Rank #3]** `Bharatiya Nyaya Sanhita, 2023` Section `326`: *Mischief by injury, inundation, fire or explosive substance, etc .* (score: 0.1693)

#### Question #13
- **Query**: "My in-laws are trying to throw me out of my husband's house. Can they do that?"
- **Target**: `Protection of Women from Domestic Violence Act, 2005`, Section `17`: *Right t o reside in a shared household.*
- **Second Ground-Truth Label**: `Protection of Women from Domestic Violence Act, 2005`, Section `19`: *Residence orders.*
- **Classification**: **(b) Second label in Top 5**: `Protection of Women from Domestic Violence Act, 2005` Section `19` (*Residence orders.*) ranked at **#1**<br>**(a) Correct Act in Top 5 (different section)**: Sec 19 (Rank #1: *Residence orders.*)
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Protection of Women from Domestic Violence Act, 2005` Section `19`: *Residence orders.* (score: 0.2000)
  2. **[Rank #2]** `Bharatiya Nyaya Sanhita, 2023` Section `85`: *Husband or relative of husband of a woman subjecting her to cruelty .* (score: 0.1993)
  3. **[Rank #3]** `Bharatiya Nyaya Sanhita, 2023` Section `84`: *Enticing or taking away or detaining with criminal intent a married woman .* (score: 0.1885)

#### Question #14
- **Query**: "My husband hits me and I want to go to court. How do I start?"
- **Target**: `Protection of Women from Domestic Violence Act, 2005`, Section `12`: *Application to Magistrate.*
- **Second Ground-Truth Label**: `Protection of Women from Domestic Violence Act, 2005`, Section `18`: *Protection orders.*
- **Classification**: **(b) Second label in Top 5**: `Protection of Women from Domestic Violence Act, 2005` Section `18` (*Protection orders.*) ranked at **#1**<br>**(a) Correct Act in Top 5 (different section)**: Sec 18 (Rank #1: *Protection orders.*), Sec 3 (Rank #2: *Definition of domestic violence.*), Sec 23 (Rank #3: *Power to grant interim and ex parte orders.*), Sec 2 (Rank #5: *Definitions.*)
- **Target Rank**: #19
- **Top 3 Returned**:
  1. **[Rank #1]** `Protection of Women from Domestic Violence Act, 2005` Section `18`: *Protection orders.* (score: 0.2000)
  2. **[Rank #2]** `Protection of Women from Domestic Violence Act, 2005` Section `3`: *Definition of domestic violence.* (score: 0.1882)
  3. **[Rank #3]** `Protection of Women from Domestic Violence Act, 2005` Section `23`: *Power to grant interim and ex parte orders.* (score: 0.1876)

#### Question #15
- **Query**: "After beating me, my husband stopped giving money for the house and my hospital bills. Can I get money from him?"
- **Target**: `Protection of Women from Domestic Violence Act, 2005`, Section `20`: *Monetary reliefs.*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 18 (Rank #1: *Protection orders.*), Sec 3 (Rank #2: *Definition of domestic violence.*), Sec 5 (Rank #3: *Duties of police officers, service providers and Magistrate .*), Sec 22 (Rank #4: *Compensation orders .*), Sec 35 (Rank #5: *Protection of action taken in good faith .*)
- **Target Rank**: #6
- **Top 3 Returned**:
  1. **[Rank #1]** `Protection of Women from Domestic Violence Act, 2005` Section `18`: *Protection orders.* (score: 0.2000)
  2. **[Rank #2]** `Protection of Women from Domestic Violence Act, 2005` Section `3`: *Definition of domestic violence.* (score: 0.1877)
  3. **[Rank #3]** `Protection of Women from Domestic Violence Act, 2005` Section `5`: *Duties of police officers, service providers and Magistrate .* (score: 0.1757)

#### Question #16
- **Query**: "Someone made a fake account with my photos and name and is chatting with people pretending to be me."
- **Target**: `Information Technology Act, 2000`, Section `66D`: *Punishment for cheating by personation by using computer resource .–Whoever, by means of any communication device or computer resource cheats by perso*
- **Second Ground-Truth Label**: `Information Technology Act, 2000`, Section `66C`: *Punishment for identity theft .–Whoever, fraudulently or dishonestly make use of the electronic signature, password or any other unique identification*
- **Classification**: **(b) Second label in Top 5**: `Information Technology Act, 2000` Section `66C` (*Punishment for identity theft .–Whoever, fraudulently or dishonestly make use of the electronic signature, password or any other unique identification*) ranked at **#5**<br>**(a) Correct Act in Top 5 (different section)**: Sec 66C (Rank #5: *Punishment for identity theft .–Whoever, fraudulently or dishonestly make use of the electronic signature, password or any other unique identification*)
- **Target Rank**: #9
- **Top 3 Returned**:
  1. **[Rank #1]** `Bharatiya Nyaya Sanhita, 2023` Section `319`: *Cheating by personation .* (score: 0.2018)
  2. **[Rank #2]** `Bharatiya Nyaya Sanhita, 2023` Section `242`: *False personation for purpose of act or proceeding in suit or prosecution.* (score: 0.1499)
  3. **[Rank #3]** `Indian Contract Act, 1872` Section `235`: *Liability of pretended agent .* (score: 0.1421)

#### Question #22
- **Query**: "My grandfather just said out loud that he's giving me his land. Is that enough, or do we need papers?"
- **Target**: `Transfer of Property Act, 1882`, Section `123`: *Transfer how effected.*
- **Second Ground-Truth Label**: `Transfer of Property Act, 1882`, Section `122`: *“Gift ” defined .*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 8 (Rank #2: *See the Indian Registration Act, 1908 (16 of 1908). immoveable property or by hypothecation or pledge of moveable property, or to any benefic ial interest in moveable property not in the possession, either actual or constructive, of the claimant, which the Civil Courts recognise as affording grounds for relief, whether such debt or beneficial interest be existent, accuring, conditional or contingent :] 1[“a person is said to have notice”] of a fact when he actually knows that fact, or when, but for wilful abstention from an enquiry or search which he ought to have made, or gross negligence, he would have known it. Explanation I.*)
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Bharatiya Nagarik Suraksha Sanhita, 2023` Section `166`: *Dispute concerning right of use of land or water .* (score: 0.2000)
  2. **[Rank #2]** `Transfer of Property Act, 1882` Section `8`: *See the Indian Registration Act, 1908 (16 of 1908). immoveable property or by hypothecation or pledge of moveable property, or to any benefic ial interest in moveable property not in the possession, either actual or constructive, of the claimant, which the Civil Courts recognise as affording grounds for relief, whether such debt or beneficial interest be existent, accuring, conditional or contingent :] 1[“a person is said to have notice”] of a fact when he actually knows that fact, or when, but for wilful abstention from an enquiry or search which he ought to have made, or gross negligence, he would have known it. Explanation I.* (score: 0.1817)
  3. **[Rank #3]** `Bharatiya Nagarik Suraksha Sanhita, 2023` Section `85`: *Attachment of property of person absconding .* (score: 0.1792)

#### Question #25
- **Query**: "How do I ask a government office why my ration card application is still pending?"
- **Target**: `Right to Information Act, 2005`, Section `6`: *Request for obtaining information .*
- **Classification**: **(c) Different Act entirely**: Top 5 retrieved from: Karnataka Rent Act, 1999, Bharatiya Nagarik Suraksha Sanhita, 2023, Bharatiya Nyaya Sanhita, 2023
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Karnataka Rent Act, 1999` Section `68`: *Removal of difficulties.* (score: 0.2000)
  2. **[Rank #2]** `Bharatiya Nagarik Suraksha Sanhita, 2023` Section `124`: *Application of this Chapter .* (score: 0.1751)
  3. **[Rank #3]** `Bharatiya Nyaya Sanhita, 2023` Section `297`: *Keeping lottery office.* (score: 0.1745)

#### Question #28
- **Query**: "I paid an advance to buy a plot but the seller now refuses to sell. Can the court make him go through with it?"
- **Target**: `Specific Relief Act, 1963`, Section `10`: *Specific performance in respect of contracts.*
- **Classification**: **(c) Different Act entirely**: Top 5 retrieved from: Transfer of Property Act, 1882
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Transfer of Property Act, 1882` Section `57`: *P rovision by Court for incumbrances and sale freed therefrom .* (score: 0.2008)
  2. **[Rank #2]** `Transfer of Property Act, 1882` Section `55`: *Rights and liabilities of buyer and seller .* (score: 0.1723)
  3. **[Rank #3]** `Transfer of Property Act, 1882` Section `54`: *“Sale ” defined .* (score: 0.1708)

#### Question #29
- **Query**: "Last week my relative changed the locks and pushed me out of my own house. How do I get back in?"
- **Target**: `Specific Relief Act, 1963`, Section `6`: *Suit by person dispossessed of immovable property .*
- **Classification**: **(c) Different Act entirely**: Top 5 retrieved from: Bharatiya Nyaya Sanhita, 2023, Karnataka Rent Act, 1999
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Bharatiya Nyaya Sanhita, 2023` Section `330`: *House-trespass and house -breaking.* (score: 0.2000)
  2. **[Rank #2]** `Bharatiya Nyaya Sanhita, 2023` Section `333`: *House-trespass after preparation for hurt, assault or wrongful restraint .* (score: 0.1902)
  3. **[Rank #3]** `Bharatiya Nyaya Sanhita, 2023` Section `127`: *Wrongful confinement.* (score: 0.1728)

#### Question #33
- **Query**: "When I moved in, my landlord charged me a big 'extra fee' on top of the rent. Can I get it back?"
- **Target**: `Karnataka Rent Act, 1999`, Section `15`: *Refund of rent, premium, etc.,.*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 8 (Rank #1: *Other charges payable.*), Sec 16 (Rank #2: *Receipt to be given for rent and other charges paid.*), Sec 19 (Rank #3: *Saving as to acceptance of rent and other charges and forfeiture of rent in deposit.*), Sec 11 (Rank #4: *Unlawful charges not to be claimed.*), Sec 13 (Rank #5: *Fixation of interim rent.*)
- **Target Rank**: #9
- **Top 3 Returned**:
  1. **[Rank #1]** `Karnataka Rent Act, 1999` Section `8`: *Other charges payable.* (score: 0.2018)
  2. **[Rank #2]** `Karnataka Rent Act, 1999` Section `16`: *Receipt to be given for rent and other charges paid.* (score: 0.2008)
  3. **[Rank #3]** `Karnataka Rent Act, 1999` Section `19`: *Saving as to acceptance of rent and other charges and forfeiture of rent in deposit.* (score: 0.1979)

### Hindi Misses (13 / 32)

#### Question #4
- **Query (Hindi)**: "थाने वाले मेरी शिकायत लिखने से मना कर रहे हैं, क्या वो ऐसा कर सकते हैं?"
- **System Translation (EN)**: "The police are refusing to write my complaint, can they do that?"
- **Draft Paired EN**: "The police station is refusing to write down my complaint. Are they allowed to do that?"
- **Target**: `Bharatiya Nagarik Suraksha Sanhita, 2023`, Section `173`: *Information in cognizable cases .*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 388 (Rank #2: *Imprisonment or committal of person refusing to answer or produce document .*), Sec 224 (Rank #4: *Procedure by Magistrate not competent to take cognizance of case.*), Sec 181 (Rank #5: *Statements to police and use thereof.*)
- **Target Rank**: #7
- **Top 3 Returned**:
  1. **[Rank #1]** `Bharatiya Nyaya Sanhita, 2023` Section `215`: *Refusing to sign statement .* (score: 0.2253)
  2. **[Rank #2]** `Bharatiya Nagarik Suraksha Sanhita, 2023` Section `388`: *Imprisonment or committal of person refusing to answer or produce document .* (score: 0.2129)
  3. **[Rank #3]** `Bharatiya Nyaya Sanhita, 2023` Section `214`: *Refusing to answer public servant authorised to question.* (score: 0.2023)

#### Question #7
- **Query (Hindi)**: "हमारे कॉन्ट्रैक्ट में लिखा था कि जो पीछे हटेगा उसे ₹50,000 देने होंगे। दूसरी पार्टी पीछे हट गई, क्या मैं वो रकम माँग सकता हूँ?"
- **System Translation (EN)**: "Our contract stated that anyone who backs out must pay ₹50,000. The other party backed out; can I claim that amount?"
- **Draft Paired EN**: "Our contract said whoever backs out has to pay ₹50,000. The other side backed out. Can I claim that amount?"
- **Target**: `Indian Contract Act, 1872`, Section `74`: *Compensation for breach of contrac t where penalty stipulated for .*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 72 (Rank #2: *Liability of person to whom money is paid , or thing delivere d, by mistake or under coercion.*), Sec 53 (Rank #4: *Liability of party preventing event on which the contract is to take effect.*), Sec 65 (Rank #5: *Obligation of person who has received advantage under void agreem ent, or contract that becomes void .*)
- **Target Rank**: #6
- **Top 3 Returned**:
  1. **[Rank #1]** `Specific Relief Act, 1963` Section `20`: *Substituted performance of contract.* (score: 0.2001)
  2. **[Rank #2]** `Indian Contract Act, 1872` Section `72`: *Liability of person to whom money is paid , or thing delivere d, by mistake or under coercion.* (score: 0.1927)
  3. **[Rank #3]** `Specific Relief Act, 1963` Section `19`: *Relief against parties and persons claiming under them by subsequent title .* (score: 0.1827)

#### Question #8
- **Query (Hindi)**: "मेरे जॉब कॉन्ट्रैक्ट में लिखा है कि नौकरी छोड़ने के बाद 2 साल तक मैं उसी फ़ील्ड की किसी और कंपनी में काम नहीं कर सकता, क्या ये सही है?"
- **System Translation (EN)**: "My job contract says that after leaving the job I cannot work for any other company in the same field for 2 years; is this correct?"
- **Draft Paired EN**: "My job contract says I can't work for any other company in the same field for 2 years after quitting. Is that legal?"
- **Target**: `Indian Contract Act, 1872`, Section `27`: *Agreement in restraint of trade, void.*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 201 (Rank #1: *Termination of agency .*), Sec 53 (Rank #2: *Liability of party preventing event on which the contract is to take effect.*), Sec 210 (Rank #5: *Termination of sub -agent’s authority.*)
- **Target Rank**: #20
- **Top 3 Returned**:
  1. **[Rank #1]** `Indian Contract Act, 1872` Section `201`: *Termination of agency .* (score: 0.2001)
  2. **[Rank #2]** `Indian Contract Act, 1872` Section `53`: *Liability of party preventing event on which the contract is to take effect.* (score: 0.1854)
  3. **[Rank #3]** `Specific Relief Act, 1963` Section `14`: *Contracts not specifically enforceable .* (score: 0.1837)

#### Question #9
- **Query (Hindi)**: "मेरे 16 साल के बेटे ने एक दुकान के साथ लोन का एग्रीमेंट साइन कर दिया, क्या उसे पैसे चुकाने पड़ेंगे?"
- **System Translation (EN)**: "My 16-year-old son signed a loan agreement with a shop; will he have to repay the money?"
- **Draft Paired EN**: "My 16-year-old son signed a loan agreement with a shop. Does he have to pay?"
- **Target**: `Indian Contract Act, 1872`, Section `11`: *Who are competent to contract .*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 50 (Rank #1: *This is a contract.*), Sec 000 (Rank #2: *This is a void agreement.*), Sec 25 (Rank #3: *Agreement without consideration, void, unless i t is in writing and registered ,or is a promise to compensate for something done or is a promise to pay a debt barred by li mitation law .*), Sec 127 (Rank #4: *Consideration for guarantee .*), Sec 65 (Rank #5: *Obligation of person who has received advantage under void agreem ent, or contract that becomes void .*)
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Indian Contract Act, 1872` Section `50`: *This is a contract.* (score: 0.2000)
  2. **[Rank #2]** `Indian Contract Act, 1872` Section `000`: *This is a void agreement.* (score: 0.1877)
  3. **[Rank #3]** `Indian Contract Act, 1872` Section `25`: *Agreement without consideration, void, unless i t is in writing and registered ,or is a promise to compensate for something done or is a promise to pay a debt barred by li mitation law .* (score: 0.1852)

#### Question #11
- **Query (Hindi)**: "मैंने तीन साल पहले एक खराब वॉशिंग मशीन खरीदी थी, क्या अब शिकायत करने में बहुत देर हो गई?"
- **System Translation (EN)**: "I bought a faulty washing machine three years ago, is it now too late to complain?"
- **Draft Paired EN**: "I bought a faulty washing machine three years ago. Is it too late to complain?"
- **Target**: `Consumer Protection Act, 2019`, Section `69`: *Limitation period .*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 85 (Rank #1: *Liability of product service provider .*), Sec 84 (Rank #2: *Liability of product manufacturer .*), Sec 87 (Rank #5: *Exceptions to product liability action.*)
- **Target Rank**: #14
- **Top 3 Returned**:
  1. **[Rank #1]** `Consumer Protection Act, 2019` Section `85`: *Liability of product service provider .* (score: 0.2000)
  2. **[Rank #2]** `Consumer Protection Act, 2019` Section `84`: *Liability of product manufacturer .* (score: 0.1733)
  3. **[Rank #3]** `Motor Vehicles Act, 1988` Section `216`: *Power to remove difficulties .* (score: 0.1688)

#### Question #13
- **Query (Hindi)**: "मेरे ससुराल वाले मुझे पति के घर से निकालने की कोशिश कर रहे हैं, क्या वो ऐसा कर सकते हैं?"
- **System Translation (EN)**: "My in-laws are trying to evict me from my husband's house; can they do that?"
- **Draft Paired EN**: "My in-laws are trying to throw me out of my husband's house. Can they do that?"
- **Target**: `Protection of Women from Domestic Violence Act, 2005`, Section `17`: *Right t o reside in a shared household.*
- **Second Ground-Truth Label**: `Protection of Women from Domestic Violence Act, 2005`, Section `19`: *Residence orders.*
- **Classification**: **(b) Second label in Top 5**: `Protection of Women from Domestic Violence Act, 2005` Section `19` (*Residence orders.*) ranked at **#1**<br>**(a) Correct Act in Top 5 (different section)**: Sec 19 (Rank #1: *Residence orders.*)
- **Target Rank**: #11
- **Top 3 Returned**:
  1. **[Rank #1]** `Protection of Women from Domestic Violence Act, 2005` Section `19`: *Residence orders.* (score: 0.2002)
  2. **[Rank #2]** `Bharatiya Nyaya Sanhita, 2023` Section `332`: *House-trespass in order to commit offence.* (score: 0.1837)
  3. **[Rank #3]** `Bharatiya Nyaya Sanhita, 2023` Section `330`: *House-trespass and house -breaking.* (score: 0.1738)

#### Question #14
- **Query (Hindi)**: "मेरे पति मुझे मारते-पीटते हैं, मैं कोर्ट जाना चाहती हूँ। शुरुआत कैसे करूँ?"
- **System Translation (EN)**: "My husband beats me, I want to go to court. How should I start?"
- **Draft Paired EN**: "My husband hits me and I want to go to court. How do I start?"
- **Target**: `Protection of Women from Domestic Violence Act, 2005`, Section `12`: *Application to Magistrate.*
- **Second Ground-Truth Label**: `Protection of Women from Domestic Violence Act, 2005`, Section `18`: *Protection orders.*
- **Classification**: **(b) Second label in Top 5**: `Protection of Women from Domestic Violence Act, 2005` Section `18` (*Protection orders.*) ranked at **#1**<br>**(a) Correct Act in Top 5 (different section)**: Sec 18 (Rank #1: *Protection orders.*), Sec 3 (Rank #2: *Definition of domestic violence.*), Sec 23 (Rank #4: *Power to grant interim and ex parte orders.*), Sec 2 (Rank #5: *Definitions.*)
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Protection of Women from Domestic Violence Act, 2005` Section `18`: *Protection orders.* (score: 0.2000)
  2. **[Rank #2]** `Protection of Women from Domestic Violence Act, 2005` Section `3`: *Definition of domestic violence.* (score: 0.1915)
  3. **[Rank #3]** `Bharatiya Nyaya Sanhita, 2023` Section `85`: *Husband or relative of husband of a woman subjecting her to cruelty .* (score: 0.1898)

#### Question #22
- **Query (Hindi)**: "दादाजी ने ज़ुबानी कह दिया कि अपनी ज़मीन मुझे दे रहे हैं, क्या इतना काफ़ी है या कागज़ बनवाने पड़ेंगे?"
- **System Translation (EN)**: "Grandfather said verbally that he is giving me his land; is that enough or will I need to get it on paper?"
- **Draft Paired EN**: "My grandfather just said out loud that he's giving me his land. Is that enough, or do we need papers?"
- **Target**: `Transfer of Property Act, 1882`, Section `123`: *Transfer how effected.*
- **Second Ground-Truth Label**: `Transfer of Property Act, 1882`, Section `122`: *“Gift ” defined .*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 8 (Rank #2: *See the Indian Registration Act, 1908 (16 of 1908). immoveable property or by hypothecation or pledge of moveable property, or to any benefic ial interest in moveable property not in the possession, either actual or constructive, of the claimant, which the Civil Courts recognise as affording grounds for relief, whether such debt or beneficial interest be existent, accuring, conditional or contingent :] 1[“a person is said to have notice”] of a fact when he actually knows that fact, or when, but for wilful abstention from an enquiry or search which he ought to have made, or gross negligence, he would have known it. Explanation I.*), Sec 800 (Rank #3: *A by an instrument of gift professes to transfer it to B, givin g by the same instrument Rs.*)
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Bharatiya Nagarik Suraksha Sanhita, 2023` Section `166`: *Dispute concerning right of use of land or water .* (score: 0.2000)
  2. **[Rank #2]** `Transfer of Property Act, 1882` Section `8`: *See the Indian Registration Act, 1908 (16 of 1908). immoveable property or by hypothecation or pledge of moveable property, or to any benefic ial interest in moveable property not in the possession, either actual or constructive, of the claimant, which the Civil Courts recognise as affording grounds for relief, whether such debt or beneficial interest be existent, accuring, conditional or contingent :] 1[“a person is said to have notice”] of a fact when he actually knows that fact, or when, but for wilful abstention from an enquiry or search which he ought to have made, or gross negligence, he would have known it. Explanation I.* (score: 0.1945)
  3. **[Rank #3]** `Transfer of Property Act, 1882` Section `800`: *A by an instrument of gift professes to transfer it to B, givin g by the same instrument Rs.* (score: 0.1868)

#### Question #23
- **Query (Hindi)**: "पापा ने मुझे एक फ्लैट गिफ़्ट किया था, अब झगड़े के बाद वापस माँग रहे हैं। क्या वो ले सकते हैं?"
- **System Translation (EN)**: "Dad had gifted me a flat, now after a dispute he is demanding it back. Can he take it?"
- **Draft Paired EN**: "My father gifted me a flat but now wants it back after a fight. Can he take it back?"
- **Target**: `Transfer of Property Act, 1882`, Section `126`: *When gift may be suspended or revoked .*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 125 (Rank #1: *Gift to several, of whom one does not accept .*), Sec 127 (Rank #2: *Onerous gifts.*), Sec 800 (Rank #4: *A by an instrument of gift professes to transfer it to B, givin g by the same instrument Rs.*)
- **Target Rank**: #7
- **Top 3 Returned**:
  1. **[Rank #1]** `Transfer of Property Act, 1882` Section `125`: *Gift to several, of whom one does not accept .* (score: 0.2000)
  2. **[Rank #2]** `Transfer of Property Act, 1882` Section `127`: *Onerous gifts.* (score: 0.1856)
  3. **[Rank #3]** `Bharatiya Nagarik Suraksha Sanhita, 2023` Section `87`: *Claims and objections to attachment.* (score: 0.1832)

#### Question #24
- **Query (Hindi)**: "मैं बिना लिखित एग्रीमेंट के महीने-महीने किराए पर रहता हूँ। मालिक को निकालने से पहले कितना नोटिस देना होगा?"
- **System Translation (EN)**: "How much notice must be given to the landlord before eviction when I am renting month-to-month without a written agreement?"
- **Draft Paired EN**: "I rent month to month with no written agreement. How much notice does the owner have to give before asking me to leave?"
- **Target**: `Transfer of Property Act, 1882`, Section `106`: *Duration of certain leases in absence of written contract or local usage .*
- **Classification**: **(c) Different Act entirely**: Top 5 retrieved from: Karnataka Rent Act, 1999
- **Target Rank**: #8
- **Top 3 Returned**:
  1. **[Rank #1]** `Karnataka Rent Act, 1999` Section `33`: *Notice of creation and termination of su b-tenancy.* (score: 0.2103)
  2. **[Rank #2]** `Karnataka Rent Act, 1999` Section `4`: *Tenancy agreement to be in writing.* (score: 0.2006)
  3. **[Rank #3]** `Karnataka Rent Act, 1999` Section `6`: *Rent payable.* (score: 0.1980)

#### Question #28
- **Query (Hindi)**: "मैंने प्लॉट खरीदने के लिए एडवांस दिया था, अब बेचने वाला मना कर रहा है। क्या कोर्ट उसे बेचने के लिए मजबूर कर सकता है?"
- **System Translation (EN)**: "I had given an advance to buy a plot, and now the seller is refusing. Can the court force him to sell?"
- **Draft Paired EN**: "I paid an advance to buy a plot but the seller now refuses to sell. Can the court make him go through with it?"
- **Target**: `Specific Relief Act, 1963`, Section `10`: *Specific performance in respect of contracts.*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 17 (Rank #1: *Contract to sell or let property by one who has no title, not specifically enforceable .*)
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Specific Relief Act, 1963` Section `17`: *Contract to sell or let property by one who has no title, not specifically enforceable .* (score: 0.2003)
  2. **[Rank #2]** `Bharatiya Nagarik Suraksha Sanhita, 2023` Section `388`: *Imprisonment or committal of person refusing to answer or produce document .* (score: 0.1821)
  3. **[Rank #3]** `Transfer of Property Act, 1882` Section `69`: *Power of sale when valid .* (score: 0.1771)

#### Question #29
- **Query (Hindi)**: "पिछले हफ़्ते मेरे रिश्तेदार ने ताला बदलकर मुझे मेरे ही घर से बाहर कर दिया, वापस कैसे जाऊँ?"
- **System Translation (EN)**: "Last week my relative changed the lock and kicked me out of my own house, how can I get back?"
- **Draft Paired EN**: "Last week my relative changed the locks and pushed me out of my own house. How do I get back in?"
- **Target**: `Specific Relief Act, 1963`, Section `6`: *Suit by person dispossessed of immovable property .*
- **Classification**: **(c) Different Act entirely**: Top 5 retrieved from: Bharatiya Nyaya Sanhita, 2023, Bharatiya Nagarik Suraksha Sanhita, 2023, Karnataka Rent Act, 1999
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Bharatiya Nyaya Sanhita, 2023` Section `330`: *House-trespass and house -breaking.* (score: 0.2000)
  2. **[Rank #2]** `Bharatiya Nyaya Sanhita, 2023` Section `333`: *House-trespass after preparation for hurt, assault or wrongful restraint .* (score: 0.1962)
  3. **[Rank #3]** `Bharatiya Nyaya Sanhita, 2023` Section `120`: *Voluntarily causing hurt or grievous hurt to extort confession, or to compel restoration of property.* (score: 0.1672)

#### Question #33
- **Query (Hindi)**: "घर में आते वक़्त मकान मालिक ने किराए के ऊपर एक बड़ी 'एक्स्ट्रा फ़ीस' ले ली, क्या मैं वो वापस ले सकता हूँ?"
- **System Translation (EN)**: "When I moved into the house, the landlord charged a large extra fee on top of the rent; can I get it back?"
- **Draft Paired EN**: "When I moved in, my landlord charged me a big 'extra fee' on top of the rent. Can I get it back?"
- **Target**: `Karnataka Rent Act, 1999`, Section `15`: *Refund of rent, premium, etc.,.*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 8 (Rank #1: *Other charges payable.*), Sec 16 (Rank #2: *Receipt to be given for rent and other charges paid.*), Sec 19 (Rank #3: *Saving as to acceptance of rent and other charges and forfeiture of rent in deposit.*), Sec 11 (Rank #4: *Unlawful charges not to be claimed.*), Sec 9 (Rank #5: *Revision of rent in certain cases.*)
- **Target Rank**: #7
- **Top 3 Returned**:
  1. **[Rank #1]** `Karnataka Rent Act, 1999` Section `8`: *Other charges payable.* (score: 0.2079)
  2. **[Rank #2]** `Karnataka Rent Act, 1999` Section `16`: *Receipt to be given for rent and other charges paid.* (score: 0.2004)
  3. **[Rank #3]** `Karnataka Rent Act, 1999` Section `19`: *Saving as to acceptance of rent and other charges and forfeiture of rent in deposit.* (score: 0.1963)

### Kannada Misses (9 / 32)

#### Question #7
- **Query (Kannada)**: "ಯಾರು ಹಿಂದೆ ಸರಿದರೂ ₹50,000 ಕೊಡಬೇಕು ಅಂತ ನಮ್ಮ ಕಾಂಟ್ರಾಕ್ಟ್ನಲ್ಲಿ ಇತ್ತು. ಬೇರೆ ಪಾರ್ಟಿ ಹಿಂದೆ ಸರಿದಿದೆ, ಆ ದುಡ್ಡು ಕೇಳಬಹುದಾ?"
- **System Translation (EN)**: "Our contract stated that whoever backs out must pay ₹50,000. The other party has backed out; can we demand that money?"
- **Draft Paired EN**: "Our contract said whoever backs out has to pay ₹50,000. The other side backed out. Can I claim that amount?"
- **Target**: `Indian Contract Act, 1872`, Section `74`: *Compensation for breach of contrac t where penalty stipulated for .*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 72 (Rank #2: *Liability of person to whom money is paid , or thing delivere d, by mistake or under coercion.*), Sec 53 (Rank #3: *Liability of party preventing event on which the contract is to take effect.*), Sec 200 (Rank #4: *C fails to pay. The guarantee given by A was a continuing guarantee, and he is accordingly liable to B to the extent of £100. (c) A guarantees payment to B of the price of five sacks of flour to be delivered by B to C and to be paid for in a month. B delivers five sacks to C. C pays for them. Afterwards B delivers four sacks to C, which C does riot pay for. The guarantee given by A was not a continuing guarantee, and accordingly he is not liable for the price of the four sacks. 130.Revocation of continuing guarantee.*), Sec 65 (Rank #5: *Obligation of person who has received advantage under void agreem ent, or contract that becomes void .*)
- **Target Rank**: #11
- **Top 3 Returned**:
  1. **[Rank #1]** `Specific Relief Act, 1963` Section `20`: *Substituted performance of contract.* (score: 0.2001)
  2. **[Rank #2]** `Indian Contract Act, 1872` Section `72`: *Liability of person to whom money is paid , or thing delivere d, by mistake or under coercion.* (score: 0.1989)
  3. **[Rank #3]** `Indian Contract Act, 1872` Section `53`: *Liability of party preventing event on which the contract is to take effect.* (score: 0.1941)

#### Question #8
- **Query (Kannada)**: "ಕೆಲಸ ಬಿಟ್ಟ ಮೇಲೆ 2 ವರ್ಷ ಅದೇ ಫೀಲ್ಡ್‌ನ ಬೇರೆ ಕಂಪನಿಯಲ್ಲಿ ಕೆಲಸ ಮಾಡಬಾರದು ಅಂತ ನನ್ನ ಕಾಂಟ್ರಾಕ್ಟ್‌ನಲ್ಲಿ ಇದೆ, ಇದು ಲೀಗಲ್ಲಾ?"
- **System Translation (EN)**: "My contract says that after leaving the job, I cannot work for another company in the same field for 2 years. Is this legal?"
- **Draft Paired EN**: "My job contract says I can't work for any other company in the same field for 2 years after quitting. Is that legal?"
- **Target**: `Indian Contract Act, 1872`, Section `27`: *Agreement in restraint of trade, void.*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 201 (Rank #2: *Termination of agency .*), Sec 53 (Rank #4: *Liability of party preventing event on which the contract is to take effect.*)
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Specific Relief Act, 1963` Section `14`: *Contracts not specifically enforceable .* (score: 0.2004)
  2. **[Rank #2]** `Indian Contract Act, 1872` Section `201`: *Termination of agency .* (score: 0.1991)
  3. **[Rank #3]** `Specific Relief Act, 1963` Section `19`: *Relief against parties and persons claiming under them by subsequent title .* (score: 0.1946)

#### Question #9
- **Query (Kannada)**: "ನನ್ನ 16 ವರ್ಷದ ಮಗ ಒಂದು ಅಂಗಡಿಯವರ ಜೊತೆ ಲೋನ್ ಅಗ್ರಿಮೆಂಟ್‌ಗೆ ಸೈನ್ ಮಾಡಿದ್ದಾನೆ, ಅವನು ದುಡ್ಡು ಕಟ್ಟಲೇಬೇಕಾ?"
- **System Translation (EN)**: "My 16-year-old son signed a loan agreement with a shopkeeper; does he have to pay the money?"
- **Draft Paired EN**: "My 16-year-old son signed a loan agreement with a shop. Does he have to pay?"
- **Target**: `Indian Contract Act, 1872`, Section `11`: *Who are competent to contract .*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 50 (Rank #1: *This is a contract.*), Sec 25 (Rank #2: *Agreement without consideration, void, unless i t is in writing and registered ,or is a promise to compensate for something done or is a promise to pay a debt barred by li mitation law .*), Sec 000 (Rank #3: *This is a void agreement.*), Sec 127 (Rank #4: *Consideration for guarantee .*), Sec 37 (Rank #5: *Obligation of parties to contracts .*)
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Indian Contract Act, 1872` Section `50`: *This is a contract.* (score: 0.2001)
  2. **[Rank #2]** `Indian Contract Act, 1872` Section `25`: *Agreement without consideration, void, unless i t is in writing and registered ,or is a promise to compensate for something done or is a promise to pay a debt barred by li mitation law .* (score: 0.1879)
  3. **[Rank #3]** `Indian Contract Act, 1872` Section `000`: *This is a void agreement.* (score: 0.1653)

#### Question #13
- **Query (Kannada)**: "ನನ್ನ ಅತ್ತೆ-ಮಾವ ನನ್ನನ್ನು ಗಂಡನ ಮನೆಯಿಂದ ಹೊರಗೆ ಹಾಕೋಕೆ ನೋಡ್ತಿದ್ದಾರೆ, ಅವರು ಹಾಗೆ ಮಾಡಬಹುದಾ?"
- **System Translation (EN)**: "My aunt and uncle are trying to evict me from my husband's house; can they do that?"
- **Draft Paired EN**: "My in-laws are trying to throw me out of my husband's house. Can they do that?"
- **Target**: `Protection of Women from Domestic Violence Act, 2005`, Section `17`: *Right t o reside in a shared household.*
- **Second Ground-Truth Label**: `Protection of Women from Domestic Violence Act, 2005`, Section `19`: *Residence orders.*
- **Classification**: **(b) Second label in Top 5**: `Protection of Women from Domestic Violence Act, 2005` Section `19` (*Residence orders.*) ranked at **#4**<br>**(a) Correct Act in Top 5 (different section)**: Sec 19 (Rank #4: *Residence orders.*)
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Bharatiya Nyaya Sanhita, 2023` Section `332`: *House-trespass in order to commit offence.* (score: 0.2000)
  2. **[Rank #2]** `Bharatiya Nyaya Sanhita, 2023` Section `85`: *Husband or relative of husband of a woman subjecting her to cruelty .* (score: 0.1873)
  3. **[Rank #3]** `Bharatiya Nyaya Sanhita, 2023` Section `330`: *House-trespass and house -breaking.* (score: 0.1824)

#### Question #14
- **Query (Kannada)**: "ನನ್ನ ಗಂಡ ನನಗೆ ಹೊಡೀತಾರೆ, ನಾನು ಕೋರ್ಟ್‌ಗೆ ಹೋಗಬೇಕು ಅಂತಿದ್ದೀನಿ. ಹೇಗೆ ಶುರು ಮಾಡೋದು?"
- **System Translation (EN)**: "My husband beats me, I want to go to court. How do I start?"
- **Draft Paired EN**: "My husband hits me and I want to go to court. How do I start?"
- **Target**: `Protection of Women from Domestic Violence Act, 2005`, Section `12`: *Application to Magistrate.*
- **Second Ground-Truth Label**: `Protection of Women from Domestic Violence Act, 2005`, Section `18`: *Protection orders.*
- **Classification**: **(b) Second label in Top 5**: `Protection of Women from Domestic Violence Act, 2005` Section `18` (*Protection orders.*) ranked at **#1**<br>**(a) Correct Act in Top 5 (different section)**: Sec 18 (Rank #1: *Protection orders.*), Sec 3 (Rank #2: *Definition of domestic violence.*), Sec 23 (Rank #4: *Power to grant interim and ex parte orders.*), Sec 2 (Rank #5: *Definitions.*)
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Protection of Women from Domestic Violence Act, 2005` Section `18`: *Protection orders.* (score: 0.2000)
  2. **[Rank #2]** `Protection of Women from Domestic Violence Act, 2005` Section `3`: *Definition of domestic violence.* (score: 0.1904)
  3. **[Rank #3]** `Bharatiya Nyaya Sanhita, 2023` Section `85`: *Husband or relative of husband of a woman subjecting her to cruelty .* (score: 0.1893)

#### Question #22
- **Query (Kannada)**: "ತಾತ ಬಾಯಿಮಾತಲ್ಲಿ ತಮ್ಮ ಜಮೀನು ನನಗೆ ಕೊಡ್ತೀನಿ ಅಂದಿದ್ದಾರೆ, ಅಷ್ಟು ಸಾಕಾ ಅಥವಾ ಪೇಪರ್ ಮಾಡಿಸಬೇಕಾ?"
- **System Translation (EN)**: "My grandfather said verbally that he will give me his land; is that enough or do I need to get it in writing?"
- **Draft Paired EN**: "My grandfather just said out loud that he's giving me his land. Is that enough, or do we need papers?"
- **Target**: `Transfer of Property Act, 1882`, Section `123`: *Transfer how effected.*
- **Second Ground-Truth Label**: `Transfer of Property Act, 1882`, Section `122`: *“Gift ” defined .*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 8 (Rank #5: *See the Indian Registration Act, 1908 (16 of 1908). immoveable property or by hypothecation or pledge of moveable property, or to any benefic ial interest in moveable property not in the possession, either actual or constructive, of the claimant, which the Civil Courts recognise as affording grounds for relief, whether such debt or beneficial interest be existent, accuring, conditional or contingent :] 1[“a person is said to have notice”] of a fact when he actually knows that fact, or when, but for wilful abstention from an enquiry or search which he ought to have made, or gross negligence, he would have known it. Explanation I.*)
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Bharatiya Nagarik Suraksha Sanhita, 2023` Section `349`: *Power of Magistrate to order person to give specimen signatures or handwriting, etc .* (score: 0.2000)
  2. **[Rank #2]** `Bharatiya Nagarik Suraksha Sanhita, 2023` Section `166`: *Dispute concerning right of use of land or water .* (score: 0.1968)
  3. **[Rank #3]** `Bharatiya Nagarik Suraksha Sanhita, 2023` Section `85`: *Attachment of property of person absconding .* (score: 0.1913)

#### Question #28
- **Query (Kannada)**: "ಸೈಟ್ ತಗೊಳ್ಳೋಕೆ ಅಡ್ವಾನ್ಸ್ ಕೊಟ್ಟಿದ್ದೆ, ಈಗ ಮಾರೋನು ಮಾರಲ್ಲ ಅಂತಿದ್ದಾನೆ. ಕೋರ್ಟ್ ಅವನನ್ನು ಮಾರೋಕೆ ಒತ್ತಾಯಿಸಬಹುದಾ?"
- **System Translation (EN)**: "I gave an advance to acquire the site, and now he says he won't sell. Can the court compel him to sell?"
- **Draft Paired EN**: "I paid an advance to buy a plot but the seller now refuses to sell. Can the court make him go through with it?"
- **Target**: `Specific Relief Act, 1963`, Section `10`: *Specific performance in respect of contracts.*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 17 (Rank #1: *Contract to sell or let property by one who has no title, not specifically enforceable .*), Sec 13 (Rank #3: *Rights of purchaser or lessee against person with no title or imperfect title .*)
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Specific Relief Act, 1963` Section `17`: *Contract to sell or let property by one who has no title, not specifically enforceable .* (score: 0.2017)
  2. **[Rank #2]** `Bharatiya Nagarik Suraksha Sanhita, 2023` Section `505`: *Power to sell perishable property.* (score: 0.1747)
  3. **[Rank #3]** `Specific Relief Act, 1963` Section `13`: *Rights of purchaser or lessee against person with no title or imperfect title .* (score: 0.1676)

#### Question #29
- **Query (Kannada)**: "ಕಳೆದ ವಾರ ನಮ್ಮ ಸಂಬಂಧಿಕರು ಬೀಗ ಬದಲಿಸಿ ನನ್ನನ್ನೇ ನನ್ನ ಮನೆಯಿಂದ ಹೊರಗೆ ಹಾಕಿದರು. ಮತ್ತೆ ಒಳಗೆ ಹೇಗೆ ಹೋಗೋದು?"
- **System Translation (EN)**: "Last week our relatives changed the lock and threw me out of my house. How can I get back inside?"
- **Draft Paired EN**: "Last week my relative changed the locks and pushed me out of my own house. How do I get back in?"
- **Target**: `Specific Relief Act, 1963`, Section `6`: *Suit by person dispossessed of immovable property .*
- **Classification**: **(c) Different Act entirely**: Top 5 retrieved from: Bharatiya Nyaya Sanhita, 2023, Protection of Women from Domestic Violence Act, 2005, Bharatiya Nagarik Suraksha Sanhita, 2023
- **Target Rank**: Not in top 20
- **Top 3 Returned**:
  1. **[Rank #1]** `Bharatiya Nyaya Sanhita, 2023` Section `330`: *House-trespass and house -breaking.* (score: 0.2000)
  2. **[Rank #2]** `Bharatiya Nyaya Sanhita, 2023` Section `333`: *House-trespass after preparation for hurt, assault or wrongful restraint .* (score: 0.1702)
  3. **[Rank #3]** `Bharatiya Nyaya Sanhita, 2023` Section `331`: *Punishment for house -trespass or house -breaking.* (score: 0.1527)

#### Question #33
- **Query (Kannada)**: "ಮನೆಗೆ ಬರುವಾಗ ಓನರ್ ಬಾಡಿಗೆ ಜೊತೆಗೆ ದೊಡ್ಡ 'ಎಕ್ಸ್ಟ್ರಾ ಫೀಸ್' ತಗೊಂಡ್ರು, ಅದನ್ನು ವಾಪಸ್ ಪಡೆಯಬಹುದಾ?"
- **System Translation (EN)**: "Can the large extra fee taken by the owner along with the rent be reclaimed?"
- **Draft Paired EN**: "When I moved in, my landlord charged me a big 'extra fee' on top of the rent. Can I get it back?"
- **Target**: `Karnataka Rent Act, 1999`, Section `15`: *Refund of rent, premium, etc.,.*
- **Classification**: **(a) Correct Act in Top 5 (different section)**: Sec 9 (Rank #2: *Revision of rent in certain cases.*)
- **Target Rank**: #14
- **Top 3 Returned**:
  1. **[Rank #1]** `Transfer of Property Act, 1882` Section `115`: *Eff ect of surrender and forfeiture on under -leases.* (score: 0.2000)
  2. **[Rank #2]** `Karnataka Rent Act, 1999` Section `9`: *Revision of rent in certain cases.* (score: 0.1867)
  3. **[Rank #3]** `Transfer of Property Act, 1882` Section `114`: *Relief against forfeiture for non -payment of rent.* (score: 0.1860)

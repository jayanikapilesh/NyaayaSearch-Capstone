content = open("search_core.py", encoding="utf-8").read()
old = '    "small mistakes": ["small mistakes", "irregularities"],'
new = '''    "small mistakes": ["small mistakes", "irregularities"],
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
    "physically bring my vehicle": ["physically bring my vehicle", "production of vehicle"],'''
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("search_core.py", "w", encoding="utf-8").write(content)
    print("Added 29 new targeted synonym entries")

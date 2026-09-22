content = open("search_core.py", encoding="utf-8").read()
old = '    "blackmail": ["blackmail", "privacy violation", "obscene", "extortion"],'
new = '''    "blackmail": ["blackmail", "privacy violation", "obscene", "extortion"],
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
    "small mistakes": ["small mistakes", "irregularities"],'''
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("search_core.py", "w", encoding="utf-8").write(content)
    print("Added 15 new synonym entries")

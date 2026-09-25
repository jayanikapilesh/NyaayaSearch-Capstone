content = open("index.html", encoding="utf-8").read()
old = """    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>frontend</title>
  </head>"""
new = """    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>NyaayaSearch - Indian Legal Search</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,500;0,600;0,700;1,500&family=Noto+Sans:wght@400;500;600;700&family=Noto+Sans+Devanagari:wght@400;500;600;700&family=Noto+Sans+Kannada:wght@400;500;600;700&display=swap" rel="stylesheet">
  </head>"""
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("index.html", "w", encoding="utf-8").write(content)
    print("Added font imports (Lora + Noto Sans + Noto Sans Devanagari + Noto Sans Kannada) and real page title")

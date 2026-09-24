content = open("src/App.css", encoding="utf-8").read()
old = """* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  min-height: 100vh;
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  background: #f7f7f5;
  color: #1a1a1a;
}

.app {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 40px;
}

.header {
  text-align: center;
  margin-bottom: 32px;
}

.header h1 {
  font-size: 2.2rem;
  color: #1a3c34;
}

.tagline {
  color: #555;
  margin-top: 6px;
  font-size: 1rem;
}"""
new = """:root {
  --color-bg: #F0E9D8;
  --color-ink: #241F18;
  --color-ink-soft: #5C5347;
  --color-primary: #1A3C34;
  --color-primary-light: #24544A;
  --color-accent: #B8863B;
  --color-border: #D4C9AE;
  --font-heading: "Lora", Georgia, serif;
  --font-body: "Noto Sans", "Noto Sans Devanagari", "Noto Sans Kannada", -apple-system, sans-serif;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  min-height: 100vh;
  font-family: var(--font-body);
  background: var(--color-bg);
  color: var(--color-ink);
}

.app {
  max-width: 900px;
  margin: 0 auto;
  padding: 40px 40px;
}

.header {
  text-align: center;
  margin-bottom: 32px;
}

.header h1 {
  font-family: var(--font-heading);
  font-weight: 600;
  font-size: 2.4rem;
  color: var(--color-primary);
  letter-spacing: -0.01em;
}

.tagline {
  color: var(--color-ink-soft);
  margin-top: 6px;
  font-size: 1rem;
}"""
count = content.count(old)
print(f"Found {count} occurrence(s)")
if count == 1:
    content = content.replace(old, new)
    open("src/App.css", "w", encoding="utf-8").write(content)
    print("Applied real color/font system to base and header")

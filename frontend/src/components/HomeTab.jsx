const WORKFLOW_STEPS = [
  {
    title: "Describe your situation",
    description: "Type or speak your question in English, Hindi, or Kannada.",
  },
  {
    title: "We search real statutes",
    description: "Hybrid search matches your question to the exact Acts and Sections that apply.",
  },
  {
    title: "Get a plain-language explanation",
    description: "See what the law means for you, with every citation traceable to its source section.",
  },
  {
    title: "Explore more tools",
    description: "Draft documents, decode BNS sections, simplify judgments, and more.",
  },
];

const CAPABILITY_CARDS = [
  { tab: "search", title: "Search", description: "Describe a legal situation and get matched sections with a plain-language explanation." },
  { tab: "bns", title: "BNS Decoder", description: "Look up any Bharatiya Nyaya Sanhita section number and see what it means." },
  { tab: "drafter", title: "Document Generator", description: "Generate rent agreements, notices, and other legal documents from a guided form." },
  { tab: "simplifier", title: "Case Simplifier", description: "Paste a court judgment and get a plain-language summary." },
  { tab: "dictionary", title: "Dictionary", description: "Look up legal terms in plain English." },
  { tab: "quiz", title: "Legal IQ Daily", description: "Test your knowledge of Indian law with a daily quiz." },
];

function HomeTab({ navigateToTab }) {
  return (
    <div>
      <section className="home-hero">
        <h2 className="home-hero-title">Search, draft, and understand Indian law in plain language.</h2>
        <p className="home-hero-subtitle">
          NyaayaSearch matches your question to the exact Acts and Sections that apply, explains
          what they mean, and helps you act on them - in English, Hindi, or Kannada.
        </p>
        <button type="button" className="search-button home-hero-cta" onClick={function () { navigateToTab("search"); }}>
          Start Searching
        </button>
        <p className="home-stat">Currently covering 11 Acts and 1,887 sections of Indian law.</p>
      </section>

      <section className="home-section">
        <h2>How NyaayaSearch Works</h2>
        <ol className="workflow-list">
          {WORKFLOW_STEPS.map(function (step, i) {
            return (
              <li className="workflow-step" key={step.title}>
                <span className="workflow-number">{String(i + 1).padStart(2, "0")}</span>
                <div className="workflow-content">
                  <h3 className="workflow-title">{step.title}</h3>
                  <p className="workflow-description">{step.description}</p>
                </div>
              </li>
            );
          })}
        </ol>
      </section>

      <section className="home-section">
        <h2>What You Can Do Here</h2>
        <div className="capability-grid">
          {CAPABILITY_CARDS.map(function (card) {
            return (
              <button
                type="button"
                className="capability-card"
                key={card.tab}
                onClick={function () { navigateToTab(card.tab); }}
              >
                <span className="capability-card-title">{card.title}</span>
                <span className="capability-card-description">{card.description}</span>
              </button>
            );
          })}
        </div>
      </section>
    </div>
  );
}

export default HomeTab;

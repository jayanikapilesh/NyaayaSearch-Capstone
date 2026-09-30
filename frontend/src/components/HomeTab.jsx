import { useEffect, useState } from "react";
import { API_URL, ALL_LANGUAGES } from "../constants";
import { getHomeContent } from "../homeContent";
import { loadHistory } from "../utils";
import {
  SearchIcon, DraftIcon, DictionaryIcon, FolderIcon, SimplifyIcon, BookIcon, QuizIcon, CheckIcon, MicIcon,
} from "./icons";

const FEATURE_ICONS = {
  search: SearchIcon,
  drafter: DraftIcon,
  dictionary: DictionaryIcon,
  documents: FolderIcon,
  simplifier: SimplifyIcon,
  bns: BookIcon,
  quiz: QuizIcon,
};

function SectionVisual({ variant }) {
  // Purely decorative - the adjacent heading/body text (rendered right next
  // to this in HomeTab) already says everything a reader needs, so this is
  // hidden from screen readers rather than announced as a vague "image".
  return (
    <div className={"section-visual section-visual-" + variant} aria-hidden="true">
      <div className="section-visual-glow" aria-hidden="true" />
      {variant === "problem" ? (
        // Illustrates the "Problem" copy directly: dense legal text (tightly
        // packed lines) scattered across sources (the GOV/PDF/PORTAL tags on
        // each card), with the search icon on top picking one clear,
        // highlighted line out of the clutter.
        <div className="visual-stack">
          <span className="visual-source-tag visual-source-tag-a">GOV</span>
          <span className="visual-source-tag visual-source-tag-b">PDF</span>
          <span className="visual-source-tag visual-source-tag-c">PORTAL</span>
          <div className="visual-card visual-card-back">
            <span className="visual-line visual-line-full" />
            <span className="visual-line visual-line-full" />
            <span className="visual-line visual-line-full" />
            <span className="visual-line visual-line-short" />
          </div>
          <div className="visual-card visual-card-mid">
            <span className="visual-line visual-line-full" />
            <span className="visual-line visual-line-full" />
            <span className="visual-line visual-line-short" />
          </div>
          <div className="visual-card visual-card-front">
            <SearchIcon className="visual-card-icon" />
            <span className="visual-line visual-line-full" />
            <span className="visual-line visual-line-highlight" />
            <span className="visual-line visual-line-full" />
            <span className="visual-line visual-line-short" />
          </div>
        </div>
      ) : (
        // Illustrates the "Support For Every Reader" copy: the three
        // language chips connect to one shared center (search stays the
        // same experience in any language), and the mic badge nods to the
        // voice-input feature named in the body text.
        <div className="visual-cluster">
          <svg className="visual-cluster-lines" viewBox="0 0 220 180" aria-hidden="true">
            <line x1="110" y1="90" x2="44" y2="24" />
            <line x1="110" y1="90" x2="180" y2="32" />
            <line x1="110" y1="90" x2="110" y2="156" />
          </svg>
          <span className="visual-chip visual-chip-a">EN</span>
          <span className="visual-chip visual-chip-b">हिं</span>
          <span className="visual-chip visual-chip-c">ಕನ್</span>
          <div className="visual-cluster-center">
            <BookIcon className="visual-cluster-icon" />
            <span className="visual-mic-badge">
              <MicIcon width="14" height="14" />
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

function HomeTab({ navigateToTab, uiLanguage, isActive, onContinueLastSearch }) {
  const content = getHomeContent(uiLanguage);
  const [stats, setStats] = useState(null);
  const [statsError, setStatsError] = useState(false);

  // Returning users get a way back into their last search without
  // disturbing the onboarding content below - this stays empty (and
  // renders nothing) for first-time users with no search history yet.
  const [lastQuery, setLastQuery] = useState(function () {
    const history = loadHistory();
    return history.length > 0 ? history[0] : null;
  });

  useEffect(function () {
    if (!isActive) return;
    const timer = setTimeout(function () {
      const history = loadHistory();
      setLastQuery(history.length > 0 ? history[0] : null);
    }, 0);
    return function () { clearTimeout(timer); };
  }, [isActive]);

  useEffect(function () {
    let cancelled = false;
    fetch(API_URL + "/stats")
      .then(function (res) {
        if (!res.ok) throw new Error("stats request failed");
        return res.json();
      })
      .then(function (data) {
        if (!cancelled) setStats(data);
      })
      .catch(function () {
        if (!cancelled) setStatsError(true);
      });
    return function () { cancelled = true; };
  }, []);

  const statPills = stats
    ? [
        { key: "acts", value: stats.acts, suffix: "+", label: content.statsLabels.acts },
        { key: "sections", value: stats.sections, suffix: "+", label: content.statsLabels.sections },
        { key: "cases", value: stats.supreme_court_cases, suffix: "+", label: content.statsLabels.cases },
        { key: "languages", value: ALL_LANGUAGES.length, suffix: "", label: content.statsLabels.languages },
      ]
    : [];

  return (
    <div className="home">
      <section className="home-hero">
        {/* Hero background is a pure-CSS radial gradient + dot-grid texture - see .home-hero-bg in App.css */}
        <div className="home-hero-bg" aria-hidden="true" />
        <div className="home-hero-overlay" aria-hidden="true" />

        <div className="home-inner home-hero-content">
          <span className="home-eyebrow-badge">{content.eyebrow}</span>
          <h1 className="home-hero-title">
            <span className="home-hero-title-gradient">{content.heroHeadlineLine1}</span>
            <span className="home-hero-title-line2">{content.heroHeadlineLine2}</span>
          </h1>
          <p className="home-hero-subtitle">{content.heroSubtitle}</p>
          <button type="button" className="home-hero-cta" onClick={function () { navigateToTab("search"); }}>
            {content.ctaLabel} <span aria-hidden="true">→</span>
          </button>

          {lastQuery && (
            <button
              type="button"
              className="home-continue-card"
              onClick={function () { onContinueLastSearch(lastQuery); }}
            >
              <span className="home-continue-label">{content.continueHeading}</span>
              <span className="home-continue-query">"{lastQuery}"</span>
            </button>
          )}

          {!statsError && (
            <div className="home-stats-row">
              {stats
                ? statPills.map(function (stat) {
                    return (
                      <div className="stat-pill" key={stat.key}>
                        <span className="stat-pill-value">{stat.value.toLocaleString()}{stat.suffix}</span>
                        <span className="stat-pill-label">{stat.label}</span>
                      </div>
                    );
                  })
                : [0, 1, 2, 3].map(function (i) {
                    return <span className="stat-pill stat-pill-skeleton" key={i} />;
                  })}
            </div>
          )}
        </div>
      </section>

      <section className="home-alt-section">
        <div className="home-inner home-alt-grid">
          <div className="home-alt-text">
            <span className="home-eyebrow">{content.problem.eyebrow}</span>
            <h2 className="home-alt-heading">{content.problem.heading}</h2>
            <p className="home-alt-body">{content.problem.body}</p>
          </div>
          <div className="home-alt-media">
            <SectionVisual variant="problem" />
          </div>
        </div>
      </section>

      <section className="home-alt-section home-alt-section-reverse">
        <div className="home-inner home-alt-grid">
          <div className="home-alt-text">
            <span className="home-eyebrow">{content.howItWorksSection.eyebrow}</span>
            <h2 className="home-alt-heading">{content.howItWorksSection.heading}</h2>
            <p className="home-alt-body">{content.howItWorksSection.body}</p>
          </div>
          <div className="home-alt-media">
            <div className="workflow-card">
              <h3 className="workflow-card-title">{content.workflowHeading}</h3>
              <ul className="workflow-checklist">
                {content.workflowSteps.map(function (step) {
                  return (
                    <li className="workflow-checklist-item" key={step.title}>
                      <CheckIcon className="workflow-checklist-icon" />
                      <div>
                        <div className="workflow-checklist-title">{step.title}</div>
                        <div className="workflow-checklist-description">{step.description}</div>
                      </div>
                    </li>
                  );
                })}
              </ul>
            </div>
          </div>
        </div>
      </section>

      <section className="home-alt-section">
        <div className="home-inner home-alt-grid">
          <div className="home-alt-text">
            <span className="home-eyebrow">{content.everyone.eyebrow}</span>
            <h2 className="home-alt-heading">{content.everyone.heading}</h2>
            <p className="home-alt-body">{content.everyone.body}</p>
          </div>
          <div className="home-alt-media">
            <SectionVisual variant="everyone" />
          </div>
        </div>
      </section>

      <section className="home-section">
        <div className="home-inner">
          <h2 className="home-section-heading">{content.featureCardsHeading}</h2>
          <div className="feature-card-grid">
            {content.featureCards.map(function (card) {
              const Icon = FEATURE_ICONS[card.tab];
              return (
                <button
                  type="button"
                  className="feature-card"
                  key={card.tab}
                  onClick={function () { navigateToTab(card.tab); }}
                >
                  <Icon className="feature-card-icon" />
                  <span className="feature-card-title">{card.title}</span>
                  <span className="feature-card-description">{card.description}</span>
                </button>
              );
            })}
          </div>
        </div>
      </section>

      <footer className="home-footer-disclaimer">{content.footerDisclaimer}</footer>
    </div>
  );
}

export default HomeTab;

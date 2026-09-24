import { useEffect, useState } from "react";
import { API_URL, ALL_LANGUAGES } from "../constants";
import { getHomeContent } from "../homeContent";
import {
  SearchIcon, DraftIcon, DictionaryIcon, FolderIcon, SimplifyIcon, BookIcon, QuizIcon, CheckIcon, ImageIcon,
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

function ImagePlaceholder({ subject }) {
  return (
    <div className="image-placeholder" role="img" aria-label={subject}>
      <ImageIcon className="image-placeholder-icon" />
    </div>
  );
}

function HomeTab({ navigateToTab, uiLanguage }) {
  const content = getHomeContent(uiLanguage);
  const [stats, setStats] = useState(null);
  const [statsError, setStatsError] = useState(false);

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
        {/* TODO: wide hero background image - old parliament / law-book texture, dark, low contrast */}
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
            <ImagePlaceholder subject={content.problem.imageSubject} />
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
            <ImagePlaceholder subject={content.everyone.imageSubject} />
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

import { ALL_LANGUAGES } from "../constants";
import { getNavContent } from "../navContent";
import { BrandIcon, SunIcon, MoonIcon } from "./icons";

function TopBar({ darkMode, toggleDarkMode, uiLanguage, setUiLanguage }) {
  const content = getNavContent(uiLanguage);

  return (
    <header className="top-bar">
      <div className="top-bar-brand">
        <BrandIcon className="top-bar-logo" />
        <span className="top-bar-name">Nyaaya<span className="top-bar-name-gold">Search</span></span>
      </div>
      <div className="top-bar-actions">
        <div className="lang-switcher" role="group" aria-label={content.languageSwitcherLabel}>
          {ALL_LANGUAGES.map(function (lang) {
            return (
              <button
                key={lang}
                type="button"
                className={"lang-switcher-button" + (uiLanguage === lang ? " active" : "")}
                aria-pressed={uiLanguage === lang}
                onClick={function () { setUiLanguage(lang); }}
              >
                {lang.toUpperCase()}
              </button>
            );
          })}
        </div>
        <button
          type="button"
          className="theme-toggle-button"
          onClick={toggleDarkMode}
          aria-label={darkMode ? content.themeToggleToLight : content.themeToggleToDark}
        >
          {darkMode ? <SunIcon width="18" height="18" /> : <MoonIcon width="18" height="18" />}
        </button>
      </div>
    </header>
  );
}

export default TopBar;

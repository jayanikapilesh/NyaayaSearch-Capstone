import { useState, useEffect, useRef, lazy, Suspense } from "react";
import "./App.css";
import SplashScreen from "./components/SplashScreen";
import TopBar from "./components/TopBar";
import BottomNav from "./components/BottomNav";
import EmergencyButton from "./components/EmergencyButton";
import { WarningIcon } from "./components/icons";
import HomeTab from "./components/HomeTab";
import SearchTab from "./components/SearchTab";
import DictionaryTab from "./components/DictionaryTab";
import DocumentsTab from "./components/DocumentsTab";
import SimplifierTab from "./components/SimplifierTab";
import EmergencyTab from "./components/EmergencyTab";
import BnsTab from "./components/BnsTab";
import QuizTab from "./components/QuizTab";

const DrafterTab = lazy(function () { return import("./components/DrafterTab"); });

const DRAFTER_LOADING_LABEL = {
  en: "Loading Document Generator...",
  hi: "डॉक्यूमेंट जनरेटर लोड हो रहा है...",
  kn: "ಡಾಕುಮೆಂಟ್ ಜನರೇಟರ್ ಲೋಡ್ ಆಗುತ್ತಿದೆ...",
};

function App() {
  const [activeTab, setActiveTab] = useState("home");
  const activeTabRef = useRef("home");
  const [errorState, setErrorState] = useState(null);
  const errorTimeoutRef = useRef(null);
  const [hasVisitedDrafter, setHasVisitedDrafter] = useState(false);
  const [uiLanguage, setUiLanguage] = useState("en");
  const [pendingViewSavedId, setPendingViewSavedId] = useState(null);
  const [pendingBnsSection, setPendingBnsSection] = useState(null);
  const [pendingCaseContext, setPendingCaseContext] = useState(null);
  const [pendingSearchQuery, setPendingSearchQuery] = useState(null);

  const [darkMode, setDarkMode] = useState(function () {
    try {
      const stored = localStorage.getItem("nyaaya-dark-mode");
      return stored === null ? false : stored === "true";
    } catch (e) {
      return false;
    }
  });

  useEffect(function () {
    document.documentElement.classList.toggle("dark-mode", darkMode);
    try {
      localStorage.setItem("nyaaya-dark-mode", darkMode ? "true" : "false");
    } catch (e) {
      return;
    }
  }, [darkMode]);

  const toggleDarkMode = function () { setDarkMode(function (prev) { return !prev; }); };

  useEffect(function () { activeTabRef.current = activeTab; }, [activeTab]);

  const ERROR_AUTO_DISMISS_MS = 6000;

  const dismissError = function () {
    if (errorTimeoutRef.current) {
      clearTimeout(errorTimeoutRef.current);
      errorTimeoutRef.current = null;
    }
    setErrorState(null);
  };

  // Each tab gets its own error setter (below). A tab can only show/clear its
  // own error, and a background request that resolves after the user has
  // already navigated away is dropped instead of popping up on whatever tab
  // (e.g. Emergency Contacts) the user is looking at now.
  const setTabError = function (tabName, message) {
    if (!message) {
      if (!errorState || errorState.tab === tabName) dismissError();
      return;
    }
    if (activeTabRef.current !== tabName) return;
    if (errorTimeoutRef.current) clearTimeout(errorTimeoutRef.current);
    setErrorState({ tab: tabName, message: message });
    errorTimeoutRef.current = setTimeout(dismissError, ERROR_AUTO_DISMISS_MS);
  };

  const setDrafterError = function (message) { setTabError("drafter", message); };
  const setBnsError = function (message) { setTabError("bns", message); };
  const setSimplifierError = function (message) { setTabError("simplifier", message); };
  const setDocumentsError = function (message) { setTabError("documents", message); };
  const setSearchError = function (message) { setTabError("search", message); };

  const navigateToTab = function (tab) {
    dismissError();
    setActiveTab(tab);
    if (tab === "drafter") setHasVisitedDrafter(true);
  };

  // My Documents shows a summary of saved searches (they live in SearchTab's
  // own storage) with a way to jump straight to one, since we don't want to
  // duplicate how a saved result is displayed in two places.
  const openSavedSearchInSearchTab = function (savedId) {
    setPendingViewSavedId(savedId);
    navigateToTab("search");
  };

  // "Look up this section" (Search -> BNS Decoder) and "Simplify this case"
  // (Search -> Case Simplifier) are both one-shot handoffs: set what the
  // destination tab should do with, then navigate. Each destination clears
  // its own pending value once it has acted on it.
  const lookUpBnsSection = function (sectionNumber) {
    setPendingBnsSection(sectionNumber);
    navigateToTab("bns");
  };

  const simplifyCaseInSimplifierTab = function (caseInfo) {
    setPendingCaseContext(caseInfo);
    navigateToTab("simplifier");
  };

  // Home's "Continue where you left off" hands the last query to Search the
  // same way, rather than Home re-running the search itself.
  const continueLastSearch = function (lastQuery) {
    setPendingSearchQuery(lastQuery);
    navigateToTab("search");
  };

  return (
    <div className={"app" + (darkMode ? " dark-mode" : "")}>
      <SplashScreen />
      <TopBar
        darkMode={darkMode}
        toggleDarkMode={toggleDarkMode}
        uiLanguage={uiLanguage}
        setUiLanguage={setUiLanguage}
        showBack={activeTab !== "home"}
        onBack={function () { navigateToTab("home"); }}
      />

      <main className="app-content">
        {errorState && (
          <div className="app-toast-error" role="alert">
            <WarningIcon className="error-icon" />
            <span>{errorState.message}</span>
            <button type="button" className="app-toast-error-close" onClick={dismissError} aria-label="Dismiss">×</button>
          </div>
        )}

        {/* Home is full-bleed (its own sections manage width); every other tab is boxed to a readable column. */}
        <div className="tab-transition" style={{ display: activeTab === "home" ? "block" : "none" }}>
          <HomeTab
            navigateToTab={navigateToTab}
            uiLanguage={uiLanguage}
            isActive={activeTab === "home"}
            onContinueLastSearch={continueLastSearch}
          />
        </div>
        <div className="tab-content-boxed tab-transition" style={{ display: activeTab === "dictionary" ? "block" : "none" }}><DictionaryTab uiLanguage={uiLanguage} /></div>
        <div className="tab-content-boxed tab-transition" style={{ display: activeTab === "drafter" ? "block" : "none" }}>
          {hasVisitedDrafter && (
            <Suspense fallback={<div className="loading">{DRAFTER_LOADING_LABEL[uiLanguage] || DRAFTER_LOADING_LABEL.en}</div>}>
              <DrafterTab setError={setDrafterError} uiLanguage={uiLanguage} />
            </Suspense>
          )}
        </div>
        <div className="tab-content-boxed tab-transition" style={{ display: activeTab === "bns" ? "block" : "none" }}>
          <BnsTab
            setError={setBnsError}
            uiLanguage={uiLanguage}
            pendingSection={pendingBnsSection}
            onConsumePendingSection={function () { setPendingBnsSection(null); }}
          />
        </div>
        <div className="tab-content-boxed tab-transition" style={{ display: activeTab === "quiz" ? "block" : "none" }}><QuizTab uiLanguage={uiLanguage} isActive={activeTab === "quiz"} /></div>
        <div className="tab-content-boxed tab-transition" style={{ display: activeTab === "emergency" ? "block" : "none" }}><EmergencyTab uiLanguage={uiLanguage} /></div>
        <div className="tab-content-boxed tab-transition" style={{ display: activeTab === "simplifier" ? "block" : "none" }}>
          <SimplifierTab
            setError={setSimplifierError}
            uiLanguage={uiLanguage}
            pendingCaseContext={pendingCaseContext}
            onConsumePendingCaseContext={function () { setPendingCaseContext(null); }}
          />
        </div>
        <div className="tab-content-boxed tab-transition" style={{ display: activeTab === "documents" ? "block" : "none" }}>
          <DocumentsTab
            setError={setDocumentsError}
            uiLanguage={uiLanguage}
            isActive={activeTab === "documents"}
            onOpenSavedSearch={openSavedSearchInSearchTab}
          />
        </div>
        <div className="tab-content-boxed tab-transition" style={{ display: activeTab === "search" ? "block" : "none" }}>
          <SearchTab
            setError={setSearchError}
            uiLanguage={uiLanguage}
            onLanguageChange={setUiLanguage}
            isActive={activeTab === "search"}
            pendingViewSavedId={pendingViewSavedId}
            onConsumePendingViewSavedId={function () { setPendingViewSavedId(null); }}
            onLookUpBnsSection={lookUpBnsSection}
            onSimplifyCase={simplifyCaseInSimplifierTab}
            pendingSearchQuery={pendingSearchQuery}
            onConsumePendingSearchQuery={function () { setPendingSearchQuery(null); }}
          />
        </div>
      </main>

      <BottomNav activeTab={activeTab} navigateToTab={navigateToTab} uiLanguage={uiLanguage} />
      <EmergencyButton navigateToTab={navigateToTab} uiLanguage={uiLanguage} />
    </div>
  );
}

export default App;

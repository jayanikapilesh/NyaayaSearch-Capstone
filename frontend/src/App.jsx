import { useState, useEffect, lazy, Suspense } from "react";
import "./App.css";
import SplashScreen from "./components/SplashScreen";
import TopBar from "./components/TopBar";
import BottomNav from "./components/BottomNav";
import EmergencyButton from "./components/EmergencyButton";
import HomeTab from "./components/HomeTab";
import SearchTab from "./components/SearchTab";
import DictionaryTab from "./components/DictionaryTab";
import DocumentsTab from "./components/DocumentsTab";
import SimplifierTab from "./components/SimplifierTab";
import EmergencyTab from "./components/EmergencyTab";
import BnsTab from "./components/BnsTab";
import QuizTab from "./components/QuizTab";

const DrafterTab = lazy(function () { return import("./components/DrafterTab"); });

function App() {
  const [activeTab, setActiveTab] = useState("home");
  const [error, setError] = useState(null);
  const [hasVisitedDrafter, setHasVisitedDrafter] = useState(false);
  const [uiLanguage, setUiLanguage] = useState("en");

  const [darkMode, setDarkMode] = useState(function () {
    try {
      const stored = localStorage.getItem("nyaaya-dark-mode");
      return stored === null ? true : stored === "true";
    } catch (e) {
      return true;
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

  const navigateToTab = function (tab) {
    setActiveTab(tab);
    if (tab === "drafter") setHasVisitedDrafter(true);
  };

  return (
    <div className={"app" + (darkMode ? " dark-mode" : "")}>
      <SplashScreen />
      <TopBar darkMode={darkMode} toggleDarkMode={toggleDarkMode} uiLanguage={uiLanguage} setUiLanguage={setUiLanguage} />

      <main className="app-content">
        {error && (
          <div className="tab-content-boxed" style={{ paddingBottom: 0 }}>
            <div className="error" role="alert">{error}</div>
          </div>
        )}

        {/* Home is full-bleed (its own sections manage width); every other tab is boxed to a readable column. */}
        <div style={{ display: activeTab === "home" ? "block" : "none" }}><HomeTab navigateToTab={navigateToTab} uiLanguage={uiLanguage} /></div>
        <div className="tab-content-boxed" style={{ display: activeTab === "dictionary" ? "block" : "none" }}><DictionaryTab uiLanguage={uiLanguage} /></div>
        <div className="tab-content-boxed" style={{ display: activeTab === "drafter" ? "block" : "none" }}>
          {hasVisitedDrafter && (
            <Suspense fallback={<div className="loading">Loading Document Generator...</div>}>
              <DrafterTab setError={setError} />
            </Suspense>
          )}
        </div>
        <div className="tab-content-boxed" style={{ display: activeTab === "bns" ? "block" : "none" }}><BnsTab setError={setError} /></div>
        <div className="tab-content-boxed" style={{ display: activeTab === "quiz" ? "block" : "none" }}><QuizTab /></div>
        <div className="tab-content-boxed" style={{ display: activeTab === "emergency" ? "block" : "none" }}><EmergencyTab uiLanguage={uiLanguage} /></div>
        <div className="tab-content-boxed" style={{ display: activeTab === "simplifier" ? "block" : "none" }}><SimplifierTab setError={setError} /></div>
        <div className="tab-content-boxed" style={{ display: activeTab === "documents" ? "block" : "none" }}><DocumentsTab setError={setError} /></div>
        <div className="tab-content-boxed" style={{ display: activeTab === "search" ? "block" : "none" }}><SearchTab setError={setError} uiLanguage={uiLanguage} onLanguageChange={setUiLanguage} /></div>
      </main>

      <BottomNav activeTab={activeTab} navigateToTab={navigateToTab} uiLanguage={uiLanguage} />
      <EmergencyButton navigateToTab={navigateToTab} uiLanguage={uiLanguage} />
    </div>
  );
}

export default App;

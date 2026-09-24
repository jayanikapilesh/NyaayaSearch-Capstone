import { useState, useEffect } from "react";
import "./App.css";
import SearchTab from "./components/SearchTab";
import DrafterTab from "./components/DrafterTab";
import DictionaryTab from "./components/DictionaryTab";
import DocumentsTab from "./components/DocumentsTab";
import SimplifierTab from "./components/SimplifierTab";
import EmergencyTab from "./components/EmergencyTab";
import BnsTab from "./components/BnsTab";
import QuizTab from "./components/QuizTab";

function App() {
  const [activeTab, setActiveTab] = useState("search");
  const [error, setError] = useState(null);

  const [darkMode, setDarkMode] = useState(function () {
    try {
      return localStorage.getItem("nyaaya-dark-mode") === "true";
    } catch (e) {
      return false;
    }
  });

  useEffect(function () {
    try {
      localStorage.setItem("nyaaya-dark-mode", darkMode ? "true" : "false");
      document.body.style.background = darkMode ? "#1a1a1a" : "#f7f7f5";
    } catch (e) {
      return;
    }
  }, [darkMode]);

  const toggleDarkMode = function () { setDarkMode(function (prev) { return !prev; }); };

  return (
    <div className={"app" + (darkMode ? " dark-mode" : "")}>
      <header className="header">
        <div className="header-top">
          <h1>NyaayaSearch</h1>
          <button className="theme-toggle" onClick={toggleDarkMode}>
            {darkMode ? "Light Mode" : "Dark Mode"}
          </button>
        </div>
        <p className="tagline">Understand Indian law in plain language</p>
      </header>

      <nav className="tab-nav">
        <button className={"tab-button" + (activeTab === "search" ? " active" : "")} onClick={function () { setActiveTab("search"); }}>Search</button>
        <button className={"tab-button" + (activeTab === "drafter" ? " active" : "")} onClick={function () { setActiveTab("drafter"); }}>Document Generator</button>
        <button className={"tab-button" + (activeTab === "dictionary" ? " active" : "")} onClick={function () { setActiveTab("dictionary"); }}>Dictionary</button>
        <button className={"tab-button" + (activeTab === "documents" ? " active" : "")} onClick={function () { setActiveTab("documents"); }}>My Documents</button>
        <button className={"tab-button" + (activeTab === "simplifier" ? " active" : "")} onClick={function () { setActiveTab("simplifier"); }}>Case Simplifier</button>
        <button className={"tab-button" + (activeTab === "emergency" ? " active" : "")} onClick={function () { setActiveTab("emergency"); }}>Emergency Help</button>
        <button className={"tab-button" + (activeTab === "bns" ? " active" : "")} onClick={function () { setActiveTab("bns"); }}>BNS Decoder</button>
        <button className={"tab-button" + (activeTab === "quiz" ? " active" : "")} onClick={function () { setActiveTab("quiz"); }}>Legal IQ Daily</button>
      </nav>

      {error && <div className="error">{error}</div>}

      <div style={{ display: activeTab === "dictionary" ? "block" : "none" }}><DictionaryTab /></div>
      <div style={{ display: activeTab === "drafter" ? "block" : "none" }}><DrafterTab setError={setError} /></div>
      <div style={{ display: activeTab === "bns" ? "block" : "none" }}><BnsTab setError={setError} /></div>
      <div style={{ display: activeTab === "quiz" ? "block" : "none" }}><QuizTab /></div>
      <div style={{ display: activeTab === "emergency" ? "block" : "none" }}><EmergencyTab /></div>
      <div style={{ display: activeTab === "simplifier" ? "block" : "none" }}><SimplifierTab setError={setError} /></div>
      <div style={{ display: activeTab === "documents" ? "block" : "none" }}><DocumentsTab setError={setError} /></div>
      <div style={{ display: activeTab === "search" ? "block" : "none" }}><SearchTab setError={setError} /></div>
    </div>
  );
}

export default App;

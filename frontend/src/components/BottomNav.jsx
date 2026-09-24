import { useEffect, useRef, useState } from "react";
import { HomeIcon, SearchIcon, BookIcon, FolderIcon, MoreIcon } from "./icons";

const PRIMARY_ITEMS = [
  { tab: "home", label: "Home", Icon: HomeIcon },
  { tab: "search", label: "Search", Icon: SearchIcon },
  { tab: "bns", label: "BNS Decoder", Icon: BookIcon },
  { tab: "documents", label: "My Documents", Icon: FolderIcon },
];

const MORE_ITEMS = [
  { tab: "drafter", label: "Document Generator" },
  { tab: "dictionary", label: "Dictionary" },
  { tab: "simplifier", label: "Case Simplifier" },
  { tab: "quiz", label: "Legal IQ Daily" },
];

function BottomNav({ activeTab, navigateToTab }) {
  const [moreOpen, setMoreOpen] = useState(false);
  const wrapRef = useRef(null);

  useEffect(function () {
    if (!moreOpen) return;
    function handleOutsideClick(e) {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) setMoreOpen(false);
    }
    document.addEventListener("mousedown", handleOutsideClick);
    return function () { document.removeEventListener("mousedown", handleOutsideClick); };
  }, [moreOpen]);

  const isMoreActive = MORE_ITEMS.some(function (item) { return item.tab === activeTab; });

  const goTo = function (tab) {
    navigateToTab(tab);
    setMoreOpen(false);
  };

  return (
    <div className="bottom-nav-wrap" ref={wrapRef}>
      {moreOpen && (
        <div className="more-menu" role="menu">
          {MORE_ITEMS.map(function (item) {
            return (
              <button
                key={item.tab}
                type="button"
                role="menuitem"
                className={"more-menu-item" + (activeTab === item.tab ? " active" : "")}
                onClick={function () { goTo(item.tab); }}
              >
                {item.label}
              </button>
            );
          })}
        </div>
      )}
      <nav className="bottom-nav" aria-label="Primary">
        {PRIMARY_ITEMS.map(function (item) {
          const Icon = item.Icon;
          const isActive = activeTab === item.tab;
          return (
            <button
              key={item.tab}
              type="button"
              className={"bottom-nav-item" + (isActive ? " active" : "")}
              aria-current={isActive ? "page" : undefined}
              onClick={function () { goTo(item.tab); }}
            >
              <span className="bottom-nav-icon"><Icon /></span>
              <span className="bottom-nav-label">{item.label}</span>
            </button>
          );
        })}
        <button
          type="button"
          className={"bottom-nav-item" + (isMoreActive ? " active" : "")}
          aria-haspopup="true"
          aria-expanded={moreOpen}
          onClick={function () { setMoreOpen(function (v) { return !v; }); }}
        >
          <span className="bottom-nav-icon"><MoreIcon /></span>
          <span className="bottom-nav-label">More</span>
        </button>
      </nav>
    </div>
  );
}

export default BottomNav;

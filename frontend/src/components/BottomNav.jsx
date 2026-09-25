import { useEffect, useRef, useState } from "react";
import { getNavContent } from "../navContent";
import { HomeIcon, SearchIcon, BookIcon, FolderIcon, MoreIcon } from "./icons";

const PRIMARY_TABS = [
  { tab: "home", key: "home", Icon: HomeIcon },
  { tab: "search", key: "search", Icon: SearchIcon },
  { tab: "bns", key: "bns", Icon: BookIcon },
  { tab: "documents", key: "documents", Icon: FolderIcon },
];

const MORE_TABS = [
  { tab: "drafter", key: "drafter" },
  { tab: "dictionary", key: "dictionary" },
  { tab: "simplifier", key: "simplifier" },
  { tab: "quiz", key: "quiz" },
];

function BottomNav({ activeTab, navigateToTab, uiLanguage }) {
  const [moreOpen, setMoreOpen] = useState(false);
  const wrapRef = useRef(null);
  const content = getNavContent(uiLanguage);

  useEffect(function () {
    if (!moreOpen) return;
    function handleOutsideClick(e) {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) setMoreOpen(false);
    }
    document.addEventListener("mousedown", handleOutsideClick);
    return function () { document.removeEventListener("mousedown", handleOutsideClick); };
  }, [moreOpen]);

  const isMoreActive = MORE_TABS.some(function (item) { return item.tab === activeTab; });

  const goTo = function (tab) {
    navigateToTab(tab);
    setMoreOpen(false);
  };

  return (
    <div className="bottom-nav-wrap" ref={wrapRef}>
      {moreOpen && (
        <div className="more-menu" role="menu" aria-label={content.moreMenuLabel}>
          {MORE_TABS.map(function (item) {
            return (
              <button
                key={item.tab}
                type="button"
                role="menuitem"
                className={"more-menu-item" + (activeTab === item.tab ? " active" : "")}
                onClick={function () { goTo(item.tab); }}
              >
                {content.more[item.key]}
              </button>
            );
          })}
        </div>
      )}
      <nav className="bottom-nav" aria-label={content.primaryNavLabel}>
        {PRIMARY_TABS.map(function (item) {
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
              <span className="bottom-nav-label">{content.nav[item.key]}</span>
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
          <span className="bottom-nav-label">{content.nav.more}</span>
        </button>
      </nav>
    </div>
  );
}

export default BottomNav;

import { useEffect, useState } from "react";
import { WarningIcon } from "./icons";

const LABELS = {
  en: { full: "Emergency Help", short: "SOS" },
  hi: { full: "आपात सहायता", short: "SOS" },
  kn: { full: "ತುರ್ತು ಸಹಾಯ", short: "SOS" },
};

const PULSE_SEEN_KEY = "nyaaya-emergency-pulse-seen";
const PULSE_DURATION_MS = 4000;

function EmergencyButton({ navigateToTab, uiLanguage }) {
  const [pulse, setPulse] = useState(function () {
    try {
      return localStorage.getItem(PULSE_SEEN_KEY) !== "true";
    } catch {
      return false;
    }
  });

  useEffect(function () {
    if (!pulse) return;

    const timer = setTimeout(function () { setPulse(false); }, PULSE_DURATION_MS);

    try {
      localStorage.setItem(PULSE_SEEN_KEY, "true");
    } catch {
      // ignore - pulse will just show again next visit, not critical
    }

    return function () { clearTimeout(timer); };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const labels = LABELS[uiLanguage] || LABELS.en;

  return (
    <button
      type="button"
      className={"emergency-fab" + (pulse ? " emergency-fab-pulse" : "")}
      onClick={function () { navigateToTab("emergency"); }}
      aria-label={labels.full}
    >
      <WarningIcon width="20" height="20" />
      <span className="emergency-fab-label emergency-fab-label-full">{labels.full}</span>
      <span className="emergency-fab-label emergency-fab-label-short" aria-hidden="true">{labels.short}</span>
    </button>
  );
}

export default EmergencyButton;

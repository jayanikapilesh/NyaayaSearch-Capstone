import { useEffect, useState } from "react";
import { BrandIcon } from "./icons";

const SPLASH_VISIBLE_MS = 1500;
const SPLASH_FADE_MS = 400;

function SplashScreen() {
  const [phase, setPhase] = useState("visible");

  useEffect(function () {
    const fadeTimer = setTimeout(function () { setPhase("fading"); }, SPLASH_VISIBLE_MS);
    return function () { clearTimeout(fadeTimer); };
  }, []);

  useEffect(function () {
    if (phase !== "fading") return;
    const doneTimer = setTimeout(function () { setPhase("done"); }, SPLASH_FADE_MS);
    return function () { clearTimeout(doneTimer); };
  }, [phase]);

  if (phase === "done") return null;

  return (
    <div className={"splash-screen" + (phase === "fading" ? " splash-fading" : "")} role="presentation" aria-hidden="true">
      <div className="splash-logo-ring">
        <BrandIcon className="splash-logo" width="52" height="52" />
      </div>
      <h1 className="splash-title">Nyaaya<span className="splash-title-gold">Search</span></h1>
      <div className="splash-underline" />
    </div>
  );
}

export default SplashScreen;

import { getEmergencyContent } from "../emergencyContent";

function EmergencyTab({ uiLanguage }) {
  const content = getEmergencyContent(uiLanguage);

  return (
    <div className="drafter-section">
      <a href="tel:112" className="call-112-button">{content.call112}</a>

      <h2>{content.heading}</h2>
      <p className="drafter-intro">{content.intro}</p>

      <div className="emergency-list">
        <div className="emergency-item">
          <div className="emergency-title">{content.policeTitle}</div>
          <div className="emergency-number">
            <a href="tel:100">100</a> / <a href="tel:112">112</a>
          </div>
          <div className="emergency-desc">{content.policeDesc}</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">{content.womenTitle}</div>
          <div className="emergency-number">
            <a href="tel:1091">1091</a>
          </div>
          <div className="emergency-desc">{content.womenDesc}</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">{content.domesticTitle}</div>
          <div className="emergency-number">
            <a href="tel:181">181</a>
          </div>
          <div className="emergency-desc">{content.domesticDesc}</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">{content.childTitle}</div>
          <div className="emergency-number">
            <a href="tel:1098">1098</a>
          </div>
          <div className="emergency-desc">{content.childDesc}</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">{content.nalsaTitle}</div>
          <div className="emergency-number">
            <a href="tel:15100">15100</a>
          </div>
          <div className="emergency-desc">{content.nalsaDesc}</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">{content.consumerTitle}</div>
          <div className="emergency-number">
            <a href="tel:1915">1915</a>
          </div>
          <div className="emergency-desc">{content.consumerDesc}</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">{content.cyberTitle}</div>
          <div className="emergency-number">
            <a href="tel:1930">1930</a>
          </div>
          <div className="emergency-desc">{content.cyberDesc}</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">{content.seniorTitle}</div>
          <div className="emergency-number">
            <a href="tel:14567">14567</a>
          </div>
          <div className="emergency-desc">{content.seniorDesc}</div>
        </div>
      </div>

      <p className="emergency-disclaimer">{content.disclaimer}</p>
    </div>
  );
}

export default EmergencyTab;

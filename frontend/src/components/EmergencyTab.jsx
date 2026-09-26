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
          <div className="emergency-number">100 / 112</div>
          <div className="emergency-desc">{content.policeDesc}</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">{content.womenTitle}</div>
          <div className="emergency-number">1091</div>
          <div className="emergency-desc">{content.womenDesc}</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">{content.domesticTitle}</div>
          <div className="emergency-number">181</div>
          <div className="emergency-desc">{content.domesticDesc}</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">{content.childTitle}</div>
          <div className="emergency-number">1098</div>
          <div className="emergency-desc">{content.childDesc}</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">{content.nalsaTitle}</div>
          <div className="emergency-number">15100</div>
          <div className="emergency-desc">{content.nalsaDesc}</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">{content.consumerTitle}</div>
          <div className="emergency-number">1915</div>
          <div className="emergency-desc">{content.consumerDesc}</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">{content.cyberTitle}</div>
          <div className="emergency-number">1930</div>
          <div className="emergency-desc">{content.cyberDesc}</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">{content.seniorTitle}</div>
          <div className="emergency-number">14567</div>
          <div className="emergency-desc">{content.seniorDesc}</div>
        </div>
      </div>

      <p className="emergency-disclaimer">{content.disclaimer}</p>
    </div>
  );
}

export default EmergencyTab;

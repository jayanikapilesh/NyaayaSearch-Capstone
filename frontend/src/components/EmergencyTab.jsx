function EmergencyTab() {
  return (
    <div className="drafter-section">
      <h2>Emergency and Legal Aid Resources</h2>
      <p className="drafter-intro">If you need urgent help, contact these resources directly.</p>

      <div className="emergency-list">
        <div className="emergency-item">
          <div className="emergency-title">Police Emergency</div>
          <div className="emergency-number">100 / 112</div>
          <div className="emergency-desc">National emergency helpline for police assistance.</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">Women Helpline</div>
          <div className="emergency-number">1091</div>
          <div className="emergency-desc">National helpline for women in distress.</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">Domestic Violence Helpline</div>
          <div className="emergency-number">181</div>
          <div className="emergency-desc">National helpline for domestic violence support.</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">Child Helpline</div>
          <div className="emergency-number">1098</div>
          <div className="emergency-desc">National helpline for children in need of help.</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">National Legal Services Authority (NALSA)</div>
          <div className="emergency-number">15100</div>
          <div className="emergency-desc">Free legal aid and services for eligible citizens.</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">Consumer Helpline</div>
          <div className="emergency-number">1915</div>
          <div className="emergency-desc">National Consumer Helpline for consumer grievances.</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">Cyber Crime Helpline</div>
          <div className="emergency-number">1930</div>
          <div className="emergency-desc">National helpline to report cyber crimes and online fraud.</div>
        </div>
        <div className="emergency-item">
          <div className="emergency-title">Senior Citizen Helpline</div>
          <div className="emergency-number">14567</div>
          <div className="emergency-desc">National helpline for elderly citizens needing assistance.</div>
        </div>
      </div>

      <p className="emergency-disclaimer">These are general national helpline numbers. In an emergency, always contact local police or emergency services directly.</p>
    </div>
  );
}

export default EmergencyTab;

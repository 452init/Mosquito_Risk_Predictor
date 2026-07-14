import "./RiskDisplay.css";

function RiskDisplay({ risk }) {
  if (!risk) return null;

  const { score, max_score, category, reasons, advice } = risk;
  const riskClass = `risk-${category.toLowerCase()}`;

  const reasonIcons = ["🌡️", "💧", "🌧️"];

  return (
    <div className="risk-display" id="risk-display">
      {/* Risk Gauge */}
      <div className={`risk-gauge ${riskClass}`}>
        <span className="risk-gauge-label">Mosquito Risk Score</span>

        <div className="risk-gauge-score">
          <div className={`risk-gauge-circle ${riskClass}`}>
            {score}
          </div>
          <span className="risk-gauge-max">/ {max_score}</span>
        </div>

        <span className={`risk-badge ${riskClass}`}>
          <span className="risk-badge-dot"></span>
          {category} RISK
        </span>
      </div>

      {/* Reasons */}
      <div className="risk-reasons">
        <h4 className="risk-reasons-title">
          <span aria-hidden="true">📋</span> Risk Factors
        </h4>
        {reasons && reasons.length > 0 ? (
          <ul className="risk-reasons-list">
            {reasons.map((reason, i) => (
              <li className="risk-reason-item" key={i}>
                <span className="risk-reason-icon" aria-hidden="true">
                  {reasonIcons[i] || "⚠️"}
                </span>
                {reason}
              </li>
            ))}
          </ul>
        ) : (
          <p className="risk-no-reasons">
            No significant risk factors detected.
          </p>
        )}
      </div>

      {/* Advice */}
      <div className={`risk-advice ${riskClass}`}>
        <div className="risk-advice-header">
          <span aria-hidden="true">💡</span>
          <h4 className="risk-advice-title">Recommendation</h4>
        </div>
        <p className="risk-advice-text">{advice}</p>
      </div>
    </div>
  );
}

export default RiskDisplay;

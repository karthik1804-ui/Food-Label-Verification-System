import React from "react";

/**
 * SafetyIndicatorCard — v2.0
 *
 * Displays the rule-based food safety indicator score.
 *
 * v2.0 change: Renamed internal labels from "XAI Safety Score" to
 * "Rule-Based Safety Indicator". Added visible disclaimer. Scoring
 * methodology note shown directly on the card.
 */
function SafetyScoreCard({ safetyScoring, product }) {
  // Support both v1 (safety_scoring) and v2 (safety_indicator) field names
  const scoring = safetyScoring;
  if (!scoring) return null;

  const { final_score, grade, base_baseline_score, score_deductions, scoring_disclaimer } = scoring;

  const totalDeductions = (score_deductions || []).reduce(
    (acc, cur) => acc + (cur.points_deducted || 0),
    0
  );

  const getGradeTheme = (g) => {
    switch (g) {
      case "A": return {
        color: "#10b981", bg: "rgba(16,185,129,0.15)",
        label: "No Major Regulatory Concerns Detected"
      };
      case "B": return {
        color: "#3b82f6", bg: "rgba(59,130,246,0.15)",
        label: "Minor Regulatory Concerns"
      };
      case "C": return {
        color: "#f59e0b", bg: "rgba(245,158,11,0.15)",
        label: "Moderate Concerns — Review Additives"
      };
      case "D": return {
        color: "#f97316", bg: "rgba(249,115,22,0.15)",
        label: "High Concern — Multiple Flagged Additives"
      };
      default: return {
        color: "#ef4444", bg: "rgba(239,68,68,0.15)",
        label: "Severe Concerns — Check Regulatory Status"
      };
    }
  };

  const theme = getGradeTheme(grade);

  return (
    <div className="card glass safety-score-card">
      {/* Product info bar */}
      <div className="product-info-bar">
        <div>
          <span className="product-category">{product?.category || "Food Product"}</span>
          <h2 className="product-title">{product?.name || "Scanned Food Item"}</h2>
          <span className="product-brand">
            {product?.brand ? `By ${product.brand}` : ""}
            {product?.ean ? ` • EAN: ${product.ean}` : ""}
            {product?.valid_ean13 === false && (
              <span className="badge-invalid" style={{ marginLeft: 8 }}>
                ⚠ Invalid EAN
              </span>
            )}
          </span>
        </div>
        <div
          className="grade-badge"
          style={{
            backgroundColor: theme.bg,
            color: theme.color,
            borderColor: theme.color
          }}
        >
          <span className="grade-letter">Grade {grade}</span>
          <span className="grade-sub">{theme.label}</span>
        </div>
      </div>

      {/* Score gauge */}
      <div className="score-main-row">
        <div className="gauge-container">
          <svg className="circular-chart" viewBox="0 0 36 36">
            <path
              className="circle-bg"
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            />
            <path
              className="circle"
              strokeDasharray={`${final_score}, 100`}
              style={{ stroke: theme.color }}
              d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
            />
            <text x="18" y="20.35" className="gauge-score" fill="#fff">
              {final_score}
            </text>
            <text x="18" y="27" className="gauge-label" fill="#94a3b8">
              / 100
            </text>
          </svg>
        </div>

        <div className="score-breakdown-panel">
          {/* Methodology label — v2.0 */}
          <div className="formula-pill method-label">
            <span className="method-tag">📐 Rule-Based Indicator</span>
            <code>
              Score = Base ({base_baseline_score}) + Σ(Deductions:{" "}
              {totalDeductions.toFixed(1)}) = {final_score}
            </code>
          </div>

          <div className="stats-mini-grid">
            <div className="stat-mini">
              <span className="stat-label">Baseline Score</span>
              <span className="stat-val">{base_baseline_score}</span>
            </div>
            <div className="stat-mini">
              <span className="stat-label">Total Deductions</span>
              <span className="stat-val penalty">{totalDeductions.toFixed(1)} pts</span>
            </div>
            <div className="stat-mini">
              <span className="stat-label">Indicator Score</span>
              <span className="stat-val" style={{ color: theme.color }}>
                {final_score}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Disclaimer banner — v2.0 */}
      <div className="scoring-disclaimer-banner">
        <span>⚠️</span>
        <small>
          {scoring_disclaimer ||
            "Rule-based indicator. Not a medical or scientific health risk assessment. " +
            "Lower scores indicate more additives or nutrients with regulatory concerns " +
            "at high consumption levels — not a guarantee of harm."}
        </small>
      </div>
    </div>
  );
}

export default SafetyScoreCard;

import React, { useState } from "react";

/**
 * RuleAttributionChart — v2.0
 *
 * Displays rule-based score deductions per additive and nutrient.
 *
 * v2.0 change: Renamed from ShapAttributionChart to RuleAttributionChart.
 * The term "SHAP" has been removed. These are transparent rule-based
 * deductions, not Shapley values from a trained ML model.
 */
function RuleAttributionChart({ deductions = [] }) {
  const [filter, setFilter] = useState("all");

  const filteredDeductions = deductions.filter((d) => {
    if (filter === "additive") return d.type === "additive";
    if (filter === "nutrient") return d.type === "nutrient";
    return true;
  });

  const maxAbsPoints = deductions.reduce(
    (max, d) => Math.max(max, Math.abs(d.points_deducted || 0)),
    1
  );

  return (
    <div className="card glass shap-card">
      <div className="card-header-between">
        <div>
          <h2>📊 Rule-Based Score Deductions</h2>
          <p className="card-sub">
            Transparent point deductions per additive and nutrient, derived from
            regulatory concern classifications (EFSA, FSSAI, WHO thresholds).
          </p>
        </div>
        <div className="filter-pill-group">
          <button
            className={`filter-pill ${filter === "all" ? "active" : ""}`}
            onClick={() => setFilter("all")}
          >
            All ({deductions.length})
          </button>
          <button
            className={`filter-pill ${filter === "additive" ? "active" : ""}`}
            onClick={() => setFilter("additive")}
          >
            Additives
          </button>
          <button
            className={`filter-pill ${filter === "nutrient" ? "active" : ""}`}
            onClick={() => setFilter("nutrient")}
          >
            Nutrients
          </button>
        </div>
      </div>

      {deductions.length === 0 ? (
        <div className="empty-notice">
          <span>🛡️</span>
          <p>No rule deductions triggered. No high-concern additives or excess nutrients detected.</p>
        </div>
      ) : (
        <div className="deductions-list">
          {filteredDeductions.map((item, index) => {
            const points = item.points_deducted || 0;
            const barWidth = Math.min(
              100,
              Math.round((Math.abs(points) / maxAbsPoints) * 100)
            );
            return (
              <div key={index} className="deduction-row">
                <div className="deduction-meta">
                  <div className="feature-name-group">
                    <span className={`type-badge badge-${item.type}`}>
                      {item.type === "additive" ? "🧪 Additive" : "🧂 Nutrient"}
                    </span>
                    <strong className="feature-label">{item.feature}</strong>
                  </div>
                  <span className="deduction-score-pill">
                    {points > 0 ? `+${points}` : points} pts
                  </span>
                </div>

                <div className="deduction-bar-track">
                  <div
                    className={`deduction-bar-fill fill-${item.type}`}
                    style={{ width: `${barWidth}%` }}
                  />
                </div>

                {/* Show rationale if available */}
                {item.rationale && (
                  <p className="deduction-rationale">
                    📌 {item.rationale}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}

      <div className="shap-footer-note">
        <span>ℹ️</span>
        <small>
          <strong>Methodology note:</strong> These are rule-based deductions derived from
          regulatory concern classifications, not Shapley values from a trained ML model.
          They indicate regulatory concern levels — not absolute health risk quantities.
        </small>
      </div>
    </div>
  );
}

export default RuleAttributionChart;

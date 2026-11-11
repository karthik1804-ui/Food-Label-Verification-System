import React, { useState } from "react";

function CounterfactualCard({ counterfactual, currentScore }) {
  const [simulated, setSimulated] = useState(false);

  if (!counterfactual) return null;

  const { target_score, recommended_action, potential_score_gain } = counterfactual;

  const isEligible = currentScore < 75;

  return (
    <div className={`card glass counterfactual-card ${simulated ? "simulated-active" : ""}`}>
      <div className="card-header">
        <span className="card-icon">⚡</span>
        <div>
          <div className="cf-title-row">
            <h2>Actionable Counterfactual Engine</h2>
            <span className="research-gap-tag">Research Gap G2</span>
          </div>
          <p className="card-sub">
            Algorithmic simulation demonstrating actionable intervention pathways to optimize product food safety.
          </p>
        </div>
      </div>

      <div className="counterfactual-body">
        <div className="action-box">
          <span className="action-tag">Recommended Reformulation:</span>
          <p className="action-text">{recommended_action}</p>
        </div>

        <div className="metrics-comparison">
          <div className="metric-col">
            <span className="metric-label">Current Score</span>
            <span className="metric-val current">{currentScore}</span>
          </div>

          <div className="metric-arrow">➔</div>

          <div className="metric-col">
            <span className="metric-label">Potential Gain</span>
            <span className="metric-val gain">{potential_score_gain}</span>
          </div>

          <div className="metric-arrow">➔</div>

          <div className="metric-col">
            <span className="metric-label">Target Score</span>
            <span className="metric-val target">{target_score}</span>
          </div>
        </div>

        {isEligible && (
          <div className="simulation-control">
            <button
              className={`btn ${simulated ? "btn-secondary" : "btn-action"}`}
              onClick={() => setSimulated(!simulated)}
            >
              {simulated ? "↩ Reset to Original Formulation" : "🧪 Simulate Counterfactual Intervention"}
            </button>
            {simulated && (
              <div className="simulated-feedback">
                <span>🎉</span>
                <p>
                  Intervention applied! Safety score elevated to <strong>{target_score}</strong> (Grade A). Consumer risk reduced significantly.
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export default CounterfactualCard;

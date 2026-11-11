import React from "react";

function AuditStatusBadge({ systemAudit }) {
  if (!systemAudit) return null;

  const { parser_confidence, flagged_for_human_review } = systemAudit;
  const confidencePercent = Math.round((parser_confidence || 0) * 100);

  return (
    <div className="card glass audit-card">
      <div className="audit-header">
        <div className="audit-title-group">
          <span className="card-icon">🔬</span>
          <div>
            <div className="audit-title-row">
              <h3>Human-in-the-Loop Audit Protocol</h3>
              <span className="research-gap-tag">Research Gap G3</span>
            </div>
            <p className="card-sub">
              Active learning fallback mechanism for unclassified additives and low-confidence predictions.
            </p>
          </div>
        </div>

        <div className="confidence-meter-box">
          <span className="confidence-title">Parser Confidence</span>
          <div className="confidence-badge">
            <span className="confidence-number">{confidencePercent}%</span>
            <div className="confidence-mini-bar">
              <div
                className="confidence-fill"
                style={{
                  width: `${confidencePercent}%`,
                  backgroundColor: confidencePercent >= 85 ? "#10b981" : "#f59e0b"
                }}
              />
            </div>
          </div>
        </div>
      </div>

      <div className="audit-status-row">
        {flagged_for_human_review ? (
          <div className="audit-banner banner-flagged">
            <span className="status-icon">⚠️</span>
            <div>
              <strong>Flagged for Human Expert Review</strong>
              <p>
                Unmapped chemical token or low extraction confidence detected. Record logged to active learning audit registry for taxonomy expansion.
              </p>
            </div>
          </div>
        ) : (
          <div className="audit-banner banner-verified">
            <span className="status-icon">🛡️</span>
            <div>
              <strong>Automated Taxonomy Verification Passed</strong>
              <p>
                All additive tokens cleanly mapped against verified INS/E-number taxonomy. High confidence attribution confirmed.
              </p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default AuditStatusBadge;

import React, { useState } from "react";
import Icon from "./Icons";

export default function AnalysisResultsView({
  analysisResult,
  onScanAnother,
  onOpenPreferences,
  dietaryProfile
}) {
  const [showRawText, setShowRawText] = useState(false);
  const [showTechnicalDetails, setShowTechnicalDetails] = useState(false);
  const [showCounterfactuals, setShowCounterfactuals] = useState(false);

  if (!analysisResult) return null;

  const product = analysisResult.product || {};
  const personalEvaluation = analysisResult.personal_evaluation || {};
  const safetyIndicator = analysisResult.safety_indicator || analysisResult.safety_scoring || {};
  const systemAudit = analysisResult.system_audit || {};
  const parsedAdditives = analysisResult.parsed_additives || [];
  const counterfactual = analysisResult.counterfactual_explanation || {};

  const {
    personal_score = safetyIndicator.final_score || 100,
    personal_verdict = "Compatible",
    allergen_alerts = [],
    preference_conflicts = [],
    caution_items = [],
    preset_name = dietaryProfile?.preset_name || "custom",
    is_provisional = false,
    extraction_warning = "",
    recommendation = ""
  } = personalEvaluation;

  const hasAllergens = allergen_alerts && allergen_alerts.length > 0;
  const hasConflicts = preference_conflicts && preference_conflicts.length > 0;
  const hasCautions = caution_items && caution_items.length > 0;

  // Confidence indicators from system audit
  const conf = systemAudit.confidence || {};
  const ocrConfidence = conf.ocr_confidence !== undefined ? Math.round(conf.ocr_confidence * 100) : null;
  const additiveConfidence = conf.additive_match_confidence !== undefined ? Math.round(conf.additive_match_confidence * 100) : null;
  const barcodeStatus = conf.barcode_decode_status || "not_provided";

  const getScoreTheme = (score, hasAllergen) => {
    if (hasAllergen) return { color: "#dc2626", bg: "#fef2f2", border: "#fecaca", status: "Allergen Warning" };
    if (score >= 90) return { color: "#059669", bg: "#ecfdf5", border: "#a7f3d0", status: "High Compatibility" };
    if (score >= 70) return { color: "#d97706", bg: "#fffbeb", border: "#fde68a", status: "Moderate Caution" };
    return { color: "#dc2626", bg: "#fef2f2", border: "#fecaca", status: "Preference Conflicts" };
  };

  const scoreTheme = getScoreTheme(personal_score, hasAllergens);

  const isBarcodeProduct = product.ean && product.ean !== "N/A" && product.name !== "Uploaded Packaging Scan" && product.name !== "Live Camera Capture" && product.name !== "Manual Ingredient Label";

  return (
    <div className="analysis-results-container">
      {/* Top Banner Navigation & Actions */}
      <div className="results-top-action-bar">
        <button
          type="button"
          className="btn btn-outline"
          onClick={onScanAnother}
        >
          <Icon name="arrowLeft" size={16} />
          <span>Scan Another Product</span>
        </button>

        <div className="results-top-right-actions">
          {onOpenPreferences && (
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={onOpenPreferences}
            >
              <Icon name="sliders" size={16} />
              <span>Adjust Preferences</span>
            </button>
          )}
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={() => window.print()}
          >
            <Icon name="download" size={16} />
            <span>Save / Print Report</span>
          </button>
        </div>
      </div>

      {/* SECTION A: PRODUCT INFORMATION CARD */}
      <div className="card glass product-overview-card">
        <div className="product-overview-grid">
          <div className="product-details-left">
            <div className="product-source-badge">
              {isBarcodeProduct ? (
                <span className="source-pill barcode-source">
                  <Icon name="barcode" size={14} />
                  <span>EAN Barcode Catalog Record</span>
                </span>
              ) : (
                <span className="source-pill physical-source">
                  <Icon name="camera" size={14} />
                  <span>Physical Packaging Label OCR</span>
                </span>
              )}
            </div>

            <h1 className="product-name-heading">
              {product.name || "Scanned Food Formulation"}
            </h1>

            <div className="product-meta-row">
              {product.brand && (
                <span className="product-brand-tag">
                  Brand: <strong>{product.brand}</strong>
                </span>
              )}
              {product.category && (
                <span className="product-category-tag">
                  Category: <strong>{product.category}</strong>
                </span>
              )}
              {product.ean && product.ean !== "N/A" && (
                <span className="product-barcode-tag">
                  EAN-13: <code>{product.ean}</code>
                </span>
              )}
            </div>
          </div>

          <div className="product-verdict-right">
            <div
              className="verdict-capsule"
              style={{
                backgroundColor: scoreTheme.bg,
                borderColor: scoreTheme.border,
                color: scoreTheme.color
              }}
            >
              <span className="verdict-label">Dietary Verdict</span>
              <span className="verdict-status-text">{personal_verdict}</span>
            </div>
          </div>
        </div>
      </div>

      {/* SECTION B: PERSONALISED SUITABILITY SCORE CARD */}
      <div className="card glass score-showcase-card">
        <div className="score-showcase-grid">
          {/* Circular Score Visualizer */}
          <div className="score-visualizer-col">
            <div className="circular-meter-wrapper">
              <svg className="circular-meter-svg" viewBox="0 0 36 36">
                <path
                  className="meter-circle-bg"
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path
                  className="meter-circle-fill"
                  strokeDasharray={`${hasAllergens ? 100 : personal_score}, 100`}
                  style={{ stroke: scoreTheme.color }}
                  d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                />
              </svg>
              <div className="meter-center-content">
                <span className="meter-score-num" style={{ color: scoreTheme.color }}>
                  {hasAllergens ? "!" : personal_score}
                </span>
                <span className="meter-score-max">/ 100</span>
              </div>
            </div>
          </div>

          {/* Explanation & Context */}
          <div className="score-explanation-col">
            <div className="score-title-group">
              <span className="score-kicker">Personalised Dietary Preference Score</span>
              <h2>{scoreTheme.status}</h2>
              <div className="active-profile-pill">
                <Icon name="leaf" size={14} color="#059669" />
                <span>Evaluated for: <strong>{preset_name.replace("_", " ").toUpperCase()}</strong></span>
              </div>
            </div>

            <p className="score-summary-text">
              {hasAllergens
                ? "This product contains one or more ingredients matching your configured allergen sensitivities. Please do not consume if you have severe intolerances."
                : is_provisional
                ? "This score is provisional due to partial OCR text confidence. Inspect the physical packaging label carefully."
                : personal_score >= 90
                ? "This product is compliant with your active dietary avoidances. No major preference conflicts detected."
                : personal_score >= 70
                ? "This product is mostly suitable, but contains minor additives or ingredients you prefer to limit."
                : "This product conflicts with one or more of your active dietary preferences. Review flagged additives below."}
            </p>

            <div className="score-disclaimer-callout">
              <Icon name="info" size={16} />
              <span>
                <strong>Informational Verification:</strong> This is a personalised preference calculation, not a clinical health diagnosis or medical safety guarantee.
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* SECTION C: ALLERGEN ALERTS (Prominent Warning Styling) */}
      {hasAllergens && (
        <div className="card allergen-alert-card">
          <div className="allergen-alert-header">
            <div className="allergen-alert-icon">
              <Icon name="alertTriangle" size={24} color="#dc2626" />
            </div>
            <div>
              <h3>Allergen Warning Detected</h3>
              <p>The following configured allergen triggers were identified in the ingredient list:</p>
            </div>
          </div>

          <div className="allergen-triggers-list">
            {allergen_alerts.map((alert, idx) => (
              <div key={idx} className="allergen-trigger-item">
                <div className="allergen-badge-name">
                  🚨 <strong>{alert.allergen?.toUpperCase()}</strong>
                </div>
                <div className="allergen-details">
                  <span>Matched keyword: "<strong>{alert.matched_term}</strong>"</span>
                  {alert.action_required && <span className="action-tag">{alert.action_required}</span>}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {!hasAllergens && dietaryProfile?.custom_allergens && dietaryProfile.custom_allergens.length > 0 && (
        <div className="card allergen-reassurance-card">
          <div className="reassurance-left">
            <Icon name="shieldCheck" size={20} color="#059669" />
            <div>
              <strong>No Configured Allergens Detected</strong>
              <p>
                None of your {dietaryProfile.custom_allergens.length} configured allergens ({dietaryProfile.custom_allergens.join(", ")}) were found in the scanned text.
              </p>
            </div>
          </div>
          <span className="reassurance-note">Always check packaging for precautionary statements</span>
        </div>
      )}

      {/* PROVISIONAL OCR SAFETY GATE WARNING (When OCR Confidence is low) */}
      {is_provisional && (
        <div className="card ocr-provisional-warning-card">
          <div className="provisional-header">
            <Icon name="alertCircle" size={22} color="#d97706" />
            <div>
              <h4>Provisional Analysis Notice (OCR Uncertainty)</h4>
              <p>
                {extraction_warning || "OCR clarity is below the standard confidence threshold. Some additive codes or text may not have been fully captured."}
              </p>
            </div>
          </div>
          <div className="provisional-recommendations">
            <div className="rec-title">Recommended Next Steps:</div>
            <ul>
              <li>💡 {recommendation || "Ensure bright, even lighting and retake photo closer to the ingredient text."}</li>
              <li>📝 Alternatively, switch to manual ingredient text input to paste exact label text.</li>
            </ul>
          </div>
        </div>
      )}

      {/* PREFERENCE CONFLICTS & CAUTIONS SUMMARY */}
      {(hasConflicts || hasCautions) && (
        <div className="card glass conflicts-breakdown-card">
          <div className="conflicts-header">
            <Icon name="sliders" size={20} color="#d97706" />
            <div>
              <h3>Specific Preference Conflicts & Cautions</h3>
              <p>Items in this formulation that triggered score deductions according to your profile:</p>
            </div>
          </div>

          <div className="conflicts-grid">
            {preference_conflicts.map((confItem, i) => (
              <div key={i} className="conflict-card conflict-strict">
                <div className="conflict-card-top">
                  <span className="conflict-name">{confItem.name || confItem.code}</span>
                  <span className="conflict-points">-{confItem.deduction} pts</span>
                </div>
                <div className="conflict-code-badge">INS {confItem.code}</div>
                <p className="conflict-reason">{confItem.reason}</p>
              </div>
            ))}

            {caution_items.map((cautItem, i) => (
              <div key={i} className="conflict-card conflict-caution">
                <div className="conflict-card-top">
                  <span className="conflict-name">{cautItem.name || cautItem.code}</span>
                  <span className="conflict-points caution">-{cautItem.deduction} pts</span>
                </div>
                <div className="conflict-code-badge caution">INS {cautItem.code}</div>
                <p className="conflict-reason">{cautItem.reason}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SECTION D: DETECTED ADDITIVES TABLE & CARDS */}
      <div className="card glass detected-additives-card">
        <div className="additives-card-header">
          <div className="additives-title-left">
            <div className="additives-icon-circle">
              <Icon name="sparkles" size={20} color="#059669" />
            </div>
            <div>
              <h3>Detected Food Additives & INS Classification</h3>
              <p>Mapped from verified chemical taxonomy against Codex Alimentarius and FSSAI schedules.</p>
            </div>
          </div>

          <div className="additives-count-badge">
            <span>{parsedAdditives.length} additive{parsedAdditives.length === 1 ? "" : "s"} identified</span>
          </div>
        </div>

        {parsedAdditives.length === 0 ? (
          <div className="empty-additives-state">
            <span className="empty-emoji">🌿</span>
            <h4>Zero Food Additives Detected</h4>
            <p>No synthetic food additives, artificial colours, or chemical preservatives were detected in this formulation.</p>
          </div>
        ) : (
          <div className="additives-table-wrapper">
            <table className="consumer-additives-table">
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Additive Name</th>
                  <th>Functional Category</th>
                  <th>Hazard Assessment</th>
                  <th>Regulatory Status</th>
                </tr>
              </thead>
              <tbody>
                {parsedAdditives.map((item, idx) => {
                  const hazard = (item.hazard_level || "low").toLowerCase();
                  return (
                    <tr key={idx}>
                      <td>
                        <span className="ins-pill">INS {item.code}</span>
                      </td>
                      <td>
                        <div className="additive-name-cell">
                          <strong>{item.name}</strong>
                          {item.alternative_names && item.alternative_names.length > 0 && (
                            <span className="alt-names">Synonyms: {item.alternative_names.slice(0, 2).join(", ")}</span>
                          )}
                          {item.is_color && (
                            <span className={`color-tag ${item.color_origin === "synthetic" ? "synthetic" : "natural"}`}>
                              🎨 {item.color_origin} color
                            </span>
                          )}
                        </div>
                      </td>
                      <td>
                        <div className="functional-classes-row">
                          {(item.functional_categories || [item.class || "Food Additive"]).map((fc, i) => (
                            <span key={i} className="fc-chip">{fc}</span>
                          ))}
                        </div>
                      </td>
                      <td>
                        <span className={`hazard-badge hazard-${hazard}`}>
                          {item.hazard_level || "Low Concern"}
                        </span>
                      </td>
                      <td>
                        <span className={`regulatory-badge ${item.regulatory?.verified ? "verified" : "unverified"}`}>
                          {item.regulatory?.fssai_status ? item.regulatory.fssai_status.substring(0, 24) : "Approved"}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* SECTION E: VERIFICATION & MULTIMODAL CONFIDENCE GAUGES */}
      <div className="card glass confidence-section-card">
        <div className="confidence-section-header">
          <div className="confidence-title-left">
            <Icon name="shieldCheck" size={20} color="#2563eb" />
            <div>
              <h3>Analysis Quality & Verification Confidence</h3>
              <p>Transparent measurement of optical character clarity, catalog lookup, and taxonomy coverage.</p>
            </div>
          </div>
        </div>

        <div className="confidence-metrics-grid">
          {/* Metric 1: OCR Text Confidence */}
          <div className="confidence-metric-box">
            <div className="metric-box-top">
              <span className="metric-box-label">OCR Text Clarity</span>
              <span className="metric-box-val" style={{ color: ocrConfidence >= 75 ? "#059669" : ocrConfidence >= 40 ? "#d97706" : "#dc2626" }}>
                {ocrConfidence !== null ? `${ocrConfidence}%` : "100% (Direct)"}
              </span>
            </div>
            <div className="metric-bar-track">
              <div
                className="metric-bar-fill"
                style={{
                  width: `${ocrConfidence !== null ? ocrConfidence : 100}%`,
                  backgroundColor: ocrConfidence >= 75 ? "#059669" : ocrConfidence >= 40 ? "#d97706" : "#dc2626"
                }}
              />
            </div>
            <span className="metric-box-sub">
              {ocrConfidence >= 75
                ? "Sharp, legible text extraction"
                : ocrConfidence >= 40
                ? "Moderate clarity with minor noise"
                : "Low optical confidence (Provisional)"}
            </span>
          </div>

          {/* Metric 2: Additive Matching */}
          <div className="confidence-metric-box">
            <div className="metric-box-top">
              <span className="metric-box-label">Taxonomy Match</span>
              <span className="metric-box-val" style={{ color: "#059669" }}>
                {additiveConfidence !== null ? `${additiveConfidence}%` : "100%"}
              </span>
            </div>
            <div className="metric-bar-track">
              <div
                className="metric-bar-fill"
                style={{
                  width: `${additiveConfidence !== null ? additiveConfidence : 100}%`,
                  backgroundColor: "#059669"
                }}
              />
            </div>
            <span className="metric-box-sub">Formulation tokens mapped to INS records</span>
          </div>

          {/* Metric 3: Barcode Status */}
          <div className="confidence-metric-box">
            <div className="metric-box-top">
              <span className="metric-box-label">Barcode Status</span>
              <span className="metric-box-badge">
                {barcodeStatus === "valid_ean13" ? "✓ Valid EAN" : barcodeStatus === "not_provided" ? "Optional / Omitted" : "Lookup Pending"}
              </span>
            </div>
            <div className="metric-bar-track">
              <div
                className="metric-bar-fill"
                style={{
                  width: barcodeStatus === "valid_ean13" ? "100%" : "30%",
                  backgroundColor: barcodeStatus === "valid_ean13" ? "#059669" : "#94a3b8"
                }}
              />
            </div>
            <span className="metric-box-sub">
              {barcodeStatus === "valid_ean13"
                ? "Verified against Open Food Facts catalog"
                : "Analyzed strictly via physical packaging label"}
            </span>
          </div>

          {/* Metric 4: Safety Gate Indicator */}
          <div className="confidence-metric-box">
            <div className="metric-box-top">
              <span className="metric-box-label">OCR Safety Gate</span>
              <span className="metric-box-badge" style={{ color: is_provisional ? "#d97706" : "#059669" }}>
                {is_provisional ? "⚠️ Provisional" : "✓ Decision Verified"}
              </span>
            </div>
            <div className="metric-bar-track">
              <div
                className="metric-bar-fill"
                style={{
                  width: "100%",
                  backgroundColor: is_provisional ? "#d97706" : "#059669"
                }}
              />
            </div>
            <span className="metric-box-sub">
              {is_provisional
                ? "Uncertainty warning active (< 40% confidence)"
                : "Text satisfies quality threshold for dietary evaluation"}
            </span>
          </div>
        </div>
      </div>

      {/* SECTION F: EXPANDABLE DETAILED INFORMATION */}
      <div className="detailed-expandables-group">
        {/* Accordion 1: Raw Extracted Ingredient Text */}
        <div className="accordion-card card glass">
          <button
            type="button"
            className="accordion-trigger-btn"
            onClick={() => setShowRawText(!showRawText)}
          >
            <div className="accordion-trigger-left">
              <Icon name="fileText" size={18} />
              <span>Inspect Raw Extracted Ingredient Text</span>
            </div>
            <Icon name={showRawText ? "chevronUp" : "chevronDown"} size={18} />
          </button>

          {showRawText && (
            <div className="accordion-body">
              <p className="accordion-body-help">
                Below is the verbatim text extracted from the packaging image by the OCR optical character recognition engine:
              </p>
              <pre className="raw-text-block">
                {analysisResult.extracted_text || product.raw_ingredient_text || "No raw text available."}
              </pre>
            </div>
          )}
        </div>

        {/* Accordion 2: Rule-Based Deductions & Scoring Formula */}
        <div className="accordion-card card glass">
          <button
            type="button"
            className="accordion-trigger-btn"
            onClick={() => setShowTechnicalDetails(!showTechnicalDetails)}
          >
            <div className="accordion-trigger-left">
              <Icon name="sliders" size={18} />
              <span>Technical Audit & Rule Deductions Breakdown</span>
            </div>
            <Icon name={showTechnicalDetails ? "chevronUp" : "chevronDown"} size={18} />
          </button>

          {showTechnicalDetails && (
            <div className="accordion-body">
              <p className="accordion-body-help">
                Calculated deterministically using codified dietary evaluation rules:
              </p>

              <div className="deductions-list">
                {safetyIndicator.score_deductions && safetyIndicator.score_deductions.map((ded, i) => (
                  <div key={i} className="deduction-row">
                    <span className="deduction-feature">{ded.feature || ded.reason}</span>
                    <span className="deduction-pts">-{ded.points_deducted} pts</span>
                  </div>
                ))}
              </div>

              {analysisResult.ambiguous_detections && analysisResult.ambiguous_detections.length > 0 && (
                <div className="ambiguous-notice-box">
                  <strong>⚠️ Ambiguous Formulations Flagged:</strong>
                  <ul>
                    {analysisResult.ambiguous_detections.map((item, i) => (
                      <li key={i}>{item.matched_term || item.code} ({item.warning || "Unspecified additive class"})</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Accordion 3: Counterfactual Formulation Guidance */}
        {counterfactual && counterfactual.suggested_substitutions && counterfactual.suggested_substitutions.length > 0 && (
          <div className="accordion-card card glass">
            <button
              type="button"
              className="accordion-trigger-btn"
              onClick={() => setShowCounterfactuals(!showCounterfactuals)}
            >
              <div className="accordion-trigger-left">
                <Icon name="sparkles" size={18} color="#059669" />
                <span>Formulation Improvement Suggestions (Counterfactual Optimization)</span>
              </div>
              <Icon name={showCounterfactuals ? "chevronUp" : "chevronDown"} size={18} />
            </button>

            {showCounterfactuals && (
              <div className="accordion-body">
                <p className="accordion-body-help">
                  How formulation score can increase to {counterfactual.target_score || 95}/100 by substituting higher-risk ingredients:
                </p>
                <div className="substitutions-grid">
                  {counterfactual.suggested_substitutions.map((sub, i) => (
                    <div key={i} className="substitution-card">
                      <div className="sub-header">
                        <span className="sub-remove">Remove: {sub.original_additive}</span>
                        <span className="sub-gain">+{sub.potential_score_gain} pts</span>
                      </div>
                      <div className="sub-replace">
                        <span>Recommended replacement:</span>
                        <strong>{sub.suggested_natural_alternative}</strong>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Footer Return Action */}
      <div className="results-bottom-actions">
        <button
          type="button"
          className="btn btn-primary btn-large"
          onClick={onScanAnother}
        >
          <Icon name="camera" size={18} />
          <span>Scan Another Food Product</span>
        </button>
      </div>
    </div>
  );
}

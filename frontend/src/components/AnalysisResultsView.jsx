import React, { useState } from "react";
import Icon from "./Icons";

export default function AnalysisResultsView({
  analysisResult,
  onScanAnother,
  onOpenPreferences,
  onBackToDashboard,
  onViewHistory,
  dietaryProfile
}) {
  const [activeTab, setActiveTab] = useState("additives"); // 'additives' | 'allergens' | 'rules' | 'raw' | 'recommendations'
  const [expandedIngredient, setExpandedIngredient] = useState(null);
  const [showTechDetails, setShowTechDetails] = useState(false);

  if (!analysisResult) return null;

  const product = analysisResult.product || {};
  const personalEvaluation = analysisResult.personal_evaluation || {};
  const safetyIndicator = analysisResult.safety_indicator || analysisResult.safety_scoring || {};
  const systemAudit = analysisResult.system_audit || {};
  const parsedAdditives = analysisResult.parsed_additives || [];
  const counterfactual = analysisResult.counterfactual_explanation || {};

  const detectedCategories = Array.from(
    new Set(
      parsedAdditives.flatMap((item) =>
        Array.isArray(item.functional_categories)
          ? item.functional_categories
          : item.class ? [item.class] : []
      )
    )
  );

  const {
    personal_score = safetyIndicator.final_score || 100,
    allergen_alerts = [],
    preference_conflicts = [],
    caution_items = [],
    is_provisional = false,
    extraction_warning = "",
    recommendation = ""
  } = personalEvaluation;

  const hasAllergens = allergen_alerts && allergen_alerts.length > 0;
  const hasConflicts = preference_conflicts && preference_conflicts.length > 0;

  // System audit confidence metrics
  const conf = systemAudit.confidence || {};
  const ocrConfidence = conf.ocr_confidence !== undefined ? Math.round(conf.ocr_confidence * 100) : null;
  const additiveConfidence = conf.additive_match_confidence !== undefined ? Math.round(conf.additive_match_confidence * 100) : null;
  const barcodeStatus = conf.barcode_decode_status || "not_provided";

  const ocrPipelineConfig = product.ocr_pipeline_config || analysisResult.ocr_pipeline_config || null;
  const preprocessingMetrics = product.preprocessing_metrics || analysisResult.preprocessing_metrics || null;

  const getScoreTheme = (score, hasAllergen) => {
    if (hasAllergen) {
      return {
        color: "#DC2626",
        bg: "#FEF2F2",
        border: "#FECACA",
        status: "Allergen Warning",
        badgeClass: "badge-danger"
      };
    }
    if (score >= 90) {
      return {
        color: "#16A34A",
        bg: "#F0FDF4",
        border: "#BBF7D0",
        status: "Highly Suitable",
        badgeClass: "badge-success"
      };
    }
    if (score >= 70) {
      return {
        color: "#F59E0B",
        bg: "#FFFBEB",
        border: "#FDE68A",
        status: "Moderate Caution",
        badgeClass: "badge-warning"
      };
    }
    return {
      color: "#DC2626",
      bg: "#FEF2F2",
      border: "#FECACA",
      status: "Preference Conflicts",
      badgeClass: "badge-danger"
    };
  };

  const scoreTheme = getScoreTheme(personal_score, hasAllergens);

  const toggleExpandIngredient = (idx) => {
    setExpandedIngredient(expandedIngredient === idx ? null : idx);
  };

  return (
    <div className="clinical-page-container">
      {/* Page Heading */}
      <div className="clinical-page-header">
        <h1 className="clinical-title">Analysis Results</h1>
        <p className="clinical-description">
          Personalised ingredient evaluation based on your dietary preferences.
        </p>
      </div>

      {/* SECTION 1: OVERALL SUITABILITY HERO CARD */}
      <div className="card clinical-hero-result-card" style={{ borderColor: scoreTheme.border }}>
        <div className="suitability-hero-grid">
          {/* Circular Score Gauge */}
          <div className="suitability-meter-col">
            <div className="meter-wrapper">
              <svg viewBox="0 0 36 36" className="circular-meter-svg">
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
                {hasAllergens ? (
                  <>
                    <span className="meter-score-num meter-score-alert" style={{ color: scoreTheme.color }}>
                      ⚠
                    </span>
                    <span className="meter-score-status-text">UNSUITABLE</span>
                  </>
                ) : (
                  <>
                    <span className="meter-score-num" style={{ color: scoreTheme.color }}>
                      {personal_score}
                    </span>
                    <span className="meter-score-max">/ 100</span>
                  </>
                )}
              </div>
            </div>
            <span className={`status-badge-hero ${scoreTheme.badgeClass}`}>
              {scoreTheme.status}
            </span>
          </div>

          {/* Product & Evaluation Context */}
          <div className="suitability-details-col">
            <div className="product-title-row">
              <h2 className="product-main-name">
                {product.name || "Scanned Formulation"}
              </h2>
              {hasAllergens && (
                <span className="hero-alert-pill">
                  {allergen_alerts.length} Allergen Trigger{allergen_alerts.length > 1 ? "s" : ""}
                </span>
              )}
            </div>

            {product.brand && (
              <span className="product-brand-line">Brand: <strong>{product.brand}</strong></span>
            )}

            {/* DIRECT DETECTED INGREDIENTS CALLOUT BANNER WHEN ALLERGENS DETECTED */}
            {hasAllergens && (
              <div className="hero-detected-triggers-banner">
                <div className="hero-detected-triggers-title">
                  <Icon name="shieldAlert" size={16} color="#DC2626" />
                  <span>Detected Allergen Matches:</span>
                </div>
                <div className="hero-detected-triggers-chips">
                  {allergen_alerts.map((alert, idx) => (
                    <span key={idx} className="hero-trigger-chip">
                      <strong className="hero-chip-allergen">{alert.allergen?.toUpperCase()}</strong>
                      <span className="hero-chip-term">("{alert.matched_term}")</span>
                    </span>
                  ))}
                </div>
              </div>
            )}

            <p className="suitability-explanation-text">
              {hasAllergens
                ? `Immediate warning: This food formulation contains ${allergen_alerts.map(a => `${a.allergen?.toUpperCase()} ("${a.matched_term}")`).join(", ")}. It conflicts directly with your active allergen profile.`
                : is_provisional
                ? "This compatibility score is provisional due to moderate OCR text clarity. Verify fine print on the physical label."
                : personal_score >= 90
                ? "This product matches your configured dietary preferences. No conflicting food additives were detected."
                : personal_score >= 70
                ? "This product is mostly compatible with your profile, but contains minor additives you prefer to limit."
                : "This product contradicts one or more active dietary preferences. Review flagged additives in the breakdown below."}
            </p>

            <div className="clinical-disclaimer-callout">
              <Icon name="info" size={15} color="#2563EB" />
              <span>
                <strong>Note:</strong> This score reflects your personal dietary preferences, not a clinical diagnosis or food-safety certification.
              </span>
            </div>

            {extraction_warning && (
              <div className="clinical-disclaimer-callout" style={{ backgroundColor: "#FEF3C7", borderColor: "#FDE68A", color: "#92400E", marginTop: "0.75rem" }}>
                <Icon name="alertTriangle" size={15} color="#D97706" />
                <span>
                  <strong>Text Extraction Note:</strong> {extraction_warning}
                </span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* SECTION 2: ANALYSIS SUMMARY METRICS GRID */}
      <div className="clinical-metrics-grid">
        <div className="metric-card">
          <div className="metric-card-top">
            <span className="metric-label">Detected Ingredients</span>
            <Icon name="activity" size={16} color="#00454A" />
          </div>
          <span className="metric-value">{parsedAdditives.length}</span>
          <span className="metric-sub">Total verified ingredients</span>
        </div>

        <div className="metric-card">
          <div className="metric-card-top">
            <span className="metric-label">Flagged Additives</span>
            <Icon name="sliders" size={16} color={hasConflicts ? "#DC2626" : "#16A34A"} />
          </div>
          <span className="metric-value" style={{ color: hasConflicts ? "#DC2626" : "#0F172A" }}>
            {preference_conflicts.length}
          </span>
          <span className="metric-sub">
            {hasConflicts ? `${preference_conflicts.length} avoidances flagged` : "Zero preference conflicts"}
          </span>
        </div>

        <div className="metric-card">
          <div className="metric-card-top">
            <span className="metric-label">Allergen Triggers</span>
            <Icon name="shieldAlert" size={16} color={hasAllergens ? "#DC2626" : "#16A34A"} />
          </div>
          <span className="metric-value" style={{ color: hasAllergens ? "#DC2626" : "#0F172A" }}>
            {allergen_alerts.length}
          </span>
          <span className="metric-sub">
            {hasAllergens ? `${allergen_alerts.length} allergen matches` : "Zero allergens detected"}
          </span>
        </div>

        <div className="metric-card">
          <div className="metric-card-top">
            <span className="metric-label">Categories Detected</span>
            <Icon name="leaf" size={16} color="#00454A" />
          </div>
          <span className="metric-value">{detectedCategories.length}</span>
          <span className="metric-sub">Functional ingredient classes</span>
        </div>
      </div>

      {/* ALLERGEN ALERT BANNER (If allergens detected) */}
      {hasAllergens && (
        <div className="card clinical-allergen-alert-card">
          <div className="alert-card-header">
            <div className="alert-icon-circle">
              <Icon name="alertTriangle" size={22} color="#DC2626" />
            </div>
            <div>
              <h3 className="alert-card-title">Allergen Warning Detected</h3>
              <p className="alert-card-sub">
                The following configured allergen triggers were identified in the ingredient list:
              </p>
            </div>
          </div>

          <div className="alert-triggers-list">
            {allergen_alerts.map((alert, idx) => (
              <div key={idx} className="alert-trigger-item">
                <span className="trigger-badge">🚨 {alert.allergen?.toUpperCase()}</span>
                <span className="trigger-detail">
                  Matched keyword in packaging: "<strong>{alert.matched_term}</strong>"
                </span>
                {alert.action_required && (
                  <span className="trigger-action-tag">{alert.action_required}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* SECTION 3: INGREDIENT LIST & ADDITIVES BREAKDOWN */}
      <div className="card clinical-section-card">
        <div className="results-tab-bar">
          <button
            type="button"
            className={`results-tab ${activeTab === "additives" ? "active" : ""}`}
            onClick={() => setActiveTab("additives")}
          >
            <Icon name="activity" size={15} />
            <span>Detected Additives ({parsedAdditives.length})</span>
          </button>

          {hasAllergens && (
            <button
              type="button"
              className={`results-tab tab-danger ${activeTab === "allergens" ? "active" : ""}`}
              onClick={() => setActiveTab("allergens")}
            >
              <Icon name="shieldAlert" size={15} />
              <span>Allergen Warnings ({allergen_alerts.length})</span>
            </button>
          )}

          <button
            type="button"
            className={`results-tab ${activeTab === "rules" ? "active" : ""}`}
            onClick={() => setActiveTab("rules")}
          >
            <Icon name="sliders" size={15} />
            <span>Rule Deductions ({safetyIndicator.score_deductions?.length || 0})</span>
          </button>

          <button
            type="button"
            className={`results-tab ${activeTab === "raw" ? "active" : ""}`}
            onClick={() => setActiveTab("raw")}
          >
            <Icon name="fileText" size={15} />
            <span>Extracted Label Text</span>
          </button>

          {counterfactual?.rules_triggered && (
            <button
              type="button"
              className={`results-tab ${activeTab === "recommendations" ? "active" : ""}`}
              onClick={() => setActiveTab("recommendations")}
            >
              <Icon name="sparkles" size={15} />
              <span>Recommendations</span>
            </button>
          )}
        </div>

        {/* TAB 1: DETECTED ADDITIVES */}
        {activeTab === "additives" && (
          <div className="tab-pane-content">
            {parsedAdditives.length === 0 ? (
              <div className="empty-subtle-box">
                <span style={{ fontSize: "1.5rem" }}>🌿</span>
                <h4 style={{ margin: "0.5rem 0 0.25rem 0" }}>Zero Food Additives Identified</h4>
                <p style={{ color: "#64748B", fontSize: "0.88rem" }}>
                  No synthetic colours, chemical preservatives, or flavour enhancers matching the Codex Alimentarius schedule were detected.
                </p>
              </div>
            ) : (
              <div className="clinical-ingredients-table-wrap">
                <table className="clinical-table">
                  <thead>
                    <tr>
                      <th>Code</th>
                      <th>Additive Name</th>
                      <th>Functional Category</th>
                      <th>Preference Status</th>
                      <th>Regulatory Assessment</th>
                    </tr>
                  </thead>
                  <tbody>
                    {parsedAdditives.map((item, idx) => {
                      const isAvoided = preference_conflicts.some((c) => c.code === item.code || c.name === item.name);
                      const isCaution = caution_items.some((c) => c.code === item.code || c.name === item.name);
                      const isExpanded = expandedIngredient === idx;

                      let statusBadge = { label: "Compatible", cls: "status-pill-success" };
                      if (isAvoided) statusBadge = { label: "Avoided Conflict", cls: "status-pill-danger" };
                      else if (isCaution) statusBadge = { label: "Caution / Limit", cls: "status-pill-warning" };

                      return (
                        <React.Fragment key={idx}>
                          <tr
                            className={`table-row-interactive ${isExpanded ? "row-expanded" : ""}`}
                            onClick={() => toggleExpandIngredient(idx)}
                          >
                            <td>
                              <span className="ins-code-pill">INS {item.code}</span>
                            </td>
                            <td>
                              <div className="additive-name-cell">
                                <strong>{item.name}</strong>
                                {item.is_color && (
                                  <span className="micro-color-pill">
                                    🎨 {item.color_origin || "synthetic"} colour
                                  </span>
                                )}
                              </div>
                            </td>
                            <td>
                              <span className="fc-chip">
                                {Array.isArray(item.functional_categories)
                                  ? item.functional_categories[0]
                                  : item.class || "Food Additive"}
                              </span>
                            </td>
                            <td>
                              <span className={`status-pill ${statusBadge.cls}`}>
                                {statusBadge.label}
                              </span>
                            </td>
                            <td>
                              <span className="regulatory-text">
                                {item.regulatory?.fssai_status ? item.regulatory.fssai_status.substring(0, 24) : "Codex Approved"}
                              </span>
                            </td>
                          </tr>

                          {isExpanded && (
                            <tr className="expanded-detail-row">
                              <td colSpan={5}>
                                <div className="expanded-detail-box">
                                  <div className="detail-item">
                                    <span className="detail-label">Codex Functional Category:</span>
                                    <span className="detail-val">
                                      {Array.isArray(item.functional_categories)
                                        ? item.functional_categories.join(", ")
                                        : item.class || "General Additive"}
                                    </span>
                                  </div>
                                  {item.alternative_names && item.alternative_names.length > 0 && (
                                    <div className="detail-item">
                                      <span className="detail-label">Recognized Synonyms:</span>
                                      <span className="detail-val">{item.alternative_names.join(", ")}</span>
                                    </div>
                                  )}
                                  <div className="detail-item">
                                    <span className="detail-label">Hazard Profile:</span>
                                    <span className="detail-val">{item.hazard_level || "Standard Food Safety Evaluation"}</span>
                                  </div>
                                  {item.description && (
                                    <div className="detail-item">
                                      <span className="detail-label">Chemical Description:</span>
                                      <span className="detail-val">{item.description}</span>
                                    </div>
                                  )}
                                </div>
                              </td>
                            </tr>
                          )}
                        </React.Fragment>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* TAB 2: ALLERGEN WARNINGS */}
        {activeTab === "allergens" && (
          <div className="tab-pane-content">
            <div className="alert-triggers-list">
              {allergen_alerts.map((alert, idx) => (
                <div key={idx} className="alert-trigger-item">
                  <span className="trigger-badge">🚨 {alert.allergen?.toUpperCase()}</span>
                  <span className="trigger-detail">
                    Matched ingredient: "<strong>{alert.matched_term}</strong>"
                  </span>
                  {alert.action_required && (
                    <span className="trigger-action-tag">{alert.action_required}</span>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}

        {/* TAB 3: RULE DEDUCTIONS & SCORING */}
        {activeTab === "rules" && (
          <div className="tab-pane-content">
            <div className="rule-deductions-list">
              {safetyIndicator.score_deductions && safetyIndicator.score_deductions.length > 0 ? (
                safetyIndicator.score_deductions.map((ded, i) => (
                  <div key={i} className="rule-deduction-item">
                    <div className="deduction-left">
                      <span className="deduction-rule-name">{ded.rule_id || "DIETARY_CONFLICT"}</span>
                      <p className="deduction-reason">{ded.reason || ded.feature}</p>
                    </div>
                    <span className="deduction-score-pts">-{ded.points_deducted} pts</span>
                  </div>
                ))
              ) : (
                <div className="empty-subtle-box">
                  <Icon name="checkCircle" size={24} color="#16A34A" />
                  <p>Zero score deductions applied. Product completely satisfies active profile rules.</p>
                </div>
              )}
            </div>
          </div>
        )}

        {/* TAB 4: EXTRACTED LABEL TEXT */}
        {activeTab === "raw" && (
          <div className="tab-pane-content">
            <p className="raw-text-explainer">
              Verbatim ingredient declaration text extracted from the packaging image by the OCR optical character recognition engine:
            </p>
            <pre className="clinical-raw-text-block">
              {analysisResult.extracted_text || product.raw_ingredient_text || "No raw text available."}
            </pre>
          </div>
        )}

        {/* TAB 5: RECOMMENDATIONS */}
        {activeTab === "recommendations" && (
          <div className="tab-pane-content">
            <div className="recommendations-container">
              {counterfactual?.counterfactual_score && (
                <div className="counterfactual-banner">
                  <Icon name="sparkles" size={18} color="#00454A" />
                  <span>
                    Achievable score without flagged conflicting additives: <strong>{counterfactual.counterfactual_score}/100</strong>
                  </span>
                </div>
              )}
              {recommendation && (
                <p className="rec-text">💡 {recommendation}</p>
              )}
            </div>
          </div>
        )}
      </div>

      {/* SECTION 4: ADVANCED TECHNICAL DETAILS (COLLAPSIBLE ACCORDION) */}
      <div className="card clinical-section-card accordion-card" style={{ marginTop: "1.5rem" }}>
        <button
          type="button"
          className="clinical-accordion-trigger"
          onClick={() => setShowTechDetails(!showTechDetails)}
          aria-expanded={showTechDetails}
        >
          <div className="accordion-trigger-left">
            <Icon name="sliders" size={16} color="#64748B" />
            <span>Technical Verification & Optical Details</span>
          </div>
          <Icon name={showTechDetails ? "chevronUp" : "chevronDown"} size={16} color="#64748B" />
        </button>

        {showTechDetails && (
          <div className="accordion-expandable-content" style={{ paddingTop: "1rem" }}>
            <div className="confidence-gauges-grid">
              <div className="confidence-gauge-item">
                <div className="gauge-top">
                  <span className="gauge-label">OCR Text Clarity</span>
                  <span className="gauge-val" style={{ color: ocrConfidence >= 75 ? "#16A34A" : ocrConfidence >= 40 ? "#F59E0B" : "#DC2626" }}>
                    {ocrConfidence !== null ? `${ocrConfidence}%` : "100%"}
                  </span>
                </div>
                <div className="gauge-track">
                  <div
                    className="gauge-fill"
                    style={{
                      width: `${ocrConfidence !== null ? ocrConfidence : 100}%`,
                      backgroundColor: ocrConfidence >= 75 ? "#16A34A" : ocrConfidence >= 40 ? "#F59E0B" : "#DC2626"
                    }}
                  />
                </div>
              </div>

              <div className="confidence-gauge-item">
                <div className="gauge-top">
                  <span className="gauge-label">Taxonomy Match</span>
                  <span className="gauge-val" style={{ color: "#16A34A" }}>
                    {additiveConfidence !== null ? `${additiveConfidence}%` : "100%"}
                  </span>
                </div>
                <div className="gauge-track">
                  <div
                    className="gauge-fill"
                    style={{
                      width: `${additiveConfidence !== null ? additiveConfidence : 100}%`,
                      backgroundColor: "#16A34A"
                    }}
                  />
                </div>
              </div>

              <div className="confidence-gauge-item">
                <div className="gauge-top">
                  <span className="gauge-label">Barcode Catalog Status</span>
                  <span className="gauge-badge">
                    {barcodeStatus === "valid_ean13" ? "✓ Verified EAN" : "Physical Label"}
                  </span>
                </div>
                <div className="gauge-track">
                  <div
                    className="gauge-fill"
                    style={{
                      width: barcodeStatus === "valid_ean13" ? "100%" : "30%",
                      backgroundColor: barcodeStatus === "valid_ean13" ? "#16A34A" : "#94A3B8"
                    }}
                  />
                </div>
              </div>

              <div className="confidence-gauge-item">
                <div className="gauge-top">
                  <span className="gauge-label">Decision Gate</span>
                  <span className="gauge-badge" style={{ color: is_provisional ? "#F59E0B" : "#16A34A" }}>
                    {is_provisional ? "⚠️ Provisional" : "✓ Verified"}
                  </span>
                </div>
                <div className="gauge-track">
                  <div
                    className="gauge-fill"
                    style={{
                      width: "100%",
                      backgroundColor: is_provisional ? "#F59E0B" : "#16A34A"
                    }}
                  />
                </div>
              </div>
            </div>

            {(ocrPipelineConfig || preprocessingMetrics) && (
              <div className="clinical-pipeline-banner" style={{ marginTop: "1rem" }}>
                <div className="pipeline-left">
                  <Icon name="sliders" size={15} color="#475569" />
                  <span>
                    <strong>Pipeline:</strong> {ocrPipelineConfig || "Configuration B (OpenCV + Tesseract)"}
                  </span>
                </div>
                {preprocessingMetrics && (
                  <div className="pipeline-badges-wrap">
                    <span className="pipeline-pill">
                      Sharpness: {Math.round(preprocessingMetrics.sharpness_score || 0)}
                      {preprocessingMetrics.is_blurry ? " (Blurry)" : " (Sharp)"}
                    </span>
                    <span className="pipeline-pill">
                      Lighting: {Math.round((preprocessingMetrics.lighting_uniformity || 0) * 100)}%
                      {preprocessingMetrics.has_uneven_lighting ? " (Uneven)" : " (Uniform)"}
                    </span>
                    {preprocessingMetrics.original_dims && (
                      <span className="pipeline-pill">
                        Resolution: {preprocessingMetrics.original_dims[0]}×{preprocessingMetrics.original_dims[1]}
                        {preprocessingMetrics.upscaled ? " (Scaled)" : ""}
                      </span>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Extracted Raw OCR Text */}
            <div style={{ marginTop: "1rem" }}>
              <span className="detail-label" style={{ display: "block", marginBottom: "0.35rem" }}>
                Extracted Raw OCR Text:
              </span>
              <pre className="clinical-raw-text-block">
                {analysisResult.extracted_text || product.raw_ingredient_text || "No raw text available."}
              </pre>
            </div>
          </div>
        )}
      </div>

      {/* STICKY BOTTOM ACTIONS */}
      <div className="sticky-action-bar">
        <div className="action-bar-content">
          <button
            type="button"
            className="btn btn-outline"
            onClick={onScanAnother}
          >
            <Icon name="camera" size={16} />
            <span>Scan Another</span>
          </button>

          {onOpenPreferences && (
            <button
              type="button"
              className="btn btn-outline"
              onClick={onOpenPreferences}
            >
              <Icon name="sliders" size={16} />
              <span>Update Preferences</span>
            </button>
          )}

          {onBackToDashboard && (
            <button
              type="button"
              className="btn btn-primary"
              onClick={onBackToDashboard}
            >
              <Icon name="layoutDashboard" size={16} />
              <span>Back to Dashboard</span>
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

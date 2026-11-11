import React from "react";

/**
 * ConfidencePanel — v2.2 (Multimodal Preprocessing & OCR Safety Gate Integrated)
 *
 * Displays all four confidence dimensions separately with clear labels explaining
 * what each value measures:
 *   1. OCR Confidence        — Mean word-level confidence from Tesseract OCR (float 0.0–1.0)
 *   2. Additive Matching     — Fraction of detected tokens resolved in taxonomy (float 0.0–1.0)
 *   3. Barcode Decode Status — Deterministic status enum ("valid_ean13", "invalid_checksum",
 *                              "not_provided", "lookup_failed"). NOT an invented percentage.
 *   4. Product Identity      — Confidence that product matches its barcode record (float 0.0–1.0)
 *
 * Plus OCR Safety Gate verification and Ingredient Section Isolation indicators.
 */
function ConfidencePanel({ systemAudit }) {
  if (!systemAudit) return null;

  const conf = systemAudit.confidence || {};
  const flagged = systemAudit.flagged_for_human_review;
  const reasons = systemAudit.flag_reasons || [];
  const ocrSafety = systemAudit.ocr_safety_gate || {};
  const sectionFound = systemAudit.ingredient_section_found;
  const separatedCount = systemAudit.separated_ingredients_count;
  const ocrWarning = systemAudit.ocr_uncertainty_warning;

  const getBarcodeBadge = (rawStatus) => {
    const status = (rawStatus || "").toLowerCase();
    switch (status) {
      case "valid_ean13":
        return {
          label: "Valid EAN-13",
          icon: "✓",
          color: "#10b981",
          bg: "rgba(16, 185, 129, 0.15)",
          barWidth: "100%",
          barColor: "#10b981"
        };
      case "invalid_checksum":
        return {
          label: "Invalid Checksum",
          icon: "✗",
          color: "#ef4444",
          bg: "rgba(239, 68, 68, 0.15)",
          barWidth: "100%",
          barColor: "#ef4444"
        };
      case "lookup_failed":
        return {
          label: "Lookup Failed",
          icon: "⚠",
          color: "#f59e0b",
          bg: "rgba(245, 158, 11, 0.15)",
          barWidth: "100%",
          barColor: "#f59e0b"
        };
      case "not_provided":
      default:
        return {
          label: "Not Provided",
          icon: "—",
          color: "#94a3b8",
          bg: "rgba(148, 163, 184, 0.15)",
          barWidth: "0%",
          barColor: "#64748b"
        };
    }
  };

  const barcodeStatus = conf.barcode_decode_status || (
    conf.barcode_confidence !== undefined
      ? (conf.barcode_confidence === 1.0 ? "valid_ean13" : "not_provided")
      : "not_provided"
  );
  const barcodeBadge = getBarcodeBadge(barcodeStatus);

  const metrics = [
    {
      key: "ocr_confidence",
      label: "OCR Text Confidence",
      icon: "🔤",
      isStatus: false,
      value: conf.ocr_confidence,
      description: "Mean word-level confidence from Tesseract OCR engine",
      tooltip: "1.0 when text came directly from a barcode database lookup (no OCR used)"
    },
    {
      key: "additive_match_confidence",
      label: "Additive Match Confidence",
      icon: "🧪",
      isStatus: false,
      value: conf.additive_match_confidence,
      description: "Fraction of detected additive tokens resolved in the taxonomy",
      tooltip: "Lower when additives appear on the label but aren't in our database"
    },
    {
      key: "barcode_decode_status",
      label: "Barcode Status",
      icon: "📦",
      isStatus: true,
      badge: barcodeBadge,
      description: "Deterministic EAN-13 checksum validation and lookup status",
      tooltip: "Categorical status enum (not an invented float)."
    },
    {
      key: "product_identity_confidence",
      label: "Product Identity Confidence",
      icon: "🏷️",
      isStatus: false,
      value: conf.product_identity_confidence,
      description: "Confidence that the product matches its barcode record",
      tooltip: "Reflects EAN validation and catalog verification status."
    },
  ];

  const getConfColor = (val) => {
    if (val === undefined || val === null) return "#64748b";
    if (val >= 0.85) return "#10b981";
    if (val >= 0.65) return "#f59e0b";
    return "#ef4444";
  };

  const formatPct = (val) => {
    if (val === undefined || val === null) return "N/A";
    return `${Math.round(val * 100)}%`;
  };

  return (
    <div className="card glass confidence-panel-card">
      <div className="card-header">
        <span className="card-icon">🎯</span>
        <div>
          <h2>Confidence & Multimodal Quality Indicators</h2>
          <p className="card-sub">
            Four independent confidence dimensions, OCR Safety Gate status, and automated section isolation.
          </p>
        </div>
      </div>

      <div className="confidence-grid">
        {metrics.map((m) => {
          if (m.isStatus) {
            const badge = m.badge;
            return (
              <div key={m.key} className="confidence-metric-card" title={m.tooltip}>
                <div className="conf-metric-header">
                  <span className="conf-icon">{m.icon}</span>
                  <span className="conf-label">{m.label}</span>
                  <span
                    className="conf-status-badge"
                    style={{
                      color: badge.color,
                      backgroundColor: badge.bg,
                      borderColor: badge.color
                    }}
                  >
                    {badge.icon} {badge.label}
                  </span>
                </div>
                <div className="conf-bar-track">
                  <div
                    className="conf-bar-fill"
                    style={{
                      width: badge.barWidth,
                      backgroundColor: badge.barColor
                    }}
                  />
                </div>
                <p className="conf-description">{m.description}</p>
              </div>
            );
          }

          const val = m.value;
          const pct = val !== undefined && val !== null ? Math.round(val * 100) : null;
          const color = getConfColor(val);

          return (
            <div key={m.key} className="confidence-metric-card" title={m.tooltip}>
              <div className="conf-metric-header">
                <span className="conf-icon">{m.icon}</span>
                <span className="conf-label">{m.label}</span>
                <span className="conf-value" style={{ color }}>
                  {formatPct(val)}
                </span>
              </div>
              <div className="conf-bar-track">
                <div
                  className="conf-bar-fill"
                  style={{
                    width: pct !== null ? `${pct}%` : "0%",
                    backgroundColor: color
                  }}
                />
              </div>
              <p className="conf-description">{m.description}</p>
            </div>
          );
        })}
      </div>

      {/* Multimodal Pipeline Telemetry (Section Isolation & Safety Gate) */}
      <div style={{
        marginTop: "1rem",
        padding: "0.85rem 1rem",
        backgroundColor: "rgba(15, 23, 42, 0.4)",
        borderRadius: "8px",
        border: "1px solid rgba(255, 255, 255, 0.06)",
        display: "flex",
        flexWrap: "wrap",
        gap: "1.25rem",
        fontSize: "0.82rem"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <span>🛡️ <strong>OCR Safety Gate:</strong></span>
          <span
            style={{
              padding: "0.15rem 0.5rem",
              borderRadius: "4px",
              backgroundColor: ocrWarning ? "rgba(245, 158, 11, 0.2)" : "rgba(16, 185, 129, 0.2)",
              color: ocrWarning ? "#fde68a" : "#a7f3d0",
              fontWeight: 600,
              cursor: ocrSafety.safety_warning ? "help" : "default"
            }}
            title={ocrSafety.safety_warning || (ocrWarning ? "OCR clarity is below threshold" : "All OCR quality checks passed")}
          >
            {ocrWarning ? "⚠️ Triggered (Provisional)" : "✓ Verified Safe for Decisions"}
          </span>
        </div>

        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <span>📑 <strong>Section Isolation:</strong></span>
          <span style={{ color: sectionFound ? "#93c5fd" : "#cbd5e1" }}>
            {sectionFound ? "✓ INGREDIENTS Header Isolated" : "ℹ️ Full Label Scan"}
            {separatedCount ? ` (${separatedCount} clauses)` : ""}
          </span>
        </div>
      </div>

      {/* HITL status */}
      <div className={`hitl-status-banner ${flagged ? "hitl-flagged" : "hitl-clear"}`} style={{ marginTop: "1rem" }}>
        {flagged ? (
          <>
            <span>⚠️</span>
            <div>
              <strong>Flagged for Human Review</strong>
              <ul className="flag-reasons-list">
                {reasons.map((r, i) => <li key={i}>{r}</li>)}
              </ul>
            </div>
          </>
        ) : (
          <>
            <span>✅</span>
            <strong>All confidence and safety checks passed — automated decision approved.</strong>
          </>
        )}
      </div>
    </div>
  );
}

export default ConfidencePanel;

import React from "react";

export default function PersonalisedScoreCard({ personalEvaluation, onOpenProfileModal }) {
  if (!personalEvaluation) return null;

  const {
    personal_score = 100,
    personal_verdict = "Compatible",
    allergen_alerts = [],
    preference_conflicts = [],
    caution_items = [],
    preset_name = "custom",
    is_personalized = false,
    is_provisional = false,
    definitive_score_suppressed = false,
    extraction_warning = "",
    recommendation = ""
  } = personalEvaluation;

  const getScoreColor = (score) => {
    if (score >= 90) return "#10b981"; // emerald green
    if (score >= 70) return "#f59e0b"; // amber
    return "#ef4444"; // red
  };

  const hasAllergens = allergen_alerts && allergen_alerts.length > 0;
  const scoreColor = hasAllergens ? "#ef4444" : getScoreColor(personal_score);

  return (
    <div className="card glass personalised-card" style={{ marginBottom: "1.5rem" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <div>
          <h3 style={{ margin: 0, fontSize: "1.2rem", color: "#f8fafc", display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <span>🥗 Personalised Dietary Assessment</span>
            {is_personalized && (
              <span style={{
                fontSize: "0.75rem",
                padding: "0.2rem 0.6rem",
                borderRadius: "12px",
                backgroundColor: "rgba(99, 102, 241, 0.2)",
                border: "1px solid rgba(99, 102, 241, 0.4)",
                color: "#c7d2fe",
                fontWeight: 600,
                textTransform: "capitalize"
              }}>
                {preset_name.replace("_", " ")} Profile
              </span>
            )}
            {is_provisional && (
              <span style={{
                fontSize: "0.72rem",
                padding: "0.2rem 0.5rem",
                borderRadius: "12px",
                backgroundColor: "rgba(245, 158, 11, 0.2)",
                border: "1px solid rgba(245, 158, 11, 0.4)",
                color: "#fde68a",
                fontWeight: 600
              }}>
                ⚠️ Provisional Score
              </span>
            )}
          </h3>
          <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.82rem", color: "#94a3b8" }}>
            Tailored evaluation based on your individual dietary restrictions, active avoidances, and configured allergens.
          </p>
        </div>
        {onOpenProfileModal && (
          <button
            onClick={onOpenProfileModal}
            className="btn btn-outline"
            style={{ padding: "0.35rem 0.75rem", fontSize: "0.8rem" }}
          >
            ⚙️ Edit Profile
          </button>
        )}
      </div>

      {/* OCR Safety Gate Provisional Alert (Phase 7 & 9) */}
      {(is_provisional || definitive_score_suppressed) && (
        <div style={{
          backgroundColor: "rgba(245, 158, 11, 0.12)",
          border: "1px solid rgba(245, 158, 11, 0.35)",
          borderRadius: "8px",
          padding: "0.85rem 1rem",
          marginBottom: "1rem"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontWeight: "bold", fontSize: "0.9rem", color: "#fde68a" }}>
            <span>⚠️</span>
            <span>OCR SAFETY GATE: PROVISIONAL DIETARY VERDICT</span>
          </div>
          <p style={{ margin: "0.35rem 0 0.25rem 0", fontSize: "0.82rem", color: "#e2e8f0", lineHeight: 1.4 }}>
            {extraction_warning || "OCR text confidence is below the safety threshold (< 40%). Dietary conclusions may be incomplete."}
          </p>
          {recommendation && (
            <div style={{ fontSize: "0.78rem", color: "#fef08a", marginTop: "0.25rem" }}>
              💡 <em>Action:</em> {recommendation}
            </div>
          )}
        </div>
      )}

      {/* Critical Allergen Alert Banner */}
      {hasAllergens && (
        <div style={{
          backgroundColor: "rgba(239, 68, 68, 0.15)",
          border: "2px solid #ef4444",
          borderRadius: "8px",
          padding: "0.85rem 1.1rem",
          color: "#fca5a5",
          marginBottom: "1rem"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", fontWeight: "bold", fontSize: "0.98rem", color: "#fecaca" }}>
            <span style={{ fontSize: "1.3rem" }}>🚨</span>
            <span>CRITICAL ALLERGEN WARNING</span>
          </div>
          <div style={{ marginTop: "0.5rem", display: "flex", flexDirection: "column", gap: "0.4rem" }}>
            {allergen_alerts.map((alert, idx) => (
              <div key={idx} style={{ fontSize: "0.85rem", lineHeight: 1.4, color: "#fee2e2" }}>
                • <strong>{alert.allergen.toUpperCase()}:</strong> Detected token "<em>{alert.matched_term}</em>". {alert.action_required}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Score & Verdict Section */}
      <div style={{
        display: "flex",
        alignItems: "center",
        gap: "1.5rem",
        padding: "1rem 1.25rem",
        backgroundColor: "rgba(15, 23, 42, 0.55)",
        border: "1px solid rgba(255, 255, 255, 0.06)",
        borderRadius: "8px",
        marginBottom: "1rem"
      }}>
        <div style={{
          width: "72px",
          height: "72px",
          borderRadius: "50%",
          backgroundColor: scoreColor,
          display: "flex",
          flexDirection: "column",
          justifyContent: "center",
          alignItems: "center",
          color: "#ffffff",
          flexShrink: 0,
          boxShadow: `0 0 16px ${scoreColor}40`
        }}>
          <span style={{ fontSize: "1.5rem", fontWeight: "bold", lineHeight: 1 }}>{hasAllergens ? "!" : personal_score}</span>
          <span style={{ fontSize: "0.65rem", opacity: 0.9 }}>/ 100</span>
        </div>

        <div>
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem" }}>
            <span style={{
              fontSize: "0.92rem",
              fontWeight: 700,
              padding: "0.25rem 0.65rem",
              borderRadius: "4px",
              backgroundColor: hasAllergens ? "rgba(239, 68, 68, 0.2)" : personal_score >= 90 ? "rgba(16, 185, 129, 0.2)" : personal_score >= 70 ? "rgba(245, 158, 11, 0.2)" : "rgba(239, 68, 68, 0.2)",
              color: scoreColor,
              border: `1px solid ${scoreColor}50`
            }}>
              {personal_verdict}
            </span>
          </div>
          <p style={{ margin: "0.4rem 0 0 0", fontSize: "0.84rem", color: "#cbd5e1", lineHeight: 1.4 }}>
            {hasAllergens
              ? "Allergen triggers detected. Do not consume if you have severe intolerances."
              : is_provisional
              ? "Evaluation is based on partial or low-confidence OCR text. Inspect physical packaging manually."
              : personal_score >= 90
              ? "Product is fully compliant with your active dietary preferences."
              : personal_score >= 70
              ? "Product contains minor additives you prefer to limit. Review caution notes below."
              : "Product conflicts with one or more of your active dietary preferences."}
          </p>
        </div>
      </div>

      {/* Preference Conflicts List */}
      {preference_conflicts && preference_conflicts.length > 0 && (
        <div style={{ marginBottom: "1rem" }}>
          <h4 style={{ margin: "0 0 0.5rem 0", fontSize: "0.9rem", color: "#fca5a5" }}>
            Specific Dietary Preference Conflicts ({preference_conflicts.length})
          </h4>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
            {preference_conflicts.map((c, i) => (
              <div key={i} style={{
                backgroundColor: "rgba(239, 68, 68, 0.1)",
                borderLeft: "3px solid #ef4444",
                padding: "0.5rem 0.75rem",
                borderRadius: "4px"
              }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ fontWeight: 600, color: "#fca5a5" }}>{c.name} ({c.code})</span>
                  <span style={{ fontSize: "0.78rem", color: "#f87171", fontWeight: 600 }}>-{c.deduction} pts</span>
                </div>
                <div style={{ fontSize: "0.8rem", color: "#fecaca", marginTop: "0.15rem" }}>
                  {c.reason}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Caution Items */}
      {caution_items && caution_items.length > 0 && (
        <div>
          <h4 style={{ margin: "0 0 0.5rem 0", fontSize: "0.9rem", color: "#fde68a" }}>
            Dietary Caution Items ({caution_items.length})
          </h4>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
            {caution_items.map((item, i) => (
              <div key={i} style={{
                backgroundColor: "rgba(245, 158, 11, 0.1)",
                borderLeft: "3px solid #f59e0b",
                padding: "0.5rem 0.75rem",
                borderRadius: "4px"
              }}>
                <div style={{ display: "flex", justifyContent: "space-between" }}>
                  <span style={{ fontWeight: 600, color: "#fde68a" }}>{item.name} ({item.code})</span>
                  <span style={{ fontSize: "0.78rem", color: "#fbbf24", fontWeight: 600 }}>-{item.deduction} pts</span>
                </div>
                <div style={{ fontSize: "0.8rem", color: "#fef3c7", marginTop: "0.15rem" }}>
                  {item.reason}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

import React, { useState } from "react";
import { parseAdditivesDirect, extractIngredientSection } from "../api";

const PRESET_FORMULATIONS = [
  {
    name: "Instant Noodles",
    tag: "MSG (INS 621) + Thickeners + Caramel IV",
    text: "Ingredients: Refined Wheat Flour (Maida), Palm Oil, Salt, Wheat Gluten, Mineral (Calcium Carbonate), Thickeners (INS 508, INS 412), Acidity Regulators (INS 501(i), INS 500(i), INS 451(i)). Noodle Tastemaker: Hydrolysed Peanut Protein, Mixed Spices (15.5%) (Onion Powder, Coriander Powder, Chilli Powder, Turmeric Powder, Garlic Powder, Cumin Powder, Aniseed Powder, Black Pepper Powder, Fenugreek Powder, Ginger Powder, Clove Powder, Nutmeg Powder, Cardamom Powder), Noodle Powder, Sugar, Edible Starch, Flavour Enhancer (INS 635, INS 621), Palm Oil, Thickener (INS 508), Salt, Acidity Regulator (INS 330), Mineral (Ferric Pyrophosphate), Caramel Colour (INS 150d). CONTAINS WHEAT, PEANUT AND GLUTEN."
  },
  {
    name: "Sparkling Citrus Drink",
    tag: "Tartrazine (INS 102) + Sunset Yellow + Preservative",
    text: "Ingredients: Carbonated Water, Sugar, Acidity Regulators (INS 330, INS 331), Preservative (INS 211), Synthetic Food Colour (INS 102, INS 110), Added Nature Identical Flavouring Substances (Orange). Contains Permitted Synthetic Food Colours."
  },
  {
    name: "Salty Snack Chips",
    tag: "INS 627, INS 631, Acidity Regulators & Dairy",
    text: "Ingredients: Potato (62%), Edible Vegetable Oil (Palmolein Oil), Seasoning (Spices & Condiments, Iodised Salt, Sugar, Flavour (Natural and Nature Identical Flavouring Substances), Flavour Enhancer (INS 627, INS 631), Milk Solids, Acidity Regulators (INS 330, INS 296), Anticaking Agent (INS 551)). CONTAINS MILK."
  },
  {
    name: "Clean Label Fruit Snack",
    tag: "Zero Additives, All-Natural Ingredients",
    text: "Ingredients: Rolled Oats, Raw Honey, Almonds, Pumpkin Seeds, Sunflower Seeds, Virgin Coconut Oil, Cinnamon Powder, Sea Salt. CONTAINS TREE NUTS (ALMONDS)."
  }
];

function IngredientTextInput({ onAnalyze, loading }) {
  const [text, setText] = useState("");
  const [inspectLoading, setInspectLoading] = useState(false);
  const [quickInspectResult, setQuickInspectResult] = useState(null);
  const [sectionResult, setSectionResult] = useState(null);
  const [inspectError, setInspectError] = useState("");

  const handleSelectPreset = (preset) => {
    setText(preset.text);
    setQuickInspectResult(null);
    setSectionResult(null);
    setInspectError("");
  };

  const handleAnalyze = (e) => {
    e.preventDefault();
    if (!text.trim()) return;
    onAnalyze({
      text: text.trim(),
      ocr_confidence: 1.0,
      product: {
        name: "Manual Ingredient Label",
        brand: "Custom Entry",
        category: "Direct Formulation Check"
      }
    });
  };

  const handleQuickParse = async () => {
    if (!text.trim()) return;
    setInspectLoading(true);
    setInspectError("");
    setSectionResult(null);
    try {
      const data = await parseAdditivesDirect(text.trim(), 1.0);
      setQuickInspectResult(data.result);
    } catch (err) {
      setInspectError(err.response?.data?.message || err.message || "Failed to inspect additives");
    } finally {
      setInspectLoading(false);
    }
  };

  const handleExtractSection = async () => {
    if (!text.trim()) return;
    setInspectLoading(true);
    setInspectError("");
    setQuickInspectResult(null);
    try {
      const data = await extractIngredientSection(text.trim(), 1.0);
      setSectionResult(data);
    } catch (err) {
      setInspectError(err.response?.data?.message || err.message || "Failed to extract ingredient section");
    } finally {
      setInspectLoading(false);
    }
  };

  return (
    <div className="card glass ingredient-text-card">
      <div className="card-header">
        <span className="card-icon">📝</span>
        <div>
          <h2>Manual Ingredient Text & Section Analysis</h2>
          <p className="card-sub">
            Paste food packaging ingredients, run quick live parsing, or test automated section isolation.
          </p>
        </div>
      </div>

      {/* Preset selection bar */}
      <div className="benchmark-section" style={{ marginBottom: "1rem" }}>
        <span className="benchmark-title">⚡ Quick Formulation Presets:</span>
        <div className="benchmark-chips">
          {PRESET_FORMULATIONS.map((p, idx) => (
            <button
              key={idx}
              type="button"
              className={`chip ${text === p.text ? "active" : ""}`}
              onClick={() => handleSelectPreset(p)}
              disabled={loading || inspectLoading}
            >
              <strong>{p.name}</strong>
              <span className="chip-tag">{p.tag}</span>
            </button>
          ))}
        </div>
      </div>

      <form onSubmit={handleAnalyze}>
        <div style={{ position: "relative" }}>
          <textarea
            className="ingredient-textarea"
            rows={5}
            placeholder="Paste complete ingredient declaration here... (e.g., 'Ingredients: Water, Sugar, Acidity Regulators (INS 330, INS 331), Preservative (INS 211), Synthetic Food Colour (INS 102). CONTAINS PERMITTED NATURAL FLAVOUR.')"
            value={text}
            onChange={(e) => setText(e.target.value)}
            disabled={loading || inspectLoading}
          />
          <div style={{
            display: "flex",
            justifyContent: "space-between",
            fontSize: "0.78rem",
            color: "#94a3b8",
            marginTop: "0.35rem"
          }}>
            <span>Characters: {text.length} • Words: {text.trim() ? text.trim().split(/\s+/).length : 0}</span>
            {text && (
              <button
                type="button"
                onClick={() => { setText(""); setQuickInspectResult(null); setSectionResult(null); }}
                style={{ background: "none", border: "none", color: "#f87171", cursor: "pointer", fontSize: "0.78rem" }}
              >
                Clear text
              </button>
            )}
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem", marginTop: "1rem" }}>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || inspectLoading || !text.trim()}
          >
            {loading ? "Analyzing..." : "🔍 Run Full Verification"}
          </button>

          <button
            type="button"
            className="btn btn-outline"
            onClick={handleQuickParse}
            disabled={loading || inspectLoading || !text.trim()}
          >
            {inspectLoading ? "Parsing..." : "🧪 Quick Parse Additives"}
          </button>

          <button
            type="button"
            className="btn btn-outline"
            onClick={handleExtractSection}
            disabled={loading || inspectLoading || !text.trim()}
          >
            {inspectLoading ? "Isolating..." : "📑 Test Section Isolation"}
          </button>
        </div>
      </form>

      {inspectError && (
        <div style={{ marginTop: "1rem", color: "#fca5a5", fontSize: "0.85rem" }}>
          ⚠️ {inspectError}
        </div>
      )}

      {/* Quick Additives Inspection Result */}
      {quickInspectResult && (
        <div className="quick-inspect-panel" style={{
          marginTop: "1.25rem",
          padding: "1rem",
          backgroundColor: "rgba(15, 23, 42, 0.6)",
          borderRadius: "8px",
          border: "1px solid rgba(255, 255, 255, 0.1)"
        }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
            <h4 style={{ margin: 0, fontSize: "0.95rem", color: "#93c5fd" }}>
              🧪 Fast Additive Parser Results ({quickInspectResult.parsed_additives?.length || 0} additives found)
            </h4>
            <span style={{ fontSize: "0.78rem", color: "#cbd5e1" }}>
              Match Confidence: <strong>{Math.round((quickInspectResult.additive_match_confidence || 0) * 100)}%</strong>
            </span>
          </div>

          {/* Categories */}
          {quickInspectResult.detected_categories && Object.keys(quickInspectResult.detected_categories).length > 0 && (
            <div style={{ marginBottom: "0.75rem" }}>
              <div style={{ fontSize: "0.75rem", color: "#94a3b8", marginBottom: "0.35rem" }}>DETECTED FUNCTIONAL CATEGORIES:</div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem" }}>
                {Object.entries(quickInspectResult.detected_categories).map(([cat, codes]) => (
                  <span key={cat} style={{
                    padding: "0.2rem 0.5rem",
                    borderRadius: "6px",
                    backgroundColor: "rgba(99, 102, 241, 0.2)",
                    border: "1px solid rgba(99, 102, 241, 0.4)",
                    color: "#c7d2fe",
                    fontSize: "0.75rem"
                  }}>
                    🏷️ <strong>{cat}</strong> ({codes.length}): {codes.join(", ")}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Additives List */}
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginBottom: "0.5rem" }}>
            {quickInspectResult.parsed_additives?.map((a, i) => (
              <span key={i} style={{
                padding: "0.25rem 0.6rem",
                borderRadius: "6px",
                backgroundColor: a.hazard_level === "High" ? "rgba(239, 68, 68, 0.2)" : "rgba(16, 185, 129, 0.15)",
                border: `1px solid ${a.hazard_level === "High" ? "rgba(239, 68, 68, 0.4)" : "rgba(16, 185, 129, 0.3)"}`,
                color: a.hazard_level === "High" ? "#fca5a5" : "#a7f3d0",
                fontSize: "0.8rem"
              }}>
                <strong>{a.code}</strong> — {a.name}
              </span>
            ))}
          </div>

          {/* Ambiguous Terms Notice */}
          {quickInspectResult.ambiguous_detections && quickInspectResult.ambiguous_detections.length > 0 && (
            <div style={{ marginTop: "0.5rem", fontSize: "0.78rem", color: "#fde68a" }}>
              ⚠️ <strong>Ambiguous detections:</strong> {quickInspectResult.ambiguous_detections.map(item => item.matched_term || item.code).join(", ")}
            </div>
          )}

          {/* Duplicate Detections Notice */}
          {quickInspectResult.duplicate_detections && quickInspectResult.duplicate_detections.length > 0 && (
            <div style={{ marginTop: "0.35rem", fontSize: "0.78rem", color: "#93c5fd" }}>
              ℹ️ <strong>Duplicate mentions consolidated:</strong> {quickInspectResult.duplicate_detections.map(d => `${d.code} (${d.count}x)`).join(", ")}
            </div>
          )}
        </div>
      )}

      {/* Section Isolation Result */}
      {sectionResult && (
        <div className="quick-inspect-panel" style={{
          marginTop: "1.25rem",
          padding: "1rem",
          backgroundColor: "rgba(15, 23, 42, 0.6)",
          borderRadius: "8px",
          border: "1px solid rgba(255, 255, 255, 0.1)"
        }}>
          <h4 style={{ margin: "0 0 0.5rem 0", fontSize: "0.95rem", color: "#93c5fd" }}>
            📑 Ingredient Section Isolation Result
          </h4>
          <div style={{ fontSize: "0.8rem", color: "#e2e8f0", marginBottom: "0.5rem" }}>
            Section Found: <strong>{sectionResult.section_info?.section_found ? "✅ Yes (Header Isolated)" : "ℹ️ Whole Text Used (No explicit header)"}</strong>
            {" • "}Separated Clauses: <strong>{sectionResult.separated_count}</strong>
          </div>
          <div style={{
            fontSize: "0.78rem",
            backgroundColor: "rgba(0,0,0,0.3)",
            padding: "0.6rem",
            borderRadius: "6px",
            color: "#cbd5e1",
            maxHeight: "120px",
            overflowY: "auto",
            marginBottom: "0.5rem"
          }}>
            <strong>Extracted Section:</strong> {sectionResult.section_info?.ingredient_text || "N/A"}
          </div>
          {sectionResult.separated_ingredients && sectionResult.separated_ingredients.length > 0 && (
            <div>
              <div style={{ fontSize: "0.75rem", color: "#94a3b8", marginBottom: "0.35rem" }}>PARSED INGREDIENT CLAUSES:</div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: "0.3rem" }}>
                {sectionResult.separated_ingredients.map((ing, idx) => (
                  <span key={idx} style={{
                    padding: "0.15rem 0.45rem",
                    borderRadius: "4px",
                    backgroundColor: "rgba(255, 255, 255, 0.05)",
                    fontSize: "0.75rem",
                    color: "#e2e8f0"
                  }}>
                    {ing}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default IngredientTextInput;

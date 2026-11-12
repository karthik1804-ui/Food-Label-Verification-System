import React, { useState, useEffect } from "react";
import { updateDietaryProfile } from "../api";
import Icon from "./Icons";

const ALLERGEN_OPTIONS = [
  { id: "peanuts", label: "Peanuts", icon: "🥜" },
  { id: "tree_nuts", label: "Tree Nuts (Almonds, Cashews)", icon: "🌰" },
  { id: "dairy", label: "Dairy / Milk Solids", icon: "🥛" },
  { id: "gluten", label: "Gluten / Wheat", icon: "🌾" },
  { id: "soy", label: "Soy / Soybeans", icon: "🌱" },
  { id: "egg", label: "Eggs & Albumin", icon: "🥚" },
  { id: "fish", label: "Fish", icon: "🐟" },
  { id: "shellfish", label: "Crustaceans / Shellfish", icon: "🦐" },
  { id: "sesame", label: "Sesame", icon: "🥯" },
  { id: "sulfites", label: "Sulfites (Sulphur Dioxide)", icon: "🍷" },
  { id: "mustard", label: "Mustard", icon: "🌭" },
];

const PRESET_CARDS = [
  {
    key: "clean_label",
    title: "Clean Eating",
    subtitle: "Zero synthetic dyes, preservatives & artificial enhancers",
    icon: "leaf",
    color: "#059669"
  },
  {
    key: "vegan",
    title: "Strict Vegan",
    subtitle: "Avoids all animal-derived additives (Carmine, Gelatin, Shellac)",
    icon: "heart",
    color: "#0284c7"
  },
  {
    key: "vegetarian",
    title: "Vegetarian",
    subtitle: "Avoids meat-derived collagen, animal fats & bone phosphates",
    icon: "sparkles",
    color: "#7c3aed"
  },
  {
    key: "child_safe",
    title: "Low Additive",
    subtitle: "Flags intense synthetic dyes & non-nutritive sweeteners",
    icon: "shieldCheck",
    color: "#d97706"
  },
  {
    key: "custom",
    title: "Custom Profile",
    subtitle: "Tailor your exact avoided additive categories & allergens",
    icon: "sliders",
    color: "#475569"
  }
];

export default function DietaryPreferencesView({
  currentProfile,
  onProfileSaved,
  onProceedToScan,
  currentUser
}) {
  const [selectedPreset, setSelectedPreset] = useState("clean_label");
  const [avoidColors, setAvoidColors] = useState(false);
  const [avoidPreserv, setAvoidPreserv] = useState(false);
  const [avoidSweeteners, setAvoidSweeteners] = useState(false);
  const [avoidMsg, setAvoidMsg] = useState(false);
  const [avoidAnimal, setAvoidAnimal] = useState(false);
  const [selectedAllergens, setSelectedAllergens] = useState([]);
  const [customAvoidIns, setCustomAvoidIns] = useState("");
  const [showAdvanced, setShowAdvanced] = useState(false);
  const [saving, setSaving] = useState(false);
  const [statusMessage, setStatusMessage] = useState({ text: "", type: "" });

  useEffect(() => {
    if (currentProfile) {
      setSelectedPreset(currentProfile.preset_name || "clean_label");
      setAvoidColors(Boolean(currentProfile.avoid_synthetic_colors));
      setAvoidPreserv(Boolean(currentProfile.avoid_preservatives));
      setAvoidSweeteners(Boolean(currentProfile.avoid_artificial_sweeteners));
      setAvoidMsg(Boolean(currentProfile.avoid_msg_flavor_enhancers));
      setAvoidAnimal(Boolean(currentProfile.avoid_animal_derivatives));
      setSelectedAllergens(currentProfile.custom_allergens || []);
      setCustomAvoidIns((currentProfile.custom_avoid_ins || []).join(", "));
    } else {
      // Default initial preset
      handlePresetSelect("clean_label");
    }
  }, [currentProfile]);

  const handlePresetSelect = (presetKey) => {
    setSelectedPreset(presetKey);
    if (presetKey === "custom") return;

    if (presetKey === "clean_label") {
      setAvoidColors(true);
      setAvoidPreserv(true);
      setAvoidSweeteners(true);
      setAvoidMsg(true);
      setAvoidAnimal(false);
      setCustomAvoidIns("INS 102, INS 110, INS 122, INS 124, INS 129, INS 133, INS 211, INS 250");
    } else if (presetKey === "vegan") {
      setAvoidColors(false);
      setAvoidPreserv(false);
      setAvoidSweeteners(false);
      setAvoidMsg(false);
      setAvoidAnimal(true);
      setCustomAvoidIns("INS 120, INS 428, INS 542, INS 901, INS 904, INS 920");
    } else if (presetKey === "vegetarian") {
      setAvoidColors(false);
      setAvoidPreserv(false);
      setAvoidSweeteners(false);
      setAvoidMsg(false);
      setAvoidAnimal(true);
      setCustomAvoidIns("INS 120, INS 428, INS 542");
    } else if (presetKey === "child_safe") {
      setAvoidColors(true);
      setAvoidPreserv(false);
      setAvoidSweeteners(true);
      setAvoidMsg(true);
      setAvoidAnimal(false);
      setCustomAvoidIns("INS 102, INS 110, INS 122, INS 124, INS 129, INS 951, INS 955");
    }
  };

  const toggleAllergen = (id) => {
    if (selectedAllergens.includes(id)) {
      setSelectedAllergens(selectedAllergens.filter((a) => a !== id));
    } else {
      setSelectedAllergens([...selectedAllergens, id]);
    }
  };

  const handleSavePreferences = async (e) => {
    if (e) e.preventDefault();
    setSaving(true);
    setStatusMessage({ text: "", type: "" });

    const avoidList = customAvoidIns
      .split(",")
      .map((s) => s.trim().toUpperCase())
      .filter((s) => s.length > 0);

    const payload = {
      preset_name: selectedPreset,
      custom_override: true,
      avoid_synthetic_colors: avoidColors,
      avoid_preservatives: avoidPreserv,
      avoid_artificial_sweeteners: avoidSweeteners,
      avoid_msg_flavor_enhancers: avoidMsg,
      avoid_animal_derivatives: avoidAnimal,
      custom_allergens: selectedAllergens,
      custom_avoid_ins: avoidList,
      custom_caution_ins: currentProfile?.custom_caution_ins || []
    };

    try {
      if (currentUser) {
        const res = await updateDietaryProfile(payload);
        setStatusMessage({ text: "Preferences saved to your account!", type: "success" });
        if (onProfileSaved && res.dietary_profile) {
          onProfileSaved(res.dietary_profile);
        }
      } else {
        // Guest mode session update
        setStatusMessage({ text: "Preferences saved for this session!", type: "success" });
        if (onProfileSaved) {
          onProfileSaved(payload);
        }
      }

      setTimeout(() => {
        if (onProceedToScan) onProceedToScan();
      }, 500);
    } catch (err) {
      console.error("Save preferences failed:", err);
      // Even if network fails or guest mode, keep local preferences active
      if (onProfileSaved) {
        onProfileSaved(payload);
      }
      setStatusMessage({ text: "Preferences active locally. Proceeding...", type: "warning" });
      setTimeout(() => {
        if (onProceedToScan) onProceedToScan();
      }, 700);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="dietary-preferences-container">
      {/* Header */}
      <div className="section-intro-header">
        <div className="section-badge">
          <Icon name="leaf" size={16} />
          <span>Step 2 of 4</span>
        </div>
        <h2>Configure Your Dietary Preferences</h2>
        <p>
          Select a preset or customize specific additives and allergens. Your product scans will be evaluated against these personal criteria.
        </p>
      </div>

      {statusMessage.text && (
        <div className={`alert-banner alert-${statusMessage.type === "success" ? "success" : "warning"}`} style={{ marginBottom: "1.5rem" }}>
          <Icon name={statusMessage.type === "success" ? "checkCircle" : "alertTriangle"} size={18} />
          <span>{statusMessage.text}</span>
        </div>
      )}

      {/* 1. Visual Preset Selection Cards */}
      <div className="preference-block">
        <label className="preference-block-title">Choose a Lifestyle Preset</label>
        <p className="preference-block-sub">Pick a preset to automatically populate recommended avoidance targets:</p>

        <div className="preset-cards-grid">
          {PRESET_CARDS.map((card) => {
            const isSelected = selectedPreset === card.key;
            return (
              <button
                key={card.key}
                type="button"
                className={`preset-card ${isSelected ? "selected" : ""}`}
                onClick={() => handlePresetSelect(card.key)}
              >
                <div className="preset-card-top">
                  <div className="preset-card-icon" style={{ backgroundColor: `${card.color}15`, color: card.color }}>
                    <Icon name={card.icon} size={22} />
                  </div>
                  <div className="preset-radio-indicator">
                    {isSelected ? <Icon name="check" size={14} strokeWidth={3} /> : null}
                  </div>
                </div>
                <h3 className="preset-card-title">{card.title}</h3>
                <p className="preset-card-desc">{card.subtitle}</p>
              </button>
            );
          })}
        </div>
      </div>

      {/* 2. Specific Additive Categories to Avoid */}
      <div className="preference-block">
        <div className="preference-block-header">
          <div>
            <label className="preference-block-title">Additive Categories to Avoid</label>
            <p className="preference-block-sub">Fine-tune individual functional additive classes:</p>
          </div>
        </div>

        <div className="category-toggles-grid">
          <label className={`toggle-card ${avoidColors ? "checked" : ""}`}>
            <input
              type="checkbox"
              checked={avoidColors}
              onChange={(e) => { setAvoidColors(e.target.checked); setSelectedPreset("custom"); }}
            />
            <div className="toggle-card-content">
              <span className="toggle-title">🎨 Synthetic / Artificial Colours</span>
              <span className="toggle-sub">Flags Tartrazine (INS 102), Sunset Yellow (INS 110), Allura Red, etc.</span>
            </div>
            <div className="toggle-switch-ui" />
          </label>

          <label className={`toggle-card ${avoidPreserv ? "checked" : ""}`}>
            <input
              type="checkbox"
              checked={avoidPreserv}
              onChange={(e) => { setAvoidPreserv(e.target.checked); setSelectedPreset("custom"); }}
            />
            <div className="toggle-card-content">
              <span className="toggle-title">🛡️ Chemical Preservatives</span>
              <span className="toggle-sub">Flags Sodium Benzoate (INS 211), Sodium Nitrite (INS 250), Sorbates.</span>
            </div>
            <div className="toggle-switch-ui" />
          </label>

          <label className={`toggle-card ${avoidSweeteners ? "checked" : ""}`}>
            <input
              type="checkbox"
              checked={avoidSweeteners}
              onChange={(e) => { setAvoidSweeteners(e.target.checked); setSelectedPreset("custom"); }}
            />
            <div className="toggle-card-content">
              <span className="toggle-title">🍬 Non-Nutritive Sweeteners</span>
              <span className="toggle-sub">Flags Aspartame (INS 951), Sucralose (INS 955), Acesulfame-K (INS 950).</span>
            </div>
            <div className="toggle-switch-ui" />
          </label>

          <label className={`toggle-card ${avoidMsg ? "checked" : ""}`}>
            <input
              type="checkbox"
              checked={avoidMsg}
              onChange={(e) => { setAvoidMsg(e.target.checked); setSelectedPreset("custom"); }}
            />
            <div className="toggle-card-content">
              <span className="toggle-title">🥣 Flavour Enhancers & MSG</span>
              <span className="toggle-sub">Flags Monosodium Glutamate (INS 621), Disodium Inosinate/Guanylate (INS 627, 631).</span>
            </div>
            <div className="toggle-switch-ui" />
          </label>

          <label className={`toggle-card ${avoidAnimal ? "checked" : ""}`}>
            <input
              type="checkbox"
              checked={avoidAnimal}
              onChange={(e) => { setAvoidAnimal(e.target.checked); setSelectedPreset("custom"); }}
            />
            <div className="toggle-card-content">
              <span className="toggle-title">🐾 Animal-Derived Additives</span>
              <span className="toggle-sub">Flags Gelatin (INS 428), Carmine Cochineal (INS 120), Shellac (INS 904).</span>
            </div>
            <div className="toggle-switch-ui" />
          </label>
        </div>
      </div>

      {/* 3. Known Allergens & Intolerances */}
      <div className="preference-block">
        <label className="preference-block-title">Allergen Sensitivity Alerts</label>
        <p className="preference-block-sub">
          Select any allergens you want prominently flagged on every scanned label:
        </p>

        <div className="allergens-pill-grid">
          {ALLERGEN_OPTIONS.map((alg) => {
            const isSelected = selectedAllergens.includes(alg.id);
            return (
              <button
                key={alg.id}
                type="button"
                className={`allergen-pill ${isSelected ? "selected" : ""}`}
                onClick={() => toggleAllergen(alg.id)}
              >
                <span className="allergen-pill-emoji">{alg.icon}</span>
                <span className="allergen-pill-label">{alg.label}</span>
                <span className="allergen-pill-check">
                  {isSelected ? <Icon name="check" size={14} /> : "+"}
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* 4. Advanced Custom INS Avoidance Section */}
      <div className="preference-block advanced-settings-block">
        <button
          type="button"
          className="advanced-toggle-btn"
          onClick={() => setShowAdvanced(!showAdvanced)}
        >
          <div className="advanced-toggle-left">
            <Icon name="settings" size={16} />
            <span>Advanced: Custom INS / E-Number Codes</span>
          </div>
          <Icon name={showAdvanced ? "chevronUp" : "chevronDown"} size={16} />
        </button>

        {showAdvanced && (
          <div className="advanced-content-body">
            <label className="form-label" htmlFor="custom-ins-input">
              Specific INS Codes to Avoid (comma-separated):
            </label>
            <input
              id="custom-ins-input"
              type="text"
              className="form-input"
              value={customAvoidIns}
              onChange={(e) => {
                setCustomAvoidIns(e.target.value);
                setSelectedPreset("custom");
              }}
              placeholder="e.g. INS 102, INS 211, INS 621, E250"
            />
            <p className="helper-hint">
              Enter INS or E-number codes to generate tailored preference alerts during packaging analysis.
            </p>
          </div>
        )}
      </div>

      {/* Bottom Sticky Action Bar */}
      <div className="preferences-action-bar">
        <div className="action-bar-info">
          <span>Active Preset: <strong>{selectedPreset.replace("_", " ").toUpperCase()}</strong></span>
          <span>•</span>
          <span>{selectedAllergens.length} allergen{selectedAllergens.length === 1 ? "" : "s"} tracked</span>
        </div>

        <button
          type="button"
          className="btn btn-primary btn-large"
          onClick={handleSavePreferences}
          disabled={saving}
        >
          {saving ? (
            <>
              <div className="btn-spinner" />
              <span>Saving Preferences...</span>
            </>
          ) : (
            <>
              <span>Save & Proceed to Scan Product</span>
              <Icon name="arrowRight" size={18} />
            </>
          )}
        </button>
      </div>
    </div>
  );
}

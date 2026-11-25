import React, { useState, useEffect } from "react";
import { updateDietaryProfile } from "../api";
import Icon from "./Icons";
import { SUPPORTED_ALLERGENS } from "./AllergySelectionView";

const PRESET_CARDS = [
  {
    key: "clean_label",
    title: "Clean Eating",
    subtitle: "Zero synthetic dyes, preservatives & artificial sweeteners",
    icon: "leaf"
  },
  {
    key: "vegan",
    title: "Strict Vegan",
    subtitle: "Avoids all animal-derived ingredients",
    icon: "heart"
  },
  {
    key: "vegetarian",
    title: "Vegetarian",
    subtitle: "Avoids animal fats and animal-derived additives",
    icon: "sparkles"
  },
  {
    key: "child_safe",
    title: "Low Additive",
    subtitle: "Limits synthetic additives & artificial sweeteners",
    icon: "shieldCheck"
  },
  {
    key: "custom",
    title: "Custom Profile",
    subtitle: "Tailor your exact avoided additives and chemical codes",
    icon: "sliders"
  }
];

export default function DietaryPreferencesView({
  currentProfile,
  onProfileSaved,
  onProceedToScan,
  onBackToAllergies,
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
        setStatusMessage({ text: "Preferences saved to your profile.", type: "success" });
        if (onProfileSaved && res.dietary_profile) {
          onProfileSaved(res.dietary_profile);
        }
      } else {
        setStatusMessage({ text: "Preferences active for this session.", type: "success" });
        if (onProfileSaved) {
          onProfileSaved(payload);
        }
      }

      setTimeout(() => {
        if (onProceedToScan) onProceedToScan();
      }, 400);
    } catch (err) {
      console.error("Save preferences failed:", err);
      if (onProfileSaved) onProfileSaved(payload);
      if (onProceedToScan) onProceedToScan();
    } finally {
      setSaving(false);
    }
  };

  const activeCategoriesCount = [
    avoidColors,
    avoidPreserv,
    avoidSweeteners,
    avoidMsg,
    avoidAnimal
  ].filter(Boolean).length;

  return (
    <div className="clinical-page-container">
      {/* Page Header */}
      <div className="clinical-page-header">
        <h1 className="clinical-title">Dietary Preferences</h1>
        <p className="clinical-description">
          Choose a lifestyle preset or configure which additive categories to avoid.
        </p>
      </div>

      {statusMessage.text && (
        <div className={`alert-banner alert-${statusMessage.type === "success" ? "success" : "warning"}`} style={{ marginBottom: "1.5rem" }}>
          <Icon name={statusMessage.type === "success" ? "checkCircle" : "alertTriangle"} size={18} />
          <span>{statusMessage.text}</span>
        </div>
      )}

      {/* SECTION 1: LIFESTYLE PRESETS */}
      <div className="card clinical-section-card">
        <div className="section-card-header">
          <div className="header-icon-box">
            <Icon name="leaf" size={18} color="#00454A" />
          </div>
          <div>
            <h2 className="section-heading">Lifestyle Presets</h2>
            <p className="section-subtext">Select a standard profile to automatically configure ingredient avoidances.</p>
          </div>
        </div>

        <div className="preset-cards-grid">
          {PRESET_CARDS.map((card) => {
            const isSelected = selectedPreset === card.key;
            return (
              <div
                key={card.key}
                role="button"
                tabIndex={0}
                className={`preset-card ${isSelected ? "selected" : ""}`}
                onClick={() => handlePresetSelect(card.key)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    handlePresetSelect(card.key);
                  }
                }}
                aria-pressed={isSelected}
              >
                <div className="preset-card-top">
                  <div className="preset-card-icon">
                    <Icon name={card.icon} size={20} color={isSelected ? "#00454A" : "#777C70"} />
                  </div>
                  <div className={`preset-radio-indicator ${isSelected ? "checked" : ""}`}>
                    {isSelected && <Icon name="check" size={14} strokeWidth={3} color="#00454A" />}
                  </div>
                </div>
                <h3 className="preset-card-title">{card.title}</h3>
                <p className="preset-card-desc">{card.subtitle}</p>
              </div>
            );
          })}
        </div>
      </div>

      {/* SECTION 2: ADDITIVE CATEGORIES TO AVOID */}
      <div className="card clinical-section-card">
        <div className="section-card-header">
          <div className="header-icon-box">
            <Icon name="sliders" size={18} color="#00454A" />
          </div>
          <div>
            <h2 className="section-heading">Additives to Avoid</h2>
            <p className="section-subtext">Toggle functional additive categories to flag during analysis:</p>
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
              <span className="toggle-title">Synthetic / Artificial Colours</span>
              <span className="toggle-sub">Avoid artificial food dyes and synthetic colorants.</span>
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
              <span className="toggle-title">Chemical Preservatives</span>
              <span className="toggle-sub">Avoid chemical shelf-life extenders and preservatives.</span>
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
              <span className="toggle-title">Non-Nutritive Sweeteners</span>
              <span className="toggle-sub">Avoid artificial, low-calorie, and intense sweeteners.</span>
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
              <span className="toggle-title">Flavour Enhancers & MSG</span>
              <span className="toggle-sub">Avoid added MSG and synthetic flavour enhancers.</span>
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
              <span className="toggle-title">Animal-Derived Additives</span>
              <span className="toggle-sub">Avoid gelatin, carmine, shellac, and animal derivatives.</span>
            </div>
            <div className="toggle-switch-ui" />
          </label>
        </div>
      </div>

      {/* SECTION 3: FOOD ALLERGIES SUMMARY */}
      <div className="card clinical-section-card">
        <div className="section-card-header justify-between">
          <div className="flex-row items-center gap-md">
            <div className="header-icon-box">
              <Icon name="shieldAlert" size={18} color="#00454A" />
            </div>
            <div>
              <h2 className="section-heading">Food Allergies</h2>
              <p className="section-subtext">Selected food sensitivities that trigger priority alerts.</p>
            </div>
          </div>
          {onBackToAllergies && (
            <button
              type="button"
              className="btn btn-outline btn-sm"
              onClick={onBackToAllergies}
            >
              <Icon name="sliders" size={14} />
              <span>Edit Allergies</span>
            </button>
          )}
        </div>

        {selectedAllergens.length === 0 ? (
          <div style={{ padding: "0.25rem 0", display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.85rem", color: "var(--text-secondary)" }}>
            <span>No food allergens selected.</span>
            {onBackToAllergies && (
              <button
                type="button"
                className="btn btn-ghost btn-xs"
                onClick={onBackToAllergies}
                style={{ textDecoration: "underline", color: "var(--dark-accent)", padding: 0 }}
              >
                Add Allergies
              </button>
            )}
          </div>
        ) : (
          <div className="summary-pills-wrap" style={{ marginTop: "0.5rem" }}>
            {selectedAllergens.map((algId) => {
              const item = SUPPORTED_ALLERGENS.find((a) => a.id === algId);
              return (
                <span key={algId} className="allergy-selected-pill static">
                  <span>{item ? `${item.icon} ${item.label}` : algId}</span>
                </span>
              );
            })}
          </div>
        )}
      </div>

      {/* SECTION 4: ADVANCED INS / E-NUMBER SETTINGS (COLLAPSED ACCORDION) */}
      <div className="card clinical-section-card accordion-card">
        <button
          type="button"
          className="clinical-accordion-trigger"
          onClick={() => setShowAdvanced(!showAdvanced)}
          aria-expanded={showAdvanced}
        >
          <div className="accordion-trigger-left">
            <Icon name="settings" size={16} color="#64748B" />
            <span>Advanced: Custom Avoided INS / E-Number Codes</span>
          </div>
          <Icon name={showAdvanced ? "chevronUp" : "chevronDown"} size={16} color="#64748B" />
        </button>

        {showAdvanced && (
          <div className="accordion-expandable-content">
            <label className="form-label" htmlFor="custom-ins-input">
              Specific INS or E-numbers to avoid (comma-separated):
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
              placeholder="e.g. INS 102, INS 211, INS 621, E250, INS 150d"
            />
            <p className="helper-hint">
              Specific additive codes that will trigger personal deductions and caution flags during packaging analysis.
            </p>
          </div>
        )}
      </div>

      {/* Sticky Bottom Navigation Actions */}
      <div className="sticky-action-bar">
        <div className="action-bar-content">
          <button
            type="button"
            className="btn btn-outline"
            onClick={onBackToAllergies}
            disabled={saving}
          >
            <Icon name="arrowLeft" size={16} />
            <span>Back</span>
          </button>

          <div className="action-bar-summary">
            <span className="summary-text">
              Preset: <strong>{selectedPreset.replace("_", " ").toUpperCase()}</strong> • {activeCategoriesCount} categories • {selectedAllergens.length} allergens
            </span>
          </div>

          <button
            type="button"
            className="btn btn-primary"
            onClick={handleSavePreferences}
            disabled={saving}
          >
            {saving ? (
              <span>Saving Preferences...</span>
            ) : (
              <>
                <span>Save Preferences & Continue</span>
                <Icon name="arrowRight" size={16} />
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

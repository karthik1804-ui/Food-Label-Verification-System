import React, { useState, useEffect } from "react";
import { updateDietaryProfile, fetchDietaryPresets } from "../api";

const ALLERGEN_OPTIONS = [
  { id: "peanuts", label: "Peanuts" },
  { id: "tree_nuts", label: "Tree Nuts (Almonds, Cashews, Walnuts, etc.)" },
  { id: "dairy", label: "Dairy / Milk" },
  { id: "gluten", label: "Gluten / Wheat" },
  { id: "soy", label: "Soy / Soybean" },
  { id: "egg", label: "Eggs" },
  { id: "fish", label: "Fish" },
  { id: "shellfish", label: "Crustaceans / Shellfish" },
  { id: "sesame", label: "Sesame" },
  { id: "sulfites", label: "Sulfites / Sulphur Dioxide" },
  { id: "mustard", label: "Mustard" },
];

export default function DietaryProfileModal({ isOpen, onClose, currentProfile, onProfileSaved }) {
  const [presets, setPresets] = useState({});
  const [selectedPreset, setSelectedPreset] = useState("custom");
  const [avoidColors, setAvoidColors] = useState(false);
  const [avoidPreserv, setAvoidPreserv] = useState(false);
  const [avoidSweeteners, setAvoidSweeteners] = useState(false);
  const [avoidMsg, setAvoidMsg] = useState(false);
  const [avoidAnimal, setAvoidAnimal] = useState(false);
  const [selectedAllergens, setSelectedAllergens] = useState([]);
  const [customAvoidIns, setCustomAvoidIns] = useState("");
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState("");

  useEffect(() => {
    fetchDietaryPresets()
      .then((data) => setPresets(data.presets || {}))
      .catch((err) => console.error("Could not load presets", err));
  }, []);

  useEffect(() => {
    if (currentProfile) {
      setSelectedPreset(currentProfile.preset_name || "custom");
      setAvoidColors(Boolean(currentProfile.avoid_synthetic_colors));
      setAvoidPreserv(Boolean(currentProfile.avoid_preservatives));
      setAvoidSweeteners(Boolean(currentProfile.avoid_artificial_sweeteners));
      setAvoidMsg(Boolean(currentProfile.avoid_msg_flavor_enhancers));
      setAvoidAnimal(Boolean(currentProfile.avoid_animal_derivatives));
      setSelectedAllergens(currentProfile.custom_allergens || []);
      setCustomAvoidIns((currentProfile.custom_avoid_ins || []).join(", "));
    }
  }, [currentProfile, isOpen]);

  if (!isOpen) return null;

  const handlePresetChange = (presetKey) => {
    setSelectedPreset(presetKey);
    if (presetKey === "custom" || !presets[presetKey]) return;

    const p = presets[presetKey];
    setAvoidColors(Boolean(p.avoid_synthetic_colors));
    setAvoidPreserv(Boolean(p.avoid_preservatives));
    setAvoidSweeteners(Boolean(p.avoid_artificial_sweeteners));
    setAvoidMsg(Boolean(p.avoid_msg_flavor_enhancers));
    setAvoidAnimal(Boolean(p.avoid_animal_derivatives));
    setSelectedAllergens(p.custom_allergens || []);
    setCustomAvoidIns((p.custom_avoid_ins || []).join(", "));
  };

  const toggleAllergen = (id) => {
    if (selectedAllergens.includes(id)) {
      setSelectedAllergens(selectedAllergens.filter((a) => a !== id));
    } else {
      setSelectedAllergens([...selectedAllergens, id]);
    }
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setSaving(true);
    setMessage("");

    const avoidList = customAvoidIns
      .split(",")
      .map((s) => s.trim().toUpperCase())
      .filter((s) => s.length > 0);

    const payload = {
      preset_name: selectedPreset,
      custom_override: true, // Preserve specific toggle states
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
      const res = await updateDietaryProfile(payload);
      setMessage("Preferences saved successfully!");
      if (onProfileSaved && res.dietary_profile) {
        onProfileSaved(res.dietary_profile);
      }
      setTimeout(() => {
        onClose();
        setMessage("");
      }, 700);
    } catch (err) {
      setMessage("Error saving preferences: " + (err.message || "Network error"));
    } finally {
      setSaving(false);
    }
  };

  return (
    <div style={overlayStyle}>
      <div style={modalStyle}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.25rem", color: "#1e293b" }}>Personal Dietary Preferences</h2>
            <p style={{ margin: "0.25rem 0 0 0", fontSize: "0.85rem", color: "#64748b" }}>
              Configure your individual dietary restrictions, allergens, and additive avoidance targets.
            </p>
          </div>
          <button onClick={onClose} style={closeButtonStyle}>×</button>
        </div>

        {message && (
          <div style={{
            padding: "0.6rem 0.8rem",
            borderRadius: "6px",
            marginBottom: "1rem",
            fontSize: "0.85rem",
            backgroundColor: message.includes("Error") ? "#fef2f2" : "#f0fdf4",
            color: message.includes("Error") ? "#b91c1c" : "#166534"
          }}>
            {message}
          </div>
        )}

        <form onSubmit={handleSave} style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
          {/* Preset Selector */}
          <div>
            <label style={labelStyle}>Quick Preset</label>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", marginTop: "0.35rem" }}>
              {["custom", "clean_label", "vegan", "vegetarian", "low_sodium", "child_safe"].map((pKey) => (
                <button
                  key={pKey}
                  type="button"
                  onClick={() => handlePresetChange(pKey)}
                  style={{
                    padding: "0.4rem 0.75rem",
                    borderRadius: "6px",
                    border: selectedPreset === pKey ? "2px solid #2563eb" : "1px solid #cbd5e1",
                    backgroundColor: selectedPreset === pKey ? "#eff6ff" : "#ffffff",
                    color: selectedPreset === pKey ? "#1e40af" : "#334155",
                    fontSize: "0.8rem",
                    fontWeight: 600,
                    cursor: "pointer",
                    textTransform: "capitalize"
                  }}
                >
                  {pKey.replace("_", " ")}
                </button>
              ))}
            </div>
          </div>

          {/* Category Toggles */}
          <div>
            <label style={labelStyle}>Additive Categories to Avoid</label>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem", marginTop: "0.4rem" }}>
              <label style={checkboxLabelStyle}>
                <input type="checkbox" checked={avoidColors} onChange={(e) => setAvoidColors(e.target.checked)} />
                Avoid Synthetic Colors
              </label>
              <label style={checkboxLabelStyle}>
                <input type="checkbox" checked={avoidPreserv} onChange={(e) => setAvoidPreserv(e.target.checked)} />
                Avoid Preservatives
              </label>
              <label style={checkboxLabelStyle}>
                <input type="checkbox" checked={avoidSweeteners} onChange={(e) => setAvoidSweeteners(e.target.checked)} />
                Avoid Artificial Sweeteners
              </label>
              <label style={checkboxLabelStyle}>
                <input type="checkbox" checked={avoidMsg} onChange={(e) => setAvoidMsg(e.target.checked)} />
                Avoid MSG / Flavor Enhancers
              </label>
              <label style={checkboxLabelStyle}>
                <input type="checkbox" checked={avoidAnimal} onChange={(e) => setAvoidAnimal(e.target.checked)} />
                Avoid Animal Derivatives
              </label>
            </div>
          </div>

          {/* Allergens Checklist */}
          <div>
            <label style={labelStyle}>Known Allergies & Intolerances</label>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.4rem", marginTop: "0.4rem" }}>
              {ALLERGEN_OPTIONS.map((alg) => {
                const isSelected = selectedAllergens.includes(alg.id);
                return (
                  <button
                    key={alg.id}
                    type="button"
                    onClick={() => toggleAllergen(alg.id)}
                    style={{
                      padding: "0.3rem 0.6rem",
                      borderRadius: "16px",
                      border: isSelected ? "1.5px solid #dc2626" : "1px solid #cbd5e1",
                      backgroundColor: isSelected ? "#fef2f2" : "#f8fafc",
                      color: isSelected ? "#b91c1c" : "#475569",
                      fontSize: "0.78rem",
                      cursor: "pointer",
                      fontWeight: isSelected ? 600 : 400
                    }}
                  >
                    {isSelected ? "✕ " : "+ "}
                    {alg.label}
                  </button>
                );
              })}
            </div>
          </div>

          {/* Custom Avoid INS Codes */}
          <div>
            <label style={labelStyle}>Specific INS / E-Numbers to Avoid (comma-separated)</label>
            <input
              type="text"
              value={customAvoidIns}
              onChange={(e) => setCustomAvoidIns(e.target.value)}
              placeholder="e.g. INS 250, INS 102, INS 621"
              style={{
                width: "100%",
                padding: "0.5rem 0.75rem",
                border: "1px solid #cbd5e1",
                borderRadius: "6px",
                fontSize: "0.85rem",
                boxSizing: "border-box"
              }}
            />
          </div>

          {/* Save Button */}
          <div style={{ display: "flex", justifyContent: "flex-end", gap: "0.75rem" }}>
            <button type="button" onClick={onClose} style={cancelButtonStyle}>Cancel</button>
            <button type="submit" disabled={saving} style={saveButtonStyle}>
              {saving ? "Saving..." : "Save Dietary Profile"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

const overlayStyle = {
  position: "fixed",
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  backgroundColor: "rgba(15, 23, 42, 0.6)",
  display: "flex",
  justifyContent: "center",
  alignItems: "center",
  zIndex: 1000,
  padding: "1rem"
};

const modalStyle = {
  backgroundColor: "#ffffff",
  borderRadius: "12px",
  padding: "1.75rem",
  width: "100%",
  maxWidth: "600px",
  maxHeight: "90vh",
  overflowY: "auto",
  boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)"
};

const closeButtonStyle = {
  background: "none",
  border: "none",
  fontSize: "1.5rem",
  color: "#64748b",
  cursor: "pointer"
};

const labelStyle = {
  display: "block",
  fontSize: "0.85rem",
  fontWeight: 700,
  color: "#334155",
  marginBottom: "0.25rem"
};

const checkboxLabelStyle = {
  display: "flex",
  alignItems: "center",
  gap: "0.4rem",
  fontSize: "0.82rem",
  color: "#334155",
  cursor: "pointer"
};

const cancelButtonStyle = {
  padding: "0.6rem 1rem",
  backgroundColor: "#f1f5f9",
  color: "#475569",
  border: "1px solid #cbd5e1",
  borderRadius: "6px",
  fontWeight: 600,
  cursor: "pointer"
};

const saveButtonStyle = {
  padding: "0.6rem 1.25rem",
  backgroundColor: "#2563eb",
  color: "#ffffff",
  border: "none",
  borderRadius: "6px",
  fontWeight: 600,
  cursor: "pointer"
};

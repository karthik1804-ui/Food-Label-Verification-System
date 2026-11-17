import React, { useState, useEffect } from "react";
import { updateDietaryProfile } from "../api";
import Icon from "./Icons";

export const SUPPORTED_ALLERGENS = [
  {
    id: "peanuts",
    label: "Peanuts",
    sublabel: "Arachis hypogaea & peanut proteins",
    icon: "🥜",
    category: "Legumes"
  },
  {
    id: "tree_nuts",
    label: "Tree Nuts",
    sublabel: "Almonds, cashews, walnuts, hazelnuts, pistachios",
    icon: "🌰",
    category: "Nuts"
  },
  {
    id: "dairy",
    label: "Dairy / Milk",
    sublabel: "Casein, whey, lactose, milk solids, butter",
    icon: "🥛",
    category: "Animal Dairy"
  },
  {
    id: "gluten",
    label: "Gluten / Wheat",
    sublabel: "Wheat flour, maida, barley, rye, spelt, malt",
    icon: "🌾",
    category: "Cereals"
  },
  {
    id: "soy",
    label: "Soy / Soybeans",
    sublabel: "Soy lecithin, soya protein, edamame, tofu",
    icon: "🌱",
    category: "Legumes"
  },
  {
    id: "egg",
    label: "Eggs",
    sublabel: "Egg whites, yolk, albumin, ovalbumin, lysozyme",
    icon: "🥚",
    category: "Poultry"
  },
  {
    id: "fish",
    label: "Fish",
    sublabel: "Cod, salmon, tuna, anchovy, gelatin (fish)",
    icon: "🐟",
    category: "Marine"
  },
  {
    id: "shellfish",
    label: "Crustaceans / Shellfish",
    sublabel: "Crab, prawns, shrimp, lobster, oysters, clams",
    icon: "🦐",
    category: "Marine"
  },
  {
    id: "sesame",
    label: "Sesame",
    sublabel: "Sesame seeds, tahini, til, gingelly oil",
    icon: "🥯",
    category: "Seeds"
  },
  {
    id: "sulfites",
    label: "Sulphites / Sulfur Dioxide",
    sublabel: "Preservatives INS 220–228, metabisulphites",
    icon: "🍷",
    category: "Preservatives"
  },
  {
    id: "mustard",
    label: "Mustard",
    sublabel: "Mustard seeds, mustard powder, mustard oil",
    icon: "🌭",
    category: "Spices"
  }
];

export default function AllergySelectionView({
  currentProfile,
  onProfileUpdated,
  onContinue,
  onBack,
  currentUser
}) {
  const [selectedAllergens, setSelectedAllergens] = useState([]);
  const [saving, setSaving] = useState(false);

  // Sync state from active profile
  useEffect(() => {
    if (currentProfile && Array.isArray(currentProfile.custom_allergens)) {
      setSelectedAllergens(currentProfile.custom_allergens);
    }
  }, [currentProfile]);

  const toggleAllergen = (allergenId) => {
    setSelectedAllergens((prev) => {
      if (prev.includes(allergenId)) {
        return prev.filter((id) => id !== allergenId);
      } else {
        return [...prev, allergenId];
      }
    });
  };

  const handleSelectAllCommon = () => {
    // Big 8 Common Allergens
    const big8 = ["peanuts", "tree_nuts", "dairy", "gluten", "soy", "egg", "fish", "shellfish"];
    setSelectedAllergens(big8);
  };

  const handleClearAll = () => {
    setSelectedAllergens([]);
  };

  const handleSaveAndContinue = async () => {
    setSaving(true);
    try {
      // Build updated profile object preserving other preferences
      const updatedData = {
        ...(currentProfile || {}),
        custom_allergens: selectedAllergens,
        custom_override: true
      };

      if (currentUser) {
        const saved = await updateDietaryProfile(updatedData);
        if (onProfileUpdated) onProfileUpdated(saved.profile || updatedData);
      } else {
        // Guest mode in-memory update
        if (onProfileUpdated) onProfileUpdated(updatedData);
      }
      onContinue();
    } catch (err) {
      console.error("Failed to save allergy preferences:", err);
      // Fallback: continue in-memory
      if (onProfileUpdated) {
        onProfileUpdated({
          ...(currentProfile || {}),
          custom_allergens: selectedAllergens,
          custom_override: true
        });
      }
      onContinue();
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="clinical-page-container">
      {/* Page Header */}
      <div className="clinical-page-header">
        <span className="clinical-kicker">Step 2 • Safety Profile</span>
        <h1 className="clinical-title">Select Your Food Allergies</h1>
        <p className="clinical-description">
          Choose the food items you want to avoid. We will highlight matching allergens during product analysis.
        </p>
      </div>

      {/* Quick Filter & Counter Toolbar */}
      <div className="card clinical-toolbar-card">
        <div className="toolbar-left">
          <div className="allergen-count-badge">
            <Icon name="shieldAlert" size={18} color="#00454A" />
            <span>
              <strong>{selectedAllergens.length}</strong> {selectedAllergens.length === 1 ? "allergen" : "allergens"} configured
            </span>
          </div>
          {selectedAllergens.length === 0 && (
            <span className="toolbar-hint">No allergens active. Select items below if you have food sensitivities.</span>
          )}
        </div>

        <div className="toolbar-right">
          <button
            type="button"
            className="btn btn-ghost btn-sm"
            onClick={handleSelectAllCommon}
            title="Select standard top 8 common allergens"
          >
            Select Top 8 Common
          </button>
          {selectedAllergens.length > 0 && (
            <button
              type="button"
              className="btn btn-ghost btn-sm text-muted"
              onClick={handleClearAll}
              title="Clear all selected allergens"
            >
              Clear All
            </button>
          )}
        </div>
      </div>

      {/* Allergen Interactive Cards Grid */}
      <div className="allergy-selection-grid">
        {SUPPORTED_ALLERGENS.map((item) => {
          const isSelected = selectedAllergens.includes(item.id);

          return (
            <div
              key={item.id}
              role="button"
              tabIndex={0}
              className={`allergy-card ${isSelected ? "selected" : ""}`}
              onClick={() => toggleAllergen(item.id)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  toggleAllergen(item.id);
                }
              }}
              aria-pressed={isSelected}
            >
              <div className="allergy-card-header">
                <div className="allergy-icon-box">
                  <span className="allergy-emoji">{item.icon}</span>
                </div>
                <div className={`allergy-check-circle ${isSelected ? "checked" : ""}`}>
                  {isSelected && <Icon name="check" size={14} strokeWidth={3} color="#ffffff" />}
                </div>
              </div>

              <div className="allergy-card-body">
                <h3 className="allergy-name">{item.label}</h3>
                <p className="allergy-desc">{item.sublabel}</p>
              </div>

              <div className="allergy-card-footer">
                <span className="allergy-category-tag">{item.category}</span>
                <span className={`allergy-status-indicator ${isSelected ? "active" : ""}`}>
                  {isSelected ? "Avoided" : "Permitted"}
                </span>
              </div>
            </div>
          );
        })}
      </div>

      {/* Selected Allergens Summary Bar */}
      {selectedAllergens.length > 0 && (
        <div className="card clinical-selection-summary-card">
          <div className="summary-card-header">
            <Icon name="checkCircle" size={18} color="#00454A" />
            <span>Active Allergen Warning Triggers:</span>
          </div>
          <div className="summary-pills-wrap">
            {selectedAllergens.map((allergenId) => {
              const item = SUPPORTED_ALLERGENS.find((a) => a.id === allergenId);
              return (
                <span key={allergenId} className="allergy-selected-pill">
                  <span>{item ? `${item.icon} ${item.label}` : allergenId}</span>
                  <button
                    type="button"
                    className="pill-remove-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      toggleAllergen(allergenId);
                    }}
                    title={`Remove ${item?.label || allergenId}`}
                  >
                    <Icon name="x" size={12} />
                  </button>
                </span>
              );
            })}
          </div>
        </div>
      )}

      {/* Sticky Bottom Navigation Actions */}
      <div className="sticky-action-bar">
        <div className="action-bar-content">
          <button
            type="button"
            className="btn btn-outline"
            onClick={onBack}
            disabled={saving}
          >
            <Icon name="arrowLeft" size={16} />
            <span>Back</span>
          </button>

          <div className="action-bar-summary">
            <span className="summary-text">
              {selectedAllergens.length} {selectedAllergens.length === 1 ? "allergen" : "allergens"} configured
            </span>
          </div>

          <button
            type="button"
            className="btn btn-primary"
            onClick={handleSaveAndContinue}
            disabled={saving}
          >
            <span>{saving ? "Saving..." : "Continue to Dietary Preferences"}</span>
            <Icon name="arrowRight" size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}

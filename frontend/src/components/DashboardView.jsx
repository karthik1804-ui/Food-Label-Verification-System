import React, { useState, useEffect } from "react";
import { fetchUserHistory } from "../api";
import Icon from "./Icons";

export default function DashboardView({
  currentUser,
  dietaryProfile,
  onNavigateScan,
  onNavigateAllergies,
  onNavigatePreferences,
  onNavigateHistory,
  onOpenAudit,
  onSelectScanRecord
}) {
  const [recentScans, setRecentScans] = useState([]);
  const [loadingScans, setLoadingScans] = useState(false);

  useEffect(() => {
    let isMounted = true;
    setLoadingScans(true);
    fetchUserHistory(5, 0)
      .then((data) => {
        if (isMounted) {
          setRecentScans(data.history || []);
        }
      })
      .catch((err) => {
        console.warn("Failed to load recent dashboard scans:", err);
      })
      .finally(() => {
        if (isMounted) setLoadingScans(false);
      });
    return () => {
      isMounted = false;
    };
  }, []);

  const presetName = dietaryProfile?.preset_name
    ? dietaryProfile.preset_name.replace("_", " ").toUpperCase()
    : "CLEAN LABEL";

  const allergenCount = dietaryProfile?.custom_allergens?.length || 0;

  const additiveCategoriesCount = [
    dietaryProfile?.avoid_synthetic_colors,
    dietaryProfile?.avoid_preservatives,
    dietaryProfile?.avoid_artificial_sweeteners,
    dietaryProfile?.avoid_msg_flavor_enhancers,
    dietaryProfile?.avoid_animal_derivatives
  ].filter(Boolean).length;

  const formatDate = (isoStr) => {
    if (!isoStr) return "";
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric"
      });
    } catch {
      return isoStr;
    }
  };

  return (
    <div className="clinical-page-container">
      {/* Dashboard Top Header */}
      <div className="dashboard-welcome-header">
        <div className="welcome-avatar-circle">
          <Icon name="user" size={26} color="#00454A" />
        </div>
        <div>
          <h1 className="welcome-title">
            Welcome Back{currentUser ? `, ${currentUser.username}` : ""}
          </h1>
          <p className="welcome-desc">
            Manage your food preferences and scan products.
          </p>
        </div>
      </div>

      {/* DASHBOARD GRID: MAIN SCAN ACTION & DIETARY PROFILE */}
      <div className="dashboard-hero-grid">
        {/* PRIMARY SCAN ACTION (MAIN PROMINENT ELEMENT) */}
        <div className="card dashboard-primary-scan-card">
          <div>
            <h2 className="primary-scan-title">Scan a Food Product</h2>
            <p className="primary-scan-desc">
              Check ingredients against your dietary preferences.
            </p>
          </div>
          <div className="primary-scan-actions">
            <button
              type="button"
              className="btn btn-primary btn-large"
              onClick={onNavigateScan}
            >
              <Icon name="camera" size={18} />
              <span>Scan Product</span>
              <Icon name="arrowRight" size={16} />
            </button>
          </div>
        </div>

        {/* DIETARY PROFILE SUMMARY */}
        <div className="card dashboard-profile-summary-card">
          <div className="summary-card-header">
            <div className="header-icon-box">
              <Icon name="leaf" size={18} color="#00454A" />
            </div>
            <div>
              <h3 className="summary-title">Dietary Profile Summary</h3>
            </div>
          </div>

          <div className="summary-stats-list">
            <div className="stat-row">
              <span className="stat-label">Selected Lifestyle:</span>
              <span className="stat-badge preset-badge">{presetName}</span>
            </div>

            <div className="stat-row">
              <span className="stat-label">Selected Allergens:</span>
              <span className="stat-badge allergen-badge">
                {allergenCount} {allergenCount === 1 ? "allergen" : "allergens"}
              </span>
            </div>

            <div className="stat-row">
              <span className="stat-label">Additive Categories:</span>
              <span className="stat-badge categories-badge">
                {additiveCategoriesCount} {additiveCategoriesCount === 1 ? "category" : "categories"}
              </span>
            </div>
          </div>

          <div className="summary-card-footer">
            <button
              type="button"
              className="btn btn-outline btn-sm btn-block"
              onClick={onNavigatePreferences}
            >
              <Icon name="sliders" size={14} />
              <span>Manage Preferences</span>
            </button>
          </div>
        </div>
      </div>

      {/* RECENT SCANS SECTION (CLEAN & MINIMAL) */}
      <div className="card dashboard-recent-scans-card" style={{ marginTop: "1.5rem" }}>
        <div className="section-card-header justify-between">
          <div className="flex-row items-center gap-md">
            <div className="header-icon-box">
              <Icon name="history" size={18} color="#00454A" />
            </div>
            <div>
              <h3 className="section-heading">Recent Scans</h3>
            </div>
          </div>

          {recentScans.length > 0 && (
            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={onNavigateHistory}
            >
              <span>View All</span>
              <Icon name="chevronRight" size={14} />
            </button>
          )}
        </div>

        {loadingScans ? (
          <div className="empty-subtle-box" style={{ padding: "1.5rem" }}>
            <div className="btn-spinner" />
            <p>Loading recent scans...</p>
          </div>
        ) : recentScans.length === 0 ? (
          <div className="empty-subtle-box" style={{ padding: "1.5rem" }}>
            <p className="text-muted" style={{ margin: 0 }}>
              No recent scans yet. Use "Scan a Food Product" above to evaluate your first product.
            </p>
          </div>
        ) : (
          <div className="recent-scans-list">
            {recentScans.map((item) => {
              const score = item.personal_score !== undefined ? item.personal_score : item.safety_score;
              const hasAllergen = item.has_allergens || (item.allergen_alerts && item.allergen_alerts.length > 0);

              let badgeColor = "#16A34A";
              let badgeText = "Compatible";
              if (hasAllergen) {
                badgeColor = "#DC2626";
                badgeText = "Allergen Alert";
              } else if (score < 70) {
                badgeColor = "#DC2626";
                badgeText = "Conflicts";
              } else if (score < 90) {
                badgeColor = "#F59E0B";
                badgeText = "Caution";
              }

              return (
                <div
                  key={item.id}
                  className="recent-scan-item"
                  onClick={() => onSelectScanRecord && onSelectScanRecord(item)}
                  role="button"
                  tabIndex={0}
                >
                  <div className="recent-item-icon">
                    <Icon name={item.ean ? "barcode" : "camera"} size={16} color="#00454A" />
                  </div>

                  <div className="recent-item-info">
                    <strong className="recent-product-name">{item.product_name}</strong>
                    <span className="recent-scan-date">{formatDate(item.created_at)}</span>
                  </div>

                  <div className="recent-item-score-col">
                    <span className="recent-score-pill" style={{ color: badgeColor, borderColor: `${badgeColor}40` }}>
                      {hasAllergen ? "!" : score}
                    </span>
                    <span className="recent-verdict-label" style={{ color: badgeColor }}>
                      {badgeText}
                    </span>
                  </div>

                  <span className="btn btn-outline btn-xs" style={{ marginLeft: "0.5rem" }}>
                    View Results
                  </span>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

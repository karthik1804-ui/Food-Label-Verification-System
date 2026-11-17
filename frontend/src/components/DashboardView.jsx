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
          <span className="welcome-kicker">Healthcare Verification Portal</span>
          <h1 className="welcome-title">
            Welcome Back, {currentUser ? currentUser.username : "Guest User"}
          </h1>
          <p className="welcome-desc">
            Your personal clinical dietary verification center. Scan food packaging to verify ingredients against your active preferences.
          </p>
        </div>
      </div>

      {/* DASHBOARD GRID: SECTION A & SECTION B */}
      <div className="dashboard-hero-grid">
        {/* SECTION B: PRIMARY SCAN ACTION (MAIN FOCUS) */}
        <div className="card dashboard-primary-scan-card">
          <div className="primary-scan-badge">
            <Icon name="activity" size={14} color="#00454A" />
            <span>Primary Healthcare Action</span>
          </div>
          <h2 className="primary-scan-title">Scan a Food Product</h2>
          <p className="primary-scan-desc">
            Check packaging ingredients or barcodes instantly against your personal allergy triggers and avoided food additives.
          </p>
          <div className="primary-scan-actions">
            <button
              type="button"
              className="btn btn-primary btn-large"
              onClick={onNavigateScan}
            >
              <Icon name="camera" size={18} />
              <span>Launch Product Scanner</span>
              <Icon name="arrowRight" size={16} />
            </button>
          </div>
        </div>

        {/* SECTION A: DIETARY PROFILE SUMMARY */}
        <div className="card dashboard-profile-summary-card">
          <div className="summary-card-header">
            <div className="header-icon-box">
              <Icon name="leaf" size={18} color="#00454A" />
            </div>
            <div>
              <h3 className="summary-title">Dietary Profile Summary</h3>
              <span className="summary-subtitle">Active verification parameters</span>
            </div>
          </div>

          <div className="summary-stats-list">
            <div className="stat-row">
              <span className="stat-label">Active Lifestyle Preset:</span>
              <span className="stat-badge preset-badge">{presetName}</span>
            </div>

            <div className="stat-row">
              <span className="stat-label">Configured Allergens:</span>
              <span className="stat-badge allergen-badge">
                {allergenCount} {allergenCount === 1 ? "trigger" : "triggers"}
              </span>
            </div>

            <div className="stat-row">
              <span className="stat-label">Avoided Additive Classes:</span>
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

      {/* SECTION C: RECENT SCANS & SECTION D: QUICK ACTIONS */}
      <div className="dashboard-secondary-grid">
        {/* SECTION C: RECENT SCANS */}
        <div className="card dashboard-recent-scans-card">
          <div className="section-card-header justify-between">
            <div className="flex-row items-center gap-md">
              <div className="header-icon-box">
                <Icon name="history" size={18} color="#00454A" />
              </div>
              <div>
                <h3 className="section-heading">Recent Product Analyses</h3>
                <p className="section-subtext">Last evaluated food items</p>
              </div>
            </div>

            <button
              type="button"
              className="btn btn-ghost btn-sm"
              onClick={onNavigateHistory}
            >
              <span>View All History</span>
              <Icon name="chevronRight" size={14} />
            </button>
          </div>

          {loadingScans ? (
            <div className="empty-subtle-box">
              <div className="btn-spinner" />
              <p>Loading recent scans...</p>
            </div>
          ) : recentScans.length === 0 ? (
            <div className="empty-subtle-box">
              <span style={{ fontSize: "1.75rem" }}>📦</span>
              <h4>No scans recorded yet</h4>
              <p>Scan your first food packaging label or enter a barcode to build your clinical history.</p>
              <button
                type="button"
                className="btn btn-primary btn-sm"
                onClick={onNavigateScan}
                style={{ marginTop: "0.5rem" }}
              >
                Scan Product Now
              </button>
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

                    <Icon name="chevronRight" size={16} color="#94A3B8" />
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* SECTION D: QUICK ACTIONS */}
        <div className="card dashboard-quick-actions-card">
          <div className="section-card-header">
            <div className="header-icon-box">
              <Icon name="sparkles" size={18} color="#00454A" />
            </div>
            <div>
              <h3 className="section-heading">Quick Shortcuts</h3>
              <p className="section-subtext">Immediate actions</p>
            </div>
          </div>

          <div className="quick-actions-grid">
            <button
              type="button"
              className="quick-action-btn"
              onClick={onNavigateScan}
            >
              <div className="action-btn-icon">
                <Icon name="camera" size={18} color="#00454A" />
              </div>
              <div className="action-btn-text">
                <strong>Scan Packaging</strong>
                <span>Camera OCR or Barcode</span>
              </div>
            </button>

            <button
              type="button"
              className="quick-action-btn"
              onClick={onNavigateAllergies}
            >
              <div className="action-btn-icon">
                <Icon name="shieldAlert" size={18} color="#00454A" />
              </div>
              <div className="action-btn-text">
                <strong>Food Allergies</strong>
                <span>Configure 11 allergens</span>
              </div>
            </button>

            <button
              type="button"
              className="quick-action-btn"
              onClick={onNavigatePreferences}
            >
              <div className="action-btn-icon">
                <Icon name="sliders" size={18} color="#00454A" />
              </div>
              <div className="action-btn-text">
                <strong>Additive Avoidances</strong>
                <span>Preservatives, dyes, MSG</span>
              </div>
            </button>

            <button
              type="button"
              className="quick-action-btn"
              onClick={onOpenAudit}
            >
              <div className="action-btn-icon">
                <Icon name="clipboardList" size={18} color="#00454A" />
              </div>
              <div className="action-btn-text">
                <strong>HITL Audit Queue</strong>
                <span>Review unmapped tokens</span>
              </div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

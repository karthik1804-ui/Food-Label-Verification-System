import React, { useState, useEffect, useCallback } from "react";
import {
  fetchUserHistory,
  deleteHistoryRecord,
  clearUserHistory,
  exportUserHistory
} from "../api";
import Icon from "./Icons";

export default function AnalysisHistoryView({ onSelectScanRecord, onBackToScan, onBackToDashboard }) {
  const [history, setHistory] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [verdictFilter, setVerdictFilter] = useState("all");
  const [onlyAllergens, setOnlyAllergens] = useState(false);
  const [page, setPage] = useState(0);
  const pageSize = 10;
  const [actionMessage, setActionMessage] = useState("");

  const loadHistory = useCallback(async (currentPage = page) => {
    setLoading(true);
    setError("");
    try {
      const data = await fetchUserHistory(
        pageSize,
        currentPage * pageSize,
        searchTerm,
        verdictFilter,
        onlyAllergens ? true : null
      );
      setHistory(data.history || []);
      setTotalCount(data.total_count || data.count || 0);
    } catch (err) {
      setError("Failed to load scan history: " + (err.response?.data?.message || err.message || "Network error"));
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, searchTerm, verdictFilter, onlyAllergens]);

  useEffect(() => {
    loadHistory(0);
    setPage(0);
  }, [verdictFilter, onlyAllergens]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(0);
    loadHistory(0);
  };

  const handleDelete = async (recordId, e) => {
    e.stopPropagation();
    if (!window.confirm("Are you sure you want to remove this scan record?")) return;
    try {
      await deleteHistoryRecord(recordId);
      setActionMessage("Scan record removed from history.");
      loadHistory();
    } catch (err) {
      setError("Failed to delete record: " + (err.response?.data?.message || err.message));
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm("Warning: This will permanently delete all scan records for your account. Continue?")) return;
    try {
      const res = await clearUserHistory();
      setActionMessage(res.message || "History cleared successfully.");
      loadHistory(0);
      setPage(0);
    } catch (err) {
      setError("Failed to clear history: " + (err.response?.data?.message || err.message));
    }
  };

  const handleExport = async (format) => {
    try {
      const blob = await exportUserHistory(format);
      const url = window.URL.createObjectURL(new Blob([blob]));
      const link = document.createElement("a");
      link.href = url;
      link.setAttribute("download", `food_verification_history.${format}`);
      document.body.appendChild(link);
      link.click();
      link.parentNode.removeChild(link);
      setActionMessage(`History exported as ${format.toUpperCase()}.`);
    } catch (err) {
      setError("Export failed: " + (err.response?.data?.message || err.message));
    }
  };

  const formatDate = (isoStr) => {
    if (!isoStr) return "";
    try {
      const d = new Date(isoStr);
      return d.toLocaleDateString(undefined, {
        month: "short",
        day: "numeric",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      });
    } catch {
      return isoStr;
    }
  };

  return (
    <div className="clinical-page-container">
      {/* Top Breadcrumb Navigation */}
      <div className="results-top-nav-bar">
        <div className="nav-bar-left">
          {onBackToDashboard && (
            <button
              type="button"
              className="btn btn-outline btn-sm"
              onClick={onBackToDashboard}
            >
              <Icon name="layoutDashboard" size={14} />
              <span>Back to Dashboard</span>
            </button>
          )}
          <button
            type="button"
            className="btn btn-primary btn-sm"
            onClick={onBackToScan}
          >
            <Icon name="camera" size={14} />
            <span>Scan New Product</span>
          </button>
        </div>

        <div className="nav-bar-right">
          <button
            type="button"
            className="btn btn-outline btn-sm"
            onClick={() => handleExport("json")}
            disabled={history.length === 0}
          >
            <Icon name="download" size={14} />
            <span>Export JSON</span>
          </button>
          <button
            type="button"
            className="btn btn-outline btn-sm"
            onClick={() => handleExport("csv")}
            disabled={history.length === 0}
          >
            <Icon name="download" size={14} />
            <span>Export CSV</span>
          </button>
          {history.length > 0 && (
            <button
              type="button"
              className="btn btn-ghost btn-sm text-danger"
              onClick={handleClearAll}
            >
              <Icon name="trash2" size={14} />
              <span>Clear All</span>
            </button>
          )}
        </div>
      </div>

      {/* Page Header */}
      <div className="clinical-page-header">
        <span className="clinical-kicker">Account Records</span>
        <h1 className="clinical-title">Product Scan History</h1>
        <p className="clinical-description">
          Review past packaging analyses, inspect detected food additives, and track your historical dietary compatibility scores.
        </p>
      </div>

      {actionMessage && (
        <div className="alert-banner alert-success" style={{ marginBottom: "1.25rem" }}>
          <Icon name="checkCircle" size={18} />
          <span>{actionMessage}</span>
        </div>
      )}

      {error && (
        <div className="alert-banner alert-danger" style={{ marginBottom: "1.25rem" }}>
          <Icon name="alertCircle" size={18} />
          <span>{error}</span>
        </div>
      )}

      {/* Filter and Search Bar */}
      <div className="card clinical-filter-card">
        <form onSubmit={handleSearchSubmit} className="history-search-form">
          <div className="input-with-icon search-input-wrapper">
            <Icon name="search" size={18} className="input-leading-icon" />
            <input
              type="text"
              className="form-input"
              placeholder="Search by product name, brand, or barcode EAN..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>

          <div className="filter-controls-group">
            <select
              className="form-select"
              value={verdictFilter}
              onChange={(e) => setVerdictFilter(e.target.value)}
            >
              <option value="all">All Verdicts</option>
              <option value="Compatible">Compatible</option>
              <option value="Caution">Caution</option>
              <option value="Conflicts">Conflicts</option>
            </select>

            <label className="checkbox-filter-label">
              <input
                type="checkbox"
                checked={onlyAllergens}
                onChange={(e) => setOnlyAllergens(e.target.checked)}
              />
              <span>Allergen Warnings Only</span>
            </label>

            <button type="submit" className="btn btn-primary btn-sm">
              <Icon name="filter" size={14} />
              <span>Apply Filter</span>
            </button>
          </div>
        </form>
      </div>

      {/* History Items List / Cards */}
      {loading ? (
        <div className="card empty-subtle-box">
          <div className="btn-spinner" />
          <p>Loading your past packaging scans...</p>
        </div>
      ) : history.length === 0 ? (
        <div className="card empty-subtle-box">
          <div className="empty-history-icon">
            <Icon name="history" size={36} color="#94A3B8" />
          </div>
          <h3 style={{ margin: "0.5rem 0" }}>No Past Scans Found</h3>
          <p style={{ color: "#64748B", maxWidth: 440, margin: "0 auto 1rem auto" }}>
            {searchTerm || verdictFilter !== "all" || onlyAllergens
              ? "No scan records match your active search filters. Try clearing your search parameters."
              : "You have not performed any product scans yet. Scan your first food packaging label to get started."}
          </p>
          <button
            type="button"
            className="btn btn-primary"
            onClick={onBackToScan}
          >
            <Icon name="camera" size={16} />
            <span>Scan a Food Product</span>
          </button>
        </div>
      ) : (
        <div className="history-cards-list">
          {history.map((record) => {
            const hasAllergensInRecord = record.allergen_alerts && record.allergen_alerts.length > 0;
            const score = record.personal_score !== undefined ? record.personal_score : record.safety_score;
            const scoreColor = hasAllergensInRecord ? "#DC2626" : score >= 90 ? "#16A34A" : score >= 70 ? "#F59E0B" : "#DC2626";

            return (
              <div
                key={record.id}
                className="card history-item-card"
                onClick={() => onSelectScanRecord && onSelectScanRecord(record)}
                role="button"
                tabIndex={0}
              >
                <div className="history-item-left">
                  <div
                    className="history-score-badge"
                    style={{
                      backgroundColor: `${scoreColor}15`,
                      color: scoreColor,
                      borderColor: `${scoreColor}40`
                    }}
                  >
                    <span className="history-score-num">{hasAllergensInRecord ? "!" : score}</span>
                    <span className="history-score-max">/100</span>
                  </div>

                  <div className="history-item-info">
                    <div className="history-title-row">
                      <h4 className="history-prod-name">{record.product_name || "Food Product Scan"}</h4>
                      {record.brand && <span className="history-brand">{record.brand}</span>}
                    </div>
                    <div className="history-tags-row">
                      <span className="history-date">
                        {formatDate(record.created_at || record.scanned_at)}
                      </span>
                      {record.ean && record.ean !== "N/A" && (
                        <span className="history-ean">EAN: {record.ean}</span>
                      )}
                      {record.preset_name && (
                        <span className="history-preset">
                          {record.preset_name.replace("_", " ")}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="history-item-right">
                  <div className="history-status-group">
                    <span
                      className="history-verdict-pill"
                      style={{
                        backgroundColor: `${scoreColor}15`,
                        color: scoreColor,
                        borderColor: `${scoreColor}30`
                      }}
                    >
                      {record.personal_verdict || "Evaluated"}
                    </span>
                    {hasAllergensInRecord && (
                      <span className="history-allergen-flag">
                        🚨 Allergen Warning
                      </span>
                    )}
                  </div>

                  <button
                    type="button"
                    className="history-delete-btn"
                    onClick={(e) => handleDelete(record.id, e)}
                    title="Delete this record"
                  >
                    <Icon name="trash2" size={16} />
                  </button>
                </div>
              </div>
            );
          })}

          {/* Pagination Controls */}
          {totalCount > pageSize && (
            <div className="history-pagination-bar">
              <button
                type="button"
                className="btn btn-outline btn-sm"
                onClick={() => {
                  const newPage = Math.max(0, page - 1);
                  setPage(newPage);
                  loadHistory(newPage);
                }}
                disabled={page === 0}
              >
                <Icon name="arrowLeft" size={14} />
                <span>Previous</span>
              </button>

              <span className="pagination-info">
                Page {page + 1} of {Math.ceil(totalCount / pageSize)} ({totalCount} total scans)
              </span>

              <button
                type="button"
                className="btn btn-outline btn-sm"
                onClick={() => {
                  const newPage = page + 1;
                  setPage(newPage);
                  loadHistory(newPage);
                }}
                disabled={(page + 1) * pageSize >= totalCount}
              >
                <span>Next</span>
                <Icon name="arrowRight" size={14} />
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

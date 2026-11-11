import React, { useState, useEffect, useCallback } from "react";
import {
  fetchUserHistory,
  deleteHistoryRecord,
  clearUserHistory,
  exportUserHistory
} from "../api";

export default function AnalysisHistoryModal({ isOpen, onClose }) {
  const [history, setHistory] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [verdictFilter, setVerdictFilter] = useState("all");
  const [onlyAllergens, setOnlyAllergens] = useState(false);
  const [page, setPage] = useState(0);
  const pageSize = 10;
  const [selectedRecord, setSelectedRecord] = useState(null);
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
      setError("Failed to load history: " + (err.response?.data?.message || err.message || "Network error"));
    } finally {
      setLoading(false);
    }
  }, [page, pageSize, searchTerm, verdictFilter, onlyAllergens]);

  useEffect(() => {
    if (isOpen) {
      loadHistory(0);
      setPage(0);
      setSelectedRecord(null);
      setActionMessage("");
    }
  }, [isOpen, verdictFilter, onlyAllergens]); // eslint-disable-line react-hooks/exhaustive-deps

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    setPage(0);
    loadHistory(0);
  };

  const handleDelete = async (recordId) => {
    if (!window.confirm("Are you sure you want to delete this scan record?")) return;
    try {
      await deleteHistoryRecord(recordId);
      setActionMessage("Scan record deleted successfully.");
      if (selectedRecord && selectedRecord.id === recordId) {
        setSelectedRecord(null);
      }
      loadHistory();
    } catch (err) {
      setError("Failed to delete record: " + (err.response?.data?.message || err.message));
    }
  };

  const handleClearAll = async () => {
    if (!window.confirm("Warning: This will delete ALL scan history records for your account. Continue?")) return;
    try {
      const res = await clearUserHistory();
      setActionMessage(res.message || "History cleared.");
      setSelectedRecord(null);
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

  if (!isOpen) return null;

  const totalPages = Math.ceil(totalCount / pageSize);

  return (
    <div className="modal-overlay">
      <div className="modal-content glass" style={{ maxWidth: "900px", width: "95%" }}>
        {/* Header */}
        <div className="modal-header">
          <div>
            <h2>📜 Verification Scan History</h2>
            <p className="card-sub">
              Search, filter, inspect, and export past packaging OCR & barcode assessments.
            </p>
          </div>
          <button className="btn-close" onClick={onClose}>&times;</button>
        </div>

        {/* Action feedback / errors */}
        {actionMessage && (
          <div style={{
            padding: "0.6rem 1rem",
            backgroundColor: "rgba(16, 185, 129, 0.15)",
            border: "1px solid rgba(16, 185, 129, 0.3)",
            borderRadius: "6px",
            color: "#a7f3d0",
            fontSize: "0.85rem",
            marginBottom: "0.75rem"
          }}>
            ✓ {actionMessage}
          </div>
        )}
        {error && (
          <div style={{
            padding: "0.6rem 1rem",
            backgroundColor: "rgba(239, 68, 68, 0.15)",
            border: "1px solid rgba(239, 68, 68, 0.3)",
            borderRadius: "6px",
            color: "#fca5a5",
            fontSize: "0.85rem",
            marginBottom: "0.75rem"
          }}>
            ⚠️ {error}
          </div>
        )}

        {/* Toolbar: Search, Filters & Export */}
        <div style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "0.75rem",
          marginBottom: "1rem",
          padding: "0.85rem",
          backgroundColor: "rgba(15, 23, 42, 0.5)",
          borderRadius: "8px",
          border: "1px solid rgba(255, 255, 255, 0.06)"
        }}>
          {/* Search form */}
          <form onSubmit={handleSearchSubmit} style={{ display: "flex", gap: "0.5rem", flex: "1 1 240px" }}>
            <input
              type="text"
              placeholder="Search product, barcode, text..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="barcode-input"
              style={{ fontSize: "0.82rem", padding: "0.4rem 0.75rem" }}
            />
            <button type="submit" className="btn btn-primary" style={{ padding: "0.4rem 0.8rem", fontSize: "0.82rem" }}>
              🔍 Search
            </button>
          </form>

          {/* Filters & Actions */}
          <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
            <select
              value={verdictFilter}
              onChange={(e) => { setVerdictFilter(e.target.value); setPage(0); }}
              className="barcode-input"
              style={{ fontSize: "0.82rem", padding: "0.4rem 0.75rem", width: "auto" }}
            >
              <option value="all">All Verdicts</option>
              <option value="Compatible">Compatible</option>
              <option value="Minor">Minor Caution</option>
              <option value="Conflict">Preference Conflicts</option>
              <option value="ALLERGEN">Allergen Triggers</option>
              <option value="PROVISIONAL">Provisional Scores</option>
            </select>

            <label style={{ display: "flex", alignItems: "center", gap: "0.35rem", fontSize: "0.8rem", color: "#cbd5e1", cursor: "pointer" }}>
              <input
                type="checkbox"
                checked={onlyAllergens}
                onChange={(e) => { setOnlyAllergens(e.target.checked); setPage(0); }}
              />
              Allergens Only
            </label>

            {/* Export buttons */}
            <button
              onClick={() => handleExport("json")}
              className="btn btn-outline"
              style={{ padding: "0.35rem 0.65rem", fontSize: "0.78rem" }}
              title="Export history records as JSON"
            >
              📥 JSON
            </button>
            <button
              onClick={() => handleExport("csv")}
              className="btn btn-outline"
              style={{ padding: "0.35rem 0.65rem", fontSize: "0.78rem" }}
              title="Export history records as CSV"
            >
              📊 CSV
            </button>
          </div>
        </div>

        {/* Modal Body */}
        <div className="modal-body" style={{ maxHeight: "55vh", overflowY: "auto" }}>
          {loading ? (
            <div className="loading-state">
              <div className="spinner" />
              <p>Retrieving scan history records...</p>
            </div>
          ) : history.length === 0 ? (
            <div className="empty-notice">
              <span>📭</span>
              <p>No past scan records found matching your filters.</p>
            </div>
          ) : (
            <div className="table-responsive">
              <table className="additives-table" style={{ fontSize: "0.82rem" }}>
                <thead>
                  <tr>
                    <th>Date & Time</th>
                    <th>Product / Barcode</th>
                    <th>Safety Score</th>
                    <th>Personal Score</th>
                    <th>Allergens</th>
                    <th>Additives</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {history.map((rec) => {
                    const hasAllergens = rec.allergen_alerts && rec.allergen_alerts.length > 0;
                    return (
                      <React.Fragment key={rec.id}>
                        <tr style={{ backgroundColor: selectedRecord?.id === rec.id ? "rgba(99, 102, 241, 0.15)" : "transparent" }}>
                          <td style={{ whiteSpace: "nowrap", color: "#94a3b8" }}>
                            {rec.scanned_at ? rec.scanned_at.slice(0, 16).replace("T", " ") : "N/A"}
                          </td>
                          <td>
                            <div style={{ fontWeight: 600, color: "#f8fafc" }}>{rec.product_name}</div>
                            <div style={{ fontSize: "0.75rem", color: "#94a3b8" }}>
                              {rec.ean && rec.ean !== "N/A" ? `EAN: ${rec.ean}` : "OCR Scan"}
                            </div>
                          </td>
                          <td>
                            <span style={{
                              fontWeight: 700,
                              padding: "0.15rem 0.45rem",
                              borderRadius: "4px",
                              backgroundColor: rec.final_score >= 80 ? "rgba(16, 185, 129, 0.2)" : rec.final_score >= 60 ? "rgba(245, 158, 11, 0.2)" : "rgba(239, 68, 68, 0.2)",
                              color: rec.final_score >= 80 ? "#a7f3d0" : rec.final_score >= 60 ? "#fde68a" : "#fca5a5"
                            }}>
                              {rec.final_score} ({rec.grade})
                            </span>
                          </td>
                          <td>
                            <span style={{
                              fontWeight: 700,
                              padding: "0.15rem 0.45rem",
                              borderRadius: "4px",
                              backgroundColor: rec.personal_score >= 90 ? "rgba(16, 185, 129, 0.2)" : rec.personal_score >= 70 ? "rgba(245, 158, 11, 0.2)" : "rgba(239, 68, 68, 0.2)",
                              color: rec.personal_score >= 90 ? "#a7f3d0" : rec.personal_score >= 70 ? "#fde68a" : "#fca5a5"
                            }}>
                              {rec.personal_score}/100
                            </span>
                            <div style={{ fontSize: "0.72rem", color: "#cbd5e1", marginTop: "0.15rem" }}>
                              {rec.personal_verdict}
                            </div>
                          </td>
                          <td>
                            {hasAllergens ? (
                              <span style={{ color: "#f87171", fontWeight: 700, fontSize: "0.78rem" }}>
                                ⚠️ {rec.allergen_alerts.length} Trigger(s)
                              </span>
                            ) : (
                              <span style={{ color: "#a7f3d0", fontSize: "0.78rem" }}>✓ Clear</span>
                            )}
                          </td>
                          <td>
                            <span style={{ color: "#cbd5e1" }}>
                              {rec.additives_count > 0 ? `${rec.additives_count} found` : "None"}
                            </span>
                          </td>
                          <td>
                            <div style={{ display: "flex", gap: "0.35rem" }}>
                              <button
                                className="btn btn-outline"
                                style={{ padding: "0.2rem 0.45rem", fontSize: "0.72rem" }}
                                onClick={() => setSelectedRecord(selectedRecord?.id === rec.id ? null : rec)}
                              >
                                {selectedRecord?.id === rec.id ? "Hide" : "Inspect"}
                              </button>
                              <button
                                className="btn btn-outline"
                                style={{ padding: "0.2rem 0.45rem", fontSize: "0.72rem", color: "#f87171", borderColor: "#f8717140" }}
                                onClick={() => handleDelete(rec.id)}
                                title="Delete this scan record"
                              >
                                🗑️
                              </button>
                            </div>
                          </td>
                        </tr>

                        {/* Collapsible Details Drawer */}
                        {selectedRecord?.id === rec.id && (
                          <tr>
                            <td colSpan={7} style={{ backgroundColor: "rgba(15, 23, 42, 0.7)", padding: "1rem" }}>
                              <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                                  <h4 style={{ margin: 0, color: "#93c5fd", fontSize: "0.9rem" }}>
                                    🔍 Detailed Scan Record #{rec.id} — {rec.product_name}
                                  </h4>
                                  <span style={{ fontSize: "0.75rem", color: "#94a3b8" }}>
                                    OCR Confidence: {Math.round((rec.ocr_confidence || 1.0) * 100)}%
                                  </span>
                                </div>

                                {rec.raw_text && (
                                  <div>
                                    <span style={{ fontSize: "0.75rem", color: "#94a3b8" }}>RAW LABEL TEXT:</span>
                                    <div style={{
                                      backgroundColor: "rgba(0,0,0,0.4)",
                                      padding: "0.5rem",
                                      borderRadius: "4px",
                                      fontSize: "0.75rem",
                                      color: "#cbd5e1",
                                      maxHeight: "80px",
                                      overflowY: "auto",
                                      marginTop: "0.2rem"
                                    }}>
                                      {rec.raw_text}
                                    </div>
                                  </div>
                                )}

                                {rec.additives && rec.additives.length > 0 && (
                                  <div>
                                    <span style={{ fontSize: "0.75rem", color: "#94a3b8" }}>DETECTED ADDITIVES:</span>
                                    <div style={{ display: "flex", flexWrap: "wrap", gap: "0.3rem", marginTop: "0.2rem" }}>
                                      {rec.additives.map((code, idx) => (
                                        <span key={idx} className="ins-code-pill">
                                          {code}
                                        </span>
                                      ))}
                                    </div>
                                  </div>
                                )}

                                {hasAllergens && (
                                  <div>
                                    <span style={{ fontSize: "0.75rem", color: "#f87171" }}>ALLERGEN DETAILS:</span>
                                    <div style={{ marginTop: "0.2rem", display: "flex", flexDirection: "column", gap: "0.2rem" }}>
                                      {rec.allergen_alerts.map((al, idx) => (
                                        <div key={idx} style={{ fontSize: "0.75rem", color: "#fecaca" }}>
                                          • <strong>{al.allergen}:</strong> Matched token "{al.matched_term}". {al.action_required}
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                )}
                              </div>
                            </td>
                          </tr>
                        )}
                      </React.Fragment>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Footer: Pagination & Actions */}
        <div className="modal-footer" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <span style={{ fontSize: "0.78rem", color: "#94a3b8" }}>
              Total Records: <strong>{totalCount}</strong>
              {totalPages > 1 && ` • Page ${page + 1} of ${totalPages}`}
            </span>
          </div>

          <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
            {history.length > 0 && (
              <button
                className="btn btn-outline"
                style={{ color: "#f87171", borderColor: "#f8717140", fontSize: "0.8rem", padding: "0.35rem 0.65rem" }}
                onClick={handleClearAll}
              >
                Clear All History
              </button>
            )}
            <button
              className="btn btn-secondary"
              disabled={page === 0 || loading}
              onClick={() => { const p = page - 1; setPage(p); loadHistory(p); }}
            >
              ◀ Prev
            </button>
            <button
              className="btn btn-secondary"
              disabled={page >= totalPages - 1 || loading}
              onClick={() => { const p = page + 1; setPage(p); loadHistory(p); }}
            >
              Next ▶
            </button>
            <button className="btn btn-secondary" onClick={onClose}>
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

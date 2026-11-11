import React, { useState, useEffect, useCallback } from "react";
import { fetchAuditQueue, submitAuditReview, fetchAuditStats, deleteAuditRecord } from "../api";

/**
 * AuditQueueModal — v2.5 (Phase 10: HITL Review & Audit Records Management)
 *
 * Full Human-in-the-Loop review and queue management interface:
 *   - Aggregated Queue Statistics (Pending, Confirmed, Corrected, Rejected)
 *   - Status Filter Tabs & In-Memory Quick Search
 *   - Review Actions: Confirm (not an additive), Reject (false positive), Correct (provide INS numbers)
 *   - Record Dismissal/Deletion for obsolete queue records
 */
function AuditQueueModal({ isOpen, onClose }) {
  const [records, setRecords] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(false);
  const [statusFilter, setStatusFilter] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");
  const [reviewingId, setReviewingId] = useState(null);
  const [correctionInput, setCorrectionInput] = useState("");
  const [reviewNote, setReviewNote] = useState("");
  const [feedback, setFeedback] = useState("");

  const loadData = useCallback(async () => {
    setLoading(true);
    setFeedback("");
    try {
      const [queueData, statsData] = await Promise.all([
        fetchAuditQueue(statusFilter !== "all" ? statusFilter : null),
        fetchAuditStats().catch(() => null)
      ]);
      setRecords(queueData.records || []);
      if (statsData) setStats(statsData);
    } catch (err) {
      console.error("Failed to load audit queue:", err);
      setFeedback("Failed to load records. Is the backend running?");
    } finally {
      setLoading(false);
    }
  }, [statusFilter]);

  useEffect(() => {
    if (isOpen) {
      loadData();
      setReviewingId(null);
    }
  }, [isOpen, loadData]);

  const handleReview = async (recordId, action) => {
    const corrected = action === "correct"
      ? correctionInput.split(",").map(s => s.trim()).filter(Boolean)
      : undefined;

    if (action === "correct" && (!corrected || corrected.length === 0)) {
      setFeedback("Please enter the correct INS code(s) before submitting a correction.");
      return;
    }

    try {
      const result = await submitAuditReview(recordId, action, corrected, reviewNote);
      setFeedback(result.message || "Review submitted.");
      setReviewingId(null);
      setCorrectionInput("");
      setReviewNote("");
      await loadData();
    } catch (err) {
      setFeedback(`Failed to submit review: ${err.response?.data?.message || err.message}`);
    }
  };

  const handleDeleteRecord = async (recordId) => {
    if (!window.confirm("Are you sure you want to dismiss this audit record?")) return;
    try {
      await deleteAuditRecord(recordId);
      setFeedback("Audit record deleted.");
      await loadData();
    } catch (err) {
      setFeedback(`Failed to delete record: ${err.response?.data?.message || err.message}`);
    }
  };

  const statusBadgeClass = (status) => {
    if (!status) return "badge-pending";
    if (status.includes("CONFIRMED")) return "badge-valid";
    if (status.includes("REJECTED")) return "badge-invalid";
    if (status.includes("CORRECTED")) return "badge-class";
    return "badge-pending";
  };

  const filteredRecords = records.filter((r) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    const matchContext = (r.context_identifier || "").toLowerCase().includes(q);
    const matchTokens = (r.unmapped_tokens || []).some(t => t.toLowerCase().includes(q));
    const matchNote = (r.review_history || []).some(h => (h.reviewer_note || "").toLowerCase().includes(q));
    return matchContext || matchTokens || matchNote;
  });

  if (!isOpen) return null;

  return (
    <div className="modal-overlay">
      <div className="modal-content glass" style={{ maxWidth: "1000px", width: "95%" }}>
        {/* Header */}
        <div className="modal-header">
          <div>
            <h2>📋 Human-in-the-Loop Audit & Taxonomy Queue</h2>
            <p className="card-sub">
              Review unmapped additive tokens, track reviewer actions, and manage taxonomy verification.
            </p>
          </div>
          <button className="btn-close" onClick={onClose}>&times;</button>
        </div>

        {/* Feedback Banner */}
        {feedback && (
          <div className="audit-feedback-banner" style={{ margin: "0.5rem 0" }}>
            {feedback}
          </div>
        )}

        {/* Audit Queue Summary Statistics Pills */}
        {stats && (
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))",
            gap: "0.5rem",
            marginBottom: "1rem"
          }}>
            <div style={statCardStyle}>
              <span style={statNumberStyle}>{stats.total_records}</span>
              <span style={statLabelStyle}>Total Flagged</span>
            </div>
            <div style={{ ...statCardStyle, borderColor: "rgba(245, 158, 11, 0.4)" }}>
              <span style={{ ...statNumberStyle, color: "#fde68a" }}>{stats.pending_count}</span>
              <span style={statLabelStyle}>Pending Review</span>
            </div>
            <div style={{ ...statCardStyle, borderColor: "rgba(16, 185, 129, 0.4)" }}>
              <span style={{ ...statNumberStyle, color: "#a7f3d0" }}>{stats.confirmed_count}</span>
              <span style={statLabelStyle}>Confirmed Non-Additives</span>
            </div>
            <div style={{ ...statCardStyle, borderColor: "rgba(99, 102, 241, 0.4)" }}>
              <span style={{ ...statNumberStyle, color: "#c7d2fe" }}>{stats.corrected_count}</span>
              <span style={statLabelStyle}>Corrected Mappings</span>
            </div>
            <div style={{ ...statCardStyle, borderColor: "rgba(239, 68, 68, 0.4)" }}>
              <span style={{ ...statNumberStyle, color: "#fca5a5" }}>{stats.rejected_count}</span>
              <span style={statLabelStyle}>False Positives</span>
            </div>
          </div>
        )}

        {/* Status Filter Tabs & Search Bar */}
        <div style={{
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "space-between",
          alignItems: "center",
          gap: "0.75rem",
          marginBottom: "1rem"
        }}>
          {/* Status Tabs */}
          <div className="tab-control-container" style={{ margin: 0, padding: "0.2rem" }}>
            {[
              { id: "all", label: "All Records" },
              { id: "PENDING_EXPERT_REVIEW", label: "Pending" },
              { id: "CONFIRMED_BY_REVIEWER", label: "Confirmed" },
              { id: "CORRECTED_BY_REVIEWER", label: "Corrected" },
              { id: "REJECTED_BY_REVIEWER", label: "Rejected" }
            ].map(tab => (
              <button
                key={tab.id}
                className={`tab-btn ${statusFilter === tab.id ? "active" : ""}`}
                style={{ padding: "0.35rem 0.75rem", fontSize: "0.78rem" }}
                onClick={() => setStatusFilter(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {/* Quick Search */}
          <input
            type="text"
            placeholder="Filter by token or product..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="barcode-input"
            style={{ width: "220px", padding: "0.35rem 0.65rem", fontSize: "0.8rem" }}
          />
        </div>

        {/* Modal Body */}
        <div className="modal-body" style={{ maxHeight: "55vh", overflowY: "auto" }}>
          {loading ? (
            <div className="loading-state">
              <div className="spinner" />
              <p>Loading audit queue...</p>
            </div>
          ) : filteredRecords.length === 0 ? (
            <div className="empty-notice">
              <span>✅</span>
              <p>No audit records found matching your current filter.</p>
            </div>
          ) : (
            <div className="audit-table-container">
              <table className="audit-table">
                <thead>
                  <tr>
                    <th>Timestamp</th>
                    <th>Product / Context</th>
                    <th>Unrecognised Tokens</th>
                    <th>Match Ratio</th>
                    <th>OCR Conf.</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredRecords.map((r) => (
                    <React.Fragment key={r.id || r.timestamp}>
                      <tr>
                        <td style={{ fontSize: "0.75rem", whiteSpace: "nowrap" }}>
                          {r.timestamp ? new Date(r.timestamp).toLocaleString() : "N/A"}
                        </td>
                        <td><strong>{r.context_identifier || "Direct Scan"}</strong></td>
                        <td>
                          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.25rem" }}>
                            {(r.unmapped_tokens || []).map((t, idx) => (
                              <span key={idx} className="badge badge-unmapped">{t}</span>
                            ))}
                          </div>
                          {r.corrected_tokens && r.corrected_tokens.length > 0 && (
                            <div style={{ fontSize: "0.72rem", color: "#93c5fd", marginTop: "0.2rem" }}>
                              Mapped to: <strong>{r.corrected_tokens.join(", ")}</strong>
                            </div>
                          )}
                        </td>
                        <td>
                          {r.additive_match_confidence !== undefined
                            ? `${Math.round(r.additive_match_confidence * 100)}%`
                            : "N/A"}
                        </td>
                        <td>
                          {r.ocr_confidence !== undefined
                            ? `${Math.round(r.ocr_confidence * 100)}%`
                            : "N/A"}
                        </td>
                        <td>
                          <span className={`badge ${statusBadgeClass(r.audit_status)}`}>
                            {r.audit_status?.replace(/_/g, " ") || "Pending"}
                          </span>
                        </td>
                        <td>
                          <div style={{ display: "flex", gap: "0.3rem" }}>
                            {r.audit_status === "PENDING_EXPERT_REVIEW" ? (
                              <button
                                className="btn btn-xs btn-valid"
                                onClick={() => setReviewingId(
                                  reviewingId === r.id ? null : r.id
                                )}
                              >
                                {reviewingId === r.id ? "Cancel" : "Review"}
                              </button>
                            ) : (
                              <button
                                className="btn btn-xs btn-outline"
                                onClick={() => setReviewingId(
                                  reviewingId === r.id ? null : r.id
                                )}
                              >
                                {reviewingId === r.id ? "Close" : "History"}
                              </button>
                            )}
                            <button
                              className="btn btn-xs btn-outline"
                              style={{ color: "#f87171", borderColor: "#f8717140" }}
                              onClick={() => handleDeleteRecord(r.id)}
                              title="Dismiss/delete this audit record"
                            >
                              🗑️
                            </button>
                          </div>
                        </td>
                      </tr>

                      {/* Review or History drawer */}
                      {reviewingId === r.id && (
                        <tr className="review-form-row">
                          <td colSpan={7}>
                            <div className="review-inline-form">
                              <p className="review-form-title">
                                Record #{r.id} • Tokens: <strong>{(r.unmapped_tokens || []).join(", ")}</strong>
                              </p>

                              {/* Show prior review history if available */}
                              {r.review_history && r.review_history.length > 0 && (
                                <div style={{
                                  marginBottom: "0.75rem",
                                  padding: "0.5rem",
                                  backgroundColor: "rgba(0,0,0,0.3)",
                                  borderRadius: "4px",
                                  fontSize: "0.78rem"
                                }}>
                                  <span style={{ color: "#94a3b8" }}>PREVIOUS REVIEW DECISIONS:</span>
                                  {r.review_history.map((h, i) => (
                                    <div key={i} style={{ color: "#cbd5e1", marginTop: "0.2rem" }}>
                                      • [{new Date(h.timestamp).toLocaleString()}] Action: <strong>{h.action.toUpperCase()}</strong>
                                      {h.reviewer_note && ` — Note: "${h.reviewer_note}"`}
                                    </div>
                                  ))}
                                </div>
                              )}

                              {/* Review Action Form (allowed for both pending and updates) */}
                              <div className="review-form-fields">
                                <div className="form-field">
                                  <label>Correction (INS codes, comma-separated)</label>
                                  <input
                                    type="text"
                                    placeholder="e.g. INS 250, INS 211"
                                    value={correctionInput}
                                    onChange={(e) => setCorrectionInput(e.target.value)}
                                    className="review-text-input"
                                  />
                                </div>
                                <div className="form-field">
                                  <label>Reviewer Note (optional)</label>
                                  <input
                                    type="text"
                                    placeholder="Explain your decision..."
                                    value={reviewNote}
                                    onChange={(e) => setReviewNote(e.target.value)}
                                    className="review-text-input"
                                  />
                                </div>
                              </div>

                              <div className="review-action-btns review-action-btns-row">
                                <button
                                  className="btn btn-sm btn-valid"
                                  onClick={() => handleReview(r.id, "confirm")}
                                >
                                  ✓ Confirm (not an additive)
                                </button>
                                <button
                                  className="btn btn-sm btn-invalid"
                                  onClick={() => handleReview(r.id, "reject")}
                                >
                                  ✗ Reject (false positive)
                                </button>
                                <button
                                  className="btn btn-sm btn-primary"
                                  onClick={() => handleReview(r.id, "correct")}
                                >
                                  ✏ Correct
                                </button>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer" style={{ display: "flex", justifyContent: "space-between" }}>
          <span style={{ fontSize: "0.8rem", color: "#94a3b8" }}>
            Showing {filteredRecords.length} of {records.length} records
          </span>
          <div style={{ display: "flex", gap: "0.5rem" }}>
            <button className="btn btn-secondary" onClick={loadData}>🔄 Refresh</button>
            <button className="btn btn-secondary" onClick={onClose}>Close</button>
          </div>
        </div>
      </div>
    </div>
  );
}

const statCardStyle = {
  padding: "0.6rem 0.85rem",
  backgroundColor: "rgba(15, 23, 42, 0.55)",
  border: "1px solid rgba(255, 255, 255, 0.08)",
  borderRadius: "8px",
  display: "flex",
  flexDirection: "column",
  alignItems: "center"
};

const statNumberStyle = {
  fontSize: "1.3rem",
  fontWeight: 800,
  color: "#f8fafc",
  lineHeight: 1.1
};

const statLabelStyle = {
  fontSize: "0.68rem",
  color: "#94a3b8",
  textTransform: "uppercase",
  letterSpacing: "0.5px",
  marginTop: "0.2rem",
  textAlign: "center"
};

export default AuditQueueModal;

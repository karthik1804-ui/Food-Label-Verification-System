import React, { useState, useEffect, useCallback } from "react";
import { fetchAuditQueue, submitAuditReview, fetchAuditStats, deleteAuditRecord } from "../api";
import Icon from "./Icons";

export default function AuditQueueModal({ isOpen, onClose }) {
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
      setFeedback("Failed to load audit queue. Please ensure the backend is running.");
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
      ? correctionInput.split(",").map((s) => s.trim()).filter(Boolean)
      : undefined;

    if (action === "correct" && (!corrected || corrected.length === 0)) {
      setFeedback("Please enter at least one INS code for the correction.");
      return;
    }

    try {
      const result = await submitAuditReview(recordId, action, corrected, reviewNote);
      setFeedback(result.message || "Review decision recorded.");
      setReviewingId(null);
      setCorrectionInput("");
      setReviewNote("");
      await loadData();
    } catch (err) {
      setFeedback(`Review submission failed: ${err.response?.data?.message || err.message}`);
    }
  };

  const handleDeleteRecord = async (recordId) => {
    if (!window.confirm("Dismiss and remove this audit record from the queue?")) return;
    try {
      await deleteAuditRecord(recordId);
      setFeedback("Audit record dismissed.");
      await loadData();
    } catch (err) {
      setFeedback(`Failed to delete record: ${err.response?.data?.message || err.message}`);
    }
  };

  const statusBadgeInfo = (status) => {
    if (!status) return { label: "Pending", cls: "status-pill-warning" };
    if (status.includes("CONFIRMED")) return { label: "Confirmed", cls: "status-pill-success" };
    if (status.includes("REJECTED")) return { label: "Rejected", cls: "status-pill-danger" };
    if (status.includes("CORRECTED")) return { label: "Corrected", cls: "status-pill-info" };
    return { label: "Pending", cls: "status-pill-warning" };
  };

  const filteredRecords = records.filter((r) => {
    if (!searchQuery.trim()) return true;
    const q = searchQuery.toLowerCase();
    const matchContext = (r.context_identifier || "").toLowerCase().includes(q);
    const matchTokens = (r.unmapped_tokens || []).some((t) => t.toLowerCase().includes(q));
    const matchNote = (r.review_history || []).some((h) => (h.reviewer_note || "").toLowerCase().includes(q));
    return matchContext || matchTokens || matchNote;
  });

  if (!isOpen) return null;

  return (
    <div className="clinical-modal-overlay" onClick={onClose}>
      <div
        className="clinical-modal-box audit-modal-box"
        onClick={(e) => e.stopPropagation()}
        role="dialog"
        aria-labelledby="audit-modal-title"
      >
        {/* Header */}
        <div className="clinical-modal-header">
          <div className="modal-title-left">
            <div className="modal-icon-box">
              <Icon name="clipboardList" size={20} color="#00454A" />
            </div>
            <div>
              <h2 id="audit-modal-title" className="modal-heading">
                HITL Audit Queue
              </h2>
              <p className="modal-subtext">
                Review and verify unmapped ingredient tokens and taxonomy assignments.
              </p>
            </div>
          </div>
          <button
            type="button"
            className="modal-close-btn"
            onClick={onClose}
            aria-label="Close modal"
          >
            <Icon name="x" size={20} />
          </button>
        </div>

        {/* Feedback message */}
        {feedback && (
          <div className="alert-banner alert-success" style={{ margin: "1rem 1.5rem 0 1.5rem" }}>
            <Icon name="checkCircle" size={16} />
            <span>{feedback}</span>
          </div>
        )}

        {/* Aggregate Statistics Row */}
        {stats && (
          <div className="audit-stats-row">
            <div className="audit-stat-pill">
              <span className="stat-number">{stats.total_records}</span>
              <span className="stat-name">Total Flagged</span>
            </div>
            <div className="audit-stat-pill warning">
              <span className="stat-number">{stats.pending_count}</span>
              <span className="stat-name">Pending Review</span>
            </div>
            <div className="audit-stat-pill success">
              <span className="stat-number">{stats.confirmed_count}</span>
              <span className="stat-name">Confirmed</span>
            </div>
            <div className="audit-stat-pill info">
              <span className="stat-number">{stats.corrected_count}</span>
              <span className="stat-name">Corrected</span>
            </div>
          </div>
        )}

        {/* Filters and Search Bar */}
        <div className="audit-filter-bar">
          <div className="audit-tabs-segmented">
            {[
              { id: "all", label: "All Records" },
              { id: "PENDING_EXPERT_REVIEW", label: "Pending" },
              { id: "CONFIRMED_BY_REVIEWER", label: "Confirmed" },
              { id: "CORRECTED_BY_REVIEWER", label: "Corrected" },
              { id: "REJECTED_BY_REVIEWER", label: "Rejected" }
            ].map((tab) => (
              <button
                key={tab.id}
                type="button"
                className={`audit-tab-btn ${statusFilter === tab.id ? "active" : ""}`}
                onClick={() => setStatusFilter(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </div>

          <div className="input-with-icon audit-search-box">
            <Icon name="search" size={16} className="input-leading-icon" />
            <input
              type="text"
              className="form-input form-input-sm"
              placeholder="Search token or product..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>

        {/* Table Body */}
        <div className="audit-table-wrap">
          {loading ? (
            <div className="empty-subtle-box">
              <div className="btn-spinner" />
              <p>Loading audit queue...</p>
            </div>
          ) : filteredRecords.length === 0 ? (
            <div className="empty-subtle-box">
              <Icon name="checkCircle" size={32} color="#16A34A" />
              <h4 style={{ margin: "0.5rem 0" }}>No Records In Queue</h4>
              <p style={{ color: "var(--text-secondary)", fontSize: "0.85rem" }}>
                No unmapped additive tokens match your selected filter criteria.
              </p>
            </div>
          ) : (
            <table className="clinical-table audit-table">
              <thead>
                <tr>
                  <th>Product Context</th>
                  <th>Unmapped Tokens</th>
                  <th>Match Conf.</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {filteredRecords.map((r) => {
                  const statusObj = statusBadgeInfo(r.audit_status);
                  const isReviewing = reviewingId === r.id;

                  return (
                    <React.Fragment key={r.id || r.timestamp}>
                      <tr className={isReviewing ? "row-expanded" : ""}>
                        <td>
                          <strong>{r.context_identifier || "Direct Scan"}</strong>
                          <div className="text-muted text-xs" style={{ marginTop: "0.15rem" }}>
                            {r.timestamp ? new Date(r.timestamp).toLocaleString(undefined, {
                              month: "short",
                              day: "numeric",
                              hour: "2-digit",
                              minute: "2-digit"
                            }) : "N/A"}
                          </div>
                        </td>
                        <td>
                          <div className="unmapped-tokens-wrap">
                            {(r.unmapped_tokens || []).map((t, i) => (
                              <span key={i} className="token-chip">{t}</span>
                            ))}
                          </div>
                          {r.corrected_tokens && r.corrected_tokens.length > 0 && (
                            <span className="corrected-tokens-hint">
                              Mapped to: <strong>{r.corrected_tokens.join(", ")}</strong>
                            </span>
                          )}
                        </td>
                        <td>
                          {r.additive_match_confidence !== undefined
                            ? `${Math.round(r.additive_match_confidence * 100)}%`
                            : "100%"}
                        </td>
                        <td>
                          <span className={`status-pill ${statusObj.cls}`}>
                            {statusObj.label}
                          </span>
                        </td>
                        <td>
                          <div className="audit-actions-group">
                            <button
                              type="button"
                              className="btn btn-outline btn-xs"
                              onClick={() => setReviewingId(isReviewing ? null : r.id)}
                            >
                              {r.audit_status === "PENDING_EXPERT_REVIEW" ? (isReviewing ? "Cancel" : "Review") : (isReviewing ? "Close" : "History")}
                            </button>
                            <button
                              type="button"
                              className="btn btn-ghost btn-xs text-danger"
                              onClick={() => handleDeleteRecord(r.id)}
                              title="Dismiss record"
                            >
                              <Icon name="trash2" size={13} />
                            </button>
                          </div>
                        </td>
                      </tr>

                      {/* Expandable Review / History Drawer */}
                      {isReviewing && (
                        <tr className="expanded-detail-row">
                          <td colSpan={5}>
                            <div className="audit-review-drawer">
                              <h4 className="drawer-title">
                                Reviewing Record #{r.id} • Tokens: <strong>{(r.unmapped_tokens || []).join(", ")}</strong>
                              </h4>

                              {r.review_history && r.review_history.length > 0 && (
                                <div className="prior-history-box">
                                  <span className="prior-history-label">Previous Decisions:</span>
                                  {r.review_history.map((h, i) => (
                                    <div key={i} className="history-step">
                                      • [{new Date(h.timestamp).toLocaleTimeString()}] Action: <strong>{h.action.toUpperCase()}</strong>
                                      {h.reviewer_note && ` — Note: "${h.reviewer_note}"`}
                                    </div>
                                  ))}
                                </div>
                              )}

                              <div className="review-inputs-row">
                                <div className="form-group flex-1">
                                  <label className="form-label">Correction (INS codes, comma-separated):</label>
                                  <input
                                    type="text"
                                    className="form-input form-input-sm"
                                    placeholder="e.g. INS 250, INS 211"
                                    value={correctionInput}
                                    onChange={(e) => setCorrectionInput(e.target.value)}
                                  />
                                </div>
                                <div className="form-group flex-1">
                                  <label className="form-label">Reviewer Note (optional):</label>
                                  <input
                                    type="text"
                                    className="form-input form-input-sm"
                                    placeholder="Provide clinical rationale..."
                                    value={reviewNote}
                                    onChange={(e) => setReviewNote(e.target.value)}
                                  />
                                </div>
                              </div>

                              <div className="review-btn-row">
                                <button
                                  type="button"
                                  className="btn btn-outline btn-sm"
                                  onClick={() => handleReview(r.id, "confirm")}
                                >
                                  <Icon name="check" size={14} color="#16A34A" />
                                  <span>Confirm (Not an Additive)</span>
                                </button>
                                <button
                                  type="button"
                                  className="btn btn-outline btn-sm text-danger"
                                  onClick={() => handleReview(r.id, "reject")}
                                >
                                  <Icon name="x" size={14} />
                                  <span>Reject (False Positive)</span>
                                </button>
                                <button
                                  type="button"
                                  className="btn btn-primary btn-sm"
                                  onClick={() => handleReview(r.id, "correct")}
                                >
                                  <Icon name="checkCircle" size={14} />
                                  <span>Submit INS Correction</span>
                                </button>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          )}
        </div>

        {/* Modal Footer */}
        <div className="clinical-modal-footer">
          <span className="footer-count-text">
            Showing {filteredRecords.length} of {records.length} records in queue
          </span>
          <div className="flex-row gap-sm">
            <button
              type="button"
              className="btn btn-outline btn-sm"
              onClick={loadData}
            >
              <Icon name="refreshCw" size={14} />
              <span>Refresh</span>
            </button>
            <button
              type="button"
              className="btn btn-secondary btn-sm"
              onClick={onClose}
            >
              Close
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

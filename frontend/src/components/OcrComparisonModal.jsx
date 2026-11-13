import React, { useState, useEffect, useRef } from "react";
import Tesseract from "tesseract.js";
import Icon from "./Icons";
import { fetchOcrBenchmark, compareOcr, preprocessOcrImage } from "../api";

// Word-level mean confidence calculation
const computeMeanOcrConfidence = (tesseractData) => {
  const words = tesseractData?.words || [];
  if (words.length === 0) return 1.0;
  const validWords = words.filter((w) => w.text && w.text.trim().length > 0);
  if (validWords.length === 0) return 1.0;
  const sum = validWords.reduce((acc, w) => acc + (w.confidence || 0), 0);
  return Math.min(1.0, Math.max(0.0, sum / validWords.length / 100));
};

export default function OcrComparisonModal({
  isOpen,
  onClose,
  activeImage = null,
  activeMode = "upload",
  ocrConfig = "B"
}) {
  const [activeTab, setActiveTab] = useState("benchmark"); // 'benchmark' | 'live' | 'methodology'
  const [benchmarkData, setBenchmarkData] = useState(null);
  const [loadingBenchmark, setLoadingBenchmark] = useState(false);
  const [benchmarkError, setBenchmarkError] = useState("");

  // Live comparison state
  const [liveComparing, setLiveComparing] = useState(false);
  const [comparingStep, setComparingStep] = useState("");
  const [liveComparisonResult, setLiveComparisonResult] = useState(null);
  const [liveError, setLiveError] = useState("");

  const requestIdRef = useRef(0);

  // Clear stale comparison results whenever active image changes
  useEffect(() => {
    setLiveComparisonResult(null);
    setLiveError("");
    setComparingStep("");
  }, [activeImage]);

  useEffect(() => {
    if (isOpen && !benchmarkData && !loadingBenchmark) {
      loadBenchmark();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [isOpen]);

  const loadBenchmark = async () => {
    setLoadingBenchmark(true);
    setBenchmarkError("");
    try {
      const data = await fetchOcrBenchmark();
      setBenchmarkData(data);
    } catch (err) {
      console.error("Failed to load OCR benchmark:", err);
      setBenchmarkError("Could not load benchmark metrics from backend server.");
    } finally {
      setLoadingBenchmark(false);
    }
  };

  const handleRunLiveComparison = async () => {
    if (!activeImage) {
      setLiveError("No active image available. Please capture or upload a packaging image first.");
      return;
    }

    const currentReqId = ++requestIdRef.current;
    setLiveComparing(true);
    setLiveError("");
    setLiveComparisonResult(null);

    let worker = null;
    try {
      setComparingStep("Preprocessing image with OpenCV (CLAHE, unsharp masking)...");
      const prepRes = await preprocessOcrImage(activeImage, "B", "best");
      if (requestIdRef.current !== currentReqId) return;

      if (!prepRes || !prepRes.enhanced_image_base64) {
        throw new Error(prepRes?.error || "OpenCV preprocessing failed for Configuration B");
      }

      setComparingStep("Initializing Tesseract OCR worker...");
      worker = await Tesseract.createWorker("eng", 1);
      await worker.setParameters({
        tessedit_pageseg_mode: "6",
        preserve_interword_spaces: "1"
      });
      if (requestIdRef.current !== currentReqId) return;

      // Configuration A: Raw original image
      setComparingStep("Running Configuration A (Raw Tesseract on original image)...");
      const t0_a = performance.now();
      const resA = await worker.recognize(activeImage);
      const time_a = Math.round(performance.now() - t0_a);
      if (requestIdRef.current !== currentReqId) return;

      const text_a = resA.data?.text || "";
      const conf_a = computeMeanOcrConfidence(resA.data);

      // Configuration B: OpenCV preprocessed image
      setComparingStep("Running Configuration B (Tesseract on OpenCV preprocessed image)...");
      const t0_b = performance.now();
      const resB = await worker.recognize(prepRes.enhanced_image_base64);
      const time_b = Math.round(performance.now() - t0_b);
      if (requestIdRef.current !== currentReqId) return;

      const text_b = resB.data?.text || "";
      const conf_b = computeMeanOcrConfidence(resB.data);

      setComparingStep("Analyzing comparative metrics & character confusions...");
      const payload = {
        image_base64: activeImage,
        text_a: text_a,
        text_b: text_b,
        confidence_a: conf_a,
        confidence_b: conf_b,
        timings_a: { ocr_ms: time_a },
        timings_b: {
          preprocessing_ms: prepRes.timings_ms?.total_preprocessing_ms || 0,
          ocr_ms: time_b
        }
      };

      const compResult = await compareOcr(payload);
      if (requestIdRef.current !== currentReqId) return;

      setLiveComparisonResult(compResult);
    } catch (err) {
      if (requestIdRef.current === currentReqId) {
        console.error("Live OCR comparison failed:", err);
        setLiveError(err.message || "Failed to execute side-by-side OCR comparison.");
        setLiveComparisonResult(null);
      }
    } finally {
      if (worker) {
        try {
          await worker.terminate();
        } catch (termErr) {
          console.warn("Worker termination error:", termErr);
        }
      }
      if (requestIdRef.current === currentReqId) {
        setLiveComparing(false);
        setComparingStep("");
      }
    }
  };

  if (!isOpen) return null;

  const summary = benchmarkData?.benchmark_summary;
  const samples = benchmarkData?.samples || [];

  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal-window ocr-modal-window" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <div className="modal-header-title">
            <Icon name="sliders" size={20} color="#2563eb" />
            <div>
              <h3>OCR Pipeline Comparison & Evaluation Suite</h3>
              <p className="modal-subtitle">
                Academic evaluation comparing Configuration A (Raw Tesseract) vs Configuration B (OpenCV + Tesseract)
              </p>
            </div>
          </div>
          <button className="modal-close-btn" onClick={onClose} aria-label="Close modal">
            <Icon name="x" size={18} />
          </button>
        </div>

        {/* Tab Navigation */}
        <div className="modal-tab-bar">
          <button
            type="button"
            className={`modal-tab-btn ${activeTab === "benchmark" ? "active" : ""}`}
            onClick={() => setActiveTab("benchmark")}
          >
            <Icon name="barChart" size={16} />
            <span>Benchmark Evaluation (CER / WER / F1)</span>
          </button>

          <button
            type="button"
            className={`modal-tab-btn ${activeTab === "live" ? "active" : ""}`}
            onClick={() => setActiveTab("live")}
          >
            <Icon name="refresh" size={16} />
            <span>Side-by-Side Comparison</span>
          </button>

          <button
            type="button"
            className={`modal-tab-btn ${activeTab === "methodology" ? "active" : ""}`}
            onClick={() => setActiveTab("methodology")}
          >
            <Icon name="fileText" size={16} />
            <span>Pipeline Architecture & Integrity</span>
          </button>
        </div>

        {/* Modal Body */}
        <div className="modal-body ocr-modal-body">
          {/* TAB 1: BENCHMARK SUITE */}
          {activeTab === "benchmark" && (
            <div className="benchmark-tab-content">
              {loadingBenchmark && (
                <div className="loading-state">
                  <div className="spinner" />
                  <p>Computing empirical benchmark metrics...</p>
                </div>
              )}

              {benchmarkError && (
                <div className="alert-banner alert-warning">
                  <Icon name="alertTriangle" size={18} />
                  <span>{benchmarkError}</span>
                </div>
              )}

              {summary && !loadingBenchmark && (
                <>
                  {/* KPI Summary Cards */}
                  <div className="benchmark-kpi-grid">
                    <div className="kpi-metric-card positive">
                      <span className="kpi-label">Character Error Rate (CER)</span>
                      <div className="kpi-value-row">
                        <span className="val-old">{(summary.mean_cer_config_a * 100).toFixed(1)}%</span>
                        <span className="val-arrow">→</span>
                        <span className="val-new">{(summary.mean_cer_config_b * 100).toFixed(1)}%</span>
                      </div>
                      <span className="kpi-delta">-{summary.cer_relative_reduction_pct}% Relative Reduction</span>
                    </div>

                    <div className="kpi-metric-card positive">
                      <span className="kpi-label">Word Error Rate (WER)</span>
                      <div className="kpi-value-row">
                        <span className="val-old">{(summary.mean_wer_config_a * 100).toFixed(1)}%</span>
                        <span className="val-arrow">→</span>
                        <span className="val-new">{(summary.mean_wer_config_b * 100).toFixed(1)}%</span>
                      </div>
                      <span className="kpi-delta">-{summary.wer_relative_reduction_pct}% Relative Reduction</span>
                    </div>

                    <div className="kpi-metric-card highlight">
                      <span className="kpi-label">INS Code Detection F1 Score</span>
                      <div className="kpi-value-row">
                        <span className="val-old">{(summary.config_a_ins_metrics.f1_score * 100).toFixed(1)}%</span>
                        <span className="val-arrow">→</span>
                        <span className="val-new">{(summary.config_b_ins_metrics.f1_score * 100).toFixed(1)}%</span>
                      </div>
                      <span className="kpi-delta">+{((summary.f1_absolute_gain) * 100).toFixed(1)}% Absolute F1 Gain</span>
                    </div>

                    <div className="kpi-metric-card neutral">
                      <span className="kpi-label">Test Samples Breakdown</span>
                      <div className="kpi-value-row">
                        <span className="val-new">{summary.total_samples} Evaluated</span>
                      </div>
                      <span className="kpi-sub">
                        {summary.improved_samples || 0} Improved • {summary.unchanged_samples || summary.neutral_samples || 0} Unchanged • {summary.mixed_samples || 0} Mixed • {summary.regressed_samples || summary.degraded_samples || 0} Regressed
                      </span>
                    </div>
                  </div>

                  {/* Sample Breakdown Table */}
                  <div className="table-responsive benchmark-table-container">
                    <table className="data-table">
                      <thead>
                        <tr>
                          <th>Sample ID & Packaging Type</th>
                          <th>Ground Truth Codes</th>
                          <th>Config A Detected</th>
                          <th>Config B Detected</th>
                          <th>Error Rates (A vs B)</th>
                          <th>Outcome Impact</th>
                        </tr>
                      </thead>
                      <tbody>
                        {samples.map((s) => (
                          <tr key={s.sample_id}>
                            <td>
                              <strong>{s.sample_id}</strong>
                              <div className="text-muted small">{s.label_category}</div>
                            </td>
                            <td>
                              <div className="chip-list">
                                {s.ground_truth.codes.map((c, i) => (
                                  <span key={i} className="badge badge-gt">INS {c}</span>
                                ))}
                              </div>
                            </td>
                            <td>
                              <span className="mono-code">
                                {s.config_a.detected_codes.join(", ") || "(none)"}
                              </span>
                            </td>
                            <td>
                              <span className="mono-code font-semibold" style={{ color: "#059669" }}>
                                {s.config_b.detected_codes.join(", ") || "(none)"}
                              </span>
                            </td>
                            <td>
                              <div className="small">
                                CER: {(s.config_a.cer * 100).toFixed(1)}% → {(s.config_b.cer * 100).toFixed(1)}%
                              </div>
                              <div className="small text-muted">
                                WER: {(s.config_a.wer * 100).toFixed(1)}% → {(s.config_b.wer * 100).toFixed(1)}%
                              </div>
                            </td>
                            <td>
                              <span className={`impact-badge impact-${s.comparison.impact.toLowerCase()}`}>
                                {s.comparison.impact}
                              </span>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </div>
          )}

          {/* TAB 2: LIVE COMPARISON */}
          {activeTab === "live" && (
            <div className="live-comparison-tab-content">
              <div className="live-controls-bar">
                <p className="text-muted">
                  Compare how Configuration A (Raw Tesseract) and Configuration B (OpenCV Preprocessed) analyze the currently selected food packaging image.
                </p>
                <button
                  type="button"
                  className="btn btn-primary"
                  onClick={handleRunLiveComparison}
                  disabled={liveComparing || !activeImage}
                >
                  {liveComparing ? (
                    <>
                      <div className="spinner small" />
                      <span>{comparingStep || "Comparing Pipelines..."}</span>
                    </>
                  ) : (
                    <>
                      <Icon name="refresh" size={16} />
                      <span>Run Live Side-by-Side Comparison</span>
                    </>
                  )}
                </button>
              </div>

              {!activeImage && (
                <div className="alert-banner alert-info" style={{ marginTop: "1rem" }}>
                  <Icon name="info" size={18} />
                  <span>
                    No image active in current mode ({activeMode}). Capture a packaging label in Camera mode or browse an image in Upload mode to run live comparison.
                  </span>
                </div>
              )}

              {liveComparing && comparingStep && (
                <div className="alert-banner alert-info" style={{ marginTop: "1rem" }}>
                  <div className="spinner small" style={{ marginRight: "0.5rem" }} />
                  <span>{comparingStep}</span>
                </div>
              )}

              {liveError && (
                <div className="alert-banner alert-warning" style={{ marginTop: "1rem" }}>
                  <Icon name="alertTriangle" size={18} />
                  <span>{liveError}</span>
                </div>
              )}

              {liveComparisonResult && (
                <div className="side-by-side-grid" style={{ marginTop: "1.5rem" }}>
                  {/* Config A Card */}
                  <div className="comparison-card config-a-card">
                    <div className="comp-card-header">
                      <span className="pipeline-tag a-tag">Configuration A</span>
                      <h4>Raw Tesseract (No OpenCV)</h4>
                    </div>
                    <div className="comp-meta-row">
                      <span>Confidence: {Math.round(liveComparisonResult.config_a.confidence * 100)}%</span>
                      <span>Words: {liveComparisonResult.config_a.word_count}</span>
                    </div>
                    <div className="comp-text-box">
                      <label>Extracted OCR Text:</label>
                      <pre>{liveComparisonResult.config_a.text}</pre>
                    </div>
                    <div className="comp-additives-box">
                      <label>Detected INS Codes:</label>
                      <div className="chip-list">
                        {liveComparisonResult.config_a.detected_ins_codes.map((c, i) => (
                          <span key={i} className="badge badge-secondary">{c}</span>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Config B Card */}
                  <div className="comparison-card config-b-card">
                    <div className="comp-card-header">
                      <span className="pipeline-tag b-tag">Configuration B</span>
                      <h4>OpenCV Preprocessed + Tesseract</h4>
                    </div>
                    <div className="comp-meta-row">
                      <span style={{ color: "#059669", fontWeight: 600 }}>
                        Confidence: {Math.round(liveComparisonResult.config_b.confidence * 100)}%
                      </span>
                      <span>Words: {liveComparisonResult.config_b.word_count}</span>
                    </div>
                    <div className="comp-text-box">
                      <label>Extracted OCR Text:</label>
                      <pre>{liveComparisonResult.config_b.text}</pre>
                    </div>
                    <div className="comp-additives-box">
                      <label>Detected INS Codes:</label>
                      <div className="chip-list">
                        {liveComparisonResult.config_b.detected_ins_codes.map((c, i) => (
                          <span key={i} className="badge badge-success">{c}</span>
                        ))}
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Comparison Differential Metrics */}
              {liveComparisonResult?.comparison_metrics && (
                <div className="comparison-differential-panel" style={{ marginTop: "1.5rem" }}>
                  <h4>Differential Analysis & Confusion Corrections</h4>
                  <div className="differential-grid">
                    <div className="diff-card">
                      <span className="diff-label">Text Similarity</span>
                      <span className="diff-value">
                        {Math.round(liveComparisonResult.comparison_metrics.similarity_ratio * 100)}%
                      </span>
                    </div>
                    <div className="diff-card">
                      <span className="diff-label">Newly Recovered Codes in B</span>
                      <span className="diff-value text-success">
                        {liveComparisonResult.comparison_metrics.new_ins_codes_detected_in_b.join(", ") || "None"}
                      </span>
                    </div>
                    <div className="diff-card">
                      <span className="diff-label">Character Confusion Corrections</span>
                      <span className="diff-value">
                        {liveComparisonResult.comparison_metrics.character_confusion_count} fixed
                      </span>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: METHODOLOGY */}
          {activeTab === "methodology" && (
            <div className="methodology-tab-content">
              <h4>Academic Architecture & Academic Integrity Notice</h4>
              <p>
                <strong>Tesseract OCR</strong> remains the sole optical character recognition engine.
                <strong>OpenCV</strong> serves exclusively as an image preprocessing filter layer positioned immediately before OCR execution.
              </p>
              <div className="methodology-steps-list">
                <div className="m-step">
                  <strong>1. Bilateral Edge-Preserving Denoising:</strong> Eliminates sensor grain on phone camera captures while preserving sharp stroke boundaries of small 6pt text.
                </div>
                <div className="m-step">
                  <strong>2. Contrast Limited Adaptive Histogram Equalization (CLAHE):</strong> Equalizes regional shadows and highlights across curved metallic beverage cans and reflective snack pouches.
                </div>
                <div className="m-step">
                  <strong>3. Unsharp Masking:</strong> Accentuates letter edges and parenthetical numerals without amplifying background packaging clutter.
                </div>
                <div className="m-step">
                  <strong>4. Automatic Fallback Architecture:</strong> If any OpenCV filter step fails or degrades contrast, the pipeline automatically falls back to Configuration A.
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="modal-footer">
          <button type="button" className="btn btn-secondary" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}

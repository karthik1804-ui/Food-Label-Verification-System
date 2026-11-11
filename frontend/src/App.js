import React, { useState, useEffect } from "react";
import Tesseract from "tesseract.js";
import { analyzePayload, fetchCurrentUser, logoutUser, preprocessOcrImage } from "./api";
import BarcodeScanner from "./components/BarcodeScanner";
import SafetyScoreCard from "./components/SafetyScoreCard";
import ShapAttributionChart from "./components/ShapAttributionChart";
import CounterfactualCard from "./components/CounterfactualCard";
import ConfidencePanel from "./components/ConfidencePanel";
import CameraScanner from "./components/CameraScanner";
import ImageUpload from "./components/ImageUpload";
import IngredientTextInput from "./components/IngredientTextInput";
import AuditQueueModal from "./components/AuditQueueModal";
import AuthModal from "./components/AuthModal";
import DietaryProfileModal from "./components/DietaryProfileModal";
import PersonalisedScoreCard from "./components/PersonalisedScoreCard";
import AnalysisHistoryModal from "./components/AnalysisHistoryModal";
import "./style.css";

// Compute mean word-level confidence from Tesseract result (0.0–1.0)
const computeOcrConfidence = (tesseractData) => {
  const words = tesseractData?.words || [];
  if (words.length === 0) return 1.0;
  const validWords = words.filter(w => w.confidence > 0);
  if (validWords.length === 0) return 0.5;
  const mean = validWords.reduce((sum, w) => sum + w.confidence, 0) / validWords.length;
  return Math.round((mean / 100) * 1000) / 1000; // 0.0–1.0, 3 decimal places
};

// Helper function to crop the center region (center 70%) of captured camera frame
const cropCenterImage = (imageSrc) => {
  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      const margin = 0.15;
      const cropX = img.width * margin;
      const cropY = img.height * margin;
      const cropWidth = img.width * (1 - 2 * margin);
      const cropHeight = img.height * (1 - 2 * margin);

      const canvas = document.createElement("canvas");
      canvas.width = cropWidth;
      canvas.height = cropHeight;
      const ctx = canvas.getContext("2d");
      if (!ctx) return resolve(imageSrc);

      ctx.drawImage(img, cropX, cropY, cropWidth, cropHeight, 0, 0, cropWidth, cropHeight);
      resolve(canvas.toDataURL("image/jpeg", 0.95));
    };
    img.onerror = () => resolve(imageSrc);
    img.src = imageSrc;
  });
};

// Canvas preprocessing for OCR enhancement
const preprocessImageForOcr = (imageSrc, isUpload) => {
  return new Promise((resolve) => {
    const img = new Image();
    img.crossOrigin = "anonymous";
    img.onload = () => {
      let width = img.width;
      let height = img.height;

      if (isUpload && (width < 1500 || height < 1500)) {
        const target = 2000;
        if (width >= height) {
          height = Math.round(target * (height / width));
          width = target;
        } else {
          width = Math.round(target * (width / height));
          height = target;
        }
      }

      const canvas = document.createElement("canvas");
      canvas.width = width;
      canvas.height = height;
      const ctx = canvas.getContext("2d");
      if (!ctx) return resolve(imageSrc);

      ctx.drawImage(img, 0, 0, width, height);

      const imgData = ctx.getImageData(0, 0, width, height);
      const data = imgData.data;
      const orig = new Uint8ClampedArray(data);

      const contrast = 1.7;
      const brightness = 1.1;
      const centerWeight = isUpload ? 3.0 : 4.0;
      const neighborWeight = isUpload ? -0.5 : -0.75;

      for (let y = 1; y < height - 1; y++) {
        for (let x = 1; x < width - 1; x++) {
          const idx = (y * width + x) * 4;
          const up = idx - width * 4;
          const down = idx + width * 4;
          const left = idx - 4;
          const right = idx + 4;

          for (let c = 0; c < 3; c++) {
            const sharp = centerWeight * orig[idx + c] +
              neighborWeight * (orig[up + c] + orig[down + c] + orig[left + c] + orig[right + c]);
            const val = ((sharp * brightness) - 127.5) * contrast + 127.5;
            data[idx + c] = val < 0 ? 0 : (val > 255 ? 255 : val);
          }
        }
      }

      ctx.putImageData(imgData, 0, 0);
      resolve(canvas.toDataURL("image/jpeg", 0.95));
    };
    img.onerror = () => resolve(imageSrc);
    img.src = imageSrc;
  });
};

function App() {
  const [activeTab, setActiveTab] = useState("barcode");
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [analysisResult, setAnalysisResult] = useState(null);
  const [showAuditModal, setShowAuditModal] = useState(false);

  // Authentication & Dietary Profile state
  const [currentUser, setCurrentUser] = useState(null);
  const [dietaryProfile, setDietaryProfile] = useState(null);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileModal, setShowProfileModal] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);

  // Auto-hydrate session from token on mount
  useEffect(() => {
    fetchCurrentUser()
      .then((data) => {
        if (data && data.user) {
          setCurrentUser(data.user);
          setDietaryProfile(data.dietary_profile);
        }
      })
      .catch(() => {
        // Guest mode
      });
  }, []);

  // Initial load demo with benchmark product
  useEffect(() => {
    handleRunAnalysis({ ean: "8901234567890" });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const handleRunAnalysis = async (payload) => {
    setLoading(true);
    setErrorMessage("");
    try {
      const fullPayload = {
        ...payload,
        ...(dietaryProfile ? { dietary_profile: dietaryProfile } : {})
      };
      const data = await analyzePayload(fullPayload);
      setAnalysisResult(data);
    } catch (err) {
      console.error("Analysis failure:", err);
      const msg = err.response?.data?.message || err.message || "Failed to complete analysis. Is Flask server running?";
      setErrorMessage(msg);
    } finally {
      setLoading(false);
    }
  };

  const handleOcrImage = async (imageSrc, isUpload = false) => {
    setLoading(true);
    setErrorMessage("");
    try {
      let finalImg = imageSrc;
      if (!isUpload) {
        finalImg = await cropCenterImage(imageSrc);
      }

      // Try OpenCV backend preprocessing first (Laplacian blur detection + CLAHE contrast enhancement)
      let ocrInput = finalImg;
      try {
        const prepRes = await preprocessOcrImage(finalImg);
        if (prepRes && prepRes.quality_metrics) {
          if (prepRes.quality_metrics.is_blurry) {
            console.warn(`Laplacian blur detected (variance: ${prepRes.quality_metrics.blur_score}). Image may be out of focus.`);
          }
          if (prepRes.enhanced_image_base64) {
            ocrInput = prepRes.enhanced_image_base64;
          }
        }
      } catch (prepErr) {
        console.warn("Backend OpenCV preprocessing skipped, falling back to client canvas:", prepErr);
        ocrInput = await preprocessImageForOcr(finalImg, isUpload);
      }

      const worker = await Tesseract.createWorker("eng", 1);
      await worker.setParameters({
        tessedit_pageseg_mode: "6",
        preserve_interword_spaces: "1"
      });

      const res = await worker.recognize(ocrInput);
      await worker.terminate();

      const extracted = res.data.text;
      if (!extracted || !extracted.trim()) {
        setErrorMessage("No legible text recognized from image. Please ensure packaging is well-lit.");
        setLoading(false);
        return;
      }

      // Compute and forward Tesseract word-level confidence to backend
      const ocrConfidence = computeOcrConfidence(res.data);
      console.log(`OCR confidence: ${(ocrConfidence * 100).toFixed(1)}%`);

      await handleRunAnalysis({
        text: extracted,
        ocr_confidence: ocrConfidence,
        product: {
          name: isUpload ? "Uploaded Packaging Scan" : "Live Camera Capture",
          brand: "Scanned Label",
          category: "Visual OCR Inspection"
        }
      });
    } catch (err) {
      console.error("OCR Pipeline error:", err);
      setErrorMessage(`OCR Processing Failed: ${err.message || err}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app dark-theme">
      {/* Navigation Header */}
      <nav className="navbar">
        <div className="navbar-container">
          <div className="navbar-brand">
            <span className="brand-logo">🔬</span>
            <div>
              <span className="brand-name">Food Label Verification System</span>
              <span className="brand-tagline">Multimodal Deep Learning & Dietary Verification</span>
            </div>
          </div>

          <div className="navbar-actions">
            {currentUser ? (
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
                <span style={{ fontSize: "0.85rem", color: "#e2e8f0" }}>
                  👤 <strong>{currentUser.username}</strong>
                </span>
                {dietaryProfile?.preset_name && (
                  <span style={{
                    fontSize: "0.72rem",
                    padding: "0.2rem 0.5rem",
                    borderRadius: "12px",
                    backgroundColor: "#1e3a8a",
                    color: "#93c5fd",
                    textTransform: "capitalize"
                  }}>
                    {dietaryProfile.preset_name.replace("_", " ")}
                  </span>
                )}
                <button
                  className="btn btn-outline"
                  onClick={() => setShowProfileModal(true)}
                  title="Configure dietary restrictions & allergens"
                >
                  🥗 Dietary Profile
                </button>
                <button
                  className="btn btn-outline"
                  onClick={() => setShowHistoryModal(true)}
                  title="View past scans"
                >
                  📜 History
                </button>
                <button
                  className="btn btn-outline"
                  onClick={async () => {
                    await logoutUser();
                    setCurrentUser(null);
                    setDietaryProfile(null);
                  }}
                >
                  Sign Out
                </button>
              </div>
            ) : (
              <button
                className="btn btn-primary"
                onClick={() => setShowAuthModal(true)}
              >
                Sign In / Register
              </button>
            )}

            <button
              className="btn btn-outline"
              onClick={() => setShowAuditModal(true)}
            >
              📋 HITL Audit Queue
            </button>
            <div className="service-status-pill">
              <span className="status-dot"></span>
              <span>API Active</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Global Toast */}
      {errorMessage && (
        <div className="error-toast-container">
          <div className="error-toast card glass">
            <div className="error-toast-content">
              <span>⚠️</span>
              <p>{errorMessage}</p>
            </div>
            <button className="close-toast-btn" onClick={() => setErrorMessage("")}>&times;</button>
          </div>
        </div>
      )}

      {/* Main Content Layout */}
      <main className="main-content">
        {/* Hero Banner */}
        <section className="hero">
          <h1 className="hero-title">Food Label Verification System</h1>
          <p className="hero-subtitle">
            Evaluating food additives, nutrient density, and chemical hazards with transparent rule-based feature deductions, decoupled product identity, and personalised dietary assessments.
          </p>
        </section>

        {/* Input Method Selector Tabs */}
        <div className="tab-control-container">
          <button
            className={`tab-btn ${activeTab === "barcode" ? "active" : ""}`}
            onClick={() => setActiveTab("barcode")}
          >
            🏷️ EAN-13 Barcode
          </button>
          <button
            className={`tab-btn ${activeTab === "camera" ? "active" : ""}`}
            onClick={() => setActiveTab("camera")}
          >
            📷 Live Camera Scanner
          </button>
          <button
            className={`tab-btn ${activeTab === "upload" ? "active" : ""}`}
            onClick={() => setActiveTab("upload")}
          >
            📁 Upload Packaging Image
          </button>
          <button
            className={`tab-btn ${activeTab === "text" ? "active" : ""}`}
            onClick={() => setActiveTab("text")}
          >
            📝 Ingredient Text
          </button>
        </div>

        {/* Active Input Panel */}
        <div className="input-active-panel">
          {activeTab === "barcode" && (
            <BarcodeScanner onAnalyze={handleRunAnalysis} loading={loading} />
          )}

          {activeTab === "camera" && (
            <CameraScanner
              onCapture={(src) => handleOcrImage(src, false)}
              onCameraError={(err) => setErrorMessage(err)}
              loading={loading}
            />
          )}

          {activeTab === "upload" && (
            <ImageUpload processImage={(src) => handleOcrImage(src, true)} loading={loading} />
          )}

          {activeTab === "text" && (
            <IngredientTextInput onAnalyze={handleRunAnalysis} loading={loading} />
          )}
        </div>

        {/* Loading Indicator */}
        {loading && (
          <div className="loading-container glass card">
            <div className="spinner"></div>
            <p>Evaluating chemical taxonomy, computing rule-based deductions, and optimizing counterfactuals...</p>
          </div>
        )}

        {/* Results Dashboard Grid */}
        {analysisResult && !loading && (
          <div className="dashboard-results">
            {/* Top Row: Universal Safety Indicator & Counterfactual */}
            <div className="results-top-grid">
              <SafetyScoreCard
                safetyScoring={analysisResult.safety_indicator || analysisResult.safety_scoring}
                product={analysisResult.product}
              />
              <CounterfactualCard
                counterfactual={analysisResult.counterfactual_explanation}
                currentScore={(analysisResult.safety_indicator || analysisResult.safety_scoring)?.final_score || 0}
              />
            </div>

            {/* Personalised Dietary Evaluation & Allergen Alert */}
            {analysisResult.personal_evaluation && (
              <PersonalisedScoreCard
                personalEvaluation={analysisResult.personal_evaluation}
                onOpenProfileModal={() => setShowProfileModal(true)}
              />
            )}

            {/* Middle Row: Rule-Based Deductions */}
            <ShapAttributionChart
              deductions={(analysisResult.safety_indicator || analysisResult.safety_scoring)?.score_deductions}
            />

            {/* Confidence Panel (v2.0 — 4 dimensions) */}
            <ConfidencePanel systemAudit={analysisResult.system_audit} />

            {/* Bottom Row: Parsed Additives Table */}
            <div className="card glass additives-table-card">
              <div className="card-header">
                <span className="card-icon">🧪</span>
                <div>
                  <h2>Parsed INS / E-Number Additives & Categories</h2>
                  <p className="card-sub">
                    Mapped from verified taxonomy. Regulatory info, functional categories, and ambiguity status.
                  </p>
                </div>
              </div>

              {/* Functional Categories Breakdown Chips */}
              {analysisResult.detected_categories && Object.keys(analysisResult.detected_categories).length > 0 && (
                <div className="category-breakdown-bar">
                  <span style={{ fontSize: "0.78rem", color: "#94a3b8", display: "flex", alignItems: "center", marginRight: "4px" }}>
                    CATEGORIES:
                  </span>
                  {Object.entries(analysisResult.detected_categories).map(([cat, codes]) => (
                    <span key={cat} className="category-badge-chip">
                      <strong>{cat}</strong> ({codes.length})
                    </span>
                  ))}
                </div>
              )}

              {/* Individual INS Codes Found */}
              {analysisResult.individual_ins_codes && analysisResult.individual_ins_codes.length > 0 && (
                <div style={{ display: "flex", flexWrap: "wrap", alignItems: "center", gap: "6px", marginBottom: "1rem" }}>
                  <span style={{ fontSize: "0.78rem", color: "#94a3b8" }}>INS BADGES:</span>
                  {analysisResult.individual_ins_codes.map((code) => (
                    <span key={code} className="ins-code-pill">
                      INS {code}
                    </span>
                  ))}
                </div>
              )}

              {/* Ambiguous Detections Notice */}
              {analysisResult.ambiguous_detections && analysisResult.ambiguous_detections.length > 0 && (
                <div className="ambiguous-alert-banner">
                  <strong>⚠️ Ambiguous Additive Notice: </strong>
                  The formulation contains general or unnumbered additive classes:{" "}
                  {analysisResult.ambiguous_detections.map(a => `${a.matched_term || a.code} (${a.warning || a.code})`).join("; ")}
                </div>
              )}

              {/* Duplicate Detections Notice */}
              {analysisResult.duplicate_detections && analysisResult.duplicate_detections.length > 0 && (
                <div className="duplicate-consolidated-note">
                  ℹ️ <strong>Duplicate Consolidations: </strong>
                  Repeated additive mentions ({analysisResult.duplicate_detections.map(d => `${d.code} x${d.count}`).join(", ")}) were consolidated without duplicate penalty deductions.
                </div>
              )}

              {(!analysisResult.parsed_additives || analysisResult.parsed_additives.length === 0) ? (
                <div className="empty-notice">
                  <span>🌿</span>
                  <p>No food additives detected in this formulation.</p>
                </div>
              ) : (
                <div className="table-responsive">
                  <table className="additives-table">
                    <thead>
                      <tr>
                        <th>Code</th>
                        <th>Additive Name</th>
                        <th>Functional Classes</th>
                        <th>Color Type</th>
                        <th>Hazard Level</th>
                        <th>FSSAI Status</th>
                      </tr>
                    </thead>
                    <tbody>
                      {analysisResult.parsed_additives.map((item, idx) => (
                        <tr key={idx}>
                          <td><strong>{item.code}</strong></td>
                          <td>
                            {item.name}
                            {item.alternative_names && item.alternative_names.length > 0 && (
                              <p className="additive-desc" style={{ fontSize: "0.75rem", color: "#94a3b8" }}>
                                Also: {item.alternative_names.slice(0, 3).join(", ")}
                              </p>
                            )}
                            {item.description && (
                              <p className="additive-desc">{item.description}</p>
                            )}
                          </td>
                          <td>
                            <div style={{ display: "flex", flexWrap: "wrap", gap: "4px" }}>
                              {(item.functional_categories || [item.class]).map((fc, i) => (
                                <span key={i} className="badge badge-class">{fc}</span>
                              ))}
                            </div>
                          </td>
                          <td>
                            {item.is_color ? (
                              <span style={{
                                fontSize: "0.72rem",
                                padding: "2px 6px",
                                borderRadius: "4px",
                                backgroundColor: item.color_origin === "synthetic" ? "rgba(239, 68, 68, 0.2)" : "rgba(16, 185, 129, 0.2)",
                                color: item.color_origin === "synthetic" ? "#fca5a5" : "#a7f3d0",
                                border: `1px solid ${item.color_origin === "synthetic" ? "rgba(239, 68, 68, 0.3)" : "rgba(16, 185, 129, 0.3)"}`
                              }}>
                                🎨 {item.color_origin}
                              </span>
                            ) : (
                              <span style={{ color: "#64748b", fontSize: "0.75rem" }}>—</span>
                            )}
                          </td>
                          <td>
                            <span className={`badge badge-hazard hazard-${item.hazard_level?.toLowerCase()}`}>
                              {item.hazard_level}
                            </span>
                          </td>
                          <td>
                            {item.regulatory ? (
                              <span
                                className={`badge ${item.regulatory.verified ? "badge-valid" : "badge-pending"}`}
                                title={item.regulatory.regulatory_notes || ""}
                              >
                                {item.regulatory.fssai_status?.substring(0, 30) || "Unknown"}
                                {item.regulatory.fssai_status?.length > 30 ? "…" : ""}
                              </span>
                            ) : (
                              <span className="badge badge-pending">Not checked</span>
                            )}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}

              {/* Unmapped tokens notice */}
              {analysisResult.unmapped_tokens && analysisResult.unmapped_tokens.length > 0 && (
                <div className="unmapped-notice">
                  <span>⚠️</span>
                  <span>
                    <strong>Unrecognised tokens (flagged for review): </strong>
                    {analysisResult.unmapped_tokens.join(", ")}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
      </main>

      {/* Modals */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onAuthSuccess={(user, profile) => {
          setCurrentUser(user);
          setDietaryProfile(profile);
          if (analysisResult?.product?.ean && analysisResult.product.ean !== "N/A") {
            handleRunAnalysis({ ean: analysisResult.product.ean, dietary_profile: profile });
          }
        }}
      />

      <DietaryProfileModal
        isOpen={showProfileModal}
        onClose={() => setShowProfileModal(false)}
        currentProfile={dietaryProfile}
        onProfileSaved={(prof) => {
          setDietaryProfile(prof);
          if (analysisResult?.product?.ean && analysisResult.product.ean !== "N/A") {
            handleRunAnalysis({ ean: analysisResult.product.ean, dietary_profile: prof });
          }
        }}
      />

      <AnalysisHistoryModal
        isOpen={showHistoryModal}
        onClose={() => setShowHistoryModal(false)}
      />

      {/* Human-in-the-Loop Audit Modal */}
      <AuditQueueModal
        isOpen={showAuditModal}
        onClose={() => setShowAuditModal(false)}
      />

      <footer className="main-footer">
        <p>&copy; {new Date().getFullYear()} Food Label Verification System • Multimodal Deep Learning & Dietary Verification</p>
      </footer>
    </div>
  );
}

export default App;

import React, { useState, useEffect } from "react";
import Tesseract from "tesseract.js";
import {
  analyzePayload,
  fetchCurrentUser,
  logoutUser,
  preprocessOcrImage
} from "./api";

// Modern UI Components
import Icon from "./components/Icons";
import StepProgressBar from "./components/StepProgressBar";
import AuthCard from "./components/AuthCard";
import DietaryPreferencesView from "./components/DietaryPreferencesView";
import ProductScanningView from "./components/ProductScanningView";
import AnalysisResultsView from "./components/AnalysisResultsView";
import AnalysisHistoryView from "./components/AnalysisHistoryView";
import AuditQueueModal from "./components/AuditQueueModal";

import "./style.css";

// Compute mean word-level confidence from Tesseract result (0.0–1.0)
const computeOcrConfidence = (tesseractData) => {
  const words = tesseractData?.words || [];
  if (words.length === 0) return 1.0;
  const validWords = words.filter((w) => w.confidence > 0);
  if (validWords.length === 0) return 0.5;
  const mean = validWords.reduce((sum, w) => sum + w.confidence, 0) / validWords.length;
  return Math.round((mean / 100) * 1000) / 1000;
};

// Canvas preprocessing for OCR enhancement (client fallback)
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
            const sharp =
              centerWeight * orig[idx + c] +
              neighborWeight * (orig[up + c] + orig[down + c] + orig[left + c] + orig[right + c]);
            const val = (sharp * brightness - 127.5) * contrast + 127.5;
            data[idx + c] = val < 0 ? 0 : val > 255 ? 255 : val;
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
  // Navigation & 4-Step Journey State
  // Steps: 1 = Account, 2 = Preferences, 3 = Scan, 4 = Results
  const [currentStep, setCurrentStep] = useState(3);
  const [currentView, setCurrentView] = useState("flow"); // 'flow' | 'history'
  const [showAuditModal, setShowAuditModal] = useState(false);

  // Authentication & Dietary Profile
  const [currentUser, setCurrentUser] = useState(null);
  const [dietaryProfile, setDietaryProfile] = useState(null);

  // Analysis State
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [analysisResult, setAnalysisResult] = useState(null);

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

  // Handler: Run full backend verification payload
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
      setCurrentView("flow");
      setCurrentStep(4); // Advance to Step 4: Personalised Results
    } catch (err) {
      console.error("Analysis failure:", err);
      const msg =
        err.response?.data?.message ||
        err.message ||
        "Analysis could not be completed. Please ensure the backend server is active.";
      setErrorMessage(msg);
    } finally {
      setLoading(false);
    }
  };

  // Handler: OCR processing for camera captures and uploaded images
  const handleOcrImage = async (imageSrc, isUpload = false, ocrConfig = "B") => {
    setLoading(true);
    setErrorMessage("");
    try {
      let ocrInput = imageSrc;
      let configUsed = ocrConfig;
      let preprocessingMetrics = null;

      if (ocrConfig === "B") {
        // Configuration B: Attempt OpenCV backend preprocessing (Laplacian blur + CLAHE + Sharpening)
        try {
          const prepRes = await preprocessOcrImage(imageSrc, "B", "best");
          if (prepRes && prepRes.enhanced_image_base64) {
            ocrInput = prepRes.enhanced_image_base64;
            configUsed = prepRes.configuration_used || "B";
            preprocessingMetrics = prepRes.quality_metrics || null;
          }
        } catch (prepErr) {
          console.warn("Backend OpenCV preprocessing bypassed, using client canvas fallback:", prepErr);
          ocrInput = await preprocessImageForOcr(imageSrc, isUpload);
          configUsed = "B (Client Fallback)";
        }
      } else {
        // Configuration A: Existing OCR directly on original image
        configUsed = "A (Original)";
      }

      // Perform OCR with Tesseract.js using standard configuration
      const worker = await Tesseract.createWorker("eng", 1);
      await worker.setParameters({
        tessedit_pageseg_mode: "6",
        preserve_interword_spaces: "1"
      });

      const res = await worker.recognize(ocrInput);
      await worker.terminate();

      const extracted = res.data.text;
      if (!extracted || !extracted.trim()) {
        setErrorMessage("No legible text could be recognized. Please ensure label is well-lit and in focus.");
        setLoading(false);
        return;
      }

      const ocrConfidence = computeOcrConfidence(res.data);

      await handleRunAnalysis({
        text: extracted,
        ocr_confidence: ocrConfidence,
        product: {
          name: isUpload ? "Uploaded Packaging Scan" : "Live Camera Capture",
          brand: "Scanned Label",
          category: "Physical Label OCR",
          ocr_pipeline_config: configUsed,
          preprocessing_metrics: preprocessingMetrics
        }
      });
    } catch (err) {
      console.error("OCR Pipeline error:", err);
      setErrorMessage(`OCR Processing Failed: ${err.message || err}`);
    } finally {
      setLoading(false);
    }
  };

  // Handler: Barcode lookup analysis
  const handleBarcodeAnalyze = async (barcode) => {
    await handleRunAnalysis({ ean: barcode });
  };

  // Handler: Manual ingredient text analysis
  const handleManualTextAnalyze = async (text) => {
    await handleRunAnalysis({
      text,
      ocr_confidence: 1.0,
      product: {
        name: "Manual Ingredient Formulation",
        brand: "Direct Entry",
        category: "Direct Formulation Check"
      }
    });
  };

  // Handler: Sign out
  const handleSignOut = async () => {
    try {
      await logoutUser();
    } catch {
      // Ignored
    } finally {
      setCurrentUser(null);
      setDietaryProfile(null);
      setCurrentStep(1);
    }
  };

  return (
    <div className="app">
      {/* Navigation Header */}
      <nav className="navbar">
        <div className="navbar-container">
          <div
            className="navbar-brand"
            onClick={() => {
              setCurrentView("flow");
              setCurrentStep(analysisResult ? 4 : 3);
            }}
          >
            <div className="brand-icon-wrapper">
              <Icon name="shieldCheck" size={24} color="#059669" />
            </div>
            <div>
              <span className="brand-name">Food Label Verification System</span>
              <span className="brand-tagline">Multimodal Deep Learning & Dietary Verification</span>
            </div>
          </div>

          <div className="navbar-nav-links">
            <button
              type="button"
              className={`nav-link-btn ${currentView === "flow" && (currentStep === 3 || currentStep === 4) ? "active" : ""}`}
              onClick={() => {
                setCurrentView("flow");
                setCurrentStep(analysisResult ? 4 : 3);
              }}
            >
              <Icon name="camera" size={16} />
              <span>Scan Product</span>
            </button>

            <button
              type="button"
              className={`nav-link-btn ${currentView === "flow" && currentStep === 2 ? "active" : ""}`}
              onClick={() => {
                setCurrentView("flow");
                setCurrentStep(2);
              }}
            >
              <Icon name="sliders" size={16} />
              <span>Preferences</span>
            </button>

            <button
              type="button"
              className={`nav-link-btn ${currentView === "history" ? "active" : ""}`}
              onClick={() => {
                setCurrentView("history");
              }}
            >
              <Icon name="history" size={16} />
              <span>History</span>
            </button>

            <button
              type="button"
              className="nav-link-btn"
              onClick={() => setShowAuditModal(true)}
              title="Human-in-the-Loop review queue for unmapped additives"
            >
              <Icon name="clipboardList" size={16} />
              <span>HITL Audit</span>
            </button>
          </div>

          <div className="navbar-user-actions">
            {currentUser ? (
              <div className="user-badge-pill">
                <Icon name="user" size={15} color="#059669" />
                <span>{currentUser.username}</span>
                {dietaryProfile?.preset_name && (
                  <span className="user-preset-badge">
                    {dietaryProfile.preset_name.replace("_", " ")}
                  </span>
                )}
                <button
                  type="button"
                  className="btn btn-ghost btn-sm"
                  onClick={handleSignOut}
                  title="Sign out of account"
                  style={{ padding: "0.15rem 0.35rem", marginLeft: "0.25rem" }}
                >
                  <Icon name="logOut" size={14} />
                </button>
              </div>
            ) : (
              <button
                type="button"
                className="btn btn-primary btn-sm"
                onClick={() => {
                  setCurrentView("flow");
                  setCurrentStep(1);
                }}
              >
                <Icon name="user" size={14} />
                <span>Sign In / Register</span>
              </button>
            )}
          </div>
        </div>
      </nav>

      {/* Global Error Banner */}
      {errorMessage && (
        <div style={{ maxWidth: 1200, margin: "1rem auto 0 auto", padding: "0 1.5rem" }}>
          <div className="alert-banner alert-danger">
            <Icon name="alertTriangle" size={18} />
            <span style={{ flex: 1 }}>{errorMessage}</span>
            <button
              type="button"
              onClick={() => setErrorMessage("")}
              style={{ background: "none", border: "none", cursor: "pointer", color: "inherit" }}
            >
              <Icon name="x" size={16} />
            </button>
          </div>
        </div>
      )}

      {/* 4-Step Workflow Progress Indicator */}
      {currentView === "flow" && (
        <StepProgressBar
          currentStep={currentStep}
          onSelectStep={(stepNum) => setCurrentStep(stepNum)}
          currentUser={currentUser}
        />
      )}

      {/* Main Dynamic View Content */}
      <main className="main-content">
        {currentView === "history" ? (
          <AnalysisHistoryView
            onSelectScanRecord={(record) => {
              // Convert history record to analysis result format and view in Step 4
              setAnalysisResult({
                product: {
                  name: record.product_name,
                  brand: record.brand,
                  ean: record.ean,
                  category: record.category || "Past Scan Record"
                },
                personal_evaluation: {
                  personal_score: record.personal_score !== undefined ? record.personal_score : record.safety_score,
                  personal_verdict: record.personal_verdict || "Compatible",
                  allergen_alerts: record.allergen_alerts || [],
                  preference_conflicts: record.preference_conflicts || [],
                  caution_items: record.caution_items || [],
                  preset_name: record.preset_name || "custom"
                },
                safety_indicator: {
                  final_score: record.safety_score || record.personal_score || 95,
                  grade: record.grade || "A",
                  base_baseline_score: 100,
                  score_deductions: []
                },
                system_audit: record.system_audit || {
                  confidence: {
                    ocr_confidence: record.ocr_confidence || 1.0,
                    additive_match_confidence: 1.0,
                    barcode_decode_status: record.ean ? "valid_ean13" : "not_provided"
                  }
                },
                parsed_additives: record.parsed_additives || []
              });
              setCurrentView("flow");
              setCurrentStep(4);
            }}
            onBackToScan={() => {
              setCurrentView("flow");
              setCurrentStep(3);
            }}
          />
        ) : (
          <>
            {/* STEP 1: ACCOUNT CREATION / LOGIN */}
            {currentStep === 1 && (
              <AuthCard
                currentUser={currentUser}
                onAuthSuccess={(user, profile) => {
                  setCurrentUser(user);
                  setDietaryProfile(profile);
                  // Advance to Step 2
                  setCurrentStep(2);
                }}
                onContinueAsGuest={() => {
                  setCurrentStep(2);
                }}
                onSignOut={handleSignOut}
              />
            )}

            {/* STEP 2: DIETARY PREFERENCE SELECTION */}
            {currentStep === 2 && (
              <DietaryPreferencesView
                currentProfile={dietaryProfile}
                currentUser={currentUser}
                onProfileSaved={(prof) => {
                  setDietaryProfile(prof);
                }}
                onProceedToScan={() => {
                  setCurrentStep(3);
                }}
              />
            )}

            {/* STEP 3: PRODUCT SCANNING */}
            {currentStep === 3 && (
              <ProductScanningView
                loading={loading}
                dietaryProfile={dietaryProfile}
                onAnalyzeOcr={handleOcrImage}
                onAnalyzeBarcode={handleBarcodeAnalyze}
                onAnalyzeManualText={handleManualTextAnalyze}
              />
            )}

            {/* STEP 4: PERSONALISED ANALYSIS RESULTS */}
            {currentStep === 4 && (
              <AnalysisResultsView
                analysisResult={analysisResult}
                dietaryProfile={dietaryProfile}
                onScanAnother={() => {
                  setAnalysisResult(null);
                  setCurrentStep(3);
                }}
                onOpenPreferences={() => {
                  setCurrentStep(2);
                }}
              />
            )}
          </>
        )}
      </main>

      {/* Human-in-the-Loop Audit Queue Modal */}
      <AuditQueueModal
        isOpen={showAuditModal}
        onClose={() => setShowAuditModal(false)}
      />

      {/* Footer */}
      <footer className="main-footer">
        <p>
          &copy; {new Date().getFullYear()} Food Label Verification System • Multimodal Deep Learning & Dietary Verification
        </p>
      </footer>
    </div>
  );
}

export default App;
